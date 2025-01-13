import random
from datetime import datetime, timezone

from flask import url_for
from sqlalchemy.orm import Mapped, mapped_column

from fastnote import db
from settings import HASH_LENGTH, HASH_ALPHABET


class Note(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    hash: Mapped[str] = mapped_column(
        db.String(HASH_LENGTH), nullable=False, unique=True,
        default=lambda: Note.generate_hash())
    is_expired: Mapped[bool] = mapped_column(db.Boolean, nullable=False,
                                             default=False)

    title: Mapped[str] = mapped_column(db.String(100), nullable=True)
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
    def generate_hash():
        hash = ''.join(random.choices(HASH_ALPHABET, k=HASH_LENGTH))

        while Note.query.filter_by(hash=hash).first():
            hash = ''.join(random.choices(HASH_ALPHABET, k=HASH_LENGTH))

        return hash

    @staticmethod
    def from_dict(data):
        if 'expiration' in data:
            if data['expiration']:
                data['expiration'] = (datetime.now(timezone.utc) +
                                      data['expiration'])
            else:
                data['expiration'] = None

        return Note(
            title=data['title'],
            text=data['text'],
            expiration_date=data['expiration'],
            burn_after_reading=data['burn_after_reading']
        )

    def to_dict(self):
        return {
            'hash': self.hash,
            'title': self.title,
            'text': self.text,
            'timestamp': self.timestamp,
            'expiration_date': self.expiration_date,
            'burn_after_reading': self.burn_after_reading
        }

    def is_available(self):
        if self.is_expired:
            return False

        if self.expiration_date:
            return (datetime.now(timezone.utc) < self.expiration_date.replace(
                tzinfo=timezone.utc))

        return True

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_link(self):
        return url_for('webapp.note', hash=self.hash, _external=True)

    def expire(self):
        self.is_expired = True
        self.expiration_date = datetime.now(timezone.utc)
        db.session.commit()

    @staticmethod
    def get_by_hash(hash):
        return Note.query.filter_by(hash=hash).first_or_404()
