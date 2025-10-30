from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models.user import db
from backend.models.settings import Settings

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET'])
def get_all_settings():
    """Récupère tous les paramètres (publics)"""
    try:
        public_keys = ['platform_name', 'platform_tagline', 'platform_description', 'platform_keywords']
        settings = Settings.query.filter(Settings.key.in_(public_keys)).all()
        
        return jsonify({
            'settings': {s.key: s.value for s in settings}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/<key>', methods=['GET'])
def get_setting(key):
    """Récupère un paramètre spécifique"""
    try:
        public_keys = ['platform_name', 'platform_tagline', 'platform_description', 'platform_keywords']
        
        if key not in public_keys:
            return jsonify({'error': 'Paramètre non accessible'}), 403
        
        value = Settings.get_value(key, '')
        return jsonify({
            'key': key,
            'value': value
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/admin/settings', methods=['GET'])
@login_required
def get_admin_settings():
    """Récupère tous les paramètres (admin seulement)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Accès refusé'}), 403
    
    try:
        settings = Settings.query.all()
        return jsonify({
            'settings': [{
                'id': s.id,
                'key': s.key,
                'value': s.value,
                'description': s.description,
                'updated_at': s.updated_at.isoformat() if s.updated_at else None
            } for s in settings]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/admin/settings/<key>', methods=['PUT'])
@login_required
def update_setting(key):
    """Met à jour un paramètre (admin seulement)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Accès refusé'}), 403
    
    try:
        data = request.get_json()
        value = data.get('value')
        description = data.get('description')
        
        if value is None:
            return jsonify({'error': 'La valeur est requise'}), 400
        
        setting = Settings.set_value(key, value, description)
        
        return jsonify({
            'message': 'Paramètre mis à jour avec succès',
            'setting': {
                'id': setting.id,
                'key': setting.key,
                'value': setting.value,
                'description': setting.description
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/admin/settings', methods=['POST'])
@login_required
def create_setting():
    """Crée un nouveau paramètre (admin seulement)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Accès refusé'}), 403
    
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        description = data.get('description')
        
        if not key:
            return jsonify({'error': 'La clé est requise'}), 400
        
        if Settings.query.filter_by(key=key).first():
            return jsonify({'error': 'Ce paramètre existe déjà'}), 400
        
        setting = Settings.set_value(key, value or '', description)
        
        return jsonify({
            'message': 'Paramètre créé avec succès',
            'setting': {
                'id': setting.id,
                'key': setting.key,
                'value': setting.value,
                'description': setting.description
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
