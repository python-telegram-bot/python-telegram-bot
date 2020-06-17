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
import copy
from flaky import flaky
from functools import partial
from queue import Queue
from random import randrange
from threading import Thread, Event
from time import sleep

try:
    # python2
    from urllib2 import urlopen, Request, HTTPError
except ImportError:
    # python3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

import pytest
from future.builtins import bytes

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


class TestUpdater(object):
    message_count = 0
    received = None
    attempts = 0
    err_handler_called = Event()
    cb_handler_called = Event()
    update_id = 0

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

    # TODO: test clean= argument, both bool and timedelta, of Updater._bootstrap











    @pytest.mark.parametrize(('error',),
                             argvalues=[(TelegramError(''),)],
                             ids=('TelegramError',))
    def test_bootstrap_retries_success(self, monkeypatch, updater, error):
        retries = 2

        def attempt(*args, **kwargs):
            if self.attempts < retries:
                self.attempts += 1
                raise error

        monkeypatch.setattr(updater.bot, 'set_webhook', attempt)

        updater.running = True
        updater._bootstrap(retries, False, 'path', None, bootstrap_interval=0)
        assert self.attempts == retries

    @pytest.mark.parametrize(('error', 'attempts'),
                             argvalues=[(TelegramError(''), 2),
                                        (Unauthorized(''), 1),
                                        (InvalidToken(), 1)],
                             ids=('TelegramError', 'Unauthorized', 'InvalidToken'))
    def test_bootstrap_retries_error(self, monkeypatch, updater, error, attempts):
        retries = 1

        def attempt(*args, **kwargs):
            self.attempts += 1
            raise error

        monkeypatch.setattr(updater.bot, 'set_webhook', attempt)

        updater.running = True
        with pytest.raises(type(error)):
            updater._bootstrap(retries, False, 'path', None, bootstrap_interval=0)
        assert self.attempts == attempts

    @pytest.mark.parametrize(('error', ),
                             argvalues=[(TelegramError(''),)],
                             ids=('TelegramError', ))
    def test_bootstrap_clean_bool(self, monkeypatch, updater, error):
        clean = True
        expected_id = 4 # max 9

        def updates(uid, *args, **kwargs):
            # we're hitting this func twice
            # 1. no args, return list of updates
            # 2. with arg, int = 4, expecting list args, delete all updates with updated_id < int

            # case ???
            if uid:
                print('uid: "%s"', uid)
                raise error

            # case ???
            if self.update_id>10:
                raise error

            # case 2
            if len(args) > 0:
                # we expect to get int(4)
                self.update_id = int(args[0])
                raise error
                
            if len(args) > 0:
                self.update_id+=1
                print(args[0])
                
            class fakeUpdate(object):
                pass

            # case 1
            # return list of dict's
            i=1
            ls = []
            while i < (expected_id):
                o = fakeUpdate()
                o.update_id = i
                ls.append(copy.deepcopy(o))
                i+=1
            return ls

        def updates(*args, **kwargs):
            # we're hitting this func twice
            # 1. no args, return list of updates
            # 2. with arg, int = 4, expecting list args, delete all updates with updated_id < int

            # case ???
            if self.update_id>10:
                raise error

            # case 2
            if len(args) > 0:
                # we expect to get int(4)
                print ("in here")
                self.update_id = int(args[0])
                raise error
                
            if len(args) > 0:
                self.update_id+=1
                print(args[0])
                
            class fakeUpdate(object):
                pass

            # case 1
            # return list of dict's
            i=1
            ls = []
            while i < (expected_id):
                o = fakeUpdate()
                o.update_id = i
                ls.append(copy.deepcopy(o))
                i+=1
            return ls

        monkeypatch.setattr(updater.bot, 'get_updates', updates)

        updater.running = True
        with pytest.raises(type(error)):
            updater._bootstrap(1, clean, None, None, bootstrap_interval=0)
        assert self.update_id == expected_id+1

