from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from . import api
from .schemas import NoteSchema, NoteAccessSchema

note_schema = NoteSchema()
note_access_schema = NoteAccessSchema()


class NotesCreateResource(Resource):
    def post(self):
        try:
            data = note_schema.load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400
        return {'key': note_schema.dump(data)['key']}, 201


class NotesViewResource(Resource):
    def post(self):
        try:
            data = note_access_schema.load(request.json)
        except ValidationError as err:
            return {"error": err.messages}, 400
        return note_access_schema.dump(data)['note'], 200


api.add_resource(NotesCreateResource, '/notes/create')
api.add_resource(NotesViewResource, '/notes')
