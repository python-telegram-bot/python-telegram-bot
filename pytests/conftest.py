#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import logging
import os
import sys
from collections import defaultdict
from queue import Queue
from threading import Thread, Event
from time import sleep

import pytest

from pytests.bots import get_bot
from telegram import Bot
from telegram.ext import Dispatcher, JobQueue

TRAVIS = os.getenv('TRAVIS', False)

if TRAVIS:
    pytest_plugins = ['pytests.travis_fold']

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope='session')
def bot_info():
    return get_bot()


@pytest.fixture(scope='session')
def bot(bot_info):
    return Bot(bot_info['token'])


@pytest.fixture(scope='session')
def chat_id(bot_info):
    return bot_info['chat_id']


@pytest.fixture(scope='session')
def group_id(bot_info):
    return bot_info['group_id']


@pytest.fixture(scope='session')
def channel_id(bot_info):
    return bot_info['channel_id']


@pytest.fixture(scope='session')
def provider_token(bot_info):
    return bot_info['payment_provider_token']


def create_dp(bot):
    print('create before before')
    # Dispatcher is heavy to init (due to many threads and such) so we have a single session
    # scoped one here, but before each test, reset it (dp fixture below)
    dispatcher = Dispatcher(bot, Queue(), job_queue=JobQueue(bot), workers=2)
    thr = Thread(target=dispatcher.start)
    thr.start()
    sleep(2)
    print('create before after')
    yield dispatcher
    print('create after before')
    sleep(1)
    print(dispatcher.__dict__)
    print(dispatcher._Dispatcher__stop_event.is_set())
    if dispatcher.running:
        dispatcher.stop()
    print(dispatcher._Dispatcher__stop_event.is_set())
    thr.join()
    print('create after after')


@pytest.fixture(scope='session')
def _dp(bot):
    print('_dp before')
    for dp in create_dp(bot):
        print('_dp in before')
        yield dp
        print('_dp in after')
    print('_dp after')


@pytest.fixture(scope='function')
def dp(_dp):
    # Reset the dispatcher first
    while not _dp.update_queue.empty():
        _dp.update_queue.get(False)
    _dp.chat_data = defaultdict(dict)
    _dp.user_data = defaultdict(dict)
    _dp.handlers = {}
    _dp.groups = []
    _dp.error_handlers = []
    _dp.__stop_event = Event()
    _dp.__exception_event = Event()
    _dp.__async_queue = Queue()
    _dp.__async_threads = set()
    if _dp._Dispatcher__singleton_semaphore.acquire(blocking=0):
        Dispatcher._set_singleton(_dp)
    yield _dp
    Dispatcher._Dispatcher__singleton_semaphore.release()


def pytest_configure(config):
    if sys.version_info >= (3,):
        config.addinivalue_line('filterwarnings', 'ignore::ResourceWarning')
        # TODO: Write so good code that we don't need to ignore ResourceWarnings anymore
