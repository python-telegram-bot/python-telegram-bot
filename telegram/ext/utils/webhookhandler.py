#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
# pylint: disable=C0114

import logging
from queue import Queue
from ssl import SSLContext
from threading import Event, Lock
from typing import TYPE_CHECKING, Any, Optional

import tornado.web
from tornado import httputil
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from telegram import Update
from telegram.ext import ExtBot
from telegram.utils.deprecate import set_new_attribute_deprecated
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot

try:
    import ujson as json
except ImportError:
    import json  # type: ignore[no-redef]


class WebhookServer:
    __slots__ = (
        'http_server',
        'listen',
        'port',
        'loop',
        'logger',
        'is_running',
        'server_lock',
        'shutdown_lock',
        '__dict__',
    )

    def __init__(
        self, listen: str, port: int, webhook_app: 'WebhookAppClass', ssl_ctx: SSLContext
    ):
        self.http_server = HTTPServer(webhook_app, ssl_options=ssl_ctx)
        self.listen = listen
        self.port = port
        self.loop: Optional[IOLoop] = None
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.server_lock = Lock()
        self.shutdown_lock = Lock()

    def __setattr__(self, key: str, value: object) -> None:
        set_new_attribute_deprecated(self, key, value)

    def serve_forever(self, ready: Event = None) -> None:
        with self.server_lock:
            IOLoop().make_current()
            self.is_running = True
            self.logger.debug('Webhook Server started.')
            self.loop = IOLoop.current()
            self.http_server.listen(self.port, address=self.listen)

            if ready is not None:
                ready.set()

            self.loop.start()
            self.logger.debug('Webhook Server stopped.')
            self.is_running = False

    def shutdown(self) -> None:
        with self.shutdown_lock:
            if not self.is_running:
                self.logger.warning('Webhook Server already stopped.')
                return
            self.loop.add_callback(self.loop.stop)  # type: ignore

    def handle_error(self, request: object, client_address: str) -> None:  # pylint: disable=W0613
        """Handle an error gracefully."""
        self.logger.debug(
            'Exception happened during processing of request from %s',
            client_address,
            exc_info=True,
        )


class WebhookAppClass(tornado.web.Application):
    def __init__(self, webhook_path: str, bot: 'Bot', update_queue: Queue):
        self.shared_objects = {"bot": bot, "update_queue": update_queue}
        handlers = [(rf"{webhook_path}/?", WebhookHandler, self.shared_objects)]  # noqa
        tornado.web.Application.__init__(self, handlers)  # type: ignore

    def log_request(self, handler: tornado.web.RequestHandler) -> None:  # skipcq: PTC-W0049
        pass


# WebhookHandler, process webhook calls
# pylint: disable=W0223
class WebhookHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ["POST"]  # type: ignore

    def __init__(
        self,
        application: tornado.web.Application,
        request: httputil.HTTPServerRequest,
        **kwargs: JSONDict,
    ):
        super().__init__(application, request, **kwargs)
        self.logger = logging.getLogger(__name__)

    def initialize(self, bot: 'Bot', update_queue: Queue) -> None:
        # pylint: disable=W0201
        self.bot = bot
        self.update_queue = update_queue

    def set_default_headers(self) -> None:
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def post(self) -> None:
        self.logger.debug('Webhook triggered')
        self._validate_post()
        json_string = self.request.body.decode()
        data = json.loads(json_string)
        self.set_status(200)
        self.logger.debug('Webhook received data: %s', json_string)
        update = Update.de_json(data, self.bot)
        if update:
            self.logger.debug('Received Update with ID %d on Webhook', update.update_id)
            # handle arbitrary callback data, if necessary
            if isinstance(self.bot, ExtBot):
                self.bot.insert_callback_data(update)
            self.update_queue.put(update)

    def _validate_post(self) -> None:
        ct_header = self.request.headers.get("Content-Type", None)
        if ct_header != 'application/json':
            raise tornado.web.HTTPError(403)

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        """Log an arbitrary message.

        This is used by all other logging functions.

        It overrides ``BaseHTTPRequestHandler.log_message``, which logs to ``sys.stderr``.

        The first argument, FORMAT, is a format string for the message to be logged.  If the format
        string contains any % escapes requiring parameters, they should be specified as subsequent
        arguments (it's just like printf!).

        The client ip is prefixed to every message.

        """
        super().write_error(status_code, **kwargs)
        self.logger.debug(
            "%s - - %s",
            self.request.remote_ip,
            "Exception in WebhookHandler",
            exc_info=kwargs['exc_info'],
        )
