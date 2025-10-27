let currentPage = 1;
const perPage = 20;
let selectedCases = new Set();
let allCases = [];

function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
    
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach((tab, index) => {
        if (tab.textContent.includes(tabName === 'list' ? 'Liste' : 
                                       tabName === 'add' ? 'Ajouter' :
                                       tabName === 'import-pdf' ? 'Import PDF' :
                                       'Import en Masse')) {
            tab.classList.add('active');
        }
    });
    
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

async function loadStats() {
    try {
        const response = await fetch('/api/cases/stats');
        const stats = await response.json();
        
        document.getElementById('stat-total-cases').textContent = stats.total || 0;
        document.getElementById('stat-recent-cases').textContent = stats.this_month || 0;
        document.getElementById('stat-my-cases').textContent = stats.my_cases || 0;
        document.getElementById('stat-pdf-cases').textContent = stats.with_pdf || 0;
    } catch (error) {
        console.error('Erreur lors du chargement des stats:', error);
    }
}

async function loadCases(page = 1) {
    try {
        const response = await fetch(`/api/cases?page=${page}&per_page=${perPage}`);
        const data = await response.json();
        
        allCases = data.cases;
        displayCases(data.cases);
        displayPagination(data.page, data.pages);
        currentPage = page;
    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('casesTableBody').innerHTML = `
            <tr>
                <td colspan="11" style="text-align: center; padding: 2rem; color: #ef4444;">
                    Erreur lors du chargement des cas
                </td>
            </tr>
        `;
    }
}

function displayCases(cases) {
    const tbody = document.getElementById('casesTableBody');
    
    if (cases.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="11" style="text-align: center; padding: 2rem;">
                    Aucun cas trouvé
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = cases.map(c => `
        <tr>
            <td>
                <input type="checkbox" 
                       class="checkbox case-checkbox" 
                       data-case-id="${c.id}"
                       ${selectedCases.has(c.id) ? 'checked' : ''}
                       onchange="handleCheckboxChange(${c.id}, this.checked)">
            </td>
            <td class="ref-cell">${c.ref || 'N/A'}</td>
            <td>${c.titre || 'Sans titre'}</td>
            <td>${c.juridiction || 'N/A'}</td>
            <td>${c.pays_ville || 'N/A'}</td>
            <td>${c.chambre || 'N/A'}</td>
            <td>${c.numero_decision || 'N/A'}</td>
            <td>${c.date_decision ? formatDate(c.date_decision) : 'N/A'}</td>
            <td>${c.type_decision || 'N/A'}</td>
            <td>${c.theme ? truncate(c.theme, 30) : 'N/A'}</td>
            <td style="text-align: center;">
                <button class="btn-primary btn-sm" onclick="viewCase(${c.id})">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    } catch (e) {
        return dateString;
    }
}

function truncate(str, length) {
    if (!str) return '';
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function handleCheckboxChange(caseId, checked) {
    if (checked) {
        selectedCases.add(caseId);
    } else {
        selectedCases.delete(caseId);
    }
}

function toggleSelectAll() {
    const checkboxes = document.querySelectorAll('.case-checkbox');
    const selectAllCheckbox = document.getElementById('selectAll');
    const allChecked = selectAllCheckbox.checked;
    
    checkboxes.forEach(cb => {
        const caseId = parseInt(cb.dataset.caseId);
        cb.checked = !allChecked;
        if (!allChecked) {
            selectedCases.add(caseId);
        } else {
            selectedCases.delete(caseId);
        }
    });
    selectAllCheckbox.checked = !allChecked;
}

async function deleteSelected() {
    if (selectedCases.size === 0) {
        showAlert('Veuillez sélectionner au moins un cas à supprimer', 'warning');
        return;
    }
    
    if (!confirm(`⚠️ Voulez-vous vraiment supprimer ${selectedCases.size} cas sélectionné(s) ? Cette action est irréversible !`)) {
        return;
    }
    
    try {
        const deletePromises = Array.from(selectedCases).map(caseId =>
            fetch(`/api/cases/${caseId}`, { method: 'DELETE' })
        );
        
        await Promise.all(deletePromises);
        
        selectedCases.clear();
        showAlert(`${deletePromises.length} cas supprimé(s) avec succès`, 'success');
        loadCases(currentPage);
        loadStats();
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la suppression des cas', 'error');
    }
}

function displayPagination(currentPage, totalPages) {
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    if (currentPage > 1) {
        html += `<button class="btn-secondary btn-sm" onclick="loadCases(${currentPage - 1})">← Précédent</button>`;
    }
    
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        html += `<button class="btn-${i === currentPage ? 'primary' : 'secondary'} btn-sm" onclick="loadCases(${i})">${i}</button>`;
    }
    
    if (currentPage < totalPages) {
        html += `<button class="btn-secondary btn-sm" onclick="loadCases(${currentPage + 1})">Suivant →</button>`;
    }
    
    pagination.innerHTML = html;
}

async function viewCase(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}`);
        const caseData = await response.json();
        
        const detailsHTML = `
            <h2 style="color: #3b82f6; margin-bottom: 1.5rem;">${caseData.titre}</h2>
            
            <div class="section-blue" style="margin-bottom: 1rem;">
                <h3>Identification</h3>
                <p><strong>Référence:</strong> ${caseData.ref}</p>
                <p><strong>Juridiction:</strong> ${caseData.juridiction || 'N/A'}</p>
                <p><strong>Pays/Ville:</strong> ${caseData.pays_ville || 'N/A'}</p>
                <p><strong>N° de décision:</strong> ${caseData.numero_decision || 'N/A'}</p>
                <p><strong>Date de décision:</strong> ${caseData.date_decision ? formatDate(caseData.date_decision) : 'N/A'}</p>
                <p><strong>N° de dossier:</strong> ${caseData.numero_dossier || 'N/A'}</p>
                <p><strong>Type de décision:</strong> ${caseData.type_decision || 'N/A'}</p>
                <p><strong>Chambre:</strong> ${caseData.chambre || 'N/A'}</p>
            </div>
            
            ${caseData.theme ? `
            <div class="section-green" style="margin-bottom: 1rem;">
                <h3>Thème</h3>
                <p>${caseData.theme}</p>
            </div>
            ` : ''}
            
            ${caseData.mots_cles ? `
            <div class="section-violet" style="margin-bottom: 1rem;">
                <h3>Mots clés</h3>
                <p>${caseData.mots_cles}</p>
            </div>
            ` : ''}
            
            ${caseData.base_legale ? `
            <div class="section-cyan" style="margin-bottom: 1rem;">
                <h3>Base légale</h3>
                <p>${caseData.base_legale}</p>
            </div>
            ` : ''}
            
            ${caseData.resume_francais ? `
            <div class="section-blue" style="margin-bottom: 1rem;">
                <h3>Résumé en français</h3>
                <p>${caseData.resume_francais}</p>
            </div>
            ` : ''}
            
            ${caseData.resume_arabe ? `
            <div class="section-green" style="margin-bottom: 1rem;">
                <h3>Résumé en arabe</h3>
                <p style="direction: rtl; text-align: right;">${caseData.resume_arabe}</p>
            </div>
            ` : ''}
            
            ${caseData.texte_integral ? `
            <div class="section-violet">
                <h3>Texte intégral</h3>
                <p style="white-space: pre-wrap;">${caseData.texte_integral}</p>
            </div>
            ` : ''}
        `;
        
        document.getElementById('caseDetails').innerHTML = detailsHTML;
        document.getElementById('caseModal').style.display = 'block';
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement des détails du cas', 'error');
    }
}

function closeModal() {
    document.getElementById('caseModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('caseModal');
    if (event.target === modal) {
        closeModal();
    }
}

document.getElementById('add-case-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const caseData = {
        ref: document.getElementById('ref').value,
        titre: document.getElementById('titre').value,
        juridiction: document.getElementById('juridiction').value,
        pays_ville: document.getElementById('pays_ville').value,
        numero_decision: document.getElementById('numero_decision').value,
        numero_dossier: document.getElementById('numero_dossier').value,
        type_decision: document.getElementById('type_decision').value,
        date_decision: document.getElementById('date_decision').value,
        chambre: document.getElementById('chambre').value,
        source: document.getElementById('source').value,
        theme: document.getElementById('theme').value,
        mots_cles: document.getElementById('mots_cles').value,
        base_legale: document.getElementById('base_legale').value,
        resume_francais: document.getElementById('resume_francais').value,
        resume_arabe: document.getElementById('resume_arabe').value,
        texte_integral: document.getElementById('texte_integral').value
    };
    
    try {
        const response = await fetch('/api/cases', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(caseData)
        });
        
        if (response.ok) {
            showAlert('Cas ajouté avec succès!', 'success');
            e.target.reset();
            switchTab('list');
            loadCases(1);
            loadStats();
        } else {
            const error = await response.json();
            showAlert(error.error || 'Erreur lors de l\'ajout du cas', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de l\'ajout du cas', 'error');
    }
});

async function importSinglePDF() {
    const fileInput = document.getElementById('single-pdf-file');
    if (!fileInput.files.length) {
        showAlert('Veuillez sélectionner un fichier PDF', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('pdf', fileInput.files[0]);
    
    try {
        showAlert('Extraction en cours...', 'info');
        const response = await fetch('/api/batch-import/extract-pdf', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showAlert('Cas importé et ajouté avec succès!', 'success');
            fileInput.value = '';
            loadCases(1);
            loadStats();
        } else {
            showAlert(result.error || 'Erreur lors de l\'extraction', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de l\'import du PDF', 'error');
    }
}

function loadFilesList() {
    const fileInput = document.getElementById('batch-files');
    const files = fileInput.files;
    
    if (files.length === 0) {
        showAlert('Veuillez sélectionner des fichiers PDF', 'warning');
        return;
    }
    
    if (files.length > 200) {
        showAlert('Maximum 200 fichiers autorisés', 'error');
        return;
    }
    
    const filesList = document.getElementById('files-list');
    filesList.innerHTML = Array.from(files).map((file, index) => `
        <div style="padding: 0.5rem; border-bottom: 1px solid #e5e7eb;">
            <span class="badge-blue">${index + 1}</span>
            ${file.name}
        </div>
    `).join('');
    
    document.getElementById('total-files-count').textContent = files.length;
    document.getElementById('files-list-section').style.display = 'block';
    document.getElementById('file-count-number').textContent = files.length;
}

async function startBatchImport() {
    const fileInput = document.getElementById('batch-files');
    const files = fileInput.files;
    
    if (files.length === 0) {
        showAlert('Aucun fichier sélectionné', 'warning');
        return;
    }
    
    document.getElementById('batch-progress').style.display = 'block';
    document.getElementById('start-import-btn').disabled = true;
    
    let successCount = 0;
    let errorCount = 0;
    let errorsList = [];
    
    const resultsDiv = document.createElement('div');
    resultsDiv.id = 'import-results';
    resultsDiv.style.marginTop = '1rem';
    resultsDiv.style.maxHeight = '400px';
    resultsDiv.style.overflowY = 'auto';
    document.getElementById('batch-progress').appendChild(resultsDiv);
    
    for (let i = 0; i < files.length; i++) {
        const fileName = files[i].name;
        const formData = new FormData();
        formData.append('file', files[i]);
        
        const fileStatus = document.createElement('div');
        fileStatus.style.padding = '0.75rem';
        fileStatus.style.marginBottom = '0.5rem';
        fileStatus.style.borderRadius = '8px';
        fileStatus.style.border = '2px solid #e5e7eb';
        fileStatus.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-spinner fa-spin" style="color: #3b82f6;"></i>
                <strong>${i + 1}. ${fileName}</strong>
                <span style="margin-left: auto; color: #6b7280;">En cours...</span>
            </div>
        `;
        resultsDiv.appendChild(fileStatus);
        resultsDiv.scrollTop = resultsDiv.scrollHeight;
        
        try {
            const response = await fetch('/api/import/single-pdf', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                successCount++;
                fileStatus.style.border = '2px solid #10b981';
                fileStatus.style.background = '#ecfdf5';
                fileStatus.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-check-circle" style="color: #10b981;"></i>
                        <strong>${i + 1}. ${fileName}</strong>
                        <span style="margin-left: auto; color: #059669;">✓ Importé (Ref: ${result.case?.ref || 'N/A'})</span>
                    </div>
                `;
            } else {
                errorCount++;
                const errorMsg = result.error || 'Erreur inconnue';
                errorsList.push({file: fileName, error: errorMsg});
                fileStatus.style.border = '2px solid #ef4444';
                fileStatus.style.background = '#fef2f2';
                fileStatus.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-times-circle" style="color: #ef4444;"></i>
                        <strong>${i + 1}. ${fileName}</strong>
                    </div>
                    <div style="margin-left: 1.5rem; color: #dc2626; font-size: 0.875rem; margin-top: 0.25rem;">
                        ${errorMsg}
                    </div>
                `;
            }
        } catch (error) {
            errorCount++;
            errorsList.push({file: fileName, error: error.message});
            fileStatus.style.border = '2px solid #ef4444';
            fileStatus.style.background = '#fef2f2';
            fileStatus.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fas fa-times-circle" style="color: #ef4444;"></i>
                    <strong>${i + 1}. ${fileName}</strong>
                </div>
                <div style="margin-left: 1.5rem; color: #dc2626; font-size: 0.875rem; margin-top: 0.25rem;">
                    Erreur réseau: ${error.message}
                </div>
            `;
        }
        
        const progress = Math.round(((i + 1) / files.length) * 100);
        document.getElementById('progress-fill').style.width = progress + '%';
        document.getElementById('progress-fill').textContent = progress + '%';
        document.getElementById('success-count').textContent = successCount;
        document.getElementById('error-count').textContent = errorCount;
        document.getElementById('pending-count').textContent = files.length - (successCount + errorCount);
        document.getElementById('batch-status-text').textContent = `Traitement de ${i + 1}/${files.length}...`;
    }
    
    document.getElementById('batch-status-text').textContent = 'Import terminé!';
    document.getElementById('start-import-btn').disabled = false;
    
    const alertType = errorCount === 0 ? 'success' : errorCount === files.length ? 'error' : 'warning';
    showAlert(`Import terminé: ${successCount} succès, ${errorCount} erreurs`, alertType);
    
    loadCases(1);
    loadStats();
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertClass = type === 'success' ? 'alert-success' : 
                       type === 'error' ? 'alert-error' : 
                       type === 'warning' ? 'alert-warning' : 'alert-info';
    
    alertContainer.innerHTML = `
        <div class="${alertClass}" style="margin-bottom: 1rem; padding: 1rem; border-radius: 8px; border: 3px dotted;">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}

async function checkAdminStatus() {
    try {
        const response = await fetch('/api/user/info');
        const user = await response.json();
        if (user.is_admin) {
            const adminLink = document.getElementById('admin-link');
            if (adminLink) adminLink.style.display = 'flex';
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.href = '/';
    } catch (error) {
        console.error('Erreur:', error);
    }
}

document.getElementById('logout-btn')?.addEventListener('click', logout);
document.getElementById('batch-files')?.addEventListener('change', function() {
    document.getElementById('file-count-number').textContent = this.files.length;
});

loadCases(1);
loadStats();
checkAdminStatus();
