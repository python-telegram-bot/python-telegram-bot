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
import pytest

from telegram import BotDescription, BotShortDescription
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def bot_description(bot):
    return BotDescription(TestBotDescriptionBase.description)


@pytest.fixture(scope="module")
def bot_short_description(bot):
    return BotShortDescription(TestBotDescriptionBase.short_description)


class TestBotDescriptionBase:
    description = "This is a test description"
    short_description = "This is a test short description"


class TestBotDescriptionWithoutRequest(TestBotDescriptionBase):
    def test_slot_behaviour(self, bot_description):
        for attr in bot_description.__slots__:
            assert getattr(bot_description, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(bot_description)) == len(
            set(mro_slots(bot_description))
        ), "duplicate slot"

    def test_to_dict(self, bot_description):
        bot_description_dict = bot_description.to_dict()

        assert isinstance(bot_description_dict, dict)
        assert bot_description_dict["description"] == self.description

    def test_equality(self):
        a = BotDescription(self.description)
        b = BotDescription(self.description)
        c = BotDescription("text.com")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)


class TestBotShortDescriptionWithoutRequest(TestBotDescriptionBase):
    def test_slot_behaviour(self, bot_short_description):
        for attr in bot_short_description.__slots__:
            assert getattr(bot_short_description, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(bot_short_description)) == len(
            set(mro_slots(bot_short_description))
        ), "duplicate slot"

    def test_to_dict(self, bot_short_description):
        bot_short_description_dict = bot_short_description.to_dict()

        assert isinstance(bot_short_description_dict, dict)
        assert bot_short_description_dict["short_description"] == self.short_description

    def test_equality(self):
        a = BotShortDescription(self.short_description)
        b = BotShortDescription(self.short_description)
        c = BotShortDescription("text.com")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)
