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
# along with this program. If not, see [http://www.gnu.org/licenses/].

import pytest

from telegram import ChatShared, UserShared
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="class")
def user_shared():
    return UserShared(
        TestUserSharedBase.request_id,
        TestUserSharedBase.user_id,
    )


class TestUserSharedBase:
    request_id = 789
    user_id = 101112


class TestUserSharedWithoutRequest(TestUserSharedBase):
    def test_slot_behaviour(self, user_shared):
        for attr in user_shared.__slots__:
            assert getattr(user_shared, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(user_shared)) == len(set(mro_slots(user_shared))), "duplicate slot"

    def test_to_dict(self, user_shared):
        user_shared_dict = user_shared.to_dict()

        assert isinstance(user_shared_dict, dict)
        assert user_shared_dict["request_id"] == self.request_id
        assert user_shared_dict["user_id"] == self.user_id

    def test_de_json(self, bot):
        json_dict = {
            "request_id": self.request_id,
            "user_id": self.user_id,
        }
        user_shared = UserShared.de_json(json_dict, bot)
        assert user_shared.api_kwargs == {}

        assert user_shared.request_id == self.request_id
        assert user_shared.user_id == self.user_id

    def test_equality(self):
        a = UserShared(self.request_id, self.user_id)
        b = UserShared(self.request_id, self.user_id)
        c = UserShared(1, self.user_id)
        d = UserShared(self.request_id, 1)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture(scope="class")
def chat_shared():
    return ChatShared(
        TestChatSharedBase.request_id,
        TestChatSharedBase.chat_id,
    )


class TestChatSharedBase:
    request_id = 131415
    chat_id = 161718


class TestChatSharedWithoutRequest(TestChatSharedBase):
    def test_slot_behaviour(self, chat_shared):
        for attr in chat_shared.__slots__:
            assert getattr(chat_shared, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(chat_shared)) == len(set(mro_slots(chat_shared))), "duplicate slot"

    def test_to_dict(self, chat_shared):
        chat_shared_dict = chat_shared.to_dict()

        assert isinstance(chat_shared_dict, dict)
        assert chat_shared_dict["request_id"] == self.request_id
        assert chat_shared_dict["chat_id"] == self.chat_id

    def test_de_json(self, bot):
        json_dict = {
            "request_id": self.request_id,
            "chat_id": self.chat_id,
        }
        chat_shared = ChatShared.de_json(json_dict, bot)
        assert chat_shared.api_kwargs == {}

        assert chat_shared.request_id == self.request_id
        assert chat_shared.chat_id == self.chat_id

    def test_equality(self):
        a = ChatShared(self.request_id, self.chat_id)
        b = ChatShared(self.request_id, self.chat_id)
        c = ChatShared(1, self.chat_id)
        d = ChatShared(self.request_id, 1)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
