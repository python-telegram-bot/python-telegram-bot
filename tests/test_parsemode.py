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
"""This module contains an object that represents Tests for Telegram ParseMode"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ParseMode(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram ParseMode."""

    def setUp(self):
        self.markdown_text = "*bold* _italic_ [link](http://google.com)."
        self.html_text = '<b>bold</b> <i>italic</i> <a href="http://google.com">link</a>.'
        self.formatted_text_formatted = u'bold italic link.'

    def test_send_message_with_parse_mode_markdown(self):
        message = self._bot.sendMessage(
            chat_id=self._chat_id, text=self.markdown_text, parse_mode=telegram.ParseMode.MARKDOWN)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, self.formatted_text_formatted)

    def test_send_message_with_parse_mode_html(self):
        message = self._bot.sendMessage(
            chat_id=self._chat_id, text=self.html_text, parse_mode=telegram.ParseMode.HTML)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, self.formatted_text_formatted)


if __name__ == '__main__':
    unittest.main()
