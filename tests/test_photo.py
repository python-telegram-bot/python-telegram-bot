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
"""This module contains an object that represents Tests for Telegram Photo"""

import sys
import unittest
import os

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest, timeout


class PhotoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Photo."""

    def setUp(self):
        self.photo_file = open('tests/data/telegram.jpg', 'rb')
        self.photo_file_id = 'AgADAQADgEsyGx8j9QfmDMmwkPBrFcKRzy8ABHW8ul9nW7FoNHYBAAEC'
        self.photo_file_url = 'https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/tests/data/telegram.jpg'
        self.width = 300
        self.height = 300
        self.thumb = {
            'width': 90,
            'height': 90,
            'file_id': 'AgADAQADgEsyGx8j9QeYW9oDz2mKRsKRzy8ABD64nkFkjujeNXYBAAEC',
            'file_size': 1478
        }
        self.file_size = 10209

        # caption is part of sendPhoto method but not Photo object
        self.caption = u'PhotoTest - Caption'

        self.json_dict = {
            'file_id': self.photo_file_id,
            'width': self.width,
            'height': self.height,
            'file_size': self.file_size
        }

    @flaky(3, 1)
    @timeout(10)
    def test_sendphotoo_all_args(self):
        message = self._bot.sendPhoto(self._chat_id, self.photo_file, caption=self.caption)

        thumb, photo = message.photo

        self.assertTrue(isinstance(thumb.file_id, str))
        self.assertNotEqual(thumb.file_id, '')
        self.assertTrue(isinstance(thumb, telegram.PhotoSize))
        self.assertEqual(thumb.width, self.thumb['width'])
        self.assertEqual(thumb.height, self.thumb['height'])
        self.assertEqual(thumb.file_size, self.thumb['file_size'])

        self.assertTrue(isinstance(photo.file_id, str))
        self.assertNotEqual(photo.file_id, '')
        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertEqual(photo.width, self.width)
        self.assertEqual(photo.height, self.height)
        self.assertEqual(photo.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_jpg_file(self):
        message = self._bot.sendPhoto(self._chat_id, self.photo_file)

        thumb, photo = message.photo

        self.assertTrue(isinstance(thumb.file_id, str))
        self.assertNotEqual(thumb.file_id, '')
        self.assertTrue(isinstance(thumb, telegram.PhotoSize))
        self.assertEqual(thumb.width, self.thumb['width'])
        self.assertEqual(thumb.height, self.thumb['height'])
        self.assertEqual(thumb.file_size, self.thumb['file_size'])

        self.assertTrue(isinstance(photo.file_id, str))
        self.assertNotEqual(photo.file_id, '')
        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertEqual(photo.width, self.width)
        self.assertEqual(photo.height, self.height)
        self.assertEqual(photo.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_url_jpg_file(self):
        message = self._bot.sendPhoto(self._chat_id, self.photo_file_url)

        thumb, photo = message.photo

        self.assertTrue(isinstance(thumb.file_id, str))
        self.assertNotEqual(thumb.file_id, '')
        self.assertTrue(isinstance(thumb, telegram.PhotoSize))
        self.assertEqual(thumb.width, self.thumb['width'])
        self.assertEqual(thumb.height, self.thumb['height'])
        self.assertEqual(thumb.file_size, self.thumb['file_size'])

        self.assertTrue(isinstance(photo.file_id, str))
        self.assertNotEqual(photo.file_id, '')
        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertEqual(photo.width, self.width)
        self.assertEqual(photo.height, self.height)
        self.assertEqual(photo.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_resend(self):
        message = self._bot.sendPhoto(chat_id=self._chat_id, photo=self.photo_file_id)

        thumb, photo = message.photo

        self.assertEqual(thumb.file_id, self.thumb['file_id'])
        self.assertTrue(isinstance(thumb, telegram.PhotoSize))
        self.assertEqual(thumb.width, self.thumb['width'])
        self.assertEqual(thumb.height, self.thumb['height'])

        self.assertEqual(photo.file_id, self.photo_file_id)
        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertEqual(photo.width, self.width)
        self.assertEqual(photo.height, self.height)

    def test_photo_de_json(self):
        photo = telegram.PhotoSize.de_json(self.json_dict, self._bot)

        self.assertEqual(photo.file_id, self.photo_file_id)
        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertEqual(photo.width, self.width)
        self.assertEqual(photo.height, self.height)
        self.assertEqual(photo.file_size, self.file_size)

    def test_photo_to_json(self):
        photo = telegram.PhotoSize.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(photo.to_json()))

    def test_photo_to_dict(self):
        photo = telegram.PhotoSize.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(photo.to_dict()))
        self.assertEqual(photo['file_id'], self.photo_file_id)
        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertEqual(photo['width'], self.width)
        self.assertEqual(photo['height'], self.height)
        self.assertEqual(photo['file_size'], self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_photo_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['photo'] = open(os.devnull, 'rb')

        self.assertRaises(
            telegram.TelegramError,
            lambda: self._bot.sendPhoto(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_photo_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['photo'] = ''

        self.assertRaises(
            telegram.TelegramError,
            lambda: self._bot.sendPhoto(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_photo_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        del (json_dict['width'])
        del (json_dict['height'])

        self.assertRaises(
            TypeError,
            lambda: self._bot.sendPhoto(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_reply_photo(self):
        """Test for Message.reply_photo"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_photo(self.photo_file)

        self.assertNotEqual(message.photo[0].file_id, '')


if __name__ == '__main__':
    unittest.main()
