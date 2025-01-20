from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from . import api
from .schemas import NoteAccessSchema, NoteSchema

note_schema = NoteSchema()
note_access_schema = NoteAccessSchema()


class NotesCreateResource(Resource):
    """
    API resource for creating new notes.
    """

    def post(self):
        """
        Handle HTTP POST requests to create a new note.

        :return:
          - 201 Created with a JSON object containing the generated note key
          - 400 Bad Request if validation fails
        """
        try:
            data = note_schema.load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400
        return {'key': note_schema.dump(data)['key']}, 201


class NotesViewResource(Resource):
    """
    API resource for retrieving and decrypting existing notes.
    """

    def post(self):
        """
        Handle HTTP POST requests to fetch and decrypt an existing note.

        :return:
          - 200 OK with a JSON object containing the decrypted note data
          - 400 Bad Request if validation fails
        """
        try:
            data = note_access_schema.load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400
        return note_access_schema.dump(data)['note'], 200


api.add_resource(NotesCreateResource, '/notes/create')
api.add_resource(NotesViewResource, '/notes')
