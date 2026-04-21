// API Configuration
const API_BASE = 'http://localhost:5000/api';

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(`${btn.dataset.tab}-panel`).classList.add('active');
    });
});

// SHA-512 Computation
async function computeSHA512() {
    const input = document.getElementById('sha512-input').value;
    
    if (!input) {
        alert('Please enter a message');
        return;
    }
    
    showLoading('sha512-steps');
    
    try {
        const response = await fetch(`${API_BASE}/sha512`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input })
        });
        
        const data = await response.json();
        displaySHA512Results(data);
    } catch (error) {
        displayError('sha512-steps', error);
    }
}

// CMAC Computation
async function computeCMAC() {
    const input = document.getElementById('cmac-input').value;
    const key = document.getElementById('cmac-key').value;
    
    if (!key || key.length < 16) {
        alert('Please enter a key with at least 16 characters');
        return;
    }
    
    showLoading('cmac-steps');
    
    try {
        const response = await fetch(`${API_BASE}/cmac`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input, key: key })
        });
        
        const data = await response.json();
        displayCMACResults(data);
    } catch (error) {
        displayError('cmac-steps', error);
    }
}

// Display SHA-512 Results
function displaySHA512Results(data) {
    document.getElementById('sha512-results').style.display = 'block';
    document.getElementById('sha512-result-input').textContent = `"${data.input}" (${data.input_bytes} bytes)`;
    document.getElementById('sha512-result-hash').textContent = data.final_hash;
    
    const stepsContainer = document.getElementById('sha512-steps');
    stepsContainer.innerHTML = '';
    
    data.steps.forEach((step, index) => {
        const stepCard = createStepCard(index + 1, step.step, step.description, step.value, step.details);
        stepsContainer.appendChild(stepCard);
    });
}

// Display CMAC Results
function displayCMACResults(data) {
    document.getElementById('cmac-results').style.display = 'block';
    document.getElementById('cmac-result-input').textContent = `"${data.input}"`;
    document.getElementById('cmac-result-key').textContent = `"${data.key}"`;
    document.getElementById('cmac-result-hash').textContent = data.cmac;
    
    // Key derivation info
    document.getElementById('cmac-L').textContent = data.L;
    document.getElementById('cmac-K1').textContent = data.K1;
    document.getElementById('cmac-K2').textContent = data.K2;
    
    const stepsContainer = document.getElementById('cmac-steps');
    stepsContainer.innerHTML = '';
    
    data.steps.forEach((step, index) => {
        const stepCard = createStepCard(index + 1, step.step, step.description, step.value, step.details, 'cmac');
        stepsContainer.appendChild(stepCard);
    });
}

// Create step card element
function createStepCard(number, title, description, value, details, prefix = 'sha512') {
    const card = document.createElement('div');
    card.className = 'step-card';
    
    const colorClass = prefix === 'cmac' ? 'cmac-' : '';
    
    card.innerHTML = `
        <div class="step-header" onclick="toggleStep(this.parentElement)">
            <h4>
                <span class="step-number">${number}</span>
                ${title}
            </h4>
            <span class="step-toggle">▼</span>
        </div>
        <div class="step-content">
            <p class="step-description">${description}</p>
            <div class="step-value">
                <code>${escapeHtml(value)}</code>
            </div>
            <p class="step-details">${escapeHtml(details)}</p>
        </div>
    `;
    
    return card;
}

// Toggle step expansion
function toggleStep(card) {
    card.classList.toggle('expanded');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show loading state
function showLoading(containerId) {
    document.getElementById(containerId).innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Computing...</p>
        </div>
    `;
    document.getElementById(containerId.replace('-steps', '-results')).style.display = 'block';
}

// Display error
function displayError(containerId, error) {
    document.getElementById(containerId).innerHTML = `
        <div class="step-card" style="border-color: #ff6b6b;">
            <div class="step-header" style="background: rgba(255, 107, 107, 0.2);">
                <h4 style="color: #ff6b6b;">Error</h4>
            </div>
            <div class="step-content" style="max-height: none; padding: 20px;">
                <p style="color: #ff6b6b;">Failed to connect to backend. Make sure Flask server is running on port 5000.</p>
                <p style="color: #666; margin-top: 10px;">Error: ${error.message}</p>
            </div>
        </div>
    `;
    document.getElementById(containerId.replace('-steps', '-results')).style.display = 'block';
}

// Add enter key support for inputs
document.getElementById('sha512-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') computeSHA512();
});

document.getElementById('cmac-key').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') computeCMAC();
});