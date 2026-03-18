# aact_integration.py
import os
import re
import psycopg2
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables (if using .env)
load_dotenv()

# AACT database connection parameters
AACT_CONFIG = {
    'dbname': 'aact',
    'user': os.getenv('AACT_USER'),
    'password': os.getenv('AACT_PASSWORD'),
    'host': 'aact-db.ctti-clinicaltrials.org',
    'port': 5432
}

def get_aact_connection():
    """Create and return a connection to the AACT database."""
    try:
        conn = psycopg2.connect(**AACT_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to AACT: {e}")
        return None

@lru_cache(maxsize=128)
def map_to_emergency_category(keyword):
    """Map a search keyword to one of your emergency categories."""
    keyword_lower = keyword.lower()
    cardiac = ['heart', 'cardiac', 'stemi', 'nstemi', 'myocardial', 'angina', 'coronary']
    trauma = ['trauma', 'injury', 'hemorrhage', 'fracture', 'wound', 'accident']
    respiratory = ['respiratory', 'copd', 'asthma', 'pulmonary', 'lung', 'breath', 'ventilation']
    neuro = ['stroke', 'neuro', 'brain', 'seizure', 'headache', 'cerebral', 'intracranial']
    
    if any(k in keyword_lower for k in cardiac):
        return 'cardiac'
    elif any(k in keyword_lower for k in trauma):
        return 'trauma'
    elif any(k in keyword_lower for k in respiratory):
        return 'respiratory'
    elif any(k in keyword_lower for k in neuro):
        return 'neuro'
    else:
        return 'other'

def infer_priority(phase, status):
    """Infer a priority level based on trial phase and status."""
    phase_lower = (phase or '').lower()
    status_lower = (status or '').lower()
    if 'phase 3' in phase_lower or 'phase 4' in phase_lower:
        return 'critical' if 'recruiting' in status_lower else 'urgent'
    elif 'phase 2' in phase_lower:
        return 'urgent'
    else:
        return 'moderate'

def extract_steps_from_text(text, max_steps=5):
    """Extract potential protocol steps from free text (criteria, summary)."""
    if not text:
        return []
    # Split by sentences
    sentences = re.split(r'[.!?]+', text)
    steps = []
    action_indicators = ['administer', 'give', 'monitor', 'assess', 'perform', 'check',
                         'obtain', 'measure', 'evaluate', 'titrate', 'infuse', 'inject']
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if any(indicator in sent.lower() for indicator in action_indicators):
            steps.append(sent)
        if len(steps) >= max_steps:
            break
    return steps

def extract_contraindications(text, max_items=3):
    """Extract contraindication-like phrases."""
    if not text:
        return []
    contra_indicators = ['contraindication', 'exclusion', 'not eligible', 'cannot',
                         'should not', 'avoid', 'contraindicated']
    sentences = re.split(r'[.!?]+', text)
    contra = []
    for sent in sentences:
        if any(ind in sent.lower() for ind in contra_indicators):
            contra.append(sent.strip())
        if len(contra) >= max_items:
            break
    return contra

def extract_drugs_from_text(text):
    """Simple drug name extraction based on a common drug list."""
    if not text:
        return []
    common_drugs = [
        'aspirin', 'heparin', 'nitroglycerin', 'morphine', 'epinephrine',
        'amiodarone', 'furosemide', 'albuterol', 'ipratropium', 'mannitol',
        'tpa', 'ceftriaxone', 'vancomycin', 'dexamethasone', 'lorazepam',
        'fosphenytoin', 'levetiracetam', 'corticosteroids', 'antibiotics'
    ]
    text_lower = text.lower()
    found = [drug for drug in common_drugs if drug in text_lower]
    return found

def fetch_emergency_protocols(condition_keywords, limit_per_keyword=20):
    """
    Query AACT for studies matching the given keywords (e.g., ['heart attack', 'stroke']).
    Returns a list of raw study dictionaries.
    """
    conn = get_aact_connection()
    if not conn:
        return []
    
    cur = conn.cursor()
    all_results = []
    
    for keyword in condition_keywords:
        # Search in titles and brief summary
        query = """
        SELECT 
            s.nct_id,
            s.brief_title,
            s.official_title,
            s.study_type,
            s.overall_status,
            s.phase,
            s.enrollment,
            bs.description as brief_summary,
            ec.criteria,
            po.description as primary_outcome
        FROM ctgov.studies s
        LEFT JOIN ctgov.brief_summaries bs ON s.nct_id = bs.nct_id
        LEFT JOIN ctgov.eligibilities ec ON s.nct_id = ec.nct_id
        LEFT JOIN ctgov.design_outcomes po ON s.nct_id = po.nct_id AND po.outcome_type = 'primary'
        WHERE 
            LOWER(s.brief_title) LIKE %s 
            OR LOWER(s.official_title) LIKE %s
            OR LOWER(bs.description) LIKE %s
        LIMIT %s;
        """
        search_term = f"%{keyword.lower()}%"
        cur.execute(query, (search_term, search_term, search_term, limit_per_keyword))
        rows = cur.fetchall()
        
        for row in rows:
            all_results.append({
                'nct_id': row[0],
                'brief_title': row[1],
                'official_title': row[2],
                'study_type': row[3],
                'overall_status': row[4],
                'phase': row[5],
                'enrollment': row[6],
                'brief_summary': row[7],
                'criteria': row[8],
                'primary_outcome': row[9],
                'search_keyword': keyword
            })
    
    cur.close()
    conn.close()
    return all_results

def transform_to_protocol(aact_study):
    """Convert a raw AACT study dictionary into your app's protocol format."""
    # Combine title
    title = aact_study.get('official_title') or aact_study.get('brief_title') or 'Unknown Title'
    
    # Combine text fields for extraction
    combined_text = (aact_study.get('brief_summary') or '') + ' ' + (aact_study.get('criteria') or '')
    
    steps = extract_steps_from_text(combined_text)
    contraindications = extract_contraindications(combined_text)
    drugs = extract_drugs_from_text(combined_text)
    
    # Map category using the original search keyword (or try to infer from title)
    keyword = aact_study.get('search_keyword', '')
    category = map_to_emergency_category(keyword)
    if category == 'other':
        # fallback: try to guess from title
        category = map_to_emergency_category(title)
    
    priority = infer_priority(aact_study.get('phase'), aact_study.get('overall_status'))
    
    protocol = {
        'title': title,
        'category': category,
        'priority': priority,
        'baseline_relevance': 0.7,  # default, can be adjusted
        'steps': steps,
        'contraindications': contraindications,
        'source': f"ClinicalTrials.gov (NCT: {aact_study['nct_id']})",
        'drugs': drugs,
        'nct_id': aact_study['nct_id']
    }
    return protocol

def search_and_transform(keywords, limit=20):
    """High-level function: search AACT and return a list of protocols ready for your app."""
    raw = fetch_emergency_protocols(keywords, limit_per_keyword=limit)
    protocols = [transform_to_protocol(study) for study in raw]
    return protocols