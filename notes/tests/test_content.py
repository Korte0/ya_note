from .core import URL, SetUpTest
from notes.forms import NoteForm


class TestContent(SetUpTest):
    def test_anonymous_client_has_no_form(self):
        response = self.reader_client.get(URL.list)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_authorized_client_has_form(self):
        response = self.auth_client.get(URL.list)
        self.assertIn(self.note, response.context['object_list'])

    def test_create_and_add_note_has_form(self):
        urls = (
            (URL.add),
            (URL.edit),
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertIsInstance(
                    self.auth_client.get(url).context['form'], NoteForm,
                    msg=(
                        f'Проверьте, что форма редактирования передается на '
                        f'страницу {url}.'
                    ),
                )
