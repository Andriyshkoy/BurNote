from datetime import timedelta

from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, SelectField,
                     BooleanField, PasswordField)
from wtforms.validators import DataRequired, Optional, Length

choises = (
    ('', 'Never'),
    ('1 0 0', '1 minute'),
    ('10 0 0', '10 minutes'),
    ('0 1 0', '1 hour'),
    ('0 0 1', '1 day'),
    ('0 0 7', '1 week'),
    ('0 0 14', '2 weeks'),
    ('0 0 30', '1 month'),
    ('0 0 90', '3 months'),
    ('0 0 180', '6 months'),
    ('0 0 365', '1 year'),
)


def parse_timedelta(timedelta_str):
    if not timedelta_str:
        return None
    minutes, hours, days = map(int, timedelta_str.split())
    return timedelta(days=days, hours=hours, minutes=minutes)


class NoteForm(FlaskForm):
    title = StringField('Title', validators=[Optional(), Length(max=32)])
    text = TextAreaField('Body', validators=[DataRequired()])
    expiration = SelectField('Expiration', choices=choises,
                             coerce=parse_timedelta)
    burn_after_reading = BooleanField('Burn after reading')
    password = PasswordField('Password', validators=[Optional()])
    submit = SubmitField('Submit')


class NoteAccessForm(FlaskForm):
    password = PasswordField('Password', validators=[Optional()])
    submit = SubmitField('Submit')
