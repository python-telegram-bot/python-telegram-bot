#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
import os
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional

import pytest
from httpx import AsyncClient, Response

from telegram import (
    Bot,
    CallbackQuery,
    Chat,
    ChosenInlineResult,
    InlineQuery,
    Message,
    MessageEntity,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
    User,
)
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import ODVInput
from telegram.error import BadRequest, RetryAfter, TimedOut
from telegram.ext import Application, ApplicationBuilder, Defaults, ExtBot, Updater
from telegram.ext.filters import MessageFilter, UpdateFilter
from telegram.request import RequestData
from telegram.request._httpxrequest import HTTPXRequest
from tests.auxil.object_conversions import env_var_2_bool
from tests.bots import BotInfoProvider

BOT_INFO = BotInfoProvider()


# This is here instead of in setup.cfg due to https://github.com/pytest-dev/pytest/issues/8343
def pytest_runtestloop(session: pytest.Session):
    session.add_marker(
        pytest.mark.filterwarnings("ignore::telegram.warnings.PTBDeprecationWarning")
    )


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


def no_rerun_after_xfail_or_flood(error, name, test: pytest.Function, plugin):
    """Don't rerun tests that have xfailed when marked with xfail, or when we hit a flood limit."""
    xfail_present = test.get_closest_marker(name="xfail")
    did_we_flood = "flood" in getattr(error[1], "msg", "")  # _pytest.outcomes.XFailed has 'msg'
    if xfail_present or did_we_flood:
        return False
    return True


GITHUB_ACTION = os.getenv("GITHUB_ACTION", False)

if GITHUB_ACTION:
    pytest_plugins = ["tests.plugin_github_group"]

# THIS KEY IS OBVIOUSLY COMPROMISED
# DO NOT USE IN PRODUCTION!
PRIVATE_KEY = b"-----BEGIN RSA PRIVATE KEY-----\r\nMIIEowIBAAKCAQEA0AvEbNaOnfIL3GjB8VI4M5IaWe+GcK8eSPHkLkXREIsaddum\r\nwPBm/+w8lFYdnY+O06OEJrsaDtwGdU//8cbGJ/H/9cJH3dh0tNbfszP7nTrQD+88\r\nydlcYHzClaG8G+oTe9uEZSVdDXj5IUqR0y6rDXXb9tC9l+oSz+ShYg6+C4grAb3E\r\nSTv5khZ9Zsi/JEPWStqNdpoNuRh7qEYc3t4B/a5BH7bsQENyJSc8AWrfv+drPAEe\r\njQ8xm1ygzWvJp8yZPwOIYuL+obtANcoVT2G2150Wy6qLC0bD88Bm40GqLbSazueC\r\nRHZRug0B9rMUKvKc4FhG4AlNzBCaKgIcCWEqKwIDAQABAoIBACcIjin9d3Sa3S7V\r\nWM32JyVF3DvTfN3XfU8iUzV7U+ZOswA53eeFM04A/Ly4C4ZsUNfUbg72O8Vd8rg/\r\n8j1ilfsYpHVvphwxaHQlfIMa1bKCPlc/A6C7b2GLBtccKTbzjARJA2YWxIaqk9Nz\r\nMjj1IJK98i80qt29xRnMQ5sqOO3gn2SxTErvNchtBiwOH8NirqERXig8VCY6fr3n\r\nz7ZImPU3G/4qpD0+9ULrt9x/VkjqVvNdK1l7CyAuve3D7ha3jPMfVHFtVH5gqbyp\r\nKotyIHAyD+Ex3FQ1JV+H7DkP0cPctQiss7OiO9Zd9C1G2OrfQz9el7ewAPqOmZtC\r\nKjB3hUECgYEA/4MfKa1cvaCqzd3yUprp1JhvssVkhM1HyucIxB5xmBcVLX2/Kdhn\r\nhiDApZXARK0O9IRpFF6QVeMEX7TzFwB6dfkyIePsGxputA5SPbtBlHOvjZa8omMl\r\nEYfNa8x/mJkvSEpzvkWPascuHJWv1cEypqphu/70DxubWB5UKo/8o6cCgYEA0HFy\r\ncgwPMB//nltHGrmaQZPFT7/Qgl9ErZT3G9S8teWY4o4CXnkdU75tBoKAaJnpSfX3\r\nq8VuRerF45AFhqCKhlG4l51oW7TUH50qE3GM+4ivaH5YZB3biwQ9Wqw+QyNLAh/Q\r\nnS4/Wwb8qC9QuyEgcCju5lsCaPEXZiZqtPVxZd0CgYEAshBG31yZjO0zG1TZUwfy\r\nfN3euc8mRgZpSdXIHiS5NSyg7Zr8ZcUSID8jAkJiQ3n3OiAsuq1MGQ6kNa582kLT\r\nFPQdI9Ea8ahyDbkNR0gAY9xbM2kg/Gnro1PorH9PTKE0ekSodKk1UUyNrg4DBAwn\r\nqE6E3ebHXt/2WmqIbUD653ECgYBQCC8EAQNX3AFegPd1GGxU33Lz4tchJ4kMCNU0\r\nN2NZh9VCr3nTYjdTbxsXU8YP44CCKFG2/zAO4kymyiaFAWEOn5P7irGF/JExrjt4\r\nibGy5lFLEq/HiPtBjhgsl1O0nXlwUFzd7OLghXc+8CPUJaz5w42unqT3PBJa40c3\r\nQcIPdQKBgBnSb7BcDAAQ/Qx9juo/RKpvhyeqlnp0GzPSQjvtWi9dQRIu9Pe7luHc\r\nm1Img1EO1OyE3dis/rLaDsAa2AKu1Yx6h85EmNjavBqP9wqmFa0NIQQH8fvzKY3/\r\nP8IHY6009aoamLqYaexvrkHVq7fFKiI6k8myMJ6qblVNFv14+KXU\r\n-----END RSA PRIVATE KEY-----"  # noqa: E501

TEST_WITH_OPT_DEPS = env_var_2_bool(os.getenv("TEST_WITH_OPT_DEPS", True))
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


@pytest.fixture(scope="session")
def bot_info() -> Dict[str, str]:
    return BOT_INFO.get_info()


# Below classes are used to monkeypatch attributes since parent classes don't have __dict__
class TestHttpxRequest(HTTPXRequest):
    async def _request_wrapper(
        self,
        method: str,
        url: str,
        request_data: RequestData = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
    ) -> bytes:
        try:
            return await super()._request_wrapper(
                method=method,
                url=url,
                request_data=request_data,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
            )
        except RetryAfter as e:
            pytest.xfail(f"Not waiting for flood control: {e}")
        except TimedOut as e:
            pytest.xfail(f"Ignoring TimedOut error: {e}")


class DictExtBot(ExtBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Makes it easier to work with the bot in tests
        self._unfreeze()

    # Here we override get_me for caching because we don't want to call the API repeatedly in tests
    async def get_me(self, *args, **kwargs):
        return await mocked_get_me(self)


class DictBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Makes it easier to work with the bot in tests
        self._unfreeze()

    # Here we override get_me for caching because we don't want to call the API repeatedly in tests
    async def get_me(self, *args, **kwargs):
        return await mocked_get_me(self)


class DictApplication(Application):
    pass


async def mocked_get_me(bot: Bot):
    if bot._bot_user is None:
        bot._bot_user = get_bot_user(bot.token)
    return bot._bot_user


def get_bot_user(token: str) -> User:
    """Used to return a mock user in bot.get_me(). This saves API calls on every init."""
    bot_info = BOT_INFO.get_info()
    # We don't take token from bot_info, because we need to make a bot with a specific ID. So we
    # generate the correct user_id from the token (token from bot_info is random each test run).
    # This is important in e.g. bot equality tests. The other parameters like first_name don't
    # matter as much. In the future we may provide a way to get all the correct info from the token
    user_id = int(token.split(":")[0])
    first_name = bot_info.get("name")
    username = bot_info.get("username").strip("@")
    return User(
        user_id,
        first_name,
        is_bot=True,
        username=username,
        can_join_groups=True,
        can_read_all_group_messages=False,
        supports_inline_queries=True,
    )


@pytest.fixture(scope="session")
async def bot(bot_info):
    """Makes an ExtBot instance with the given bot_info"""
    async with make_bot(bot_info) as _bot:
        yield _bot


@pytest.fixture(scope="function")
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
    async with DictBot(
        bot_info["token"],
        private_key=PRIVATE_KEY,
        request=TestHttpxRequest(8),
        get_updates_request=TestHttpxRequest(1),
    ) as _bot:
        yield _bot


# Here we store the default bots so that we don't have to create them again and again.
# They are initialized but not shutdown on pytest_sessionfinish because it is causing
# problems with the event loop (Event loop is closed).
default_bots = {}


@pytest.fixture(scope="session")
async def default_bot(request, bot_info):
    param = request.param if hasattr(request, "param") else {}
    defaults = Defaults(**param)

    # If the bot is already created, return it. Else make a new one.
    default_bot = default_bots.get(defaults, None)
    if default_bot is None:
        default_bot = make_bot(bot_info, defaults=defaults)
        await default_bot.initialize()
        default_bots[defaults] = default_bot  # Defaults object is hashable
    return default_bot


@pytest.fixture(scope="session")
async def tz_bot(timezone, bot_info):
    defaults = Defaults(tzinfo=timezone)
    try:  # If the bot is already created, return it. Saves time since get_me is not called again.
        return default_bots[defaults]
    except KeyError:
        default_bot = make_bot(bot_info, defaults=defaults)
        await default_bot.initialize()
        default_bots[defaults] = default_bot
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


PROJECT_ROOT_PATH = Path(__file__).parent.parent.resolve()
TEST_DATA_PATH = Path(__file__).parent.resolve() / "data"


def data_file(filename: str) -> Path:
    return TEST_DATA_PATH / filename


@pytest.fixture(scope="function")
def thumb_file():
    with data_file("thumb.jpg").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
def class_thumb_file():
    with data_file("thumb.jpg").open("rb") as f:
        yield f


def make_bot(bot_info=None, **kwargs):
    """
    Tests are executed on tg.ext.ExtBot, as that class only extends the functionality of tg.bot
    """
    token = kwargs.pop("token", (bot_info or {}).get("token"))
    private_key = kwargs.pop("private_key", PRIVATE_KEY)
    kwargs.pop("token", None)
    _bot = DictExtBot(
        token=token,
        private_key=private_key if TEST_WITH_OPT_DEPS else None,
        request=TestHttpxRequest(8),
        get_updates_request=TestHttpxRequest(1),
        **kwargs,
    )
    return _bot


CMD_PATTERN = re.compile(r"/[\da-z_]{1,32}(?:@\w{1,32})?")
DATE = datetime.datetime.now()


def make_message(text, **kwargs):
    """
    Testing utility factory to create a fake ``telegram.Message`` with
    reasonable defaults for mimicking a real message.
    :param text: (str) message text
    :return: a (fake) ``telegram.Message``
    """
    bot = kwargs.pop("bot", None)
    if bot is None:
        bot = make_bot(BOT_INFO.get_info())
    message = Message(
        message_id=1,
        from_user=kwargs.pop("user", User(id=1, first_name="", is_bot=False)),
        date=kwargs.pop("date", DATE),
        chat=kwargs.pop("chat", Chat(id=1, type="")),
        text=text,
        **kwargs,
    )
    message.set_bot(bot)
    return message


def make_command_message(text, **kwargs):
    """
    Testing utility factory to create a message containing a single telegram
    command.
    Mimics the Telegram API in that it identifies commands within the message
    and tags the returned ``Message`` object with the appropriate ``MessageEntity``
    tag (but it does this only for commands).

    :param text: (str) message text containing (or not) the command
    :return: a (fake) ``telegram.Message`` containing only the command
    """

    match = re.search(CMD_PATTERN, text)
    entities = (
        [
            MessageEntity(
                type=MessageEntity.BOT_COMMAND, offset=match.start(0), length=len(match.group(0))
            )
        ]
        if match
        else []
    )

    return make_message(text, entities=entities, **kwargs)


def make_message_update(message, message_factory=make_message, edited=False, **kwargs):
    """
    Testing utility factory to create an update from a message, as either a
    ``telegram.Message`` or a string. In the latter case ``message_factory``
    is used to convert ``message`` to a ``telegram.Message``.
    :param message: either a ``telegram.Message`` or a string with the message text
    :param message_factory: function to convert the message text into a ``telegram.Message``
    :param edited: whether the message should be stored as ``edited_message`` (vs. ``message``)
    :return: ``telegram.Update`` with the given message
    """
    if not isinstance(message, Message):
        message = message_factory(message, **kwargs)
    update_kwargs = {"message" if not edited else "edited_message": message}
    return Update(0, **update_kwargs)


def make_command_update(message, edited=False, **kwargs):
    """
    Testing utility factory to create an update from a message that potentially
    contains a command. See ``make_command_message`` for more details.
    :param message: message potentially containing a command
    :param edited: whether the message should be stored as ``edited_message`` (vs. ``message``)
    :return: ``telegram.Update`` with the given message
    """
    return make_message_update(message, make_command_message, edited, **kwargs)


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
    def __init__(self, offset, name):
        self.offset = offset
        self.name = name

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return datetime.timedelta(0)


@pytest.fixture(scope="session", params=["Europe/Berlin", "Asia/Singapore", "UTC"])
def tzinfo(request):
    if TEST_WITH_OPT_DEPS:
        return pytz.timezone(request.param)
    else:
        hours_offset = {"Europe/Berlin": 2, "Asia/Singapore": 8, "UTC": 0}[request.param]
        return BasicTimezone(offset=datetime.timedelta(hours=hours_offset), name=request.param)


@pytest.fixture(scope="session")
def timezone(tzinfo):
    return tzinfo


@pytest.fixture()
def mro_slots():
    def _mro_slots(_class, only_parents: bool = False):
        if only_parents:
            classes = _class.__class__.__mro__[1:-1]
        else:
            classes = _class.__class__.__mro__[:-1]

        return [
            attr
            for cls in classes
            if hasattr(cls, "__slots__")  # The Exception class doesn't have slots
            for attr in cls.__slots__
            if attr != "__dict__"  # left here for classes which still has __dict__
        ]

    return _mro_slots


def call_after(function: Callable, after: Callable):
    """Run a callable after another has executed. Useful when trying to make sure that a function
    did actually run, but just monkeypatching it doesn't work because this would break some other
    functionality.

    Example usage:

    def test_stuff(self, bot, monkeypatch):

        def after(arg):
            # arg is the return value of `send_message`
            self.received = arg

        monkeypatch.setattr(bot, 'send_message', call_after(bot.send_message, after)

    """
    if asyncio.iscoroutinefunction(function):

        async def wrapped(*args, **kwargs):
            out = await function(*args, **kwargs)
            if asyncio.iscoroutinefunction(after):
                await after(out)
            else:
                after(out)
            return out

    else:

        def wrapped(*args, **kwargs):
            out = function(*args, **kwargs)
            after(out)
            return out

    return wrapped


async def expect_bad_request(func, message, reason):
    """
    Wrapper for testing bot functions expected to result in an :class:`telegram.error.BadRequest`.
    Makes it XFAIL, if the specified error message is present.

    Args:
        func: The awaitable to be executed.
        message: The expected message of the bad request error. If another message is present,
            the error will be reraised.
        reason: Explanation for the XFAIL.

    Returns:
        On success, returns the return value of :attr:`func`
    """
    try:
        return await func()
    except BadRequest as e:
        if message in str(e):
            pytest.xfail(f"{reason}. {e}")
        else:
            raise e


async def send_webhook_message(
    ip: str,
    port: int,
    payload_str: Optional[str],
    url_path: str = "",
    content_len: int = -1,
    content_type: str = "application/json",
    get_method: str = None,
    secret_token: str = None,
) -> Response:
    headers = {
        "content-type": content_type,
    }
    if secret_token:
        headers["X-Telegram-Bot-Api-Secret-Token"] = secret_token

    if not payload_str:
        content_len = None
        payload = None
    else:
        payload = bytes(payload_str, encoding="utf-8")

    if content_len == -1:
        content_len = len(payload)

    if content_len is not None:
        headers["content-length"] = str(content_len)

    url = f"http://{ip}:{port}/{url_path}"

    async with AsyncClient() as client:
        return await client.request(
            url=url, method=get_method or "POST", data=payload, headers=headers
        )
