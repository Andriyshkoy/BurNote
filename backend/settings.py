import os

from string import ascii_lowercase, digits


HASH_LENGTH = 64

KEY_ALPHABET = ascii_lowercase + digits
KEY_LENGTH = 8
DOMAIN = os.environ.get('DOMAIN', 'localhost:5000')
SCHEMA = 'https' if os.environ.get('HTTPS', '0') == '1' else 'http'

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
