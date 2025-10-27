from .user import db
from datetime import datetime

class JurisprudenceCase(db.Model):
    __tablename__ = 'jurisprudence_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.Text, nullable=False)
    description_encrypted = db.Column(db.Text, nullable=False)
    facts_encrypted = db.Column(db.Text, nullable=False)
    decision_encrypted = db.Column(db.Text, nullable=False)
    court = db.Column(db.String(200), nullable=False)
    date_decision = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<JurisprudenceCase {self.case_number}>'

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query_encrypted = db.Column(db.Text, nullable=False)
    results_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<SearchHistory {self.id}>'
