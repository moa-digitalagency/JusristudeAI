from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from backend.models.user import db, User

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Cet email est déjà utilisé'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    new_user = User(
        email=data['email'],
        password_hash=hashed_password,
        first_name=data['first_name'],
        last_name=data['last_name'],
        is_approved=False,
        is_admin=False
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
def get_pending_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    pending_users = User.query.filter_by(is_approved=False).all()
    
    return jsonify({
        'users': [{
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'created_at': user.created_at.isoformat()
        } for user in pending_users]
    }), 200

@auth_bp.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    return jsonify({'message': f'Utilisateur {user.email} approuvé'}), 200
