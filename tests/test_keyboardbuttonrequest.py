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

from telegram import ChatAdministratorRights, KeyboardButtonRequestChat, KeyboardButtonRequestUser
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="class")
def request_user():
    return KeyboardButtonRequestUser(
        TestKeyboardButtonRequestUserBase.request_id,
        TestKeyboardButtonRequestUserBase.user_is_bot,
        TestKeyboardButtonRequestUserBase.user_is_premium,
    )


class TestKeyboardButtonRequestUserBase:
    request_id = 123
    user_is_bot = True
    user_is_premium = False


class TestKeyboardButtonRequestUserWithoutRequest(TestKeyboardButtonRequestUserBase):
    def test_slot_behaviour(self, request_user):
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
        TestKeyboardButtonRequestChatBase.request_id,
        TestKeyboardButtonRequestChatBase.chat_is_channel,
        TestKeyboardButtonRequestChatBase.chat_is_forum,
        TestKeyboardButtonRequestChatBase.chat_has_username,
        TestKeyboardButtonRequestChatBase.chat_is_created,
        TestKeyboardButtonRequestChatBase.user_administrator_rights,
        TestKeyboardButtonRequestChatBase.bot_administrator_rights,
        TestKeyboardButtonRequestChatBase.bot_is_member,
    )


class TestKeyboardButtonRequestChatBase:
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


class TestKeyboardButtonRequestChatWithoutRequest(TestKeyboardButtonRequestChatBase):
    def test_slot_behaviour(self, request_chat):
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
