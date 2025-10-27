from datetime import datetime
from backend.models.user import db

# Table d'association pour la relation many-to-many entre Role et Permission
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    is_system = db.Column(db.Boolean, default=False, nullable=False)  # Les rôles système ne peuvent pas être supprimés
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relations
    permissions = db.relationship('Permission', secondary=role_permissions, lazy='subquery',
                                  backref=db.backref('roles', lazy=True))
    users = db.relationship('User', backref='role', lazy=True)
    
    def __init__(self, name, description=None, is_system=False):
        self.name = name
        self.description = description
        self.is_system = is_system
    
    def has_permission(self, permission_name):
        """Vérifie si ce rôle a une permission spécifique"""
        return any(p.name == permission_name for p in self.permissions)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_system': self.is_system,
            'permissions': [p.to_dict() for p in self.permissions],
            'user_count': len(self.users),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'


class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))  # Pour grouper les permissions (ex: 'cases', 'admin', 'search')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, name, description=None, category=None):
        self.name = name
        self.description = description
        self.category = category
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category
        }
    
    def __repr__(self):
        return f'<Permission {self.name}>'
