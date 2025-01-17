from marshmallow import (Schema, ValidationError, fields, post_load,
                         validates_schema)

from burnote.models import Note
from burnote.models.errors import DecryptionError


class NoteSchema(Schema):
    """
    Handles serialization and deserialization of Note data.
    """
    title = fields.Str(required=False, load_default='')
    text = fields.Str(required=True)
    expiration = fields.TimeDelta(required=False, allow_none=True,
                                  precision='minutes', load_default=None,
                                  load_only=True)
    timestamp = fields.DateTime(dump_only=True)
    expiration_date = fields.DateTime(dump_only=True)
    burn_after_reading = fields.Bool(required=False, load_default=False)
    password = fields.Str(required=False, load_default='', load_only=True)
    key = fields.Str(dump_only=True)

    @post_load
    def create_note(self, data, **kwargs):
        """
        Create and save a new Note from the provided data.

        :param data: Deserialized note data
        :return: The same data with an added 'key' field
        """
        _, key = Note.create(data, save=True)
        data['key'] = key
        return data


class NoteAccessSchema(Schema):
    """
    Facilitates accessing and decrypting an existing Note
    via provided key/password.
    """
    key = fields.Str(required=True)
    password = fields.Str(required=False, load_default='')
    note = fields.Nested(NoteSchema, dump_only=True)

    class Meta:
        load_only = ('key', 'password')

    @validates_schema
    def validate_schema(self, data, **kwargs):
        """
        Validate the provided key and password,
        ensuring the note is available and decryptable.

        :param data: Deserialized schema data containing key/password
        :raises ValidationError: If key is invalid, note is expired,
                                 or decryption fails
        """
        key = data.get('key')
        password = data.get('password', '')

        note = Note.get_by_key(key, silent=True)
        if not note:
            raise ValidationError({'key': 'Invalid key.'})

        if not note.is_available():
            raise ValidationError({'note': 'Note has been expired and deleted'}
                                  )

        try:
            note.decrypt(key, password)
        except DecryptionError:
            raise ValidationError({'password': 'Invalid password.'})

        self.context['note'] = note

    @post_load
    def add_note_to_output(self, data, **kwargs):
        """
        Add the decrypted note instance to the output if validation succeeds.

        :param data: Schema data after validation
        :return: Data updated with 'note' field
        """
        if 'note' not in self.context:
            raise ValidationError({'note': 'Failed to decrypt note.'})

        data['note'] = self.context['note']
        return data
