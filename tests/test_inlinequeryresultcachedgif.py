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
InlineQueryResultCachedGif"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultCachedGifTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultCachedGif."""

    def setUp(self):
        self.id = 'id'
        self.type = 'gif'
        self.gif_file_id = 'gif file id'
        self.title = 'title'
        self.caption = 'caption'
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])

        self.json_dict = {
            'type': self.type,
            'id': self.id,
            'gif_file_id': self.gif_file_id,
            'title': self.title,
            'caption': self.caption,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_gif_de_json(self):
        gif = telegram.InlineQueryResultCachedGif.de_json(self.json_dict, self._bot)

        self.assertEqual(gif.type, self.type)
        self.assertEqual(gif.id, self.id)
        self.assertEqual(gif.gif_file_id, self.gif_file_id)
        self.assertEqual(gif.title, self.title)
        self.assertEqual(gif.caption, self.caption)
        self.assertDictEqual(gif.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(gif.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_gif_to_json(self):
        gif = telegram.InlineQueryResultCachedGif.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(gif.to_json()))

    def test_gif_to_dict(self):
        gif = telegram.InlineQueryResultCachedGif.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(gif))
        self.assertDictEqual(self.json_dict, gif)


if __name__ == '__main__':
    unittest.main()
