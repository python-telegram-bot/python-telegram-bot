# !/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
"""This module contains a object that represents Tests for Telegram Chat"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ChatTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Chat."""

    def setUp(self):
        self.id = -28767330
        self.title = 'ToledosPalaceBot - Group'
        self.type = 'group'

        self.json_dict = {
            'id': self.id,
            'title': self.title,
            'type': self.type
        }

    def test_group_chat_de_json_empty_json(self):
        group_chat = telegram.Chat.de_json({})

        self.assertEqual(group_chat, None)

    def test_group_chat_de_json(self):
        group_chat = telegram.Chat.de_json(self.json_dict)

        self.assertEqual(group_chat.id, self.id)
        self.assertEqual(group_chat.title, self.title)
        self.assertEqual(group_chat.type, self.type)

    def test_group_chat_to_json(self):
        group_chat = telegram.Chat.de_json(self.json_dict)

        self.assertTrue(self.is_json(group_chat.to_json()))

    def test_group_chat_to_dict(self):
        group_chat = telegram.Chat.de_json(self.json_dict)

        self.assertTrue(self.is_dict(group_chat.to_dict()))
        self.assertEqual(group_chat['id'], self.id)
        self.assertEqual(group_chat['title'], self.title)
        self.assertEqual(group_chat['type'], self.type)


if __name__ == '__main__':
    unittest.main()
