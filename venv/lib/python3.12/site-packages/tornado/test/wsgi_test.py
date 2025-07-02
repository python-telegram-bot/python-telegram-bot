from wsgiref.validate import validator

from tornado.testing import AsyncHTTPTestCase
from tornado.wsgi import WSGIContainer


class WSGIContainerTest(AsyncHTTPTestCase):
    # TODO: Now that WSGIAdapter is gone, this is a pretty weak test.
    def wsgi_app(self, environ, start_response):
        status = "200 OK"
        response_headers = [("Content-Type", "text/plain")]
        start_response(status, response_headers)
        return [b"Hello world!"]

    def get_app(self):
        return WSGIContainer(validator(self.wsgi_app))

    def test_simple(self):
        response = self.fetch("/")
        self.assertEqual(response.body, b"Hello world!")
