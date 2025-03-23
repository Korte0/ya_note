from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_anonymous_client_has_no_form(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.list_url)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        self.assertIn(self.note, response.context['object_list'])

    def test_create_and_add_note_has_form(self):
        urls = (
            (self.add_url),
            (self.edit_url)
        )
        for url in urls:
            self.client.force_login(self.author)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
