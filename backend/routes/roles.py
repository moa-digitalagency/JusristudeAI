from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models.role import db, Role, Permission
from backend.models.user import User

roles_bp = Blueprint('roles', __name__)

def admin_required(f):
    """Décorateur pour vérifier que l'utilisateur est admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403
        return f(*args, **kwargs)
    return decorated_function

@roles_bp.route('/roles', methods=['GET'])
@login_required
@admin_required
def get_roles():
    """Récupérer tous les rôles"""
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles]), 200

@roles_bp.route('/roles/<int:role_id>', methods=['GET'])
@login_required
@admin_required
def get_role(role_id):
    """Récupérer un rôle spécifique"""
    role = Role.query.get_or_404(role_id)
    return jsonify(role.to_dict()), 200

@roles_bp.route('/roles', methods=['POST'])
@login_required
@admin_required
def create_role():
    """Créer un nouveau rôle"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Le nom du rôle est requis'}), 400
    
    existing_role = Role.query.filter_by(name=data['name']).first()
    if existing_role:
        return jsonify({'error': 'Un rôle avec ce nom existe déjà'}), 409
    
    try:
        new_role = Role(
            name=data['name'],
            description=data.get('description'),
            is_system=False
        )
        
        if 'permission_ids' in data:
            permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
            new_role.permissions = permissions
        
        db.session.add(new_role)
        db.session.commit()
        
        return jsonify({
            'message': 'Rôle créé avec succès',
            'role': new_role.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la création: {str(e)}'}), 500

@roles_bp.route('/roles/<int:role_id>', methods=['PUT'])
@login_required
@admin_required
def update_role(role_id):
    """Mettre à jour un rôle"""
    role = Role.query.get_or_404(role_id)
    
    if role.is_system:
        return jsonify({'error': 'Les rôles système ne peuvent pas être modifiés'}), 403
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            existing_role = Role.query.filter(Role.name == data['name'], Role.id != role_id).first()
            if existing_role:
                return jsonify({'error': 'Un rôle avec ce nom existe déjà'}), 409
            role.name = data['name']
        
        if 'description' in data:
            role.description = data['description']
        
        if 'permission_ids' in data:
            permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
            role.permissions = permissions
        
        db.session.commit()
        
        return jsonify({
            'message': 'Rôle mis à jour avec succès',
            'role': role.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

@roles_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_role(role_id):
    """Supprimer un rôle"""
    role = Role.query.get_or_404(role_id)
    
    if role.is_system:
        return jsonify({'error': 'Les rôles système ne peuvent pas être supprimés'}), 403
    
    if len(role.users) > 0:
        return jsonify({'error': f'Ce rôle est assigné à {len(role.users)} utilisateur(s). Veuillez d\'abord réassigner ces utilisateurs.'}), 409
    
    try:
        db.session.delete(role)
        db.session.commit()
        return jsonify({'message': 'Rôle supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500

@roles_bp.route('/permissions', methods=['GET'])
@login_required
@admin_required
def get_permissions():
    """Récupérer toutes les permissions"""
    permissions = Permission.query.all()
    
    permissions_by_category = {}
    for perm in permissions:
        category = perm.category or 'Autres'
        if category not in permissions_by_category:
            permissions_by_category[category] = []
        permissions_by_category[category].append(perm.to_dict())
    
    return jsonify(permissions_by_category), 200

@roles_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@login_required
@admin_required
def update_user_role(user_id):
    """Assigner un rôle à un utilisateur"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'role_id' not in data:
        return jsonify({'error': 'role_id est requis'}), 400
    
    role_id = data['role_id']
    if role_id is not None:
        role = Role.query.get_or_404(role_id)
    
    try:
        user.role_id = role_id
        db.session.commit()
        
        return jsonify({
            'message': 'Rôle assigné avec succès',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'assignation: {str(e)}'}), 500
