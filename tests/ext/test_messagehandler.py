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
import re

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
from telegram.ext import CallbackContext, JobQueue, MessageHandler, filters
from telegram.ext.filters import MessageFilter
from tests.auxil.slots import mro_slots

message = Message(1, None, Chat(1, ""), from_user=User(1, "", False), text="Text")

params = [
    {"callback_query": CallbackQuery(1, User(1, "", False), "chat", message=message)},
    {"inline_query": InlineQuery(1, User(1, "", False), "", "")},
    {"chosen_inline_result": ChosenInlineResult("id", User(1, "", False), "")},
    {"shipping_query": ShippingQuery("id", User(1, "", False), "", None)},
    {"pre_checkout_query": PreCheckoutQuery("id", User(1, "", False), "", 0, "")},
    {"callback_query": CallbackQuery(1, User(1, "", False), "chat")},
]

ids = (
    "callback_query",
    "inline_query",
    "chosen_inline_result",
    "shipping_query",
    "pre_checkout_query",
    "callback_query_without_message",
)


@pytest.fixture(scope="class", params=params, ids=ids)
def false_update(request):
    return Update(update_id=1, **request.param)


@pytest.fixture(scope="class")
def message(bot):
    message = Message(1, None, Chat(1, ""), from_user=User(1, "", False))
    message._unfreeze()
    message.chat._unfreeze()
    message.set_bot(bot)
    return message


class TestMessageHandler:
    test_flag = False
    SRE_TYPE = type(re.match("", ""))

    def test_slot_behaviour(self):
        handler = MessageHandler(filters.ALL, self.callback)
        for attr in handler.__slots__:
            assert getattr(handler, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"

    @pytest.fixture(autouse=True)
    def _reset(self):
        self.test_flag = False

    async def callback(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, Update)
            and isinstance(context.update_queue, asyncio.Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.chat_data, dict)
            and isinstance(context.bot_data, dict)
            and (
                (
                    isinstance(context.user_data, dict)
                    and (
                        isinstance(update.message, Message)
                        or isinstance(update.edited_message, Message)
                    )
                )
                or (
                    context.user_data is None
                    and (
                        isinstance(update.channel_post, Message)
                        or isinstance(update.edited_channel_post, Message)
                    )
                )
            )
        )

    def callback_regex1(self, update, context):
        if context.matches:
            types = all(type(res) is self.SRE_TYPE for res in context.matches)
            num = len(context.matches) == 1
            self.test_flag = types and num

    def callback_regex2(self, update, context):
        if context.matches:
            types = all(type(res) is self.SRE_TYPE for res in context.matches)
            num = len(context.matches) == 2
            self.test_flag = types and num

    def test_with_filter(self, message):
        handler = MessageHandler(filters.ChatType.GROUP, self.callback)

        message.chat.type = "group"
        assert handler.check_update(Update(0, message))

        message.chat.type = "private"
        assert not handler.check_update(Update(0, message))

    def test_callback_query_with_filter(self, message):
        class TestFilter(filters.UpdateFilter):
            flag = False

            def filter(self, u):
                self.flag = True

        test_filter = TestFilter()
        handler = MessageHandler(test_filter, self.callback)

        update = Update(1, callback_query=CallbackQuery(1, None, None, message=message))

        assert update.effective_message
        assert not handler.check_update(update)
        assert not test_filter.flag

    def test_specific_filters(self, message):
        f = (
            ~filters.UpdateType.MESSAGES
            & ~filters.UpdateType.CHANNEL_POST
            & filters.UpdateType.EDITED_CHANNEL_POST
        )
        handler = MessageHandler(f, self.callback)

        assert not handler.check_update(Update(0, edited_message=message))
        assert not handler.check_update(Update(0, message=message))
        assert not handler.check_update(Update(0, channel_post=message))
        assert handler.check_update(Update(0, edited_channel_post=message))

    def test_other_update_types(self, false_update):
        handler = MessageHandler(None, self.callback)
        assert not handler.check_update(false_update)
        assert not handler.check_update("string")

    def test_filters_returns_empty_dict(self):
        class DataFilter(MessageFilter):
            data_filter = True

            def filter(self, msg: Message):
                return {}

        handler = MessageHandler(DataFilter(), self.callback)
        assert handler.check_update(Update(0, message)) is False

    async def test_context(self, app, message):
        handler = MessageHandler(
            None,
            self.callback,
        )
        app.add_handler(handler)

        async with app:
            await app.process_update(Update(0, message=message))
            assert self.test_flag

            self.test_flag = False
            await app.process_update(Update(0, edited_message=message))
            assert self.test_flag

            self.test_flag = False
            await app.process_update(Update(0, channel_post=message))
            assert self.test_flag

            self.test_flag = False
            await app.process_update(Update(0, edited_channel_post=message))
            assert self.test_flag

    async def test_context_regex(self, app, message):
        handler = MessageHandler(filters.Regex("one two"), self.callback_regex1)
        app.add_handler(handler)

        async with app:
            message.text = "not it"
            await app.process_update(Update(0, message))
            assert not self.test_flag

            message.text += " one two now it is"
            await app.process_update(Update(0, message))
            assert self.test_flag

    async def test_context_multiple_regex(self, app, message):
        handler = MessageHandler(filters.Regex("one") & filters.Regex("two"), self.callback_regex2)
        app.add_handler(handler)

        async with app:
            message.text = "not it"
            await app.process_update(Update(0, message))
            assert not self.test_flag

            message.text += " one two now it is"
            await app.process_update(Update(0, message))
            assert self.test_flag
