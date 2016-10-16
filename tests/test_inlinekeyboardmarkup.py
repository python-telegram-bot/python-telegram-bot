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
"""This module contains an object that represents Tests for Telegram InlineKeyboardMarkup"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineKeyboardMarkupTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram KeyboardButton."""

    def setUp(self):
        self.inline_keyboard = [[
            telegram.InlineKeyboardButton(
                text='button1', callback_data='data1'), telegram.InlineKeyboardButton(
                    text='button2', callback_data='data2')
        ]]

        self.json_dict = {
            'inline_keyboard':
            [[self.inline_keyboard[0][0].to_dict(), self.inline_keyboard[0][1].to_dict()]],
        }

    def test_send_message_with_inline_keyboard_markup(self):
        message = self._bot.sendMessage(
            self._chat_id,
            'Testing InlineKeyboardMarkup',
            reply_markup=telegram.InlineKeyboardMarkup(self.inline_keyboard))

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, 'Testing InlineKeyboardMarkup')

    def test_inline_keyboard_markup_de_json_empty(self):
        inline_keyboard_markup = telegram.InlineKeyboardMarkup.de_json(None, self._bot)

        self.assertFalse(inline_keyboard_markup)

    def test_inline_keyboard_markup_de_json(self):
        inline_keyboard_markup = telegram.InlineKeyboardMarkup.de_json(self.json_dict, self._bot)

        self.assertTrue(isinstance(inline_keyboard_markup.inline_keyboard, list))
        self.assertTrue(
            isinstance(inline_keyboard_markup.inline_keyboard[0][0],
                       telegram.InlineKeyboardButton))

    def test_inline_keyboard_markup_to_json(self):
        inline_keyboard_markup = telegram.InlineKeyboardMarkup.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(inline_keyboard_markup.to_json()))

    def test_inline_keyboard_markup_to_dict(self):
        inline_keyboard_markup = telegram.InlineKeyboardMarkup.de_json(self.json_dict, self._bot)

        self.assertTrue(isinstance(inline_keyboard_markup.inline_keyboard, list))
        self.assertTrue(
            isinstance(inline_keyboard_markup.inline_keyboard[0][0],
                       telegram.InlineKeyboardButton))


if __name__ == '__main__':
    unittest.main()
