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
import logging
import os
import signal
import sys
import asyncio
from flaky import flaky
from functools import partial
from queue import Queue
from random import randrange
from threading import Thread, Event
from time import sleep

from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest

from telegram import TelegramError, Message, User, Chat, Update, Bot
from telegram.error import Unauthorized, InvalidToken, TimedOut, RetryAfter
from telegram.ext import Updater, Dispatcher, DictPersistence

signalskip = pytest.mark.skipif(sys.platform == 'win32',
                                reason='Can\'t send signals without stopping '
                                       'whole process on windows')


if sys.platform.startswith("win") and sys.version_info >= (3, 8):
    """set default asyncio policy to be compatible with tornado
    Tornado 6 (at least) is not compatible with the default
    asyncio implementation on Windows
    Pick the older SelectorEventLoopPolicy on Windows
    if the known-incompatible default policy is in use.
    do this as early as possible to make it a low priority and overrideable
    ref: https://github.com/tornadoweb/tornado/issues/2608
    TODO: if/when tornado supports the defaults in asyncio,
            remove and bump tornado requirement for py38
    Copied from https://github.com/ipython/ipykernel/pull/456/
    """
    try:
        from asyncio import (
            WindowsProactorEventLoopPolicy,
            WindowsSelectorEventLoopPolicy,
        )
    except ImportError:
        pass
        # not affected
    else:
        if type(asyncio.get_event_loop_policy()) is WindowsProactorEventLoopPolicy:
            # WindowsProactorEventLoopPolicy is not compatible with tornado 6
            # fallback to the pre-3.8 default of Selector
            asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


class TestUpdater:
    message_count = 0
    received = None
    attempts = 0
    err_handler_called = Event()
    cb_handler_called = Event()
    updates = []

    @pytest.fixture(autouse=True)
    def reset(self):
        self.message_count = 0
        self.received = None
        self.attempts = 0
        self.err_handler_called.clear()
        self.cb_handler_called.clear()

    def error_handler(self, bot, update, error):
        self.received = error.message
        self.err_handler_called.set()

    def callback(self, bot, update):
        self.received = update.message.text
        self.cb_handler_called.set()

    def test_bootstrap_clean_updates(self, monkeypatch, updater):
        clean = True
        expected_id = 4

        def get_updates(*args, **kwargs):
            # we're hitting this func twice
            # 1. no args, return list of updates
            # 2. with 1 arg, int => if int == expected_id => test successful
            class FakeUpdate():
                def __init__(self, update_id):
                    self.update_id = update_id

            # case 2
            # 2nd call from bootstrap____clean
            # we should be called with offset = 4
            # save value passed in self.offset for assert down below
            if len(args) > 0:
                return [self.updates[i] for i in range(args[0], expected_id)]

            # case 1
            # return list of obj's

            # build list of fake updates
            # returns list of 3 objects with
            # update_id's 1, 2 and 3
            print ('bla')
            self.updates = [FakeUpdate(i) for i in range(1, expected_id)]
            return self.updates

        monkeypatch.setattr(updater.bot, 'get_updates', get_updates)

        updater.running = True
        updater._bootstrap(1, clean, None, None, bootstrap_interval=0)
        assert updater.bot.get_updates() == []

