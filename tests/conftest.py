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
import asyncio
import datetime
import functools
import inspect
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

import pytest
import pytz
from httpx import AsyncClient, Response

from telegram import (
    Bot,
    CallbackQuery,
    Chat,
    ChatPermissions,
    ChosenInlineResult,
    File,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultCachedPhoto,
    InputMediaPhoto,
    InputTextMessageContent,
    Message,
    MessageEntity,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
    User,
)
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram._utils.types import ODVInput
from telegram.constants import InputMediaType
from telegram.error import BadRequest, RetryAfter, TimedOut
from telegram.ext import Application, ApplicationBuilder, Defaults, ExtBot, Updater
from telegram.ext.filters import MessageFilter, UpdateFilter
from telegram.request import RequestData
from telegram.request._httpxrequest import HTTPXRequest
from tests.bots import get_bot


# This is here instead of in setup.cfg due to https://github.com/pytest-dev/pytest/issues/8343
def pytest_runtestloop(session):
    session.add_marker(
        pytest.mark.filterwarnings("ignore::telegram.warnings.PTBDeprecationWarning")
    )


GITHUB_ACTION = os.getenv("GITHUB_ACTION", False)

if GITHUB_ACTION:
    pytest_plugins = ["tests.plugin_github_group"]

# THIS KEY IS OBVIOUSLY COMPROMISED
# DO NOT USE IN PRODUCTION!
PRIVATE_KEY = b"-----BEGIN RSA PRIVATE KEY-----\r\nMIIEowIBAAKCAQEA0AvEbNaOnfIL3GjB8VI4M5IaWe+GcK8eSPHkLkXREIsaddum\r\nwPBm/+w8lFYdnY+O06OEJrsaDtwGdU//8cbGJ/H/9cJH3dh0tNbfszP7nTrQD+88\r\nydlcYHzClaG8G+oTe9uEZSVdDXj5IUqR0y6rDXXb9tC9l+oSz+ShYg6+C4grAb3E\r\nSTv5khZ9Zsi/JEPWStqNdpoNuRh7qEYc3t4B/a5BH7bsQENyJSc8AWrfv+drPAEe\r\njQ8xm1ygzWvJp8yZPwOIYuL+obtANcoVT2G2150Wy6qLC0bD88Bm40GqLbSazueC\r\nRHZRug0B9rMUKvKc4FhG4AlNzBCaKgIcCWEqKwIDAQABAoIBACcIjin9d3Sa3S7V\r\nWM32JyVF3DvTfN3XfU8iUzV7U+ZOswA53eeFM04A/Ly4C4ZsUNfUbg72O8Vd8rg/\r\n8j1ilfsYpHVvphwxaHQlfIMa1bKCPlc/A6C7b2GLBtccKTbzjARJA2YWxIaqk9Nz\r\nMjj1IJK98i80qt29xRnMQ5sqOO3gn2SxTErvNchtBiwOH8NirqERXig8VCY6fr3n\r\nz7ZImPU3G/4qpD0+9ULrt9x/VkjqVvNdK1l7CyAuve3D7ha3jPMfVHFtVH5gqbyp\r\nKotyIHAyD+Ex3FQ1JV+H7DkP0cPctQiss7OiO9Zd9C1G2OrfQz9el7ewAPqOmZtC\r\nKjB3hUECgYEA/4MfKa1cvaCqzd3yUprp1JhvssVkhM1HyucIxB5xmBcVLX2/Kdhn\r\nhiDApZXARK0O9IRpFF6QVeMEX7TzFwB6dfkyIePsGxputA5SPbtBlHOvjZa8omMl\r\nEYfNa8x/mJkvSEpzvkWPascuHJWv1cEypqphu/70DxubWB5UKo/8o6cCgYEA0HFy\r\ncgwPMB//nltHGrmaQZPFT7/Qgl9ErZT3G9S8teWY4o4CXnkdU75tBoKAaJnpSfX3\r\nq8VuRerF45AFhqCKhlG4l51oW7TUH50qE3GM+4ivaH5YZB3biwQ9Wqw+QyNLAh/Q\r\nnS4/Wwb8qC9QuyEgcCju5lsCaPEXZiZqtPVxZd0CgYEAshBG31yZjO0zG1TZUwfy\r\nfN3euc8mRgZpSdXIHiS5NSyg7Zr8ZcUSID8jAkJiQ3n3OiAsuq1MGQ6kNa582kLT\r\nFPQdI9Ea8ahyDbkNR0gAY9xbM2kg/Gnro1PorH9PTKE0ekSodKk1UUyNrg4DBAwn\r\nqE6E3ebHXt/2WmqIbUD653ECgYBQCC8EAQNX3AFegPd1GGxU33Lz4tchJ4kMCNU0\r\nN2NZh9VCr3nTYjdTbxsXU8YP44CCKFG2/zAO4kymyiaFAWEOn5P7irGF/JExrjt4\r\nibGy5lFLEq/HiPtBjhgsl1O0nXlwUFzd7OLghXc+8CPUJaz5w42unqT3PBJa40c3\r\nQcIPdQKBgBnSb7BcDAAQ/Qx9juo/RKpvhyeqlnp0GzPSQjvtWi9dQRIu9Pe7luHc\r\nm1Img1EO1OyE3dis/rLaDsAa2AKu1Yx6h85EmNjavBqP9wqmFa0NIQQH8fvzKY3/\r\nP8IHY6009aoamLqYaexvrkHVq7fFKiI6k8myMJ6qblVNFv14+KXU\r\n-----END RSA PRIVATE KEY-----"  # noqa: E501


def env_var_2_bool(env_var: object) -> bool:
    if isinstance(env_var, bool):
        return env_var
    if not isinstance(env_var, str):
        return False
    return env_var.lower().strip() == "true"


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
    pass


class DictBot(Bot):
    pass


class DictApplication(Application):
    pass


@pytest.fixture(scope="session")
async def bot(bot_info):
    """Makes an ExtBot instance with the given bot_info"""
    async with make_bot(bot_info) as _bot:
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


def data_file(filename: str):
    return TEST_DATA_PATH / filename


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


def make_bot(bot_info, **kwargs):
    """
    Tests are executed on tg.ext.ExtBot, as that class only extends the functionality of tg.bot
    """
    _bot = DictExtBot(
        bot_info["token"],
        private_key=PRIVATE_KEY,
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
        bot = make_bot(get_bot())
    return Message(
        message_id=1,
        from_user=kwargs.pop("user", User(id=1, first_name="", is_bot=False)),
        date=kwargs.pop("date", DATE),
        chat=kwargs.pop("chat", Chat(id=1, type="")),
        text=text,
        bot=bot,
        **kwargs,
    )


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


@pytest.fixture(params=["Europe/Berlin", "Asia/Singapore", "UTC"])
def tzinfo(request):
    return pytz.timezone(request.param)


@pytest.fixture()
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


def check_shortcut_signature(
    shortcut: Callable,
    bot_method: Callable,
    shortcut_kwargs: List[str],
    additional_kwargs: List[str],
) -> bool:
    """
    Checks that the signature of a shortcut matches the signature of the underlying bot method.

    Args:
        shortcut: The shortcut, e.g. :meth:`telegram.Message.reply_text`
        bot_method: The bot method, e.g. :meth:`telegram.Bot.send_message`
        shortcut_kwargs: The kwargs passed by the shortcut directly, e.g. ``chat_id``
        additional_kwargs: Additional kwargs of the shortcut that the bot method doesn't have, e.g.
            ``quote``.

    Returns:
        :obj:`bool`: Whether or not the signature matches.
    """
    shortcut_sig = inspect.signature(shortcut)
    effective_shortcut_args = set(shortcut_sig.parameters.keys()).difference(additional_kwargs)
    effective_shortcut_args.discard("self")

    bot_sig = inspect.signature(bot_method)
    expected_args = set(bot_sig.parameters.keys()).difference(shortcut_kwargs)
    expected_args.discard("self")

    args_check = expected_args == effective_shortcut_args
    if not args_check:
        raise Exception(f"Expected arguments {expected_args}, got {effective_shortcut_args}")

    # TODO: Also check annotation of return type. Would currently be a hassle b/c typing doesn't
    # resolve `ForwardRef('Type')` to `Type`. For now we rely on MyPy, which probably allows the
    # shortcuts to return more specific types than the bot method, but it's only annotations after
    # all
    for kwarg in effective_shortcut_args:
        if bot_sig.parameters[kwarg].annotation != shortcut_sig.parameters[kwarg].annotation:
            if isinstance(bot_sig.parameters[kwarg].annotation, type):
                if bot_sig.parameters[kwarg].annotation.__name__ != str(
                    shortcut_sig.parameters[kwarg].annotation
                ):
                    raise Exception(
                        f"For argument {kwarg} I expected {bot_sig.parameters[kwarg].annotation}, "
                        f"but got {shortcut_sig.parameters[kwarg].annotation}"
                    )
            else:
                raise Exception(
                    f"For argument {kwarg} I expected {bot_sig.parameters[kwarg].annotation}, but "
                    f"got {shortcut_sig.parameters[kwarg].annotation}"
                )

    bot_method_sig = inspect.signature(bot_method)
    shortcut_sig = inspect.signature(shortcut)
    for arg in expected_args:
        if not shortcut_sig.parameters[arg].default == bot_method_sig.parameters[arg].default:
            raise Exception(
                f"Default for argument {arg} does not match the default of the Bot method."
            )

    return True


async def check_shortcut_call(
    shortcut_method: Callable,
    bot: ExtBot,
    bot_method_name: str,
    skip_params: Iterable[str] = None,
    shortcut_kwargs: Iterable[str] = None,
) -> bool:
    """
    Checks that a shortcut passes all the existing arguments to the underlying bot method. Use as::

        assert await check_shortcut_call(message.reply_text, message.bot, 'send_message')

    Args:
        shortcut_method: The shortcut method, e.g. `message.reply_text`
        bot: The bot
        bot_method_name: The bot methods name, e.g. `'send_message'`
        skip_params: Parameters that are allowed to be missing, e.g. `['inline_message_id']`
        shortcut_kwargs: The kwargs passed by the shortcut directly, e.g. ``chat_id``

    Returns:
        :obj:`bool`
    """
    if not skip_params:
        skip_params = set()
    if not shortcut_kwargs:
        shortcut_kwargs = set()

    orig_bot_method = getattr(bot, bot_method_name)
    bot_signature = inspect.signature(orig_bot_method)
    expected_args = set(bot_signature.parameters.keys()) - {"self"} - set(skip_params)
    positional_args = {
        name for name, param in bot_signature.parameters.items() if param.default == param.empty
    }
    ignored_args = positional_args | set(shortcut_kwargs)

    shortcut_signature = inspect.signature(shortcut_method)
    # auto_pagination: Special casing for InlineQuery.answer
    kwargs = {name: name for name in shortcut_signature.parameters if name != "auto_pagination"}

    async def make_assertion(**kw):
        # name == value makes sure that
        # a) we receive non-None input for all parameters
        # b) we receive the correct input for each kwarg
        received_kwargs = {
            name for name, value in kw.items() if name in ignored_args or value == name
        }
        if not received_kwargs == expected_args:
            raise Exception(
                f"{orig_bot_method.__name__} did not receive correct value for the parameters "
                f"{expected_args - received_kwargs}"
            )

        if bot_method_name == "get_file":
            # This is here mainly for PassportFile.get_file, which calls .set_credentials on the
            # return value
            return File(file_id="result", file_unique_id="result")
        return True

    setattr(bot, bot_method_name, make_assertion)
    try:
        await shortcut_method(**kwargs)
    except Exception as exc:
        raise exc
    finally:
        setattr(bot, bot_method_name, orig_bot_method)

    return True


# mainly for check_defaults_handling below
def build_kwargs(signature: inspect.Signature, default_kwargs, dfv: Any = DEFAULT_NONE):
    kws = {}
    for name, param in signature.parameters.items():
        # For required params we need to pass something
        if param.default is inspect.Parameter.empty:
            # Some special casing
            if name == "permissions":
                kws[name] = ChatPermissions()
            elif name in ["prices", "commands", "errors"]:
                kws[name] = []
            elif name == "media":
                media = InputMediaPhoto("media", parse_mode=dfv)
                if "list" in str(param.annotation).lower():
                    kws[name] = [media]
                else:
                    kws[name] = media
            elif name == "results":
                itmc = InputTextMessageContent(
                    "text", parse_mode=dfv, disable_web_page_preview=dfv
                )
                kws[name] = [
                    InlineQueryResultArticle("id", "title", input_message_content=itmc),
                    InlineQueryResultCachedPhoto(
                        "id", "photo_file_id", parse_mode=dfv, input_message_content=itmc
                    ),
                ]
            elif name == "ok":
                kws["ok"] = False
                kws["error_message"] = "error"
            else:
                kws[name] = True
        # pass values for params that can have defaults only if we don't want to use the
        # standard default
        elif name in default_kwargs:
            if dfv != DEFAULT_NONE:
                kws[name] = dfv
        # Some special casing for methods that have "exactly one of the optionals" type args
        elif name in ["location", "contact", "venue", "inline_message_id"]:
            kws[name] = True
        elif name == "until_date":
            if dfv == "non-None-value":
                # Europe/Berlin
                kws[name] = pytz.timezone("Europe/Berlin").localize(
                    datetime.datetime(2000, 1, 1, 0)
                )
            else:
                # UTC
                kws[name] = datetime.datetime(2000, 1, 1, 0)
    return kws


async def check_defaults_handling(
    method: Callable,
    bot: ExtBot,
    return_value=None,
) -> bool:
    """
    Checks that tg.ext.Defaults are handled correctly.

    Args:
        method: The shortcut/bot_method
        bot: The bot
        return_value: Optional. The return value of Bot._post that the method expects. Defaults to
            None. get_file is automatically handled.

    """

    shortcut_signature = inspect.signature(method)
    kwargs_need_default = [
        kwarg
        for kwarg, value in shortcut_signature.parameters.items()
        if isinstance(value.default, DefaultValue) and not kwarg.endswith("_timeout")
    ]

    defaults_no_custom_defaults = Defaults()
    kwargs = {kwarg: "custom_default" for kwarg in inspect.signature(Defaults).parameters.keys()}
    kwargs["tzinfo"] = pytz.timezone("America/New_York")
    defaults_custom_defaults = Defaults(**kwargs)

    expected_return_values = [None, []] if return_value is None else [return_value]

    async def make_assertion(
        url, request_data: RequestData, df_value=DEFAULT_NONE, *args, **kwargs
    ):
        data = request_data.parameters

        # Check regular arguments that need defaults
        for arg in (dkw for dkw in kwargs_need_default if dkw != "timeout"):
            # 'None' should not be passed along to Telegram
            if df_value in [None, DEFAULT_NONE]:
                if arg in data:
                    pytest.fail(
                        f"Got value {data[arg]} for argument {arg}, expected it to be absent"
                    )
            else:
                value = data.get(arg, "`not passed at all`")
                if value != df_value:
                    pytest.fail(f"Got value {value} for argument {arg} instead of {df_value}")

        # Check InputMedia (parse_mode can have a default)
        def check_input_media(m: Dict):
            parse_mode = m.get("parse_mode", None)
            if df_value is DEFAULT_NONE:
                if parse_mode is not None:
                    pytest.fail("InputMedia has non-None parse_mode")
            elif parse_mode != df_value:
                pytest.fail(
                    f"Got value {parse_mode} for InputMedia.parse_mode instead of {df_value}"
                )

        media = data.pop("media", None)
        if media:
            if isinstance(media, dict) and isinstance(media.get("type", None), InputMediaType):
                check_input_media(media)
            else:
                for m in media:
                    check_input_media(m)

        # Check InlineQueryResults
        results = data.pop("results", [])
        for result in results:
            if df_value in [DEFAULT_NONE, None]:
                if "parse_mode" in result:
                    pytest.fail("ILQR has a parse mode, expected it to be absent")
            # Here we explicitly use that we only pass ILQRPhoto and ILQRArticle for testing
            # so ILQRPhoto is expected to have parse_mode if df_value is not in [DF_NONE, NONE]
            elif "photo" in result and result.get("parse_mode") != df_value:
                pytest.fail(
                    f'Got value {result.get("parse_mode")} for '
                    f"ILQR.parse_mode instead of {df_value}"
                )
            imc = result.get("input_message_content")
            if not imc:
                continue
            for attr in ["parse_mode", "disable_web_page_preview"]:
                if df_value in [DEFAULT_NONE, None]:
                    if attr in imc:
                        pytest.fail(f"ILQR.i_m_c has a {attr}, expected it to be absent")
                # Here we explicitly use that we only pass InputTextMessageContent for testing
                # which has both attributes
                elif imc.get(attr) != df_value:
                    pytest.fail(
                        f"Got value {imc.get(attr)} for ILQR.i_m_c.{attr} instead of {df_value}"
                    )

        # Check datetime conversion
        until_date = data.pop("until_date", None)
        if until_date:
            if df_value == "non-None-value":
                if until_date != 946681200:
                    pytest.fail("Non-naive until_date was interpreted as Europe/Berlin.")
            if df_value is DEFAULT_NONE:
                if until_date != 946684800:
                    pytest.fail("Naive until_date was not interpreted as UTC")
            if df_value == "custom_default":
                if until_date != 946702800:
                    pytest.fail("Naive until_date was not interpreted as America/New_York")

        if method.__name__ in ["get_file", "get_small_file", "get_big_file"]:
            # This is here mainly for PassportFile.get_file, which calls .set_credentials on the
            # return value
            out = File(file_id="result", file_unique_id="result")
            nonlocal expected_return_values
            expected_return_values = [out]
            return out.to_dict()
        # Otherwise return None by default, as TGObject.de_json/list(None) in [None, []]
        # That way we can check what gets passed to Request.post without having to actually
        # make a request
        # Some methods expect specific output, so we allow to customize that
        return return_value

    orig_post = bot.request.post
    try:
        for default_value, defaults in [
            (DEFAULT_NONE, defaults_no_custom_defaults),
            ("custom_default", defaults_custom_defaults),
        ]:
            bot._defaults = defaults
            # 1: test that we get the correct default value, if we don't specify anything
            kwargs = build_kwargs(
                shortcut_signature,
                kwargs_need_default,
            )
            assertion_callback = functools.partial(make_assertion, df_value=default_value)
            setattr(bot.request, "post", assertion_callback)
            assert await method(**kwargs) in expected_return_values

            # 2: test that we get the manually passed non-None value
            kwargs = build_kwargs(shortcut_signature, kwargs_need_default, dfv="non-None-value")
            assertion_callback = functools.partial(make_assertion, df_value="non-None-value")
            setattr(bot.request, "post", assertion_callback)
            assert await method(**kwargs) in expected_return_values

            # 3: test that we get the manually passed None value
            kwargs = build_kwargs(
                shortcut_signature,
                kwargs_need_default,
                dfv=None,
            )
            assertion_callback = functools.partial(make_assertion, df_value=None)
            setattr(bot.request, "post", assertion_callback)
            assert await method(**kwargs) in expected_return_values
    except Exception as exc:
        raise exc
    finally:
        setattr(bot.request, "post", orig_post)
        bot._defaults = None

    return True


async def send_webhook_message(
    ip: str,
    port: int,
    payload_str: Optional[str],
    url_path: str = "",
    content_len: int = -1,
    content_type: str = "application/json",
    get_method: str = None,
) -> Response:
    headers = {
        "content-type": content_type,
    }

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
