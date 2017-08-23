#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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

from telegram import Chat, ChatAction
from telegram import User


@pytest.fixture(scope='class')
def chat(bot):
    return Chat(TestChat.id, TestChat.title, TestChat.type,
                all_members_are_administrators=TestChat.all_members_are_administrators,
                bot=bot)


class TestChat(object):
    id = -28767330
    title = 'ToledosPalaceBot - Group'
    type = 'group'
    all_members_are_administrators = False

    def test_de_json(self, bot):
        json_dict = {
            'id': TestChat.id,
            'title': TestChat.title,
            'type': TestChat.type,
            'all_members_are_administrators': TestChat.all_members_are_administrators
        }
        chat = Chat.de_json(json_dict, bot)

        assert chat.id == self.id
        assert chat.title == self.title
        assert chat.type == self.type
        assert chat.all_members_are_administrators == self.all_members_are_administrators

    def test_to_dict(self, chat):
        chat_dict = chat.to_dict()

        assert isinstance(chat_dict, dict)
        assert chat_dict['id'] == chat.id
        assert chat_dict['title'] == chat.title
        assert chat_dict['type'] == chat.type
        assert chat_dict['all_members_are_administrators'] == chat.all_members_are_administrators

    def test_send_action(self, monkeypatch, chat):
        def test(*args, **kwargs):
            id = args[1] == chat.id
            action = kwargs['action'] == ChatAction.TYPING
            return id and action

        monkeypatch.setattr('telegram.Bot.send_chat_action', test)
        assert chat.send_action(action=ChatAction.TYPING)

    def test_leave(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[1] == chat.id

        monkeypatch.setattr('telegram.Bot.leave_chat', test)
        assert chat.leave()

    def test_get_administrators(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[1] == chat.id

        monkeypatch.setattr('telegram.Bot.get_chat_administrators', test)
        assert chat.get_administrators()

    def test_get_members_count(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[1] == chat.id

        monkeypatch.setattr('telegram.Bot.get_chat_members_count', test)
        assert chat.get_members_count()

    def test_get_member(self, monkeypatch, chat):
        def test(*args, **kwargs):
            chat_id = args[1] == chat.id
            user_id = args[2] == 42
            return chat_id and user_id

        monkeypatch.setattr('telegram.Bot.get_chat_member', test)
        assert chat.get_member(42)

    def test_kick_member(self, monkeypatch, chat):
        def test(*args, **kwargs):
            chat_id = args[1] == chat.id
            user_id = args[2] == 42
            until = kwargs['until_date'] == 43
            return chat_id and user_id and until

        monkeypatch.setattr('telegram.Bot.kick_chat_member', test)
        assert chat.kick_member(42, until_date=43)

    def test_unban_member(self, monkeypatch, chat):
        def test(*args, **kwargs):
            chat_id = args[1] == chat.id
            user_id = args[2] == 42
            return chat_id and user_id

        monkeypatch.setattr('telegram.Bot.unban_chat_member', test)
        assert chat.unban_member(42)

    def test_equality(self):
        a = Chat(self.id, self.title, self.type)
        b = Chat(self.id, self.title, self.type)
        c = Chat(self.id, '', '')
        d = Chat(0, self.title, self.type)
        e = User(self.id, '', False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
