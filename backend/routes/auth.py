from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from backend.models.user import db, User
from backend.models.role import Role

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Cet email est déjà utilisé'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    juriste_role = Role.query.filter_by(name='Juriste').first()
    
    new_user = User(
        email=data['email'],
        password_hash=hashed_password,
        first_name=data['first_name'],
        last_name=data['last_name'],
        is_approved=False,
        is_admin=False,
        role_id=juriste_role.id if juriste_role else None
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'Inscription réussie. En attente de validation par un administrateur.',
        'user_id': new_user.id
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
    
    if not user.is_approved:
        return jsonify({'error': 'Votre compte est en attente de validation par un administrateur'}), 403
    
    login_user(user)
    
    return jsonify({
        'message': 'Connexion réussie',
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user.is_admin
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Déconnexion réussie'}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'is_admin': current_user.is_admin
        }
    }), 200

@auth_bp.route('/admin/users', methods=['GET'])
@login_required
def get_all_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'pending':
        users = User.query.filter_by(is_approved=False).all()
    elif status_filter == 'approved':
        users = User.query.filter_by(is_approved=True).all()
    else:
        users = User.query.all()
    
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@auth_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@auth_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'is_approved' in data:
        user.is_approved = data['is_approved']
    if 'is_admin' in data:
        user.is_admin = data['is_admin']
    
    db.session.commit()
    return jsonify({'message': f'Utilisateur {user.email} mis à jour'}), 200

@auth_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    if user_id == current_user.id:
        return jsonify({'error': 'Vous ne pouvez pas supprimer votre propre compte'}), 400
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': f'Utilisateur {user.email} supprimé'}), 200

@auth_bp.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    return jsonify({'message': f'Utilisateur {user.email} approuvé'}), 200

@auth_bp.route('/admin/suspend/<int:user_id>', methods=['POST'])
@login_required
def suspend_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    if user_id == current_user.id:
        return jsonify({'error': 'Vous ne pouvez pas suspendre votre propre compte'}), 400
    
    user = User.query.get_or_404(user_id)
    user.is_approved = False
    db.session.commit()
    
    return jsonify({'message': f'Utilisateur {user.email} suspendu'}), 200
