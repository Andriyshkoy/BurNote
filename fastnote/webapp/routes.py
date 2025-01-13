from flask import flash, render_template

from . import bp
from .forms import BurnForm, NoteForm
from fastnote.models.note import Note


@bp.route('/', methods=['GET', 'POST'])
def create():
    form = NoteForm()

    if form.validate_on_submit():
        note = Note.from_dict(form.data)
        note.save()
        flash('Note created successfully', 'success')
        return render_template('notes/success.html', link=note.get_link())

    return render_template('notes/create.html', form=form)


@bp.route('/about')
def about():
    return render_template('pages/about.html')


@bp.route('/<hash>', methods=['GET', 'POST'])
def note(hash):
    note = Note.get_by_hash(hash)

    if not note.is_available():
        flash('This note has expired and has been deleted.', 'danger')
        return render_template('notes/expired.html')

    if note.burn_after_reading:
        form = BurnForm()
        if form.validate_on_submit():
            note.expire()
            return render_template('notes/view.html', note=note)

        flash('This note will be deleted after reading. '
              'Make sure to remember the content.', 'warning')
        return render_template('notes/warning.html', form=form)

    return render_template('notes/view.html', note=note)
