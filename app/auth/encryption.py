import os
import sys
import base64
from cryptography.fernet import Fernet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def generate_encryption_key():
    return Fernet.generate_key()


def encrypt_2fa_secret(secret: str, key: bytes):
    f = Fernet(key)
    encrypted_secret = f.encrypt(secret.encode())
    # Return as a Base64-encoded string
    return base64.b64encode(encrypted_secret).decode('utf-8')


def decrypt_2fa_secret(encrypted_secret: str, key: bytes) -> str:
    f = Fernet(key)
    try:
        # Decode the Base64-encoded encrypted secret back to bytes
        encrypted_bytes = base64.b64decode(encrypted_secret.encode('utf-8'))
        secret = f.decrypt(encrypted_bytes).decode()
        return secret
    except Exception as exc:
        raise ValueError(
            "Decryption failed. Possible key mismatch or corrupted data."
        ) from exc

