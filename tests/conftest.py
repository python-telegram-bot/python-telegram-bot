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
import asyncio
import datetime
import logging
import sys
from typing import Dict, List
from uuid import uuid4

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
from tests.auxil.ci_bots import BOT_INFO_PROVIDER
from tests.auxil.constants import PRIVATE_KEY
from tests.auxil.envvars import RUN_TEST_OFFICIAL, TEST_WITH_OPT_DEPS
from tests.auxil.files import data_file
from tests.auxil.networking import NonchalantHttpxRequest
from tests.auxil.pytest_classes import PytestApplication, PytestBot, make_bot
from tests.auxil.timezones import BasicTimezone

if TEST_WITH_OPT_DEPS:
    import pytz


# Don't collect `test_official.py` on Python 3.10- since it uses newer features like X | Y syntax.
# Docs: https://docs.pytest.org/en/7.1.x/example/pythoncollection.html#customizing-test-collection
collect_ignore = []
if sys.version_info < (3, 10):
    if RUN_TEST_OFFICIAL:
        logging.warning("Skipping test_official.py since it requires Python 3.10+")
    collect_ignore_glob = ["test_official/*.py"]


# This is here instead of in setup.cfg due to https://github.com/pytest-dev/pytest/issues/8343
def pytest_runtestloop(session: pytest.Session):
    session.add_marker(
        pytest.mark.filterwarnings("ignore::telegram.warnings.PTBDeprecationWarning")
    )


def no_rerun_after_xfail_or_flood(error, name, test: pytest.Function, plugin):
    """Don't rerun tests that have xfailed when marked with xfail, or when we hit a flood limit."""
    xfail_present = test.get_closest_marker(name="xfail")
    if getattr(error[1], "msg", "") is None:
        raise error[1]
    did_we_flood = "flood" in getattr(error[1], "msg", "")  # _pytest.outcomes.XFailed has 'msg'
    if xfail_present or did_we_flood:
        return False
    return True


def pytest_collection_modifyitems(items: List[pytest.Item]):
    """Here we add a flaky marker to all request making tests and a (no_)req marker to the rest."""
    for item in items:  # items are the test methods
        parent = item.parent  # Get the parent of the item (class, or module if defined outside)
        if parent is None:  # should never happen, but just in case
            return
        if (  # Check if the class name ends with 'WithRequest' and if it has no flaky marker
            parent.name.endswith("WithRequest")
            and not parent.get_closest_marker(  # get_closest_marker gets pytest.marks with `name`
                name="flaky"
            )  # don't add/override any previously set markers
            and not parent.get_closest_marker(name="req")
        ):  # Add the flaky marker with a rerun filter to the class
            parent.add_marker(pytest.mark.flaky(3, 1, rerun_filter=no_rerun_after_xfail_or_flood))
            parent.add_marker(pytest.mark.req)
        # Add the no_req marker to all classes that end with 'WithoutRequest' and don't have it
        elif parent.name.endswith("WithoutRequest") and not parent.get_closest_marker(
            name="no_req"
        ):
            parent.add_marker(pytest.mark.no_req)


# Redefine the event_loop fixture to have a session scope. Otherwise `bot` fixture can't be
# session. See https://github.com/pytest-dev/pytest-asyncio/issues/68 for more details.
@pytest.fixture(scope="session")
def event_loop(request):
    # ever since ProactorEventLoop became the default in Win 3.8+, the app crashes after the loop
    # is closed. Hence, we use SelectorEventLoop on Windows to avoid this. See
    # https://github.com/python/cpython/issues/83413, https://github.com/encode/httpx/issues/914
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.get_event_loop_policy().new_event_loop()
    # loop.close() # instead of closing here, do that at the every end of the test session


@pytest.fixture(scope="session")
def bot_info() -> Dict[str, str]:
    return BOT_INFO_PROVIDER.get_info()


@pytest.fixture(scope="session")
async def bot(bot_info):
    """Makes an ExtBot instance with the given bot_info"""
    async with make_bot(bot_info) as _bot:
        yield _bot


@pytest.fixture()
def one_time_bot(bot_info):
    """A function scoped bot since the session bot would shutdown when `async with app` finishes"""
    return make_bot(bot_info)


@pytest.fixture(scope="session")
async def cdc_bot(bot_info):
    """Makes an ExtBot instance with the given bot_info that uses arbitrary callback_data"""
    async with make_bot(bot_info, arbitrary_callback_data=True) as _bot:
        yield _bot


@pytest.fixture(scope="session")
async def raw_bot(bot_info):
    """Makes an regular Bot instance with the given bot_info"""
    async with PytestBot(
        bot_info["token"],
        private_key=PRIVATE_KEY if TEST_WITH_OPT_DEPS else None,
        request=NonchalantHttpxRequest(8),
        get_updates_request=NonchalantHttpxRequest(1),
    ) as _bot:
        yield _bot


# Here we store the default bots so that we don't have to create them again and again.
# They are initialized but not shutdown on pytest_sessionfinish because it is causing
# problems with the event loop (Event loop is closed).
_default_bots = {}


@pytest.fixture(scope="session")
async def default_bot(request, bot_info):
    param = request.param if hasattr(request, "param") else {}
    defaults = Defaults(**param)

    # If the bot is already created, return it. Else make a new one.
    default_bot = _default_bots.get(defaults)
    if default_bot is None:
        default_bot = make_bot(bot_info, defaults=defaults)
        await default_bot.initialize()
        _default_bots[defaults] = default_bot  # Defaults object is hashable
    return default_bot


@pytest.fixture(scope="session")
async def tz_bot(timezone, bot_info):
    defaults = Defaults(tzinfo=timezone)
    try:  # If the bot is already created, return it. Saves time since get_me is not called again.
        return _default_bots[defaults]
    except KeyError:
        default_bot = make_bot(bot_info, defaults=defaults)
        await default_bot.initialize()
        _default_bots[defaults] = default_bot
        return default_bot


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


@pytest.fixture()
async def app(bot_info):
    # We build a new bot each time so that we use `app` in a context manager without problems
    application = (
        ApplicationBuilder().bot(make_bot(bot_info)).application_class(PytestApplication).build()
    )
    yield application
    if application.running:
        await application.stop()
        await application.shutdown()


@pytest.fixture()
async def updater(bot_info):
    # We build a new bot each time so that we use `updater` in a context manager without problems
    up = Updater(bot=make_bot(bot_info), update_queue=asyncio.Queue())
    yield up
    if up.running:
        await up.stop()
        await up.shutdown()


@pytest.fixture()
def thumb_file():
    with data_file("thumb.jpg").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
def class_thumb_file():
    with data_file("thumb.jpg").open("rb") as f:
        yield f


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


def _get_false_update_fixture_decorator_params():
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


@pytest.fixture(**_get_false_update_fixture_decorator_params())
def false_update(request):
    return Update(update_id=1, **request.param)


@pytest.fixture(scope="session", params=["Europe/Berlin", "Asia/Singapore", "UTC"])
def tzinfo(request):
    if TEST_WITH_OPT_DEPS:
        return pytz.timezone(request.param)
    hours_offset = {"Europe/Berlin": 2, "Asia/Singapore": 8, "UTC": 0}[request.param]
    return BasicTimezone(offset=datetime.timedelta(hours=hours_offset), name=request.param)


@pytest.fixture(scope="session")
def timezone(tzinfo):
    return tzinfo


@pytest.fixture()
def tmp_file(tmp_path):
    with tmp_path / uuid4().hex as file:
        yield file
