#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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

"""This module contains a object that represents Tests for Telegram Sticker"""

import os
import unittest
import sys
sys.path.append('.')

import telegram
from tests.base import BaseTest


class StickerTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Sticker."""

    def setUp(self):
        self.sticker_file_id = 'BQADAQADHAADyIsGAAFZfq1bphjqlgI'
        self.width = 510
        self.height = 512
        self.thumb = {'width': 90,
                      'height': 90,
                      'file_id': 'BQADAQADoQADHyP1B0mzJMVyzcB0Ag',
                      'file_size': 2364}
        self.file_size = 39518

        self.json_dict = {
            'file_id': self.sticker_file_id,
            'width': self.width,
            'height': self.height,
            'thumb': self.thumb,
            'file_size': self.file_size
        }

    def test_send_sticker_file(self):
        pass

    def test_send_sticker_resend(self):
        """Test telegram.Bot sendSticker method"""
        print('Testing bot.sendSticker - Resend by file_id')

        message = self._bot.sendSticker(chat_id=self._chat_id,
                                         sticker=self.sticker_file_id)

        sticker = message.sticker

        self.assertEqual(sticker.file_id, self.sticker_file_id)
        self.assertEqual(sticker.width, self.width)
        self.assertEqual(sticker.height, self.height)
        self.assertTrue(isinstance(sticker.thumb, telegram.PhotoSize))
        self.assertEqual(sticker.file_size, self.file_size)

    def test_sticker_de_json(self):
        """Test Sticker.de_json() method"""
        print('Testing Sticker.de_json()')

        sticker = telegram.Sticker.de_json(self.json_dict)

        self.assertEqual(sticker.file_id, self.sticker_file_id)
        self.assertEqual(sticker.width, self.width)
        self.assertEqual(sticker.height, self.height)
        self.assertTrue(isinstance(sticker.thumb, telegram.PhotoSize))
        self.assertEqual(sticker.file_size, self.file_size)

    def test_sticker_to_json(self):
        """Test Sticker.to_json() method"""
        print('Testing Sticker.to_json()')

        sticker = telegram.Sticker.de_json(self.json_dict)

        self.assertTrue(self.is_json(sticker.to_json()))

    def test_sticker_to_dict(self):
        """Test Sticker.to_dict() method"""
        print('Testing Sticker.to_dict()')

        sticker = telegram.Sticker.de_json(self.json_dict)

        self.assertEqual(sticker['file_id'], self.sticker_file_id)
        self.assertEqual(sticker['width'], self.width)
        self.assertEqual(sticker['height'], self.height)
        self.assertTrue(isinstance(sticker['thumb'], telegram.PhotoSize))
        self.assertEqual(sticker['file_size'], self.file_size)

    def test_error_send_sticker_empty_file(self):
        print('Testing bot.sendSticker - Null file')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['sticker'] = open(os.devnull, 'rb')

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendSticker(chat_id=self._chat_id,
                                                        **json_dict))

    def test_error_send_sticker_empty_file_id(self):
        print('Testing bot.sendSticker - Empty file_id')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['sticker'] = ''

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendSticker(chat_id=self._chat_id,
                                                         **json_dict))

    def test_error_sticker_without_required_args(self):
        print('Testing bot.sendSticker - Without required arguments')

        json_dict = self.json_dict

        del(json_dict['file_id'])

        self.assertRaises(TypeError,
                          lambda: self._bot.sendSticker(chat_id=self._chat_id,
                                                         **json_dict))

if __name__ == '__main__':
    unittest.main()
