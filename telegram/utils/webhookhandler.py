#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
import asyncio
import os
import sys
import logging
from telegram import Update
from threading import Lock, Event

try:
    import ujson as json
except ImportError:
    import json  # type: ignore[no-redef]
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import tornado.web

from ssl import SSLContext
from queue import Queue
from telegram.utils.types import JSONDict
from typing import Any, TYPE_CHECKING
from tornado import httputil
if TYPE_CHECKING:
    from telegram import Bot


class WebhookServer:

    def __init__(self,
                 listen: str,
                 port: int,
                 webhook_app: 'WebhookAppClass',
                 ssl_ctx: SSLContext):
        self.http_server = HTTPServer(webhook_app, ssl_options=ssl_ctx)
        self.listen = listen
        self.port = port
        self.loop = None
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.server_lock = Lock()
        self.shutdown_lock = Lock()

    def serve_forever(self, force_event_loop: bool = False, ready: Event = None) -> None:
        with self.server_lock:
            self.is_running = True
            self.logger.debug('Webhook Server started.')
            self._ensure_event_loop(force_event_loop=force_event_loop)
            self.loop = IOLoop.current()
            self.http_server.listen(self.port, address=self.listen)

            if ready is not None:
                ready.set()

            self.loop.start()  # type: ignore
            self.logger.debug('Webhook Server stopped.')
            self.is_running = False

    def shutdown(self) -> None:
        with self.shutdown_lock:
            if not self.is_running:
                self.logger.warning('Webhook Server already stopped.')
                return
            else:
                self.loop.add_callback(self.loop.stop)  # type: ignore

    def handle_error(self, request: Any, client_address: str) -> None:
        """Handle an error gracefully."""
        self.logger.debug('Exception happened during processing of request from %s',
                          client_address, exc_info=True)

    def _ensure_event_loop(self, force_event_loop: bool = False) -> None:
        """If there's no asyncio event loop set for the current thread - create one."""
        try:
            loop = asyncio.get_event_loop()
            if (not force_event_loop and os.name == 'nt' and sys.version_info >= (3, 8)
                    and isinstance(loop, asyncio.ProactorEventLoop)):
                raise TypeError('`ProactorEventLoop` is incompatible with '
                                'Tornado. Please switch to `SelectorEventLoop`.')
        except RuntimeError:
            # Python 3.8 changed default asyncio event loop implementation on windows
            # from SelectorEventLoop to ProactorEventLoop. At the time of this writing
            # Tornado doesn't support ProactorEventLoop and suggests that end users
            # change asyncio event loop policy to WindowsSelectorEventLoopPolicy.
            # https://github.com/tornadoweb/tornado/issues/2608
            # To avoid changing the global event loop policy, we manually construct
            # a SelectorEventLoop instance instead of using asyncio.new_event_loop().
            # Note that the fix is not applied in the main thread, as that can break
            # user code in even more ways than changing the global event loop policy can,
            # and because Updater always starts its webhook server in a separate thread.
            # Ideally, we would want to check that Tornado actually raises the expected
            # NotImplementedError, but it's not possible to cleanly recover from that
            # exception in current Tornado version.
            if (os.name == 'nt'
                    and sys.version_info >= (3, 8)
                    # OS+version check makes hasattr check redundant, but just to be sure
                    and hasattr(asyncio, 'WindowsProactorEventLoopPolicy')
                    and (isinstance(
                         asyncio.get_event_loop_policy(),
                         asyncio.WindowsProactorEventLoopPolicy))):  # pylint: disable=E1101
                self.logger.debug(
                    'Applying Tornado asyncio event loop fix for Python 3.8+ on Windows')
                loop = asyncio.SelectorEventLoop()
            else:
                loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)


class WebhookAppClass(tornado.web.Application):

    def __init__(self,
                 webhook_path: str,
                 bot: 'Bot',
                 update_queue: Queue):
        self.shared_objects = {"bot": bot, "update_queue": update_queue}
        handlers = [
            (r"{}/?".format(webhook_path), WebhookHandler,
             self.shared_objects)
        ]  # noqa
        tornado.web.Application.__init__(self, handlers)

    def log_request(self, handler: tornado.web.RequestHandler) -> None:
        pass


# WebhookHandler, process webhook calls
class WebhookHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ["POST"]

    def __init__(self,
                 application: tornado.web.Application,
                 request: httputil.HTTPServerRequest,
                 **kwargs: JSONDict):
        super().__init__(application, request, **kwargs)
        self.logger = logging.getLogger(__name__)

    def initialize(self, bot: 'Bot', update_queue: Queue) -> None:
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
        self.logger.debug('Webhook received data: ' + json_string)
        update = Update.de_json(data, self.bot)
        if update:
            self.logger.debug('Received Update with ID %d on Webhook' % update.update_id)
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
        self.logger.debug("{} - - {}".format(self.request.remote_ip,
                                             "Exception in WebhookHandler"),
                          exc_info=kwargs['exc_info'])
