from flask_restful import Resource

from . import api
from .parsers import parser, parse_time_unit
from burnote.models import Note
from burnote.models.errors import DecryptionError


class NotesResource(Resource):

    def get(self):
        args = parser.get.parse_args(strict=True)
        key = args['key']
        password = args.get('password') or ''

        note = Note.get_by_key(key, silent=True)

        if not note:
            return {'message': 'Note not found'}, 404

        if not note.is_available():
            return {'message': 'Note has expired and has been deleted'}, 410

        try:
            note.decrypt(key, password)
        except DecryptionError:
            return {'password': 'Invalid password'}, 400

        return {
            'title': note.title,
            'text': note.text,
            'timestamp': note.timestamp.isoformat(),
            'expiration_date': (note.expiration_date.isoformat()
                                if note.expiration_date else None),
            'burn_after_reading': note.burn_after_reading
        }, 200

    def post(self):
        args = parser.post.parse_args(strict=True)
        args['expiration'] = parse_time_unit(args['expiration'])
        note, key = Note.create(args)
        note.save()
        return {'key': key}, 201


api.add_resource(NotesResource, '/notes')
