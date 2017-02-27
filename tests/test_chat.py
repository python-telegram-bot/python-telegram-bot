#!/usr/bin/env python
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
"""This module contains an object that represents Tests for Telegram Chat"""

import unittest
import sys

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ChatTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Chat."""

    def setUp(self):
        self.id = -28767330
        self.title = 'ToledosPalaceBot - Group'
        self.type = 'group'
        self.all_members_are_administrators = False

        self.json_dict = {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'all_members_are_administrators': self.all_members_are_administrators
        }

    def test_group_chat_de_json_empty_json(self):
        group_chat = telegram.Chat.de_json({}, self._bot)

        self.assertEqual(group_chat, None)

    def test_group_chat_de_json(self):
        group_chat = telegram.Chat.de_json(self.json_dict, self._bot)

        self.assertEqual(group_chat.id, self.id)
        self.assertEqual(group_chat.title, self.title)
        self.assertEqual(group_chat.type, self.type)
        self.assertEqual(group_chat.all_members_are_administrators,
                         self.all_members_are_administrators)

    def test_group_chat_to_json(self):
        group_chat = telegram.Chat.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(group_chat.to_json()))

    def test_group_chat_to_dict(self):
        group_chat = telegram.Chat.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(group_chat.to_dict()))
        self.assertEqual(group_chat['id'], self.id)
        self.assertEqual(group_chat['title'], self.title)
        self.assertEqual(group_chat['type'], self.type)
        self.assertEqual(group_chat['all_members_are_administrators'],
                         self.all_members_are_administrators)

    @flaky(3, 1)
    def test_send_action(self):
        """Test for Chat.send_action"""
        self.json_dict['id'] = self._chat_id
        group_chat = telegram.Chat.de_json(self.json_dict, self._bot)
        group_chat.bot = self._bot

        result = group_chat.send_action(telegram.ChatAction.TYPING)

        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
