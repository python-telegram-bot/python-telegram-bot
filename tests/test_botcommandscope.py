#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2021
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
from copy import deepcopy

import pytest

from telegram import (
    Dice,
    BotCommandScope,
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeChat,
    BotCommandScopeChatAdministrators,
    BotCommandScopeChatMember,
)


@pytest.fixture(scope="class", params=['str', 'int'])
def chat_id(request):
    if request.param == 'str':
        return '@supergroupusername'
    return 43


@pytest.fixture(
    scope="class",
    params=[
        BotCommandScope.DEFAULT,
        BotCommandScope.ALL_PRIVATE_CHATS,
        BotCommandScope.ALL_GROUP_CHATS,
        BotCommandScope.ALL_CHAT_ADMINISTRATORS,
        BotCommandScope.CHAT,
        BotCommandScope.CHAT_ADMINISTRATORS,
        BotCommandScope.CHAT_MEMBER,
    ],
)
def scope_type(request):
    return request.param


@pytest.fixture(
    scope="class",
    params=[
        BotCommandScopeDefault,
        BotCommandScopeAllPrivateChats,
        BotCommandScopeAllGroupChats,
        BotCommandScopeAllChatAdministrators,
        BotCommandScopeChat,
        BotCommandScopeChatAdministrators,
        BotCommandScopeChatMember,
    ],
    ids=[
        BotCommandScope.DEFAULT,
        BotCommandScope.ALL_PRIVATE_CHATS,
        BotCommandScope.ALL_GROUP_CHATS,
        BotCommandScope.ALL_CHAT_ADMINISTRATORS,
        BotCommandScope.CHAT,
        BotCommandScope.CHAT_ADMINISTRATORS,
        BotCommandScope.CHAT_MEMBER,
    ],
)
def scope_class(request):
    return request.param


@pytest.fixture(
    scope="class",
    params=[
        (BotCommandScopeDefault, BotCommandScope.DEFAULT),
        (BotCommandScopeAllPrivateChats, BotCommandScope.ALL_PRIVATE_CHATS),
        (BotCommandScopeAllGroupChats, BotCommandScope.ALL_GROUP_CHATS),
        (BotCommandScopeAllChatAdministrators, BotCommandScope.ALL_CHAT_ADMINISTRATORS),
        (BotCommandScopeChat, BotCommandScope.CHAT),
        (BotCommandScopeChatAdministrators, BotCommandScope.CHAT_ADMINISTRATORS),
        (BotCommandScopeChatMember, BotCommandScope.CHAT_MEMBER),
    ],
    ids=[
        BotCommandScope.DEFAULT,
        BotCommandScope.ALL_PRIVATE_CHATS,
        BotCommandScope.ALL_GROUP_CHATS,
        BotCommandScope.ALL_CHAT_ADMINISTRATORS,
        BotCommandScope.CHAT,
        BotCommandScope.CHAT_ADMINISTRATORS,
        BotCommandScope.CHAT_MEMBER,
    ],
)
def scope_class_and_type(request):
    return request.param


@pytest.fixture(scope='class')
def bot_command_scope(scope_class_and_type, chat_id):
    return scope_class_and_type[0](type=scope_class_and_type[1], chat_id=chat_id, user_id=42)


# All the scope types are very similar, so we test everything via parametrization
class TestBotCommandScope:
    def test_slot_behaviour(self, bot_command_scope, mro_slots, recwarn):
        for attr in bot_command_scope.__slots__:
            assert getattr(bot_command_scope, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not bot_command_scope.__dict__, f"got missing slot(s): {bot_command_scope.__dict__}"
        assert len(mro_slots(bot_command_scope)) == len(
            set(mro_slots(bot_command_scope))
        ), "duplicate slot"
        bot_command_scope.custom, bot_command_scope.type = 'warning!', bot_command_scope.type
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self, bot, scope_class_and_type, chat_id):
        cls = scope_class_and_type[0]
        type_ = scope_class_and_type[1]

        assert cls.de_json({}, bot) is None

        json_dict = {'type': type_, 'chat_id': chat_id, 'user_id': 42}
        bot_command_scope = BotCommandScope.de_json(json_dict, bot)

        assert isinstance(bot_command_scope, BotCommandScope)
        assert isinstance(bot_command_scope, cls)
        assert bot_command_scope.type == type_
        if 'chat_id' in cls.__slots__:
            assert bot_command_scope.chat_id == chat_id
        if 'user_id' in cls.__slots__:
            assert bot_command_scope.user_id == 42

    def test_de_json_invalid_type(self, bot):
        json_dict = {'type': 'invalid', 'chat_id': chat_id, 'user_id': 42}
        bot_command_scope = BotCommandScope.de_json(json_dict, bot)

        assert type(bot_command_scope) is BotCommandScope
        assert bot_command_scope.type == 'invalid'

    def test_de_json_subclass(self, scope_class, bot, chat_id):
        """This makes sure that e.g. BotCommandScopeDefault(data) never returns a
        BotCommandScopeChat instance."""
        json_dict = {'type': 'invalid', 'chat_id': chat_id, 'user_id': 42}
        assert type(scope_class.de_json(json_dict, bot)) is scope_class

    def test_to_dict(self, bot_command_scope):
        bot_command_scope_dict = bot_command_scope.to_dict()

        assert isinstance(bot_command_scope_dict, dict)
        assert bot_command_scope['type'] == bot_command_scope.type
        if hasattr(bot_command_scope, 'chat_id'):
            assert bot_command_scope['chat_id'] == bot_command_scope.chat_id
        if hasattr(bot_command_scope, 'user_id'):
            assert bot_command_scope['user_id'] == bot_command_scope.user_id

    def test_equality(self, bot_command_scope, bot):
        a = BotCommandScope('base_type')
        b = BotCommandScope('base_type')
        c = bot_command_scope
        d = deepcopy(bot_command_scope)
        e = Dice(4, 'emoji')

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)

        if hasattr(c, 'chat_id'):
            json_dict = c.to_dict()
            json_dict['chat_id'] = 0
            f = c.__class__.de_json(json_dict, bot)

            assert c != f
            assert hash(c) != hash(f)

        if hasattr(c, 'user_id'):
            json_dict = c.to_dict()
            json_dict['user_id'] = 0
            g = c.__class__.de_json(json_dict, bot)

            assert c != g
            assert hash(c) != hash(g)
