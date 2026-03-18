import re
from data import protocols

def _tokenize(text):
    return set(re.findall(r'\b[a-z0-9]+\b', text.lower())) if text else set()

def check_openfda(drug, patient):
    # Mock implementation – replace with actual OpenFDA API call
    drug_lower = drug.lower()
    if any(drug_lower in a.lower() for a in patient.get('allergies', [])):
        return True
    return False

def compute_relevance(protocol, patient, query_tokens):
    score = 0.0
    baseline = protocol.get('baseline_relevance', 0.5)
    score += baseline * 0.3

    protocol_text = ' '.join([protocol['title'], protocol.get('category', ''), ' '.join(protocol.get('steps', []))])
    protocol_tokens = _tokenize(protocol_text)
    match_protocol = len(query_tokens & protocol_tokens) / len(query_tokens) if query_tokens else 0
    score += match_protocol * 0.45

    patient_text = ' '.join([patient.get('complaint', ''), patient.get('presentation', ''), ' '.join(patient.get('history', []))])
    patient_tokens = _tokenize(patient_text)
    match_patient = len(query_tokens & patient_tokens) / len(query_tokens) if query_tokens else 0
    score += match_patient * 0.25

    vitals = patient.get('vitals', {})
    if vitals.get('spo2', 100) < 90 and 'oxygen' in protocol_text.lower():
        score += 0.10
    if vitals.get('gcs', 15) < 13 and ('neuro' in protocol_text.lower() or 'gcs' in protocol_text.lower()):
        score += 0.10
    if vitals.get('hr', 80) > 110 and ('cardiac' in protocol_text.lower() or 'heart' in protocol_text.lower()):
        score += 0.08
    if vitals.get('bp_sys', 120) > 160 and ('stroke' in protocol_text.lower() or 'neuro' in protocol_text.lower()):
        score += 0.08

    # OpenFDA contraindication penalty
    if protocol.get('drugs'):
        for drug in protocol['drugs']:
            if check_openfda(drug, patient):
                score *= 0.5
                break

    return min(score, 1.0)

def score_protocols(query_text, patient, threshold=0.55, limit=5):
    query_tokens = _tokenize(query_text)
    results = []
    for cat, prots in protocols.protocols.items():
        for key, prot in prots.items():
            prot['category'] = cat
            score = compute_relevance(prot, patient, query_tokens)
            if score >= threshold:
                results.append({
                    'category': cat,
                    'key': key,
                    'title': prot['title'],
                    'priority': prot['priority'],
                    'steps': prot['steps'],
                    'contraindications': prot['contraindications'],
                    'source': prot['source'],
                    'score': round(score * 100, 1)
                })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]