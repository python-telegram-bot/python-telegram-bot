#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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

from telegram import (
    BotCommandScope,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeChatAdministrators,
    BotCommandScopeChatMember,
    BotCommandScopeDefault,
    Dice,
)
from telegram.constants import BotCommandScopeType
from tests.auxil.slots import mro_slots


@pytest.fixture
def bot_command_scope():
    return BotCommandScope(BotCommandScopeTestBase.type)


class BotCommandScopeTestBase:
    type = BotCommandScopeType.DEFAULT
    chat_id = 123456789
    user_id = 987654321


class TestBotCommandScopeWithoutRequest(BotCommandScopeTestBase):
    def test_slot_behaviour(self, bot_command_scope):
        inst = bot_command_scope
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self, bot_command_scope):
        assert type(BotCommandScope("default").type) is BotCommandScopeType
        assert BotCommandScope("unknown").type == "unknown"

    def test_de_json(self, offline_bot):
        data = {"type": "unknown"}
        transaction_partner = BotCommandScope.de_json(data, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "unknown"

    @pytest.mark.parametrize(
        ("bcs_type", "subclass"),
        [
            ("all_private_chats", BotCommandScopeAllPrivateChats),
            ("all_chat_administrators", BotCommandScopeAllChatAdministrators),
            ("all_group_chats", BotCommandScopeAllGroupChats),
            ("chat", BotCommandScopeChat),
            ("chat_administrators", BotCommandScopeChatAdministrators),
            ("chat_member", BotCommandScopeChatMember),
            ("default", BotCommandScopeDefault),
        ],
    )
    def test_de_json_subclass(self, offline_bot, bcs_type, subclass):
        json_dict = {
            "type": bcs_type,
            "chat_id": self.chat_id,
            "user_id": self.user_id,
        }
        bcs = BotCommandScope.de_json(json_dict, offline_bot)

        assert type(bcs) is subclass
        assert set(bcs.api_kwargs.keys()) == set(json_dict.keys()) - set(subclass.__slots__) - {
            "type"
        }
        assert bcs.type == bcs_type

    def test_to_dict(self, bot_command_scope):
        data = bot_command_scope.to_dict()
        assert data == {"type": "default"}

    def test_equality(self, bot_command_scope):
        a = bot_command_scope
        b = BotCommandScope(self.type)
        c = BotCommandScope("unknown")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def bot_command_scope_all_private_chats():
    return BotCommandScopeAllPrivateChats()


class TestBotCommandScopeAllPrivateChatsWithoutRequest(BotCommandScopeTestBase):
    type = BotCommandScopeType.ALL_PRIVATE_CHATS

    def test_slot_behaviour(self, bot_command_scope_all_private_chats):
        inst = bot_command_scope_all_private_chats
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        transaction_partner = BotCommandScopeAllPrivateChats.de_json({}, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "all_private_chats"

    def test_to_dict(self, bot_command_scope_all_private_chats):
        assert bot_command_scope_all_private_chats.to_dict() == {
            "type": bot_command_scope_all_private_chats.type
        }

    def test_equality(self, bot_command_scope_all_private_chats):
        a = bot_command_scope_all_private_chats
        b = BotCommandScopeAllPrivateChats()
        c = Dice(5, "test")
        d = BotCommandScopeDefault()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def bot_command_scope_all_chat_administrators():
    return BotCommandScopeAllChatAdministrators()


class TestBotCommandScopeAllChatAdministratorsWithoutRequest(BotCommandScopeTestBase):
    type = BotCommandScopeType.ALL_CHAT_ADMINISTRATORS

    def test_slot_behaviour(self, bot_command_scope_all_chat_administrators):
        inst = bot_command_scope_all_chat_administrators
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        transaction_partner = BotCommandScopeAllChatAdministrators.de_json({}, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "all_chat_administrators"

    def test_to_dict(self, bot_command_scope_all_chat_administrators):
        assert bot_command_scope_all_chat_administrators.to_dict() == {
            "type": bot_command_scope_all_chat_administrators.type
        }

    def test_equality(self, bot_command_scope_all_chat_administrators):
        a = bot_command_scope_all_chat_administrators
        b = BotCommandScopeAllChatAdministrators()
        c = Dice(5, "test")
        d = BotCommandScopeDefault()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def bot_command_scope_all_group_chats():
    return BotCommandScopeAllGroupChats()


class TestBotCommandScopeAllGroupChatsWithoutRequest(BotCommandScopeTestBase):
    type = BotCommandScopeType.ALL_GROUP_CHATS

    def test_slot_behaviour(self, bot_command_scope_all_group_chats):
        inst = bot_command_scope_all_group_chats
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        transaction_partner = BotCommandScopeAllGroupChats.de_json({}, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "all_group_chats"

    def test_to_dict(self, bot_command_scope_all_group_chats):
        assert bot_command_scope_all_group_chats.to_dict() == {
            "type": bot_command_scope_all_group_chats.type
        }

    def test_equality(self, bot_command_scope_all_group_chats):
        a = bot_command_scope_all_group_chats
        b = BotCommandScopeAllGroupChats()
        c = Dice(5, "test")
        d = BotCommandScopeDefault()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def bot_command_scope_chat():
    return BotCommandScopeChat(TestBotCommandScopeChatWithoutRequest.chat_id)


class TestBotCommandScopeChatWithoutRequest(BotCommandScopeTestBase):
    type = BotCommandScopeType.CHAT

    def test_slot_behaviour(self, bot_command_scope_chat):
        inst = bot_command_scope_chat
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        transaction_partner = BotCommandScopeChat.de_json({"chat_id": self.chat_id}, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "chat"
        assert transaction_partner.chat_id == self.chat_id

    def test_to_dict(self, bot_command_scope_chat):
        assert bot_command_scope_chat.to_dict() == {
            "type": bot_command_scope_chat.type,
            "chat_id": self.chat_id,
        }

    def test_equality(self, bot_command_scope_chat):
        a = bot_command_scope_chat
        b = BotCommandScopeChat(self.chat_id)
        c = BotCommandScopeChat(self.chat_id + 1)
        d = Dice(5, "test")
        e = BotCommandScopeDefault()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture
def bot_command_scope_chat_administrators():
    return BotCommandScopeChatAdministrators(
        TestBotCommandScopeChatAdministratorsWithoutRequest.chat_id
    )


class TestBotCommandScopeChatAdministratorsWithoutRequest(BotCommandScopeTestBase):
    type = BotCommandScopeType.CHAT_ADMINISTRATORS

    def test_slot_behaviour(self, bot_command_scope_chat_administrators):
        inst = bot_command_scope_chat_administrators
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        transaction_partner = BotCommandScopeChatAdministrators.de_json(
            {"chat_id": self.chat_id}, offline_bot
        )
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "chat_administrators"
        assert transaction_partner.chat_id == self.chat_id

    def test_to_dict(self, bot_command_scope_chat_administrators):
        assert bot_command_scope_chat_administrators.to_dict() == {
            "type": bot_command_scope_chat_administrators.type,
            "chat_id": self.chat_id,
        }

    def test_equality(self, bot_command_scope_chat_administrators):
        a = bot_command_scope_chat_administrators
        b = BotCommandScopeChatAdministrators(self.chat_id)
        c = BotCommandScopeChatAdministrators(self.chat_id + 1)
        d = Dice(5, "test")
        e = BotCommandScopeDefault()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture
def bot_command_scope_chat_member():
    return BotCommandScopeChatMember(
        TestBotCommandScopeChatMemberWithoutRequest.chat_id,
        TestBotCommandScopeChatMemberWithoutRequest.user_id,
    )


class TestBotCommandScopeChatMemberWithoutRequest(BotCommandScopeTestBase):
    type = BotCommandScopeType.CHAT_MEMBER

    def test_slot_behaviour(self, bot_command_scope_chat_member):
        inst = bot_command_scope_chat_member
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        transaction_partner = BotCommandScopeChatMember.de_json(
            {"chat_id": self.chat_id, "user_id": self.user_id}, offline_bot
        )
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "chat_member"
        assert transaction_partner.chat_id == self.chat_id
        assert transaction_partner.user_id == self.user_id

    def test_to_dict(self, bot_command_scope_chat_member):
        assert bot_command_scope_chat_member.to_dict() == {
            "type": bot_command_scope_chat_member.type,
            "chat_id": self.chat_id,
            "user_id": self.user_id,
        }

    def test_equality(self, bot_command_scope_chat_member):
        a = bot_command_scope_chat_member
        b = BotCommandScopeChatMember(self.chat_id, self.user_id)
        c = BotCommandScopeChatMember(self.chat_id + 1, self.user_id)
        d = BotCommandScopeChatMember(self.chat_id, self.user_id + 1)
        e = Dice(5, "test")
        f = BotCommandScopeDefault()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)


@pytest.fixture
def bot_command_scope_default():
    return BotCommandScopeDefault()


class TestBotCommandScopeDefaultWithoutRequest(BotCommandScopeTestBase):
    type = BotCommandScopeType.DEFAULT

    def test_slot_behaviour(self, bot_command_scope_default):
        inst = bot_command_scope_default
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        transaction_partner = BotCommandScopeDefault.de_json({}, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "default"

    def test_to_dict(self, bot_command_scope_default):
        assert bot_command_scope_default.to_dict() == {"type": bot_command_scope_default.type}

    def test_equality(self, bot_command_scope_default):
        a = bot_command_scope_default
        b = BotCommandScopeDefault()
        c = Dice(5, "test")
        d = BotCommandScopeChatMember(123, 456)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
