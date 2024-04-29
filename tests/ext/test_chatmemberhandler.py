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
import time

import pytest

from telegram import (
    Bot,
    CallbackQuery,
    Chat,
    ChatMember,
    ChatMemberUpdated,
    ChosenInlineResult,
    Message,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
    User,
)
from telegram._utils.datetime import from_timestamp
from telegram.ext import CallbackContext, ChatMemberHandler, JobQueue
from tests.auxil.slots import mro_slots

message = Message(1, None, Chat(1, ""), from_user=User(1, "", False), text="Text")

params = [
    {"message": message},
    {"edited_message": message},
    {"callback_query": CallbackQuery(1, User(1, "", False), "chat", message=message)},
    {"channel_post": message},
    {"edited_channel_post": message},
    {"chosen_inline_result": ChosenInlineResult("id", User(1, "", False), "")},
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
    "chosen_inline_result",
    "shipping_query",
    "pre_checkout_query",
    "callback_query_without_message",
)


@pytest.fixture(scope="class", params=params, ids=ids)
def false_update(request):
    return Update(update_id=2, **request.param)


@pytest.fixture(scope="class")
def chat_member_updated():
    return ChatMemberUpdated(
        Chat(1, "chat"),
        User(1, "", False),
        from_timestamp(int(time.time())),
        ChatMember(User(1, "", False), ChatMember.OWNER),
        ChatMember(User(1, "", False), ChatMember.OWNER),
    )


@pytest.fixture()
def chat_member(bot, chat_member_updated):
    update = Update(0, my_chat_member=chat_member_updated)
    update._unfreeze()
    return update


class TestChatMemberHandler:
    test_flag = False

    def test_slot_behaviour(self):
        action = ChatMemberHandler(self.callback)
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

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
            and isinstance(context.user_data, dict)
            and isinstance(context.chat_data, dict)
            and isinstance(context.bot_data, dict)
            and isinstance(update.chat_member or update.my_chat_member, ChatMemberUpdated)
        )

    @pytest.mark.parametrize(
        argnames=["allowed_types", "expected"],
        argvalues=[
            (ChatMemberHandler.MY_CHAT_MEMBER, (True, False)),
            (ChatMemberHandler.CHAT_MEMBER, (False, True)),
            (ChatMemberHandler.ANY_CHAT_MEMBER, (True, True)),
        ],
        ids=["MY_CHAT_MEMBER", "CHAT_MEMBER", "ANY_CHAT_MEMBER"],
    )
    async def test_chat_member_types(
        self, app, chat_member_updated, chat_member, expected, allowed_types
    ):
        result_1, result_2 = expected

        handler = ChatMemberHandler(self.callback, chat_member_types=allowed_types)
        app.add_handler(handler)

        async with app:
            assert handler.check_update(chat_member) == result_1
            await app.process_update(chat_member)
            assert self.test_flag == result_1

            self.test_flag = False
            chat_member.my_chat_member = None
            chat_member.chat_member = chat_member_updated

            assert handler.check_update(chat_member) == result_2
            await app.process_update(chat_member)
            assert self.test_flag == result_2

    def test_other_update_types(self, false_update):
        handler = ChatMemberHandler(self.callback)
        assert not handler.check_update(false_update)
        assert not handler.check_update(True)

    async def test_context(self, app, chat_member):
        handler = ChatMemberHandler(self.callback)
        app.add_handler(handler)

        async with app:
            await app.process_update(chat_member)
            assert self.test_flag
