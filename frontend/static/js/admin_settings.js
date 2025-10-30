let currentUser = null;

async function checkAuth() {
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'
        });

        if (!response.ok) {
            window.location.href = '/';
            return false;
        }

        const data = await response.json();
        currentUser = data;

        if (!currentUser.isAdmin) {
            showAlert('Accès refusé. Vous devez être administrateur.', 'error');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 2000);
            return false;
        }

        return true;
    } catch (error) {
        console.error('Erreur:', error);
        window.location.href = '/';
        return false;
    }
}

function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alert-container');
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    
    alertContainer.innerHTML = `
        <div class="${alertClass}" style="margin-bottom: 1rem;">
            ${message}
        </div>
    `;

    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}

async function loadSettings() {
    try {
        const response = await fetch('/api/admin/settings', {
            credentials: 'include'
        });

        if (!response.ok) throw new Error('Erreur lors du chargement');

        const data = await response.json();
        const settings = data.settings;

        settings.forEach(setting => {
            const input = document.getElementById(setting.key.replace(/_/g, '-'));
            if (input) {
                input.value = setting.value || '';
            }
        });

        displayAllSettings(settings);
        
        const platformName = settings.find(s => s.key === 'platform_name');
        if (platformName) {
            document.getElementById('platform-name-nav').textContent = platformName.value;
            document.getElementById('page-title').textContent = `Paramètres - ${platformName.value}`;
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement des paramètres', 'error');
    }
}

function displayAllSettings(settings) {
    const container = document.getElementById('all-settings-container');
    
    if (settings.length === 0) {
        container.innerHTML = '<p style="color: var(--gray-500);">Aucun paramètre trouvé</p>';
        return;
    }

    let html = '<div class="table-container"><table class="data-table"><thead><tr>';
    html += '<th>Clé</th><th>Valeur</th><th>Description</th><th>Dernière modification</th>';
    html += '</tr></thead><tbody>';

    settings.forEach(setting => {
        const date = setting.updated_at ? new Date(setting.updated_at).toLocaleString('fr-FR') : 'N/A';
        html += `
            <tr>
                <td><code style="background: var(--gray-100); padding: 0.25rem 0.5rem; border-radius: 0.25rem;">${setting.key}</code></td>
                <td>${setting.value || '<em style="color: var(--gray-400);">vide</em>'}</td>
                <td>${setting.description || '<em style="color: var(--gray-400);">N/A</em>'}</td>
                <td style="font-size: 0.875rem; color: var(--gray-500);">${date}</td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

async function updateSetting(key, value, description = null) {
    try {
        const response = await fetch(`/api/admin/settings/${key}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ value, description })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors de la mise à jour');
        }

        return await response.json();
    } catch (error) {
        throw error;
    }
}

document.getElementById('save-identity-btn').addEventListener('click', async () => {
    const btn = document.getElementById('save-identity-btn');
    btn.disabled = true;
    btn.textContent = 'Enregistrement...';

    try {
        const updates = [
            {
                key: 'platform_name',
                value: document.getElementById('platform-name').value,
                description: 'Nom de la plateforme affiché partout'
            },
            {
                key: 'platform_tagline',
                value: document.getElementById('platform-tagline').value,
                description: 'Slogan de la plateforme'
            },
            {
                key: 'platform_description',
                value: document.getElementById('platform-description').value,
                description: 'Description SEO de la plateforme'
            },
            {
                key: 'platform_keywords',
                value: document.getElementById('platform-keywords').value,
                description: 'Mots-clés SEO (séparés par des virgules)'
            }
        ];

        for (const update of updates) {
            await updateSetting(update.key, update.value, update.description);
        }

        showAlert('Identité de la plateforme mise à jour avec succès !', 'success');
        await loadSettings();
    } catch (error) {
        showAlert(error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '💾 Enregistrer l\'identité';
    }
});

document.getElementById('save-system-btn').addEventListener('click', async () => {
    const btn = document.getElementById('save-system-btn');
    btn.disabled = true;
    btn.textContent = 'Enregistrement...';

    try {
        const updates = [
            {
                key: 'admin_email',
                value: document.getElementById('admin-email').value,
                description: 'Email de l\'administrateur principal'
            },
            {
                key: 'max_upload_size',
                value: document.getElementById('max-upload-size').value,
                description: 'Taille maximale d\'upload en MB'
            },
            {
                key: 'max_batch_import',
                value: document.getElementById('max-batch-import').value,
                description: 'Nombre maximum de PDFs pour import en masse'
            }
        ];

        for (const update of updates) {
            await updateSetting(update.key, update.value, update.description);
        }

        showAlert('Configuration système mise à jour avec succès !', 'success');
        await loadSettings();
    } catch (error) {
        showAlert(error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '💾 Enregistrer la configuration';
    }
});

document.getElementById('logout-btn').addEventListener('click', async (e) => {
    e.preventDefault();
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        window.location.href = '/';
    } catch (error) {
        console.error('Erreur lors de la déconnexion:', error);
        window.location.href = '/';
    }
});

async function init() {
    const isAuth = await checkAuth();
    if (isAuth) {
        await loadSettings();
    }
}

init();
