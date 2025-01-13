import os

from string import ascii_lowercase, digits


HASH_LENGTH = 8
HASH_ALPHABET = ascii_lowercase + digits


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///app.db')
