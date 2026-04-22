// Tab switching functionality
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Add active to clicked
        btn.classList.add('active');
        const tabId = btn.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

// Toggle card collapse/expand
function toggleCard(header) {
    header.classList.toggle('collapsed');
    const content = header.nextElementSibling;
    content.classList.toggle('collapsed');
}

// Render step-by-step results
function renderSteps(steps, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = steps.map((step, index) => `
        <div class="step-item">
            <div class="step-title">
                <span class="step-number">${index + 1}</span>
                ${step.step}
            </div>
            ${step.description ? `<div class="step-desc">${step.description}</div>` : ''}
            ${step.calculation ? `<div class="step-calc">${step.calculation}</div>` : ''}
            ${step.result ? `<div class="step-result">Result: ${step.result}</div>` : ''}
        </div>
    `).join('');
}

// RSA Calculation
async function calculateRSA() {
    const p = document.getElementById('rsa-p').value;
    const q = document.getElementById('rsa-q').value;
    const message = document.getElementById('rsa-message').value;

    if (!p || !q || !message) {
        alert('Please fill in all fields');
        return;
    }

    const btn = event.target;
    btn.innerHTML = '<span class="loading"></span> Calculating...';
    btn.disabled = true;

    try {
        const response = await fetch('/rsa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ p: parseInt(p), q: parseInt(q), message })
        });

        const data = await response.json();

        // Key Generation
        renderSteps(data.key_generation.steps, 'key-gen-steps');
        document.getElementById('public-key').textContent = 
            `(${data.key_generation.public_key.e}, ${data.key_generation.public_key.n})`;
        document.getElementById('private-key').textContent = 
            `(${data.key_generation.private_key.d}, ${data.key_generation.private_key.n})`;

        // Encryption
        renderSteps(data.encryption.steps, 'encryption-steps');
        document.getElementById('ciphertext-result').textContent = data.encryption.ciphertext;

        // Decryption
        renderSteps(data.decryption.steps, 'decryption-steps');
        document.getElementById('decrypted-result').textContent = data.decryption.plaintext;

        // Scroll to results
        document.getElementById('rsa-results').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during calculation');
    } finally {
        btn.innerHTML = '<span class="btn-icon"></span> Calculate RSA';
        btn.disabled = false;
    }
}

// Diffie-Hellman Calculation
async function calculateDH() {
    const p = document.getElementById('dh-p').value;
    const g = document.getElementById('dh-g').value;
    const xa = document.getElementById('dh-xa').value;
    const xb = document.getElementById('dh-xb').value;

    if (!p || !g || !xa || !xb) {
        alert('Please fill in all fields');
        return;
    }

    const btn = event.target;
    btn.innerHTML = '<span class="loading"></span> Calculating...';
    btn.disabled = true;

    try {
        const response = await fetch('/dh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                p: parseInt(p), 
                g: parseInt(g), 
                xa: parseInt(xa), 
                xb: parseInt(xb) 
            })
        });

        const data = await response.json();

        // Steps
        renderSteps(data.steps, 'dh-steps');

        // Alice
        document.getElementById('alice-private').textContent = document.getElementById('dh-xa').value;
        document.getElementById('alice-public').textContent = data.public_keys.ya;

        // Bob
        document.getElementById('bob-private').textContent = document.getElementById('dh-xb').value;
        document.getElementById('bob-public').textContent = data.public_keys.yb;

        // Shared Secret
        document.getElementById('shared-secret').textContent = data.shared_secret;

        // Scroll to results
        document.getElementById('dh-results').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during calculation');
    } finally {
        btn.innerHTML = '<span class="btn-icon"></span> Calculate Diffie-Hellman';
        btn.disabled = false;
    }
}

// Initialize tooltips
document.querySelectorAll('.tooltip').forEach(tooltip => {
    tooltip.addEventListener('mouseenter', (e) => {
        const rect = e.target.getBoundingClientRect();
        const tooltipText = e.target.getAttribute('data-tooltip');
        // Tooltip is handled via CSS :hover
    });
});