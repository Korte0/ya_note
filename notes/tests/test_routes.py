from http import HTTPStatus

from .core import URL, SetUpTest


class TestRoutes(SetUpTest):
    def test_pages_availability(self):
        urls = [
            (self.author, URL.home, HTTPStatus.OK),
            (self.reader, URL.home, HTTPStatus.OK),
            (self.author, URL.login, HTTPStatus.OK),
            (self.reader, URL.login, HTTPStatus.OK),
            (self.author, URL.logout, HTTPStatus.OK),
            (self.reader, URL.logout, HTTPStatus.OK),
            (self.author, URL.signup, HTTPStatus.OK),
            (self.reader, URL.signup, HTTPStatus.OK),
            (self.author, URL.add, HTTPStatus.OK),
            (self.author, URL.success, HTTPStatus.OK),
            (self.author, URL.detail, HTTPStatus.OK),
            (self.reader, URL.detail, HTTPStatus.NOT_FOUND),
            (self.author, URL.edit, HTTPStatus.OK),
            (self.reader, URL.edit, HTTPStatus.NOT_FOUND),
            (self.author, URL.delete, HTTPStatus.OK),
            (self.reader, URL.delete, HTTPStatus.NOT_FOUND),
        ]
        for user, url, expected_status in urls:
            with self.subTest(user=user, url=url):
                self.client.force_login(user)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            URL.list,
            URL.add,
            URL.success,
            URL.detail,
            URL.edit,
            URL.delete,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{URL.login}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
