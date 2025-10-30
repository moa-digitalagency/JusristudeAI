from backend.models.user import db
from datetime import datetime

class Settings(db.Model):
    """
    Modèle pour les paramètres configurables de la plateforme
    """
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Settings {self.key}={self.value}>'
    
    @staticmethod
    def get_value(key, default=None):
        """Récupère la valeur d'un paramètre"""
        setting = Settings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_value(key, value, description=None):
        """Définit la valeur d'un paramètre"""
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = Settings(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting
    
    @staticmethod
    def initialize_defaults():
        """Initialise les paramètres par défaut"""
        defaults = {
            'platform_name': {
                'value': 'LexIA',
                'description': 'Nom de la plateforme affiché partout'
            },
            'platform_tagline': {
                'value': 'Intelligence Artificielle au service du Droit',
                'description': 'Slogan de la plateforme'
            },
            'platform_description': {
                'value': 'Plateforme de recherche juridique alimentée par l\'IA pour trouver des précédents et analyser des cas',
                'description': 'Description SEO de la plateforme'
            },
            'platform_keywords': {
                'value': 'jurisprudence, IA juridique, recherche juridique, cas juridiques, intelligence artificielle, droit',
                'description': 'Mots-clés SEO (séparés par des virgules)'
            },
            'admin_email': {
                'value': 'admin@jurisprudence.com',
                'description': 'Email de l\'administrateur principal'
            },
            'max_upload_size': {
                'value': '100',
                'description': 'Taille maximale d\'upload en MB'
            },
            'max_batch_import': {
                'value': '200',
                'description': 'Nombre maximum de PDFs pour import en masse'
            }
        }
        
        for key, data in defaults.items():
            if not Settings.query.filter_by(key=key).first():
                Settings.set_value(key, data['value'], data['description'])
