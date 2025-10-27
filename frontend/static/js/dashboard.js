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
        document.getElementById('user-name').textContent = `${data.user.first_name} ${data.user.last_name}`;
        
        if (data.user.is_admin) {
            document.getElementById('admin-link').style.display = 'inline-block';
        }
    } catch (error) {
        console.error('Erreur:', error);
        window.location.href = '/';
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('total-cases').textContent = data.total_cases;
            document.getElementById('user-searches').textContent = data.user_searches;
        }
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
    }
}

async function loadRecentCases() {
    try {
        const response = await fetch('/api/cases?per_page=5', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const casesContainer = document.getElementById('recent-cases');
            
            if (data.cases.length === 0) {
                casesContainer.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 2rem;">Aucun cas trouvé</p>';
                return;
            }
            
            casesContainer.innerHTML = data.cases.map(c => `
                <div class="card" style="margin-bottom: 1rem; border-left: 4px solid #3b82f6;">
                    <h3 style="font-size: 1rem; margin-bottom: 0.5rem;">${c.title}</h3>
                    <div style="margin-bottom: 0.5rem;">
                        <span class="badge-cyan">${c.case_number}</span>
                        <span class="badge-green">${c.category}</span>
                    </div>
                    <p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">
                        ${c.description.substring(0, 150)}...
                    </p>
                    <p style="font-size: 0.8rem; color: #9ca3af;">
                        ${c.court} • ${new Date(c.date_decision).toLocaleDateString('fr-FR')}
                    </p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        window.location.href = '/';
    } catch (error) {
        console.error('Erreur:', error);
        window.location.href = '/';
    }
});

loadUserInfo();
loadStats();
loadRecentCases();
