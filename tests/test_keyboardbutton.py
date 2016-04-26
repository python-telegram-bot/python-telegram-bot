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
"""This module contains a object that represents Tests for Telegram
KeyboardButton"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class KeyboardButtonTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram KeyboardButton."""

    def setUp(self):
        self.text = 'text'
        self.request_location = True
        self.request_contact = True

        self.json_dict = {
            'text': self.text,
            'request_location': self.request_location,
            'request_contact': self.request_contact,
        }

    def test_inline_keyboard_button_markup_de_json(self):
        inline_keyboard_button_markup = telegram.KeyboardButton.de_json(
            self.json_dict)

        self.assertEqual(inline_keyboard_button_markup.text, self.text)
        self.assertEqual(inline_keyboard_button_markup.request_location,
                         self.request_location)
        self.assertEqual(inline_keyboard_button_markup.request_contact,
                         self.request_contact)

    def test_inline_keyboard_button_markup_to_json(self):
        inline_keyboard_button_markup = telegram.KeyboardButton.de_json(
            self.json_dict)

        self.assertTrue(self.is_json(inline_keyboard_button_markup.to_json()))

    def test_inline_keyboard_button_markup_to_dict(self):
        inline_keyboard_button_markup = telegram.KeyboardButton.de_json(
            self.json_dict).to_dict()

        self.assertTrue(self.is_dict(inline_keyboard_button_markup))
        self.assertDictEqual(self.json_dict, inline_keyboard_button_markup)


if __name__ == '__main__':
    unittest.main()
