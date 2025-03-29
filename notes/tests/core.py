from collections import namedtuple

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

SLUG = 'note-slug'
NOTE_TEXT = 'Текст'
NOTE_TITLE = 'Заголовок'
NEW_NOTE_TEXT = 'Новый текст записи'
NEW_NOTE_TITLE = 'Новый заголовок записи'
NEW_NOTE_SLUG = 'new_slug'

URL_NAME = namedtuple(
    'URL_NAME',
    [
        'home',
        'add',
        'list',
        'detail',
        'edit',
        'delete',
        'success',
        'login',
        'logout',
        'signup',
    ],
)

URL = URL_NAME(
    reverse('notes:home'),
    reverse('notes:add'),
    reverse('notes:list'),
    reverse('notes:detail', args=(SLUG,)),
    reverse('notes:edit', args=(SLUG,)),
    reverse('notes:delete', args=(SLUG,)),
    reverse('notes:success'),
    reverse('users:login'),
    reverse('users:logout'),
    reverse('users:signup'),
)


class SetUpTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.client = Client()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=SLUG,
            author=cls.author,
        )
        cls.form_data = {
            'text': NEW_NOTE_TEXT,
            'title': NEW_NOTE_TITLE,
            'slug': NEW_NOTE_SLUG,
            'author': cls.auth_client
        }


class SetUpTestLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = {
            'title': NOTE_TITLE,
            'text': NOTE_TEXT,
            'slug': SLUG,
            'author': cls.author_client
        }
        cls.note = Note.objects.create(
            title='Заголовок',
            slug='Slug',
            author=cls.author,
            text=NOTE_TEXT
        )
        cls.notes_counts = Note.objects.count()
