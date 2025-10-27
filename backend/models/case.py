from .user import db
from datetime import datetime

class JurisprudenceCase(db.Model):
    __tablename__ = 'jurisprudence_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    
    ref = db.Column(db.String(50), unique=True, nullable=False, index=True)
    titre = db.Column(db.Text, nullable=False)
    
    juridiction = db.Column(db.String(200))
    pays_ville = db.Column(db.String(200))
    numero_decision = db.Column(db.String(100))
    date_decision = db.Column(db.Date)
    numero_dossier = db.Column(db.String(100))
    type_decision = db.Column(db.String(100))
    chambre = db.Column(db.String(100))
    
    theme = db.Column(db.Text)
    mots_cles = db.Column(db.Text)
    
    base_legale = db.Column(db.Text)
    source = db.Column(db.String(200))
    
    resume_francais_encrypted = db.Column(db.Text)
    resume_arabe_encrypted = db.Column(db.Text)
    texte_integral_encrypted = db.Column(db.Text)
    
    pdf_file_path = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JurisprudenceCase {self.ref}>'
    
    def to_dict(self, decrypt=False):
        from backend.utils.encryption import encryption_service
        from backend.utils.text_cleaner import clean_case_data
        
        data = {
            'id': self.id,
            'ref': self.ref,
            'titre': self.titre,
            'juridiction': self.juridiction,
            'pays_ville': self.pays_ville,
            'numero_decision': self.numero_decision,
            'date_decision': self.date_decision.isoformat() if self.date_decision else None,
            'numero_dossier': self.numero_dossier,
            'type_decision': self.type_decision,
            'chambre': self.chambre,
            'theme': self.theme,
            'mots_cles': self.mots_cles,
            'base_legale': self.base_legale,
            'source': self.source,
            'pdf_file_path': self.pdf_file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if decrypt:
            try:
                if self.resume_francais_encrypted:
                    data['resume_francais'] = encryption_service.decrypt(self.resume_francais_encrypted)
            except Exception as e:
                data['resume_francais'] = "[Erreur de déchiffrement - clé de chiffrement invalide]"
            
            try:
                if self.resume_arabe_encrypted:
                    data['resume_arabe'] = encryption_service.decrypt(self.resume_arabe_encrypted)
            except Exception as e:
                data['resume_arabe'] = "[خطأ في فك التشفير - مفتاح تشفير غير صالح]"
            
            try:
                if self.texte_integral_encrypted:
                    data['texte_integral'] = encryption_service.decrypt(self.texte_integral_encrypted)
            except Exception as e:
                data['texte_integral'] = "[Erreur de déchiffrement - clé de chiffrement invalide]"
        
        # Nettoie les caractères spéciaux Unicode (U+E000 à U+F8FF)
        data = clean_case_data(data)
        
        return data

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query_encrypted = db.Column(db.Text, nullable=False)
    results_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<SearchHistory {self.id}>'
