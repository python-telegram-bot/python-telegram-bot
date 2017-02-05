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
"""This module contains an object that represents Tests for Telegram Update"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class UpdateTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Update."""

    def setUp(self):
        self.update_id = 868573637
        self.message = {
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

        self.json_dict = {'update_id': self.update_id, 'message': self.message}

    def test_update_de_json(self):
        update = telegram.Update.de_json(self.json_dict, self._bot)

        self.assertEqual(update.update_id, self.update_id)
        self.assertTrue(isinstance(update.message, telegram.Message))

    def test_update_de_json_empty(self):
        update = telegram.Update.de_json(None, self._bot)

        self.assertFalse(update)

    def test_update_to_json(self):
        update = telegram.Update.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(update.to_json()))

    def test_update_to_dict(self):
        update = telegram.Update.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(update.to_dict()))
        self.assertEqual(update['update_id'], self.update_id)
        self.assertTrue(isinstance(update['message'], telegram.Message))

    def test_extract_chat_and_user(self):
        update = telegram.Update.de_json(self.json_dict, self._bot)
        chat, user = update.extract_chat_and_user()
        self.assertEqual(update.message.chat, chat)
        self.assertEqual(update.message.from_user, user)

    def test_extract_message_text(self):
        update = telegram.Update.de_json(self.json_dict, self._bot)
        text = update.extract_message_text()
        self.assertEqual(update.message.text, text)


if __name__ == '__main__':
    unittest.main()
