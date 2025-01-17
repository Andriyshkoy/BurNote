import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .errors import DecryptionError


class Encryptor:
    """
    Provides methods for creating encryption keys, encrypting,
    and decrypting data.
    """

    @staticmethod
    def generate_key(password: str, note_id: str) -> bytes:
        """
        Generate a SHA-256 key from the provided password and note identifier.

        :param password: The password used to generate the key
        :param note_id: A unique identifier for the note
        :return: A 32-byte encryption key
        """
        return hashlib.sha256((password + note_id).encode()).digest()

    @staticmethod
    def encrypt_data(data: str, password: str, note_id: str) -> bytes:
        """
        Encrypt text data using AES-GCM.

        :param data: The plaintext data to be encrypted
        :param password: The password used to generate the key
        :param note_id: A unique identifier for the note
        :return: The AES-GCM encrypted data with nonce prepended
        """
        key = Encryptor.generate_key(password, note_id)
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        return nonce + ciphertext

    @staticmethod
    def decrypt_data(ciphertext: bytes, password: str, note_id: str) -> str:
        """
        Decrypt data previously encrypted with AES-GCM.

        :param ciphertext: The encrypted data (nonce + ciphertext)
        :param password: The password used to generate the key
        :param note_id: A unique identifier for the note
        :return: The decrypted plaintext as a string
        :raises DecryptionError: If decryption fails due to invalid key or data
        """
        key = Encryptor.generate_key(password, note_id)
        nonce = ciphertext[:12]
        encrypted_data = ciphertext[12:]
        aesgcm = AESGCM(key)
        try:
            decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
            return decrypted_data.decode()
        except Exception as e:
            raise DecryptionError('Invalid password or data corrupted') from e
