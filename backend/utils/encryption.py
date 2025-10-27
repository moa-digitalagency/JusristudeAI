from cryptography.fernet import Fernet
from backend.config import Config

class EncryptionService:
    def __init__(self):
        self.cipher = Fernet(Config.ENCRYPTION_KEY.encode() if isinstance(Config.ENCRYPTION_KEY, str) else Config.ENCRYPTION_KEY)
    
    def encrypt(self, data: str) -> str:
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return ""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

encryption_service = EncryptionService()
