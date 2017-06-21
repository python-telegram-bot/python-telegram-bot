#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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

import os
import unittest
from io import BytesIO

from flaky import flaky

import telegram
from tests.base import BaseTest, timeout
from tests.bots import get_bot


class PhotoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Photo."""

    @classmethod
    def setUpClass(cls):
        cls.caption = u'PhotoTest - Caption'
        cls.photo_file_url = 'https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/tests/data/telegram.jpg'

        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = telegram.Bot(bot_info['token'])

        photo_file = open('tests/data/telegram.jpg', 'rb')
        photo = cls._bot.send_photo(cls._chat_id, photo=photo_file, timeout=10).photo
        cls.thumb, cls.photo = photo

        # Make sure file has been uploaded.
        # Simple assertions PY2 Only
        assert isinstance(cls.photo, telegram.PhotoSize)
        assert isinstance(cls.thumb, telegram.PhotoSize)
        assert isinstance(cls.photo.file_id, str)
        assert isinstance(cls.thumb.file_id, str)
        assert cls.photo.file_id is not ''
        assert cls.thumb.file_id is not ''

    def setUp(self):
        self.photo_file = open('tests/data/telegram.jpg', 'rb')
        self.photo_bytes_jpg_no_standard = 'tests/data/telegram_no_standard_header.jpg'
        self.json_dict = {
            'file_id': self.photo.file_id,
            'width': self.photo.width,
            'height': self.photo.height,
            'file_size': self.photo.file_size
        }

    def test_expected_values(self):
        self.assertEqual(self.photo.width, 300)
        self.assertEqual(self.photo.height, 300)
        self.assertEqual(self.photo.file_size, 10209)
        self.assertEqual(self.thumb.width, 90)
        self.assertEqual(self.thumb.height, 90)
        self.assertEqual(self.thumb.file_size, 1478)

    @flaky(3, 1)
    @timeout(10)
    def test_sendphotoo_all_args(self):
        message = self._bot.sendPhoto(self._chat_id, self.photo_file, caption=self.caption, disable_notification=False)
        thumb, photo = message.photo

        self.assertTrue(isinstance(thumb, telegram.PhotoSize))
        self.assertTrue(isinstance(thumb.file_id, str))
        self.assertNotEqual(thumb.file_id, '')
        self.assertEqual(thumb.width, self.thumb.width)
        self.assertEqual(thumb.height, self.thumb.height)
        self.assertEqual(thumb.file_size, self.thumb.file_size)

        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertTrue(isinstance(photo.file_id, str))
        self.assertNotEqual(photo.file_id, '')
        self.assertEqual(photo.width, self.photo.width)
        self.assertEqual(photo.height, self.photo.height)
        self.assertEqual(photo.file_size, self.photo.file_size)

        self.assertEqual(message.caption, self.caption)

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_url_jpg_file(self):
        message = self._bot.sendPhoto(self._chat_id, photo=self.photo_file_url)

        thumb, photo = message.photo

        self.assertTrue(isinstance(thumb, telegram.PhotoSize))
        self.assertTrue(isinstance(thumb.file_id, str))
        self.assertNotEqual(thumb.file_id, '')
        self.assertEqual(thumb.width, self.thumb.width)
        self.assertEqual(thumb.height, self.thumb.height)
        self.assertEqual(thumb.file_size, self.thumb.file_size)

        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertTrue(isinstance(photo.file_id, str))
        self.assertNotEqual(photo.file_id, '')
        self.assertEqual(photo.width, self.photo.width)
        self.assertEqual(photo.height, self.photo.height)
        self.assertEqual(photo.file_size, self.photo.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_bytesio_jpg_file(self):
        from telegram.inputfile import InputFile
        # raw image bytes
        raw_bytes = BytesIO(open(self.photo_bytes_jpg_no_standard, 'rb').read())
        inputfile = InputFile({"photo": raw_bytes})
        self.assertEqual(inputfile.mimetype, 'application/octet-stream')

        # raw image bytes with name info
        raw_bytes = BytesIO(open(self.photo_bytes_jpg_no_standard, 'rb').read())
        raw_bytes.name = self.photo_bytes_jpg_no_standard
        inputfile = InputFile({"photo": raw_bytes})
        self.assertEqual(inputfile.mimetype, 'image/jpeg')

        # send raw photo
        raw_bytes = BytesIO(open(self.photo_bytes_jpg_no_standard, 'rb').read())
        message = self._bot.sendPhoto(self._chat_id, photo=raw_bytes)
        photo = message.photo[-1]
        self.assertTrue(isinstance(photo.file_id, str))
        self.assertNotEqual(photo.file_id, '')
        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertEqual(photo.width, 1920)
        self.assertEqual(photo.height, 1080)
        self.assertEqual(photo.file_size, 30907)

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_resend(self):
        message = self._bot.sendPhoto(chat_id=self._chat_id, photo=self.photo.file_id)

        thumb, photo = message.photo

        self.assertTrue(isinstance(thumb, telegram.PhotoSize))
        self.assertEqual(thumb.file_id, self.thumb.file_id)
        self.assertEqual(thumb.width, self.thumb.width)
        self.assertEqual(thumb.height, self.thumb.height)
        self.assertEqual(thumb.file_size, self.thumb.file_size)

        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertEqual(photo.file_id, self.photo.file_id)
        self.assertEqual(photo.width, self.photo.width)
        self.assertEqual(photo.height, self.photo.height)
        self.assertEqual(photo.file_size, self.photo.file_size)

    def test_photo_de_json(self):
        photo = telegram.PhotoSize.de_json(self.json_dict, self._bot)

        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertEqual(photo.file_id, self.photo.file_id)
        self.assertEqual(photo.width, self.photo.width)
        self.assertEqual(photo.height, self.photo.height)
        self.assertEqual(photo.file_size, self.photo.file_size)

    def test_photo_to_json(self):
        photo = telegram.PhotoSize.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(photo.to_json()))

    def test_photo_to_dict(self):
        photo = telegram.PhotoSize.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(photo))
        self.assertEqual(photo['file_id'], self.photo.file_id)
        self.assertEqual(photo['width'], self.photo.width)
        self.assertEqual(photo['height'], self.photo.height)
        self.assertEqual(photo['file_size'], self.photo.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_photo_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['photo'] = open(os.devnull, 'rb')

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendPhoto(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_photo_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['photo'] = ''

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendPhoto(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_photo_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        del (json_dict['width'])
        del (json_dict['height'])

        with self.assertRaises(TypeError):
            self._bot.sendPhoto(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_reply_photo(self):
        """Test for Message.reply_photo"""
        message = self._bot.sendMessage(self._chat_id, '.')
        thumb, photo = message.reply_photo(self.photo_file).photo

        self.assertTrue(isinstance(thumb, telegram.PhotoSize))
        self.assertTrue(isinstance(thumb.file_id, str))
        self.assertNotEqual(thumb.file_id, '')

        self.assertTrue(isinstance(photo, telegram.PhotoSize))
        self.assertTrue(isinstance(photo.file_id, str))
        self.assertNotEqual(photo.file_id, '')

    def test_equality(self):
        a = telegram.PhotoSize(self.photo.file_id, self.photo.width, self.photo.height)
        b = telegram.PhotoSize(self.photo.file_id, self.photo.width, self.photo.height)
        c = telegram.PhotoSize(self.photo.file_id, 0, 0)
        d = telegram.PhotoSize("", self.photo.width, self.photo.height)
        e = telegram.Sticker(self.photo.file_id, self.photo.width, self.photo.height)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertIsNot(a, b)

        self.assertEqual(a, c)
        self.assertEqual(hash(a), hash(c))

        self.assertNotEqual(a, d)
        self.assertNotEqual(hash(a), hash(d))

        self.assertNotEqual(a, e)
        self.assertNotEqual(hash(a), hash(e))


if __name__ == '__main__':
    unittest.main()
