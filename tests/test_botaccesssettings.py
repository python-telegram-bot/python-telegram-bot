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
"""This module contains an object that represents a Telegram Bot Access Settings."""

import pytest

from telegram import BotAccessSettings
from telegram._user import User
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def bot_access_settings():
    return BotAccessSettings(
        is_access_restricted=BotAccessSettingsTestBase.is_access_restricted,
        added_users=BotAccessSettingsTestBase.added_users,
    )


class BotAccessSettingsTestBase:
    is_access_restricted = True
    added_users = [User(id=123, first_name="John", is_bot=False)]


class TestBotAccessSettingsWithoutRequest(BotAccessSettingsTestBase):
    def test_slot_behaviour(self, bot_access_settings):
        inst = bot_access_settings
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "is_access_restricted": self.is_access_restricted,
            "added_users": [user.to_dict() for user in self.added_users],
        }
        bot_access_settings = BotAccessSettings.de_json(json_dict, offline_bot)
        assert bot_access_settings.api_kwargs == {}

        assert bot_access_settings.is_access_restricted == self.is_access_restricted
        assert bot_access_settings.added_users == tuple(self.added_users)

    def test_to_dict(self, bot_access_settings):
        bot_access_settings_dict = bot_access_settings.to_dict()

        assert isinstance(bot_access_settings_dict, dict)
        assert (
            bot_access_settings_dict["is_access_restricted"]
            == bot_access_settings.is_access_restricted
        )
        assert isinstance(bot_access_settings_dict["added_users"], list)
        assert bot_access_settings_dict["added_users"][0] == self.added_users[0].to_dict()

    def test_equality(self):
        a = BotAccessSettings(is_access_restricted=True, added_users=self.added_users)
        b = BotAccessSettings(is_access_restricted=True, added_users=self.added_users)
        c = BotAccessSettings(is_access_restricted=False, added_users=self.added_users)
        d = BotAccessSettings(is_access_restricted=True, added_users=None)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
