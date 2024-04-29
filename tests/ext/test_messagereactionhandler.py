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
    CallbackQuery,
    Chat,
    ChosenInlineResult,
    Message,
    MessageReactionCountUpdated,
    MessageReactionUpdated,
    PreCheckoutQuery,
    ReactionCount,
    ReactionTypeEmoji,
    ShippingQuery,
    Update,
    User,
)
from telegram._utils.datetime import UTC
from telegram.ext import CallbackContext, JobQueue, MessageReactionHandler
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
def message_reaction_updated(time, bot):
    mr = MessageReactionUpdated(
        chat=Chat(1, Chat.SUPERGROUP),
        message_id=1,
        date=time,
        old_reaction=[ReactionTypeEmoji("👍")],
        new_reaction=[ReactionTypeEmoji("👎")],
        user=User(1, "user_a", False),
        actor_chat=Chat(2, Chat.SUPERGROUP),
    )
    mr.set_bot(bot)
    mr._unfreeze()
    mr.chat._unfreeze()
    mr.user._unfreeze()
    return mr


@pytest.fixture(scope="class")
def message_reaction_count_updated(time, bot):
    mr = MessageReactionCountUpdated(
        chat=Chat(1, Chat.SUPERGROUP),
        message_id=1,
        date=time,
        reactions=[
            ReactionCount(ReactionTypeEmoji("👍"), 1),
            ReactionCount(ReactionTypeEmoji("👎"), 1),
        ],
    )
    mr.set_bot(bot)
    mr._unfreeze()
    mr.chat._unfreeze()
    return mr


@pytest.fixture()
def message_reaction_update(bot, message_reaction_updated):
    return Update(0, message_reaction=message_reaction_updated)


@pytest.fixture()
def message_reaction_count_update(bot, message_reaction_count_updated):
    return Update(0, message_reaction_count=message_reaction_count_updated)


class TestMessageReactionHandler:
    test_flag = False

    def test_slot_behaviour(self):
        action = MessageReactionHandler(self.callback)
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    @pytest.fixture(autouse=True)
    def _reset(self):
        self.test_flag = False

    async def callback(self, update: Update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, Update)
            and isinstance(context.update_queue, asyncio.Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.user_data, dict if update.effective_user else type(None))
            and isinstance(context.chat_data, dict)
            and isinstance(context.bot_data, dict)
            and (
                isinstance(
                    update.message_reaction,
                    MessageReactionUpdated,
                )
                or isinstance(update.message_reaction_count, MessageReactionCountUpdated)
            )
        )

    def test_other_update_types(self, false_update):
        handler = MessageReactionHandler(self.callback)
        assert not handler.check_update(false_update)
        assert not handler.check_update(True)

    async def test_context(self, app, message_reaction_update, message_reaction_count_update):
        handler = MessageReactionHandler(callback=self.callback)
        app.add_handler(handler)

        async with app:
            assert handler.check_update(message_reaction_update)
            await app.process_update(message_reaction_update)
            assert self.test_flag

            self.test_flag = False
            await app.process_update(message_reaction_count_update)
            assert self.test_flag

    @pytest.mark.parametrize(
        argnames=["allowed_types", "expected"],
        argvalues=[
            (MessageReactionHandler.MESSAGE_REACTION_UPDATED, (True, False)),
            (MessageReactionHandler.MESSAGE_REACTION_COUNT_UPDATED, (False, True)),
            (MessageReactionHandler.MESSAGE_REACTION, (True, True)),
        ],
        ids=["MESSAGE_REACTION_UPDATED", "MESSAGE_REACTION_COUNT_UPDATED", "MESSAGE_REACTION"],
    )
    async def test_message_reaction_types(
        self, app, message_reaction_update, message_reaction_count_update, expected, allowed_types
    ):
        result_1, result_2 = expected

        handler = MessageReactionHandler(self.callback, message_reaction_types=allowed_types)
        app.add_handler(handler)

        async with app:
            assert handler.check_update(message_reaction_update) == result_1
            await app.process_update(message_reaction_update)
            assert self.test_flag == result_1

            self.test_flag = False

            assert handler.check_update(message_reaction_count_update) == result_2
            await app.process_update(message_reaction_count_update)
            assert self.test_flag == result_2

    @pytest.mark.parametrize(
        argnames=["allowed_types", "kwargs"],
        argvalues=[
            (MessageReactionHandler.MESSAGE_REACTION_COUNT_UPDATED, {"user_username": "user"}),
            (MessageReactionHandler.MESSAGE_REACTION, {"user_id": 123}),
        ],
        ids=["MESSAGE_REACTION_COUNT_UPDATED", "MESSAGE_REACTION"],
    )
    async def test_username_with_anonymous_reaction(self, app, allowed_types, kwargs):
        with pytest.raises(
            ValueError, match="You can not filter for users and include anonymous reactions."
        ):
            MessageReactionHandler(self.callback, message_reaction_types=allowed_types, **kwargs)

    @pytest.mark.parametrize(
        argnames=["chat_id", "expected"],
        argvalues=[(1, True), ([1], True), (2, False), ([2], False)],
    )
    async def test_with_chat_ids(
        self, chat_id, expected, message_reaction_update, message_reaction_count_update
    ):
        handler = MessageReactionHandler(self.callback, chat_id=chat_id)
        assert handler.check_update(message_reaction_update) == expected
        assert handler.check_update(message_reaction_count_update) == expected

    @pytest.mark.parametrize(
        argnames=["chat_username"],
        argvalues=[("group_a",), ("@group_a",), (["group_a"],), (["@group_a"],)],
        ids=["group_a", "@group_a", "['group_a']", "['@group_a']"],
    )
    async def test_with_chat_usernames(
        self, chat_username, message_reaction_update, message_reaction_count_update
    ):
        handler = MessageReactionHandler(self.callback, chat_username=chat_username)
        assert not handler.check_update(message_reaction_update)
        assert not handler.check_update(message_reaction_count_update)

        message_reaction_update.message_reaction.chat.username = "group_a"
        message_reaction_count_update.message_reaction_count.chat.username = "group_a"

        assert handler.check_update(message_reaction_update)
        assert handler.check_update(message_reaction_count_update)

        message_reaction_update.message_reaction.chat.username = None
        message_reaction_count_update.message_reaction_count.chat.username = None

    @pytest.mark.parametrize(
        argnames=["user_id", "expected"],
        argvalues=[(1, True), ([1], True), (2, False), ([2], False)],
    )
    async def test_with_user_ids(
        self, user_id, expected, message_reaction_update, message_reaction_count_update
    ):
        handler = MessageReactionHandler(
            self.callback,
            user_id=user_id,
            message_reaction_types=MessageReactionHandler.MESSAGE_REACTION_UPDATED,
        )
        assert handler.check_update(message_reaction_update) == expected
        assert not handler.check_update(message_reaction_count_update)

    @pytest.mark.parametrize(
        argnames=["user_username"],
        argvalues=[("user_a",), ("@user_a",), (["user_a"],), (["@user_a"],)],
        ids=["user_a", "@user_a", "['user_a']", "['@user_a']"],
    )
    async def test_with_user_usernames(
        self, user_username, message_reaction_update, message_reaction_count_update
    ):
        handler = MessageReactionHandler(
            self.callback,
            user_username=user_username,
            message_reaction_types=MessageReactionHandler.MESSAGE_REACTION_UPDATED,
        )
        assert not handler.check_update(message_reaction_update)
        assert not handler.check_update(message_reaction_count_update)

        message_reaction_update.message_reaction.user.username = "user_a"

        assert handler.check_update(message_reaction_update)
        assert not handler.check_update(message_reaction_count_update)

        message_reaction_update.message_reaction.user.username = None

    async def test_message_reaction_count_with_combination(
        self, message_reaction_count_update, message_reaction_update
    ):
        handler = MessageReactionHandler(
            self.callback,
            chat_id=2,
            chat_username="group_a",
            message_reaction_types=MessageReactionHandler.MESSAGE_REACTION,
        )
        assert not handler.check_update(message_reaction_count_update)

        message_reaction_count_update.message_reaction_count.chat.id = 2
        message_reaction_update.message_reaction.chat.id = 2
        assert handler.check_update(message_reaction_count_update)
        assert handler.check_update(message_reaction_update)
        message_reaction_count_update.message_reaction_count.chat.id = 1
        message_reaction_update.message_reaction.chat.id = 1

        message_reaction_count_update.message_reaction_count.chat.username = "group_a"
        message_reaction_update.message_reaction.chat.username = "group_a"
        assert handler.check_update(message_reaction_count_update)
        assert handler.check_update(message_reaction_update)
        message_reaction_count_update.message_reaction_count.chat.username = None
        message_reaction_update.message_reaction.chat.username = None

    async def test_message_reaction_with_combination(self, message_reaction_update):
        handler = MessageReactionHandler(
            self.callback,
            chat_id=2,
            chat_username="group_a",
            user_id=2,
            user_username="user_a",
            message_reaction_types=MessageReactionHandler.MESSAGE_REACTION_UPDATED,
        )
        assert not handler.check_update(message_reaction_update)

        message_reaction_update.message_reaction.chat.id = 2
        assert handler.check_update(message_reaction_update)
        message_reaction_update.message_reaction.chat.id = 1

        message_reaction_update.message_reaction.chat.username = "group_a"
        assert handler.check_update(message_reaction_update)
        message_reaction_update.message_reaction.chat.username = None

        message_reaction_update.message_reaction.user.id = 2
        assert handler.check_update(message_reaction_update)
        message_reaction_update.message_reaction.user.id = 1

        message_reaction_update.message_reaction.user.username = "user_a"
        assert handler.check_update(message_reaction_update)
        message_reaction_update.message_reaction.user.username = None
