import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
from functools import lru_cache
from data import protocols

# Global TF-IDF objects, initialized lazily
_vectorizer = None
_tfidf_matrix = None
_protocol_indices = []  # list of (category, key) in same order as matrix rows

def _build_tfidf_index():
    """Build TF-IDF index from all protocols."""
    global _vectorizer, _tfidf_matrix, _protocol_indices
    texts = []
    _protocol_indices = []
    for category, cat_protocols in protocols.protocols.items():
        for key, prot in cat_protocols.items():
            # Combine title, category, and steps into one document
            doc = f"{prot['title']} {category} " + " ".join(prot.get('steps', []))
            texts.append(doc)
            _protocol_indices.append((category, key))
    _vectorizer = TfidfVectorizer(stop_words='english')
    _tfidf_matrix = _vectorizer.fit_transform(texts)

def _get_tfidf_scores(query_text):
    """Return array of cosine similarities between query and all protocols."""
    global _vectorizer, _tfidf_matrix
    if _vectorizer is None or _tfidf_matrix is None:
        _build_tfidf_index()
    query_vec = _vectorizer.transform([query_text])
    # cosine similarity = dot product of normalized vectors
    similarities = (_tfidf_matrix * query_vec.T).toarray().flatten()
    return similarities

def _tokenize(text):
    """Convert text to set of lowercase alphanumeric tokens (kept for potential future use)."""
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
    patient_allergies = list(patient_allergies_tuple)
    if not patient_allergies:
        return False

    query_parts = [f'patient.drug.medicinalproduct:"{drug_name}"']
    reaction_terms = ' OR '.join([f'patient.reaction.reactionmeddrapt:"{allergy}"' for allergy in patient_allergies])
    if reaction_terms:
        query_parts.append(f'({reaction_terms})')
    query = '+AND+'.join(query_parts)

    url = f"https://api.fda.gov/drug/event.json?search={query}&limit=1"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('meta', {}).get('results', {}).get('total', 0) > 0
        elif response.status_code == 404:
            return False
        else:
            print(f"OpenFDA error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"OpenFDA exception: {e}")
        return False

def score_protocols(query_text, patient, threshold=0.55, limit=5):
    """
    Rank all protocols against query and patient using TF‑IDF similarity.
    Returns list of dicts with protocol details and score.
    """
    # Ensure TF‑IDF index is built
    global _protocol_indices, _vectorizer, _tfidf_matrix
    if not _protocol_indices:
        _build_tfidf_index()

    # Precompute query similarities for all protocols
    query_similarities = _get_tfidf_scores(query_text)

    # Precompute patient vector once
    patient_text = ' '.join([
        patient.get('complaint', ''),
        patient.get('presentation', ''),
        ' '.join(patient.get('history', []))
    ])
    patient_vec = _vectorizer.transform([patient_text])

    results = []

    for idx, (category, key) in enumerate(_protocol_indices):
        protocol = protocols.protocols[category][key].copy()
        protocol['category'] = category

        # Baseline weight (20%)
        baseline = protocol.get('baseline_relevance', 0.5)
        score = baseline * 0.2

        # Query similarity (40%)
        query_sim = query_similarities[idx]
        score += query_sim * 0.4

        # Patient similarity (20%)
        patient_sim = (_tfidf_matrix[idx] * patient_vec.T).toarray()[0, 0]
        score += patient_sim * 0.2

        # Vital sign boosts (up to 0.36)
        vitals = patient.get('vitals', {})
        protocol_text = ' '.join([
            protocol['title'],
            category,
            ' '.join(protocol.get('steps', []))
        ]).lower()

        if vitals.get('spo2', 100) < 90 and 'oxygen' in protocol_text:
            score += 0.10
        if vitals.get('gcs', 15) < 13 and ('neuro' in protocol_text or 'gcs' in protocol_text):
            score += 0.10
        if vitals.get('hr', 80) > 110 and ('cardiac' in protocol_text or 'heart' in protocol_text):
            score += 0.08
        if vitals.get('bp_sys', 120) > 160 and ('stroke' in protocol_text or 'neuro' in protocol_text):
            score += 0.08

        # OpenFDA contraindication penalty
        if protocol.get('drugs'):
            allergies_tuple = tuple(patient.get('allergies', []))
            for drug in protocol['drugs']:
                if check_openfda(drug, allergies_tuple):
                    score *= 0.5
                    break

        score = min(score, 1.0)

        if score >= threshold:
            results.append({
                'category': category,
                'key': key,
                'title': protocol['title'],
                'priority': protocol['priority'],
                'steps': protocol['steps'],
                'contraindications': protocol['contraindications'],
                'source': protocol['source'],
                'score': round(score * 100, 1)
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]