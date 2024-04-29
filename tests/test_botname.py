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

from telegram import BotName
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def bot_name(bot):
    return BotName(TestBotNameBase.name)


class TestBotNameBase:
    name = "This is a test name"


class TestBotNameWithoutRequest(TestBotNameBase):
    def test_slot_behaviour(self, bot_name):
        for attr in bot_name.__slots__:
            assert getattr(bot_name, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(bot_name)) == len(set(mro_slots(bot_name))), "duplicate slot"

    def test_to_dict(self, bot_name):
        bot_name_dict = bot_name.to_dict()

        assert isinstance(bot_name_dict, dict)
        assert bot_name_dict["name"] == self.name

    def test_equality(self):
        a = BotName(self.name)
        b = BotName(self.name)
        c = BotName("text.com")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)
