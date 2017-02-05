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
"""This module contains an object that represents Tests for Telegram Document"""

import sys
import unittest
import os

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest, timeout


class DocumentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Document."""

    def setUp(self):
        self.document_file = open('tests/data/telegram.png', 'rb')
        self.document_file_id = 'BQADAQADpAADHyP1B04ipZxJTe2BAg'
        self.document_file_url = 'https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/tests/data/telegram.gif'
        self.thumb = {
            'width': 90,
            'height': 90,
            'file_id': 'BQADAQADoQADHyP1B0mzJMVyzcB0Ag',
            'file_size': 2364
        }
        self.file_name = 'telegram.png'
        self.mime_type = 'image/png'
        self.file_size = 12948

        self.json_dict = {
            'file_id': self.document_file_id,
            'thumb': self.thumb,
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }

    @flaky(3, 1)
    @timeout(10)
    def test_send_document_png_file(self):
        message = self._bot.sendDocument(self._chat_id, self.document_file, caption='caption text')

        document = message.document

        self.assertTrue(isinstance(document.file_id, str))
        self.assertNotEqual(document.file_id, '')
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, self.file_name)
        self.assertEqual(document.mime_type, self.mime_type)
        self.assertEqual(document.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_document_png_file_with_custom_file_name(self):
        message = self._bot.sendDocument(
            self._chat_id, self.document_file, filename='telegram_custom.png')

        document = message.document

        self.assertTrue(isinstance(document.file_id, str))
        self.assertNotEqual(document.file_id, '')
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, 'telegram_custom.png')
        self.assertEqual(document.mime_type, self.mime_type)
        self.assertEqual(document.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_document_url_gif_file(self):
        message = self._bot.sendDocument(self._chat_id, self.document_file_url)

        document = message.document

        self.assertTrue(isinstance(document.file_id, str))
        self.assertNotEqual(document.file_id, '')
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, 'telegram.gif')
        self.assertEqual(document.mime_type, 'image/gif')
        self.assertEqual(document.file_size, 3878)

    @flaky(3, 1)
    @timeout(10)
    def test_send_document_resend(self):
        message = self._bot.sendDocument(chat_id=self._chat_id, document=self.document_file_id)

        document = message.document

        self.assertEqual(document.file_id, self.document_file_id)
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, self.file_name)
        self.assertEqual(document.mime_type, self.mime_type)

    def test_document_de_json(self):
        document = telegram.Document.de_json(self.json_dict, self._bot)

        self.assertEqual(document.file_id, self.document_file_id)
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, self.file_name)
        self.assertEqual(document.mime_type, self.mime_type)
        self.assertEqual(document.file_size, self.file_size)

    def test_document_to_json(self):
        document = telegram.Document.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(document.to_json()))

    def test_document_to_dict(self):
        document = telegram.Document.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(document.to_dict()))
        self.assertEqual(document['file_id'], self.document_file_id)
        self.assertTrue(isinstance(document['thumb'], telegram.PhotoSize))
        self.assertEqual(document['file_name'], self.file_name)
        self.assertEqual(document['mime_type'], self.mime_type)
        self.assertEqual(document['file_size'], self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_document_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['document'] = open(os.devnull, 'rb')

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendDocument(chat_id=self._chat_id,
                                                         **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_document_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['document'] = ''

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendDocument(chat_id=self._chat_id,
                                                         **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_document_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])

        self.assertRaises(TypeError,
                          lambda: self._bot.sendDocument(chat_id=self._chat_id,
                                                         **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_reply_document(self):
        """Test for Message.reply_document"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_document(self.document_file)

        self.assertNotEqual(message.document.file_id, '')


if __name__ == '__main__':
    unittest.main()
