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

from telegram import BotCommand, ChatOwnerChanged, ChatOwnerLeft, User
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def chat_owner_changed():
    return ChatOwnerChanged(ChatOwnerTestBase.new_owner)


@pytest.fixture(scope="module")
def chat_owner_left():
    return ChatOwnerLeft(ChatOwnerTestBase.new_owner)


class ChatOwnerTestBase:
    new_owner = User(1, "SnowCrash", False)


class TestChatOwnerChangedWithoutRequest(ChatOwnerTestBase):
    def test_slot_behaviour(self, chat_owner_changed):
        inst = chat_owner_changed
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "new_owner": self.new_owner.to_dict(),
        }
        chat_owner_changed = ChatOwnerChanged.de_json(json_dict, offline_bot)
        assert chat_owner_changed.api_kwargs == {}

        assert chat_owner_changed.new_owner == self.new_owner
        assert chat_owner_changed.new_owner.first_name == self.new_owner.first_name

    def test_to_dict(self, chat_owner_changed):
        chat_owner_changed_dict = chat_owner_changed.to_dict()

        assert isinstance(chat_owner_changed_dict, dict)
        assert chat_owner_changed_dict["new_owner"] == chat_owner_changed.new_owner.to_dict()

    def test_equality(self, chat_owner_changed):
        a = chat_owner_changed
        b = ChatOwnerChanged(ChatOwnerTestBase.new_owner)
        c = ChatOwnerChanged(User(2, "SnowCrash", False))
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


class TestChatOwnerLeftWithoutRequest(ChatOwnerTestBase):
    def test_slot_behaviour(self, chat_owner_left):
        inst = chat_owner_left
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "new_owner": self.new_owner.to_dict(),
        }
        chat_owner_left = ChatOwnerLeft.de_json(json_dict, offline_bot)
        assert chat_owner_left.api_kwargs == {}

        assert chat_owner_left.new_owner == self.new_owner
        assert chat_owner_left.new_owner.first_name == self.new_owner.first_name

    def test_to_dict(self, chat_owner_left):
        chat_owner_left_dict = chat_owner_left.to_dict()

        assert isinstance(chat_owner_left_dict, dict)
        assert chat_owner_left_dict["new_owner"] == chat_owner_left.new_owner.to_dict()

    def test_equality(self, chat_owner_left):
        a = chat_owner_left
        b = ChatOwnerLeft(ChatOwnerTestBase.new_owner)
        c = ChatOwnerLeft(User(2, "SnowCrash", False))
        d = ChatOwnerLeft()
        e = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
