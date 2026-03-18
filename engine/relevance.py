import re
import requests
from functools import lru_cache
from data import protocols

def _tokenize(text):
    """Convert text to set of lowercase alphanumeric tokens."""
    if not text:
        return set()
    words = re.findall(r'\b[a-z0-9]+\b', text.lower())
    return set(words)

@lru_cache(maxsize=128)
def check_openfda(drug_name, patient_allergies_tuple):
    """
    Query OpenFDA for adverse events related to the drug.
    Returns True if the drug has known adverse reactions matching patient allergies.
    """
    # Convert tuple back to list for processing
    patient_allergies = list(patient_allergies_tuple)
    if not patient_allergies:
        return False

    # Build query: search for drug name and reaction terms matching allergies
    query_parts = [f'patient.drug.medicinalproduct:"{drug_name}"']
    # Add reaction terms (OR)
    reaction_terms = ' OR '.join([f'patient.reaction.reactionmeddrapt:"{allergy}"' for allergy in patient_allergies])
    if reaction_terms:
        query_parts.append(f'({reaction_terms})')
    query = '+AND+'.join(query_parts)

    url = f"https://api.fda.gov/drug/event.json?search={query}&limit=1"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # If there's at least one result, the drug has a reported adverse event matching an allergy
            return data.get('meta', {}).get('results', {}).get('total', 0) > 0
        elif response.status_code == 404:
            # No results means no adverse events found
            return False
        else:
            # Log error (use print for now, but consider proper logging)
            print(f"OpenFDA error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"OpenFDA exception: {e}")
        return False

def compute_relevance(protocol, patient, query_tokens):
    """
    Compute relevance score for a single protocol against patient and query.
    Returns score between 0 and 1.
    """
    score = 0.0

    # Baseline weight (30%)
    baseline = protocol.get('baseline_relevance', 0.5)
    score += baseline * 0.3

    # Keyword match vs protocol (45%)
    protocol_text = ' '.join([
        protocol['title'],
        protocol.get('category', ''),
        ' '.join(protocol.get('steps', []))
    ])
    protocol_tokens = _tokenize(protocol_text)
    if query_tokens:
        match_protocol = len(query_tokens & protocol_tokens) / len(query_tokens)
    else:
        match_protocol = 0
    score += match_protocol * 0.45

    # Keyword match vs patient (25%)
    patient_text = ' '.join([
        patient.get('complaint', ''),
        patient.get('presentation', ''),
        ' '.join(patient.get('history', []))
    ])
    patient_tokens = _tokenize(patient_text)
    if query_tokens:
        match_patient = len(query_tokens & patient_tokens) / len(query_tokens)
    else:
        match_patient = 0
    score += match_patient * 0.25

    # Vital sign boosts
    vitals = patient.get('vitals', {})

    # SpO2 < 90% and protocol mentions oxygen
    if vitals.get('spo2', 100) < 90 and 'oxygen' in protocol_text.lower():
        score += 0.10

    # GCS < 13 and protocol mentions neuro
    if vitals.get('gcs', 15) < 13 and ('neuro' in protocol_text.lower() or 'gcs' in protocol_text.lower()):
        score += 0.10

    # HR > 110 and protocol mentions cardiac
    if vitals.get('hr', 80) > 110 and ('cardiac' in protocol_text.lower() or 'heart' in protocol_text.lower()):
        score += 0.08

    # Systolic BP > 160 and protocol mentions stroke
    if vitals.get('bp_sys', 120) > 160 and ('stroke' in protocol_text.lower() or 'neuro' in protocol_text.lower()):
        score += 0.08

    # OpenFDA contraindication check
    if protocol.get('drugs'):
        # Convert patient allergies list to a tuple for caching (must be hashable)
        allergies_tuple = tuple(patient.get('allergies', []))
        for drug in protocol['drugs']:
            if check_openfda(drug, allergies_tuple):
                score *= 0.5  # halve score if contraindicated
                break

    return min(score, 1.0)  # Cap at 1.0

def score_protocols(query_text, patient, threshold=0.55, limit=5):
    """
    Rank all protocols against query and patient.
    Returns list of dicts with protocol details and score.
    """
    query_tokens = _tokenize(query_text)
    results = []

    for category, cat_protocols in protocols.protocols.items():
        for key, protocol in cat_protocols.items():
            # Add category to protocol dict for tokenization
            protocol['category'] = category
            score = compute_relevance(protocol, patient, query_tokens)
            if score >= threshold:
                result = {
                    'category': category,
                    'key': key,
                    'title': protocol['title'],
                    'priority': protocol['priority'],
                    'steps': protocol['steps'],
                    'contraindications': protocol['contraindications'],
                    'source': protocol['source'],
                    'score': round(score * 100, 1)
                }
                results.append(result)

    # Sort descending by score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]