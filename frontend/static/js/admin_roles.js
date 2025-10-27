let allPermissions = {};
let allRoles = [];

// Charger les données au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadPermissions();
    loadRoles();
    
    document.getElementById('role-form').addEventListener('submit', handleRoleSubmit);
});

// Vérifier l'authentification
async function checkAuth() {
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
        }
    } catch (error) {
        window.location.href = '/';
    }
}

// Gérer la déconnexion
document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        window.location.href = '/';
    } catch (error) {
        console.error('Erreur lors de la déconnexion:', error);
    }
});

// Charger les permissions
async function loadPermissions() {
    try {
        const response = await fetch('/api/permissions', {
            credentials: 'include'
        });
        
        if (!response.ok) throw new Error('Erreur de chargement');
        
        allPermissions = await response.json();
    } catch (error) {
        showAlert('Erreur lors du chargement des permissions', 'error');
    }
}

// Charger les rôles
async function loadRoles() {
    try {
        const response = await fetch('/api/roles', {
            credentials: 'include'
        });
        
        if (!response.ok) throw new Error('Erreur de chargement');
        
        allRoles = await response.json();
        displayRoles();
    } catch (error) {
        showAlert('Erreur lors du chargement des rôles', 'error');
    }
}

// Afficher les rôles
function displayRoles() {
    const container = document.getElementById('roles-list');
    
    if (allRoles.length === 0) {
        container.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 2rem;">Aucun rôle trouvé</p>';
        return;
    }
    
    container.innerHTML = allRoles.map(role => `
        <div class="card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                        <h3 style="margin: 0;"><i class="fas fa-user-tag"></i> ${escapeHtml(role.name)}</h3>
                        <span class="role-badge ${role.is_system ? 'system' : 'custom'}">
                            ${role.is_system ? 'Système' : 'Personnalisé'}
                        </span>
                    </div>
                    ${role.description ? `<p style="color: #6b7280; margin-bottom: 1rem;">${escapeHtml(role.description)}</p>` : ''}
                    <p style="color: #374151; font-size: 0.875rem; margin-bottom: 0.5rem;">
                        <i class="fas fa-users"></i> <strong>${role.user_count}</strong> utilisateur${role.user_count > 1 ? 's' : ''}
                    </p>
                    <p style="color: #374151; font-size: 0.875rem;">
                        <i class="fas fa-key"></i> <strong>${role.permissions.length}</strong> permission${role.permissions.length > 1 ? 's' : ''}
                    </p>
                    ${role.permissions.length > 0 ? `
                        <div style="margin-top: 1rem;">
                            ${role.permissions.map(p => `
                                <span style="display: inline-block; margin: 0.25rem; padding: 0.25rem 0.75rem; background: #f3f4f6; border-radius: 0.5rem; font-size: 0.75rem;">
                                    ${escapeHtml(p.description || p.name)}
                                </span>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="btn-primary btn-sm" onclick="editRole(${role.id})" title="Modifier">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${!role.is_system && role.user_count === 0 ? `
                        <button class="btn-secondary btn-sm" onclick="deleteRole(${role.id})" title="Supprimer">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

// Ouvrir le modal de création
function openCreateRoleModal() {
    document.getElementById('modal-title').innerHTML = '<i class="fas fa-plus"></i> Créer un rôle';
    document.getElementById('role-id').value = '';
    document.getElementById('role-name').value = '';
    document.getElementById('role-description').value = '';
    document.getElementById('role-name').disabled = false;
    
    displayPermissionsInModal([]);
    document.getElementById('role-modal').classList.add('active');
}

// Éditer un rôle
function editRole(roleId) {
    const role = allRoles.find(r => r.id === roleId);
    if (!role) return;
    
    document.getElementById('modal-title').innerHTML = '<i class="fas fa-edit"></i> Modifier le rôle';
    document.getElementById('role-id').value = role.id;
    document.getElementById('role-name').value = role.name;
    document.getElementById('role-description').value = role.description || '';
    document.getElementById('role-name').disabled = role.is_system;
    
    const selectedPermissionIds = role.permissions.map(p => p.id);
    displayPermissionsInModal(selectedPermissionIds);
    
    document.getElementById('role-modal').classList.add('active');
}

// Afficher les permissions dans le modal
function displayPermissionsInModal(selectedIds) {
    const container = document.getElementById('permissions-list');
    
    const html = Object.entries(allPermissions).map(([category, permissions]) => `
        <div class="permission-category">
            <h4><i class="fas fa-folder"></i> ${escapeHtml(category)}</h4>
            ${permissions.map(perm => `
                <label class="permission-checkbox">
                    <input 
                        type="checkbox" 
                        name="permissions" 
                        value="${perm.id}"
                        ${selectedIds.includes(perm.id) ? 'checked' : ''}
                    >
                    <span>${escapeHtml(perm.description || perm.name)}</span>
                </label>
            `).join('')}
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// Fermer le modal
function closeRoleModal() {
    document.getElementById('role-modal').classList.remove('active');
}

// Gérer la soumission du formulaire
async function handleRoleSubmit(e) {
    e.preventDefault();
    
    const roleId = document.getElementById('role-id').value;
    const name = document.getElementById('role-name').value.trim();
    const description = document.getElementById('role-description').value.trim();
    
    const selectedPermissions = Array.from(document.querySelectorAll('input[name="permissions"]:checked'))
        .map(cb => parseInt(cb.value));
    
    const data = {
        name,
        description,
        permission_ids: selectedPermissions
    };
    
    try {
        const url = roleId ? `/api/roles/${roleId}` : '/api/roles';
        const method = roleId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erreur lors de l\'enregistrement');
        }
        
        showAlert(result.message || 'Rôle enregistré avec succès', 'success');
        closeRoleModal();
        loadRoles();
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

// Supprimer un rôle
async function deleteRole(roleId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce rôle ?')) return;
    
    try {
        const response = await fetch(`/api/roles/${roleId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erreur lors de la suppression');
        }
        
        showAlert(result.message || 'Rôle supprimé avec succès', 'success');
        loadRoles();
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

// Afficher une alerte
function showAlert(message, type = 'info') {
    const container = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        border-radius: 0.75rem;
        font-weight: 500;
        ${type === 'success' ? 'background: #d1fae5; color: #065f46; border: 2px solid #10b981;' : ''}
        ${type === 'error' ? 'background: #fee2e2; color: #991b1b; border: 2px solid #ef4444;' : ''}
        ${type === 'info' ? 'background: #dbeafe; color: #1e40af; border: 2px solid #3b82f6;' : ''}
    `;
    alert.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${escapeHtml(message)}
    `;
    container.appendChild(alert);
    
    setTimeout(() => alert.remove(), 5000);
}

// Échapper le HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
