#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

import pytest

from telegram import User, ChatMember
from telegram.utils.helpers import to_timestamp


@pytest.fixture(scope='class')
def user():
    return User(1, 'First name', False)


@pytest.fixture(scope='class')
def chat_member(user):
    return ChatMember(user, TestChatMember.status)


class TestChatMember(object):
    status = ChatMember.CREATOR

    def test_de_json_required_args(self, bot, user):
        json_dict = {'user': user.to_dict(), 'status': self.status}

        chat_member = ChatMember.de_json(json_dict, bot)

        assert chat_member.user == user
        assert chat_member.status == self.status

    def test_de_json_all_args(self, bot, user):
        time = datetime.datetime.now()
        json_dict = {'user': user.to_dict(),
                     'status': self.status,
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
                     'can_send_other_messages': False,
                     'can_add_web_page_previews': True}

        chat_member = ChatMember.de_json(json_dict, bot)

        assert chat_member.user == user
        assert chat_member.status == self.status
        assert chat_member.can_be_edited is False
        assert chat_member.can_change_info is True
        assert chat_member.can_post_messages is False
        assert chat_member.can_edit_messages is True
        assert chat_member.can_delete_messages is True
        assert chat_member.can_invite_users is False
        assert chat_member.can_restrict_members is True
        assert chat_member.can_pin_messages is False
        assert chat_member.can_promote_members is True
        assert chat_member.can_send_messages is False
        assert chat_member.can_send_media_messages is True
        assert chat_member.can_send_other_messages is False
        assert chat_member.can_add_web_page_previews is True

    def test_to_dict(self, chat_member):
        chat_member_dict = chat_member.to_dict()
        assert isinstance(chat_member_dict, dict)
        assert chat_member_dict['user'] == chat_member.user.to_dict()
        assert chat_member['status'] == chat_member.status

    def test_equality(self):
        a = ChatMember(User(1, '', False), ChatMember.ADMINISTRATOR)
        b = ChatMember(User(1, '', False), ChatMember.ADMINISTRATOR)
        d = ChatMember(User(2, '', False), ChatMember.ADMINISTRATOR)
        d2 = ChatMember(User(1, '', False), ChatMember.CREATOR)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != d2
        assert hash(a) != hash(d2)
