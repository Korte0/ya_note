from http import HTTPStatus

from pytils.translit import slugify

from .core import NOTE_TEXT, NOTE_TITLE, SLUG, URL, SetUpTestLogic, SetUpTest
from notes.forms import WARNING
from notes.models import Note


class TestNoteCreation(SetUpTestLogic):
    def test_anonymous_user_cant_create_note(self):
        self.client.post(URL.add, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_counts)

    def test_user_can_create_note(self):
        Note.objects.filter().delete()
        response = self.author_client.post(URL.add, data=self.form_data)
        self.assertRedirects(response, URL.success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_counts)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_user_cant_use_slug_warning(self):
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(URL.add, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.notes_counts)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=self.note.slug + WARNING
        )

    def test_empty_slug(self):
        Note.objects.filter().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(URL.add, data=self.form_data)
        self.assertRedirects(response, URL.success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.notes_counts)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(SetUpTest):
    def test_author_can_delete_note(self):
        expected_count = Note.objects.count() - 1
        response = self.auth_client.delete(URL.delete)
        self.assertRedirects(response, URL.success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, expected_count)

    def test_user_cant_delete_note_of_another_user(self):
        expected_count = Note.objects.count()
        response = self.reader_client.delete(URL.delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, expected_count)

    def test_author_can_edit_note(self):
        response = self.auth_client.post(URL.edit, data=self.form_data)
        self.assertRedirects(response, URL.success)
        self.note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(URL.edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, NOTE_TEXT)
        self.assertEqual(self.note.title, NOTE_TITLE)
        self.assertEqual(self.note.slug, SLUG)
        self.assertEqual(self.note.author, self.author)
