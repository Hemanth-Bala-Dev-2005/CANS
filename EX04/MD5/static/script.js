/**
 * MD5 Hashing Process Demonstration - Frontend Logic
 * Handles API communication and step-by-step visualization
 */

// DOM Elements
const elements = {
    messageInput: document.getElementById('messageInput'),
    charCount: document.getElementById('charCount'),
    byteCount: document.getElementById('byteCount'),
    hashButton: document.getElementById('hashButton'),
    clearButton: document.getElementById('clearButton'),
    hashOutput: document.getElementById('hashOutput'),
    hashLength: document.getElementById('hashLength'),
    copyHash: document.getElementById('copyHash'),
    processSection: document.getElementById('processSection'),
    stepTimeline: document.getElementById('stepTimeline'),
    stepDetailPanel: document.getElementById('stepDetailPanel'),
    stepTitle: document.getElementById('stepTitle'),
    stepDescription: document.getElementById('stepDescription'),
    stepValues: document.getElementById('stepValues'),
    binarySection: document.getElementById('binarySection'),
    stepBinary: document.getElementById('stepBinary'),
    hexSection: document.getElementById('hexSection'),
    stepHex: document.getElementById('stepHex'),
    prevStep: document.getElementById('prevStep'),
    nextStep: document.getElementById('nextStep'),
    currentStep: document.getElementById('currentStep'),
    totalSteps: document.getElementById('totalSteps'),
    loadingOverlay: document.getElementById('loadingOverlay')
};

// State
let currentSteps = [];
let currentStepIndex = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateCharCount();
});

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Input changes
    elements.messageInput.addEventListener('input', updateCharCount);
    
    // Hash button
    elements.hashButton.addEventListener('click', computeMD5);
    
    // Clear button
    elements.clearButton.addEventListener('click', clearAll);
    
    // Copy hash
    elements.copyHash.addEventListener('click', copyHashToClipboard);
    
    // Navigation buttons
    elements.prevStep.addEventListener('click', () => navigateStep(-1));
    elements.nextStep.addEventListener('click', () => navigateStep(1));
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            computeMD5();
        }
    });
}

/**
 * Update character and byte count display
 */
function updateCharCount() {
    const message = elements.messageInput.value;
    const charCount = message.length;
    const byteCount = new Blob([message]).size;
    
    elements.charCount.textContent = `${charCount} character${charCount !== 1 ? 's' : ''}`;
    elements.byteCount.textContent = `${byteCount} byte${byteCount !== 1 ? 's' : ''}`;
}

/**
 * Compute MD5 hash via API
 */
async function computeMD5() {
    const message = elements.messageInput.value;
    
    if (!message.trim()) {
        showError('Please enter a message to hash');
        return;
    }
    
    // Show loading
    elements.loadingOverlay.style.display = 'flex';
    
    try {
        const response = await fetch('/api/hash', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error('Failed to compute hash');
        }
        
        const data = await response.json();
        
        // Update results
        displayResults(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        elements.loadingOverlay.style.display = 'none';
    }
}

/**
 * Display hash results and steps
 */
function displayResults(data) {
    // Update hash output
    elements.hashOutput.textContent = data.hash;
    elements.hashLength.textContent = '128 bits';
    
    // Store steps
    currentSteps = data.steps;
    currentStepIndex = 0;
    
    // Render timeline
    renderStepTimeline();
    
    // Show first step
    if (currentSteps.length > 0) {
        displayStep(0);
        updateNavigation();
    }
}

/**
 * Render step timeline
 */
function renderStepTimeline() {
    elements.stepTimeline.innerHTML = '';
    
    currentSteps.forEach((step, index) => {
        const item = document.createElement('div');
        
        // Check if this is a section header
        if (step.title.includes('Step 5') || step.title.includes('Step 6') || 
            step.title.includes('Step 7') || step.title.includes('  Round') ||
            step.title.includes('  Update')) {
            item.className = 'step-item section-marker';
            item.textContent = step.title;
        } else {
            item.className = 'step-item';
            item.textContent = step.title;
            item.addEventListener('click', () => {
                currentStepIndex = index;
                displayStep(index);
                updateNavigation();
                updateTimelineActive();
            });
        }
        
        elements.stepTimeline.appendChild(item);
    });
    
    elements.totalSteps.textContent = currentSteps.length;
}

/**
 * Display a specific step's details
 */
function displayStep(index) {
    const step = currentSteps[index];
    
    // Update header
    elements.stepTitle.textContent = step.title;
    elements.stepDescription.textContent = step.description || '';
    
    // Update values
    elements.stepValues.innerHTML = '';
    if (step.values && step.values.length > 0) {
        document.getElementById('valuesSection').style.display = 'block';
        step.values.forEach(value => {
            const li = document.createElement('li');
            li.textContent = value;
            elements.stepValues.appendChild(li);
        });
    } else {
        document.getElementById('valuesSection').style.display = 'none';
    }
    
    // Update binary
    if (step.binary) {
        elements.binarySection.style.display = 'block';
        elements.stepBinary.textContent = step.binary;
    } else {
        elements.binarySection.style.display = 'none';
    }
    
    // Update hex values
    if (step.hex_values && step.hex_values.length > 0) {
        elements.hexSection.style.display = 'block';
        elements.stepHex.textContent = step.hex_values.join('\n\n');
    } else {
        elements.hexSection.style.display = 'none';
    }
    
    // Update current step indicator
    elements.currentStep.textContent = index + 1;
    
    // Update timeline active state
    updateTimelineActive();
}

/**
 * Update timeline active state
 */
function updateTimelineActive() {
    const items = elements.stepTimeline.querySelectorAll('.step-item');
    items.forEach((item, index) => {
        if (index === currentStepIndex) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

/**
 * Navigate between steps
 */
function navigateStep(direction) {
    const newIndex = currentStepIndex + direction;
    
    if (newIndex >= 0 && newIndex < currentSteps.length) {
        currentStepIndex = newIndex;
        displayStep(newIndex);
        updateNavigation();
    }
}

/**
 * Update navigation button states
 */
function updateNavigation() {
    elements.prevStep.disabled = currentStepIndex === 0;
    elements.nextStep.disabled = currentStepIndex === currentSteps.length - 1;
}

/**
 * Clear all inputs and results
 */
function clearAll() {
    elements.messageInput.value = '';
    elements.hashOutput.textContent = '—';
    elements.hashLength.textContent = '0 bits';
    elements.charCount.textContent = '0 characters';
    elements.byteCount.textContent = '0 bytes';
    
    currentSteps = [];
    currentStepIndex = 0;
    
    elements.stepTimeline.innerHTML = '';
    elements.stepTitle.textContent = 'Select a step to view details';
    elements.stepDescription.textContent = '';
    elements.stepValues.innerHTML = '';
    elements.binarySection.style.display = 'none';
    elements.hexSection.style.display = 'none';
    elements.currentStep.textContent = '0';
    elements.totalSteps.textContent = '0';
    
    elements.prevStep.disabled = true;
    elements.nextStep.disabled = true;
}

/**
 * Copy hash to clipboard
 */
function copyHashToClipboard() {
    const hash = elements.hashOutput.textContent;
    
    if (hash && hash !== '—') {
        navigator.clipboard.writeText(hash).then(() => {
            // Visual feedback
            const originalText = elements.copyHash.innerHTML;
            elements.copyHash.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 6L9 17l-5-5"/>
                </svg>
            `;
            
            setTimeout(() => {
                elements.copyHash.innerHTML = originalText;
            }, 1500);
        });
    }
}

/**
 * Show error message
 */
function showError(message) {
    alert(message);
}

// Expose for debugging
window.md5Demo = {
    computeMD5,
    clearAll
};