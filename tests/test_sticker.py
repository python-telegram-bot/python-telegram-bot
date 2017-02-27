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
"""This module contains an object that represents Tests for Telegram Sticker"""

import sys
import unittest
import os

from flaky import flaky
from future.utils import PY2

sys.path.append('.')

import telegram
from tests.base import BaseTest, timeout


class StickerTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Sticker."""

    def setUp(self):
        self.sticker_file_id = 'CAADAQADHAADyIsGAAFZfq1bphjqlgI'
        self.width = 510
        self.height = 512
        self.thumb = {
            'width': 90,
            'height': 90,
            'file_id': 'BQADAQADoQADHyP1B0mzJMVyzcB0Ag',
            'file_size': 2364
        }
        self.emoji = telegram.Emoji.FLEXED_BICEPS
        self.file_size = 39518

        self.json_dict = {
            'file_id': self.sticker_file_id,
            'width': self.width,
            'height': self.height,
            'thumb': self.thumb,
            'emoji': self.emoji,
            'file_size': self.file_size
        }

    @flaky(3, 1)
    @timeout(10)
    def test_send_sticker_file(self):
        pass

    @flaky(3, 1)
    @timeout(10)
    def test_send_sticker_resend(self):
        message = self._bot.sendSticker(chat_id=self._chat_id, sticker=self.sticker_file_id)

        sticker = message.sticker

        self.assertEqual(sticker.file_id, self.sticker_file_id)
        self.assertEqual(sticker.width, self.width)
        self.assertEqual(sticker.height, self.height)
        self.assertTrue(isinstance(sticker.thumb, telegram.PhotoSize))
        if PY2:
            self.assertEqual(sticker.emoji, self.emoji.decode('utf-8'))
        else:
            self.assertEqual(sticker.emoji, self.emoji)
        # self.assertEqual(sticker.file_size, self.file_size)  # TODO

    def test_sticker_de_json(self):
        sticker = telegram.Sticker.de_json(self.json_dict, self._bot)

        self.assertEqual(sticker.file_id, self.sticker_file_id)
        self.assertEqual(sticker.width, self.width)
        self.assertEqual(sticker.height, self.height)
        self.assertTrue(isinstance(sticker.thumb, telegram.PhotoSize))
        self.assertEqual(sticker.emoji, self.emoji)
        self.assertEqual(sticker.file_size, self.file_size)

    def test_sticker_to_json(self):
        sticker = telegram.Sticker.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(sticker.to_json()))

    def test_sticker_to_dict(self):
        sticker = telegram.Sticker.de_json(self.json_dict, self._bot)

        self.assertEqual(sticker['file_id'], self.sticker_file_id)
        self.assertEqual(sticker['width'], self.width)
        self.assertEqual(sticker['height'], self.height)
        self.assertTrue(isinstance(sticker['thumb'], telegram.PhotoSize))
        self.assertEqual(sticker['emoji'], self.emoji)
        self.assertEqual(sticker['file_size'], self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_sticker_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['sticker'] = open(os.devnull, 'rb')

        self.assertRaises(
            telegram.TelegramError,
            lambda: self._bot.sendSticker(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_sticker_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['sticker'] = ''

        self.assertRaises(
            telegram.TelegramError,
            lambda: self._bot.sendSticker(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_sticker_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])

        self.assertRaises(
            TypeError,
            lambda: self._bot.sendSticker(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_reply_sticker(self):
        """Test for Message.reply_sticker"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_sticker(self.sticker_file_id)

        self.assertNotEqual(message.sticker.file_id, '')


if __name__ == '__main__':
    unittest.main()
