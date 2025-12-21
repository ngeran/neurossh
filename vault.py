from cryptography.fernet import Fernet
import os

class Vault:
    def __init__(self, master_key=None):
        self.key = master_key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def seal(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())

    def reveal(self, token: bytes) -> str:
        return self.cipher.decrypt(token).decode()
