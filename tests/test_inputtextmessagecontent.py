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
"""This module contains an object that represents Tests for Telegram
InputTextMessageContent"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InputTextMessageContentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InputTextMessageContent."""

    def setUp(self):
        self.message_text = '*message text*'
        self.parse_mode = telegram.ParseMode.MARKDOWN
        self.disable_web_page_preview = True

        self.json_dict = {
            'parse_mode': self.parse_mode,
            'message_text': self.message_text,
            'disable_web_page_preview': self.disable_web_page_preview,
        }

    def test_itmc_de_json(self):
        itmc = telegram.InputTextMessageContent.de_json(self.json_dict, self._bot)

        self.assertEqual(itmc.parse_mode, self.parse_mode)
        self.assertEqual(itmc.message_text, self.message_text)
        self.assertEqual(itmc.disable_web_page_preview, self.disable_web_page_preview)

    def test_itmc_de_json_factory(self):
        itmc = telegram.InputMessageContent.de_json(self.json_dict, self._bot)

        self.assertTrue(isinstance(itmc, telegram.InputTextMessageContent))

    def test_itmc_de_json_factory_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['message_text'])

        itmc = telegram.InputMessageContent.de_json(json_dict, self._bot)

        self.assertFalse(itmc)

    def test_itmc_to_json(self):
        itmc = telegram.InputTextMessageContent.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(itmc.to_json()))

    def test_itmc_to_dict(self):
        itmc = telegram.InputTextMessageContent.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(itmc))
        self.assertDictEqual(self.json_dict, itmc)


if __name__ == '__main__':
    unittest.main()
