#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import logging

from telegram import Update
from future.utils import bytes_to_native_str
from threading import Lock
try:
    import ujson as json
except ImportError:
    import json
try:
    import BaseHTTPServer
except ImportError:
    import http.server as BaseHTTPServer

logging.getLogger(__name__).addHandler(logging.NullHandler())


class _InvalidPost(Exception):

    def __init__(self, http_code):
        self.http_code = http_code
        super(_InvalidPost, self).__init__()


class WebhookServer(BaseHTTPServer.HTTPServer, object):

    def __init__(self, server_address, RequestHandlerClass, update_queue, webhook_path, bot):
        super(WebhookServer, self).__init__(server_address, RequestHandlerClass)
        self.logger = logging.getLogger(__name__)
        self.update_queue = update_queue
        self.webhook_path = webhook_path
        self.bot = bot
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
                self.logger.warning('Webhook Server already stopped.')
                return
            else:
                super(WebhookServer, self).shutdown()
                self.is_running = False

    def handle_error(self, request, client_address):
        """Handle an error gracefully."""
        self.logger.debug('Exception happened during processing of request from %s',
                          client_address, exc_info=True)


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

            update = Update.de_json(json.loads(json_string), self.server.bot)

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

    def log_message(self, format, *args):
        """Log an arbitrary message.

        This is used by all other logging functions.

        It overrides ``BaseHTTPRequestHandler.log_message``, which logs to ``sys.stderr``.

        The first argument, FORMAT, is a format string for the message to be logged.  If the format
        string contains any % escapes requiring parameters, they should be specified as subsequent
        arguments (it's just like printf!).

        The client ip is prefixed to every message.

        """
        self.logger.debug("%s - - %s" % (self.address_string(), format % args))
