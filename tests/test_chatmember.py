#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
    User,
    ChatMember,
    ChatMemberOwner,
    ChatMemberAdministrator,
    ChatMemberMember,
    ChatMemberRestricted,
    ChatMemberLeft,
    ChatMemberBanned,
    Dice,
)


@pytest.fixture(scope='class')
def user():
    return User(1, 'First name', False)


@pytest.fixture(
    scope="class",
    params=[
        (ChatMemberOwner, ChatMember.CREATOR),
        (ChatMemberAdministrator, ChatMember.ADMINISTRATOR),
        (ChatMemberMember, ChatMember.MEMBER),
        (ChatMemberRestricted, ChatMember.RESTRICTED),
        (ChatMemberLeft, ChatMember.LEFT),
        (ChatMemberBanned, ChatMember.KICKED),
    ],
    ids=[
        ChatMember.CREATOR,
        ChatMember.ADMINISTRATOR,
        ChatMember.MEMBER,
        ChatMember.RESTRICTED,
        ChatMember.LEFT,
        ChatMember.KICKED,
    ],
)
def chatmember_class_and_status(request):
    return request.param


@pytest.fixture(scope='class')
def chatmember_types(chatmember_class_and_status, user):
    return chatmember_class_and_status[0](status=chatmember_class_and_status[1], user=user)


class TestChatMember:
    def test_slot_behaviour(self, chatmember_types, mro_slots):
        for attr in chatmember_types.__slots__:
            assert getattr(chatmember_types, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(chatmember_types)) == len(
            set(mro_slots(chatmember_types))
        ), "duplicate slot"
        with pytest.raises(AttributeError):
            chatmember_types.custom

    def test_de_json(self, bot, chatmember_class_and_status, user):
        cls = chatmember_class_and_status[0]
        status = chatmember_class_and_status[1]

        assert cls.de_json({}, bot) is None

        json_dict = {'status': status, 'user': user.to_dict()}
        chatmember_type = ChatMember.de_json(json_dict, bot)

        assert isinstance(chatmember_type, ChatMember)
        assert isinstance(chatmember_type, cls)
        assert chatmember_type.status == status

    def test_de_json_invalid_status(self, bot, user):
        json_dict = {'status': 'invalid', 'user': user.to_dict()}
        chatmember_type = ChatMember.de_json(json_dict, bot)

        assert type(chatmember_type) is ChatMember
        assert chatmember_type.status == 'invalid'

    def test_to_dict(self, chatmember_types, user):
        chatmember_dict = chatmember_types.to_dict()

        assert isinstance(chatmember_dict, dict)
        assert chatmember_dict['status'] == chatmember_types.status
        assert chatmember_dict['user'] == user.to_dict()

    def test_equality(self, chatmember_types, user):
        a = ChatMember(status='status', user=user)
        b = ChatMember(status='status', user=user)
        c = chatmember_types
        d = deepcopy(chatmember_types)
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
