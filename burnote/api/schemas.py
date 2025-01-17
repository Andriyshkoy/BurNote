from marshmallow import (Schema, fields, ValidationError,
                         validates_schema, post_load)

from burnote.models import Note
from burnote.models.errors import DecryptionError


class NoteSchema(Schema):
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
        _, key = Note.create(data, save=True)
        data['key'] = key
        return data


class NoteAccessSchema(Schema):
    key = fields.Str(required=True)
    password = fields.Str(required=False, load_default='')
    note = fields.Nested(NoteSchema, dump_only=True)

    class Meta:
        load_only = ('key', 'password')

    @validates_schema
    def validate_schema(self, data, **kwargs):
        """Комплексная проверка пароля и ключа."""
        key = data.get('key')
        password = data.get('password', '')

        note = Note.get_by_key(key, silent=True)
        if not note:
            raise ValidationError({'key': 'Invalid key.'})

        if not note.is_available():
            raise ValidationError({'note': 'Note has been expired and deleted'})

        try:
            note.decrypt(key, password)
        except DecryptionError:
            raise ValidationError({'password': 'Invalid password.'})

        self.context['note'] = note

    @post_load
    def add_note_to_output(self, data, **kwargs):
        """Добавляем расшифрованный объект note в выходные данные."""
        if 'note' not in self.context:
            raise ValidationError({'note': 'Failed to decrypt note.'})

        # Добавляем объект note в выходные данные
        data['note'] = self.context['note']
        return data
