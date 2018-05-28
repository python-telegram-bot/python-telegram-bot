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

from telegram import Sticker
from telegram import Update
from telegram import User
from telegram.message import Message
from telegram.utils import helpers


class TestHelpers(object):
    def test_escape_markdown(self):
        test_str = '*bold*, _italic_, `code`, [text_link](http://github.com/)'
        expected_str = '\*bold\*, \_italic\_, \`code\`, \[text\_link](http://github.com/)'

        assert expected_str == helpers.escape_markdown(test_str)

    def test_effective_message_type(self):
        test_message = Message(message_id=1,
                               from_user=None,
                               date=None,
                               chat=None)

        test_message.text = 'Test'
        assert helpers.effective_message_type(test_message) == 'text'
        test_message.text = None

        test_message.sticker = Sticker('sticker_id', 50, 50)
        assert helpers.effective_message_type(test_message) == 'sticker'
        test_message.sticker = None

        test_message.new_chat_members = [User(55, 'new_user', False)]
        assert helpers.effective_message_type(test_message) == 'new_chat_members'

        test_update = Update(1)
        test_message.text = 'Test'
        test_update.message = test_message
        assert helpers.effective_message_type(test_update) == 'text'

        empty_update = Update(2)
        assert helpers.effective_message_type(empty_update) is None

    def test_mention_html(self):
        expected = '<a href="tg://user?id=1">the name</a>'

        assert expected == helpers.mention_html(1, 'the name')

    def test_mention_markdown(self):
        expected = '[the name](tg://user?id=1)'

        assert expected == helpers.mention_markdown(1, 'the name')
