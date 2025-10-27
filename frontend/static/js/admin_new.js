// Variables globales
let currentBatchId = null;
let extractedCaseData = null;

// Gestion des tabs
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
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
    `;
    alertDiv.textContent = message;
    
    const container = document.getElementById('alert-container');
    container.appendChild(alertDiv);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

// Déconnexion
document.getElementById('logout-btn').addEventListener('click', async () => {
    const response = await fetch('/api/auth/logout', { method: 'POST' });
    if (response.ok) {
        window.location.href = '/';
    }
});

// Charger les utilisateurs
async function loadUsers() {
    try {
        const response = await fetch('/api/auth/users');
        const users = await response.json();
        
        const usersList = document.getElementById('users-list');
        if (users.length === 0) {
            usersList.innerHTML = '<p style="text-align: center; color: #6b7280;">Aucun utilisateur</p>';
            return;
        }
        
        usersList.innerHTML = users.map(user => `
            <div class="card mb-2">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>${user.first_name} ${user.last_name}</strong><br>
                        <span style="color: #6b7280; font-size: 0.875rem;">${user.email}</span>
                        ${user.is_admin ? '<span style="color: #3b82f6; font-weight: 600; margin-left: 0.5rem;">Admin</span>' : ''}
                    </div>
                    <div>
                        ${!user.is_approved ? `
                            <button onclick="approveUser(${user.id})" class="btn-primary btn-sm">Approuver</button>
                        ` : '<span style="color: #10b981; font-weight: 600;">Approuvé</span>'}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        showAlert('Erreur lors du chargement des utilisateurs', 'error');
    }
}

// Approuver un utilisateur
async function approveUser(userId) {
    try {
        const response = await fetch(`/api/auth/users/${userId}/approve`, { method: 'POST' });
        if (response.ok) {
            showAlert('Utilisateur approuvé avec succès');
            loadUsers();
        }
    } catch (error) {
        showAlert('Erreur lors de l\'approbation', 'error');
    }
}

// Charger les cas
async function loadCases() {
    try {
        const response = await fetch('/api/cases');
        const data = await response.json();
        
        const casesList = document.getElementById('cases-list');
        if (data.cases.length === 0) {
            casesList.innerHTML = '<p style="text-align: center; color: #6b7280;">Aucun cas de jurisprudence</p>';
            return;
        }
        
        casesList.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Ref</th>
                        <th>Titre</th>
                        <th>Juridiction</th>
                        <th>Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.cases.map(c => `
                        <tr>
                            <td>${c.ref || 'N/A'}</td>
                            <td>${c.titre || 'Sans titre'}</td>
                            <td>${c.juridiction || 'N/A'}</td>
                            <td>${c.date_decision || 'N/A'}</td>
                            <td>
                                <button onclick="deleteCase(${c.id})" class="btn-secondary btn-sm">Supprimer</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        showAlert('Erreur lors du chargement des cas', 'error');
    }
}

// Supprimer un cas
async function deleteCase(caseId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce cas ?')) return;
    
    try {
        const response = await fetch(`/api/cases/${caseId}`, { method: 'DELETE' });
        if (response.ok) {
            showAlert('Cas supprimé avec succès');
            loadCases();
        }
    } catch (error) {
        showAlert('Erreur lors de la suppression', 'error');
    }
}

// Importation en masse - Upload
document.getElementById('batch-files')?.addEventListener('change', (e) => {
    const count = e.target.files.length;
    document.getElementById('file-count').textContent = `${count} fichier(s) sélectionné(s)`;
    if (count > 200) {
        showAlert('Maximum 200 fichiers par lot', 'error');
        e.target.value = '';
    }
});

async function startBatchUpload() {
    const fileInput = document.getElementById('batch-files');
    const files = fileInput.files;
    
    if (files.length === 0) {
        showAlert('Veuillez sélectionner des fichiers', 'error');
        return;
    }
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files[]', file);
    }
    
    document.getElementById('upload-btn').disabled = true;
    document.getElementById('batch-progress').style.display = 'block';
    document.getElementById('batch-status-text').textContent = 'Upload en cours...';
    
    try {
        const response = await fetch('/api/batch/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentBatchId = data.batch_id;
            showAlert(`${data.uploaded_count} fichiers uploadés avec succès`);
            await processBatch(currentBatchId, data.uploaded_count);
        } else {
            showAlert(data.error || 'Erreur lors de l\'upload', 'error');
        }
    } catch (error) {
        showAlert('Erreur lors de l\'upload: ' + error.message, 'error');
    } finally {
        document.getElementById('upload-btn').disabled = false;
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
                })
            });
            
            const data = await response.json();
            
            processedCount += data.processed;
            successCount += data.success;
            errorCount += data.errors_count;
            allErrors = allErrors.concat(data.errors);
            
            const progress = Math.round((processedCount / totalFiles) * 100);
            document.getElementById('progress-fill').style.width = `${progress}%`;
            document.getElementById('progress-fill').textContent = `${progress}%`;
            document.getElementById('batch-status-text').textContent = 
                `Traitement en cours... ${processedCount}/${totalFiles} fichiers`;
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
    
    document.getElementById('batch-status-text').textContent = 
        `Terminé! ${successCount} succès, ${errorCount} erreurs`;
    
    if (allErrors.length > 0) {
        document.getElementById('error-details').style.display = 'block';
        document.getElementById('error-list').innerHTML = allErrors.map(err => `
            <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: #fee2e2; border-radius: 4px;">
                <strong>${err.filename}:</strong> ${err.error}
            </div>
        `).join('');
    }
    
    showAlert(`Importation terminée: ${successCount} succès, ${errorCount} erreurs`);
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
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Cas importé avec succès!');
            extractedCaseData = data.case;
            
            displayExtractedData(data.case);
            
            fileInput.value = '';
            loadCases();
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
        <p><strong>Ref:</strong> ${caseData.ref || 'N/A'}</p>
        <p><strong>Titre:</strong> ${caseData.titre || 'N/A'}</p>
        <p><strong>Juridiction:</strong> ${caseData.juridiction || 'N/A'}</p>
        <p><strong>Date:</strong> ${caseData.date_decision || 'N/A'}</p>
        <p><strong>Thème:</strong> ${caseData.theme || 'N/A'}</p>
        <p><strong>Mots-clés:</strong> ${caseData.mots_cles || 'N/A'}</p>
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
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Cas ajouté avec succès!');
            e.target.reset();
        } else {
            showAlert(data.error || 'Erreur lors de l\'ajout', 'error');
        }
    } catch (error) {
        showAlert('Erreur: ' + error.message, 'error');
    }
});

// Charger les utilisateurs au démarrage
loadUsers();
