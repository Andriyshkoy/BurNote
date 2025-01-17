import hashlib
import random
from datetime import datetime, timezone

from flask import url_for
from sqlalchemy.orm import Mapped, mapped_column

from burnote import db
from settings import HASH_LENGTH, KEY_ALPHABET, KEY_LENGTH

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

    title: Mapped[str] = mapped_column(db.String(256), nullable=True)
    text: Mapped[str] = mapped_column(db.Text, nullable=False)
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
    def get_by_hash(hash, silent=False):
        q = Note.query.filter_by(hash=hash)
        return q.first() if silent else q.first_or_404()

    @staticmethod
    def get_by_key(key, silent=False):
        q = Note.query.filter_by(hash=Note.generate_hash(key))
        return q.first() if silent else q.first_or_404()

    @staticmethod
    def generate_key():
        key = ''.join(random.choices(KEY_ALPHABET, k=KEY_LENGTH))

        while Note.get_by_key(key, silent=True):
            key = ''.join(random.choices(KEY_ALPHABET, k=KEY_LENGTH))

        return key

    @staticmethod
    def generate_hash(external_key: str) -> str:
        return hashlib.sha256(external_key.encode()).hexdigest()

    @staticmethod
    def from_dict(data):
        return Note(
            title=data.get('title', ''),
            text=data['text'],
            expiration_date=(datetime.now(timezone.utc) + data['expiration']
                             if data['expiration'] else None),
            burn_after_reading=data.get('burn_after_reading', False)
        )

    @staticmethod
    def create(data, save=False):
        note = Note.from_dict(data)
        key = Note.generate_key()
        note.hash = Note.generate_hash(key)
        note.encrypt(key, data.get('password', ''))
        if save:
            note.save()
        return note, key

    def copy(self):
        return Note(
            title=self.title,
            text=self.text,
            expiration_date=self.expiration_date,
            burn_after_reading=self.burn_after_reading
        )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def encrypt(self, key, password):
        self.text = Encryptor.encrypt_data(self.text, password, key)
        self.title = Encryptor.encrypt_data(self.title, password, key)

    def decrypt(self, key, password):
        self.text = Encryptor.decrypt_data(self.text, password, key)
        self.title = Encryptor.decrypt_data(self.title, password, key)
        if self.burn_after_reading:
            return self.expire()
        return self

    def is_available(self):
        if self.is_expired:
            return False

        if self.expiration_date:
            if datetime.now(timezone.utc) > self.expiration_date.replace(
                    tzinfo=timezone.utc):
                self.expire()
                return False

        return True

    def get_link(self, key):
        return url_for('webapp.note_view', key=key, _external=True)

    def expire(self):
        self.is_expired = True
        self.expiration_date = datetime.now(timezone.utc)
        copy = self.copy()
        self.text = ''
        self.title = ''
        db.session.commit()
        return copy
