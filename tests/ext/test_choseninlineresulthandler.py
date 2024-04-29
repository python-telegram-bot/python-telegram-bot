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

import pytest

from telegram import (
    Bot,
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
from telegram.ext import CallbackContext, ChosenInlineResultHandler, JobQueue
from tests.auxil.slots import mro_slots

message = Message(1, None, Chat(1, ""), from_user=User(1, "", False), text="Text")

params = [
    {"message": message},
    {"edited_message": message},
    {"callback_query": CallbackQuery(1, User(1, "", False), "chat", message=message)},
    {"channel_post": message},
    {"edited_channel_post": message},
    {"inline_query": InlineQuery(1, User(1, "", False), "", "")},
    {"shipping_query": ShippingQuery("id", User(1, "", False), "", None)},
    {"pre_checkout_query": PreCheckoutQuery("id", User(1, "", False), "", 0, "")},
    {"callback_query": CallbackQuery(1, User(1, "", False), "chat")},
]

ids = (
    "message",
    "edited_message",
    "callback_query",
    "channel_post",
    "edited_channel_post",
    "inline_query",
    "shipping_query",
    "pre_checkout_query",
    "callback_query_without_message",
)


@pytest.fixture(scope="class", params=params, ids=ids)
def false_update(request):
    return Update(update_id=1, **request.param)


@pytest.fixture(scope="class")
def chosen_inline_result():
    out = Update(
        1,
        chosen_inline_result=ChosenInlineResult("result_id", User(1, "test_user", False), "query"),
    )
    out._unfreeze()
    out.chosen_inline_result._unfreeze()
    return out


class TestChosenInlineResultHandler:
    test_flag = False

    @pytest.fixture(autouse=True)
    def _reset(self):
        self.test_flag = False

    def test_slot_behaviour(self):
        handler = ChosenInlineResultHandler(self.callback_basic)
        for attr in handler.__slots__:
            assert getattr(handler, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"

    def callback_basic(self, update, context):
        test_bot = isinstance(context.bot, Bot)
        test_update = isinstance(update, Update)
        self.test_flag = test_bot and test_update

    def callback_data_1(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) or (chat_data is not None)

    def callback_data_2(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) and (chat_data is not None)

    def callback_queue_1(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) or (update_queue is not None)

    def callback_queue_2(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) and (update_queue is not None)

    async def callback(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, Update)
            and isinstance(context.update_queue, asyncio.Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.user_data, dict)
            and context.chat_data is None
            and isinstance(context.bot_data, dict)
            and isinstance(update.chosen_inline_result, ChosenInlineResult)
        )

    def callback_pattern(self, update, context):
        if context.matches[0].groups():
            self.test_flag = context.matches[0].groups() == ("res", "_id")
        if context.matches[0].groupdict():
            self.test_flag = context.matches[0].groupdict() == {"begin": "res", "end": "_id"}

    def test_other_update_types(self, false_update):
        handler = ChosenInlineResultHandler(self.callback_basic)
        assert not handler.check_update(false_update)

    async def test_context(self, app, chosen_inline_result):
        handler = ChosenInlineResultHandler(self.callback)
        app.add_handler(handler)

        async with app:
            await app.process_update(chosen_inline_result)
        assert self.test_flag

    def test_with_pattern(self, chosen_inline_result):
        handler = ChosenInlineResultHandler(self.callback_basic, pattern=".*ult.*")

        assert handler.check_update(chosen_inline_result)

        chosen_inline_result.chosen_inline_result.result_id = "nothing here"
        assert not handler.check_update(chosen_inline_result)
        chosen_inline_result.chosen_inline_result.result_id = "result_id"

    async def test_context_pattern(self, app, chosen_inline_result):
        handler = ChosenInlineResultHandler(
            self.callback_pattern, pattern=r"(?P<begin>.*)ult(?P<end>.*)"
        )
        app.add_handler(handler)
        async with app:
            await app.process_update(chosen_inline_result)
            assert self.test_flag

            app.remove_handler(handler)
            handler = ChosenInlineResultHandler(self.callback_pattern, pattern=r"(res)ult(.*)")
            app.add_handler(handler)

            await app.process_update(chosen_inline_result)
            assert self.test_flag
