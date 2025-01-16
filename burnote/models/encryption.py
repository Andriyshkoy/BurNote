import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .errors import DecryptionError


class Encryptor:

    @staticmethod
    def generate_key(password: str, note_id: str) -> bytes:
        return hashlib.sha256((password + note_id).encode()).digest()

    @staticmethod
    def encrypt_data(data: str, password: str, note_id: str) -> bytes:
        key = Encryptor.generate_key(password, note_id)
        # AES-GCM требует уникального nonce для каждой операции шифрования
        nonce = os.urandom(12)  # 96 бит (12 байт) для AES-GCM
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        return nonce + ciphertext

    @staticmethod
    def decrypt_data(ciphertext: bytes, password: str, note_id: str) -> str:
        key = Encryptor.generate_key(password, note_id)
        nonce = ciphertext[:12]
        encrypted_data = ciphertext[12:]
        aesgcm = AESGCM(key)
        try:
            decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
            return decrypted_data.decode()
        except Exception as e:
            raise DecryptionError('Invalid password or data corrupted') from e
