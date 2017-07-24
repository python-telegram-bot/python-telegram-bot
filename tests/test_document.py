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
"""This module contains an object that represents Tests for Telegram Document"""

import os
import unittest

from flaky import flaky

import telegram
from tests.base import BaseTest, timeout
from tests.bots import get_bot

class DocumentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Document."""

    @classmethod
    def setUpClass(cls):
        cls.caption = u'DocumentTest - Caption'
        cls.document_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.gif'

        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = telegram.Bot(bot_info['token'])

        document_file = open('tests/data/telegram.png', 'rb')
        document = cls._bot.send_document(cls._chat_id, document=document_file, timeout=10).document
        cls.document = document

        # Make sure file has been uploaded.
        # Simple assertions PY2 Only
        assert isinstance(cls.document, telegram.Document)
        assert isinstance(cls.document.file_id, str)
        assert cls.document.file_id is not ''

    def setUp(self):
        self.document_file = open('tests/data/telegram.png', 'rb')
        self.json_dict = {
            'file_id': self.document.file_id,
            'thumb': self.document.thumb.to_dict(),
            'file_name': self.document.file_name,
            'mime_type': self.document.mime_type,
            'file_size': self.document.file_size
        }

    def test_expected_values(self):
        self.assertEqual(self.document.file_size, 12948)
        self.assertEqual(self.document.mime_type, 'image/png')
        self.assertEqual(self.document.file_name, 'telegram.png')
        self.assertEqual(self.document.thumb.file_size, 2364)
        self.assertEqual(self.document.thumb.width, 90)
        self.assertEqual(self.document.thumb.height, 90)

    @flaky(3, 1)
    @timeout(10)
    def test_send_document_all_args(self):
        message = self._bot.sendDocument(self._chat_id, document=self.document_file, caption=self.caption,
                                         disable_notification=False)

        document = message.document

        self.assertIsInstance(document, telegram.Document)
        self.assertIsInstance(document.file_id, str)
        self.assertNotEqual(document.file_id, '')
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, self.document.file_name)
        self.assertEqual(document.mime_type, self.document.mime_type)
        self.assertEqual(document.file_size, self.document.file_size)
        self.assertEqual(document.thumb, self.document.thumb)
        self.assertEqual(message.caption, self.caption)

    @flaky(3, 1)
    @timeout(10)
    def test_get_and_download_document(self):
        new_file = self._bot.getFile(self.document.file_id)

        self.assertEqual(new_file.file_size, self.document.file_size)
        self.assertEqual(new_file.file_id, self.document.file_id)
        self.assertTrue(new_file.file_path.startswith('https://'))

        new_file.download('telegram.png')

        self.assertTrue(os.path.isfile('telegram.png'))

    @flaky(3, 1)
    @timeout(10)
    def test_send_document_png_file_with_custom_file_name(self):
        message = self._bot.sendDocument(
            self._chat_id, self.document_file, filename='telegram_custom.png')

        document = message.document

        self.assertEqual(document.file_name, 'telegram_custom.png')

    @flaky(3, 1)
    @timeout(10)
    def test_send_document_url_gif_file(self):
        message = self._bot.sendDocument(self._chat_id, self.document_file_url)

        document = message.document

        self.assertIsInstance(document, telegram.Document)
        self.assertIsInstance(document.file_id, str)
        self.assertNotEqual(document.file_id, '')
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, 'telegram.gif')
        self.assertEqual(document.mime_type, 'image/gif')
        self.assertEqual(document.file_size, 3878)

    @flaky(3, 1)
    @timeout(10)
    def test_send_document_resend(self):
        message = self._bot.sendDocument(chat_id=self._chat_id, document=self.document.file_id)

        document = message.document

        self.assertEqual(document, self.document)

    @flaky(3, 1)
    @timeout(10)
    def test_send_document_with_document(self):
        message = self._bot.send_document(document=self.document, chat_id=self._chat_id)
        document = message.document

        self.assertEqual(document, self.document)


    def test_document_de_json(self):
        document = telegram.Document.de_json(self.json_dict, self._bot)

        self.assertEqual(document, self.document)

    def test_document_to_json(self):
        self.assertTrue(self.is_json(self.document.to_json()))

    def test_document_to_dict(self):
        document = self.document.to_dict()

        self.assertTrue(self.is_dict(document))
        self.assertEqual(document['file_id'], self.document.file_id)
        self.assertEqual(document['file_name'], self.document.file_name)
        self.assertEqual(document['mime_type'], self.document.mime_type)
        self.assertEqual(document['file_size'], self.document.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_document_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['document'] = open(os.devnull, 'rb')

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendDocument(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_document_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['document'] = ''

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendDocument(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_document_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])

        with self.assertRaises(TypeError): self._bot.sendDocument(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_reply_document(self):
        """Test for Message.reply_document"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_document(self.document_file)

        document = message.document

        self.assertIsInstance(document, telegram.Document)
        self.assertIsInstance(document.file_id, str)
        self.assertNotEqual(document.file_id, '')
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))

    def test_equality(self):
        a = telegram.Document(self.document.file_id)
        b = telegram.Document(self.document.file_id)
        d = telegram.Document("")
        e = telegram.Voice(self.document.file_id, 0)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertIsNot(a, b)

        self.assertNotEqual(a, d)
        self.assertNotEqual(hash(a), hash(d))

        self.assertNotEqual(a, e)
        self.assertNotEqual(hash(a), hash(e))


if __name__ == '__main__':
    unittest.main()
