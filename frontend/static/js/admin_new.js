// Variables globales
let currentBatchId = null;
let extractedCaseData = null;
let selectedFiles = [];
let fileStatuses = {};

// Charger les statistiques
async function loadStats() {
    try {
        const [usersRes, casesRes] = await Promise.all([
            fetch('/api/auth/admin/users', { credentials: 'include' }),
            fetch('/api/cases', { credentials: 'include' })
        ]);
        
        const usersData = await usersRes.json();
        const casesData = await casesRes.json();
        
        const users = usersData.users || [];
        const cases = casesData.cases || [];
        
        document.getElementById('stat-total-users').textContent = users.length;
        document.getElementById('stat-total-cases').textContent = cases.length;
        document.getElementById('stat-pending-users').textContent = 
            users.filter(u => !u.is_approved).length;
        document.getElementById('stat-admin-users').textContent = 
            users.filter(u => u.is_admin).length;
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
    }
}

// Gestion des tabs
function switchTab(tabName, evt) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    if (evt && evt.target) {
        evt.target.closest('.tab').classList.add('active');
    }
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    if (tabName === 'users') loadUsers();
    if (tabName === 'cases') loadCases();
}

// Affichage des alertes
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.style.cssText = `
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        background: ${type === 'success' ? '#d1fae5' : '#fee2e2'};
        color: ${type === 'success' ? '#065f46' : '#991b1b'};
        border: 3px dotted ${type === 'success' ? '#10b981' : '#ef4444'};
        display: flex;
        align-items: center;
        gap: 0.5rem;
    `;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    const container = document.getElementById('alert-container');
    container.appendChild(alertDiv);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

// Déconnexion
document.getElementById('logout-btn').addEventListener('click', async () => {
    const response = await fetch('/api/auth/logout', { 
        method: 'POST',
        credentials: 'include'
    });
    if (response.ok) {
        window.location.href = '/';
    }
});

// Charger les utilisateurs
async function loadUsers() {
    try {
        const response = await fetch('/api/auth/admin/users', { credentials: 'include' });
        const data = await response.json();
        const users = data.users || [];
        
        const usersList = document.getElementById('users-list');
        if (users.length === 0) {
            usersList.innerHTML = '<p style="text-align: center; color: #6b7280;">Aucun utilisateur</p>';
            return;
        }
        
        usersList.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-user"></i> Nom</th>
                        <th><i class="fas fa-envelope"></i> Email</th>
                        <th><i class="fas fa-shield-alt"></i> Rôle</th>
                        <th><i class="fas fa-check-circle"></i> Statut</th>
                        <th><i class="fas fa-cog"></i> Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td><strong>${user.first_name} ${user.last_name}</strong></td>
                            <td>${user.email}</td>
                            <td>
                                ${user.is_admin ? 
                                    '<span class="badge admin"><i class="fas fa-user-shield"></i> Admin</span>' : 
                                    '<span class="badge" style="background: #e5e7eb; color: #374151;">Juriste</span>'}
                            </td>
                            <td>
                                ${user.is_approved ? 
                                    '<span class="badge approved"><i class="fas fa-check"></i> Approuvé</span>' : 
                                    '<span class="badge pending"><i class="fas fa-clock"></i> En attente</span>'}
                            </td>
                            <td>
                                <div style="display: flex; gap: 0.5rem;">
                                    ${!user.is_approved ? `
                                        <button onclick="approveUser(${user.id})" class="action-btn approve">
                                            <i class="fas fa-check"></i> Approuver
                                        </button>
                                    ` : `
                                        <button onclick="suspendUser(${user.id})" class="action-btn suspend">
                                            <i class="fas fa-ban"></i> Suspendre
                                        </button>
                                    `}
                                    <button onclick="deleteUser(${user.id})" class="action-btn delete">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        loadStats();
    } catch (error) {
        showAlert('Erreur lors du chargement des utilisateurs', 'error');
    }
}

// Approuver un utilisateur
async function approveUser(userId) {
    try {
        const response = await fetch(`/api/auth/admin/approve/${userId}`, { 
            method: 'POST',
            credentials: 'include'
        });
        if (response.ok) {
            showAlert('Utilisateur approuvé avec succès');
            loadUsers();
        }
    } catch (error) {
        showAlert('Erreur lors de l\'approbation', 'error');
    }
}

// Suspendre un utilisateur
async function suspendUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir suspendre cet utilisateur ?')) return;
    
    try {
        const response = await fetch(`/api/auth/admin/suspend/${userId}`, { 
            method: 'POST',
            credentials: 'include'
        });
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Utilisateur suspendu avec succès');
            loadUsers();
        } else {
            showAlert(data.error || 'Erreur lors de la suspension', 'error');
        }
    } catch (error) {
        showAlert('Erreur lors de la suspension', 'error');
    }
}

// Supprimer un utilisateur
async function deleteUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ? Cette action est irréversible.')) return;
    
    try {
        const response = await fetch(`/api/auth/admin/users/${userId}`, { 
            method: 'DELETE',
            credentials: 'include'
        });
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Utilisateur supprimé avec succès');
            loadUsers();
        } else {
            showAlert(data.error || 'Erreur lors de la suppression', 'error');
        }
    } catch (error) {
        showAlert('Erreur lors de la suppression', 'error');
    }
}

// Charger les cas
async function loadCases() {
    try {
        const response = await fetch('/api/cases', { credentials: 'include' });
        const data = await response.json();
        
        const casesList = document.getElementById('cases-list');
        if (data.cases.length === 0) {
            casesList.innerHTML = '<p style="text-align: center; color: #6b7280;"><i class="fas fa-inbox"></i> Aucun cas de jurisprudence</p>';
            return;
        }
        
        casesList.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-hashtag"></i> Ref</th>
                        <th><i class="fas fa-heading"></i> Titre</th>
                        <th><i class="fas fa-landmark"></i> Juridiction</th>
                        <th><i class="fas fa-calendar"></i> Date</th>
                        <th><i class="fas fa-cog"></i> Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.cases.map(c => `
                        <tr>
                            <td><strong>${c.ref || 'N/A'}</strong></td>
                            <td>${c.titre || 'Sans titre'}</td>
                            <td>${c.juridiction || 'N/A'}</td>
                            <td>${c.date_decision || 'N/A'}</td>
                            <td>
                                <button onclick="deleteCase(${c.id})" class="action-btn delete">
                                    <i class="fas fa-trash"></i> Supprimer
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        loadStats();
    } catch (error) {
        showAlert('Erreur lors du chargement des cas', 'error');
    }
}

// Supprimer un cas
async function deleteCase(caseId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce cas ?')) return;
    
    try {
        const response = await fetch(`/api/cases/${caseId}`, { 
            method: 'DELETE',
            credentials: 'include'
        });
        if (response.ok) {
            showAlert('Cas supprimé avec succès');
            loadCases();
        }
    } catch (error) {
        showAlert('Erreur lors de la suppression', 'error');
    }
}

// Importation en masse - Sélection de fichiers
document.getElementById('batch-files')?.addEventListener('change', (e) => {
    selectedFiles = Array.from(e.target.files);
    const count = selectedFiles.length;
    
    document.getElementById('file-count-number').textContent = count;
    
    if (count > 200) {
        showAlert('Maximum 200 fichiers par lot', 'error');
        e.target.value = '';
        selectedFiles = [];
        document.getElementById('file-count-number').textContent = '0';
        return;
    }
    
    if (count > 0) {
        document.getElementById('load-files-btn').style.display = 'inline-block';
    }
});

// Précharger et afficher la liste des fichiers
function loadFilesList() {
    if (selectedFiles.length === 0) {
        showAlert('Veuillez sélectionner des fichiers', 'error');
        return;
    }
    
    fileStatuses = {};
    const filesList = document.getElementById('files-list');
    document.getElementById('total-files-count').textContent = selectedFiles.length;
    
    filesList.innerHTML = selectedFiles.map((file, index) => {
        fileStatuses[index] = 'pending';
        return `
            <div id="file-item-${index}" class="file-item" style="
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 0.75rem;
                margin-bottom: 0.5rem;
                background: white;
                border: 2px dotted #d1d5db;
                border-radius: 8px;
                transition: all 0.3s ease;
            ">
                <div style="flex-shrink: 0;">
                    <i id="file-icon-${index}" class="fas fa-file-pdf" style="font-size: 1.5rem; color: #ef4444;"></i>
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 600; color: #1f2937; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${file.name}
                    </div>
                    <div style="font-size: 0.75rem; color: #6b7280;">
                        ${(file.size / 1024).toFixed(2)} KB
                    </div>
                </div>
                <div id="file-status-${index}" style="flex-shrink: 0;">
                    <span class="badge pending"><i class="fas fa-clock"></i> En attente</span>
                </div>
            </div>
        `;
    }).join('');
    
    document.getElementById('files-list-section').style.display = 'block';
    document.getElementById('load-files-btn').style.display = 'none';
    
    showAlert(`${selectedFiles.length} fichiers prêts à être importés`, 'success');
}

async function startBatchImport() {
    if (selectedFiles.length === 0) {
        showAlert('Aucun fichier à importer', 'error');
        return;
    }
    
    document.getElementById('start-import-btn').disabled = true;
    document.getElementById('batch-progress').style.display = 'block';
    document.getElementById('pending-count').textContent = selectedFiles.length;
    document.getElementById('batch-status-text').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Préparation de l\'importation...';
    
    // Étape 1: Upload de tous les fichiers
    const formData = new FormData();
    for (let file of selectedFiles) {
        formData.append('files[]', file);
    }
    
    try {
        const uploadResponse = await fetch('/api/batch/upload', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        
        const uploadData = await uploadResponse.json();
        
        if (!uploadResponse.ok) {
            showAlert(uploadData.error || 'Erreur lors de l\'upload', 'error');
            document.getElementById('start-import-btn').disabled = false;
            return;
        }
        
        currentBatchId = uploadData.batch_id;
        
        // Étape 2: Traiter les fichiers un par un
        await processFilesOneByOne(currentBatchId, selectedFiles.length);
        
    } catch (error) {
        showAlert('Erreur lors de l\'importation: ' + error.message, 'error');
        document.getElementById('start-import-btn').disabled = false;
    }
}

async function processFilesOneByOne(batchId, totalFiles) {
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < totalFiles; i++) {
        // Mettre à jour le statut visuel
        updateFileStatus(i, 'processing');
        
        document.getElementById('batch-status-text').innerHTML = 
            `<i class="fas fa-cog fa-spin"></i> Traitement de ${selectedFiles[i].name} (${i + 1}/${totalFiles})`;
        
        try {
            const response = await fetch('/api/batch/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    batch_id: batchId,
                    start_index: i,
                    batch_size: 1
                }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.success > 0) {
                successCount++;
                updateFileStatus(i, 'success', data.details[0]?.ref);
            } else if (data.errors && data.errors.length > 0) {
                errorCount++;
                updateFileStatus(i, 'error', data.errors[0]?.error);
            }
            
        } catch (error) {
            errorCount++;
            updateFileStatus(i, 'error', error.message);
        }
        
        // Mettre à jour les compteurs
        const progress = Math.round(((i + 1) / totalFiles) * 100);
        document.getElementById('progress-fill').style.width = `${progress}%`;
        document.getElementById('progress-fill').textContent = `${progress}%`;
        document.getElementById('success-count').textContent = successCount;
        document.getElementById('error-count').textContent = errorCount;
        document.getElementById('pending-count').textContent = totalFiles - (i + 1);
        
        // Petit délai entre chaque fichier pour éviter la surcharge
        await new Promise(resolve => setTimeout(resolve, 300));
    }
    
    // Importation terminée
    document.getElementById('batch-status-text').innerHTML = 
        `<i class="fas fa-check-circle"></i> Importation terminée! ${successCount} succès, ${errorCount} erreurs`;
    
    showAlert(`Importation terminée: ${successCount} succès, ${errorCount} erreurs`);
    document.getElementById('start-import-btn').disabled = false;
    loadStats();
}

function updateFileStatus(index, status, message = '') {
    const fileItem = document.getElementById(`file-item-${index}`);
    const fileIcon = document.getElementById(`file-icon-${index}`);
    const fileStatusEl = document.getElementById(`file-status-${index}`);
    
    if (!fileItem) return;
    
    fileStatuses[index] = status;
    
    switch (status) {
        case 'processing':
            fileItem.style.borderColor = '#f59e0b';
            fileItem.style.background = 'rgba(245, 158, 11, 0.05)';
            fileIcon.className = 'fas fa-spinner fa-spin';
            fileIcon.style.color = '#f59e0b';
            fileStatusEl.innerHTML = '<span class="badge" style="background: #fef3c7; color: #92400e; border: 2px solid #f59e0b;"><i class="fas fa-spinner fa-spin"></i> En cours...</span>';
            fileItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            break;
            
        case 'success':
            fileItem.style.borderColor = '#10b981';
            fileItem.style.background = 'rgba(16, 185, 129, 0.05)';
            fileIcon.className = 'fas fa-check-circle';
            fileIcon.style.color = '#10b981';
            fileStatusEl.innerHTML = `<span class="badge approved"><i class="fas fa-check"></i> Importé${message ? ` (${message})` : ''}</span>`;
            break;
            
        case 'error':
            fileItem.style.borderColor = '#ef4444';
            fileItem.style.background = 'rgba(239, 68, 68, 0.05)';
            fileIcon.className = 'fas fa-times-circle';
            fileIcon.style.color = '#ef4444';
            fileStatusEl.innerHTML = `<span class="badge suspended"><i class="fas fa-times"></i> Erreur</span>`;
            if (message) {
                fileStatusEl.innerHTML += `<div style="font-size: 0.75rem; color: #991b1b; margin-top: 0.25rem;">${message}</div>`;
            }
            break;
    }
}

async function processBatch(batchId, totalFiles) {
    let processedCount = 0;
    let successCount = 0;
    let errorCount = 0;
    let allErrors = [];
    let startIndex = 0;
    const batchSize = 10;
    
    while (startIndex < totalFiles) {
        try {
            const response = await fetch('/api/batch/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    batch_id: batchId,
                    start_index: startIndex,
                    batch_size: batchSize
                }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            processedCount += data.processed;
            successCount += data.success;
            errorCount += data.errors_count;
            allErrors = allErrors.concat(data.errors);
            
            const progress = Math.round((processedCount / totalFiles) * 100);
            document.getElementById('progress-fill').style.width = `${progress}%`;
            document.getElementById('progress-fill').textContent = `${progress}%`;
            document.getElementById('batch-status-text').innerHTML = 
                `<i class="fas fa-cog fa-spin"></i> Traitement en cours... ${processedCount}/${totalFiles} fichiers`;
            document.getElementById('success-count').textContent = successCount;
            document.getElementById('error-count').textContent = errorCount;
            
            if (!data.has_more) break;
            startIndex = data.next_index;
            
            await new Promise(resolve => setTimeout(resolve, 500));
            
        } catch (error) {
            showAlert('Erreur lors du traitement: ' + error.message, 'error');
            break;
        }
    }
    
    document.getElementById('batch-status-text').innerHTML = 
        `<i class="fas fa-check-circle"></i> Terminé! ${successCount} succès, ${errorCount} erreurs`;
    
    if (allErrors.length > 0) {
        document.getElementById('error-details').style.display = 'block';
        document.getElementById('error-list').innerHTML = allErrors.map(err => `
            <div style="margin-bottom: 0.5rem; padding: 0.75rem; background: #fee2e2; border-radius: 8px; border-left: 4px solid #ef4444;">
                <strong><i class="fas fa-file-pdf"></i> ${err.filename}:</strong> ${err.error}
            </div>
        `).join('');
    }
    
    showAlert(`Importation terminée: ${successCount} succès, ${errorCount} erreurs`);
    loadStats();
}

// Import PDF simple avec extraction automatique
async function importSinglePDF() {
    const fileInput = document.getElementById('single-pdf-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Veuillez sélectionner un fichier PDF', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showAlert('Extraction en cours...', 'success');
        
        const response = await fetch('/api/import/single-pdf', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Cas importé avec succès!');
            extractedCaseData = data.case;
            
            displayExtractedData(data.case);
            
            fileInput.value = '';
            loadStats();
        } else {
            showAlert(data.error || 'Erreur lors de l\'extraction', 'error');
        }
    } catch (error) {
        showAlert('Erreur: ' + error.message, 'error');
    }
}

function displayExtractedData(caseData) {
    const preview = document.getElementById('extraction-preview');
    const dataDiv = document.getElementById('extracted-data');
    
    dataDiv.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
            <p><strong><i class="fas fa-hashtag"></i> Ref:</strong> ${caseData.ref || 'N/A'}</p>
            <p><strong><i class="fas fa-heading"></i> Titre:</strong> ${caseData.titre || 'N/A'}</p>
            <p><strong><i class="fas fa-landmark"></i> Juridiction:</strong> ${caseData.juridiction || 'N/A'}</p>
            <p><strong><i class="fas fa-calendar"></i> Date:</strong> ${caseData.date_decision || 'N/A'}</p>
            <p><strong><i class="fas fa-book"></i> Thème:</strong> ${caseData.theme || 'N/A'}</p>
            <p><strong><i class="fas fa-tags"></i> Mots-clés:</strong> ${caseData.mots_cles || 'N/A'}</p>
        </div>
    `;
    
    preview.style.display = 'block';
}

// Ajouter un cas manuellement
document.getElementById('add-case-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        ref: document.getElementById('ref').value,
        titre: document.getElementById('titre').value,
        juridiction: document.getElementById('juridiction').value,
        pays_ville: document.getElementById('pays_ville').value,
        numero_decision: document.getElementById('numero_decision').value,
        date_decision: document.getElementById('date_decision').value,
        numero_dossier: document.getElementById('numero_dossier').value,
        type_decision: document.getElementById('type_decision').value,
        chambre: document.getElementById('chambre').value,
        theme: document.getElementById('theme').value,
        mots_cles: document.getElementById('mots_cles').value,
        base_legale: document.getElementById('base_legale').value,
        source: document.getElementById('source').value,
        resume_francais: document.getElementById('resume_francais').value,
        resume_arabe: document.getElementById('resume_arabe').value,
        texte_integral: document.getElementById('texte_integral').value
    };
    
    try {
        const response = await fetch('/api/cases', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Cas ajouté avec succès!');
            e.target.reset();
            loadStats();
        } else {
            showAlert(data.error || 'Erreur lors de l\'ajout', 'error');
        }
    } catch (error) {
        showAlert('Erreur: ' + error.message, 'error');
    }
});

// Charger les données initiales
loadStats();
loadUsers();
