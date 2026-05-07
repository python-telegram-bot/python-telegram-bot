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

from telegram import ManagedBotCreated, ManagedBotUpdated, User
from tests.auxil.slots import mro_slots


@pytest.fixture
def managed_bot_created():
    return ManagedBotCreated(
        bot=User(
            id=ManagedBotTestBase.bot_id,
            is_bot=ManagedBotTestBase.is_bot,
            first_name=ManagedBotTestBase.bot_first_name,
            username=ManagedBotTestBase.bot_username,
        ),
    )


@pytest.fixture
def managed_bot_updated():
    return ManagedBotUpdated(
        user=User(
            id=ManagedBotTestBase.bot_creator_id,
            is_bot=ManagedBotTestBase.is_bot,
            first_name=ManagedBotTestBase.bot_creator_first_name,
            username=ManagedBotTestBase.bot_creator_username,
        ),
        bot=User(
            id=ManagedBotTestBase.bot_id,
            is_bot=ManagedBotTestBase.is_bot,
            first_name=ManagedBotTestBase.bot_first_name,
            username=ManagedBotTestBase.bot_username,
        ),
    )


class ManagedBotTestBase:
    bot_creator_id = 123
    bot_creator_first_name = "TestBotManager"
    bot_creator_username = "test_bot_manager"
    bot_id = 321
    bot_first_name = "TestBot"
    bot_username = "test_bot"
    is_bot = True


class TestManagedBotCreatedWithoutRequest(ManagedBotTestBase):
    def test_slot_behaviour(self, managed_bot_created):
        inst = managed_bot_created
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, managed_bot_created):
        json_dict = {
            "bot": managed_bot_created.bot.to_dict(),
        }
        managed_bot_created = ManagedBotCreated.de_json(json_dict, offline_bot)
        assert managed_bot_created.api_kwargs == {}
        assert managed_bot_created.bot.id == self.bot_id
        assert managed_bot_created.bot.is_bot is True
        assert managed_bot_created.bot.first_name == self.bot_first_name
        assert managed_bot_created.bot.username == self.bot_username

    def test_to_dict(self, managed_bot_created):
        managed_bot_created_dict = managed_bot_created.to_dict()
        assert managed_bot_created_dict["bot"]["id"] == self.bot_id
        assert managed_bot_created_dict["bot"]["is_bot"] is True
        assert managed_bot_created_dict["bot"]["first_name"] == self.bot_first_name
        assert managed_bot_created_dict["bot"]["username"] == self.bot_username

    def test_equality(self, managed_bot_created):
        managed_bot_created_2 = ManagedBotCreated(
            bot=User(
                id=self.bot_id,
                is_bot=True,
                first_name=self.bot_first_name,
                username=self.bot_username,
            ),
        )
        managed_bot_created_3 = ManagedBotCreated(
            bot=User(
                id=4534, is_bot=True, first_name=self.bot_first_name, username=self.bot_username
            ),
        )
        not_a_managed_bot_created = ManagedBotUpdated(
            user=User(
                id=self.bot_creator_id,
                is_bot=True,
                first_name=self.bot_creator_first_name,
                username=self.bot_creator_username,
            ),
            bot=User(
                id=self.bot_id,
                is_bot=True,
                first_name=self.bot_first_name,
                username=self.bot_username,
            ),
        )

        assert managed_bot_created == managed_bot_created_2
        assert hash(managed_bot_created) == hash(managed_bot_created_2)

        assert managed_bot_created != managed_bot_created_3
        assert hash(managed_bot_created) != hash(managed_bot_created_3)

        assert managed_bot_created != not_a_managed_bot_created
        assert hash(managed_bot_created) != hash(not_a_managed_bot_created)


class TestManagedBotUpdatedWithoutRequest(ManagedBotTestBase):
    def test_slot_behaviour(self, managed_bot_updated):
        inst = managed_bot_updated
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, managed_bot_updated):
        json_dict = {
            "user": managed_bot_updated.user.to_dict(),
            "bot": managed_bot_updated.bot.to_dict(),
        }
        managed_bot_updated_new = ManagedBotUpdated.de_json(json_dict, offline_bot)
        assert managed_bot_updated_new.api_kwargs == {}
        assert managed_bot_updated_new.user == managed_bot_updated.user
        assert managed_bot_updated_new.bot == managed_bot_updated.bot

    def test_to_dict(self, managed_bot_updated):
        managed_bot_updated_dict = managed_bot_updated.to_dict()
        assert managed_bot_updated_dict["user"] == managed_bot_updated.user.to_dict()
        assert managed_bot_updated_dict["bot"] == managed_bot_updated.bot.to_dict()

    def test_equality(self, managed_bot_updated):
        managed_bot_updated_2 = ManagedBotUpdated(
            user=User(
                id=self.bot_creator_id,
                is_bot=True,
                first_name=self.bot_creator_first_name,
                username=self.bot_creator_username,
            ),
            bot=User(
                id=self.bot_id,
                is_bot=True,
                first_name=self.bot_first_name,
                username=self.bot_username,
            ),
        )
        managed_bot_updated_3 = ManagedBotUpdated(
            user=User(
                id=4534,
                is_bot=True,
                first_name=self.bot_creator_first_name,
                username=self.bot_creator_username,
            ),
            bot=User(
                id=self.bot_id,
                is_bot=True,
                first_name=self.bot_first_name,
                username=self.bot_username,
            ),
        )
        not_a_managed_bot_updated = ManagedBotCreated(
            bot=User(
                id=self.bot_id,
                is_bot=True,
                first_name=self.bot_first_name,
                username=self.bot_username,
            ),
        )

        assert managed_bot_updated == managed_bot_updated_2
        assert hash(managed_bot_updated) == hash(managed_bot_updated_2)

        assert managed_bot_updated != managed_bot_updated_3
        assert hash(managed_bot_updated) != hash(managed_bot_updated_3)

        assert managed_bot_updated != not_a_managed_bot_updated
        assert hash(managed_bot_updated) != hash(not_a_managed_bot_updated)
