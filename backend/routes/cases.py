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

@cases_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    total_cases = JurisprudenceCase.query.count()
    user_searches = SearchHistory.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        'total_cases': total_cases,
        'user_searches': user_searches
    }), 200
