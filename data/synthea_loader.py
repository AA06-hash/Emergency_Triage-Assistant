import json
import random
import time
from data.patients import patients
from data.vitals_history import vitals_history

def load_synthea_patients(filepath='synthea_output.json'):
    try:
        with open(filepath) as f:
            synthea_patients = json.load(f)
    except FileNotFoundError:
        print("Synthea file not found; skipping.")
        return
    for i, sp in enumerate(synthea_patients[:10]):  # load first 10
        key = f"synthea_{i}"
        patients[key] = {
            'name': f"{sp['name']['given']} {sp['name']['family']}",
            'age': sp['age'],
            'sex': sp['gender'][0].upper(),
            'complaint': sp.get('chief_complaint', 'Unknown'),
            'vitals': {
                'hr': random.randint(60, 120),
                'bp_sys': random.randint(90, 180),
                'bp_dia': random.randint(60, 100),
                'spo2': random.randint(90, 100),
                'rr': random.randint(12, 24),
                'temp': round(random.uniform(36.0, 38.5), 1),
                'gcs': 15
            },
            'history': sp.get('conditions', [])[:3],
            'irrelevant_history': [],
            'allergies': sp.get('allergies', []),
            'esi': random.choice(['ESI-1', 'ESI-2', 'ESI-3'])
        }
        base = time.time() - 1800
        vitals_history[key] = [
            {'time': base + i*180, 
             'hr': patients[key]['vitals']['hr'] + random.randint(-5,5),
             'bp_sys': patients[key]['vitals']['bp_sys'] + random.randint(-10,10),
             'spo2': patients[key]['vitals']['spo2'] + random.randint(-2,2),
             'rr': patients[key]['vitals']['rr'] + random.randint(-2,2)
            } for i in range(10)
        ]
    print(f"Loaded {len(synthea_patients[:10])} synthetic patients.")