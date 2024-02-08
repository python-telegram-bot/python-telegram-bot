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
import time

import pytest

from telegram import (
    Chat,
    ChatBoost,
    ChatBoostRemoved,
    ChatBoostSourcePremium,
    ChatBoostUpdated,
    Update,
    User,
)
from telegram._utils.datetime import from_timestamp
from telegram.ext import CallbackContext, ChatBoostHandler
from tests.auxil.slots import mro_slots
from tests.test_update import all_types as really_all_types
from tests.test_update import params as all_params

# Remove "chat_boost" from params
params = [param for param in all_params for key in param if "chat_boost" not in key]
all_types = [param for param in really_all_types if "chat_boost" not in param]
ids = (*all_types, "callback_query_without_message")


@pytest.fixture(scope="class", params=params, ids=ids)
def false_update(request):
    return Update(update_id=2, **request.param)


def chat_boost():
    return ChatBoost(
        "1",
        from_timestamp(int(time.time())),
        from_timestamp(int(time.time())),
        ChatBoostSourcePremium(
            User(1, "first_name", False),
        ),
    )


@pytest.fixture(scope="module")
def removed_chat_boost():
    return ChatBoostRemoved(
        Chat(1, "group", username="chat"),
        "1",
        from_timestamp(int(time.time())),
        ChatBoostSourcePremium(
            User(1, "first_name", False),
        ),
    )


def removed_chat_boost_update():
    return Update(
        update_id=2,
        removed_chat_boost=ChatBoostRemoved(
            Chat(1, "group", username="chat"),
            "1",
            from_timestamp(int(time.time())),
            ChatBoostSourcePremium(
                User(1, "first_name", False),
            ),
        ),
    )


@pytest.fixture(scope="module")
def chat_boost_updated():
    return ChatBoostUpdated(Chat(1, "group", username="chat"), chat_boost())


def chat_boost_updated_update():
    return Update(
        update_id=2,
        chat_boost=ChatBoostUpdated(
            Chat(1, "group", username="chat"),
            chat_boost(),
        ),
    )


class TestChatBoostHandler:
    test_flag = False

    def test_slot_behaviour(self):
        action = ChatBoostHandler(self.cb_chat_boost_removed)
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    @pytest.fixture(autouse=True)
    def _reset(self):
        self.test_flag = False

    async def cb_chat_boost_updated(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(update.chat_boost, ChatBoostUpdated)
            and not isinstance(update.removed_chat_boost, ChatBoostRemoved)
        )

    async def cb_chat_boost_removed(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(update.removed_chat_boost, ChatBoostRemoved)
            and not isinstance(update.chat_boost, ChatBoostUpdated)
        )

    async def cb_chat_boost_any(self, update, context):
        self.test_flag = isinstance(context, CallbackContext) and (
            isinstance(update.removed_chat_boost, ChatBoostRemoved)
            or isinstance(update.chat_boost, ChatBoostUpdated)
        )

    @pytest.mark.parametrize(
        argnames=["allowed_types", "cb", "expected"],
        argvalues=[
            (ChatBoostHandler.CHAT_BOOST, "cb_chat_boost_updated", (True, False)),
            (ChatBoostHandler.REMOVED_CHAT_BOOST, "cb_chat_boost_removed", (False, True)),
            (ChatBoostHandler.ANY_CHAT_BOOST, "cb_chat_boost_any", (True, True)),
        ],
        ids=["CHAT_BOOST", "REMOVED_CHAT_BOOST", "ANY_CHAT_MEMBER"],
    )
    async def test_chat_boost_types(self, app, cb, expected, allowed_types):
        result_1, result_2 = expected

        update_type, other = chat_boost_updated_update(), removed_chat_boost_update()

        handler = ChatBoostHandler(getattr(self, cb), chat_boost_types=allowed_types)
        app.add_handler(handler)

        async with app:
            assert handler.check_update(update_type) == result_1
            await app.process_update(update_type)
            assert self.test_flag == result_1

            self.test_flag = False

            assert handler.check_update(other) == result_2
            await app.process_update(other)
            assert self.test_flag == result_2

    def test_other_update_types(self, false_update):
        handler = ChatBoostHandler(self.cb_chat_boost_removed)
        assert not handler.check_update(false_update)
        assert not handler.check_update(True)

    async def test_context(self, app):
        handler = ChatBoostHandler(self.cb_chat_boost_updated)
        app.add_handler(handler)

        async with app:
            await app.process_update(chat_boost_updated_update())
            assert self.test_flag

    def test_with_chat_id(self):
        update = chat_boost_updated_update()
        cb = self.cb_chat_boost_updated
        handler = ChatBoostHandler(cb, chat_id=1)
        assert handler.check_update(update)
        handler = ChatBoostHandler(cb, chat_id=[1])
        assert handler.check_update(update)
        handler = ChatBoostHandler(cb, chat_id=2, chat_username="@chat")
        assert handler.check_update(update)

        handler = ChatBoostHandler(cb, chat_id=2)
        assert not handler.check_update(update)
        handler = ChatBoostHandler(cb, chat_id=[2])
        assert not handler.check_update(update)

    def test_with_username(self):
        update = removed_chat_boost_update()
        cb = self.cb_chat_boost_removed
        handler = ChatBoostHandler(cb, chat_boost_types=0, chat_username="chat")
        assert handler.check_update(update)
        handler = ChatBoostHandler(cb, chat_boost_types=0, chat_username="@chat")
        assert handler.check_update(update)
        handler = ChatBoostHandler(cb, chat_boost_types=0, chat_username=["chat"])
        assert handler.check_update(update)
        handler = ChatBoostHandler(cb, chat_boost_types=0, chat_username=["@chat"])
        assert handler.check_update(update)
        handler = ChatBoostHandler(
            cb, chat_boost_types=0, chat_id=1, chat_username="@chat_something"
        )
        assert handler.check_update(update)

        handler = ChatBoostHandler(cb, chat_boost_types=0, chat_username="chat_b")
        assert not handler.check_update(update)
        handler = ChatBoostHandler(cb, chat_boost_types=0, chat_username="@chat_b")
        assert not handler.check_update(update)
        handler = ChatBoostHandler(cb, chat_boost_types=0, chat_username=["chat_b"])
        assert not handler.check_update(update)
        handler = ChatBoostHandler(cb, chat_boost_types=0, chat_username=["@chat_b"])
        assert not handler.check_update(update)

        update.removed_chat_boost.chat._unfreeze()
        update.removed_chat_boost.chat.username = None
        assert not handler.check_update(update)
