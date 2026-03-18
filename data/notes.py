import time

notes_store = {
    'cardiac': [
        {
            'id': 1,
            'timestamp': time.time() - 3600,
            'author': 'Dr. Adams',
            'text': 'Patient arrived with chest pain. ECG shows STEMI. Activating cath lab.'
        },
        {
            'id': 2,
            'timestamp': time.time() - 1800,
            'author': 'Nurse Chen',
            'text': 'Aspirin given. Pain 8/10. IV placed.'
        }
    ],
    'trauma': [
        {
            'id': 1,
            'timestamp': time.time() - 2700,
            'author': 'Dr. Bailey',
            'text': 'Trauma team activated. Unstable, intubated in field. FAST exam positive for free fluid.'
        },
        {
            'id': 2,
            'timestamp': time.time() - 900,
            'author': 'Nurse Davis',
            'text': 'Two large-bore IVs. Blood products hung.'
        }
    ],
    'respiratory': [
        {
            'id': 1,
            'timestamp': time.time() - 5400,
            'author': 'Dr. Evans',
            'text': 'Severe COPD exacerbation. Started on BiPAP. ABG pending.'
        },
        {
            'id': 2,
            'timestamp': time.time() - 3600,
            'author': 'Nurse Foster',
            'text': 'Nebulizers given. Slight improvement in work of breathing.'
        }
    ],
    'neuro': [
        {
            'id': 1,
            'timestamp': time.time() - 7200,
            'author': 'Dr. Garcia',
            'text': 'Sudden onset headache and weakness. STAT head CT ordered. BP 188/108.'
        },
        {
            'id': 2,
            'timestamp': time.time() - 6000,
            'author': 'Nurse Huang',
            'text': 'CT completed. Patient to radiology.'
        }
    ]
}

next_id = {
    'cardiac': 3,
    'trauma': 3,
    'respiratory': 3,
    'neuro': 3
}

def add_note(patient_key, author, text):
    global next_id
    note = {
        'id': next_id[patient_key],
        'timestamp': time.time(),
        'author': author,
        'text': text
    }
    notes_store[patient_key].append(note)
    next_id[patient_key] += 1
    return note