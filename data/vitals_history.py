import time

# 10 readings at 3-minute intervals (30 minutes total)
base_time = time.time() - 1800  # 30 minutes ago

vitals_history = {
    'cardiac': [
        {'time': base_time + i*180, 'hr': 110 + i, 'bp_sys': 140 + i, 'spo2': 98 - i*0.1, 'rr': 20 + i*0.2}
        for i in range(10)
    ],
    'trauma': [
        {'time': base_time + i*180, 'hr': 120 + i*2, 'bp_sys': 110 - i*2, 'spo2': 95 - i*0.5, 'rr': 24 + i}
        for i in range(10)
    ],
    'respiratory': [
        {'time': base_time + i*180, 'hr': 100 + i, 'bp_sys': 130 - i, 'spo2': 92 - i*0.8, 'rr': 22 + i*0.5}
        for i in range(10)
    ],
    'neuro': [
        {'time': base_time + i*180, 'hr': 90 + i*0.5, 'bp_sys': 170 + i*2, 'spo2': 97 - i*0.1, 'rr': 18 + i*0.2}
        for i in range(10)
    ]
}