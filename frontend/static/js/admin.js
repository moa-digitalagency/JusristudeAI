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
        
        if (!data.user.is_admin) {
            window.location.href = '/dashboard';
            return;
        }
    } catch (error) {
        window.location.href = '/';
    }
}

async function loadPendingUsers() {
    try {
        const response = await fetch('/api/auth/admin/users', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById('pending-users');
            
            if (data.users.length === 0) {
                container.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 2rem;">Aucun utilisateur en attente</p>';
                return;
            }
            
            container.innerHTML = data.users.map(user => `
                <div class="card" style="margin-bottom: 1rem;">
                    <h3 style="font-size: 1rem; margin-bottom: 0.5rem;">
                        ${user.first_name} ${user.last_name}
                    </h3>
                    <p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">
                        ${user.email}
                    </p>
                    <p style="font-size: 0.8rem; color: #9ca3af; margin-bottom: 1rem;">
                        Inscrit le: ${new Date(user.created_at).toLocaleDateString('fr-FR')}
                    </p>
                    <button class="btn-primary" onclick="approveUser(${user.id})">
                        Approuver
                    </button>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

async function approveUser(userId) {
    try {
        const response = await fetch(`/api/auth/admin/approve/${userId}`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadPendingUsers();
        } else {
            showAlert(data.error || 'Erreur lors de l\'approbation', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
}

document.getElementById('add-case-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        case_number: document.getElementById('case_number').value,
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        facts: document.getElementById('facts').value,
        decision: document.getElementById('decision').value,
        court: document.getElementById('court').value,
        date_decision: document.getElementById('date_decision').value,
        category: document.getElementById('category').value,
        keywords: document.getElementById('keywords').value
    };
    
    try {
        const response = await fetch('/api/cases', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            e.target.reset();
        } else {
            showAlert(data.error || 'Erreur lors de l\'ajout du cas', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
});

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

function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    
    alertContainer.innerHTML = `
        <div class="alert ${alertClass}">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}

loadUserInfo();
loadPendingUsers();
