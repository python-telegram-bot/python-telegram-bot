#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
import datetime as dtm

import pytest

from telegram import (
    Bot,
    CallbackQuery,
    Chat,
    ChosenInlineResult,
    ManagedBotUpdated,
    Message,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
    User,
)
from telegram._utils.datetime import UTC
from telegram.ext import CallbackContext, JobQueue, ManagedBotUpdatedHandler
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
    return dtm.datetime.now(tz=UTC)


@pytest.fixture(scope="class")
def managed_bot_updated(bot):
    bmd = ManagedBotUpdated(
        user=User(1, "", False, username="user_a"),
        bot=User(2, "", True),
    )
    bmd.set_bot(bot)
    return bmd


@pytest.fixture
def managed_bot_updated_update(bot, managed_bot_updated):
    return Update(0, managed_bot=managed_bot_updated)


class TestManagedBotUpdatedHandler:
    test_flag = False

    def test_slot_behaviour(self):
        action = ManagedBotUpdatedHandler(self.callback)
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
            and isinstance(context.bot_data, dict)
            and isinstance(
                update.managed_bot,
                ManagedBotUpdated,
            )
        )

    def test_with_user_id(self, managed_bot_updated_update):
        handler = ManagedBotUpdatedHandler(self.callback, user_id=1)
        assert handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, user_id=[1])
        assert handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, user_id=2, username="@user_a")
        assert handler.check_update(managed_bot_updated_update)

        handler = ManagedBotUpdatedHandler(self.callback, user_id=2)
        assert not handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, user_id=[2])
        assert not handler.check_update(managed_bot_updated_update)

    def test_with_username(self, managed_bot_updated_update):
        handler = ManagedBotUpdatedHandler(self.callback, username="user_a")
        assert handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, username="@user_a")
        assert handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, username=["user_a"])
        assert handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, username=["@user_a"])
        assert handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, user_id=1, username="@user_b")
        assert handler.check_update(managed_bot_updated_update)

        handler = ManagedBotUpdatedHandler(self.callback, username="user_b")
        assert not handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, username="@user_b")
        assert not handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, username=["user_b"])
        assert not handler.check_update(managed_bot_updated_update)
        handler = ManagedBotUpdatedHandler(self.callback, username=["@user_b"])
        assert not handler.check_update(managed_bot_updated_update)

        managed_bot_updated_update.managed_bot.user._unfreeze()
        managed_bot_updated_update.managed_bot.user.username = None
        assert not handler.check_update(managed_bot_updated_update)

    def test_other_update_types(self, false_update):
        handler = ManagedBotUpdatedHandler(self.callback)
        assert not handler.check_update(false_update)
        assert not handler.check_update(True)

    async def test_context(self, app, managed_bot_updated_update):
        handler = ManagedBotUpdatedHandler(callback=self.callback)
        app.add_handler(handler)

        async with app:
            await app.process_update(managed_bot_updated_update)
            assert self.test_flag
