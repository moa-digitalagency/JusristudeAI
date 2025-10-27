let currentPage = 1;
const perPage = 20;

async function loadCases(page = 1) {
    try {
        const response = await fetch(`/api/cases?page=${page}&per_page=${perPage}`);
        const data = await response.json();
        
        displayCases(data.cases);
        displayPagination(data.page, data.pages);
        currentPage = page;
    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('casesTableBody').innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: #ef4444;">
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
                <td colspan="6" style="text-align: center; padding: 2rem;">
                    Aucun cas trouvé
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = cases.map(c => `
        <tr>
            <td><strong>${c.ref || 'N/A'}</strong></td>
            <td>${c.titre || 'Sans titre'}</td>
            <td>${c.juridiction || 'N/A'}</td>
            <td>${c.date_decision ? new Date(c.date_decision).toLocaleDateString('fr-FR') : 'N/A'}</td>
            <td>${c.type_decision || 'N/A'}</td>
            <td>
                <button class="view-btn" onclick="viewCase(${c.id})">
                    <i class="fas fa-eye"></i> Voir
                </button>
            </td>
        </tr>
    `).join('');
}

function displayPagination(currentPage, totalPages) {
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    if (currentPage > 1) {
        html += `<button class="page-btn" onclick="loadCases(${currentPage - 1})">← Précédent</button>`;
    }
    
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="loadCases(${i})">${i}</button>`;
    }
    
    if (currentPage < totalPages) {
        html += `<button class="page-btn" onclick="loadCases(${currentPage + 1})">Suivant →</button>`;
    }
    
    pagination.innerHTML = html;
}

async function viewCase(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}`);
        const caseData = await response.json();
        
        const detailsHTML = `
            <h2 style="color: #3b82f6; margin-bottom: 1.5rem;">${caseData.titre}</h2>
            
            <div class="case-detail-section">
                <h3>Identification</h3>
                <p><strong>Référence:</strong> ${caseData.ref}</p>
                <p><strong>Juridiction:</strong> ${caseData.juridiction || 'N/A'}</p>
                <p><strong>Pays/Ville:</strong> ${caseData.pays_ville || 'N/A'}</p>
                <p><strong>N° de décision:</strong> ${caseData.numero_decision || 'N/A'}</p>
                <p><strong>Date de décision:</strong> ${caseData.date_decision ? new Date(caseData.date_decision).toLocaleDateString('fr-FR') : 'N/A'}</p>
                <p><strong>N° de dossier:</strong> ${caseData.numero_dossier || 'N/A'}</p>
                <p><strong>Type de décision:</strong> ${caseData.type_decision || 'N/A'}</p>
                <p><strong>Chambre:</strong> ${caseData.chambre || 'N/A'}</p>
            </div>
            
            ${caseData.theme ? `
            <div class="case-detail-section">
                <h3>Thème</h3>
                <p>${caseData.theme}</p>
            </div>
            ` : ''}
            
            ${caseData.mots_cles ? `
            <div class="case-detail-section">
                <h3>Mots clés</h3>
                <p>${caseData.mots_cles}</p>
            </div>
            ` : ''}
            
            ${caseData.base_legale ? `
            <div class="case-detail-section">
                <h3>Base légale</h3>
                <p>${caseData.base_legale}</p>
            </div>
            ` : ''}
            
            ${caseData.source ? `
            <div class="case-detail-section">
                <h3>Source</h3>
                <p>${caseData.source}</p>
            </div>
            ` : ''}
            
            ${caseData.resume_francais ? `
            <div class="case-detail-section">
                <h3>Résumé en français</h3>
                <p>${caseData.resume_francais}</p>
            </div>
            ` : ''}
            
            ${caseData.resume_arabe ? `
            <div class="case-detail-section">
                <h3>Résumé en arabe</h3>
                <p style="direction: rtl; text-align: right;">${caseData.resume_arabe}</p>
            </div>
            ` : ''}
            
            ${caseData.texte_integral ? `
            <div class="case-detail-section">
                <h3>Texte intégral</h3>
                <p style="white-space: pre-wrap;">${caseData.texte_integral}</p>
            </div>
            ` : ''}
        `;
        
        document.getElementById('caseDetails').innerHTML = detailsHTML;
        document.getElementById('caseModal').style.display = 'block';
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors du chargement des détails du cas');
    }
}

function closeModal() {
    document.getElementById('caseModal').style.display = 'none';
}

async function deleteAllCases() {
    if (!confirm('⚠️ ATTENTION : Voulez-vous vraiment supprimer TOUS les cas de jurisprudence ? Cette action est irréversible !')) {
        return;
    }
    
    if (!confirm('Êtes-vous absolument sûr ? Tous les cas seront définitivement supprimés !')) {
        return;
    }
    
    try {
        const response = await fetch('/api/cases/delete-all', {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`✓ ${data.message}`);
            loadCases(1);
        } else {
            alert(`❌ Erreur: ${data.error}`);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression des cas');
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('caseModal');
    if (event.target === modal) {
        closeModal();
    }
}

loadCases(1);
