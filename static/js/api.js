const API_BASE = '/api';

async function apiHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
}

async function apiGetPatients() {
    const res = await fetch(`${API_BASE}/patients`);
    return res.json();
}

async function apiGetPatient(key) {
    const res = await fetch(`${API_BASE}/patients/${key}`);
    return res.json();
}

async function apiGetVitalsTrend(key) {
    const res = await fetch(`${API_BASE}/patients/${key}/vitals-trend`);
    return res.json();
}

async function apiGetSuggestions(key) {
    const res = await fetch(`${API_BASE}/suggestions/${key}`);
    return res.json();
}

async function apiQuery(patientKey, query, threshold = 55, limit = 5) {
    const res = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient: patientKey, query, threshold, limit })
    });
    return res.json();
}

async function apiGetNotes(patientKey) {
    const res = await fetch(`${API_BASE}/notes/${patientKey}`);
    return res.json();
}

async function apiPostNote(patientKey, author, text) {
    const res = await fetch(`${API_BASE}/notes/${patientKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author, text })
    });
    return res.json();
}

// New function for patient search
async function apiSearchPatients(query) {
    const res = await fetch(`${API_BASE}/patients/search?q=${encodeURIComponent(query)}`);
    return res.json();
}