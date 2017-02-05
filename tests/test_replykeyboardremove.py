#!/usr/bin/env python
# encoding: utf-8
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
"""This module contains an object that represents Tests for Telegram ReplyKeyboardRemove"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ReplyKeyboardRemoveTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram ReplyKeyboardRemove."""

    def setUp(self):
        self.remove_keyboard = True
        self.selective = True

        self.json_dict = {
            'remove_keyboard': self.remove_keyboard,
            'selective': self.selective,
        }

    def test_send_message_with_reply_keyboard_remove(self):
        message = self._bot.sendMessage(
            self._chat_id,
            'Моё судно на воздушной подушке полно угрей',
            reply_markup=telegram.ReplyKeyboardRemove.de_json(self.json_dict, self._bot))

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, u'Моё судно на воздушной подушке полно угрей')

    def test_reply_keyboard_remove_de_json(self):
        reply_keyboard_remove = telegram.ReplyKeyboardRemove.de_json(self.json_dict, self._bot)

        self.assertEqual(reply_keyboard_remove.remove_keyboard, self.remove_keyboard)
        self.assertEqual(reply_keyboard_remove.selective, self.selective)

    def test_reply_keyboard_remove_de_json_empty(self):
        reply_keyboard_remove = telegram.ReplyKeyboardRemove.de_json(None, self._bot)

        self.assertFalse(reply_keyboard_remove)

    def test_reply_keyboard_remove_to_json(self):
        reply_keyboard_remove = telegram.ReplyKeyboardRemove.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(reply_keyboard_remove.to_json()))

    def test_reply_keyboard_remove_to_dict(self):
        reply_keyboard_remove = telegram.ReplyKeyboardRemove.de_json(self.json_dict, self._bot)

        self.assertEqual(reply_keyboard_remove['remove_keyboard'], self.remove_keyboard)
        self.assertEqual(reply_keyboard_remove['selective'], self.selective)


if __name__ == '__main__':
    unittest.main()
