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
import datetime as dtm

import pytest

from telegram import (
    BotCommand,
    Chat,
    Dice,
    MessageReactionCountUpdated,
    MessageReactionUpdated,
    ReactionCount,
    ReactionType,
    ReactionTypeCustomEmoji,
    ReactionTypeEmoji,
    ReactionTypePaid,
    User,
    constants,
)
from telegram._utils.datetime import to_timestamp
from telegram.constants import ReactionEmoji
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def reaction_type():
    return ReactionType(type=TestReactionTypeWithoutRequest.type)


class ReactionTypeTestBase:
    type = "emoji"
    emoji = "some_emoji"
    custom_emoji_id = "some_custom_emoji_id"


class TestReactionTypeWithoutRequest(ReactionTypeTestBase, DeserializationTestBase):
    de_json_class = ReactionType

    @pytest.fixture
    def de_json_dict(self):
        # An unknown type, so that ReactionType.de_json does not dispatch to a subclass
        return {"type": "unknown"}

    def test_slot_behaviour(self, reaction_type):
        inst = reaction_type
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self):
        assert type(ReactionType("emoji").type) is constants.ReactionType
        assert ReactionType("unknown").type == "unknown"

    def test_de_json(self, offline_bot, de_json_dict):
        reaction_type = ReactionType.de_json(de_json_dict, offline_bot)
        assert type(reaction_type) is ReactionType
        assert reaction_type.api_kwargs == {}
        assert reaction_type.type == "unknown"

    @pytest.mark.parametrize(
        ("rt_type", "subclass"),
        [
            ("emoji", ReactionTypeEmoji),
            ("custom_emoji", ReactionTypeCustomEmoji),
            ("paid", ReactionTypePaid),
        ],
    )
    def test_de_json_subclass(self, offline_bot, rt_type, subclass):
        json_dict = {
            "type": rt_type,
            "emoji": self.emoji,
            "custom_emoji_id": self.custom_emoji_id,
        }
        rt = ReactionType.de_json(json_dict, offline_bot)

        assert type(rt) is subclass
        assert set(rt.api_kwargs.keys()) == set(json_dict.keys()) - set(subclass.__slots__) - {
            "type"
        }
        assert rt.type == rt_type

    def test_to_dict(self, reaction_type):
        reaction_type_dict = reaction_type.to_dict()
        assert isinstance(reaction_type_dict, dict)
        assert reaction_type_dict["type"] == reaction_type.type


@pytest.fixture(scope="module")
def reaction_type_emoji():
    return ReactionTypeEmoji(emoji=TestReactionTypeEmojiWithoutRequest.emoji)


class TestReactionTypeEmojiWithoutRequest(ReactionTypeTestBase, DeserializationTestBase):
    de_json_class = ReactionTypeEmoji
    type = constants.ReactionType.EMOJI

    def test_slot_behaviour(self, reaction_type_emoji):
        inst = reaction_type_emoji
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"emoji": self.emoji}

    def test_de_json(self, offline_bot, de_json_dict):
        reaction_type_emoji = ReactionTypeEmoji.de_json(de_json_dict, offline_bot)
        assert type(reaction_type_emoji) is ReactionTypeEmoji
        assert reaction_type_emoji.api_kwargs == {}
        assert reaction_type_emoji.type == self.type
        assert reaction_type_emoji.emoji == self.emoji

    def test_to_dict(self, reaction_type_emoji):
        reaction_type_emoji_dict = reaction_type_emoji.to_dict()
        assert isinstance(reaction_type_emoji_dict, dict)
        assert reaction_type_emoji_dict["type"] == reaction_type_emoji.type
        assert reaction_type_emoji_dict["emoji"] == reaction_type_emoji.emoji

    def test_equality(self, reaction_type_emoji):
        a = reaction_type_emoji
        b = ReactionTypeEmoji(emoji=self.emoji)
        c = ReactionTypeEmoji(emoji="other_emoji")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture(scope="module")
def reaction_type_custom_emoji():
    return ReactionTypeCustomEmoji(
        custom_emoji_id=TestReactionTypeCustomEmojiWithoutRequest.custom_emoji_id
    )


class TestReactionTypeCustomEmojiWithoutRequest(ReactionTypeTestBase, DeserializationTestBase):
    de_json_class = ReactionTypeCustomEmoji
    type = constants.ReactionType.CUSTOM_EMOJI

    def test_slot_behaviour(self, reaction_type_custom_emoji):
        inst = reaction_type_custom_emoji
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"custom_emoji_id": self.custom_emoji_id}

    def test_de_json(self, offline_bot, de_json_dict):
        reaction_type_custom_emoji = ReactionTypeCustomEmoji.de_json(de_json_dict, offline_bot)
        assert type(reaction_type_custom_emoji) is ReactionTypeCustomEmoji
        assert reaction_type_custom_emoji.api_kwargs == {}
        assert reaction_type_custom_emoji.type == self.type
        assert reaction_type_custom_emoji.custom_emoji_id == self.custom_emoji_id

    def test_to_dict(self, reaction_type_custom_emoji):
        reaction_type_custom_emoji_dict = reaction_type_custom_emoji.to_dict()
        assert isinstance(reaction_type_custom_emoji_dict, dict)
        assert reaction_type_custom_emoji_dict["type"] == reaction_type_custom_emoji.type
        assert (
            reaction_type_custom_emoji_dict["custom_emoji_id"]
            == reaction_type_custom_emoji.custom_emoji_id
        )

    def test_equality(self, reaction_type_custom_emoji):
        a = reaction_type_custom_emoji
        b = ReactionTypeCustomEmoji(custom_emoji_id=self.custom_emoji_id)
        c = ReactionTypeCustomEmoji(custom_emoji_id="other_custom_emoji_id")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture(scope="module")
def reaction_type_paid():
    return ReactionTypePaid()


class TestReactionTypePaidWithoutRequest(ReactionTypeTestBase, DeserializationTestBase):
    de_json_class = ReactionTypePaid
    type = constants.ReactionType.PAID

    def test_slot_behaviour(self, reaction_type_paid):
        inst = reaction_type_paid
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {}

    def test_de_json(self, offline_bot, de_json_dict):
        reaction_type_paid = ReactionTypePaid.de_json(de_json_dict, offline_bot)
        assert type(reaction_type_paid) is ReactionTypePaid
        assert reaction_type_paid.api_kwargs == {}
        assert reaction_type_paid.type == self.type

    def test_to_dict(self, reaction_type_paid):
        reaction_type_paid_dict = reaction_type_paid.to_dict()
        assert isinstance(reaction_type_paid_dict, dict)
        assert reaction_type_paid_dict["type"] == reaction_type_paid.type


@pytest.fixture(scope="module")
def reaction_count():
    return ReactionCount(
        type=TestReactionCountWithoutRequest.type,
        total_count=TestReactionCountWithoutRequest.total_count,
    )


class TestReactionCountWithoutRequest(DeserializationTestBase):
    de_json_class = ReactionCount
    type = ReactionTypeEmoji(ReactionEmoji.THUMBS_UP)
    total_count = 42

    @pytest.fixture
    def de_json_dict(self):
        return {"type": self.type.to_dict(), "total_count": self.total_count}

    def test_slot_behaviour(self, reaction_count):
        for attr in reaction_count.__slots__:
            assert getattr(reaction_count, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(reaction_count)) == len(set(mro_slots(reaction_count))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot, de_json_dict):
        reaction_count = ReactionCount.de_json(de_json_dict, offline_bot)
        assert reaction_count.api_kwargs == {}

        assert isinstance(reaction_count, ReactionCount)
        assert reaction_count.type == self.type
        assert reaction_count.type.type == self.type.type
        assert reaction_count.type.emoji == self.type.emoji
        assert reaction_count.total_count == self.total_count

    def test_to_dict(self, reaction_count):
        reaction_count_dict = reaction_count.to_dict()

        assert isinstance(reaction_count_dict, dict)
        assert reaction_count_dict["type"] == reaction_count.type.to_dict()
        assert reaction_count_dict["total_count"] == reaction_count.total_count

    def test_equality(self, reaction_count):
        a = reaction_count
        b = ReactionCount(
            type=self.type,
            total_count=self.total_count,
        )
        c = ReactionCount(
            type=self.type,
            total_count=self.total_count + 1,
        )
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


class MessageReactionTestBase:
    chat = Chat(1, Chat.SUPERGROUP)
    message_id = 123
    date = dtm.datetime.now(dtm.UTC).replace(microsecond=0)
    user = User(2, "user", False)
    actor_chat = Chat(3, Chat.CHANNEL)
    old_reaction = (ReactionTypeEmoji(ReactionEmoji.THUMBS_UP),)
    new_reaction = (
        ReactionTypeEmoji(ReactionEmoji.RED_HEART),
        ReactionTypeCustomEmoji("custom_emoji_id"),
    )
    reactions = (
        ReactionCount(ReactionTypeEmoji(ReactionEmoji.THUMBS_UP), 3),
        ReactionCount(ReactionTypeCustomEmoji("custom_emoji_id"), 1),
    )


@pytest.fixture(scope="module")
def message_reaction_updated():
    return MessageReactionUpdated(
        chat=MessageReactionTestBase.chat,
        message_id=MessageReactionTestBase.message_id,
        date=MessageReactionTestBase.date,
        old_reaction=MessageReactionTestBase.old_reaction,
        new_reaction=MessageReactionTestBase.new_reaction,
        user=MessageReactionTestBase.user,
        actor_chat=MessageReactionTestBase.actor_chat,
    )


class TestMessageReactionUpdatedWithoutRequest(MessageReactionTestBase, DeserializationTestBase):
    de_json_class = MessageReactionUpdated

    @pytest.fixture
    def de_json_dict(self):
        return {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": to_timestamp(self.date),
            "old_reaction": [reaction.to_dict() for reaction in self.old_reaction],
            "new_reaction": [reaction.to_dict() for reaction in self.new_reaction],
            "user": self.user.to_dict(),
            "actor_chat": self.actor_chat.to_dict(),
        }

    def test_slot_behaviour(self, message_reaction_updated):
        inst = message_reaction_updated
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, de_json_dict):
        message_reaction = MessageReactionUpdated.de_json(de_json_dict, offline_bot)
        assert message_reaction.api_kwargs == {}

        assert message_reaction.chat == self.chat
        assert message_reaction.message_id == self.message_id
        assert message_reaction.date == self.date
        assert message_reaction.old_reaction == self.old_reaction
        assert message_reaction.new_reaction == self.new_reaction
        assert type(message_reaction.new_reaction[1]) is ReactionTypeCustomEmoji
        assert message_reaction.user == self.user
        assert message_reaction.actor_chat == self.actor_chat

    def test_to_dict(self, message_reaction_updated):
        assert message_reaction_updated.to_dict() == {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": to_timestamp(self.date),
            "old_reaction": [reaction.to_dict() for reaction in self.old_reaction],
            "new_reaction": [reaction.to_dict() for reaction in self.new_reaction],
            "user": self.user.to_dict(),
            "actor_chat": self.actor_chat.to_dict(),
        }

    def test_equality(self, message_reaction_updated):
        a = message_reaction_updated
        b = MessageReactionUpdated(
            self.chat, self.message_id, self.date, self.old_reaction, self.new_reaction
        )
        c = MessageReactionUpdated(
            self.chat, self.message_id, self.date, self.old_reaction, self.old_reaction
        )
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture(scope="module")
def message_reaction_count_updated():
    return MessageReactionCountUpdated(
        chat=MessageReactionTestBase.chat,
        message_id=MessageReactionTestBase.message_id,
        date=MessageReactionTestBase.date,
        reactions=MessageReactionTestBase.reactions,
    )


class TestMessageReactionCountUpdatedWithoutRequest(
    MessageReactionTestBase, DeserializationTestBase
):
    de_json_class = MessageReactionCountUpdated

    @pytest.fixture
    def de_json_dict(self):
        return {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": to_timestamp(self.date),
            "reactions": [reaction.to_dict() for reaction in self.reactions],
        }

    def test_slot_behaviour(self, message_reaction_count_updated):
        inst = message_reaction_count_updated
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, de_json_dict):
        message_reaction_count = MessageReactionCountUpdated.de_json(de_json_dict, offline_bot)
        assert message_reaction_count.api_kwargs == {}

        assert message_reaction_count.chat == self.chat
        assert message_reaction_count.message_id == self.message_id
        assert message_reaction_count.date == self.date
        assert message_reaction_count.reactions == self.reactions
        assert type(message_reaction_count.reactions[1].type) is ReactionTypeCustomEmoji

    def test_to_dict(self, message_reaction_count_updated):
        assert message_reaction_count_updated.to_dict() == {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": to_timestamp(self.date),
            "reactions": [reaction.to_dict() for reaction in self.reactions],
        }

    def test_equality(self, message_reaction_count_updated):
        a = message_reaction_count_updated
        b = MessageReactionCountUpdated(self.chat, self.message_id, self.date, self.reactions)
        c = MessageReactionCountUpdated(self.chat, self.message_id + 1, self.date, self.reactions)
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
