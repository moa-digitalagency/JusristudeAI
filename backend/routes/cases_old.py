from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models.case import db, JurisprudenceCase, SearchHistory
from backend.utils.encryption import encryption_service
from backend.services.ai_service import ai_service
from datetime import datetime
import pandas as pd
import PyPDF2
from docx import Document
import io

cases_bp = Blueprint('cases', __name__)

@cases_bp.route('/cases', methods=['GET'])
@login_required
def get_cases():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    cases = JurisprudenceCase.query.order_by(JurisprudenceCase.date_decision.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'cases': [{
            'id': case.id,
            'case_number': case.case_number,
            'title': case.title,
            'description': encryption_service.decrypt(case.description_encrypted),
            'court': case.court,
            'date_decision': case.date_decision.isoformat(),
            'category': case.category,
            'keywords': case.keywords
        } for case in cases.items],
        'total': cases.total,
        'page': cases.page,
        'pages': cases.pages
    }), 200

@cases_bp.route('/cases/<int:case_id>', methods=['GET'])
@login_required
def get_case(case_id):
    case = JurisprudenceCase.query.get_or_404(case_id)
    
    return jsonify({
        'id': case.id,
        'case_number': case.case_number,
        'title': case.title,
        'description': encryption_service.decrypt(case.description_encrypted),
        'facts': encryption_service.decrypt(case.facts_encrypted),
        'decision': encryption_service.decrypt(case.decision_encrypted),
        'court': case.court,
        'date_decision': case.date_decision.isoformat(),
        'category': case.category,
        'keywords': case.keywords
    }), 200

@cases_bp.route('/cases', methods=['POST'])
@login_required
def create_case():
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    
    new_case = JurisprudenceCase(
        case_number=data['case_number'],
        title=data['title'],
        description_encrypted=encryption_service.encrypt(data['description']),
        facts_encrypted=encryption_service.encrypt(data['facts']),
        decision_encrypted=encryption_service.encrypt(data['decision']),
        court=data['court'],
        date_decision=datetime.strptime(data['date_decision'], '%Y-%m-%d').date(),
        category=data['category'],
        keywords=data.get('keywords', ''),
        created_by=current_user.id
    )
    
    db.session.add(new_case)
    db.session.commit()
    
    return jsonify({
        'message': 'Cas de jurisprudence créé avec succès',
        'case_id': new_case.id
    }), 201

@cases_bp.route('/cases/<int:case_id>', methods=['PUT'])
@login_required
def update_case(case_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    case = JurisprudenceCase.query.get_or_404(case_id)
    data = request.get_json()
    
    if 'case_number' in data:
        case.case_number = data['case_number']
    if 'title' in data:
        case.title = data['title']
    if 'description' in data:
        case.description_encrypted = encryption_service.encrypt(data['description'])
    if 'facts' in data:
        case.facts_encrypted = encryption_service.encrypt(data['facts'])
    if 'decision' in data:
        case.decision_encrypted = encryption_service.encrypt(data['decision'])
    if 'court' in data:
        case.court = data['court']
    if 'date_decision' in data:
        case.date_decision = datetime.strptime(data['date_decision'], '%Y-%m-%d').date()
    if 'category' in data:
        case.category = data['category']
    if 'keywords' in data:
        case.keywords = data['keywords']
    
    db.session.commit()
    
    return jsonify({'message': 'Cas mis à jour avec succès'}), 200

@cases_bp.route('/cases/<int:case_id>', methods=['DELETE'])
@login_required
def delete_case(case_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    case = JurisprudenceCase.query.get_or_404(case_id)
    db.session.delete(case)
    db.session.commit()
    
    return jsonify({'message': 'Cas supprimé avec succès'}), 200

@cases_bp.route('/search', methods=['POST'])
@login_required
def search_similar_cases():
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Requête vide'}), 400
    
    all_cases = JurisprudenceCase.query.all()
    decrypted_cases = [{
        'id': case.id,
        'case_number': case.case_number,
        'title': case.title,
        'description': encryption_service.decrypt(case.description_encrypted),
        'court': case.court,
        'category': case.category
    } for case in all_cases]
    
    ai_result = ai_service.find_similar_cases(query, decrypted_cases)
    
    search_history = SearchHistory(
        user_id=current_user.id,
        query_encrypted=encryption_service.encrypt(query),
        results_count=len(decrypted_cases)
    )
    db.session.add(search_history)
    db.session.commit()
    
    return jsonify(ai_result), 200

@cases_bp.route('/search/file', methods=['POST'])
@login_required
def search_by_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400
    
    query = ''
    try:
        if file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            query = ' '.join([page.extract_text() for page in pdf_reader.pages])
        elif file.filename.endswith('.docx'):
            doc = Document(file)
            query = ' '.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            return jsonify({'error': 'Format de fichier non supporté. Utilisez PDF ou DOCX'}), 400
        
        if not query.strip():
            return jsonify({'error': 'Le document est vide ou ne contient pas de texte'}), 400
        
        all_cases = JurisprudenceCase.query.all()
        decrypted_cases = [{
            'id': case.id,
            'case_number': case.case_number,
            'title': case.title,
            'description': encryption_service.decrypt(case.description_encrypted),
            'court': case.court,
            'category': case.category
        } for case in all_cases]
        
        ai_result = ai_service.find_similar_cases(query, decrypted_cases)
        
        search_history = SearchHistory(
            user_id=current_user.id,
            query_encrypted=encryption_service.encrypt(f"[Fichier: {file.filename}] {query[:500]}"),
            results_count=len(decrypted_cases)
        )
        db.session.add(search_history)
        db.session.commit()
        
        return jsonify(ai_result), 200
    
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement du fichier: {str(e)}'}), 500

@cases_bp.route('/import/csv', methods=['POST'])
@login_required
def import_csv():
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'Format non supporté. Utilisez CSV ou Excel'}), 400
        
        required_columns = ['case_number', 'title', 'description', 'facts', 'decision', 'court', 'date_decision', 'category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'Colonnes manquantes: {", ".join(missing_columns)}'}), 400
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                if JurisprudenceCase.query.filter_by(case_number=row['case_number']).first():
                    errors.append(f"Ligne {index + 1}: Numéro de cas {row['case_number']} déjà existant")
                    continue
                
                new_case = JurisprudenceCase(
                    case_number=str(row['case_number']),
                    title=str(row['title']),
                    description_encrypted=encryption_service.encrypt(str(row['description'])),
                    facts_encrypted=encryption_service.encrypt(str(row['facts'])),
                    decision_encrypted=encryption_service.encrypt(str(row['decision'])),
                    court=str(row['court']),
                    date_decision=pd.to_datetime(row['date_decision']).date(),
                    category=str(row['category']),
                    keywords=str(row.get('keywords', '')),
                    created_by=current_user.id
                )
                db.session.add(new_case)
                imported_count += 1
            except Exception as e:
                errors.append(f"Ligne {index + 1}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'{imported_count} cas importés avec succès',
            'imported_count': imported_count,
            'errors': errors
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'importation: {str(e)}'}), 500

@cases_bp.route('/import/pdf', methods=['POST'])
@login_required
def import_pdf():
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    data = request.form
    
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Fichier PDF requis'}), 400
    
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        extracted_text = ' '.join([page.extract_text() for page in pdf_reader.pages])
        
        if not extracted_text.strip():
            return jsonify({'error': 'Le PDF ne contient pas de texte'}), 400
        
        new_case = JurisprudenceCase(
            case_number=data.get('case_number'),
            title=data.get('title'),
            description_encrypted=encryption_service.encrypt(data.get('description', extracted_text[:500])),
            facts_encrypted=encryption_service.encrypt(extracted_text),
            decision_encrypted=encryption_service.encrypt(data.get('decision', '')),
            court=data.get('court'),
            date_decision=datetime.strptime(data.get('date_decision'), '%Y-%m-%d').date(),
            category=data.get('category'),
            keywords=data.get('keywords', ''),
            created_by=current_user.id
        )
        
        db.session.add(new_case)
        db.session.commit()
        
        return jsonify({
            'message': 'Cas importé depuis PDF avec succès',
            'case_id': new_case.id
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'importation du PDF: {str(e)}'}), 500

@cases_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    total_cases = JurisprudenceCase.query.count()
    user_searches = SearchHistory.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        'total_cases': total_cases,
        'user_searches': user_searches
    }), 200
