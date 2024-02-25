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
import copy
import datetime as dtm
import inspect
import logging
import pickle
import re
import socket
import time
from collections import defaultdict
from http import HTTPStatus
from io import BytesIO
from typing import Tuple

import httpx
import pytest

from telegram import (
    Bot,
    BotCommand,
    BotCommandScopeChat,
    BotDescription,
    BotName,
    BotShortDescription,
    CallbackQuery,
    Chat,
    ChatAdministratorRights,
    ChatPermissions,
    Dice,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultDocument,
    InlineQueryResultsButton,
    InlineQueryResultVoice,
    InputFile,
    InputMediaDocument,
    InputMediaPhoto,
    InputMessageContent,
    InputTextMessageContent,
    LabeledPrice,
    LinkPreviewOptions,
    MenuButton,
    MenuButtonCommands,
    MenuButtonDefault,
    MenuButtonWebApp,
    Message,
    MessageEntity,
    Poll,
    PollOption,
    ReactionTypeCustomEmoji,
    ReactionTypeEmoji,
    ReplyParameters,
    SentWebAppMessage,
    ShippingOption,
    Update,
    User,
    WebAppInfo,
)
from telegram._utils.datetime import UTC, from_timestamp, to_timestamp
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.strings import to_camel_case
from telegram.constants import (
    ChatAction,
    InlineQueryLimit,
    InlineQueryResultType,
    MenuButtonType,
    ParseMode,
    ReactionEmoji,
)
from telegram.error import BadRequest, EndPointNotFound, InvalidToken, NetworkError
from telegram.ext import ExtBot, InvalidCallbackData
from telegram.helpers import escape_markdown
from telegram.request import BaseRequest, HTTPXRequest, RequestData
from telegram.warnings import PTBDeprecationWarning, PTBUserWarning
from tests.auxil.bot_method_checks import check_defaults_handling
from tests.auxil.ci_bots import FALLBACKS
from tests.auxil.envvars import GITHUB_ACTION, TEST_WITH_OPT_DEPS
from tests.auxil.files import data_file
from tests.auxil.networking import expect_bad_request
from tests.auxil.pytest_classes import PytestBot, PytestExtBot, make_bot
from tests.auxil.slots import mro_slots

from ._files.test_photo import photo_file
from .auxil.build_messages import make_message


@pytest.fixture()
async def message(bot, chat_id):  # mostly used in tests for edit_message
    out = await bot.send_message(
        chat_id, "Text", disable_web_page_preview=True, disable_notification=True
    )
    out._unfreeze()
    return out


@pytest.fixture(scope="module")
async def media_message(bot, chat_id):
    with data_file("telegram.ogg").open("rb") as f:
        return await bot.send_voice(chat_id, voice=f, caption="my caption", read_timeout=10)


@pytest.fixture(scope="module")
def chat_permissions():
    return ChatPermissions(can_send_messages=False, can_change_info=False, can_invite_users=False)


def inline_results_callback(page=None):
    if not page:
        return [InlineQueryResultArticle(i, str(i), None) for i in range(1, 254)]
    if page <= 5:
        return [
            InlineQueryResultArticle(i, str(i), None)
            for i in range(page * 5 + 1, (page + 1) * 5 + 1)
        ]
    return None


@pytest.fixture(scope="module")
def inline_results():
    return inline_results_callback()


BASE_GAME_SCORE = 60  # Base game score for game tests

xfail = pytest.mark.xfail(
    bool(GITHUB_ACTION),  # This condition is only relevant for github actions game tests.
    reason=(
        "Can fail due to race conditions when multiple test suites "
        "with the same bot token are run at the same time"
    ),
)


def bot_methods(ext_bot=True, include_camel_case=False, include_do_api_request=False):
    arg_values = []
    ids = []
    non_api_methods = [
        "de_json",
        "de_list",
        "to_dict",
        "to_json",
        "parse_data",
        "get_bot",
        "set_bot",
        "initialize",
        "shutdown",
        "insert_callback_data",
    ]
    if not include_do_api_request:
        non_api_methods.append("do_api_request")

    classes = (Bot, ExtBot) if ext_bot else (Bot,)
    for cls in classes:
        for name, attribute in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith("_") or name in non_api_methods:
                continue
            if not include_camel_case and any(x.isupper() for x in name):
                continue
            arg_values.append((cls, name, attribute))
            ids.append(f"{cls.__name__}.{name}")

    return pytest.mark.parametrize(
        argnames="bot_class, bot_method_name,bot_method", argvalues=arg_values, ids=ids
    )


class InputMessageContentLPO(InputMessageContent):
    """
    This is here to cover the case of InputMediaContent classes in testing answer_ilq that have
    `link_preview_options` but not `parse_mode`. Unlikely to ever happen, but better be save
    than sorry …
    """

    __slots__ = ("entities", "link_preview_options", "message_text", "parse_mode")

    def __init__(
        self,
        message_text: str,
        link_preview_options=DEFAULT_NONE,
        *,
        api_kwargs=None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self._unfreeze()
        self.message_text = message_text
        self.link_preview_options = link_preview_options


class TestBotWithoutRequest:
    """
    Most are executed on tg.ext.ExtBot, as that class only extends the functionality of tg.bot

    Behavior for init of ExtBot with missing optional dependency cachetools (for CallbackDataCache)
    is tested in `test_callbackdatacache`
    """

    test_flag = None

    @pytest.fixture(autouse=True)
    def _reset(self):
        self.test_flag = None

    @pytest.mark.parametrize("bot_class", [Bot, ExtBot])
    def test_slot_behaviour(self, bot_class, bot):
        inst = bot_class(bot.token)
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    async def test_no_token_passed(self):
        with pytest.raises(InvalidToken, match="You must pass the token"):
            Bot("")

    async def test_repr(self):
        bot = Bot(token="some_token", base_file_url="")
        assert repr(bot) == "Bot[token=some_token]"

    async def test_to_dict(self, bot):
        to_dict_bot = bot.to_dict()

        assert isinstance(to_dict_bot, dict)
        assert to_dict_bot["id"] == bot.id
        assert to_dict_bot["username"] == bot.username
        assert to_dict_bot["first_name"] == bot.first_name
        if bot.last_name:
            assert to_dict_bot["last_name"] == bot.last_name

    async def test_initialize_and_shutdown(self, bot: PytestExtBot, monkeypatch):
        async def initialize(*args, **kwargs):
            self.test_flag = ["initialize"]

        async def stop(*args, **kwargs):
            self.test_flag.append("stop")

        temp_bot = PytestBot(token=bot.token)
        orig_stop = temp_bot.request.shutdown

        try:
            monkeypatch.setattr(temp_bot.request, "initialize", initialize)
            monkeypatch.setattr(temp_bot.request, "shutdown", stop)
            await temp_bot.initialize()
            assert self.test_flag == ["initialize"]
            assert temp_bot.bot == bot.bot

            await temp_bot.shutdown()
            assert self.test_flag == ["initialize", "stop"]
        finally:
            await orig_stop()

    async def test_multiple_inits_and_shutdowns(self, bot, monkeypatch):
        self.received = defaultdict(int)

        async def initialize(*args, **kwargs):
            self.received["init"] += 1

        async def shutdown(*args, **kwargs):
            self.received["shutdown"] += 1

        monkeypatch.setattr(HTTPXRequest, "initialize", initialize)
        monkeypatch.setattr(HTTPXRequest, "shutdown", shutdown)

        test_bot = PytestBot(bot.token)
        await test_bot.initialize()
        await test_bot.initialize()
        await test_bot.initialize()
        await test_bot.shutdown()
        await test_bot.shutdown()
        await test_bot.shutdown()

        # 2 instead of 1 since we have to request objects for each bot
        assert self.received["init"] == 2
        assert self.received["shutdown"] == 2

    async def test_context_manager(self, monkeypatch, bot):
        async def initialize():
            self.test_flag = ["initialize"]

        async def shutdown(*args):
            self.test_flag.append("stop")

        monkeypatch.setattr(bot, "initialize", initialize)
        monkeypatch.setattr(bot, "shutdown", shutdown)

        async with bot:
            pass

        assert self.test_flag == ["initialize", "stop"]

    async def test_context_manager_exception_on_init(self, monkeypatch, bot):
        async def initialize():
            raise RuntimeError("initialize")

        async def shutdown():
            self.test_flag = "stop"

        monkeypatch.setattr(bot, "initialize", initialize)
        monkeypatch.setattr(bot, "shutdown", shutdown)

        with pytest.raises(RuntimeError, match="initialize"):
            async with bot:
                pass

        assert self.test_flag == "stop"

    async def test_equality(self):
        async with make_bot(token=FALLBACKS[0]["token"]) as a, make_bot(
            token=FALLBACKS[0]["token"]
        ) as b, Bot(token=FALLBACKS[0]["token"]) as c, make_bot(token=FALLBACKS[1]["token"]) as d:
            e = Update(123456789)
            f = Bot(token=FALLBACKS[0]["token"])

            assert a == b
            assert hash(a) == hash(b)
            assert a is not b

            assert a == c
            assert hash(a) == hash(c)

            assert a != d
            assert hash(a) != hash(d)

            assert a != e
            assert hash(a) != hash(e)

            # We cant check equality for unintialized Bot object
            assert hash(a) != hash(f)

    @pytest.mark.parametrize(
        "attribute",
        [
            "id",
            "username",
            "first_name",
            "last_name",
            "name",
            "can_join_groups",
            "can_read_all_group_messages",
            "supports_inline_queries",
            "link",
        ],
    )
    async def test_get_me_and_properties_not_initialized(self, bot: Bot, attribute):
        bot = Bot(token=bot.token)
        try:
            with pytest.raises(RuntimeError, match="not properly initialized"):
                bot[attribute]
        finally:
            await bot.shutdown()

    async def test_get_me_and_properties(self, bot):
        get_me_bot = await ExtBot(bot.token).get_me()

        assert isinstance(get_me_bot, User)
        assert get_me_bot.id == bot.id
        assert get_me_bot.username == bot.username
        assert get_me_bot.first_name == bot.first_name
        assert get_me_bot.last_name == bot.last_name
        assert get_me_bot.name == bot.name
        assert get_me_bot.can_join_groups == bot.can_join_groups
        assert get_me_bot.can_read_all_group_messages == bot.can_read_all_group_messages
        assert get_me_bot.supports_inline_queries == bot.supports_inline_queries
        assert f"https://t.me/{get_me_bot.username}" == bot.link

    def test_bot_pickling_error(self, bot):
        with pytest.raises(pickle.PicklingError, match="Bot objects cannot be pickled"):
            pickle.dumps(bot)

    def test_bot_deepcopy_error(self, bot):
        with pytest.raises(TypeError, match="Bot objects cannot be deepcopied"):
            copy.deepcopy(bot)

    @bot_methods(ext_bot=False)
    def test_api_methods_have_log_decorator(self, bot_class, bot_method_name, bot_method):
        """Check that all bot methods have the log decorator ..."""
        # not islower() skips the camelcase aliases
        if not bot_method_name.islower():
            return
        source = inspect.getsource(bot_method)
        assert (
            # Use re.match to only match at *the beginning* of the string
            re.match(rf"\s*\@\_log\s*async def {bot_method_name}", source)
        ), f"{bot_method_name} is missing the @_log decorator"

    @pytest.mark.parametrize(
        ("cls", "logger_name"), [(Bot, "telegram.Bot"), (ExtBot, "telegram.ext.ExtBot")]
    )
    async def test_log_decorator(self, bot: PytestExtBot, cls, logger_name, caplog):
        # Second argument makes sure that we ignore logs from e.g. httpx
        with caplog.at_level(logging.DEBUG, logger="telegram"):
            await cls(bot.token).get_me()
            # Only for stabilizing this test-
            if len(caplog.records) == 4:
                for idx, record in enumerate(caplog.records):
                    print(record)
                    if record.getMessage().startswith("Task was destroyed but it is pending"):
                        caplog.records.pop(idx)
                    if record.getMessage().startswith("Task exception was never retrieved"):
                        caplog.records.pop(idx)
            assert len(caplog.records) == 3

            assert all(caplog.records[i].name == logger_name for i in [-1, 0])
            assert caplog.records[0].getMessage().startswith("Entering: get_me")
            assert caplog.records[-1].getMessage().startswith("Exiting: get_me")

    @bot_methods()
    def test_camel_case_aliases(self, bot_class, bot_method_name, bot_method):
        camel_case_name = to_camel_case(bot_method_name)
        camel_case_function = getattr(bot_class, camel_case_name, False)
        assert camel_case_function is not False, f"{camel_case_name} not found"
        assert camel_case_function is bot_method, f"{camel_case_name} is not {bot_method}"

    @bot_methods(include_do_api_request=True)
    def test_coroutine_functions(self, bot_class, bot_method_name, bot_method):
        """Check that all bot methods are defined as async def  ..."""
        meth = getattr(bot_method, "__wrapped__", bot_method)  # to unwrap the @_log decorator
        assert inspect.iscoroutinefunction(meth), f"{bot_method_name} must be a coroutine function"

    @bot_methods(include_do_api_request=True)
    def test_api_kwargs_and_timeouts_present(self, bot_class, bot_method_name, bot_method):
        """Check that all bot methods have `api_kwargs` and timeout params."""
        param_names = inspect.signature(bot_method).parameters.keys()
        params = ("pool_timeout", "read_timeout", "connect_timeout", "write_timeout", "api_kwargs")

        for param in params:
            assert param in param_names, f"{bot_method_name} is missing the parameter `{param}`"

        rate_arg = "rate_limit_args"
        if bot_method_name.replace("_", "").lower() != "getupdates" and bot_class is ExtBot:
            assert rate_arg in param_names, f"{bot_method} is missing the parameter `{rate_arg}`"

    @bot_methods(ext_bot=False)
    async def test_defaults_handling(
        self,
        bot_class,
        bot_method_name: str,
        bot_method,
        bot: PytestExtBot,
        raw_bot: PytestBot,
    ):
        """
        Here we check that the bot methods handle tg.ext.Defaults correctly. This has two parts:

        1. Check that ExtBot actually inserts the defaults values correctly
        2. Check that tg.Bot just replaces `DefaultValue(obj)` with `obj`, i.e. that it doesn't
            pass any `DefaultValue` instances to Request. See the docstring of
            tg.Bot._insert_defaults for details on why we need that

        As for most defaults,
        we can't really check the effect, we just check if we're passing the correct kwargs to
        Request.post. As bot method tests a scattered across the different test files, we do
        this here in one place.

        The same test is also run for all the shortcuts (Message.reply_text) etc in the
        corresponding tests.

        Finally, there are some tests for Defaults.{parse_mode, quote, allow_sending_without_reply}
        at the appropriate places, as those are the only things we can actually check.
        """
        # Mocking get_me within check_defaults_handling messes with the cached values like
        # Bot.{bot, username, id, …}` unless we return the expected User object.
        return_value = bot.bot if bot_method_name.lower().replace("_", "") == "getme" else None

        # Check that ExtBot does the right thing
        bot_method = getattr(bot, bot_method_name)
        raw_bot_method = getattr(raw_bot, bot_method_name)
        assert await check_defaults_handling(bot_method, bot, return_value=return_value)
        assert await check_defaults_handling(raw_bot_method, raw_bot, return_value=return_value)

    @pytest.mark.parametrize(
        ("name", "method"), inspect.getmembers(Bot, predicate=inspect.isfunction)
    )
    def test_ext_bot_signature(self, name, method):
        """
        Here we make sure that all methods of ext.ExtBot have the same signature as the
        corresponding methods of tg.Bot.
        """
        # Some methods of ext.ExtBot
        global_extra_args = {"rate_limit_args"}
        extra_args_per_method = defaultdict(
            set, {"__init__": {"arbitrary_callback_data", "defaults", "rate_limiter"}}
        )
        different_hints_per_method = defaultdict(set, {"__setattr__": {"ext_bot"}})

        signature = inspect.signature(method)
        ext_signature = inspect.signature(getattr(ExtBot, name))

        assert (
            ext_signature.return_annotation == signature.return_annotation
        ), f"Wrong return annotation for method {name}"
        assert (
            set(signature.parameters)
            == set(ext_signature.parameters) - global_extra_args - extra_args_per_method[name]
        ), f"Wrong set of parameters for method {name}"
        for param_name, param in signature.parameters.items():
            if param_name in different_hints_per_method[name]:
                continue
            assert (
                param.annotation == ext_signature.parameters[param_name].annotation
            ), f"Wrong annotation for parameter {param_name} of method {name}"
            assert (
                param.default == ext_signature.parameters[param_name].default
            ), f"Wrong default value for parameter {param_name} of method {name}"
            assert (
                param.kind == ext_signature.parameters[param_name].kind
            ), f"Wrong parameter kind for parameter {param_name} of method {name}"

    async def test_unknown_kwargs(self, bot, monkeypatch):
        async def post(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            if not all([data["unknown_kwarg_1"] == "7", data["unknown_kwarg_2"] == "5"]):
                pytest.fail("got wrong parameters")
            return True

        monkeypatch.setattr(bot.request, "post", post)
        await bot.send_message(
            123, "text", api_kwargs={"unknown_kwarg_1": 7, "unknown_kwarg_2": 5}
        )

    async def test_answer_web_app_query(self, bot, raw_bot, monkeypatch):
        params = False

        # For now just test that our internals pass the correct data

        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            nonlocal params
            params = request_data.parameters == {
                "web_app_query_id": "12345",
                "result": {
                    "title": "title",
                    "input_message_content": {
                        "message_text": "text",
                    },
                    "type": InlineQueryResultType.ARTICLE,
                    "id": "1",
                },
            }
            return SentWebAppMessage("321").to_dict()

        # We test different result types more thoroughly for answer_inline_query, so we just
        # use the one type here
        result = InlineQueryResultArticle("1", "title", InputTextMessageContent("text"))
        copied_result = copy.copy(result)

        ext_bot = bot
        for bot in (ext_bot, raw_bot):
            # We need to test 1) below both the bot and raw_bot and setting this up with
            # pytest.parametrize appears to be difficult ...
            monkeypatch.setattr(bot.request, "post", make_assertion)
            web_app_msg = await bot.answer_web_app_query("12345", result)
            assert params, "something went wrong with passing arguments to the request"
            assert isinstance(web_app_msg, SentWebAppMessage)
            assert web_app_msg.inline_message_id == "321"

            # 1)
            # make sure that the results were not edited in-place
            assert result == copied_result
            assert (
                result.input_message_content.parse_mode
                == copied_result.input_message_content.parse_mode
            )

    @pytest.mark.parametrize(
        "default_bot",
        [{"parse_mode": "Markdown", "disable_web_page_preview": True}],
        indirect=True,
    )
    @pytest.mark.parametrize(
        ("ilq_result", "expected_params"),
        [
            (
                InlineQueryResultArticle("1", "title", InputTextMessageContent("text")),
                {
                    "web_app_query_id": "12345",
                    "result": {
                        "title": "title",
                        "input_message_content": {
                            "message_text": "text",
                            "parse_mode": "Markdown",
                            "link_preview_options": {
                                "is_disabled": True,
                            },
                        },
                        "type": InlineQueryResultType.ARTICLE,
                        "id": "1",
                    },
                },
            ),
            (
                InlineQueryResultArticle(
                    "1",
                    "title",
                    InputTextMessageContent(
                        "text", parse_mode="HTML", disable_web_page_preview=False
                    ),
                ),
                {
                    "web_app_query_id": "12345",
                    "result": {
                        "title": "title",
                        "input_message_content": {
                            "message_text": "text",
                            "parse_mode": "HTML",
                            "link_preview_options": {
                                "is_disabled": False,
                            },
                        },
                        "type": InlineQueryResultType.ARTICLE,
                        "id": "1",
                    },
                },
            ),
            (
                InlineQueryResultArticle(
                    "1",
                    "title",
                    InputTextMessageContent(
                        "text", parse_mode=None, disable_web_page_preview="False"
                    ),
                ),
                {
                    "web_app_query_id": "12345",
                    "result": {
                        "title": "title",
                        "input_message_content": {
                            "message_text": "text",
                            "link_preview_options": {
                                "is_disabled": "False",
                            },
                        },
                        "type": InlineQueryResultType.ARTICLE,
                        "id": "1",
                    },
                },
            ),
        ],
    )
    async def test_answer_web_app_query_defaults(
        self, default_bot, ilq_result, expected_params, monkeypatch
    ):
        bot = default_bot
        params = False

        # For now just test that our internals pass the correct data

        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            nonlocal params
            params = request_data.parameters == expected_params
            return SentWebAppMessage("321").to_dict()

        monkeypatch.setattr(bot.request, "post", make_assertion)

        # We test different result types more thoroughly for answer_inline_query, so we just
        # use the one type here
        copied_result = copy.copy(ilq_result)

        web_app_msg = await bot.answer_web_app_query("12345", ilq_result)
        assert params, "something went wrong with passing arguments to the request"
        assert isinstance(web_app_msg, SentWebAppMessage)
        assert web_app_msg.inline_message_id == "321"

        # make sure that the results were not edited in-place
        assert ilq_result == copied_result
        assert (
            ilq_result.input_message_content.parse_mode
            == copied_result.input_message_content.parse_mode
        )

    # TODO: Needs improvement. We need incoming inline query to test answer.
    @pytest.mark.parametrize("button_type", ["start", "web_app"])
    async def test_answer_inline_query(self, monkeypatch, bot, raw_bot, button_type):
        # For now just test that our internals pass the correct data
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            expected = {
                "cache_time": 300,
                "results": [
                    {
                        "title": "first",
                        "id": "11",
                        "type": "article",
                        "input_message_content": {"message_text": "first"},
                    },
                    {
                        "title": "second",
                        "id": "12",
                        "type": "article",
                        "input_message_content": {"message_text": "second"},
                    },
                    {
                        "title": "test_result",
                        "id": "123",
                        "type": "document",
                        "document_url": (
                            "https://raw.githubusercontent.com/python-telegram-bot"
                            "/logos/master/logo/png/ptb-logo_240.png"
                        ),
                        "mime_type": "image/png",
                        "caption": "ptb_logo",
                        "input_message_content": {"message_text": "imc"},
                    },
                ],
                "next_offset": "42",
                "inline_query_id": 1234,
                "is_personal": True,
            }

            if button_type == "start":
                button_dict = {"text": "button_text", "start_parameter": "start_parameter"}
            else:
                button_dict = {
                    "text": "button_text",
                    "web_app": {"url": "https://python-telegram-bot.org"},
                }

            expected["button"] = button_dict

            return request_data.parameters == expected

        results = [
            InlineQueryResultArticle("11", "first", InputTextMessageContent("first")),
            InlineQueryResultArticle("12", "second", InputMessageContentLPO("second")),
            InlineQueryResultDocument(
                id="123",
                document_url=(
                    "https://raw.githubusercontent.com/python-telegram-bot/logos/master/"
                    "logo/png/ptb-logo_240.png"
                ),
                title="test_result",
                mime_type="image/png",
                caption="ptb_logo",
                input_message_content=InputMessageContentLPO("imc"),
            ),
        ]

        if button_type == "start":
            button = InlineQueryResultsButton(
                text="button_text", start_parameter="start_parameter"
            )
        elif button_type == "web_app":
            button = InlineQueryResultsButton(
                text="button_text", web_app=WebAppInfo("https://python-telegram-bot.org")
            )
        else:
            button = None

        copied_results = copy.copy(results)
        ext_bot = bot
        for bot in (ext_bot, raw_bot):
            # We need to test 1) below both the bot and raw_bot and setting this up with
            # pytest.parametrize appears to be difficult ...
            monkeypatch.setattr(bot.request, "post", make_assertion)
            assert await bot.answer_inline_query(
                1234,
                results=results,
                cache_time=300,
                is_personal=True,
                next_offset="42",
                button=button,
            )

            # 1)
            # make sure that the results were not edited in-place
            assert results == copied_results
            for idx, result in enumerate(results):
                if hasattr(result, "parse_mode"):
                    assert result.parse_mode == copied_results[idx].parse_mode
                if hasattr(result, "input_message_content"):
                    assert getattr(result.input_message_content, "parse_mode", None) == getattr(
                        copied_results[idx].input_message_content, "parse_mode", None
                    )
                    assert getattr(
                        result.input_message_content, "disable_web_page_preview", None
                    ) == getattr(
                        copied_results[idx].input_message_content, "disable_web_page_preview", None
                    )

            monkeypatch.delattr(bot.request, "post")

    async def test_answer_inline_query_no_default_parse_mode(self, monkeypatch, bot):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters == {
                "cache_time": 300,
                "results": [
                    {
                        "title": "first",
                        "id": "11",
                        "type": "article",
                        "input_message_content": {"message_text": "first"},
                    },
                    {
                        "title": "second",
                        "id": "12",
                        "type": "article",
                        "input_message_content": {"message_text": "second"},
                    },
                    {
                        "title": "test_result",
                        "id": "123",
                        "type": "document",
                        "document_url": (
                            "https://raw.githubusercontent.com/"
                            "python-telegram-bot/logos/master/logo/png/"
                            "ptb-logo_240.png"
                        ),
                        "mime_type": "image/png",
                        "caption": "ptb_logo",
                        "input_message_content": {"message_text": "imc"},
                    },
                ],
                "next_offset": "42",
                "inline_query_id": 1234,
                "is_personal": True,
            }

        monkeypatch.setattr(bot.request, "post", make_assertion)
        results = [
            InlineQueryResultArticle("11", "first", InputTextMessageContent("first")),
            InlineQueryResultArticle("12", "second", InputMessageContentLPO("second")),
            InlineQueryResultDocument(
                id="123",
                document_url=(
                    "https://raw.githubusercontent.com/python-telegram-bot/logos/master/"
                    "logo/png/ptb-logo_240.png"
                ),
                title="test_result",
                mime_type="image/png",
                caption="ptb_logo",
                input_message_content=InputMessageContentLPO("imc"),
            ),
        ]

        copied_results = copy.copy(results)
        assert await bot.answer_inline_query(
            1234,
            results=results,
            cache_time=300,
            is_personal=True,
            next_offset="42",
        )
        # make sure that the results were not edited in-place
        assert results == copied_results
        for idx, result in enumerate(results):
            if hasattr(result, "parse_mode"):
                assert result.parse_mode == copied_results[idx].parse_mode
            if hasattr(result, "input_message_content"):
                assert getattr(result.input_message_content, "parse_mode", None) == getattr(
                    copied_results[idx].input_message_content, "parse_mode", None
                )
                assert getattr(
                    result.input_message_content, "disable_web_page_preview", None
                ) == getattr(
                    copied_results[idx].input_message_content, "disable_web_page_preview", None
                )

    @pytest.mark.parametrize(
        "default_bot",
        [{"parse_mode": "Markdown", "disable_web_page_preview": True}],
        indirect=True,
    )
    async def test_answer_inline_query_default_parse_mode(self, monkeypatch, default_bot):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters == {
                "cache_time": 300,
                "results": [
                    {
                        "title": "first",
                        "id": "11",
                        "type": InlineQueryResultType.ARTICLE,
                        "input_message_content": {
                            "message_text": "first",
                            "parse_mode": "Markdown",
                            "link_preview_options": {
                                "is_disabled": True,
                            },
                        },
                    },
                    {
                        "title": "second",
                        "id": "12",
                        "type": InlineQueryResultType.ARTICLE,
                        "input_message_content": {
                            "message_text": "second",
                            "link_preview_options": {
                                "is_disabled": True,
                            },
                        },
                    },
                    {
                        "title": "test_result",
                        "id": "123",
                        "type": InlineQueryResultType.DOCUMENT,
                        "document_url": (
                            "https://raw.githubusercontent.com/"
                            "python-telegram-bot/logos/master/logo/png/"
                            "ptb-logo_240.png"
                        ),
                        "mime_type": "image/png",
                        "caption": "ptb_logo",
                        "parse_mode": "Markdown",
                        "input_message_content": {
                            "message_text": "imc",
                            "link_preview_options": {
                                "is_disabled": True,
                            },
                            "parse_mode": "Markdown",
                        },
                    },
                ],
                "next_offset": "42",
                "inline_query_id": 1234,
                "is_personal": True,
            }

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        results = [
            InlineQueryResultArticle("11", "first", InputTextMessageContent("first")),
            InlineQueryResultArticle("12", "second", InputMessageContentLPO("second")),
            InlineQueryResultDocument(
                id="123",
                document_url=(
                    "https://raw.githubusercontent.com/python-telegram-bot/logos/master/"
                    "logo/png/ptb-logo_240.png"
                ),
                title="test_result",
                mime_type="image/png",
                caption="ptb_logo",
                input_message_content=InputTextMessageContent("imc"),
            ),
        ]

        copied_results = copy.copy(results)
        assert await default_bot.answer_inline_query(
            1234,
            results=results,
            cache_time=300,
            is_personal=True,
            next_offset="42",
        )
        # make sure that the results were not edited in-place
        assert results == copied_results
        for idx, result in enumerate(results):
            if hasattr(result, "parse_mode"):
                assert result.parse_mode == copied_results[idx].parse_mode
            if hasattr(result, "input_message_content"):
                assert getattr(result.input_message_content, "parse_mode", None) == getattr(
                    copied_results[idx].input_message_content, "parse_mode", None
                )
                assert getattr(
                    result.input_message_content, "disable_web_page_preview", None
                ) == getattr(
                    copied_results[idx].input_message_content, "disable_web_page_preview", None
                )

    @pytest.mark.parametrize(
        ("current_offset", "num_results", "id_offset", "expected_next_offset"),
        [
            ("", InlineQueryLimit.RESULTS, 1, 1),
            (1, InlineQueryLimit.RESULTS, 51, 2),
            (5, 3, 251, ""),
        ],
    )
    async def test_answer_inline_query_current_offset_1(
        self,
        monkeypatch,
        bot,
        inline_results,
        current_offset,
        num_results,
        id_offset,
        expected_next_offset,
    ):
        # For now just test that our internals pass the correct data
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            results = data["results"]
            length_matches = len(results) == num_results
            ids_match = all(int(res["id"]) == id_offset + i for i, res in enumerate(results))
            next_offset_matches = data["next_offset"] == str(expected_next_offset)
            return length_matches and ids_match and next_offset_matches

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.answer_inline_query(
            1234, results=inline_results, current_offset=current_offset
        )

    async def test_answer_inline_query_current_offset_2(self, monkeypatch, bot, inline_results):
        # For now just test that our internals pass the correct data
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            results = data["results"]
            length_matches = len(results) == InlineQueryLimit.RESULTS
            ids_match = all(int(res["id"]) == 1 + i for i, res in enumerate(results))
            next_offset_matches = data["next_offset"] == "1"
            return length_matches and ids_match and next_offset_matches

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.answer_inline_query(1234, results=inline_results, current_offset=0)

        inline_results = inline_results[:30]

        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            results = data["results"]
            length_matches = len(results) == 30
            ids_match = all(int(res["id"]) == 1 + i for i, res in enumerate(results))
            next_offset_matches = not data["next_offset"]
            return length_matches and ids_match and next_offset_matches

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.answer_inline_query(1234, results=inline_results, current_offset=0)

    async def test_answer_inline_query_current_offset_callback(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            results = data["results"]
            length = len(results) == 5
            ids = all(int(res["id"]) == 6 + i for i, res in enumerate(results))
            next_offset = data["next_offset"] == "2"
            return length and ids and next_offset

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.answer_inline_query(
            1234, results=inline_results_callback, current_offset=1
        )

        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            results = data["results"]
            length = results == []
            next_offset = not data["next_offset"]
            return length and next_offset

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.answer_inline_query(
            1234, results=inline_results_callback, current_offset=6
        )

    async def test_send_edit_message_mutually_exclusive_link_preview(self, bot, chat_id):
        """Test that link_preview is mutually exclusive with disable_web_page_preview."""
        with pytest.raises(ValueError, match="`link_preview_options` are mutually exclusive"):
            await bot.send_message(
                chat_id, "text", disable_web_page_preview=True, link_preview_options="something"
            )

        with pytest.raises(ValueError, match="`link_preview_options` are mutually exclusive"):
            await bot.edit_message_text(
                "text", chat_id, 1, disable_web_page_preview=True, link_preview_options="something"
            )

    async def test_rtm_aswr_mutually_exclusive_reply_parameters(self, bot, chat_id):
        """Test that reply_to_message_id and allow_sending_without_reply are mutually exclusive
        with reply_parameters."""
        with pytest.raises(ValueError, match="`reply_to_message_id` and"):
            await bot.send_message(chat_id, "text", reply_to_message_id=1, reply_parameters=True)

        with pytest.raises(ValueError, match="`allow_sending_without_reply` and"):
            await bot.send_message(
                chat_id, "text", allow_sending_without_reply=True, reply_parameters=True
            )

        # Test with copy message
        with pytest.raises(ValueError, match="`reply_to_message_id` and"):
            await bot.copy_message(
                chat_id, chat_id, 1, reply_to_message_id=1, reply_parameters=True
            )

        with pytest.raises(ValueError, match="`allow_sending_without_reply` and"):
            await bot.copy_message(
                chat_id, chat_id, 1, allow_sending_without_reply=True, reply_parameters=True
            )

        # Test with send media group
        media = InputMediaPhoto(photo_file)
        with pytest.raises(ValueError, match="`reply_to_message_id` and"):
            await bot.send_media_group(
                chat_id, media, reply_to_message_id=1, reply_parameters=True
            )

        with pytest.raises(ValueError, match="`allow_sending_without_reply` and"):
            await bot.send_media_group(
                chat_id, media, allow_sending_without_reply=True, reply_parameters=True
            )

    # get_file is tested multiple times in the test_*media* modules.
    # Here we only test the behaviour for bot apis in local mode
    async def test_get_file_local_mode(self, bot, monkeypatch):
        path = str(data_file("game.gif"))

        async def make_assertion(*args, **kwargs):
            return {
                "file_id": None,
                "file_unique_id": None,
                "file_size": None,
                "file_path": path,
            }

        monkeypatch.setattr(bot, "_post", make_assertion)

        resulting_path = (await bot.get_file("file_id")).file_path
        assert bot.token not in resulting_path
        assert resulting_path == path

    # TODO: Needs improvement. No feasible way to test until bots can add members.
    async def test_ban_chat_member(self, monkeypatch, bot):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            chat_id = data["chat_id"] == "2"
            user_id = data["user_id"] == "32"
            until_date = data.get("until_date", "1577887200") == "1577887200"
            revoke_msgs = data.get("revoke_messages", "true") == "true"
            return chat_id and user_id and until_date and revoke_msgs

        monkeypatch.setattr(bot.request, "post", make_assertion)
        until = from_timestamp(1577887200)

        assert await bot.ban_chat_member(2, 32)
        assert await bot.ban_chat_member(2, 32, until_date=until)
        assert await bot.ban_chat_member(2, 32, until_date=1577887200)
        assert await bot.ban_chat_member(2, 32, revoke_messages=True)

    async def test_ban_chat_member_default_tz(self, monkeypatch, tz_bot):
        until = dtm.datetime(2020, 1, 11, 16, 13)
        until_timestamp = to_timestamp(until, tzinfo=tz_bot.defaults.tzinfo)

        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            chat_id = data["chat_id"] == 2
            user_id = data["user_id"] == 32
            until_date = data.get("until_date", until_timestamp) == until_timestamp
            return chat_id and user_id and until_date

        monkeypatch.setattr(tz_bot.request, "post", make_assertion)

        assert await tz_bot.ban_chat_member(2, 32)
        assert await tz_bot.ban_chat_member(2, 32, until_date=until)
        assert await tz_bot.ban_chat_member(2, 32, until_date=until_timestamp)

    async def test_ban_chat_sender_chat(self, monkeypatch, bot):
        # For now, we just test that we pass the correct data to TG
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            chat_id = data["chat_id"] == 2
            sender_chat_id = data["sender_chat_id"] == 32
            return chat_id and sender_chat_id

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.ban_chat_sender_chat(2, 32)

    # TODO: Needs improvement.
    @pytest.mark.parametrize("only_if_banned", [True, False, None])
    async def test_unban_chat_member(self, monkeypatch, bot, only_if_banned):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            chat_id = data["chat_id"] == 2
            user_id = data["user_id"] == 32
            o_i_b = data.get("only_if_banned", None) == only_if_banned
            return chat_id and user_id and o_i_b

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.unban_chat_member(2, 32, only_if_banned=only_if_banned)

    async def test_unban_chat_sender_chat(self, monkeypatch, bot):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            chat_id = data["chat_id"] == "2"
            sender_chat_id = data["sender_chat_id"] == "32"
            return chat_id and sender_chat_id

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.unban_chat_sender_chat(2, 32)

    async def test_set_chat_permissions(self, monkeypatch, bot, chat_permissions):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            chat_id = data["chat_id"] == "2"
            permissions = data["permissions"] == chat_permissions.to_json()
            use_independent_chat_permissions = data["use_independent_chat_permissions"]
            return chat_id and permissions and use_independent_chat_permissions

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.set_chat_permissions(2, chat_permissions, True)

    async def test_set_chat_administrator_custom_title(self, monkeypatch, bot):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            chat_id = data["chat_id"] == 2
            user_id = data["user_id"] == 32
            custom_title = data["custom_title"] == "custom_title"
            return chat_id and user_id and custom_title

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.set_chat_administrator_custom_title(2, 32, "custom_title")

    # TODO: Needs improvement. Need an incoming callbackquery to test
    async def test_answer_callback_query(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters == {
                "callback_query_id": 23,
                "show_alert": True,
                "url": "no_url",
                "cache_time": 1,
                "text": "answer",
            }

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.answer_callback_query(
            23, text="answer", show_alert=True, url="no_url", cache_time=1
        )

    @pytest.mark.parametrize("drop_pending_updates", [True, False])
    async def test_set_webhook_delete_webhook_drop_pending_updates(
        self, bot, drop_pending_updates, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            return data.get("drop_pending_updates") == drop_pending_updates

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.set_webhook("", drop_pending_updates=drop_pending_updates)
        assert await bot.delete_webhook(drop_pending_updates=drop_pending_updates)

    @pytest.mark.parametrize("local_file", ["str", "Path", False])
    async def test_set_webhook_params(self, bot, monkeypatch, local_file):
        # actually making calls to TG is done in
        # test_set_webhook_get_webhook_info_and_delete_webhook. Sadly secret_token can't be tested
        # there so we have this function \o/
        async def make_assertion(*args, **_):
            kwargs = args[1]

            if local_file is False:
                cert_assertion = (
                    kwargs["certificate"].input_file_content
                    == data_file("sslcert.pem").read_bytes()
                )
            else:
                cert_assertion = data_file("sslcert.pem").as_uri()

            return (
                kwargs["url"] == "example.com"
                and cert_assertion
                and kwargs["max_connections"] == 7
                and kwargs["allowed_updates"] == ["messages"]
                and kwargs["ip_address"] == "127.0.0.1"
                and kwargs["drop_pending_updates"]
                and kwargs["secret_token"] == "SoSecretToken"
            )

        monkeypatch.setattr(bot, "_post", make_assertion)

        cert_path = data_file("sslcert.pem")
        if local_file == "str":
            certificate = str(cert_path)
        elif local_file == "Path":
            certificate = cert_path
        else:
            certificate = cert_path.read_bytes()

        assert await bot.set_webhook(
            "example.com",
            certificate,
            7,
            ["messages"],
            "127.0.0.1",
            True,
            "SoSecretToken",
        )

    # TODO: Needs improvement. Need incoming shipping queries to test
    async def test_answer_shipping_query_ok(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters == {
                "shipping_query_id": 1,
                "ok": True,
                "shipping_options": [
                    {"title": "option1", "prices": [{"label": "price", "amount": 100}], "id": 1}
                ],
            }

        monkeypatch.setattr(bot.request, "post", make_assertion)
        shipping_options = ShippingOption(1, "option1", [LabeledPrice("price", 100)])
        assert await bot.answer_shipping_query(1, True, shipping_options=[shipping_options])

    async def test_answer_shipping_query_error_message(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters == {
                "shipping_query_id": 1,
                "error_message": "Not enough fish",
                "ok": False,
            }

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.answer_shipping_query(1, False, error_message="Not enough fish")

    # TODO: Needs improvement. Need incoming pre checkout queries to test
    async def test_answer_pre_checkout_query_ok(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters == {"pre_checkout_query_id": 1, "ok": True}

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.answer_pre_checkout_query(1, True)

    async def test_answer_pre_checkout_query_error_message(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters == {
                "pre_checkout_query_id": 1,
                "error_message": "Not enough fish",
                "ok": False,
            }

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.answer_pre_checkout_query(1, False, error_message="Not enough fish")

    async def test_restrict_chat_member(self, bot, chat_permissions, monkeypatch):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            chat_id = data["chat_id"] == "@chat"
            user_id = data["user_id"] == "2"
            permissions = data["permissions"] == chat_permissions.to_json()
            until_date = data["until_date"] == "200"
            use_independent_chat_permissions = data["use_independent_chat_permissions"]
            return (
                chat_id
                and user_id
                and permissions
                and until_date
                and use_independent_chat_permissions
            )

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.restrict_chat_member("@chat", 2, chat_permissions, 200, True)

    async def test_restrict_chat_member_default_tz(
        self, monkeypatch, tz_bot, channel_id, chat_permissions
    ):
        until = dtm.datetime(2020, 1, 11, 16, 13)
        until_timestamp = to_timestamp(until, tzinfo=tz_bot.defaults.tzinfo)

        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters.get("until_date", until_timestamp) == until_timestamp

        monkeypatch.setattr(tz_bot.request, "post", make_assertion)

        assert await tz_bot.restrict_chat_member(channel_id, 95205500, chat_permissions)
        assert await tz_bot.restrict_chat_member(
            channel_id, 95205500, chat_permissions, until_date=until
        )
        assert await tz_bot.restrict_chat_member(
            channel_id, 95205500, chat_permissions, until_date=until_timestamp
        )

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_set_chat_photo_local_files(self, monkeypatch, bot, chat_id, local_mode):
        try:
            bot._local_mode = local_mode
            # For just test that the correct paths are passed as we have no local bot API set up
            self.test_flag = False
            file = data_file("telegram.jpg")
            expected = file.as_uri()

            async def make_assertion(_, data, *args, **kwargs):
                if local_mode:
                    self.test_flag = data.get("photo") == expected
                else:
                    self.test_flag = isinstance(data.get("photo"), InputFile)

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.set_chat_photo(chat_id, file)
            assert self.test_flag
        finally:
            bot._local_mode = False

    async def test_timeout_propagation_explicit(self, monkeypatch, bot, chat_id):
        # Use BaseException that's not a subclass of Exception such that
        # OkException should not be caught anywhere
        class OkException(BaseException):
            pass

        timeout = 42

        async def do_request(*args, **kwargs):
            obj = kwargs.get("read_timeout")
            if obj == timeout:
                raise OkException

            return 200, b'{"ok": true, "result": []}'

        monkeypatch.setattr(bot.request, "do_request", do_request)

        # Test file uploading
        with pytest.raises(OkException):
            await bot.send_photo(
                chat_id, data_file("telegram.jpg").open("rb"), read_timeout=timeout
            )

        # Test JSON submission
        with pytest.raises(OkException):
            await bot.get_chat_administrators(chat_id, read_timeout=timeout)

    async def test_timeout_propagation_implicit(self, monkeypatch, bot, chat_id):
        # Use BaseException that's not a subclass of Exception such that
        # OkException should not be caught anywhere
        class OkException(BaseException):
            pass

        async def request(*args, **kwargs):
            timeout = kwargs.get("timeout")
            if timeout.write == 20:
                raise OkException

            return 200, b'{"ok": true, "result": []}'

        monkeypatch.setattr(httpx.AsyncClient, "request", request)

        # Test file uploading
        with pytest.raises(OkException):
            await bot.send_photo(chat_id, data_file("telegram.jpg").open("rb"))

    async def test_log_out(self, monkeypatch, bot):
        # We don't actually make a request as to not break the test setup
        async def assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters == {} and url.split("/")[-1] == "logOut"

        monkeypatch.setattr(bot.request, "post", assertion)

        assert await bot.log_out()

    async def test_close(self, monkeypatch, bot):
        # We don't actually make a request as to not break the test setup
        async def assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters == {} and url.split("/")[-1] == "close"

        monkeypatch.setattr(bot.request, "post", assertion)

        assert await bot.close()

    @pytest.mark.parametrize("json_keyboard", [True, False])
    @pytest.mark.parametrize("caption", ["<b>Test</b>", "", None])
    async def test_copy_message(
        self, monkeypatch, bot, chat_id, media_message, json_keyboard, caption
    ):
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="test", callback_data="test2")]]
        )

        async def post(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            if not all(
                [
                    data["chat_id"] == chat_id,
                    data["from_chat_id"] == chat_id,
                    data["message_id"] == media_message.message_id,
                    data.get("caption") == caption,
                    data["parse_mode"] == ParseMode.HTML,
                    data["reply_parameters"]
                    == ReplyParameters(message_id=media_message.message_id).to_dict(),
                    (
                        data["reply_markup"] == keyboard.to_json()
                        if json_keyboard
                        else keyboard.to_dict()
                    ),
                    data["disable_notification"] is True,
                    data["caption_entities"]
                    == [MessageEntity(MessageEntity.BOLD, 0, 4).to_dict()],
                    data["protect_content"] is True,
                    data["message_thread_id"] == 1,
                ]
            ):
                pytest.fail("I got wrong parameters in post")
            return data

        monkeypatch.setattr(bot.request, "post", post)
        await bot.copy_message(
            chat_id,
            from_chat_id=chat_id,
            message_id=media_message.message_id,
            caption=caption,
            caption_entities=[MessageEntity(MessageEntity.BOLD, 0, 4)],
            parse_mode=ParseMode.HTML,
            reply_to_message_id=media_message.message_id,
            reply_markup=keyboard.to_json() if json_keyboard else keyboard,
            disable_notification=True,
            protect_content=True,
            message_thread_id=1,
        )

    # In the following tests we check that get_updates inserts callback data correctly if necessary
    # The same must be done in the webhook updater. This is tested over at test_updater.py, but
    # here we test more extensively.

    @pytest.mark.parametrize(
        ("acd_in", "maxsize"),
        [(True, 1024), (False, 1024), (0, 0), (None, None)],
    )
    async def test_callback_data_maxsize(self, bot_info, acd_in, maxsize):
        async with make_bot(bot_info, arbitrary_callback_data=acd_in) as acd_bot:
            if acd_in is not False:
                assert acd_bot.callback_data_cache.maxsize == maxsize
            else:
                assert acd_bot.callback_data_cache is None

    async def test_arbitrary_callback_data_no_insert(self, monkeypatch, cdc_bot):
        """Updates that don't need insertion shouldn't fail obviously"""
        bot = cdc_bot

        async def post(*args, **kwargs):
            update = Update(
                17,
                poll=Poll(
                    "42",
                    "question",
                    options=[PollOption("option", 0)],
                    total_voter_count=0,
                    is_closed=False,
                    is_anonymous=True,
                    type=Poll.REGULAR,
                    allows_multiple_answers=False,
                ),
            )
            return [update.to_dict()]

        try:
            monkeypatch.setattr(BaseRequest, "post", post)
            updates = await bot.get_updates(timeout=1)

            assert len(updates) == 1
            assert updates[0].update_id == 17
            assert updates[0].poll.id == "42"
        finally:
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    @pytest.mark.parametrize(
        "message_type", ["channel_post", "edited_channel_post", "message", "edited_message"]
    )
    async def test_arbitrary_callback_data_pinned_message_reply_to_message(
        self, cdc_bot, monkeypatch, message_type
    ):
        bot = cdc_bot

        reply_markup = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="text", callback_data="callback_data")
        )

        message = Message(
            1,
            dtm.datetime.utcnow(),
            None,
            reply_markup=bot.callback_data_cache.process_keyboard(reply_markup),
        )
        message._unfreeze()
        # We do to_dict -> de_json to make sure those aren't the same objects
        message.pinned_message = Message.de_json(message.to_dict(), bot)

        async def post(*args, **kwargs):
            update = Update(
                17,
                **{
                    message_type: Message(
                        1,
                        dtm.datetime.utcnow(),
                        None,
                        pinned_message=message,
                        reply_to_message=Message.de_json(message.to_dict(), bot),
                    )
                },
            )
            return [update.to_dict()]

        try:
            monkeypatch.setattr(BaseRequest, "post", post)
            updates = await bot.get_updates(timeout=1)

            assert isinstance(updates, tuple)
            assert len(updates) == 1

            effective_message = updates[0][message_type]
            assert (
                effective_message.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data
                == "callback_data"
            )
            assert (
                effective_message.pinned_message.reply_markup.inline_keyboard[0][0].callback_data
                == "callback_data"
            )

            pinned_message = effective_message.reply_to_message.pinned_message
            assert (
                pinned_message.reply_markup.inline_keyboard[0][0].callback_data == "callback_data"
            )

        finally:
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    async def test_get_updates_invalid_callback_data(self, cdc_bot, monkeypatch):
        bot = cdc_bot

        async def post(*args, **kwargs):
            return [
                Update(
                    17,
                    callback_query=CallbackQuery(
                        id=1,
                        from_user=None,
                        chat_instance=123,
                        data="invalid data",
                        message=Message(
                            1,
                            from_user=User(1, "", False),
                            date=dtm.datetime.utcnow(),
                            chat=Chat(1, ""),
                            text="Webhook",
                        ),
                    ),
                ).to_dict()
            ]

        try:
            monkeypatch.setattr(BaseRequest, "post", post)
            updates = await bot.get_updates(timeout=1)

            assert isinstance(updates, tuple)
            assert len(updates) == 1
            assert isinstance(updates[0].callback_query.data, InvalidCallbackData)

        finally:
            # Reset b/c bots scope is session
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    # TODO: Needs improvement. We need incoming inline query to test answer.
    async def test_replace_callback_data_answer_inline_query(self, monkeypatch, cdc_bot, chat_id):
        bot = cdc_bot

        # For now just test that our internals pass the correct data
        async def make_assertion(
            endpoint,
            data=None,
            *args,
            **kwargs,
        ):
            inline_keyboard = data["results"][0]["reply_markup"].inline_keyboard
            assertion_1 = inline_keyboard[0][1] == no_replace_button
            assertion_2 = inline_keyboard[0][0] != replace_button
            keyboard, button = (
                inline_keyboard[0][0].callback_data[:32],
                inline_keyboard[0][0].callback_data[32:],
            )
            assertion_3 = (
                bot.callback_data_cache._keyboard_data[keyboard].button_data[button]
                == "replace_test"
            )
            assertion_4 = data["results"][1].reply_markup is None
            return assertion_1 and assertion_2 and assertion_3 and assertion_4

        try:
            replace_button = InlineKeyboardButton(text="replace", callback_data="replace_test")
            no_replace_button = InlineKeyboardButton(
                text="no_replace", url="http://python-telegram-bot.org/"
            )
            reply_markup = InlineKeyboardMarkup.from_row(
                [
                    replace_button,
                    no_replace_button,
                ]
            )

            bot.username  # call this here so `bot.get_me()` won't be called after mocking
            monkeypatch.setattr(bot, "_post", make_assertion)
            results = [
                InlineQueryResultArticle(
                    "11", "first", InputTextMessageContent("first"), reply_markup=reply_markup
                ),
                InlineQueryResultVoice(
                    "22",
                    "https://python-telegram-bot.org/static/testfiles/telegram.ogg",
                    title="second",
                ),
            ]

            assert await bot.answer_inline_query(chat_id, results=results)

        finally:
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    @pytest.mark.parametrize(
        "message_type", ["channel_post", "edited_channel_post", "message", "edited_message"]
    )
    @pytest.mark.parametrize("self_sender", [True, False])
    async def test_arbitrary_callback_data_via_bot(
        self, cdc_bot, monkeypatch, self_sender, message_type
    ):
        bot = cdc_bot
        reply_markup = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="text", callback_data="callback_data")
        )

        reply_markup = bot.callback_data_cache.process_keyboard(reply_markup)
        message = Message(
            1,
            dtm.datetime.utcnow(),
            None,
            reply_markup=reply_markup,
            via_bot=bot.bot if self_sender else User(1, "first", False),
        )

        async def post(*args, **kwargs):
            return [Update(17, **{message_type: message}).to_dict()]

        try:
            monkeypatch.setattr(BaseRequest, "post", post)
            updates = await bot.get_updates(timeout=1)

            assert isinstance(updates, tuple)
            assert len(updates) == 1

            message = updates[0][message_type]
            if self_sender:
                assert message.reply_markup.inline_keyboard[0][0].callback_data == "callback_data"
            else:
                assert (
                    message.reply_markup.inline_keyboard[0][0].callback_data
                    == reply_markup.inline_keyboard[0][0].callback_data
                )
        finally:
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    @pytest.mark.parametrize("bot_class", [Bot, ExtBot])
    async def test_http2_runtime_error(self, recwarn, bot_class):
        bot_class("12345:ABCDE", base_url="http://", request=HTTPXRequest(http_version="2"))
        bot_class(
            "12345:ABCDE",
            base_url="http://",
            get_updates_request=HTTPXRequest(http_version="2"),
        )
        bot_class(
            "12345:ABCDE",
            base_url="http://",
            request=HTTPXRequest(http_version="2"),
            get_updates_request=HTTPXRequest(http_version="2"),
        )
        assert len(recwarn) == 3
        assert "You set the HTTP version for the request HTTPXRequest instance" in str(
            recwarn[0].message
        )
        assert "You set the HTTP version for the get_updates_request HTTPXRequest instance" in str(
            recwarn[1].message
        )
        assert (
            "You set the HTTP version for the get_updates_request and request HTTPXRequest "
            "instance" in str(recwarn[2].message)
        )
        for warning in recwarn:
            assert warning.filename == __file__, "wrong stacklevel!"
            assert warning.category is PTBUserWarning

    async def test_set_get_my_name(self, bot, monkeypatch):
        """We only test that we pass the correct values to TG since this endpoint is heavily
        rate limited which makes automated tests rather infeasible."""
        default_name = "default_bot_name"
        en_name = "en_bot_name"
        de_name = "de_bot_name"

        # We predefine the responses that we would TG expect to send us
        set_stack = asyncio.Queue()
        get_stack = asyncio.Queue()
        await set_stack.put({"name": default_name})
        await set_stack.put({"name": en_name, "language_code": "en"})
        await set_stack.put({"name": de_name, "language_code": "de"})
        await get_stack.put({"name": default_name, "language_code": None})
        await get_stack.put({"name": en_name, "language_code": "en"})
        await get_stack.put({"name": de_name, "language_code": "de"})

        await set_stack.put({"name": default_name})
        await set_stack.put({"language_code": "en"})
        await set_stack.put({"language_code": "de"})
        await get_stack.put({"name": default_name, "language_code": None})
        await get_stack.put({"name": default_name, "language_code": "en"})
        await get_stack.put({"name": default_name, "language_code": "de"})

        async def post(url, request_data: RequestData, *args, **kwargs):
            # The mock-post now just fetches the predefined responses from the queues
            if "setMyName" in url:
                expected = await set_stack.get()
                assert request_data.json_parameters == expected
                set_stack.task_done()
                return True

            bot_name = await get_stack.get()
            if "language_code" in request_data.json_parameters:
                assert request_data.json_parameters == {"language_code": bot_name["language_code"]}
            else:
                assert request_data.json_parameters == {}
            get_stack.task_done()
            return bot_name

        monkeypatch.setattr(bot.request, "post", post)

        # Set the names
        assert all(
            await asyncio.gather(
                bot.set_my_name(default_name),
                bot.set_my_name(en_name, language_code="en"),
                bot.set_my_name(de_name, language_code="de"),
            )
        )

        # Check that they were set correctly
        assert await asyncio.gather(
            bot.get_my_name(), bot.get_my_name("en"), bot.get_my_name("de")
        ) == [
            BotName(default_name),
            BotName(en_name),
            BotName(de_name),
        ]

        # Delete the names
        assert all(
            await asyncio.gather(
                bot.set_my_name(default_name),
                bot.set_my_name(None, language_code="en"),
                bot.set_my_name(None, language_code="de"),
            )
        )

        # Check that they were deleted correctly
        assert await asyncio.gather(
            bot.get_my_name(), bot.get_my_name("en"), bot.get_my_name("de")
        ) == 3 * [BotName(default_name)]

    async def test_set_message_reaction(self, bot, monkeypatch):
        """This is here so we can test the convenient conversion we do in the function without
        having to do multiple requests to Telegram"""

        expected_param = [
            [{"emoji": ReactionEmoji.THUMBS_UP, "type": "emoji"}],
            [{"emoji": ReactionEmoji.RED_HEART, "type": "emoji"}],
            [{"custom_emoji_id": "custom_emoji_1", "type": "custom_emoji"}],
            [{"custom_emoji_id": "custom_emoji_2", "type": "custom_emoji"}],
            [{"emoji": ReactionEmoji.THUMBS_DOWN, "type": "emoji"}],
            [{"custom_emoji_id": "custom_emoji_3", "type": "custom_emoji"}],
            [
                {"emoji": ReactionEmoji.RED_HEART, "type": "emoji"},
                {"custom_emoji_id": "custom_emoji_4", "type": "custom_emoji"},
                {"emoji": ReactionEmoji.THUMBS_DOWN, "type": "emoji"},
                {"custom_emoji_id": "custom_emoji_5", "type": "custom_emoji"},
            ],
            [],
        ]

        amount = 0

        async def post(url, request_data: RequestData, *args, **kwargs):
            # The mock-post now just fetches the predefined responses from the queues
            assert request_data.json_parameters["chat_id"] == "1"
            assert request_data.json_parameters["message_id"] == "2"
            assert request_data.json_parameters["is_big"]
            nonlocal amount
            assert request_data.parameters["reaction"] == expected_param[amount]
            amount += 1

        monkeypatch.setattr(bot.request, "post", post)
        await bot.set_message_reaction(1, 2, [ReactionTypeEmoji(ReactionEmoji.THUMBS_UP)], True)
        await bot.set_message_reaction(1, 2, ReactionTypeEmoji(ReactionEmoji.RED_HEART), True)
        await bot.set_message_reaction(1, 2, [ReactionTypeCustomEmoji("custom_emoji_1")], True)
        await bot.set_message_reaction(1, 2, ReactionTypeCustomEmoji("custom_emoji_2"), True)
        await bot.set_message_reaction(1, 2, ReactionEmoji.THUMBS_DOWN, True)
        await bot.set_message_reaction(1, 2, "custom_emoji_3", True)
        await bot.set_message_reaction(
            1,
            2,
            [
                ReactionTypeEmoji(ReactionEmoji.RED_HEART),
                ReactionTypeCustomEmoji("custom_emoji_4"),
                ReactionEmoji.THUMBS_DOWN,
                ReactionTypeCustomEmoji("custom_emoji_5"),
            ],
            True,
        )

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_message_default_quote_parse_mode(
        self, default_bot, chat_id, message, custom, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            assert request_data.parameters["reply_parameters"].get("quote_parse_mode") == (
                custom or default_bot.defaults.quote_parse_mode
            )
            return make_message("dummy reply").to_dict()

        kwargs = {"message_id": 1}
        if custom is not None:
            kwargs["quote_parse_mode"] = custom

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        await default_bot.send_message(
            chat_id, message, reply_parameters=ReplyParameters(**kwargs)
        )

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_poll_default_quote_parse_mode(
        self, default_bot, chat_id, custom, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            assert request_data.parameters["reply_parameters"].get("quote_parse_mode") == (
                custom or default_bot.defaults.quote_parse_mode
            )
            return make_message("dummy reply").to_dict()

        kwargs = {"message_id": 1}
        if custom is not None:
            kwargs["quote_parse_mode"] = custom

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        await default_bot.send_poll(
            chat_id,
            question="question",
            options=["option1", "option2"],
            reply_parameters=ReplyParameters(**kwargs),
        )

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_game_default_quote_parse_mode(
        self, default_bot, chat_id, custom, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            assert request_data.parameters["reply_parameters"].get("quote_parse_mode") == (
                custom or default_bot.defaults.quote_parse_mode
            )
            return make_message("dummy reply").to_dict()

        kwargs = {"message_id": 1}
        if custom is not None:
            kwargs["quote_parse_mode"] = custom

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        await default_bot.send_game(
            chat_id, "game_short_name", reply_parameters=ReplyParameters(**kwargs)
        )

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_copy_message_default_quote_parse_mode(
        self, default_bot, chat_id, custom, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            assert request_data.parameters["reply_parameters"].get("quote_parse_mode") == (
                custom or default_bot.defaults.quote_parse_mode
            )
            return make_message("dummy reply").to_dict()

        kwargs = {"message_id": 1}
        if custom is not None:
            kwargs["quote_parse_mode"] = custom

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        await default_bot.copy_message(chat_id, 1, 1, reply_parameters=ReplyParameters(**kwargs))

    async def test_do_api_request_camel_case_conversion(self, bot, monkeypatch):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return url.endswith("camelCase")

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.do_api_request("camel_case")

    async def test_do_api_request_media_write_timeout(self, bot, chat_id, monkeypatch):
        test_flag = None

        class CustomRequest(BaseRequest):
            async def initialize(self_) -> None:
                pass

            async def shutdown(self_) -> None:
                pass

            async def do_request(self_, *args, **kwargs) -> Tuple[int, bytes]:
                nonlocal test_flag
                test_flag = (
                    kwargs.get("read_timeout"),
                    kwargs.get("connect_timeout"),
                    kwargs.get("write_timeout"),
                    kwargs.get("pool_timeout"),
                )
                return HTTPStatus.OK, b'{"ok": "True", "result": {}}'

        custom_request = CustomRequest()

        bot = Bot(bot.token, request=custom_request)
        await bot.do_api_request(
            "send_document",
            api_kwargs={
                "chat_id": chat_id,
                "caption": "test_caption",
                "document": InputFile(data_file("telegram.png").open("rb")),
            },
        )
        assert test_flag == (
            DEFAULT_NONE,
            DEFAULT_NONE,
            20,
            DEFAULT_NONE,
        )

    async def test_do_api_request_default_timezone(self, tz_bot, monkeypatch):
        until = dtm.datetime(2020, 1, 11, 16, 13)
        until_timestamp = to_timestamp(until, tzinfo=tz_bot.defaults.tzinfo)

        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            chat_id = data["chat_id"] == 2
            user_id = data["user_id"] == 32
            until_date = data.get("until_date", until_timestamp) == until_timestamp
            return chat_id and user_id and until_date

        monkeypatch.setattr(tz_bot.request, "post", make_assertion)

        assert await tz_bot.do_api_request(
            "banChatMember", api_kwargs={"chat_id": 2, "user_id": 32}
        )
        assert await tz_bot.do_api_request(
            "banChatMember", api_kwargs={"chat_id": 2, "user_id": 32, "until_date": until}
        )
        assert await tz_bot.do_api_request(
            "banChatMember",
            api_kwargs={"chat_id": 2, "user_id": 32, "until_date": until_timestamp},
        )


class TestBotWithRequest:
    """
    Most are executed on tg.ext.ExtBot, as that class only extends the functionality of tg.bot

    Behavior for init of ExtBot with missing optional dependency cachetools (for CallbackDataCache)
    is tested in `test_callbackdatacache`
    """

    async def test_invalid_token_server_response(self):
        with pytest.raises(InvalidToken, match="The token `12` was rejected by the server."):
            async with ExtBot(token="12"):
                pass

    async def test_multiple_init_cycles(self, bot):
        # nothing really to assert - this should just not fail
        test_bot = Bot(bot.token)
        async with test_bot:
            await test_bot.get_me()
        async with test_bot:
            await test_bot.get_me()

    async def test_forward_message(self, bot, chat_id, message):
        forward_message = await bot.forward_message(
            chat_id, from_chat_id=chat_id, message_id=message.message_id
        )

        assert forward_message.text == message.text
        assert forward_message.forward_origin.sender_user == message.from_user
        assert isinstance(forward_message.forward_origin.date, dtm.datetime)

    async def test_forward_protected_message(self, bot, chat_id):
        tasks = asyncio.gather(
            bot.send_message(chat_id, "cant forward me", protect_content=True),
            bot.send_message(chat_id, "forward me", protect_content=False),
        )
        to_forward_protected, to_forward_unprotected = await tasks

        assert to_forward_protected.has_protected_content
        assert not to_forward_unprotected.has_protected_content

        forwarded_but_now_protected = await to_forward_unprotected.forward(
            chat_id, protect_content=True
        )
        assert forwarded_but_now_protected.has_protected_content

        tasks = asyncio.gather(
            to_forward_protected.forward(chat_id),
            forwarded_but_now_protected.forward(chat_id),
            return_exceptions=True,
        )
        result = await tasks
        assert all("can't be forwarded" in str(exc) for exc in result)

    async def test_forward_messages(self, bot, chat_id):
        tasks = asyncio.gather(
            bot.send_message(chat_id, text="will be forwarded"),
            bot.send_message(chat_id, text="will be forwarded"),
        )

        msg1, msg2 = await tasks

        forward_messages = await bot.forward_messages(
            chat_id, from_chat_id=chat_id, message_ids=sorted((msg1.message_id, msg2.message_id))
        )

        assert isinstance(forward_messages, tuple)

        tasks = asyncio.gather(
            bot.send_message(
                chat_id, "temp 1", reply_to_message_id=forward_messages[0].message_id
            ),
            bot.send_message(
                chat_id, "temp 2", reply_to_message_id=forward_messages[1].message_id
            ),
        )

        temp_msg1, temp_msg2 = await tasks
        forward_msg1 = temp_msg1.reply_to_message
        forward_msg2 = temp_msg2.reply_to_message

        assert forward_msg1.text == msg1.text
        assert forward_msg1.forward_origin.sender_user == msg1.from_user
        assert isinstance(forward_msg1.forward_origin.date, dtm.datetime)

        assert forward_msg2.text == msg2.text
        assert forward_msg2.forward_origin.sender_user == msg2.from_user
        assert isinstance(forward_msg2.forward_origin.date, dtm.datetime)

    async def test_delete_message(self, bot, chat_id):
        message = await bot.send_message(chat_id, text="will be deleted")
        await asyncio.sleep(2)

        assert await bot.delete_message(chat_id=chat_id, message_id=message.message_id) is True

    async def test_delete_message_old_message(self, bot, chat_id):
        with pytest.raises(BadRequest):
            # Considering that the first message is old enough
            await bot.delete_message(chat_id=chat_id, message_id=1)

    # send_photo, send_audio, send_document, send_sticker, send_video, send_voice, send_video_note,
    # send_media_group, send_animation, get_user_chat_boosts are tested in their respective
    # test modules. No need to duplicate here.

    async def test_delete_messages(self, bot, chat_id):
        msg1 = await bot.send_message(chat_id, text="will be deleted")
        msg2 = await bot.send_message(chat_id, text="will be deleted")
        await asyncio.sleep(2)

        assert await bot.delete_messages(chat_id=chat_id, message_ids=(msg1.id, msg2.id)) is True

    async def test_send_venue(self, bot, chat_id):
        longitude = -46.788279
        latitude = -23.691288
        title = "title"
        address = "address"
        foursquare_id = "foursquare id"
        foursquare_type = "foursquare type"
        google_place_id = "google_place id"
        google_place_type = "google_place type"

        tasks = asyncio.gather(
            *(
                bot.send_venue(
                    chat_id=chat_id,
                    title=title,
                    address=address,
                    latitude=latitude,
                    longitude=longitude,
                    protect_content=True,
                    **i,
                )
                for i in (
                    {"foursquare_id": foursquare_id, "foursquare_type": foursquare_type},
                    {"google_place_id": google_place_id, "google_place_type": google_place_type},
                )
            ),
        )

        message, message2 = await tasks
        assert message.venue
        assert message.venue.title == title
        assert message.venue.address == address
        assert message.venue.location.latitude == latitude
        assert message.venue.location.longitude == longitude
        assert message.venue.foursquare_id == foursquare_id
        assert message.venue.foursquare_type == foursquare_type
        assert message.venue.google_place_id is None
        assert message.venue.google_place_type is None
        assert message.has_protected_content

        assert message2.venue
        assert message2.venue.title == title
        assert message2.venue.address == address
        assert message2.venue.location.latitude == latitude
        assert message2.venue.location.longitude == longitude
        assert message2.venue.google_place_id == google_place_id
        assert message2.venue.google_place_type == google_place_type
        assert message2.venue.foursquare_id is None
        assert message2.venue.foursquare_type is None
        assert message2.has_protected_content

    async def test_send_contact(self, bot, chat_id):
        phone_number = "+11234567890"
        first_name = "Leandro"
        last_name = "Toledo"
        message = await bot.send_contact(
            chat_id=chat_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            protect_content=True,
        )

        assert message.contact
        assert message.contact.phone_number == phone_number
        assert message.contact.first_name == first_name
        assert message.contact.last_name == last_name
        assert message.has_protected_content

    async def test_send_chat_action_all_args(self, bot, chat_id, monkeypatch):
        async def make_assertion(*args, **_):
            kwargs = args[1]
            return (
                kwargs["chat_id"] == chat_id
                and kwargs["action"] == "action"
                and kwargs["message_thread_id"] == 1
            )

        monkeypatch.setattr(bot, "_post", make_assertion)
        assert await bot.send_chat_action(chat_id, "action", 1)

    # TODO: Add bot to group to test polls too
    @pytest.mark.parametrize(
        "reply_markup",
        [
            None,
            InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text="text", callback_data="data")
            ),
            InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text="text", callback_data="data")
            ).to_dict(),
        ],
    )
    async def test_send_and_stop_poll(self, bot, super_group_id, reply_markup):
        question = "Is this a test?"
        answers = ["Yes", "No", "Maybe"]
        explanation = "[Here is a link](https://google.com)"
        explanation_entities = [
            MessageEntity(MessageEntity.TEXT_LINK, 0, 14, url="https://google.com")
        ]

        poll_task = asyncio.create_task(
            bot.send_poll(
                chat_id=super_group_id,
                question=question,
                options=answers,
                is_anonymous=False,
                allows_multiple_answers=True,
                read_timeout=60,
                protect_content=True,
            )
        )
        quiz_task = asyncio.create_task(
            bot.send_poll(
                chat_id=super_group_id,
                question=question,
                options=answers,
                type=Poll.QUIZ,
                correct_option_id=2,
                is_closed=True,
                explanation=explanation,
                explanation_parse_mode=ParseMode.MARKDOWN_V2,
            )
        )

        message = await poll_task
        assert message.poll
        assert message.poll.question == question
        assert message.poll.options[0].text == answers[0]
        assert message.poll.options[1].text == answers[1]
        assert message.poll.options[2].text == answers[2]
        assert not message.poll.is_anonymous
        assert message.poll.allows_multiple_answers
        assert not message.poll.is_closed
        assert message.poll.type == Poll.REGULAR
        assert message.has_protected_content

        # Since only the poll and not the complete message is returned, we can't check that the
        # reply_markup is correct. So we just test that sending doesn't give an error.
        poll = await bot.stop_poll(
            chat_id=super_group_id,
            message_id=message.message_id,
            reply_markup=reply_markup,
            read_timeout=60,
        )
        assert isinstance(poll, Poll)
        assert poll.is_closed
        assert poll.options[0].text == answers[0]
        assert poll.options[0].voter_count == 0
        assert poll.options[1].text == answers[1]
        assert poll.options[1].voter_count == 0
        assert poll.options[2].text == answers[2]
        assert poll.options[2].voter_count == 0
        assert poll.question == question
        assert poll.total_voter_count == 0

        message_quiz = await quiz_task
        assert message_quiz.poll.correct_option_id == 2
        assert message_quiz.poll.type == Poll.QUIZ
        assert message_quiz.poll.is_closed
        assert message_quiz.poll.explanation == "Here is a link"
        assert message_quiz.poll.explanation_entities == tuple(explanation_entities)
        assert poll_task.done()
        assert quiz_task.done()

    @pytest.mark.parametrize(
        ("open_period", "close_date"), [(5, None), (None, True)], ids=["open_period", "close_date"]
    )
    async def test_send_open_period(self, bot, super_group_id, open_period, close_date):
        question = "Is this a test?"
        answers = ["Yes", "No", "Maybe"]
        reply_markup = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="text", callback_data="data")
        )

        if close_date:
            close_date = dtm.datetime.utcnow() + dtm.timedelta(seconds=5.05)

        message = await bot.send_poll(
            chat_id=super_group_id,
            question=question,
            options=answers,
            is_anonymous=False,
            allows_multiple_answers=True,
            read_timeout=60,
            open_period=open_period,
            close_date=close_date,
        )
        await asyncio.sleep(5.1)
        new_message = await bot.edit_message_reply_markup(
            chat_id=super_group_id,
            message_id=message.message_id,
            reply_markup=reply_markup,
            read_timeout=60,
        )
        assert new_message.poll.id == message.poll.id
        assert new_message.poll.is_closed

    async def test_send_close_date_default_tz(self, tz_bot, super_group_id):
        question = "Is this a test?"
        answers = ["Yes", "No", "Maybe"]
        reply_markup = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="text", callback_data="data")
        )

        aware_close_date = dtm.datetime.now(tz=tz_bot.defaults.tzinfo) + dtm.timedelta(seconds=5)
        close_date = aware_close_date.replace(tzinfo=None)

        msg = await tz_bot.send_poll(  # The timezone returned from this is always converted to UTC
            chat_id=super_group_id,
            question=question,
            options=answers,
            close_date=close_date,
            read_timeout=60,
        )
        msg.poll._unfreeze()
        # Sometimes there can be a few seconds delay, so don't let the test fail due to that-
        msg.poll.close_date = msg.poll.close_date.astimezone(aware_close_date.tzinfo)
        assert abs(msg.poll.close_date - aware_close_date) <= dtm.timedelta(seconds=5)

        await asyncio.sleep(5.1)

        new_message = await tz_bot.edit_message_reply_markup(
            chat_id=super_group_id,
            message_id=msg.message_id,
            reply_markup=reply_markup,
            read_timeout=60,
        )
        assert new_message.poll.id == msg.poll.id
        assert new_message.poll.is_closed

    async def test_send_poll_explanation_entities(self, bot, chat_id):
        test_string = "Italic Bold Code"
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.send_poll(
            chat_id,
            "question",
            options=["a", "b"],
            correct_option_id=0,
            type=Poll.QUIZ,
            explanation=test_string,
            explanation_entities=entities,
        )

        assert message.poll.explanation == test_string
        assert message.poll.explanation_entities == tuple(entities)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_poll_default_parse_mode(self, default_bot, super_group_id):
        explanation = "Italic Bold Code"
        explanation_markdown = "_Italic_ *Bold* `Code`"
        question = "Is this a test?"
        answers = ["Yes", "No", "Maybe"]

        tasks = asyncio.gather(
            *(
                default_bot.send_poll(
                    chat_id=super_group_id,
                    question=question,
                    options=answers,
                    type=Poll.QUIZ,
                    correct_option_id=2,
                    is_closed=True,
                    explanation=explanation_markdown,
                    **i,
                )
                for i in ({}, {"explanation_parse_mode": None}, {"explanation_parse_mode": "HTML"})
            ),
        )
        message1, message2, message3 = await tasks
        assert message1.poll.explanation == explanation
        assert message1.poll.explanation_entities == (
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.BOLD, 7, 4),
            MessageEntity(MessageEntity.CODE, 12, 4),
        )

        assert message2.poll.explanation == explanation_markdown
        assert message2.poll.explanation_entities == ()

        assert message3.poll.explanation == explanation_markdown
        assert message3.poll.explanation_entities == ()

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_poll_default_allow_sending_without_reply(
        self, default_bot, chat_id, custom
    ):
        question = "Is this a test?"
        answers = ["Yes", "No", "Maybe"]
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_poll(
                chat_id,
                question=question,
                options=answers,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_poll(
                chat_id,
                question=question,
                options=answers,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to reply not found"):
                await default_bot.send_poll(
                    chat_id,
                    question=question,
                    options=answers,
                    reply_to_message_id=reply_to_message.message_id,
                )

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_poll_default_protect_content(self, chat_id, default_bot):
        tasks = asyncio.gather(
            default_bot.send_poll(chat_id, "Test", ["1", "2"]),
            default_bot.send_poll(chat_id, "test", ["1", "2"], protect_content=False),
        )
        protected_poll, unprotect_poll = await tasks
        assert protected_poll.has_protected_content
        assert not unprotect_poll.has_protected_content

    @pytest.mark.parametrize("emoji", [*Dice.ALL_EMOJI, None])
    async def test_send_dice(self, bot, chat_id, emoji):
        message = await bot.send_dice(chat_id, emoji=emoji, protect_content=True)

        assert message.dice
        assert message.has_protected_content
        if emoji is None:
            assert message.dice.emoji == Dice.DICE
        else:
            assert message.dice.emoji == emoji

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_dice_default_allow_sending_without_reply(
        self, default_bot, chat_id, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_dice(
                chat_id,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_dice(
                chat_id,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to reply not found"):
                await default_bot.send_dice(
                    chat_id, reply_to_message_id=reply_to_message.message_id
                )

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_dice_default_protect_content(self, chat_id, default_bot):
        tasks = asyncio.gather(
            default_bot.send_dice(chat_id), default_bot.send_dice(chat_id, protect_content=False)
        )
        protected_dice, unprotected_dice = await tasks
        assert protected_dice.has_protected_content
        assert not unprotected_dice.has_protected_content

    @pytest.mark.parametrize("chat_action", list(ChatAction))
    async def test_send_chat_action(self, bot, chat_id, chat_action):
        assert await bot.send_chat_action(chat_id, chat_action)

    async def test_wrong_chat_action(self, bot, chat_id):
        with pytest.raises(BadRequest, match="Wrong parameter action"):
            await bot.send_chat_action(chat_id, "unknown action")

    async def test_answer_inline_query_current_offset_error(self, bot, inline_results):
        with pytest.raises(ValueError, match="`current_offset` and `next_offset`"):
            await bot.answer_inline_query(
                1234, results=inline_results, next_offset=42, current_offset=51
            )

    async def test_get_user_profile_photos(self, bot, chat_id):
        user_profile_photos = await bot.get_user_profile_photos(chat_id)
        assert user_profile_photos.photos[0][0].file_size == 5403

    async def test_get_one_user_profile_photo(self, bot, chat_id):
        user_profile_photos = await bot.get_user_profile_photos(chat_id, offset=0, limit=1)
        assert user_profile_photos.total_count == 1
        assert user_profile_photos.photos[0][0].file_size == 5403

    async def test_edit_message_text(self, bot, message):
        message = await bot.edit_message_text(
            text="new_text",
            chat_id=message.chat_id,
            message_id=message.message_id,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        assert message.text == "new_text"

    async def test_edit_message_text_entities(self, bot, message):
        test_string = "Italic Bold Code"
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.edit_message_text(
            text=test_string,
            chat_id=message.chat_id,
            message_id=message.message_id,
            entities=entities,
        )

        assert message.text == test_string
        assert message.entities == tuple(entities)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_edit_message_text_default_parse_mode(self, default_bot, message):
        test_string = "Italic Bold Code"
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.edit_message_text(
            text=test_markdown_string,
            chat_id=message.chat_id,
            message_id=message.message_id,
            disable_web_page_preview=True,
        )
        assert message.text_markdown == test_markdown_string
        assert message.text == test_string

        message = await default_bot.edit_message_text(
            text=test_markdown_string,
            chat_id=message.chat_id,
            message_id=message.message_id,
            parse_mode=None,
            disable_web_page_preview=True,
        )
        assert message.text == test_markdown_string
        assert message.text_markdown == escape_markdown(test_markdown_string)

        message = await default_bot.edit_message_text(
            text=test_markdown_string,
            chat_id=message.chat_id,
            message_id=message.message_id,
            disable_web_page_preview=True,
        )
        message = await default_bot.edit_message_text(
            text=test_markdown_string,
            chat_id=message.chat_id,
            message_id=message.message_id,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        assert message.text == test_markdown_string
        assert message.text_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.skip(reason="need reference to an inline message")
    async def test_edit_message_text_inline(self):
        pass

    async def test_edit_message_caption(self, bot, media_message):
        message = await bot.edit_message_caption(
            caption="new_caption",
            chat_id=media_message.chat_id,
            message_id=media_message.message_id,
        )

        assert message.caption == "new_caption"

    async def test_edit_message_caption_entities(self, bot, media_message):
        test_string = "Italic Bold Code"
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.edit_message_caption(
            caption=test_string,
            chat_id=media_message.chat_id,
            message_id=media_message.message_id,
            caption_entities=entities,
        )

        assert message.caption == test_string
        assert message.caption_entities == tuple(entities)

    # edit_message_media is tested in test_inputmedia

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_edit_message_caption_default_parse_mode(self, default_bot, media_message):
        test_string = "Italic Bold Code"
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.edit_message_caption(
            caption=test_markdown_string,
            chat_id=media_message.chat_id,
            message_id=media_message.message_id,
        )
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

        message = await default_bot.edit_message_caption(
            caption=test_markdown_string,
            chat_id=media_message.chat_id,
            message_id=media_message.message_id,
            parse_mode=None,
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

        message = await default_bot.edit_message_caption(
            caption=test_markdown_string,
            chat_id=media_message.chat_id,
            message_id=media_message.message_id,
        )
        message = await default_bot.edit_message_caption(
            caption=test_markdown_string,
            chat_id=media_message.chat_id,
            message_id=media_message.message_id,
            parse_mode="HTML",
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    async def test_edit_message_caption_with_parse_mode(self, bot, media_message):
        message = await bot.edit_message_caption(
            caption="new *caption*",
            parse_mode="Markdown",
            chat_id=media_message.chat_id,
            message_id=media_message.message_id,
        )

        assert message.caption == "new caption"

    @pytest.mark.skip(reason="need reference to an inline message")
    async def test_edit_message_caption_inline(self):
        pass

    async def test_edit_reply_markup(self, bot, message):
        new_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="test", callback_data="1")]])
        message = await bot.edit_message_reply_markup(
            chat_id=message.chat_id, message_id=message.message_id, reply_markup=new_markup
        )

        assert message is not True

    @pytest.mark.skip(reason="need reference to an inline message")
    async def test_edit_reply_markup_inline(self):
        pass

    @pytest.mark.xdist_group("getUpdates_and_webhook")
    # TODO: Actually send updates to the test bot so this can be tested properly
    async def test_get_updates(self, bot):
        await bot.delete_webhook()  # make sure there is no webhook set if webhook tests failed
        updates = await bot.get_updates(timeout=1)

        assert isinstance(updates, tuple)
        if updates:
            assert isinstance(updates[0], Update)

    @pytest.mark.parametrize("bot_class", [Bot, ExtBot])
    async def test_get_updates_read_timeout_deprecation_warning(
        self, bot, recwarn, monkeypatch, bot_class
    ):
        # Using the normal HTTPXRequest should not issue any warnings
        await bot.get_updates()
        assert len(recwarn) == 0

        # Now let's test deprecation warning when using get_updates for other BaseRequest
        # subclasses (we just monkeypatch the existing HTTPXRequest for this)
        read_timeout = None

        async def catch_timeouts(*args, **kwargs):
            nonlocal read_timeout
            read_timeout = kwargs.get("read_timeout")
            return HTTPStatus.OK, b'{"ok": "True", "result": {}}'

        monkeypatch.setattr(HTTPXRequest, "read_timeout", BaseRequest.read_timeout)
        monkeypatch.setattr(HTTPXRequest, "do_request", catch_timeouts)

        bot = bot_class(get_updates_request=HTTPXRequest(), token=bot.token)
        await bot.get_updates()

        assert len(recwarn) == 1
        assert "does not override the property `read_timeout`" in str(recwarn[0].message)
        assert recwarn[0].category is PTBDeprecationWarning
        assert recwarn[0].filename == __file__, "wrong stacklevel"

        assert read_timeout == 2

    @pytest.mark.parametrize(
        ("read_timeout", "timeout", "expected"),
        [
            (None, None, 0),
            (1, None, 1),
            (None, 1, 1),
            (DEFAULT_NONE, None, 10),
            (DEFAULT_NONE, 1, 11),
            (1, 2, 3),
        ],
    )
    async def test_get_updates_read_timeout_value_passing(
        self, bot, read_timeout, timeout, expected, monkeypatch
    ):
        caught_read_timeout = None

        async def catch_timeouts(*args, **kwargs):
            nonlocal caught_read_timeout
            caught_read_timeout = kwargs.get("read_timeout")
            return HTTPStatus.OK, b'{"ok": "True", "result": {}}'

        monkeypatch.setattr(HTTPXRequest, "do_request", catch_timeouts)

        bot = Bot(get_updates_request=HTTPXRequest(read_timeout=10), token=bot.token)
        await bot.get_updates(read_timeout=read_timeout, timeout=timeout)
        assert caught_read_timeout == expected

    @pytest.mark.xdist_group("getUpdates_and_webhook")
    @pytest.mark.parametrize("use_ip", [True, False])
    # local file path as file_input is tested below in test_set_webhook_params
    @pytest.mark.parametrize("file_input", ["bytes", "file_handle"])
    async def test_set_webhook_get_webhook_info_and_delete_webhook(self, bot, use_ip, file_input):
        url = "https://python-telegram-bot.org/test/webhook"
        # Get the ip address of the website - dynamically just in case it ever changes
        ip = socket.gethostbyname("python-telegram-bot.org")
        max_connections = 7
        allowed_updates = ["message"]
        file_input = (
            data_file("sslcert.pem").read_bytes()
            if file_input == "bytes"
            else data_file("sslcert.pem").open("rb")
        )
        await bot.set_webhook(
            url,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            ip_address=ip if use_ip else None,
            certificate=file_input if use_ip else None,
        )

        await asyncio.sleep(1)
        live_info = await bot.get_webhook_info()
        assert live_info.url == url
        assert live_info.max_connections == max_connections
        assert live_info.allowed_updates == tuple(allowed_updates)
        assert live_info.ip_address == ip
        assert live_info.has_custom_certificate == use_ip

        await bot.delete_webhook()
        await asyncio.sleep(1)
        info = await bot.get_webhook_info()
        assert not info.url
        assert info.ip_address is None
        assert info.has_custom_certificate is False

    async def test_leave_chat(self, bot):
        with pytest.raises(BadRequest, match="Chat not found"):
            await bot.leave_chat(-123456)

        with pytest.raises(NetworkError, match="Chat not found"):
            await bot.leave_chat(-123456)

    async def test_get_chat(self, bot, super_group_id):
        chat = await bot.get_chat(super_group_id)
        assert chat.type == "supergroup"
        assert chat.title == f">>> telegram.Bot(test) @{bot.username}"
        assert chat.id == int(super_group_id)

    async def test_get_chat_administrators(self, bot, channel_id):
        admins = await bot.get_chat_administrators(channel_id)
        assert isinstance(admins, tuple)

        for a in admins:
            assert a.status in ("administrator", "creator")

    async def test_get_chat_member_count(self, bot, channel_id):
        count = await bot.get_chat_member_count(channel_id)
        assert isinstance(count, int)
        assert count > 3

    async def test_get_chat_member(self, bot, channel_id, chat_id):
        chat_member = await bot.get_chat_member(channel_id, chat_id)

        assert chat_member.status == "administrator"
        assert chat_member.user.first_name == "PTB"
        assert chat_member.user.last_name == "Test user"

    @pytest.mark.skip(reason="Not implemented since we need a supergroup with many members")
    async def test_set_chat_sticker_set(self):
        pass

    @pytest.mark.skip(reason="Not implemented since we need a supergroup with many members")
    async def test_delete_chat_sticker_set(self):
        pass

    async def test_send_game(self, bot, chat_id):
        game_short_name = "test_game"
        message = await bot.send_game(chat_id, game_short_name, protect_content=True)

        assert message.game
        assert (
            message.game.description
            == "A no-op test game, for python-telegram-bot bot framework testing."
        )
        assert message.game.animation.file_id
        # We added some test bots later and for some reason the file size is not the same for them
        # so we accept three different sizes here. Shouldn't be too much of
        assert message.game.photo[0].file_size in [851, 4928, 850]
        assert message.has_protected_content

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_game_default_allow_sending_without_reply(
        self, default_bot, chat_id, custom
    ):
        game_short_name = "test_game"
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_game(
                chat_id,
                game_short_name,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_game(
                chat_id,
                game_short_name,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to reply not found"):
                await default_bot.send_game(
                    chat_id, game_short_name, reply_to_message_id=reply_to_message.message_id
                )

    @pytest.mark.parametrize(
        ("default_bot", "val"),
        [({"protect_content": True}, True), ({"protect_content": False}, None)],
        indirect=["default_bot"],
    )
    async def test_send_game_default_protect_content(self, default_bot, chat_id, val):
        protected = await default_bot.send_game(chat_id, "test_game", protect_content=val)
        assert protected.has_protected_content is val

    @pytest.mark.xdist_group("game")
    @xfail
    async def test_set_game_score_1(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        # First, test setting a score.
        game_short_name = "test_game"
        game = await bot.send_game(chat_id, game_short_name)

        message = await bot.set_game_score(
            user_id=chat_id,
            score=BASE_GAME_SCORE,  # Score value is relevant for other set_game_score_* tests!
            chat_id=game.chat_id,
            message_id=game.message_id,
        )

        assert message.game.description == game.game.description
        assert message.game.photo[0].file_size == game.game.photo[0].file_size
        assert message.game.animation.file_unique_id == game.game.animation.file_unique_id
        assert message.game.text != game.game.text

    @pytest.mark.xdist_group("game")
    @xfail
    async def test_set_game_score_2(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        # Test setting a score higher than previous
        game_short_name = "test_game"
        game = await bot.send_game(chat_id, game_short_name)

        score = BASE_GAME_SCORE + 1

        message = await bot.set_game_score(
            user_id=chat_id,
            score=score,
            chat_id=game.chat_id,
            message_id=game.message_id,
            disable_edit_message=True,
        )

        assert message.game.description == game.game.description
        assert message.game.photo[0].file_size == game.game.photo[0].file_size
        assert message.game.animation.file_unique_id == game.game.animation.file_unique_id
        assert message.game.text == game.game.text

    @pytest.mark.xdist_group("game")
    @xfail
    async def test_set_game_score_3(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        # Test setting a score lower than previous (should raise error)
        game_short_name = "test_game"
        game = await bot.send_game(chat_id, game_short_name)

        score = BASE_GAME_SCORE  # Even a score equal to previous raises an error.

        with pytest.raises(BadRequest, match="Bot_score_not_modified"):
            await bot.set_game_score(
                user_id=chat_id, score=score, chat_id=game.chat_id, message_id=game.message_id
            )

    @pytest.mark.xdist_group("game")
    @xfail
    async def test_set_game_score_4(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        # Test force setting a lower score
        game_short_name = "test_game"
        game = await bot.send_game(chat_id, game_short_name)
        await asyncio.sleep(1.5)

        score = BASE_GAME_SCORE - 10

        message = await bot.set_game_score(
            user_id=chat_id,
            score=score,
            chat_id=game.chat_id,
            message_id=game.message_id,
            force=True,
        )

        assert message.game.description == game.game.description
        assert message.game.photo[0].file_size == game.game.photo[0].file_size
        assert message.game.animation.file_unique_id == game.game.animation.file_unique_id

        # For some reason the returned message doesn't contain the updated score. need to fetch
        # the game again... (the service message is also absent when running the test suite)
        game2 = await bot.send_game(chat_id, game_short_name)
        assert str(score) in game2.game.text

    @pytest.mark.xdist_group("game")
    @xfail
    async def test_get_game_high_scores(self, bot, chat_id):
        # We need a game to get the scores for
        game_short_name = "test_game"
        game = await bot.send_game(chat_id, game_short_name)
        high_scores = await bot.get_game_high_scores(chat_id, game.chat_id, game.message_id)
        # We assume that the other game score tests ran within 20 sec
        assert high_scores[0].score == BASE_GAME_SCORE - 10

    # send_invoice and create_invoice_link is tested in test_invoice
    async def test_promote_chat_member(self, bot, channel_id, monkeypatch):
        # TODO: Add bot to supergroup so this can be tested properly / give bot perms
        with pytest.raises(BadRequest, match="Not enough rights"):
            assert await bot.promote_chat_member(
                channel_id,
                95205500,
                is_anonymous=True,
                can_change_info=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=True,
                can_manage_chat=True,
                can_manage_video_chats=True,
                can_manage_topics=True,
                can_post_stories=True,
                can_edit_stories=True,
                can_delete_stories=True,
            )

        # Test that we pass the correct params to TG
        async def make_assertion(*args, **_):
            data = args[1]
            return (
                data.get("chat_id") == channel_id
                and data.get("user_id") == 95205500
                and data.get("is_anonymous") == 1
                and data.get("can_change_info") == 2
                and data.get("can_post_messages") == 3
                and data.get("can_edit_messages") == 4
                and data.get("can_delete_messages") == 5
                and data.get("can_invite_users") == 6
                and data.get("can_restrict_members") == 7
                and data.get("can_pin_messages") == 8
                and data.get("can_promote_members") == 9
                and data.get("can_manage_chat") == 10
                and data.get("can_manage_video_chats") == 11
                and data.get("can_manage_topics") == 12
                and data.get("can_post_stories") == 13
                and data.get("can_edit_stories") == 14
                and data.get("can_delete_stories") == 15
            )

        monkeypatch.setattr(bot, "_post", make_assertion)
        assert await bot.promote_chat_member(
            channel_id,
            95205500,
            is_anonymous=1,
            can_change_info=2,
            can_post_messages=3,
            can_edit_messages=4,
            can_delete_messages=5,
            can_invite_users=6,
            can_restrict_members=7,
            can_pin_messages=8,
            can_promote_members=9,
            can_manage_chat=10,
            can_manage_video_chats=11,
            can_manage_topics=12,
            can_post_stories=13,
            can_edit_stories=14,
            can_delete_stories=15,
        )

    async def test_export_chat_invite_link(self, bot, channel_id):
        # Each link is unique apparently
        invite_link = await bot.export_chat_invite_link(channel_id)
        assert isinstance(invite_link, str)
        assert invite_link

    async def test_edit_revoke_chat_invite_link_passing_link_objects(self, bot, channel_id):
        invite_link = await bot.create_chat_invite_link(chat_id=channel_id)
        assert invite_link.name is None

        edited_link = await bot.edit_chat_invite_link(
            chat_id=channel_id, invite_link=invite_link, name="some_name"
        )
        assert edited_link == invite_link
        assert edited_link.name == "some_name"

        revoked_link = await bot.revoke_chat_invite_link(
            chat_id=channel_id, invite_link=edited_link
        )
        assert revoked_link.invite_link == edited_link.invite_link
        assert revoked_link.is_revoked is True
        assert revoked_link.name == "some_name"

    @pytest.mark.parametrize("creates_join_request", [True, False])
    @pytest.mark.parametrize("name", [None, "name"])
    async def test_create_chat_invite_link_basics(
        self, bot, creates_join_request, name, channel_id
    ):
        data = {}
        if creates_join_request:
            data["creates_join_request"] = True
        if name:
            data["name"] = name
        invite_link = await bot.create_chat_invite_link(chat_id=channel_id, **data)

        assert invite_link.member_limit is None
        assert invite_link.expire_date is None
        assert invite_link.creates_join_request == creates_join_request
        assert invite_link.name == name

        revoked_link = await bot.revoke_chat_invite_link(
            chat_id=channel_id, invite_link=invite_link.invite_link
        )
        assert revoked_link.is_revoked

    @pytest.mark.skipif(not TEST_WITH_OPT_DEPS, reason="This test's implementation requires pytz")
    @pytest.mark.parametrize("datetime", argvalues=[True, False], ids=["datetime", "integer"])
    async def test_advanced_chat_invite_links(self, bot, channel_id, datetime):
        # we are testing this all in one function in order to save api calls
        timestamp = dtm.datetime.utcnow()
        add_seconds = dtm.timedelta(0, 70)
        time_in_future = timestamp + add_seconds
        expire_time = time_in_future if datetime else to_timestamp(time_in_future)
        aware_time_in_future = UTC.localize(time_in_future)

        invite_link = await bot.create_chat_invite_link(
            channel_id, expire_date=expire_time, member_limit=10
        )
        assert invite_link.invite_link
        assert not invite_link.invite_link.endswith("...")
        assert abs(invite_link.expire_date - aware_time_in_future) < dtm.timedelta(seconds=1)
        assert invite_link.member_limit == 10

        add_seconds = dtm.timedelta(0, 80)
        time_in_future = timestamp + add_seconds
        expire_time = time_in_future if datetime else to_timestamp(time_in_future)
        aware_time_in_future = UTC.localize(time_in_future)

        edited_invite_link = await bot.edit_chat_invite_link(
            channel_id,
            invite_link.invite_link,
            expire_date=expire_time,
            member_limit=20,
            name="NewName",
        )
        assert edited_invite_link.invite_link == invite_link.invite_link
        assert abs(edited_invite_link.expire_date - aware_time_in_future) < dtm.timedelta(
            seconds=1
        )
        assert edited_invite_link.name == "NewName"
        assert edited_invite_link.member_limit == 20

        edited_invite_link = await bot.edit_chat_invite_link(
            channel_id,
            invite_link.invite_link,
            name="EvenNewerName",
            creates_join_request=True,
        )
        assert edited_invite_link.invite_link == invite_link.invite_link
        assert not edited_invite_link.expire_date
        assert edited_invite_link.name == "EvenNewerName"
        assert edited_invite_link.creates_join_request
        assert edited_invite_link.member_limit is None

        revoked_invite_link = await bot.revoke_chat_invite_link(
            channel_id, invite_link.invite_link
        )
        assert revoked_invite_link.invite_link == invite_link.invite_link
        assert revoked_invite_link.is_revoked

    async def test_advanced_chat_invite_links_default_tzinfo(self, tz_bot, channel_id):
        # we are testing this all in one function in order to save api calls
        add_seconds = dtm.timedelta(0, 70)
        aware_expire_date = dtm.datetime.now(tz=tz_bot.defaults.tzinfo) + add_seconds
        time_in_future = aware_expire_date.replace(tzinfo=None)

        invite_link = await tz_bot.create_chat_invite_link(
            channel_id, expire_date=time_in_future, member_limit=10
        )
        assert invite_link.invite_link
        assert not invite_link.invite_link.endswith("...")
        assert abs(invite_link.expire_date - aware_expire_date) < dtm.timedelta(seconds=1)
        assert invite_link.member_limit == 10

        add_seconds = dtm.timedelta(0, 80)
        aware_expire_date += add_seconds
        time_in_future = aware_expire_date.replace(tzinfo=None)

        edited_invite_link = await tz_bot.edit_chat_invite_link(
            channel_id,
            invite_link.invite_link,
            expire_date=time_in_future,
            member_limit=20,
            name="NewName",
        )
        assert edited_invite_link.invite_link == invite_link.invite_link
        assert abs(edited_invite_link.expire_date - aware_expire_date) < dtm.timedelta(seconds=1)
        assert edited_invite_link.name == "NewName"
        assert edited_invite_link.member_limit == 20

        edited_invite_link = await tz_bot.edit_chat_invite_link(
            channel_id,
            invite_link.invite_link,
            name="EvenNewerName",
            creates_join_request=True,
        )
        assert edited_invite_link.invite_link == invite_link.invite_link
        assert not edited_invite_link.expire_date
        assert edited_invite_link.name == "EvenNewerName"
        assert edited_invite_link.creates_join_request
        assert edited_invite_link.member_limit is None

        revoked_invite_link = await tz_bot.revoke_chat_invite_link(
            channel_id, invite_link.invite_link
        )
        assert revoked_invite_link.invite_link == invite_link.invite_link
        assert revoked_invite_link.is_revoked

    async def test_approve_chat_join_request(self, bot, chat_id, channel_id):
        # TODO: Need incoming join request to properly test
        # Since we can't create join requests on the fly, we just tests the call to TG
        # by checking that it complains about approving a user who is already in the chat
        with pytest.raises(BadRequest, match="User_already_participant"):
            await bot.approve_chat_join_request(chat_id=channel_id, user_id=chat_id)

    async def test_decline_chat_join_request(self, bot, chat_id, channel_id):
        # TODO: Need incoming join request to properly test
        # Since we can't create join requests on the fly, we just tests the call to TG
        # by checking that it complains about declining a user who is already in the chat
        #
        # The error message Hide_requester_missing started showing up instead of
        # User_already_participant. Don't know why …
        with pytest.raises(BadRequest, match="User_already_participant|Hide_requester_missing"):
            await bot.decline_chat_join_request(chat_id=channel_id, user_id=chat_id)

    async def test_set_chat_photo(self, bot, channel_id):
        async def func():
            assert await bot.set_chat_photo(channel_id, f)

        with data_file("telegram_test_channel.jpg").open("rb") as f:
            await expect_bad_request(
                func, "Type of file mismatch", "Telegram did not accept the file."
            )

    async def test_delete_chat_photo(self, bot, channel_id):
        async def func():
            assert await bot.delete_chat_photo(channel_id)

        await expect_bad_request(func, "Chat_not_modified", "Chat photo was not set.")

    async def test_set_chat_title(self, bot, channel_id):
        assert await bot.set_chat_title(channel_id, ">>> telegram.Bot() - Tests")

    async def test_set_chat_description(self, bot, channel_id):
        assert await bot.set_chat_description(channel_id, "Time: " + str(time.time()))

    async def test_pin_and_unpin_message(self, bot, super_group_id):
        messages = []  # contains the Messages we sent
        pinned_messages_tasks = set()  # contains the asyncio.Tasks that pin the messages

        # Let's send 3 messages so we can pin them
        awaitables = {bot.send_message(super_group_id, f"test_pin_message_{i}") for i in range(3)}

        # We will pin the messages immediately after sending them
        for sending_msg in asyncio.as_completed(awaitables):  # as_completed sends the messages
            msg = await sending_msg
            coro = bot.pin_chat_message(super_group_id, msg.message_id, True, read_timeout=10)
            pinned_messages_tasks.add(asyncio.create_task(coro))  # start pinning the message
            messages.append(msg)

        assert len(messages) == 3  # Check if we sent 3 messages

        # Check if we pinned 3 messages
        assert all([await i for i in pinned_messages_tasks])
        assert all(i.done() for i in pinned_messages_tasks)  # Check if all tasks are done

        chat = await bot.get_chat(super_group_id)  # get the chat to check the pinned message
        assert chat.pinned_message in messages

        # Determine which message is not the most recently pinned
        for old_pin_msg in messages:
            if chat.pinned_message != old_pin_msg:
                break

        # Test unpinning our messages
        tasks = asyncio.gather(
            bot.unpin_chat_message(  # unpins any message except the most recent
                chat_id=super_group_id,  # because we don't want to accidentally unpin the same msg
                message_id=old_pin_msg.message_id,  # twice
                read_timeout=10,
            ),
            bot.unpin_chat_message(chat_id=super_group_id, read_timeout=10),  # unpins most recent
        )
        assert all(await tasks)
        assert all(i.done() for i in tasks)
        assert await bot.unpin_all_chat_messages(super_group_id, read_timeout=10)

    # get_sticker_set, upload_sticker_file, create_new_sticker_set, add_sticker_to_set,
    # set_sticker_position_in_set, delete_sticker_from_set and get_custom_emoji_stickers
    # are tested in the test_sticker module.

    # get_forum_topic_icon_stickers, edit_forum_topic, general_forum etc...
    # are tested in the test_forum module.
    async def test_send_message_disable_web_page_preview(self, bot, chat_id):
        """Test that disable_web_page_preview is substituted for link_preview_options and that
        it still works as expected for backward compatability."""
        msg = await bot.send_message(
            chat_id,
            "https://github.com/python-telegram-bot/python-telegram-bot",
            disable_web_page_preview=True,
        )
        assert msg.link_preview_options
        assert msg.link_preview_options.is_disabled

    async def test_send_message_link_preview_options(self, bot, chat_id):
        """Test whether link_preview_options is correctly passed to the API."""
        # btw it is possible to have no url in the text, but set a url for the preview.
        msg = await bot.send_message(
            chat_id,
            "https://github.com/python-telegram-bot/python-telegram-bot",
            link_preview_options=LinkPreviewOptions(prefer_small_media=True, show_above_text=True),
        )
        assert msg.link_preview_options
        assert not msg.link_preview_options.is_disabled
        # The prefer_* options aren't very consistent on the client side (big pic shown) +
        # they are not returned by the API.
        # assert msg.link_preview_options.prefer_small_media
        assert msg.link_preview_options.show_above_text

    @pytest.mark.parametrize(
        "default_bot",
        [{"link_preview_options": LinkPreviewOptions(show_above_text=True)}],
        indirect=True,
    )
    async def test_send_message_default_link_preview_options(self, default_bot, chat_id):
        """Test whether Defaults.link_preview_options is correctly fused with the passed LPO."""
        github_url = "https://github.com/python-telegram-bot/python-telegram-bot"
        website = "https://python-telegram-bot.org/"

        # First test just the default passing:
        coro1 = default_bot.send_message(chat_id, github_url)
        # Next test fusion of both LPOs:
        coro2 = default_bot.send_message(
            chat_id,
            github_url,
            link_preview_options=LinkPreviewOptions(url=website, prefer_large_media=True),
        )
        # Now test fusion + overriding of passed LPO:
        coro3 = default_bot.send_message(
            chat_id,
            github_url,
            link_preview_options=LinkPreviewOptions(show_above_text=False, url=website),
        )
        # finally test explicitly setting to None
        coro4 = default_bot.send_message(chat_id, github_url, link_preview_options=None)

        msgs = asyncio.gather(coro1, coro2, coro3, coro4)
        msg1, msg2, msg3, msg4 = await msgs
        assert msg1.link_preview_options
        assert msg1.link_preview_options.show_above_text

        assert msg2.link_preview_options
        assert msg2.link_preview_options.show_above_text
        assert msg2.link_preview_options.url == website
        assert msg2.link_preview_options.prefer_large_media  # Now works correctly using new url..

        assert msg3.link_preview_options
        assert not msg3.link_preview_options.show_above_text
        assert msg3.link_preview_options.url == website

        assert msg4.link_preview_options == LinkPreviewOptions(url=github_url)

    @pytest.mark.parametrize(
        "default_bot",
        [{"link_preview_options": LinkPreviewOptions(show_above_text=True)}],
        indirect=True,
    )
    async def test_edit_message_text_default_link_preview_options(self, default_bot, chat_id):
        """Test whether Defaults.link_preview_options is correctly fused with the passed LPO."""
        github_url = "https://github.com/python-telegram-bot/python-telegram-bot"
        website = "https://python-telegram-bot.org/"
        telegram_url = "https://telegram.org"
        base_1, base_2, base_3, base_4 = await asyncio.gather(
            *(default_bot.send_message(chat_id, telegram_url) for _ in range(4))
        )

        # First test just the default passing:
        coro1 = base_1.edit_text(github_url)
        # Next test fusion of both LPOs:
        coro2 = base_2.edit_text(
            github_url,
            link_preview_options=LinkPreviewOptions(url=website, prefer_large_media=True),
        )
        # Now test fusion + overriding of passed LPO:
        coro3 = base_3.edit_text(
            github_url,
            link_preview_options=LinkPreviewOptions(show_above_text=False, url=website),
        )
        # finally test explicitly setting to None
        coro4 = base_4.edit_text(github_url, link_preview_options=None)

        msgs = asyncio.gather(coro1, coro2, coro3, coro4)
        msg1, msg2, msg3, msg4 = await msgs
        assert msg1.link_preview_options
        assert msg1.link_preview_options.show_above_text

        assert msg2.link_preview_options
        assert msg2.link_preview_options.show_above_text
        assert msg2.link_preview_options.url == website
        assert msg2.link_preview_options.prefer_large_media  # Now works correctly using new url..

        assert msg3.link_preview_options
        assert not msg3.link_preview_options.show_above_text
        assert msg3.link_preview_options.url == website

        assert msg4.link_preview_options == LinkPreviewOptions(url=github_url)

    async def test_send_message_entities(self, bot, chat_id):
        test_string = "Italic Bold Code Spoiler"
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
            MessageEntity(MessageEntity.SPOILER, 17, 7),
        ]
        message = await bot.send_message(chat_id=chat_id, text=test_string, entities=entities)
        assert message.text == test_string
        assert message.entities == tuple(entities)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_message_default_parse_mode(self, default_bot, chat_id):
        test_string = "Italic Bold Code"
        test_markdown_string = "_Italic_ *Bold* `Code`"

        tasks = asyncio.gather(
            *(
                default_bot.send_message(chat_id, test_markdown_string, **i)
                for i in ({}, {"parse_mode": None}, {"parse_mode": "HTML"})
            )
        )
        msg1, msg2, msg3 = await tasks
        assert msg1.text_markdown == test_markdown_string
        assert msg1.text == test_string

        assert msg2.text == test_markdown_string
        assert msg2.text_markdown == escape_markdown(test_markdown_string)

        assert msg3.text == test_markdown_string
        assert msg3.text_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_message_default_protect_content(self, default_bot, chat_id):
        tasks = asyncio.gather(
            default_bot.send_message(chat_id, "test"),
            default_bot.send_message(chat_id, "test", protect_content=False),
        )
        to_check, no_protect = await tasks
        assert to_check.has_protected_content
        assert not no_protect.has_protected_content

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_message_default_allow_sending_without_reply(
        self, default_bot, chat_id, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_message(
                chat_id,
                "test",
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_message(
                chat_id, "test", reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to reply not found"):
                await default_bot.send_message(
                    chat_id, "test", reply_to_message_id=reply_to_message.message_id
                )

    async def test_get_set_my_default_administrator_rights(self, bot):
        # Test that my default administrator rights for group are as all False
        assert await bot.set_my_default_administrator_rights()  # clear any set rights
        my_admin_rights_grp = await bot.get_my_default_administrator_rights()
        assert isinstance(my_admin_rights_grp, ChatAdministratorRights)
        assert all(not getattr(my_admin_rights_grp, at) for at in my_admin_rights_grp.__slots__)

        # Test setting my default admin rights for channel
        my_rights = ChatAdministratorRights.all_rights()
        assert await bot.set_my_default_administrator_rights(my_rights, for_channels=True)
        my_admin_rights_ch = await bot.get_my_default_administrator_rights(for_channels=True)
        assert my_admin_rights_ch.can_invite_users is my_rights.can_invite_users
        # tg bug? is_anonymous is False despite setting it True for channels:
        assert my_admin_rights_ch.is_anonymous is not my_rights.is_anonymous

        assert my_admin_rights_ch.can_manage_chat is my_rights.can_manage_chat
        assert my_admin_rights_ch.can_delete_messages is my_rights.can_delete_messages
        assert my_admin_rights_ch.can_edit_messages is my_rights.can_edit_messages
        assert my_admin_rights_ch.can_post_messages is my_rights.can_post_messages
        assert my_admin_rights_ch.can_change_info is my_rights.can_change_info
        assert my_admin_rights_ch.can_promote_members is my_rights.can_promote_members
        assert my_admin_rights_ch.can_restrict_members is my_rights.can_restrict_members
        assert my_admin_rights_ch.can_pin_messages is None  # Not returned for channels
        assert my_admin_rights_ch.can_manage_topics is None  # Not returned for channels

    async def test_get_set_chat_menu_button(self, bot, chat_id):
        # Test our chat menu button is commands-
        menu_button = await bot.get_chat_menu_button()
        assert isinstance(menu_button, MenuButton)
        assert isinstance(menu_button, MenuButtonCommands)
        assert menu_button.type == MenuButtonType.COMMANDS

        # Test setting our chat menu button to Webapp.
        my_menu = MenuButtonWebApp("click me!", WebAppInfo("https://telegram.org/"))
        assert await bot.set_chat_menu_button(chat_id=chat_id, menu_button=my_menu)
        menu_button = await bot.get_chat_menu_button(chat_id)
        assert isinstance(menu_button, MenuButtonWebApp)
        assert menu_button.type == MenuButtonType.WEB_APP
        assert menu_button.text == my_menu.text
        assert menu_button.web_app.url == my_menu.web_app.url

        assert await bot.set_chat_menu_button(chat_id=chat_id, menu_button=MenuButtonDefault())
        menu_button = await bot.get_chat_menu_button(chat_id=chat_id)
        assert isinstance(menu_button, MenuButtonDefault)

    async def test_set_and_get_my_commands(self, bot):
        commands = [BotCommand("cmd1", "descr1"), ["cmd2", "descr2"]]
        assert await bot.set_my_commands([])
        assert await bot.get_my_commands() == ()
        assert await bot.set_my_commands(commands)

        for i, bc in enumerate(await bot.get_my_commands()):
            assert bc.command == f"cmd{i + 1}"
            assert bc.description == f"descr{i + 1}"

    async def test_get_set_delete_my_commands_with_scope(self, bot, super_group_id, chat_id):
        group_cmds = [BotCommand("group_cmd", "visible to this supergroup only")]
        private_cmds = [BotCommand("private_cmd", "visible to this private chat only")]
        group_scope = BotCommandScopeChat(super_group_id)
        private_scope = BotCommandScopeChat(chat_id)

        # Set supergroup command list with lang code and check if the same can be returned from api
        assert await bot.set_my_commands(group_cmds, scope=group_scope, language_code="en")
        gotten_group_cmds = await bot.get_my_commands(scope=group_scope, language_code="en")

        assert len(gotten_group_cmds) == len(group_cmds)
        assert gotten_group_cmds[0].command == group_cmds[0].command

        # Set private command list and check if same can be returned from the api
        assert await bot.set_my_commands(private_cmds, scope=private_scope)
        gotten_private_cmd = await bot.get_my_commands(scope=private_scope)

        assert len(gotten_private_cmd) == len(private_cmds)
        assert gotten_private_cmd[0].command == private_cmds[0].command

        # Delete command list from that supergroup and private chat-
        tasks = asyncio.gather(
            bot.delete_my_commands(private_scope),
            bot.delete_my_commands(group_scope, "en"),
        )
        assert all(await tasks)

        # Check if its been deleted-
        tasks = asyncio.gather(
            bot.get_my_commands(private_scope),
            bot.get_my_commands(group_scope, "en"),
        )
        deleted_priv_cmds, deleted_grp_cmds = await tasks

        assert len(deleted_grp_cmds) == 0 == len(group_cmds) - 1
        assert len(deleted_priv_cmds) == 0 == len(private_cmds) - 1

        await bot.delete_my_commands()  # Delete commands from default scope
        assert len(await bot.get_my_commands()) == 0

    async def test_copy_message_without_reply(self, bot, chat_id, media_message):
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="test", callback_data="test2")]]
        )

        returned = await bot.copy_message(
            chat_id,
            from_chat_id=chat_id,
            message_id=media_message.message_id,
            caption="<b>Test</b>",
            parse_mode=ParseMode.HTML,
            reply_to_message_id=media_message.message_id,
            reply_markup=keyboard,
        )
        # we send a temp message which replies to the returned message id in order to get a
        # message object
        temp_message = await bot.send_message(
            chat_id, "test", reply_to_message_id=returned.message_id
        )
        message = temp_message.reply_to_message
        assert message.chat_id == int(chat_id)
        assert message.caption == "Test"
        assert len(message.caption_entities) == 1
        assert message.reply_markup == keyboard

    @pytest.mark.parametrize(
        "default_bot",
        [
            ({"parse_mode": ParseMode.HTML, "allow_sending_without_reply": True}),
            ({"parse_mode": None, "allow_sending_without_reply": True}),
            ({"parse_mode": None, "allow_sending_without_reply": False}),
        ],
        indirect=["default_bot"],
    )
    async def test_copy_message_with_default(self, default_bot, chat_id, media_message):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if not default_bot.defaults.allow_sending_without_reply:
            with pytest.raises(BadRequest, match="not found"):
                await default_bot.copy_message(
                    chat_id,
                    from_chat_id=chat_id,
                    message_id=media_message.message_id,
                    caption="<b>Test</b>",
                    reply_to_message_id=reply_to_message.message_id,
                )
            return
        returned = await default_bot.copy_message(
            chat_id,
            from_chat_id=chat_id,
            message_id=media_message.message_id,
            caption="<b>Test</b>",
            reply_to_message_id=reply_to_message.message_id,
        )
        # we send a temp message which replies to the returned message id in order to get a
        # message object
        temp_message = await default_bot.send_message(
            chat_id, "test", reply_to_message_id=returned.message_id
        )
        message = temp_message.reply_to_message
        if default_bot.defaults.parse_mode:
            assert len(message.caption_entities) == 1
        else:
            assert len(message.caption_entities) == 0

    async def test_copy_messages(self, bot, chat_id):
        tasks = asyncio.gather(
            bot.send_message(chat_id, text="will be copied 1"),
            bot.send_message(chat_id, text="will be copied 2"),
        )
        msg1, msg2 = await tasks

        copy_messages = await bot.copy_messages(
            chat_id, from_chat_id=chat_id, message_ids=(msg1.message_id, msg2.message_id)
        )
        assert isinstance(copy_messages, tuple)

        tasks = asyncio.gather(
            bot.send_message(chat_id, "temp 1", reply_to_message_id=copy_messages[0].message_id),
            bot.send_message(chat_id, "temp 2", reply_to_message_id=copy_messages[1].message_id),
        )
        temp_msg1, temp_msg2 = await tasks

        forward_msg1 = temp_msg1.reply_to_message
        forward_msg2 = temp_msg2.reply_to_message

        assert forward_msg1.text == msg1.text
        assert forward_msg2.text == msg2.text

    # Continue testing arbitrary callback data here with actual requests:
    async def test_replace_callback_data_send_message(self, cdc_bot, chat_id):
        bot = cdc_bot

        try:
            replace_button = InlineKeyboardButton(text="replace", callback_data="replace_test")
            no_replace_button = InlineKeyboardButton(
                text="no_replace", url="http://python-telegram-bot.org/"
            )
            reply_markup = InlineKeyboardMarkup.from_row(
                [
                    replace_button,
                    no_replace_button,
                ]
            )
            message = await bot.send_message(
                chat_id=chat_id, text="test", reply_markup=reply_markup
            )
            inline_keyboard = message.reply_markup.inline_keyboard

            assert inline_keyboard[0][1] == no_replace_button
            assert inline_keyboard[0][0] == replace_button
            keyboard = next(iter(bot.callback_data_cache._keyboard_data))
            data = next(
                iter(bot.callback_data_cache._keyboard_data[keyboard].button_data.values())
            )
            assert data == "replace_test"
        finally:
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    async def test_replace_callback_data_stop_poll_and_repl_to_message(self, cdc_bot, chat_id):
        bot = cdc_bot

        poll_message = await bot.send_poll(chat_id=chat_id, question="test", options=["1", "2"])
        try:
            replace_button = InlineKeyboardButton(text="replace", callback_data="replace_test")
            no_replace_button = InlineKeyboardButton(
                text="no_replace", url="http://python-telegram-bot.org/"
            )
            reply_markup = InlineKeyboardMarkup.from_row(
                [
                    replace_button,
                    no_replace_button,
                ]
            )
            await poll_message.stop_poll(reply_markup=reply_markup)
            helper_message = await poll_message.reply_text("temp", quote=True)
            message = helper_message.reply_to_message
            inline_keyboard = message.reply_markup.inline_keyboard

            assert inline_keyboard[0][1] == no_replace_button
            assert inline_keyboard[0][0] == replace_button
            keyboard = next(iter(bot.callback_data_cache._keyboard_data))
            data = next(
                iter(bot.callback_data_cache._keyboard_data[keyboard].button_data.values())
            )
            assert data == "replace_test"
        finally:
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    async def test_replace_callback_data_copy_message(self, cdc_bot, chat_id):
        """This also tests that data is inserted into the buttons of message.reply_to_message
        where message is the return value of a bot method"""
        bot = cdc_bot

        original_message = await bot.send_message(chat_id=chat_id, text="original")
        try:
            replace_button = InlineKeyboardButton(text="replace", callback_data="replace_test")
            no_replace_button = InlineKeyboardButton(
                text="no_replace", url="http://python-telegram-bot.org/"
            )
            reply_markup = InlineKeyboardMarkup.from_row(
                [
                    replace_button,
                    no_replace_button,
                ]
            )
            message_id = await original_message.copy(chat_id=chat_id, reply_markup=reply_markup)
            helper_message = await bot.send_message(
                chat_id=chat_id, reply_to_message_id=message_id.message_id, text="temp"
            )
            message = helper_message.reply_to_message
            inline_keyboard = message.reply_markup.inline_keyboard

            assert inline_keyboard[0][1] == no_replace_button
            assert inline_keyboard[0][0] == replace_button
            keyboard = next(iter(bot.callback_data_cache._keyboard_data))
            data = next(
                iter(bot.callback_data_cache._keyboard_data[keyboard].button_data.values())
            )
            assert data == "replace_test"
        finally:
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    async def test_get_chat_arbitrary_callback_data(self, channel_id, cdc_bot):
        bot = cdc_bot

        try:
            reply_markup = InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text="text", callback_data="callback_data")
            )

            message = await bot.send_message(
                channel_id, text="get_chat_arbitrary_callback_data", reply_markup=reply_markup
            )
            await message.pin()

            keyboard = next(iter(bot.callback_data_cache._keyboard_data))
            data = next(
                iter(bot.callback_data_cache._keyboard_data[keyboard].button_data.values())
            )
            assert data == "callback_data"

            chat = await bot.get_chat(channel_id)
            assert chat.pinned_message == message
            assert chat.pinned_message.reply_markup == reply_markup
            assert await message.unpin()  # (not placed in finally block since msg can be unbound)
        finally:
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    async def test_arbitrary_callback_data_get_chat_no_pinned_message(
        self, super_group_id, cdc_bot
    ):
        bot = cdc_bot
        await bot.unpin_all_chat_messages(super_group_id)

        try:
            chat = await bot.get_chat(super_group_id)

            assert isinstance(chat, Chat)
            assert int(chat.id) == int(super_group_id)
            assert chat.pinned_message is None
        finally:
            bot.callback_data_cache.clear_callback_data()
            bot.callback_data_cache.clear_callback_queries()

    async def test_set_get_my_description(self, bot):
        default_description = f"{bot.username} - default - {dtm.datetime.utcnow().isoformat()}"
        en_description = f"{bot.username} - en - {dtm.datetime.utcnow().isoformat()}"
        de_description = f"{bot.username} - de - {dtm.datetime.utcnow().isoformat()}"

        # Set the descriptions
        assert all(
            await asyncio.gather(
                bot.set_my_description(default_description),
                bot.set_my_description(en_description, language_code="en"),
                bot.set_my_description(de_description, language_code="de"),
            )
        )

        # Check that they were set correctly
        assert await asyncio.gather(
            bot.get_my_description(), bot.get_my_description("en"), bot.get_my_description("de")
        ) == [
            BotDescription(default_description),
            BotDescription(en_description),
            BotDescription(de_description),
        ]

        # Delete the descriptions
        assert all(
            await asyncio.gather(
                bot.set_my_description(None),
                bot.set_my_description(None, language_code="en"),
                bot.set_my_description(None, language_code="de"),
            )
        )

        # Check that they were deleted correctly
        assert await asyncio.gather(
            bot.get_my_description(), bot.get_my_description("en"), bot.get_my_description("de")
        ) == 3 * [BotDescription("")]

    async def test_set_get_my_short_description(self, bot):
        default_short_description = (
            f"{bot.username} - default - {dtm.datetime.utcnow().isoformat()}"
        )
        en_short_description = f"{bot.username} - en - {dtm.datetime.utcnow().isoformat()}"
        de_short_description = f"{bot.username} - de - {dtm.datetime.utcnow().isoformat()}"

        # Set the short_descriptions
        assert all(
            await asyncio.gather(
                bot.set_my_short_description(default_short_description),
                bot.set_my_short_description(en_short_description, language_code="en"),
                bot.set_my_short_description(de_short_description, language_code="de"),
            )
        )

        # Check that they were set correctly
        assert await asyncio.gather(
            bot.get_my_short_description(),
            bot.get_my_short_description("en"),
            bot.get_my_short_description("de"),
        ) == [
            BotShortDescription(default_short_description),
            BotShortDescription(en_short_description),
            BotShortDescription(de_short_description),
        ]

        # Delete the short_descriptions
        assert all(
            await asyncio.gather(
                bot.set_my_short_description(None),
                bot.set_my_short_description(None, language_code="en"),
                bot.set_my_short_description(None, language_code="de"),
            )
        )

        # Check that they were deleted correctly
        assert await asyncio.gather(
            bot.get_my_short_description(),
            bot.get_my_short_description("en"),
            bot.get_my_short_description("de"),
        ) == 3 * [BotShortDescription("")]

    async def test_set_message_reaction(self, bot, chat_id, message):
        assert await bot.set_message_reaction(
            chat_id, message.message_id, ReactionEmoji.THUMBS_DOWN, True
        )

    @pytest.mark.parametrize("bot_class", [Bot, ExtBot])
    async def test_do_api_request_warning_known_method(self, bot, bot_class):
        with pytest.warns(PTBDeprecationWarning, match="Please use 'Bot.get_me'") as record:
            await bot_class(bot.token).do_api_request("get_me")

        assert record[0].filename == __file__, "Wrong stack level!"

    async def test_do_api_request_unknown_method(self, bot):
        with pytest.raises(EndPointNotFound, match="'unknownEndpoint' not found"):
            await bot.do_api_request("unknown_endpoint")

    async def test_do_api_request_invalid_token(self, bot):
        # we do not initialize the bot here on purpose b/c that's the case were we actually
        # do not know for sure if the token is invalid or the method was not found
        with pytest.raises(
            InvalidToken, match="token was rejected by Telegram or the endpoint 'getMe'"
        ):
            await Bot("invalid_token").do_api_request("get_me")

        # same test, but with a valid token bot and unknown endpoint
        with pytest.raises(
            InvalidToken, match="token was rejected by Telegram or the endpoint 'unknownEndpoint'"
        ):
            await Bot(bot.token).do_api_request("unknown_endpoint")

    @pytest.mark.parametrize("return_type", [Message, None])
    async def test_do_api_request_basic_and_files(self, bot, chat_id, return_type):
        result = await bot.do_api_request(
            "send_document",
            api_kwargs={
                "chat_id": chat_id,
                "caption": "test_caption",
                "document": InputFile(data_file("telegram.png").open("rb")),
            },
            return_type=return_type,
        )
        if return_type is None:
            assert isinstance(result, dict)
            result = Message.de_json(result, bot)

        assert isinstance(result, Message)
        assert result.chat_id == int(chat_id)
        assert result.caption == "test_caption"
        out = BytesIO()
        await (await result.document.get_file()).download_to_memory(out)
        out.seek(0)
        assert out.read() == data_file("telegram.png").open("rb").read()
        assert result.document.file_name == "telegram.png"

    @pytest.mark.parametrize("return_type", [Message, None])
    async def test_do_api_request_list_return_type(self, bot, chat_id, return_type):
        result = await bot.do_api_request(
            "send_media_group",
            api_kwargs={
                "chat_id": chat_id,
                "media": [
                    InputMediaDocument(
                        InputFile(
                            data_file("text_file.txt").open("rb"),
                            attach=True,
                        )
                    ),
                    InputMediaDocument(
                        InputFile(
                            data_file("local_file.txt").open("rb"),
                            attach=True,
                        )
                    ),
                ],
            },
            return_type=return_type,
        )
        if return_type is None:
            assert isinstance(result, list)
            for entry in result:
                assert isinstance(entry, dict)
            result = Message.de_list(result, bot)

        for message, file_name in zip(result, ("text_file.txt", "local_file.txt")):
            assert isinstance(message, Message)
            assert message.chat_id == int(chat_id)
            out = BytesIO()
            await (await message.document.get_file()).download_to_memory(out)
            out.seek(0)
            assert out.read() == data_file(file_name).open("rb").read()
            assert message.document.file_name == file_name

    @pytest.mark.parametrize("return_type", [Message, None])
    async def test_do_api_request_bool_return_type(self, bot, chat_id, return_type):
        assert await bot.do_api_request("delete_my_commands", return_type=return_type) is True
