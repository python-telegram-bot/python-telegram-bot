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

import pytest

from telegram import (
    Bot,
    BusinessMessagesDeleted,
    CallbackQuery,
    Chat,
    ChosenInlineResult,
    Message,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
    User,
)
from telegram._utils.datetime import UTC
from telegram.ext import BusinessMessagesDeletedHandler, CallbackContext, JobQueue
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
def time():
    return datetime.datetime.now(tz=UTC)


@pytest.fixture(scope="class")
def business_messages_deleted(bot):
    bmd = BusinessMessagesDeleted(
        business_connection_id="1",
        chat=Chat(1, Chat.PRIVATE, username="user_a"),
        message_ids=[1, 2, 3],
    )
    bmd.set_bot(bot)
    return bmd


@pytest.fixture()
def business_messages_deleted_update(bot, business_messages_deleted):
    return Update(0, deleted_business_messages=business_messages_deleted)


class TestBusinessMessagesDeletedHandler:
    test_flag = False

    def test_slot_behaviour(self):
        action = BusinessMessagesDeletedHandler(self.callback)
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
            and isinstance(context.chat_data, dict)
            and isinstance(context.bot_data, dict)
            and isinstance(
                update.deleted_business_messages,
                BusinessMessagesDeleted,
            )
        )

    def test_with_chat_id(self, business_messages_deleted_update):
        handler = BusinessMessagesDeletedHandler(self.callback, chat_id=1)
        assert handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, chat_id=[1])
        assert handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, chat_id=2, username="@user_a")
        assert handler.check_update(business_messages_deleted_update)

        handler = BusinessMessagesDeletedHandler(self.callback, chat_id=2)
        assert not handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, chat_id=[2])
        assert not handler.check_update(business_messages_deleted_update)

    def test_with_username(self, business_messages_deleted_update):
        handler = BusinessMessagesDeletedHandler(self.callback, username="user_a")
        assert handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, username="@user_a")
        assert handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, username=["user_a"])
        assert handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, username=["@user_a"])
        assert handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, chat_id=1, username="@user_b")
        assert handler.check_update(business_messages_deleted_update)

        handler = BusinessMessagesDeletedHandler(self.callback, username="user_b")
        assert not handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, username="@user_b")
        assert not handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, username=["user_b"])
        assert not handler.check_update(business_messages_deleted_update)
        handler = BusinessMessagesDeletedHandler(self.callback, username=["@user_b"])
        assert not handler.check_update(business_messages_deleted_update)

        business_messages_deleted_update.deleted_business_messages.chat._unfreeze()
        business_messages_deleted_update.deleted_business_messages.chat.username = None
        assert not handler.check_update(business_messages_deleted_update)

    def test_other_update_types(self, false_update):
        handler = BusinessMessagesDeletedHandler(self.callback)
        assert not handler.check_update(false_update)
        assert not handler.check_update(True)

    async def test_context(self, app, business_messages_deleted_update):
        handler = BusinessMessagesDeletedHandler(callback=self.callback)
        app.add_handler(handler)

        async with app:
            await app.process_update(business_messages_deleted_update)
            assert self.test_flag
