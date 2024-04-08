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
# along with this program. If not, see [http://www.gnu.org/licenses/].

import pytest

from telegram import ChatShared, SharedUser, UsersShared
from telegram.warnings import PTBDeprecationWarning
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="class")
def users_shared():
    return UsersShared(TestUsersSharedBase.request_id, users=TestUsersSharedBase.users)


class TestUsersSharedBase:
    request_id = 789
    user_ids = (101112, 101113)
    users = (SharedUser(101112, "user1"), SharedUser(101113, "user2"))


class TestUsersSharedWithoutRequest(TestUsersSharedBase):
    def test_slot_behaviour(self, users_shared):
        for attr in users_shared.__slots__:
            assert getattr(users_shared, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(users_shared)) == len(set(mro_slots(users_shared))), "duplicate slot"

    def test_to_dict(self, users_shared):
        users_shared_dict = users_shared.to_dict()

        assert isinstance(users_shared_dict, dict)
        assert users_shared_dict["request_id"] == self.request_id
        assert users_shared_dict["users"] == [user.to_dict() for user in self.users]

    def test_de_json(self, bot):
        json_dict = {
            "request_id": self.request_id,
            "users": [user.to_dict() for user in self.users],
            "user_ids": self.user_ids,
        }
        users_shared = UsersShared.de_json(json_dict, bot)
        assert users_shared.api_kwargs == {"user_ids": self.user_ids}

        assert users_shared.request_id == self.request_id
        assert users_shared.users == self.users
        assert users_shared.user_ids == tuple(self.user_ids)

        assert UsersShared.de_json({}, bot) is None

    def test_users_is_required_argument(self):
        with pytest.raises(TypeError, match="`users` is a required argument"):
            UsersShared(self.request_id, user_ids=self.user_ids)

    def test_user_ids_deprecation_warning(self):
        with pytest.warns(
            PTBDeprecationWarning, match="'user_ids' was renamed to 'users' in Bot API 7.2"
        ):
            users_shared = UsersShared(self.request_id, user_ids=self.user_ids, users=self.users)
        with pytest.warns(
            PTBDeprecationWarning, match="renamed the attribute 'user_ids' to 'users'"
        ):
            users_shared.user_ids

    def test_equality(self):
        a = UsersShared(self.request_id, users=self.users)
        b = UsersShared(self.request_id, users=self.users)
        c = UsersShared(1, users=self.users)
        d = UsersShared(self.request_id, users=(SharedUser(1, "user1"), SharedUser(1, "user2")))

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
