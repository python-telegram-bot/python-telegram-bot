#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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

import pytest

from telegram import (
    BotCommand,
    Dice,
    ReactionCount,
    ReactionType,
    ReactionTypeCustomEmoji,
    ReactionTypeEmoji,
    ReactionTypePaid,
    constants,
)
from telegram.constants import ReactionEmoji
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def reaction_type():
    return ReactionType(type=TestReactionTypeWithoutRequest.type)


class ReactionTypeTestBase:
    type = "emoji"
    emoji = "some_emoji"
    custom_emoji_id = "some_custom_emoji_id"


class TestReactionTypeWithoutRequest(ReactionTypeTestBase):
    def test_slot_behaviour(self, reaction_type):
        inst = reaction_type
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self):
        assert type(ReactionType("emoji").type) is constants.ReactionType
        assert ReactionType("unknown").type == "unknown"

    def test_de_json(self, offline_bot):
        json_dict = {"type": "unknown"}
        reaction_type = ReactionType.de_json(json_dict, offline_bot)
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


class TestReactionTypeEmojiWithoutRequest(ReactionTypeTestBase):
    type = constants.ReactionType.EMOJI

    def test_slot_behaviour(self, reaction_type_emoji):
        inst = reaction_type_emoji
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"emoji": self.emoji}
        reaction_type_emoji = ReactionTypeEmoji.de_json(json_dict, offline_bot)
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


class TestReactionTypeCustomEmojiWithoutRequest(ReactionTypeTestBase):
    type = constants.ReactionType.CUSTOM_EMOJI

    def test_slot_behaviour(self, reaction_type_custom_emoji):
        inst = reaction_type_custom_emoji
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"custom_emoji_id": self.custom_emoji_id}
        reaction_type_custom_emoji = ReactionTypeCustomEmoji.de_json(json_dict, offline_bot)
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


class TestReactionTypePaidWithoutRequest(ReactionTypeTestBase):
    type = constants.ReactionType.PAID

    def test_slot_behaviour(self, reaction_type_paid):
        inst = reaction_type_paid
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {}
        reaction_type_paid = ReactionTypePaid.de_json(json_dict, offline_bot)
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


class TestReactionCountWithoutRequest:
    type = ReactionTypeEmoji(ReactionEmoji.THUMBS_UP)
    total_count = 42

    def test_slot_behaviour(self, reaction_count):
        for attr in reaction_count.__slots__:
            assert getattr(reaction_count, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(reaction_count)) == len(
            set(mro_slots(reaction_count))
        ), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "type": self.type.to_dict(),
            "total_count": self.total_count,
        }

        reaction_count = ReactionCount.de_json(json_dict, offline_bot)
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
