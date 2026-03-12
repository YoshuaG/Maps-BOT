const API_BASE_URL = window.location.origin + '/api'; // Use dynamic origin based on where the frontend is loaded

// Elements
const form = document.getElementById('search-form');
const btnSearch = document.getElementById('btn-search');
const btnText = document.querySelector('.btn-text');
const spinner = document.getElementById('search-spinner');
const logsContainer = document.getElementById('logs-container');
const statusIndicator = document.querySelector('.status-indicator');
const resultsSection = document.getElementById('results-section');
const resultsGrid = document.getElementById('results-grid');
const resultCount = document.getElementById('result-count');
const exportBtns = document.querySelectorAll('.export-btn');
const toast = document.getElementById('toast');

// Global state
let pollInterval = null;
let lastLogCount = 0;

// Log Formatter
function formatLog(message) {
    let className = 'log-entry';
    if (message.includes('[✔]')) className += ' success';
    else if (message.includes('[!]')) className += ' error';
    else if (message.includes('🧠')) className += ' highlight';
    else if (message.includes('Aguardando')) className += ' system';
    return `<p class="${className}">${message}</p>`;
}

function updateLogs(logs) {
    if (!logs || logs.length === 0) return;
    
    // Only append new logs
    const newLogs = logs.slice(lastLogCount);
    if (newLogs.length > 0) {
        if (lastLogCount === 0) logsContainer.innerHTML = ''; // Clear initial message
        
        newLogs.forEach(log => {
            logsContainer.insertAdjacentHTML('beforeend', formatLog(log));
        });
        
        lastLogCount = logs.length;
        logsContainer.scrollTop = logsContainer.scrollHeight; // Auto-scroll
    }
}

// Show Toast
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Render Results
function renderResults(results) {
    if (!results || results.length === 0) return;
    
    resultsSection.classList.remove('hidden');
    resultCount.textContent = `${results.length} locais encontrados`;
    resultsGrid.innerHTML = '';
    
    results.forEach((item, index) => {
        // Status Badge Logic
        const statusText = item.status_aberto || 'Desconhecido';
        let statusClass = '';
        let icon = '⚪';
        
        if (statusText.toLowerCase().includes('aberto')) {
            statusClass = 'status-aberto';
            icon = '🟢';
        } else if (statusText.toLowerCase().includes('fechado')) {
            statusClass = 'status-fechado';
            icon = '🔴';
        }
        
        const dist = item.distancia_km ? `${item.distancia_km.toFixed(1)} km` : 'N/A';
        const rating = item.avaliacao || 'N/A';
        const phone = item.telefone || 'Sem telefone';
        const link = item.link && item.link !== 'Link indisponível' ? item.link : '#';

        const cardHTML = `
            <div class="result-card">
                <h3 class="card-title">${index + 1}. ${item.nome || 'N/A'}</h3>
                <div class="card-info">
                    <div class="info-row">
                        <span>⭐ ${rating}</span>
                        <span style="color: var(--border-light)">|</span>
                        <span>📍 ${dist}</span>
                    </div>
                    <div class="info-row">
                        <span>📞 ${phone}</span>
                    </div>
                    ${statusText !== 'Desconhecido' ? 
                        `<div class="info-row"><span class="status-badge ${statusClass}">${icon} ${statusText}</span></div>` : ''}
                </div>
                ${link !== '#' ? `<a href="${link}" target="_blank" class="card-link">🔗 Ver no Maps Módulo</a>` : ''}
            </div>
        `;
        
        resultsGrid.insertAdjacentHTML('beforeend', cardHTML);
    });
}

// Polling function to check status
async function pollStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
        const data = await response.json();
        
        updateLogs(data.logs);
        
        // If it stopped running
        if (!data.is_running) {
            clearInterval(pollInterval);
            pollInterval = null;
            
            // Reset UI
            btnSearch.disabled = false;
            btnText.textContent = 'Iniciar Busca Inteligente';
            spinner.classList.add('hidden');
            statusIndicator.textContent = 'Processo Concluído';
            statusIndicator.classList.remove('running');
            
            // Render results if any
            if (data.results && data.results.length > 0) {
                renderResults(data.results);
                showToast('Busca concluída com sucesso!');
            } else {
                showToast('A busca falhou ou não encontrou resultados.', 'error');
            }
        }
    } catch (error) {
        console.error("Error polling status:", error);
    }
}

// Form Submit Handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Prepare payload
    const payload = {
        query: document.getElementById('query').value.trim(),
        location: document.getElementById('location').value.trim(),
        radius: parseFloat(document.getElementById('radius').value) || 5.0,
        max_results: parseInt(document.getElementById('max_results').value) || 5,
        min_rating: parseFloat(document.getElementById('min_rating').value) || 0.0,
        apenas_abertos: document.getElementById('apenas_abertos').checked
    };
    
    // Update UI Loading State
    btnSearch.disabled = true;
    btnText.textContent = 'Buscando...';
    spinner.classList.remove('hidden');
    
    logsContainer.innerHTML = '';
    logsContainer.insertAdjacentHTML('beforeend', formatLog('[*] Enviando requisição para o servidor...'));
    lastLogCount = 0;
    
    statusIndicator.textContent = 'Executando';
    statusIndicator.classList.add('running');
    
    resultsSection.classList.add('hidden');
    resultsGrid.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao iniciar busca');
        }
        
        // Start polling
        if (!pollInterval) {
            pollInterval = setInterval(pollStatus, 1500); // Poll every 1.5 seconds
        }
        
    } catch (error) {
        showToast(error.message, 'error');
        
        btnSearch.disabled = false;
        btnText.textContent = 'Iniciar Busca Inteligente';
        spinner.classList.add('hidden');
        statusIndicator.textContent = 'Erro';
        statusIndicator.classList.remove('running');
        logsContainer.insertAdjacentHTML('beforeend', formatLog(`[!] Erro na comunicação com API: ${error.message}`));
    }
});

// Export Handling
exportBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
        const format = btn.getAttribute('data-format');
        
        try {
            // Trigger download
            window.open(`${API_BASE_URL}/export/${format}`, '_blank');
            showToast(`Exportação ${format.toUpperCase()} iniciada!`);
        } catch (error) {
            showToast('Erro ao exportar resultados.', 'error');
        }
    });
});
