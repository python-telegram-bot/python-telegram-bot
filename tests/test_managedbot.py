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
# along with this program. If not, see [http://www.gnu.org/licenses/].

from telegram import ManagedBotCreated, ManagedBotUpdated, User
from tests.auxil.slots import mro_slots


class TestManagedBotCreatedWithoutRequest:
    bot = User(1, "managed", True)

    def test_slot_behaviour(self):
        managed_bot_created = ManagedBotCreated(bot=self.bot)
        for attr in managed_bot_created.__slots__:
            assert getattr(managed_bot_created, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(managed_bot_created)) == len(set(mro_slots(managed_bot_created)))

    def test_de_json(self, offline_bot):
        managed_bot_created = ManagedBotCreated.de_json({"bot": self.bot.to_dict()}, offline_bot)
        assert managed_bot_created.api_kwargs == {}
        assert managed_bot_created.bot == self.bot

    def test_to_dict(self):
        managed_bot_created = ManagedBotCreated(bot=self.bot)
        assert managed_bot_created.to_dict() == {"bot": self.bot.to_dict()}

    def test_equality(self):
        a = ManagedBotCreated(bot=self.bot)
        b = ManagedBotCreated(bot=User(1, "other", True))
        c = ManagedBotCreated(bot=User(2, "managed", True))
        assert a == b
        assert a != c


class TestManagedBotUpdatedWithoutRequest:
    user = User(1, "owner", False)
    bot = User(2, "managed", True)

    def test_slot_behaviour(self):
        managed_bot_updated = ManagedBotUpdated(user=self.user, bot=self.bot)
        for attr in managed_bot_updated.__slots__:
            assert getattr(managed_bot_updated, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(managed_bot_updated)) == len(set(mro_slots(managed_bot_updated)))

    def test_de_json(self, offline_bot):
        managed_bot_updated = ManagedBotUpdated.de_json(
            {"user": self.user.to_dict(), "bot": self.bot.to_dict()},
            offline_bot,
        )
        assert managed_bot_updated.api_kwargs == {}
        assert managed_bot_updated.user == self.user
        assert managed_bot_updated.bot == self.bot

    def test_to_dict(self):
        managed_bot_updated = ManagedBotUpdated(user=self.user, bot=self.bot)
        assert managed_bot_updated.to_dict() == {
            "user": self.user.to_dict(),
            "bot": self.bot.to_dict(),
        }

    def test_equality(self):
        a = ManagedBotUpdated(user=self.user, bot=self.bot)
        b = ManagedBotUpdated(user=User(1, "other", False), bot=User(2, "other", True))
        c = ManagedBotUpdated(user=self.user, bot=User(3, "managed", True))
        assert a == b
        assert a != c
