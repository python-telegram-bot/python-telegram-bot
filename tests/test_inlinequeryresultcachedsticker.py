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
InlineQueryResultCachedSticker"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultCachedStickerTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram
    InlineQueryResultCachedSticker."""

    def setUp(self):
        self.id = 'id'
        self.type = 'sticker'
        self.sticker_file_id = 'sticker file id'
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])

        self.json_dict = {
            'type': self.type,
            'id': self.id,
            'sticker_file_id': self.sticker_file_id,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_sticker_de_json(self):
        sticker = telegram.InlineQueryResultCachedSticker.de_json(self.json_dict, self._bot)

        self.assertEqual(sticker.type, self.type)
        self.assertEqual(sticker.id, self.id)
        self.assertEqual(sticker.sticker_file_id, self.sticker_file_id)
        self.assertDictEqual(sticker.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(sticker.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_sticker_to_json(self):
        sticker = telegram.InlineQueryResultCachedSticker.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(sticker.to_json()))

    def test_sticker_to_dict(self):
        sticker = telegram.InlineQueryResultCachedSticker.de_json(self.json_dict,
                                                                  self._bot).to_dict()

        self.assertTrue(self.is_dict(sticker))
        self.assertDictEqual(self.json_dict, sticker)


if __name__ == '__main__':
    unittest.main()
