from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст записи'
    NOTE_TITLE = 'Заголовок записи'
    NOTE_SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок',
            slug='Slug',
            author=cls.author,
            text=cls.NOTE_TEXT
        )
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': cls.NOTE_TITLE,
            'slug': cls.NOTE_SLUG,
            'author': cls.auth_client
        }
        cls.notes_counts = Note.objects.count()

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url_add, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_counts)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_counts + 1)
        note = Note.objects.last()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_user_cant_use_slug_warning(self):
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(self.url_add, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=self.note.slug + WARNING
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.notes_counts)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.notes_counts + 1)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст записи'
    NEW_NOTE_TEXT = 'Новый текст записи'
    NOTE_TITLE = 'Заголовок записи'
    NEW_NOTE_TITLE = 'Новый заголовок записи'
    NOTE_SLUG = 'slug'
    NEW_NOTE_SLUG = 'new_slug'

    @classmethod
    def setUpTestData(cls):
        cls.url_success = reverse('notes:success')
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            slug='Slug',
            author=cls.author,
            text=cls.NOTE_TEXT
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NEW_NOTE_TITLE,
            'slug': cls.NEW_NOTE_SLUG,
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
