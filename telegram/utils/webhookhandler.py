import logging

from telegram import Update, NullHandler
from future.utils import bytes_to_native_str as n
from threading import Lock
import json
try:
    import BaseHTTPServer
except ImportError:
    import http.server as BaseHTTPServer


H = NullHandler()
logging.getLogger(__name__).addHandler(H)


class WebhookServer(BaseHTTPServer.HTTPServer, object):
    def __init__(self, server_address, RequestHandlerClass, update_queue,
                 webhook_path):
        super(WebhookServer, self).__init__(server_address,
                                            RequestHandlerClass)
        self.logger = logging.getLogger(__name__)
        self.update_queue = update_queue
        self.webhook_path = webhook_path
        self.is_running = False
        self.server_lock = Lock()
        self.shutdown_lock = Lock()

    def serve_forever(self, poll_interval=0.5):
        with self.server_lock:
            self.is_running = True
            self.logger.info("Webhook Server started.")
            super(WebhookServer, self).serve_forever(poll_interval)
            self.logger.info("Webhook Server stopped.")

    def shutdown(self):
        with self.shutdown_lock:
            if not self.is_running:
                return
            else:
                super(WebhookServer, self).shutdown()
                self.is_running = False


# WebhookHandler, process webhook calls
# Based on: https://github.com/eternnoir/pyTelegramBotAPI/blob/master/
# examples/webhook_examples/webhook_cpython_echo_bot.py
class WebhookHandler(BaseHTTPServer.BaseHTTPRequestHandler,    object):
    server_version = "WebhookHandler/1.0"

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
        self.logger.debug("Webhook triggered")
        if self.path == self.server.webhook_path and \
           'content-type' in self.headers and \
           'content-length' in self.headers and \
           self.headers['content-type'] == 'application/json':
            json_string = \
                n(self.rfile.read(int(self.headers['content-length'])))

            self.send_response(200)
            self.end_headers()

            self.logger.debug("Webhook received data: " + json_string)

            update = Update.de_json(json.loads(json_string))
            self.logger.info("Received Update with ID %d on Webhook" %
                             update.update_id)
            self.server.update_queue.put(update)

        else:
            self.send_error(403)
            self.end_headers()
