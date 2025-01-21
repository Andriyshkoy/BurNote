import hashlib
import random
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column

from burnote import db
from settings import DOMAIN, HASH_LENGTH, KEY_ALPHABET, KEY_LENGTH

from .encryption import Encryptor


class Note(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    hash: Mapped[str] = mapped_column(
        db.String(HASH_LENGTH), nullable=False,
        unique=True, index=True
    )
    is_expired: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=False
    )

    title: Mapped[bytes] = mapped_column(db.LargeBinary, nullable=True)
    text: Mapped[bytes] = mapped_column(db.LargeBinary, nullable=False)

    timestamp: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    expiration_date: Mapped[datetime] = mapped_column(nullable=True)
    burn_after_reading: Mapped[bool] = mapped_column(db.Boolean,
                                                     nullable=False)

    def __repr__(self):
        return f'<Note {self.hash}>'

    @staticmethod
    def get_by_hash(hash: str, silent: bool = False) -> 'Note':
        """
        Retrieve a note by its hash.

        :param hash: Hash string identifying a note
        :param silent: If True, returns None when not found;
                       otherwise raises 404
        :return: The Note object or None
        :raises NotFound: If silent=False and no note matches
        """
        q = Note.query.filter_by(hash=hash)
        return q.first() if silent else q.first_or_404()

    @staticmethod
    def get_by_key(key: str, silent: bool = False) -> 'Note':
        """
        Retrieve a note by the generated key.

        :param key: Generated key for the note
        :param silent: If True, returns None when not found;
                       otherwise raises 404
        :return: The Note object or None
        :raises NotFound: If silent=False and no note matches
        """
        q = Note.query.filter_by(hash=Note.generate_hash(key))
        return q.first() if silent else q.first_or_404()

    @staticmethod
    def generate_key() -> str:
        """
        Generate a random unique key for the note.

        :return: A random string key
        """
        key = ''.join(random.choices(KEY_ALPHABET, k=KEY_LENGTH))

        while Note.get_by_key(key, silent=True):
            key = ''.join(random.choices(KEY_ALPHABET, k=KEY_LENGTH))

        return key

    @staticmethod
    def generate_hash(external_key: str) -> str:
        """
        Generate a unique hash using SHA-256 for the given key.

        :param external_key: String to be hashed
        :return: A SHA-256 hash of the provided key
        """
        return hashlib.sha256(external_key.encode()).hexdigest()

    @staticmethod
    def from_dict(data: dict) -> 'Note':
        """
        Build a new Note instance from a dictionary.

        :param data: Dictionary containing note data
        :return: A new Note instance
        :raises KeyError: If 'text' is missing in data
        """
        return Note(
            title=data.get('title', ''),
            text=data['text'],
            expiration_date=(datetime.now(timezone.utc) + data['expiration']
                             if data['expiration'] else None),
            burn_after_reading=data.get('burn_after_reading', False)
        )

    @staticmethod
    def create(data: dict, save: bool = False) -> tuple['Note', str]:
        """
        Create a new Note and optionally save it to the database.

        :param data: Dictionary containing note data
        :param save: Flag indicating whether to save the note
        :return: A tuple of (note, key) where note is the new Note instance
        :raises KeyError: If 'text' is missing in data
        """
        note = Note.from_dict(data)
        key = Note.generate_key()
        note.hash = Note.generate_hash(key)
        note.encrypt(key, data.get('password', ''))
        if save:
            note.save()
        return note, key

    def copy(self) -> 'Note':
        """
        Copy the current note data.

        :return: A new Note instance with the same data
        """
        return Note(
            title=self.title,
            text=self.text,
            expiration_date=self.expiration_date,
            burn_after_reading=self.burn_after_reading
        )

    def save(self) -> None:
        """
        Save the current note to the database.

        :return: None
        """
        db.session.add(self)
        db.session.commit()

    def encrypt(self, key: str, password: str) -> None:
        """
        Encrypt the note's title and text.

        :param key: Key used for encryption
        :param password: Password used for encryption
        :return: None
        """
        self.text = Encryptor.encrypt_data(self.text, password, key)
        self.title = Encryptor.encrypt_data(self.title, password, key)

    def decrypt(self, key: str, password: str) -> 'Note':
        """
        Decrypt the note's title and text.

        :param key: Key used for decryption
        :param password: Password used for decryption
        :return: The current Note instance (possibly expired)
        """
        self.text = Encryptor.decrypt_data(self.text, password, key)
        self.title = Encryptor.decrypt_data(self.title, password, key)
        if self.burn_after_reading:
            return self.expire()
        return self

    def is_available(self) -> bool:
        """
        Return True if the note is not expired, otherwise False.

        :return: Boolean indicating if the note is still available
        """
        if self.is_expired:
            return False

        if self.expiration_date:
            if datetime.now(timezone.utc) > self.expiration_date.replace(
                    tzinfo=timezone.utc):
                self.expire()
                return False

        return True

    def get_link(self, key: str) -> str:
        """
        Return the note's URL using the provided key.

        :param key: Key to include in the note’s link
        :return: The generated URL as a string
        """
        return f'https://{DOMAIN}/{key}'

    def expire(self) -> 'Note':
        """
        Mark the note as expired and clear its title and text.

        :return: A copy of the note with original data
        """
        self.is_expired = True
        self.expiration_date = datetime.now(timezone.utc)
        copy = self.copy()
        self.text = b''
        self.title = b''
        db.session.commit()
        return copy
