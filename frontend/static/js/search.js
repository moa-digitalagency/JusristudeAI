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

document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const caseDescription = document.getElementById('case-description').value;
    const searchBtn = document.getElementById('search-btn');
    const loading = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    
    searchBtn.disabled = true;
    searchBtn.textContent = 'Recherche en cours...';
    loading.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ query: caseDescription })
        });
        
        const data = await response.json();
        
        loading.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.textContent = 'Rechercher des cas similaires';
        
        if (response.ok) {
            displayResults(data);
        } else {
            displayError(data.error || 'Erreur lors de la recherche');
        }
    } catch (error) {
        loading.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.textContent = 'Rechercher des cas similaires';
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
        resultsContent.innerHTML = `
            <div class="section-green mb-3">
                <h3>Analyse IA</h3>
                <div style="white-space: pre-wrap; font-size: 0.9rem; line-height: 1.6;">
                    ${formatAIResponse(data.ai_analysis)}
                </div>
                <p style="margin-top: 1rem; font-size: 0.8rem; color: #6b7280;">
                    Modèle utilisé: ${data.model_used}
                </p>
            </div>
        `;
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
