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
import pytest

from telegram import BotDescription, BotShortDescription


@pytest.fixture(scope="module")
def bot_description(bot):
    return BotDescription(BotDescriptionTestBase.description)


@pytest.fixture(scope="module")
def bot_short_description(bot):
    return BotShortDescription(BotDescriptionTestBase.short_description)


class BotDescriptionTestBase:
    description = "This is a test description"
    short_description = "This is a test short description"


class TestBotDescriptionWithoutRequest(BotDescriptionTestBase):
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


class TestBotShortDescriptionWithoutRequest(BotDescriptionTestBase):
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
