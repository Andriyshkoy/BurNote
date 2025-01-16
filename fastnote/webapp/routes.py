from flask import flash, render_template

from . import bp
from .forms import NoteAccessForm, NoteForm
from fastnote.models.note import Note


@bp.route('/', methods=['GET', 'POST'])
def create():
    form = NoteForm()

    if form.validate_on_submit():
        note, key = Note.create(form.data)
        note.save()
        flash('Note created successfully', 'success')
        return render_template('notes/success.html', link=note.get_link(key))

    return render_template('notes/create.html', form=form)


@bp.route('/about')
def about():
    return render_template('pages/about.html')


@bp.route('/<key>', methods=['GET', 'POST'])
def note_view(key):
    note = Note.get_by_key(key)

    if not note.is_available():
        flash('This note has expired and has been deleted.', 'danger')
        return render_template('notes/expired.html')

    form = NoteAccessForm()
    if form.validate_on_submit():
        try:
            note.decrypt(key, form.password.data)
        except UnicodeDecodeError:
            flash('Invalid password', 'danger')
            return render_template('notes/password_protected.html', form=form)

        if note.burn_after_reading:
            flash('This note was only available once. It has been deleted. '
                  'Make sure to remember the content.', 'warning')
            note.expire()

        return render_template('notes/view.html', note=note)

    try:
        note.decrypt(key, '')
    except UnicodeDecodeError:
        return render_template('notes/password_protected.html', form=form)

    if note.burn_after_reading:
        flash('This note was only available once. It has been deleted. '
              'Make sure to remember the content.', 'warning')
        note.expire()

    return render_template('notes/view.html', note=note)
