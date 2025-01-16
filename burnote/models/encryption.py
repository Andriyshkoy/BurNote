import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class Encryptor:

    @staticmethod
    def generate_key_iv(password: str, note_id: str):
        key = hashlib.sha256((password + note_id).encode()).digest()[:32]
        iv = hashlib.sha256((note_id + password).encode()).digest()[:16]
        return key, iv

    @staticmethod
    def encrypt_data(data: str, password: str, note_id: str) -> bytes:
        key, iv = Encryptor.generate_key_iv(password, note_id)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
        encryptor = cipher.encryptor()
        return encryptor.update(data.encode()) + encryptor.finalize()

    @staticmethod
    def decrypt_data(ciphertext: bytes, password: str, note_id: str) -> str:
        key, iv = Encryptor.generate_key_iv(password, note_id)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_data.decode()
