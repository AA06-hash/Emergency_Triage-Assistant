import time
import os
import base64
import requests
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from data import patients, protocols, vitals_history, suggestions
from engine.relevance import score_protocols
from models import db, Note

# NEW: Import AACT integration
from aact_integration import search_and_transform

api_bp = Blueprint('api', __name__)

start_time = time.time()

def get_uptime():
    seconds = int(time.time() - start_time)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def is_scaledown_configured():
    return os.environ.get('SCALEDOWN_API_KEY') is not None

def compress_with_scaledown(image_data, quality=85):
    if not is_scaledown_configured():
        return None
    api_key = os.environ['SCALEDOWN_API_KEY']
    headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}
    encoded = base64.b64encode(image_data).decode('utf-8')
    payload = {'image': encoded, 'quality': quality}
    try:
        resp = requests.post("https://api.scaledown.xyz/compress/raw/", json=payload, headers=headers)
        return resp.content if resp.status_code == 200 else None
    except:
        return None

def compression_stats(original_size, compressed_size):
    reduction = original_size - compressed_size
    ratio = (compressed_size / original_size) * 100 if original_size else 0
    savings = 100 - ratio
    return {
        'original_bytes': original_size,
        'compressed_bytes': compressed_size,
        'reduction_bytes': reduction,
        'ratio_percent': round(ratio, 1),
        'savings_percent': round(savings, 1)
    }

# ====== Public endpoints ======
@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'online',
        'uptime': get_uptime(),
        'patients': len(patients.patients),
        'protocols': sum(len(c) for c in protocols.protocols.values())
    })

@api_bp.route('/patients', methods=['GET'])
def get_patients():
    patient_list = [{'key': k, 'name': v['name'], 'esi': v['esi'], 'suggestions': suggestions.suggestions.get(k, [])} 
                    for k, v in patients.patients.items()]
    return jsonify(patient_list)

@api_bp.route('/patients/<key>', methods=['GET'])
def get_patient(key):
    patient = patients.patients.get(key)
    return jsonify(patient) if patient else (jsonify({'error': 'Not found'}), 404)

@api_bp.route('/patients/<key>/vitals-trend', methods=['GET'])
def get_vitals_trend(key):
    trend = vitals_history.vitals_history.get(key)
    return jsonify(trend) if trend else (jsonify({'error': 'Not found'}), 404)

@api_bp.route('/protocols', methods=['GET'])
def get_protocols():
    flat = []
    for cat, prots in protocols.protocols.items():
        for key, data in prots.items():
            flat.append({'category': cat, 'key': key, 'title': data['title'], 'priority': data['priority']})
    return jsonify(flat)

@api_bp.route('/protocols/<category>/<key>', methods=['GET'])
def get_protocol(category, key):
    prot = protocols.protocols.get(category, {}).get(key)
    return jsonify(prot) if prot else (jsonify({'error': 'Not found'}), 404)

@api_bp.route('/suggestions/<patient>', methods=['GET'])
def get_suggestions(patient):
    return jsonify(suggestions.suggestions.get(patient, []))

# ====== Protected endpoints (require login) ======
@api_bp.route('/query', methods=['POST'])
@login_required
def query():
    data = request.get_json()
    if not data:
        abort(400)
    patient_key = data.get('patient')
    query_text = data.get('query', '')
    threshold = float(data.get('threshold', 55)) / 100.0
    limit = int(data.get('limit', 5))
    patient = patients.patients.get(patient_key)
    if not patient:
        abort(404)

    # Get static protocol results
    static_results = score_protocols(query_text, patient, threshold, limit)

    # Decide if we need AACT results
    need_aact = False
    if len(static_results) < 3:
        need_aact = True
    elif static_results and static_results[0]['score'] < 60:
        need_aact = True

    if need_aact:
        try:
            # Call AACT search with the same query (use single keyword)
            aact_protocols = search_and_transform([query_text], limit=5)
            # Add a default score and source flag
            for p in aact_protocols:
                p['score'] = 50  # Base score for AACT results
                p['source'] = 'clinicaltrials'
                # Ensure required fields exist for frontend
                if 'priority' not in p:
                    p['priority'] = 'moderate'
                if 'steps' not in p:
                    p['steps'] = ['See protocol details at source']
                if 'contraindications' not in p:
                    p['contraindications'] = []
            # Merge static and AACT results, then sort by score descending
            combined = static_results + aact_protocols
            combined.sort(key=lambda x: x.get('score', 0), reverse=True)
            results = combined[:limit]
        except Exception as e:
            # Log error and fall back to static only
            print(f"AACT query error: {e}")
            results = static_results
    else:
        results = static_results

    return jsonify({'results': results})

@api_bp.route('/patients/search', methods=['GET'])
@login_required
def search_patients():
    q = request.args.get('q', '').lower()
    if not q:
        return jsonify([])
    results = []
    for key, p in patients.patients.items():
        if (q in p['name'].lower() or q in p.get('complaint', '').lower() or 
            any(q in h.lower() for h in p.get('history', []))):
            results.append({'key': key, 'name': p['name'], 'esi': p['esi']})
    return jsonify(results)

@api_bp.route('/notes/<patient>', methods=['GET'])
@login_required
def get_notes(patient):
    notes = Note.query.filter_by(patient_key=patient).order_by(Note.timestamp.desc()).all()
    return jsonify([{'id': n.id, 'author': n.author, 'text': n.text, 'timestamp': n.timestamp.timestamp()} for n in notes])

@api_bp.route('/notes/<patient>', methods=['POST'])
@login_required
def add_note(patient):
    data = request.get_json()
    if not data or 'text' not in data:
        abort(400)
    note = Note(patient_key=patient, author=data.get('author', current_user.username), text=data['text'])
    db.session.add(note)
    db.session.commit()
    return jsonify({'id': note.id, 'timestamp': note.timestamp.timestamp()}), 201

@api_bp.route('/compress', methods=['POST'])
@login_required
def compress_image():
    if not is_scaledown_configured():
        return jsonify({'error': 'ScaleDown API key not configured'}), 503
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    quality = int(request.form.get('quality', 85))
    original_data = file.read()
    compressed_data = compress_with_scaledown(original_data, quality)
    if not compressed_data:
        return jsonify({'error': 'Compression failed'}), 500
    stats = compression_stats(len(original_data), len(compressed_data))
    return jsonify({
        'filename': file.filename,
        'stats': stats,
        'compressed_base64': base64.b64encode(compressed_data).decode('utf-8')
    })

# ====== AACT search endpoint (optional, kept for direct access) ======
@api_bp.route('/aact/search', methods=['GET'])
@login_required
def aact_search():
    keywords_param = request.args.get('keywords', '')
    limit = int(request.args.get('limit', 10))
    if not keywords_param:
        return jsonify({'error': 'Missing keywords parameter'}), 400
    keywords = [k.strip() for k in keywords_param.split(',') if k.strip()]
    try:
        protocols = search_and_transform(keywords, limit=limit)
        return jsonify({'results': protocols, 'count': len(protocols)})
    except Exception as e:
        print(f"AACT search error: {e}")
        return jsonify({'error': str(e)}), 500

# ====== Error handlers ======
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500