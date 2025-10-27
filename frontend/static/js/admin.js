let currentFilter = 'all';
let allCases = [];

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

function switchTab(tabName, evt) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    
    if (evt && evt.target) {
        evt.target.classList.add('active');
    } else {
        document.querySelector(`.tab[onclick*="${tabName}"]`)?.classList.add('active');
    }
    
    document.getElementById(tabName + '-tab').classList.add('active');
    
    if (tabName === 'users') {
        loadUsers(currentFilter, null);
    } else if (tabName === 'cases') {
        loadCases();
    }
}

async function loadUsers(filter = 'all', evt = null) {
    currentFilter = filter;
    
    document.querySelectorAll('.filters .btn-primary, .filters .btn-secondary').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-secondary');
    });
    
    if (evt && evt.target) {
        evt.target.classList.remove('btn-secondary');
        evt.target.classList.add('btn-primary');
    } else {
        const filterBtn = document.querySelector(`.filters button[onclick*="${filter}"]`);
        if (filterBtn) {
            filterBtn.classList.remove('btn-secondary');
            filterBtn.classList.add('btn-primary');
        }
    }
    
    try {
        const response = await fetch(`/api/auth/admin/users?status=${filter}`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById('users-list');
            
            if (data.users.length === 0) {
                container.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 2rem;">Aucun utilisateur trouvé</p>';
                return;
            }
            
            container.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Nom</th>
                            <th>Email</th>
                            <th>Statut</th>
                            <th>Rôle</th>
                            <th>Inscrit le</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.users.map(user => `
                            <tr>
                                <td>${user.first_name} ${user.last_name}</td>
                                <td>${user.email}</td>
                                <td>
                                    <span class="badge ${user.is_approved ? 'badge-green' : 'badge-yellow'}">
                                        ${user.is_approved ? 'Approuvé' : 'En attente'}
                                    </span>
                                </td>
                                <td>
                                    <span class="badge ${user.is_admin ? 'badge-cyan' : 'badge-gray'}">
                                        ${user.is_admin ? 'Admin' : 'Juriste'}
                                    </span>
                                </td>
                                <td>${new Date(user.created_at).toLocaleDateString('fr-FR')}</td>
                                <td>
                                    <div class="action-buttons">
                                        ${!user.is_approved ? `
                                            <button class="btn-primary btn-small" onclick="approveUser(${user.id})">
                                                Approuver
                                            </button>
                                        ` : `
                                            <button class="btn-secondary btn-small" onclick="suspendUser(${user.id})">
                                                Suspendre
                                            </button>
                                        `}
                                        <button class="btn-secondary btn-small" onclick="deleteUser(${user.id}, '${user.email}')">
                                            Supprimer
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement des utilisateurs', 'error');
    }
}

async function approveUser(userId) {
    if (!confirm('Confirmer l\'approbation de cet utilisateur ?')) return;
    
    try {
        const response = await fetch(`/api/auth/admin/approve/${userId}`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadUsers(currentFilter);
        } else {
            showAlert(data.error || 'Erreur lors de l\'approbation', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
}

async function suspendUser(userId) {
    if (!confirm('Confirmer la suspension de cet utilisateur ?')) return;
    
    try {
        const response = await fetch(`/api/auth/admin/suspend/${userId}`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadUsers(currentFilter);
        } else {
            showAlert(data.error || 'Erreur lors de la suspension', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
}

async function deleteUser(userId, email) {
    if (!confirm(`Confirmer la suppression de l'utilisateur ${email} ? Cette action est irréversible.`)) return;
    
    try {
        const response = await fetch(`/api/auth/admin/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadUsers(currentFilter);
        } else {
            showAlert(data.error || 'Erreur lors de la suppression', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
}

async function loadCases() {
    try {
        const response = await fetch('/api/cases?per_page=100', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            allCases = data.cases;
            const container = document.getElementById('cases-list');
            
            if (data.cases.length === 0) {
                container.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 2rem;">Aucun cas trouvé</p>';
                return;
            }
            
            container.innerHTML = `
                <p style="margin-bottom: 1rem; color: #6b7280;">Total: ${data.total} cas</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Numéro</th>
                            <th>Titre</th>
                            <th>Tribunal</th>
                            <th>Catégorie</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.cases.map(c => `
                            <tr>
                                <td><span class="badge badge-cyan">${c.case_number}</span></td>
                                <td>${c.title}</td>
                                <td>${c.court}</td>
                                <td><span class="badge badge-green">${c.category}</span></td>
                                <td>${new Date(c.date_decision).toLocaleDateString('fr-FR')}</td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="btn-primary btn-small" onclick="viewCase(${c.id})">
                                            Voir
                                        </button>
                                        <button class="btn-secondary btn-small" onclick="editCase(${c.id})">
                                            Modifier
                                        </button>
                                        <button class="btn-secondary btn-small" onclick="deleteCase(${c.id}, '${c.case_number}')">
                                            Supprimer
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement des cas', 'error');
    }
}

async function viewCase(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const c = await response.json();
            alert(`Numéro: ${c.case_number}\nTitre: ${c.title}\nTribunal: ${c.court}\nDate: ${new Date(c.date_decision).toLocaleDateString('fr-FR')}\n\nDescription: ${c.description}\n\nFaits: ${c.facts}\n\nDécision: ${c.decision}`);
        }
    } catch (error) {
        showAlert('Erreur lors du chargement du cas', 'error');
    }
}

async function editCase(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const c = await response.json();
            document.getElementById('edit-case-id').value = c.id;
            document.getElementById('edit-case-number').value = c.case_number;
            document.getElementById('edit-title').value = c.title;
            document.getElementById('edit-court').value = c.court;
            document.getElementById('edit-category').value = c.category;
            document.getElementById('edit-date').value = c.date_decision;
            
            document.getElementById('edit-modal').classList.add('active');
        }
    } catch (error) {
        showAlert('Erreur lors du chargement du cas', 'error');
    }
}

function closeModal() {
    document.getElementById('edit-modal').classList.remove('active');
}

document.getElementById('edit-case-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const caseId = document.getElementById('edit-case-id').value;
    const formData = {
        case_number: document.getElementById('edit-case-number').value,
        title: document.getElementById('edit-title').value,
        court: document.getElementById('edit-court').value,
        category: document.getElementById('edit-category').value,
        date_decision: document.getElementById('edit-date').value
    };
    
    try {
        const response = await fetch(`/api/cases/${caseId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            closeModal();
            loadCases();
        } else {
            showAlert(data.error || 'Erreur lors de la modification', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
});

async function deleteCase(caseId, caseNumber) {
    if (!confirm(`Confirmer la suppression du cas ${caseNumber} ? Cette action est irréversible.`)) return;
    
    try {
        const response = await fetch(`/api/cases/${caseId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadCases();
        } else {
            showAlert(data.error || 'Erreur lors de la suppression', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
}

async function importCSV() {
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Veuillez sélectionner un fichier', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showAlert('Importation en cours...', 'info');
        
        const response = await fetch('/api/import/csv', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            let message = data.message;
            if (data.errors && data.errors.length > 0) {
                message += `\n\nErreurs:\n${data.errors.join('\n')}`;
            }
            showAlert(message, 'success');
            fileInput.value = '';
        } else {
            showAlert(data.error || 'Erreur lors de l\'importation', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
}

document.getElementById('pdf-import-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('pdf-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Veuillez sélectionner un fichier PDF', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('case_number', document.getElementById('pdf-case-number').value);
    formData.append('title', document.getElementById('pdf-title').value);
    formData.append('court', document.getElementById('pdf-court').value);
    formData.append('category', document.getElementById('pdf-category').value);
    formData.append('date_decision', document.getElementById('pdf-date').value);
    formData.append('description', '');
    formData.append('decision', '');
    
    try {
        showAlert('Importation du PDF en cours...', 'info');
        
        const response = await fetch('/api/import/pdf', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            e.target.reset();
        } else {
            showAlert(data.error || 'Erreur lors de l\'importation du PDF', 'error');
        }
    } catch (error) {
        showAlert('Erreur de connexion au serveur', 'error');
    }
});

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
    const alertClass = type === 'success' ? 'alert-success' : (type === 'info' ? 'alert-info' : 'alert-error');
    
    alertContainer.innerHTML = `
        <div class="alert ${alertClass}">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        if (type !== 'info') {
            alertContainer.innerHTML = '';
        }
    }, 5000);
}

function filterUsers(filter, evt) {
    loadUsers(filter, evt);
}

loadUserInfo();
loadUsers('all', null);
