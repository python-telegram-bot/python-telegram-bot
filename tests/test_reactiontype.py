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
import inspect
from copy import deepcopy

import pytest

from telegram import Dice, ReactionType, ReactionTypeCustomEmoji, ReactionTypeEmoji
from telegram.constants import ReactionEmojis
from tests.auxil.slots import mro_slots

ignored = ["self", "api_kwargs"]


class CMDefaults:
    custom_emoji = "123custom"
    normal_emoji = ReactionEmojis.THUMBS_UP


def reaction_type_custom_emoji():
    return ReactionTypeCustomEmoji(CMDefaults.custom_emoji)


def reaction_type_emoji():
    return ReactionTypeEmoji(CMDefaults.normal_emoji)


def make_json_dict(instance: ReactionType, include_optional_args: bool = False) -> dict:
    """Used to make the json dict which we use for testing de_json. Similar to iter_args()"""
    json_dict = {"type": instance.type}
    sig = inspect.signature(instance.__class__.__init__)

    for param in sig.parameters.values():
        if param.name in ignored:  # ignore irrelevant params
            continue

        val = getattr(instance, param.name)
        # Compulsory args-
        if param.default is inspect.Parameter.empty:
            if hasattr(val, "to_dict"):  # convert the user object or any future ones to dict.
                val = val.to_dict()
            json_dict[param.name] = val

        # If we want to test all args (for de_json)-
        elif param.default is not inspect.Parameter.empty and include_optional_args:
            json_dict[param.name] = val
    return json_dict


def iter_args(instance: ReactionType, de_json_inst: ReactionType, include_optional: bool = False):
    """
    We accept both the regular instance and de_json created instance and iterate over them for
    easy one line testing later one.
    """
    yield instance.type, de_json_inst.type  # yield this here cause it's not available in sig.

    sig = inspect.signature(instance.__class__.__init__)
    for param in sig.parameters.values():
        if param.name in ignored:
            continue
        inst_at, json_at = getattr(instance, param.name), getattr(de_json_inst, param.name)
        if (
            param.default is not inspect.Parameter.empty and include_optional
        ) or param.default is inspect.Parameter.empty:
            yield inst_at, json_at


@pytest.fixture()
def reaction_type(request):
    return request.param()


@pytest.mark.parametrize(
    "reaction_type",
    [
        reaction_type_custom_emoji,
        reaction_type_emoji,
    ],
    indirect=True,
)
class TestChatMemberTypesWithoutRequest:
    def test_slot_behaviour(self, reaction_type):
        inst = reaction_type
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json_required_args(self, bot, reaction_type):
        cls = reaction_type.__class__
        assert cls.de_json(None, bot) is None

        json_dict = make_json_dict(reaction_type)
        const_reaction_type = ReactionType.de_json(json_dict, bot)
        assert const_reaction_type.api_kwargs == {}

        assert isinstance(const_reaction_type, ReactionType)
        assert isinstance(const_reaction_type, cls)
        for reaction_type_at, const_reaction_type_at in iter_args(
            reaction_type, const_reaction_type
        ):
            assert reaction_type_at == const_reaction_type_at

    def test_de_json_all_args(self, bot, reaction_type):
        json_dict = make_json_dict(reaction_type, include_optional_args=True)
        const_reaction_type = ReactionType.de_json(json_dict, bot)
        assert const_reaction_type.api_kwargs == {}

        assert isinstance(const_reaction_type, ReactionType)
        assert isinstance(const_reaction_type, reaction_type.__class__)
        for c_mem_type_at, const_c_mem_at in iter_args(reaction_type, const_reaction_type, True):
            assert c_mem_type_at == const_c_mem_at

    def test_de_json_invalid_type(self, bot, reaction_type):
        json_dict = {"type": "invalid"}
        reaction_type = ReactionType.de_json(json_dict, bot)

        assert type(reaction_type) is ReactionType
        assert reaction_type.type == "invalid"

    def test_de_json_subclass(self, reaction_type, bot, chat_id):
        """This makes sure that e.g. ReactionTypeEmoji(data, bot) never returns a
        ReactionTypeCustomEmoji instance."""
        cls = reaction_type.__class__
        json_dict = make_json_dict(reaction_type, True)
        assert type(cls.de_json(json_dict, bot)) is cls

    def test_to_dict(self, reaction_type):
        reaction_type_dict = reaction_type.to_dict()

        assert isinstance(reaction_type_dict, dict)
        assert reaction_type_dict["type"] == reaction_type.type
        if reaction_type.type == ReactionType.EMOJI:
            assert reaction_type_dict["emoji"] == reaction_type.emoji
        else:
            assert reaction_type_dict["custom_emoji_id"] == reaction_type.custom_emoji_id

        for slot in reaction_type.__slots__:  # additional verification for the optional args
            assert getattr(reaction_type, slot) == reaction_type_dict[slot]

    def test_reaction_type_api_kwargs(self, reaction_type):
        json_dict = make_json_dict(reaction_type_custom_emoji())
        json_dict["custom_arg"] = "wuhu"
        reaction_type_custom_emoji_instance = ReactionType.de_json(json_dict, None)
        assert reaction_type_custom_emoji_instance.api_kwargs == {
            "custom_arg": "wuhu",
        }

    def test_equality(self, reaction_type):
        a = ReactionTypeEmoji(emoji=CMDefaults.normal_emoji)
        b = ReactionTypeEmoji(emoji=CMDefaults.normal_emoji)
        c = ReactionTypeCustomEmoji(custom_emoji_id=CMDefaults.custom_emoji)
        d = ReactionTypeCustomEmoji(custom_emoji_id=CMDefaults.custom_emoji)
        e = ReactionTypeEmoji(emoji=ReactionEmojis.READ_HEART)
        f = ReactionTypeCustomEmoji(custom_emoji_id="1234custom")
        g = deepcopy(a)
        h = deepcopy(c)
        i = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != e
        assert hash(a) != hash(e)

        assert a == g
        assert hash(a) == hash(g)

        assert a != i
        assert hash(a) != hash(i)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)

        assert c != f
        assert hash(c) != hash(f)

        assert c == h
        assert hash(c) == hash(h)

        assert c != i
        assert hash(c) != hash(i)
