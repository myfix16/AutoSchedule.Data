from typing import Optional
from cryptography.fernet import Fernet


class TokenManager():
    def __init__(self, key: Optional[str] = None) -> None:
        super().__init__()
        self.key = key

    def generate_key(self):
        """
        Generates a key.
        """
        self.key = Fernet.generate_key()
        return self.key

    def store_key(self, path: str):
        with open(f"{path}.key", "wb") as key_file:
            key_file.write(self.key)

    def load_key(self, path: str) -> None:
        """
        Load the previously generated key
        """
        self.key = open(f"{path}", "rb").read()

    def encrypt_message(self, message: str) -> str:
        """
        Encrypts a message
        """
        if self.key==None:
            raise ValueError("No key loaded.")
        encoded_message = message.encode()
        f = Fernet(self.key)
        return f.encrypt(encoded_message)

    def decrypt_message(self, encrypted_message: str) -> str:
        """
        Decrypts an encrypted message
        """
        if self.key==None:
            raise ValueError("No key loaded.")
        f = Fernet(self.key)
        return f.decrypt(encrypted_message)

manager = TokenManager()
manager.load_key("secret.key")
