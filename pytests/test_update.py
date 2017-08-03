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
import json

import pytest

from telegram import Message, User, Update

@pytest.fixture(scope='class')
def json_dict():
    return {'update_id': TestUpdate.update_id, 'message': TestUpdate.message}

@pytest.fixture(scope='class')
def update():
   return Update(update_id=TestUpdate.update_id, message=TestUpdate.message})

class TestUpdate:
    """This object represents Tests for Telegram Update."""

    update_id = 868573637
    message = {
    'message_id': 319,
    'from': {
    'id': 12173560,
    'first_name': "Leandro",
    'last_name': "S.",
    'username': "leandrotoledo"
    },
    'chat': {
    'id': 12173560,
    'type': 'private',
    'first_name': "Leandro",
    'last_name': "S.",
    'username': "leandrotoledo"
    },
    'date': 1441644592,
    'text': "Update Test"
    }
    
    
    
    def test_de_json(self):
        update = Update.de_json(json_dict, bot)

        assert update.update_id == self.update_id
        assert isinstance(update.message, Message)

    def test_update_de_json_empty(self):
        update = Update.de_json(None, bot)

        assert update is False

    def test_to_json(self):
        update = Update.de_json(json_dict, bot)

        json.loads(update.to_json())

    def test_to_dict(self):
        update = Update.de_json(json_dict, bot)

        assert isinstance(update.to_dict(), dict)
        assert update['update_id'] == self.update_id
        assert isinstance(update['message'], Message)

    def test_effective_chat(self):
        update = Update.de_json(json_dict, bot)
        chat = update.effective_chat
        assert update.message.chat == chat

    def test_effective_user(self):
        update = Update.de_json(json_dict, bot)
        user = update.effective_user
        assert update.message.from_user == user

    def test_effective_message(self):
        update = Update.de_json(json_dict, bot)
        message = update.effective_message
        assert update.message.text == message.text

    def test_equality(self):
        a = Update(self.update_id, message=self.message)
        b = Update(self.update_id, message=self.message)
        c = Update(self.update_id)
        d = Update(0, message=self.message)
        e = User(self.update_id, "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


