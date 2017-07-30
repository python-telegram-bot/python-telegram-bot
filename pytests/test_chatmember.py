#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import datetime
import json

import pytest

from telegram import User, ChatMember


@pytest.fixture(scope="class")
def user():
    return User(1, "User")


@pytest.fixture(scope="class")
def chatmember(user):
    return ChatMember(user, TestChatMember.status)


class TestChatMember:
    status = ChatMember.CREATOR

    def test_chatmember_de_json_required_args(self, bot, user):
        json_dict = {'user': user.to_dict(), 'status': self.status}

        chatmember = ChatMember.de_json(json_dict, bot)

        assert chatmember.user == user
        assert chatmember.status == self.status

    def test_chatmember_de_json_all_args(self, bot, user):
        time = datetime.datetime.now()
        json_dict = {'user': user.to_dict(), 'status': self.status,
                     'until_date': time.timestamp(),
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

        chatmember = ChatMember.de_json(json_dict, bot)

        assert chatmember.user == user
        assert chatmember.status == self.status
        assert chatmember.can_be_edited is False
        assert chatmember.can_change_info is True
        assert chatmember.can_post_messages is False
        assert chatmember.can_edit_messages is True
        assert chatmember.can_delete_messages is True
        assert chatmember.can_invite_users is False
        assert chatmember.can_restrict_members is True
        assert chatmember.can_pin_messages is False
        assert chatmember.can_promote_members is True
        assert chatmember.can_send_messages is False
        assert chatmember.can_send_media_messages is True
        assert chatmember.can_send_other_messages is False
        assert chatmember.can_add_web_page_previews is True

    def test_chatmember_to_json(self, chatmember):
        json.loads(chatmember.to_json())

    def test_chatmember_to_dict(self, chatmember):
        chatmember_dict = chatmember.to_dict()
        assert isinstance(chatmember_dict, dict)
        assert chatmember_dict['user'] == chatmember.user.to_dict()
        assert chatmember['status'] == chatmember.status

    def test_equality(self):
        a = ChatMember(User(1, ""), ChatMember.ADMINISTRATOR)
        b = ChatMember(User(1, ""), ChatMember.ADMINISTRATOR)
        d = ChatMember(User(2, ""), ChatMember.ADMINISTRATOR)
        d2 = ChatMember(User(1, ""), ChatMember.CREATOR)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != d2
        assert hash(a) != hash(d2)
