import os
from cryptography.fernet import Fernet

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key().decode()
    
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
    OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
