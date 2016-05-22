import logging

from telegram import Update, NullHandler
from future.utils import bytes_to_native_str
from threading import Lock
import json
try:
    import BaseHTTPServer
except ImportError:
    import http.server as BaseHTTPServer

logging.getLogger(__name__).addHandler(NullHandler())


class _InvalidPost(Exception):

    def __init__(self, http_code):
        self.http_code = http_code
        super(_InvalidPost, self).__init__()


class WebhookServer(BaseHTTPServer.HTTPServer, object):

    def __init__(self, server_address, RequestHandlerClass, update_queue, webhook_path):
        super(WebhookServer, self).__init__(server_address, RequestHandlerClass)
        self.logger = logging.getLogger(__name__)
        self.update_queue = update_queue
        self.webhook_path = webhook_path
        self.is_running = False
        self.server_lock = Lock()
        self.shutdown_lock = Lock()

    def serve_forever(self, poll_interval=0.5):
        with self.server_lock:
            self.is_running = True
            self.logger.debug('Webhook Server started.')
            super(WebhookServer, self).serve_forever(poll_interval)
            self.logger.debug('Webhook Server stopped.')

    def shutdown(self):
        with self.shutdown_lock:
            if not self.is_running:
                self.logger.warn('Webhook Server already stopped.')
                return
            else:
                super(WebhookServer, self).shutdown()
                self.is_running = False


# WebhookHandler, process webhook calls
# Based on: https://github.com/eternnoir/pyTelegramBotAPI/blob/master/
# examples/webhook_examples/webhook_cpython_echo_bot.py
class WebhookHandler(BaseHTTPServer.BaseHTTPRequestHandler, object):
    server_version = 'WebhookHandler/1.0'

    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger(__name__)
        super(WebhookHandler, self).__init__(request, client_address, server)

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        self.logger.debug('Webhook triggered')
        try:
            self._validate_post()
            clen = self._get_content_len()
        except _InvalidPost as e:
            self.send_error(e.http_code)
            self.end_headers()
        else:
            buf = self.rfile.read(clen)
            json_string = bytes_to_native_str(buf)

            self.send_response(200)
            self.end_headers()

            self.logger.debug('Webhook received data: ' + json_string)

            update = Update.de_json(json.loads(json_string))
            self.logger.debug('Received Update with ID %d on Webhook' % update.update_id)
            self.server.update_queue.put(update)

    def _validate_post(self):
        if not (self.path == self.server.webhook_path and 'content-type' in self.headers and
                self.headers['content-type'] == 'application/json'):
            raise _InvalidPost(403)

    def _get_content_len(self):
        clen = self.headers.get('content-length')
        if clen is None:
            raise _InvalidPost(411)
        try:
            clen = int(clen)
        except ValueError:
            raise _InvalidPost(403)
        if clen < 0:
            raise _InvalidPost(403)
        return clen
