#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
"""This module contains settings and fixtures for pytest. Auxiliary functions used in the tests
which are neither of those should go into `tests/auxil`.
"""
import asyncio
import datetime
import sys

import pytest

from telegram import (
    CallbackQuery,
    Chat,
    ChosenInlineResult,
    InlineQuery,
    Message,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
    User,
)
from telegram.ext import ApplicationBuilder, Defaults, Updater
from telegram.ext.filters import MessageFilter, UpdateFilter
from tests.auxil.build_messages import DATE
from tests.auxil.ci_bots import PRIVATE_KEY, get_bot, make_bot
from tests.auxil.envvars import GITHUB_ACTION, TEST_WITH_OPT_DEPS
from tests.auxil.files import data_file
from tests.auxil.networking import NonchalantHttpxRequest
from tests.auxil.slots import DictApplication, DictBot


# This is here instead of in setup.cfg due to https://github.com/pytest-dev/pytest/issues/8343
def pytest_runtestloop(session):
    session.add_marker(
        pytest.mark.filterwarnings("ignore::telegram.warnings.PTBDeprecationWarning")
    )


if GITHUB_ACTION:
    pytest_plugins = ["tests.plugin_github_group"]

if TEST_WITH_OPT_DEPS:
    import pytz


# Redefine the event_loop fixture to have a session scope. Otherwise `bot` fixture can't be
# session. See https://github.com/pytest-dev/pytest-asyncio/issues/68 for more details.
@pytest.fixture(scope="session")
def event_loop(request):
    # ever since ProactorEventLoop became the default in Win 3.8+, the app crashes after the loop
    # is closed. Hence, we use SelectorEventLoop on Windows to avoid this. See
    # https://github.com/python/cpython/issues/83413, https://github.com/encode/httpx/issues/914
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    # loop.close() # instead of closing here, do that at the every end of the test session


# Related to the above, see https://stackoverflow.com/a/67307042/10606962
def pytest_sessionfinish(session, exitstatus):
    asyncio.get_event_loop().close()


@pytest.fixture(scope="session")
def bot_info():
    return get_bot()


@pytest.fixture(scope="session")
async def bot(bot_info):
    """Makes an ExtBot instance with the given bot_info"""
    async with make_bot(bot_info) as _bot:
        yield _bot


@pytest.fixture(scope="session")
async def cdc_bot(bot_info):
    """Makes an ExtBot instance with the given bot_info that uses arbitrary callback_data"""
    async with make_bot(bot_info, arbitrary_callback_data=True) as _bot:
        yield _bot


@pytest.fixture(scope="session")
async def raw_bot(bot_info):
    """Makes an regular Bot instance with the given bot_info"""
    async with DictBot(
        bot_info["token"],
        private_key=PRIVATE_KEY,
        request=NonchalantHttpxRequest(8),
        get_updates_request=NonchalantHttpxRequest(1),
    ) as _bot:
        yield _bot


@pytest.fixture(scope="function")
async def default_bot(request, bot_info):
    param = request.param if hasattr(request, "param") else {}

    default_bot = make_bot(bot_info, defaults=Defaults(**param))
    async with default_bot:
        yield default_bot


@pytest.fixture(scope="function")
async def tz_bot(timezone, bot_info):
    default_bot = make_bot(bot_info, defaults=Defaults(tzinfo=timezone))
    async with default_bot:
        yield default_bot


@pytest.fixture(scope="session")
def chat_id(bot_info):
    return bot_info["chat_id"]


@pytest.fixture(scope="session")
def super_group_id(bot_info):
    return bot_info["super_group_id"]


@pytest.fixture(scope="session")
def forum_group_id(bot_info):
    return int(bot_info["forum_group_id"])


@pytest.fixture(scope="session")
def channel_id(bot_info):
    return bot_info["channel_id"]


@pytest.fixture(scope="session")
def provider_token(bot_info):
    return bot_info["payment_provider_token"]


@pytest.fixture(scope="function")
async def app(bot_info):
    # We build a new bot each time so that we use `app` in a context manager without problems
    application = (
        ApplicationBuilder().bot(make_bot(bot_info)).application_class(DictApplication).build()
    )
    yield application
    if application.running:
        await application.stop()
        await application.shutdown()


@pytest.fixture(scope="function")
async def updater(bot_info):
    # We build a new bot each time so that we use `updater` in a context manager without problems
    up = Updater(bot=make_bot(bot_info), update_queue=asyncio.Queue())
    yield up
    if up.running:
        await up.stop()
        await up.shutdown()


@pytest.fixture(scope="function")
def thumb_file():
    f = data_file("thumb.jpg").open("rb")
    yield f
    f.close()


@pytest.fixture(scope="class")
def class_thumb_file():
    f = data_file("thumb.jpg").open("rb")
    yield f
    f.close()


@pytest.fixture(
    scope="class",
    params=[{"class": MessageFilter}, {"class": UpdateFilter}],
    ids=["MessageFilter", "UpdateFilter"],
)
def mock_filter(request):
    class MockFilter(request.param["class"]):
        def __init__(self):
            super().__init__()
            self.tested = False

        def filter(self, _):
            self.tested = True

    return MockFilter()


def get_false_update_fixture_decorator_params():
    message = Message(1, DATE, Chat(1, ""), from_user=User(1, "", False), text="test")
    params = [
        {"callback_query": CallbackQuery(1, User(1, "", False), "chat", message=message)},
        {"channel_post": message},
        {"edited_channel_post": message},
        {"inline_query": InlineQuery(1, User(1, "", False), "", "")},
        {"chosen_inline_result": ChosenInlineResult("id", User(1, "", False), "")},
        {"shipping_query": ShippingQuery("id", User(1, "", False), "", None)},
        {"pre_checkout_query": PreCheckoutQuery("id", User(1, "", False), "", 0, "")},
        {"callback_query": CallbackQuery(1, User(1, "", False), "chat")},
    ]
    ids = tuple(key for kwargs in params for key in kwargs)
    return {"params": params, "ids": ids}


@pytest.fixture(scope="function", **get_false_update_fixture_decorator_params())
def false_update(request):
    return Update(update_id=1, **request.param)


class BasicTimezone(datetime.tzinfo):
    """Used to test the timezone functionality in case pytz is not installed."""

    def __init__(self, offset, name):
        self.offset = offset
        self.name = name

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return datetime.timedelta(0)


@pytest.fixture(params=["Europe/Berlin", "Asia/Singapore", "UTC"])
def tzinfo(request):
    if TEST_WITH_OPT_DEPS:
        return pytz.timezone(request.param)
    else:
        hours_offset = {"Europe/Berlin": 2, "Asia/Singapore": 8, "UTC": 0}[request.param]
        return BasicTimezone(offset=datetime.timedelta(hours=hours_offset), name=request.param)


@pytest.fixture()
def timezone(tzinfo):
    return tzinfo
