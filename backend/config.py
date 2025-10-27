import os
import sys
from cryptography.fernet import Fernet

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        SECRET_KEY = os.urandom(24).hex()
        print("⚠️  Avertissement: SECRET_KEY non définie, une clé temporaire a été générée")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    if not ENCRYPTION_KEY:
        print("❌ ERREUR CRITIQUE: ENCRYPTION_KEY doit être définie comme variable d'environnement")
        print("   Générez une clé avec: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'")
        print("   Puis ajoutez-la aux secrets Replit")
        ENCRYPTION_KEY = Fernet.generate_key().decode()
        print(f"⚠️  Clé temporaire générée pour cette session: {ENCRYPTION_KEY}")
        print("⚠️  ATTENTION: Les données seront perdues au prochain redémarrage!")
    
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
    OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
    
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
