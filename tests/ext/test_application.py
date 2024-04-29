#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
"""The integration of persistence into the application is tested in test_basepersistence.
"""
import asyncio
import functools
import inspect
import logging
import os
import platform
import signal
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path
from queue import Queue
from random import randrange
from threading import Thread
from typing import Optional

import pytest

from telegram import Bot, Chat, Message, MessageEntity, User
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ApplicationHandlerStop,
    BaseHandler,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    Defaults,
    JobQueue,
    MessageHandler,
    PicklePersistence,
    SimpleUpdateProcessor,
    TypeHandler,
    Updater,
    filters,
)
from telegram.warnings import PTBDeprecationWarning, PTBUserWarning
from tests.auxil.asyncio_helpers import call_after
from tests.auxil.build_messages import make_message_update
from tests.auxil.files import PROJECT_ROOT_PATH
from tests.auxil.networking import send_webhook_message
from tests.auxil.pytest_classes import make_bot
from tests.auxil.slots import mro_slots


class CustomContext(CallbackContext):
    pass


class TestApplication:
    """The integration of persistence into the application is tested in
    test_basepersistence.
    """

    message_update = make_message_update(message="Text")
    received = None
    count = 0

    @pytest.fixture(autouse=True, name="reset")
    def _reset_fixture(self):
        self.reset()

    def reset(self):
        self.received = None
        self.count = 0

    async def error_handler_context(self, update, context):
        self.received = context.error.message

    async def error_handler_raise_error(self, update, context):
        raise Exception("Failing bigly")

    async def callback_increase_count(self, update, context):
        self.count += 1

    def callback_set_count(self, count, sleep: Optional[float] = None):
        async def callback(update, context):
            if sleep:
                await asyncio.sleep(sleep)
            self.count = count

        return callback

    def callback_raise_error(self, error_message: str):
        async def callback(update, context):
            raise TelegramError(error_message)

        return callback

    async def callback_received(self, update, context):
        self.received = update.message

    async def callback_context(self, update, context):
        if (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(context.update_queue, Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.error, TelegramError)
        ):
            self.received = context.error.message

    @pytest.mark.flaky(3, 1)  # loop.call_later will error the test when a flood error is received
    def test_signal_handlers(self, app, monkeypatch):
        # this test should make sure that signal handlers are set by default on Linux + Mac,
        # and not on Windows.

        received_signals = []

        def signal_handler_test(*args, **kwargs):
            # args[0] is the signal, [1] the callback
            received_signals.append(args[0])

        loop = asyncio.get_event_loop()
        monkeypatch.setattr(loop, "add_signal_handler", signal_handler_test)

        def abort_app():
            raise SystemExit

        loop.call_later(0.6, abort_app)

        app.run_polling(close_loop=False)

        if platform.system() == "Windows":
            assert received_signals == []
        else:
            assert received_signals == [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]

        received_signals.clear()
        loop.call_later(0.8, abort_app)
        app.run_webhook(port=49152, webhook_url="example.com", close_loop=False)

        if platform.system() == "Windows":
            assert received_signals == []
        else:
            assert received_signals == [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]

    def test_signal_handlers_no_flaky(self, app, monkeypatch):
        # this test should make sure that signal handlers are set by default on Linux + Mac,
        # and not on Windows.

        received_signals = []

        def signal_handler_test(*args, **kwargs):
            # args[0] is the signal, [1] the callback
            received_signals.append(args[0])

        loop = asyncio.get_event_loop()
        monkeypatch.setattr(loop, "add_signal_handler", signal_handler_test)

        def abort_app():
            raise SystemExit

        loop.call_later(0.6, abort_app)

        app.run_polling(close_loop=False)

        if platform.system() == "Windows":
            assert received_signals == []
        else:
            assert received_signals == [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]

        received_signals.clear()
        loop.call_later(0.8, abort_app)
        app.run_webhook(port=49152, webhook_url="example.com", close_loop=False)

        if platform.system() == "Windows":
            assert received_signals == []
        else:
            assert received_signals == [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]

