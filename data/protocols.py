# Protocols organized by category
protocols = {
    'cardiac': {
        'stemi': {
            'title': 'STEMI Protocol',
            'priority': 'critical',
            'baseline_relevance': 0.95,
            'steps': [
                'Aspirin 324 mg PO (chewed)',
                'Nitroglycerin 0.4 mg SL q5min x3',
                'Morphine 2-4 mg IV for pain',
                'Oxygen if SpO2 < 90%',
                '12-lead ECG within 10 minutes',
                'Activate cath lab',
                'Heparin bolus + infusion'
            ],
            'contraindications': ['Hypotension (SBP <90)', 'RV infarct', 'Recent bleeding'],
            'source': 'AHA/ACC 2023',
            'drugs': ['aspirin', 'nitroglycerin', 'morphine', 'heparin']
        },
        'nstemi': {
            'title': 'NSTEMI Protocol',
            'priority': 'urgent',
            'baseline_relevance': 0.8,
            'steps': [
                'Aspirin 324 mg PO',
                'Nitroglycerin for chest pain',
                'Heparin infusion',
                'Beta-blocker if no contraindication',
                'Cardiology consult'
            ],
            'contraindications': ['Active bleeding', 'Severe bradycardia'],
            'source': 'AHA/ACC 2023',
            'drugs': ['aspirin', 'nitroglycerin', 'heparin', 'beta-blocker']
        },
        'cardiac_arrest': {
            'title': 'Cardiac Arrest Protocol',
            'priority': 'critical',
            'baseline_relevance': 1.0,
            'steps': [
                'Start CPR',
                'Defibrillate VF/pVT',
                'Epinephrine 1 mg q3-5min',
                'Advanced airway',
                'Amiodarone for refractory VF/pVT'
            ],
            'contraindications': ['DNAR order'],
            'source': 'AHA ACLS 2023',
            'drugs': ['epinephrine', 'amiodarone']
        },
        'heart_failure': {
            'title': 'Acute Heart Failure Protocol',
            'priority': 'urgent',
            'baseline_relevance': 0.7,
            'steps': [
                'Oxygen to maintain SpO2 > 90%',
                'Furosemide IV',
                'Nitroglycerin for BP control',
                'Non-invasive ventilation if severe',
                'Assess volume status'
            ],
            'contraindications': ['Hypotension', 'Severe aortic stenosis'],
            'source': 'ESC 2021',
            'drugs': ['furosemide', 'nitroglycerin']
        }
    },
    'trauma': {
        'primary_survey': {
            'title': 'Primary Survey (ABCDE)',
            'priority': 'critical',
            'baseline_relevance': 0.9,
            'steps': [
                'A: Airway with C-spine control',
                'B: Breathing and ventilation',
                'C: Circulation with hemorrhage control',
                'D: Disability (GCS, pupils)',
                'E: Exposure and environment'
            ],
            'contraindications': [],
            'source': 'ATLS 10th Ed.',
            'drugs': []  # No specific drugs mentioned
        },
        'hemorrhage_control': {
            'title': 'Hemorrhage Control',
            'priority': 'critical',
            'baseline_relevance': 0.95,
            'steps': [
                'Direct pressure',
                'Tourniquet for extremity bleeding',
                'Pelvic binder if suspected fracture',
                'REBOA if non-compressible torso hemorrhage',
                'Massive transfusion protocol'
            ],
            'contraindications': [],
            'source': 'EAST Guidelines',
            'drugs': []  # Massive transfusion may involve blood products, but no specific drugs listed
        },
        'tbi': {
            'title': 'TBI Protocol',
            'priority': 'urgent',
            'baseline_relevance': 0.85,
            'steps': [
                'Maintain SBP > 90 mmHg',
                'Maintain SpO2 > 90%',
                'Elevate head of bed 30°',
                'Mannitol or hypertonic saline for herniation',
                'Neurosurgery consult'
            ],
            'contraindications': ['Hypotension', 'Hypoxia'],
            'source': 'Brain Trauma Foundation 2016',
            'drugs': ['mannitol', 'hypertonic saline']
        },
        'pelvic_fracture': {
            'title': 'Pelvic Fracture Protocol',
            'priority': 'urgent',
            'baseline_relevance': 0.8,
            'steps': [
                'Pelvic binder',
                'FAST exam',
                'Transfusion if hemodynamically unstable',
                'Angiography/embolization if contrast extravasation',
                'Orthopedic consult'
            ],
            'contraindications': [],
            'source': 'EAST Guidelines',
            'drugs': []  # No specific drugs; contrast may be used but not a medication per se
        }
    },
    'respiratory': {
        'copd': {
            'title': 'COPD Exacerbation',
            'priority': 'urgent',
            'baseline_relevance': 0.75,
            'steps': [
                'Oxygen to SpO2 88-92%',
                'Albuterol/ipratropium nebulized',
                'Systemic corticosteroids',
                'Antibiotics if purulent sputum',
                'Non-invasive ventilation if hypercapnia'
            ],
            'contraindications': ['Oxygen sensitivity (rare)'],
            'source': 'GOLD 2023',
            'drugs': ['albuterol', 'ipratropium', 'corticosteroids', 'antibiotics']
        },
        'pe': {
            'title': 'Pulmonary Embolism',
            'priority': 'critical',
            'baseline_relevance': 0.9,
            'steps': [
                'Oxygen',
                'Anticoagulation (heparin)',
                'Thrombolytics if massive PE with hypotension',
                'Embolectomy if contraindication to lytics',
                'Bed rest'
            ],
            'contraindications': ['Active bleeding', 'Recent surgery'],
            'source': 'ACP 2023',
            'drugs': ['heparin', 'thrombolytics']
        },
        'asthma': {
            'title': 'Acute Asthma Attack',
            'priority': 'urgent',
            'baseline_relevance': 0.8,
            'steps': [
                'Oxygen to SpO2 > 90%',
                'Albuterol nebulized continuous',
                'Ipratropium bromide',
                'Systemic corticosteroids',
                'Magnesium sulfate if severe'
            ],
            'contraindications': [],
            'source': 'NAEPP EPR-3 2007',
            'drugs': ['albuterol', 'ipratropium', 'corticosteroids', 'magnesium sulfate']
        },
        'pneumothorax': {
            'title': 'Pneumothorax',
            'priority': 'urgent',
            'baseline_relevance': 0.8,
            'steps': [
                'Oxygen',
                'Needle decompression if tension',
                'Chest tube',
                'Chest x-ray confirmation'
            ],
            'contraindications': [],
            'source': 'ACCP 2020',
            'drugs': []  # No drugs listed
        }
    },
    'neuro': {
        'ischemic_stroke': {
            'title': 'Acute Ischemic Stroke',
            'priority': 'critical',
            'baseline_relevance': 0.95,
            'steps': [
                'Last known well time',
                'Non-contrast head CT',
                'NIHSS score',
                'tPA if within 4.5 hours and no contraindications',
                'Mechanical thrombectomy if large vessel occlusion',
                'Admit to stroke unit'
            ],
            'contraindications': ['ICH on CT', 'Recent surgery', 'Coagulopathy'],
            'source': 'AHA/ASA 2023',
            'drugs': ['tPA']  # tissue plasminogen activator
        },
        'hemorrhagic_stroke': {
            'title': 'Hemorrhagic Stroke',
            'priority': 'critical',
            'baseline_relevance': 0.95,
            'steps': [
                'Reverse anticoagulation',
                'BP control (SBP <140)',
                'Neurosurgery consult',
                'Elevate head of bed',
                'Seizure prophylaxis'
            ],
            'contraindications': [],
            'source': 'AHA/ASA 2023',
            'drugs': []  # Reversal agents depend on anticoagulant, not specified; BP meds not listed
        },
        'seizure': {
            'title': 'Seizure Protocol',
            'priority': 'urgent',
            'baseline_relevance': 0.8,
            'steps': [
                'Protect airway',
                'Benzodiazepine (lorazepam IV)',
                'If persists, second-line (fosphenytoin, levetiracetam)',
                'Treat underlying cause',
                'EEG if status epilepticus'
            ],
            'contraindications': [],
            'source': 'AAN 2017',
            'drugs': ['lorazepam', 'fosphenytoin', 'levetiracetam']
        },
        'meningitis': {
            'title': 'Meningitis Protocol',
            'priority': 'critical',
            'baseline_relevance': 0.9,
            'steps': [
                'Blood cultures',
                'Empiric antibiotics (ceftriaxone + vancomycin)',
                'Dexamethasone if suspected pneumococcal',
                'Lumbar puncture after CT if no contraindication',
                'Respiratory isolation'
            ],
            'contraindications': ['Increased ICP (relative)'],
            'source': 'CDC / IDSA',
            'drugs': ['ceftriaxone', 'vancomycin', 'dexamethasone']
        }
    }
}