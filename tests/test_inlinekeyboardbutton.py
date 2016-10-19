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
"""This module contains an object that represents Tests for Telegram InlineKeyboardButton"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineKeyboardButtonTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram KeyboardButton."""

    def setUp(self):
        self.text = 'text'
        self.url = 'url'
        self.callback_data = 'callback data'
        self.switch_inline_query = ''

        self.json_dict = {
            'text': self.text,
            'url': self.url,
            'callback_data': self.callback_data,
            'switch_inline_query': self.switch_inline_query
        }

    def test_inline_keyboard_button_de_json(self):
        inline_keyboard_button = telegram.InlineKeyboardButton.de_json(self.json_dict, self._bot)

        self.assertEqual(inline_keyboard_button.text, self.text)
        self.assertEqual(inline_keyboard_button.url, self.url)
        self.assertEqual(inline_keyboard_button.callback_data, self.callback_data)
        self.assertEqual(inline_keyboard_button.switch_inline_query, self.switch_inline_query)

    def test_inline_keyboard_button_de_json_empty(self):
        inline_keyboard_button = telegram.InlineKeyboardButton.de_json(None, self._bot)

        self.assertFalse(inline_keyboard_button)

    def test_inline_keyboard_button_de_list_empty(self):
        inline_keyboard_button = telegram.InlineKeyboardButton.de_list(None, self._bot)

        self.assertFalse(inline_keyboard_button)

    def test_inline_keyboard_button_to_json(self):
        inline_keyboard_button = telegram.InlineKeyboardButton.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(inline_keyboard_button.to_json()))

    def test_inline_keyboard_button_to_dict(self):
        inline_keyboard_button = telegram.InlineKeyboardButton.de_json(self.json_dict,
                                                                       self._bot).to_dict()

        self.assertTrue(self.is_dict(inline_keyboard_button))
        self.assertDictEqual(self.json_dict, inline_keyboard_button)


if __name__ == '__main__':
    unittest.main()
