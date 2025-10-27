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
        const casesResponse = await fetch('/api/cases', {
            credentials: 'include'
        });
        
        if (casesResponse.ok) {
            const casesData = await casesResponse.json();
            document.getElementById('total-cases').textContent = casesData.cases.length;
            document.getElementById('recent-count').textContent = Math.min(casesData.cases.length, 10);
        }
        
        document.getElementById('user-searches').textContent = 0;
        
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
    }
}

async function loadRecentCases() {
    try {
        const response = await fetch('/api/cases', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const casesContainer = document.getElementById('recent-cases');
            
            if (data.cases.length === 0) {
                casesContainer.innerHTML = `
                    <p style="color: #6b7280; text-align: center; padding: 2rem;">
                        <i class="fas fa-inbox"></i> Aucun cas trouvé
                    </p>
                `;
                return;
            }
            
            const recentCases = data.cases.slice(0, 10);
            
            casesContainer.innerHTML = `
                <table class="recent-cases-table">
                    <thead>
                        <tr>
                            <th><i class="fas fa-hashtag"></i> Référence</th>
                            <th><i class="fas fa-heading"></i> Titre</th>
                            <th><i class="fas fa-landmark"></i> Juridiction</th>
                            <th><i class="fas fa-calendar"></i> Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${recentCases.map(c => `
                            <tr>
                                <td><strong>${c.ref || 'N/A'}</strong></td>
                                <td>${c.titre || 'Sans titre'}</td>
                                <td>${c.juridiction || 'N/A'}</td>
                                <td>${c.date_decision || 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        console.error('Erreur:', error);
        const casesContainer = document.getElementById('recent-cases');
        casesContainer.innerHTML = `
            <p style="color: #ef4444; text-align: center; padding: 2rem;">
                <i class="fas fa-exclamation-triangle"></i> Erreur lors du chargement des cas
            </p>
        `;
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
