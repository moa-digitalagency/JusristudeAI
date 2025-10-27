from cryptography.fernet import Fernet
from backend.config import Config

class EncryptionService:
    def __init__(self):
        key = Config.ENCRYPTION_KEY
        if key is None:
            raise ValueError("ENCRYPTION_KEY must be set in environment variables")
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt(self, data: str) -> str:
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return ""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

encryption_service = EncryptionService()
