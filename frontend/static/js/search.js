async function loadUserInfo() {
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            window.location.href = '/';
            return;
        }
        
        const data = await response.json();
        if (data.user.is_admin) {
            document.getElementById('admin-link').style.display = 'inline-block';
        }
    } catch (error) {
        window.location.href = '/';
    }
}

function switchSearchMethod(method, evt) {
    document.querySelectorAll('.method-card').forEach(card => {
        card.classList.remove('active');
    });
    document.querySelectorAll('.search-option').forEach(option => {
        option.classList.remove('active');
    });
    
    if (evt && evt.target) {
        evt.target.closest('.method-card').classList.add('active');
    } else {
        document.querySelector(`.method-card[onclick*="${method}"]`)?.classList.add('active');
    }
    
    document.getElementById(`${method}-search`).classList.add('active');
}

document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const caseDescription = document.getElementById('case-description').value;
    
    if (!caseDescription.trim()) {
        alert('Veuillez décrire votre cas');
        return;
    }
    
    const searchBtn = document.getElementById('search-btn');
    const loading = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    
    searchBtn.disabled = true;
    searchBtn.textContent = 'Analyse en cours...';
    loading.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    // Utiliser EventSource pour le streaming SSE
    try {
        // Créer une requête POST pour initier le streaming
        const response = await fetch('/api/search/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ query: caseDescription })
        });
        
        if (!response.ok) {
            throw new Error('Erreur de connexion');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Garder la dernière ligne incomplète
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    try {
                        const message = JSON.parse(data);
                        
                        if (message.type === 'progress' || message.type === 'thinking') {
                            // Afficher le message de progression
                            const loadingText = document.querySelector('#loading p');
                            if (loadingText) {
                                loadingText.innerHTML = `
                                    <span style="display: inline-block; animation: pulse 1.5s ease-in-out infinite;">🔍</span>
                                    ${message.message}
                                `;
                            }
                        } else if (message.type === 'complete') {
                            // Afficher les résultats finaux
                            loading.style.display = 'none';
                            searchBtn.disabled = false;
                            searchBtn.textContent = 'Rechercher des cas similaires';
                            displayResults(message.result);
                        } else if (message.type === 'error') {
                            loading.style.display = 'none';
                            searchBtn.disabled = false;
                            searchBtn.textContent = 'Rechercher des cas similaires';
                            displayError(message.message);
                        }
                    } catch (e) {
                        console.error('Erreur de parsing:', e);
                    }
                }
            }
        }
        
    } catch (error) {
        loading.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.textContent = 'Rechercher des cas similaires';
        displayError('Erreur de connexion au serveur: ' + error.message);
    }
});

document.getElementById('file-search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('case-file');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Veuillez sélectionner un fichier');
        return;
    }
    
    const searchBtn = document.getElementById('file-search-btn');
    const loading = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    
    searchBtn.disabled = true;
    searchBtn.textContent = 'Analyse en cours...';
    loading.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/search/file', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        loading.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.textContent = 'Analyser le document';
        
        if (response.ok) {
            displayResults(data);
        } else {
            displayError(data.error || 'Erreur lors de l\'analyse du fichier');
        }
    } catch (error) {
        loading.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.textContent = 'Analyser le document';
        displayError('Erreur de connexion au serveur');
    }
});

function displayResults(data) {
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');
    
    if (data.error) {
        resultsContent.innerHTML = `
            <div class="alert alert-error">
                <strong>Erreur:</strong> ${data.error}
            </div>
        `;
    } else if (data.success) {
        let html = `
            <div class="section-blue mb-3">
                <h3><i class="bi bi-database"></i> Base de données analysée</h3>
                <p style="margin: 0; font-size: 0.95rem;">
                    <strong>${data.total_cases_in_db || 0}</strong> cas au total dans la base de données
                    <br>
                    <strong>${data.total_cases_analyzed || 0}</strong> cas analysés par l'IA
                </p>
            </div>
        `;
        
        // Afficher les cas similaires trouvés
        if (data.similar_cases && data.similar_cases.length > 0) {
            html += `
                <div class="section-green mb-3">
                    <h3><i class="bi bi-search"></i> Cas similaires trouvés (${data.similar_cases.length})</h3>
            `;
            
            data.similar_cases.forEach((caseItem, index) => {
                const reason = data.similarity_reasons ? data.similarity_reasons[caseItem.ref] : '';
                html += `
                    <div class="card mb-2" style="border-left: 3px solid #10b981;">
                        <h4 style="color: #10b981; margin-bottom: 0.5rem;">
                            ${index + 1}. Réf ${caseItem.ref} - ${caseItem.titre || 'Sans titre'}
                        </h4>
                        <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 0.5rem;">
                            <strong>Juridiction:</strong> ${caseItem.juridiction || 'N/A'} | 
                            <strong>Date:</strong> ${caseItem.date_decision || 'N/A'}
                        </div>
                        ${reason ? `
                            <div style="background: #f0fdf4; padding: 0.75rem; border-radius: 0.375rem; margin-top: 0.5rem;">
                                <strong style="color: #059669;">Raison de similarité:</strong>
                                <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem;">${reason}</p>
                            </div>
                        ` : ''}
                        <div style="margin-top: 0.75rem;">
                            <a href="/case/${caseItem.id}" class="btn btn-sm btn-primary">
                                Voir le cas complet
                            </a>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
        } else {
            html += `
                <div class="alert alert-info">
                    <strong>Aucun cas similaire trouvé</strong> dans la base de données analysée.
                </div>
            `;
        }
        
        // Afficher l'analyse
        if (data.analysis) {
            html += `
                <div class="section-purple mb-3">
                    <h3><i class="bi bi-lightbulb"></i> Analyse juridique</h3>
                    <div style="white-space: pre-wrap; font-size: 0.9rem; line-height: 1.6;">
                        ${data.analysis}
                    </div>
                </div>
            `;
        }
        
        // Afficher les recommandations
        if (data.recommendations) {
            html += `
                <div class="section-orange mb-3">
                    <h3><i class="bi bi-star"></i> Recommandations</h3>
                    <div style="white-space: pre-wrap; font-size: 0.9rem; line-height: 1.6;">
                        ${data.recommendations}
                    </div>
                </div>
            `;
        }
        
        html += `
            <p style="margin-top: 1.5rem; font-size: 0.8rem; color: #6b7280; text-align: center;">
                <i class="bi bi-cpu"></i> Analyse réalisée par ${data.model_used || 'IA'}
            </p>
        `;
        
        resultsContent.innerHTML = html;
    } else {
        resultsContent.innerHTML = `
            <div class="card">
                <p style="color: #6b7280;">Aucun résultat trouvé</p>
            </div>
        `;
    }
    
    resultsContainer.style.display = 'block';
}

function displayError(error) {
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');
    
    resultsContent.innerHTML = `
        <div class="alert alert-error">
            ${error}
        </div>
    `;
    
    resultsContainer.style.display = 'block';
}

function formatAIResponse(response) {
    return response
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        window.location.href = '/';
    } catch (error) {
        window.location.href = '/';
    }
});

loadUserInfo();
