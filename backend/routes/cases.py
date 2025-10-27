from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models.case import db, JurisprudenceCase, SearchHistory
from backend.utils.encryption import encryption_service
from backend.services.ai_service import ai_service
from datetime import datetime

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
        'cases': [case.to_dict(decrypt=False) for case in cases.items],
        'total': cases.total,
        'page': cases.page,
        'pages': cases.pages
    }), 200

@cases_bp.route('/cases/<int:case_id>', methods=['GET'])
@login_required
def get_case(case_id):
    case = JurisprudenceCase.query.get_or_404(case_id)
    return jsonify(case.to_dict(decrypt=True)), 200

@cases_bp.route('/cases', methods=['POST'])
@login_required
def create_case():
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    
    required_fields = ['ref', 'titre']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Le champ {field} est requis'}), 400
    
    existing_case = JurisprudenceCase.query.filter_by(ref=data['ref']).first()
    if existing_case:
        return jsonify({'error': f'Un cas avec la référence {data["ref"]} existe déjà'}), 409
    
    try:
        date_decision = None
        if data.get('date_decision'):
            date_decision = datetime.strptime(data['date_decision'], '%Y-%m-%d').date()
        
        new_case = JurisprudenceCase(
            ref=data['ref'],
            titre=data['titre'],
            juridiction=data.get('juridiction'),
            pays_ville=data.get('pays_ville'),
            numero_decision=data.get('numero_decision'),
            date_decision=date_decision,
            numero_dossier=data.get('numero_dossier'),
            type_decision=data.get('type_decision'),
            chambre=data.get('chambre'),
            theme=data.get('theme'),
            mots_cles=data.get('mots_cles'),
            base_legale=data.get('base_legale'),
            source=data.get('source'),
            resume_francais_encrypted=encryption_service.encrypt(data.get('resume_francais', '')) if data.get('resume_francais') else None,
            resume_arabe_encrypted=encryption_service.encrypt(data.get('resume_arabe', '')) if data.get('resume_arabe') else None,
            texte_integral_encrypted=encryption_service.encrypt(data.get('texte_integral', '')) if data.get('texte_integral') else None,
            created_by=current_user.id
        )
        
        db.session.add(new_case)
        db.session.commit()
        
        return jsonify({
            'message': 'Cas de jurisprudence créé avec succès',
            'case': new_case.to_dict(decrypt=True)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la création: {str(e)}'}), 500

@cases_bp.route('/cases/<int:case_id>', methods=['PUT'])
@login_required
def update_case(case_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    case = JurisprudenceCase.query.get_or_404(case_id)
    data = request.get_json()
    
    try:
        if 'ref' in data:
            case.ref = data['ref']
        if 'titre' in data:
            case.titre = data['titre']
        if 'juridiction' in data:
            case.juridiction = data['juridiction']
        if 'pays_ville' in data:
            case.pays_ville = data['pays_ville']
        if 'numero_decision' in data:
            case.numero_decision = data['numero_decision']
        if 'date_decision' in data:
            case.date_decision = datetime.strptime(data['date_decision'], '%Y-%m-%d').date() if data['date_decision'] else None
        if 'numero_dossier' in data:
            case.numero_dossier = data['numero_dossier']
        if 'type_decision' in data:
            case.type_decision = data['type_decision']
        if 'chambre' in data:
            case.chambre = data['chambre']
        if 'theme' in data:
            case.theme = data['theme']
        if 'mots_cles' in data:
            case.mots_cles = data['mots_cles']
        if 'base_legale' in data:
            case.base_legale = data['base_legale']
        if 'source' in data:
            case.source = data['source']
        if 'resume_francais' in data:
            case.resume_francais_encrypted = encryption_service.encrypt(data['resume_francais']) if data['resume_francais'] else None
        if 'resume_arabe' in data:
            case.resume_arabe_encrypted = encryption_service.encrypt(data['resume_arabe']) if data['resume_arabe'] else None
        if 'texte_integral' in data:
            case.texte_integral_encrypted = encryption_service.encrypt(data['texte_integral']) if data['texte_integral'] else None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cas mis à jour avec succès',
            'case': case.to_dict(decrypt=True)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

@cases_bp.route('/cases/<int:case_id>', methods=['DELETE'])
@login_required
def delete_case(case_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    case = JurisprudenceCase.query.get_or_404(case_id)
    
    try:
        db.session.delete(case)
        db.session.commit()
        return jsonify({'message': 'Cas supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500

@cases_bp.route('/search', methods=['POST'])
@login_required
def search_similar_cases():
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Requête vide'}), 400
    
    all_cases = JurisprudenceCase.query.all()
    decrypted_cases = [case.to_dict(decrypt=True) for case in all_cases]
    
    ai_result = ai_service.find_similar_cases(query, decrypted_cases)
    
    search_history = SearchHistory(
        user_id=current_user.id,
        query_encrypted=encryption_service.encrypt(query),
        results_count=len(decrypted_cases)
    )
    db.session.add(search_history)
    db.session.commit()
    
    return jsonify(ai_result), 200

@cases_bp.route('/search/stream', methods=['POST'])
@login_required
def search_similar_cases_stream():
    """Version avec streaming pour afficher la réflexion de l'IA en temps réel"""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Requête vide'}), 400
    
    all_cases = JurisprudenceCase.query.all()
    decrypted_cases = [case.to_dict(decrypt=True) for case in all_cases]
    
    # Sauvegarder l'historique de recherche
    search_history = SearchHistory(
        user_id=current_user.id,
        query_encrypted=encryption_service.encrypt(query),
        results_count=len(decrypted_cases)
    )
    db.session.add(search_history)
    db.session.commit()
    
    # Retourner un générateur pour le streaming SSE
    from flask import Response
    return Response(
        ai_service.find_similar_cases_streaming(query, decrypted_cases),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@cases_bp.route('/cases/stats', methods=['GET'])
@login_required
def get_case_stats():
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    total = JurisprudenceCase.query.count()
    
    this_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = JurisprudenceCase.query.filter(
        JurisprudenceCase.created_at >= this_month_start
    ).count()
    
    my_cases = JurisprudenceCase.query.filter_by(created_by=current_user.id).count()
    
    with_pdf = JurisprudenceCase.query.filter(
        JurisprudenceCase.pdf_file_path.isnot(None)
    ).count()
    
    return jsonify({
        'total': total,
        'this_month': this_month,
        'my_cases': my_cases,
        'with_pdf': with_pdf
    }), 200

@cases_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    total_cases = JurisprudenceCase.query.count()
    user_searches = SearchHistory.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        'total_cases': total_cases,
        'user_searches': user_searches
    }), 200

@cases_bp.route('/cases/delete-all', methods=['DELETE'])
@login_required
def delete_all_cases():
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    try:
        count = JurisprudenceCase.query.count()
        JurisprudenceCase.query.delete()
        db.session.commit()
        return jsonify({
            'message': f'{count} cas supprimés avec succès',
            'count': count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500

@cases_bp.route('/cases/delete-selected', methods=['POST'])
@login_required
def delete_selected_cases():
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    case_ids = data.get('case_ids', [])
    
    if not case_ids:
        return jsonify({'error': 'Aucun cas sélectionné'}), 400
    
    try:
        deleted_count = 0
        for case_id in case_ids:
            case = JurisprudenceCase.query.get(case_id)
            if case:
                db.session.delete(case)
                deleted_count += 1
        
        db.session.commit()
        return jsonify({
            'message': f'{deleted_count} cas supprimé(s) avec succès',
            'count': deleted_count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500
