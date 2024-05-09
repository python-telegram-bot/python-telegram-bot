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

from telegram import ChatShared, PhotoSize, SharedUser, UsersShared
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

        assert UsersShared.de_json({}, bot) is None

    def test_equality(self):
        a = UsersShared(self.request_id, users=self.users)
        b = UsersShared(self.request_id, users=self.users)
        c = UsersShared(1, users=self.users)
        d = UsersShared(self.request_id, users=(SharedUser(1, "user1"), SharedUser(1, "user2")))
        e = PhotoSize("file_id", "1", 1, 1)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


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

    def test_equality(self, users_shared):
        a = ChatShared(self.request_id, self.chat_id)
        b = ChatShared(self.request_id, self.chat_id)
        c = ChatShared(1, self.chat_id)
        d = ChatShared(self.request_id, 1)
        e = users_shared

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="class")
def shared_user():
    return SharedUser(
        TestSharedUserBase.user_id,
        TestSharedUserBase.first_name,
        last_name=TestSharedUserBase.last_name,
        username=TestSharedUserBase.username,
        photo=TestSharedUserBase.photo,
    )


class TestSharedUserBase:
    user_id = 101112
    first_name = "first"
    last_name = "last"
    username = "user"
    photo = (
        PhotoSize(file_id="file_id", width=1, height=1, file_unique_id="1"),
        PhotoSize(file_id="file_id", width=2, height=2, file_unique_id="2"),
    )


class TestSharedUserWithoutRequest(TestSharedUserBase):
    def test_slot_behaviour(self, shared_user):
        for attr in shared_user.__slots__:
            assert getattr(shared_user, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(shared_user)) == len(set(mro_slots(shared_user))), "duplicate slot"

    def test_to_dict(self, shared_user):
        shared_user_dict = shared_user.to_dict()

        assert isinstance(shared_user_dict, dict)
        assert shared_user_dict["user_id"] == self.user_id
        assert shared_user_dict["first_name"] == self.first_name
        assert shared_user_dict["last_name"] == self.last_name
        assert shared_user_dict["username"] == self.username
        assert shared_user_dict["photo"] == [photo.to_dict() for photo in self.photo]

    def test_de_json_required(self, bot):
        json_dict = {
            "user_id": self.user_id,
            "first_name": self.first_name,
        }
        shared_user = SharedUser.de_json(json_dict, bot)
        assert shared_user.api_kwargs == {}

        assert shared_user.user_id == self.user_id
        assert shared_user.first_name == self.first_name
        assert shared_user.last_name is None
        assert shared_user.username is None
        assert shared_user.photo == ()

    def test_de_json_all(self, bot):
        json_dict = {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "photo": [photo.to_dict() for photo in self.photo],
        }
        shared_user = SharedUser.de_json(json_dict, bot)
        assert shared_user.api_kwargs == {}

        assert shared_user.user_id == self.user_id
        assert shared_user.first_name == self.first_name
        assert shared_user.last_name == self.last_name
        assert shared_user.username == self.username
        assert shared_user.photo == self.photo

        assert SharedUser.de_json({}, bot) is None

    def test_equality(self, chat_shared):
        a = SharedUser(
            self.user_id,
            self.first_name,
            last_name=self.last_name,
            username=self.username,
            photo=self.photo,
        )
        b = SharedUser(self.user_id, "other_firs_name")
        c = SharedUser(self.user_id + 1, self.first_name)
        d = chat_shared

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
