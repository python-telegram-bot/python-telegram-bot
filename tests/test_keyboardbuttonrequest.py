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

from telegram import (
    ChatAdministratorRights,
    ChatShared,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUser,
    UserShared,
)


@pytest.fixture(scope="class")
def request_user():
    return KeyboardButtonRequestUser(
        TestKeyboardButtonRequestUser.request_id,
        TestKeyboardButtonRequestUser.user_is_bot,
        TestKeyboardButtonRequestUser.user_is_premium,
    )


class TestKeyboardButtonRequestUser:
    request_id = 123
    user_is_bot = True
    user_is_premium = False

    def test_slot_behaviour(self, request_user, mro_slots):
        for attr in request_user.__slots__:
            assert getattr(request_user, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(request_user)) == len(set(mro_slots(request_user))), "duplicate slot"

    def test_to_dict(self, request_user):
        request_user_dict = request_user.to_dict()

        assert isinstance(request_user_dict, dict)
        assert request_user_dict["request_id"] == self.request_id
        assert request_user_dict["user_is_bot"] == self.user_is_bot
        assert request_user_dict["user_is_premium"] == self.user_is_premium

    def test_de_json(self, bot):
        json_dict = {
            "request_id": self.request_id,
            "user_is_bot": self.user_is_bot,
            "user_is_premium": self.user_is_premium,
        }
        request_user = KeyboardButtonRequestUser.de_json(json_dict, bot)
        assert request_user.api_kwargs == {}

        assert request_user.request_id == self.request_id
        assert request_user.user_is_bot == self.user_is_bot
        assert request_user.user_is_premium == self.user_is_premium

    def test_equality(self):
        a = KeyboardButtonRequestUser(self.request_id)
        b = KeyboardButtonRequestUser(self.request_id)
        c = KeyboardButtonRequestUser(1)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)


@pytest.fixture(scope="class")
def request_chat():
    return KeyboardButtonRequestChat(
        TestKeyboardButtonRequestChat.request_id,
        TestKeyboardButtonRequestChat.chat_is_channel,
        TestKeyboardButtonRequestChat.chat_is_forum,
        TestKeyboardButtonRequestChat.chat_has_username,
        TestKeyboardButtonRequestChat.chat_is_created,
        TestKeyboardButtonRequestChat.user_administrator_rights,
        TestKeyboardButtonRequestChat.bot_administrator_rights,
        TestKeyboardButtonRequestChat.bot_is_member,
    )


class TestKeyboardButtonRequestChat:
    request_id = 456
    chat_is_channel = True
    chat_is_forum = False
    chat_has_username = True
    chat_is_created = False
    user_administrator_rights = ChatAdministratorRights(
        True, False, True, False, True, False, True, False
    )
    bot_administrator_rights = ChatAdministratorRights(
        True, False, True, False, True, False, True, False
    )
    bot_is_member = True

    def test_slot_behaviour(self, request_chat, mro_slots):
        for attr in request_chat.__slots__:
            assert getattr(request_chat, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(request_chat)) == len(set(mro_slots(request_chat))), "duplicate slot"

    def test_to_dict(self, request_chat):
        request_chat_dict = request_chat.to_dict()

        assert isinstance(request_chat_dict, dict)
        assert request_chat_dict["request_id"] == self.request_id
        assert request_chat_dict["chat_is_channel"] == self.chat_is_channel
        assert request_chat_dict["chat_is_forum"] == self.chat_is_forum
        assert request_chat_dict["chat_has_username"] == self.chat_has_username
        assert (
            request_chat_dict["user_administrator_rights"]
            == self.user_administrator_rights.to_dict()
        )
        assert (
            request_chat_dict["bot_administrator_rights"]
            == self.bot_administrator_rights.to_dict()
        )
        assert request_chat_dict["bot_is_member"] == self.bot_is_member

    def test_de_json(self, bot):
        json_dict = {
            "request_id": self.request_id,
            "chat_is_channel": self.chat_is_channel,
            "chat_is_forum": self.chat_is_forum,
            "chat_has_username": self.chat_has_username,
            "user_administrator_rights": self.user_administrator_rights.to_dict(),
            "bot_administrator_rights": self.bot_administrator_rights.to_dict(),
            "bot_is_member": self.bot_is_member,
        }
        request_chat = KeyboardButtonRequestChat.de_json(json_dict, bot)
        assert request_chat.api_kwargs == {}

        assert request_chat.request_id == self.request_id
        assert request_chat.chat_is_channel == self.chat_is_channel
        assert request_chat.chat_is_forum == self.chat_is_forum
        assert request_chat.chat_has_username == self.chat_has_username
        assert request_chat.user_administrator_rights == self.user_administrator_rights
        assert request_chat.bot_administrator_rights == self.bot_administrator_rights
        assert request_chat.bot_is_member == self.bot_is_member

        empty_chat = KeyboardButtonRequestChat.de_json({}, bot)
        assert empty_chat is None

    def test_equality(self):
        a = KeyboardButtonRequestChat(self.request_id, True)
        b = KeyboardButtonRequestChat(self.request_id, True)
        c = KeyboardButtonRequestChat(1, True)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)


@pytest.fixture(scope="class")
def user_shared():
    return UserShared(
        TestUserShared.request_id,
        TestUserShared.user_id,
    )


class TestUserShared:
    request_id = 789
    user_id = 101112

    def test_slot_behaviour(self, user_shared, mro_slots):
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
        TestChatShared.request_id,
        TestChatShared.chat_id,
    )


class TestChatShared:
    request_id = 131415
    chat_id = 161718

    def test_slot_behaviour(self, chat_shared, mro_slots):
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
