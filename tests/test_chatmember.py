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
import datetime
from copy import deepcopy

import pytest

from telegram.utils.helpers import to_timestamp
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
def chat_member_class_and_status(request):
    return request.param


@pytest.fixture(scope='class')
def chat_member_types(chat_member_class_and_status, user):
    return chat_member_class_and_status[0](status=chat_member_class_and_status[1], user=user)


class TestChatMember:
    def test_slot_behaviour(self, chat_member_types, mro_slots, recwarn):
        for attr in chat_member_types.__slots__:
            assert getattr(chat_member_types, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not chat_member_types.__dict__, f"got missing slot(s): {chat_member_types.__dict__}"
        assert len(mro_slots(chat_member_types)) == len(
            set(mro_slots(chat_member_types))
        ), "duplicate slot"
        chat_member_types.custom, chat_member_types.status = 'warning!', chat_member_types.status
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json_required_args(self, bot, chat_member_class_and_status, user):
        cls = chat_member_class_and_status[0]
        status = chat_member_class_and_status[1]

        assert cls.de_json({}, bot) is None

        json_dict = {'status': status, 'user': user.to_dict()}
        chat_member_type = ChatMember.de_json(json_dict, bot)

        assert isinstance(chat_member_type, ChatMember)
        assert isinstance(chat_member_type, cls)
        assert chat_member_type.status == status
        assert chat_member_type.user == user

    def test_de_json_all_args(self, bot, chat_member_class_and_status, user):
        cls = chat_member_class_and_status[0]
        status = chat_member_class_and_status[1]
        time = datetime.datetime.utcnow()

        json_dict = {
            'user': user.to_dict(),
            'status': status,
            'custom_title': 'PTB',
            'is_anonymous': True,
            'until_date': to_timestamp(time),
            'can_be_edited': False,
            'can_change_info': True,
            'can_post_messages': False,
            'can_edit_messages': True,
            'can_delete_messages': True,
            'can_invite_users': False,
            'can_restrict_members': True,
            'can_pin_messages': False,
            'can_promote_members': True,
            'can_send_messages': False,
            'can_send_media_messages': True,
            'can_send_polls': False,
            'can_send_other_messages': True,
            'can_add_web_page_previews': False,
            'can_manage_chat': True,
            'can_manage_voice_chats': True,
        }
        chat_member_type = ChatMember.de_json(json_dict, bot)

        assert isinstance(chat_member_type, ChatMember)
        assert isinstance(chat_member_type, cls)
        assert chat_member_type.user == user
        assert chat_member_type.status == status
        if chat_member_type.custom_title is not None:
            assert chat_member_type.custom_title == 'PTB'
            assert type(chat_member_type) in {ChatMemberOwner, ChatMemberAdministrator}
        if chat_member_type.is_anonymous is not None:
            assert chat_member_type.is_anonymous is True
            assert type(chat_member_type) in {ChatMemberOwner, ChatMemberAdministrator}
        if chat_member_type.until_date is not None:
            assert type(chat_member_type) in {ChatMemberBanned, ChatMemberRestricted}
        if chat_member_type.can_be_edited is not None:
            assert chat_member_type.can_be_edited is False
            assert type(chat_member_type) == ChatMemberAdministrator
        if chat_member_type.can_change_info is not None:
            assert chat_member_type.can_change_info is True
            assert type(chat_member_type) in {ChatMemberAdministrator, ChatMemberRestricted}
        if chat_member_type.can_post_messages is not None:
            assert chat_member_type.can_post_messages is False
            assert type(chat_member_type) == ChatMemberAdministrator
        if chat_member_type.can_edit_messages is not None:
            assert chat_member_type.can_edit_messages is True
            assert type(chat_member_type) == ChatMemberAdministrator
        if chat_member_type.can_delete_messages is not None:
            assert chat_member_type.can_delete_messages is True
            assert type(chat_member_type) == ChatMemberAdministrator
        if chat_member_type.can_invite_users is not None:
            assert chat_member_type.can_invite_users is False
            assert type(chat_member_type) in {ChatMemberAdministrator, ChatMemberRestricted}
        if chat_member_type.can_restrict_members is not None:
            assert chat_member_type.can_restrict_members is True
            assert type(chat_member_type) == ChatMemberAdministrator
        if chat_member_type.can_pin_messages is not None:
            assert chat_member_type.can_pin_messages is False
            assert type(chat_member_type) in {ChatMemberAdministrator, ChatMemberRestricted}
        if chat_member_type.can_promote_members is not None:
            assert chat_member_type.can_promote_members is True
            assert type(chat_member_type) == ChatMemberAdministrator
        if chat_member_type.can_send_messages is not None:
            assert chat_member_type.can_send_messages is False
            assert type(chat_member_type) == ChatMemberRestricted
        if chat_member_type.can_send_media_messages is not None:
            assert chat_member_type.can_send_media_messages is True
            assert type(chat_member_type) == ChatMemberRestricted
        if chat_member_type.can_send_polls is not None:
            assert chat_member_type.can_send_polls is False
            assert type(chat_member_type) == ChatMemberRestricted
        if chat_member_type.can_send_other_messages is not None:
            assert chat_member_type.can_send_other_messages is True
            assert type(chat_member_type) == ChatMemberRestricted
        if chat_member_type.can_add_web_page_previews is not None:
            assert chat_member_type.can_add_web_page_previews is False
            assert type(chat_member_type) == ChatMemberRestricted
        if chat_member_type.can_manage_chat is not None:
            assert chat_member_type.can_manage_chat is True
            assert type(chat_member_type) == ChatMemberAdministrator
        if chat_member_type.can_manage_voice_chats is not None:
            assert chat_member_type.can_manage_voice_chats is True
            assert type(chat_member_type) == ChatMemberAdministrator

    def test_de_json_invalid_status(self, bot, user):
        json_dict = {'status': 'invalid', 'user': user.to_dict()}
        chat_member_type = ChatMember.de_json(json_dict, bot)

        assert type(chat_member_type) is ChatMember
        assert chat_member_type.status == 'invalid'

    def test_de_json_subclass(self, chat_member_class_and_status, bot, chat_id, user):
        """This makes sure that e.g. ChatMemberAdministrator(data, bot) never returns a
        ChatMemberKicked instance."""
        cls = chat_member_class_and_status[0]
        time = datetime.datetime.utcnow()
        json_dict = {
            'user': user.to_dict(),
            'status': 'status',
            'custom_title': 'PTB',
            'is_anonymous': True,
            'until_date': to_timestamp(time),
            'can_be_edited': False,
            'can_change_info': True,
            'can_post_messages': False,
            'can_edit_messages': True,
            'can_delete_messages': True,
            'can_invite_users': False,
            'can_restrict_members': True,
            'can_pin_messages': False,
            'can_promote_members': True,
            'can_send_messages': False,
            'can_send_media_messages': True,
            'can_send_polls': False,
            'can_send_other_messages': True,
            'can_add_web_page_previews': False,
            'can_manage_chat': True,
            'can_manage_voice_chats': True,
        }
        assert type(cls.de_json(json_dict, bot)) is cls

    def test_to_dict(self, chat_member_types, user):
        chat_member_dict = chat_member_types.to_dict()

        assert isinstance(chat_member_dict, dict)
        assert chat_member_dict['status'] == chat_member_types.status
        assert chat_member_dict['user'] == user.to_dict()

    def test_equality(self, chat_member_types, user):
        a = ChatMember(status='status', user=user)
        b = ChatMember(status='status', user=user)
        c = chat_member_types
        d = deepcopy(chat_member_types)
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
