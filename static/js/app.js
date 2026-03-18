// static/js/app.js – fully updated with AACT source badge

// State
let currentPatientKey = 'cardiac';
let patientCache = {};
let lastQueryResults = [];
let lastQueryText = '';
let healthInterval = null;

// DOM elements
const patientTabs = document.querySelectorAll('.patient-tab');
const patientContent = document.getElementById('patientContent');
const chatMessages = document.getElementById('chatMessages');
const suggestionChips = document.getElementById('suggestionChips');
const queryInput = document.getElementById('queryInput');
const sendBtn = document.getElementById('sendQueryBtn');
const protocolsList = document.getElementById('protocolsList');
const protocolCountSpan = document.getElementById('protocolCount');
const statusIndicator = document.getElementById('statusIndicator');
const uptimeSpan = document.getElementById('uptime');
const modal = document.getElementById('protocolModal');
const modalDetail = document.getElementById('modalProtocolDetail');
const closeModal = document.querySelector('.close-modal');
const quickActions = document.querySelectorAll('.quick-btn');
const patientSearch = document.getElementById('patientSearch');
const searchResults = document.getElementById('patientSearchResults');
const protocolFilter = document.getElementById('protocolFilter');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadAndRenderPatient(currentPatientKey);

    patientTabs.forEach(tab => {
        tab.addEventListener('click', () => switchPatient(tab.dataset.patient));
    });

    sendBtn.addEventListener('click', handleQuery);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleQuery();
    });

    quickActions.forEach(btn => {
        btn.addEventListener('click', handleQuickAction);
    });

    closeModal.addEventListener('click', () => modal.classList.remove('show'));
    window.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('show');
    });

    patientSearch.addEventListener('input', debounce(handlePatientSearch, 300));
    protocolFilter.addEventListener('input', handleProtocolFilter);

    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && !e.shiftKey) {
            if (e.key === '1') switchPatient('cardiac');
            if (e.key === '2') switchPatient('trauma');
            if (e.key === '3') switchPatient('respiratory');
            if (e.key === '4') switchPatient('neuro');
        }
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            modal.classList.remove('show');
        }
    });

    pollHealth();
    healthInterval = setInterval(pollHealth, 15000);
});

function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

async function handlePatientSearch(e) {
    const query = e.target.value.trim();
    if (query.length < 2) {
        searchResults.innerHTML = '';
        return;
    }
    try {
        const patients = await apiSearchPatients(query);
        searchResults.innerHTML = patients.map(p => 
            `<div class="search-result-item" data-key="${p.key}">${p.name} (${p.esi})</div>`
        ).join('');
        document.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                switchPatient(item.dataset.key);
                patientSearch.value = '';
                searchResults.innerHTML = '';
            });
        });
    } catch (error) {
        console.error('Search failed', error);
    }
}

function handleProtocolFilter(e) {
    const filter = e.target.value.toLowerCase();
    if (!lastQueryResults.length) return;
    const filtered = lastQueryResults.filter(p => 
        p.title.toLowerCase().includes(filter) || 
        p.category.toLowerCase().includes(filter) ||
        p.priority.toLowerCase().includes(filter)
    );
    renderProtocols(filtered);
}

async function handleQuickAction(e) {
    const action = e.target.dataset.action;
    if (action === 'critical') {
        if (!lastQueryResults.length) {
            addChatMessage('No protocols to filter. Run a query first.', 'system');
            return;
        }
        const critical = lastQueryResults.filter(p => p.priority === 'critical');
        renderProtocols(critical);
        addChatMessage(`Showing only critical protocols (${critical.length} found).`, 'system');
    } else if (action === 'top3') {
        if (!lastQueryText) {
            addChatMessage('No previous query to refine.', 'system');
            return;
        }
        addChatMessage('Getting top 3...', 'system typing');
        protocolsList.innerHTML = '<div class="loading-spinner"></div>';
        try {
            const data = await apiQuery(currentPatientKey, lastQueryText, 55, 3);
            chatMessages.removeChild(chatMessages.lastChild);
            lastQueryResults = data.results;
            renderProtocols(data.results);
            addChatMessage(`Top 3 protocols:`, 'system');
        } catch (error) {
            chatMessages.removeChild(chatMessages.lastChild);
            protocolsList.innerHTML = '<div class="error">Failed</div>';
        }
    }
}

async function switchPatient(key) {
    if (key === currentPatientKey) return;
    patientTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.patient === key);
    });
    currentPatientKey = key;
    lastQueryResults = [];
    lastQueryText = '';
    await loadAndRenderPatient(key);
    protocolsList.innerHTML = '';
    protocolCountSpan.textContent = '0';
    addChatMessage(`Switched to patient: ${patientCache[key]?.name || key}`, 'system');
}

async function loadAndRenderPatient(key) {
    try {
        patientContent.innerHTML = '<div class="loading">Loading patient...</div>';
        if (!patientCache[key]) {
            patientCache[key] = await apiGetPatient(key);
        }
        const patient = patientCache[key];
        renderPatient(patient);
        renderSuggestions(key);
        loadAndRenderNotes(key);
        loadAndRenderSparklines(key);
    } catch (error) {
        patientContent.innerHTML = '<div class="error">Failed to load patient</div>';
    }
}

function renderPatient(patient) {
    const thresholds = {
        hr: { high: 110 }, bp_sys: { high: 160, low: 90 },
        spo2: { low: 90 }, rr: { high: 24 },
        temp: { high: 38.5 }, gcs: { low: 13 }
    };
    const vitals = patient.vitals;
    const isAlert = (vital, value) => {
        if (thresholds[vital]?.high && value >= thresholds[vital].high) return true;
        if (thresholds[vital]?.low && value <= thresholds[vital].low) return true;
        return false;
    };
    const html = `
        <div class="patient-name">${patient.name}</div>
        <div class="patient-demographics">${patient.age} ${patient.sex} • ${patient.esi}</div>
        <div class="vitals-grid">
            <div class="vital-card ${isAlert('hr', vitals.hr) ? 'alert-high' : ''}">
                <div class="vital-label">HR</div>
                <div class="vital-value">${vitals.hr}</div>
                <div class="vital-trend"><canvas class="sparkline-canvas" id="sparkline-hr" width="120" height="30"></canvas></div>
            </div>
            <div class="vital-card ${isAlert('bp_sys', vitals.bp_sys) ? 'alert-high' : ''}">
                <div class="vital-label">BP</div>
                <div class="vital-value">${vitals.bp_sys}/${vitals.bp_dia}</div>
                <div class="vital-trend"><canvas class="sparkline-canvas" id="sparkline-bp" width="120" height="30"></canvas></div>
            </div>
            <div class="vital-card ${isAlert('spo2', vitals.spo2) ? 'alert-high' : ''}">
                <div class="vital-label">SpO₂</div>
                <div class="vital-value">${vitals.spo2}%</div>
                <div class="vital-trend"><canvas class="sparkline-canvas" id="sparkline-spo2" width="120" height="30"></canvas></div>
            </div>
            <div class="vital-card ${isAlert('rr', vitals.rr) ? 'alert-high' : ''}">
                <div class="vital-label">RR</div>
                <div class="vital-value">${vitals.rr}</div>
                <div class="vital-trend"><canvas class="sparkline-canvas" id="sparkline-rr" width="120" height="30"></canvas></div>
            </div>
            <div class="vital-card ${isAlert('temp', vitals.temp) ? 'alert-high' : ''}">
                <div class="vital-label">Temp</div>
                <div class="vital-value">${vitals.temp}°C</div>
            </div>
            <div class="vital-card ${isAlert('gcs', vitals.gcs) ? 'alert-high' : ''}">
                <div class="vital-label">GCS</div>
                <div class="vital-value">${vitals.gcs}</div>
            </div>
        </div>
        <div class="history-section">
            <div class="section-title">HISTORY</div>
            ${patient.history.map(h => `<div class="history-item">${h}</div>`).join('')}
            ${patient.irrelevant_history.map(h => `<div class="history-item irrelevant">${h}</div>`).join('')}
        </div>
        <div class="allergies-section">
            <div class="section-title">ALLERGIES</div>
            ${patient.allergies.map(a => `<span class="allergy-item">${a}</span>`).join('')}
        </div>
        <div class="notes-section" id="notesSection">
            <div class="section-title">CLINICAL NOTES</div>
            <div id="notesList"></div>
            <div class="note-compose">
                <input type="text" id="noteAuthor" placeholder="Author" value="Dr. User">
                <input type="text" id="noteText" placeholder="Add note...">
                <button id="saveNoteBtn">SAVE</button>
            </div>
        </div>
    `;
    patientContent.innerHTML = html;
    document.getElementById('saveNoteBtn').addEventListener('click', saveNote);
    document.getElementById('noteText').addEventListener('keypress', (e) => {
        if (e.ctrlKey && e.key === 'Enter') saveNote();
    });
}

async function loadAndRenderSparklines(key) {
    try {
        const trend = await apiGetVitalsTrend(key);
        drawSparkline(document.getElementById('sparkline-hr'), trend.map(p => p.hr), { alertHigh: 110, alertLow: 50 });
        drawSparkline(document.getElementById('sparkline-bp'), trend.map(p => p.bp_sys), { alertHigh: 160, alertLow: 90 });
        drawSparkline(document.getElementById('sparkline-spo2'), trend.map(p => p.spo2), { alertLow: 90 });
        drawSparkline(document.getElementById('sparkline-rr'), trend.map(p => p.rr), { alertHigh: 24, alertLow: 8 });
    } catch (error) {
        console.error('Sparkline error', error);
    }
}

async function renderSuggestions(key) {
    try {
        const chips = await apiGetSuggestions(key);
        suggestionChips.innerHTML = chips.map(c => `<span class="chip" tabindex="0">${c}</span>`).join('');
        document.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', () => {
                queryInput.value = chip.textContent;
                handleQuery();
            });
        });
    } catch (error) {
        console.error('Suggestions error', error);
    }
}

async function loadAndRenderNotes(key) {
    try {
        const notes = await apiGetNotes(key);
        const now = Date.now() / 1000;
        const notesList = document.getElementById('notesList');
        notesList.innerHTML = notes.map(n => {
            const recent = (now - n.timestamp) < 300;
            return `<div class="note-item ${recent ? 'recent-note' : ''}">
                <div class="note-header"><span>${n.author}</span><span>${new Date(n.timestamp*1000).toLocaleTimeString()}</span></div>
                <div>${n.text}</div>
            </div>`;
        }).join('');
    } catch (error) {
        console.error('Notes error', error);
    }
}

async function saveNote() {
    const author = document.getElementById('noteAuthor').value.trim() || 'Clinician';
    const text = document.getElementById('noteText').value.trim();
    if (!text) return;
    try {
        await apiPostNote(currentPatientKey, author, text);
        document.getElementById('noteText').value = '';
        await loadAndRenderNotes(currentPatientKey);
    } catch (error) {
        alert('Failed to save note');
    }
}

async function handleQuery() {
    const query = queryInput.value.trim();
    if (!query) return;
    lastQueryText = query;
    addChatMessage(query, 'user');
    queryInput.value = '';
    addChatMessage('...', 'system typing');
    protocolsList.innerHTML = '<div class="loading-spinner"></div>';
    try {
        const data = await apiQuery(currentPatientKey, query, 55, 5);
        chatMessages.removeChild(chatMessages.lastChild);
        lastQueryResults = data.results;
        renderProtocols(data.results);
        addChatMessage(`Found ${data.results.length} matching protocols.`, 'system');
        protocolFilter.value = ''; // clear filter
    } catch (error) {
        chatMessages.removeChild(chatMessages.lastChild);
        protocolsList.innerHTML = '<div class="error">Query failed</div>';
        addChatMessage('Error processing query.', 'system');
    }
}

function addChatMessage(text, sender) {
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
    msg.textContent = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderProtocols(protocols) {
    protocolsList.innerHTML = '';
    protocolCountSpan.textContent = protocols.length;
    if (protocols.length === 0) {
        protocolsList.innerHTML = '<div class="empty-state">No protocols found.</div>';
        return;
    }
    protocols.forEach((p, idx) => {
        const icon = { cardiac: '❤️', trauma: '🩸', respiratory: '🫁', neuro: '🧠' }[p.category] || '📋';
        // Add source badge for AACT results
        const sourceBadge = p.source === 'clinicaltrials' 
            ? '<span class="source-badge">ClinicalTrials.gov</span>' 
            : '';
        const card = document.createElement('div');
        card.className = `protocol-card ${p.priority}`;
        card.setAttribute('data-priority', p.priority);
        card.style.animationDelay = `${idx * 0.05}s`;
        card.innerHTML = `
            <div class="protocol-title">${icon} ${p.title}</div>
            <div class="protocol-meta">
                <span class="protocol-priority">${p.priority}</span>
                <div class="protocol-score-container">
                    <span class="protocol-score">${p.score}%</span>
                    <div class="protocol-score-bar">
                        <div class="protocol-score-fill" style="width:${p.score}%"></div>
                    </div>
                </div>
            </div>
            ${sourceBadge}
        `;
        card.addEventListener('click', () => openProtocolModal(p));
        protocolsList.appendChild(card);
    });
}

function openProtocolModal(p) {
    const stepsHtml = p.steps.map((s, i) => `<li class="${i === 0 ? 'modal-step-highlight' : ''}">${s}</li>`).join('');
    modalDetail.innerHTML = `
        <div class="modal-protocol-title">${p.title}</div>
        <div class="modal-priority">Priority: ${p.priority}</div>
        <div class="modal-score">Match: ${p.score}%</div>
        <ol class="modal-steps">${stepsHtml}</ol>
        ${p.contraindications.length ? `<div class="modal-contraindications"><strong>Contraindications:</strong> ${p.contraindications.join(', ')}</div>` : ''}
        <div class="modal-source">Source: ${p.source}</div>
    `;
    modal.classList.add('show');
}

async function pollHealth() {
    try {
        const health = await apiHealth();
        statusIndicator.style.backgroundColor = 'var(--green)';
        uptimeSpan.textContent = health.uptime;
    } catch {
        statusIndicator.style.backgroundColor = 'var(--red)';
    }
}