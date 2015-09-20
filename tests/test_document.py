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

"""This module contains a object that represents Tests for Telegram Document"""

import os
import unittest
import sys
sys.path.append('.')

import telegram
from tests.base import BaseTest


class DocumentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Document."""

    def setUp(self):
        self.document_file = open('tests/data/telegram.png', 'rb')
        self.document_file_id = 'BQADAQADpAADHyP1B04ipZxJTe2BAg'
        self.document_file_url = 'http://dummyimage.com/600x400/000/fff.gif&text=telegram'
        self.thumb = {'width': 90,
                      'height': 90,
                      'file_id': 'BQADAQADoQADHyP1B0mzJMVyzcB0Ag',
                      'file_size': 2364}
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

    def test_send_document_png_file(self):
        """Test telegram.Bot sendDocument method"""
        print('Testing bot.sendDocument - PNG File')

        message = self._bot.sendDocument(self._chat_id,
                                         self.document_file)

        document = message.document

        self.assertTrue(isinstance(document.file_id, str))
        self.assertNotEqual(document.file_id, '')
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, self.file_name)
        self.assertEqual(document.mime_type, self.mime_type)
        self.assertEqual(document.file_size, self.file_size)

    def test_send_document_png_file_with_custom_file_name(self):
        """Test telegram.Bot sendDocument method"""
        print('Testing bot.sendDocument - PNG File with custom filename')

        message = self._bot.sendDocument(self._chat_id,
                                         self.document_file,
                                         filename='telegram_custom.png')

        document = message.document

        self.assertTrue(isinstance(document.file_id, str))
        self.assertNotEqual(document.file_id, '')
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, 'telegram_custom.png')
        self.assertEqual(document.mime_type, self.mime_type)
        self.assertEqual(document.file_size, self.file_size)

    def test_send_document_url_gif_file(self):
        """Test telegram.Bot sendDocument method"""
        print('Testing bot.sendDocument - GIF File by URL')

        message = self._bot.sendDocument(self._chat_id,
                                         self.document_file_url)

        document = message.document

        self.assertTrue(isinstance(document.file_id, str))
        self.assertNotEqual(document.file_id, '')
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, 'image.gif')
        self.assertEqual(document.mime_type, 'image/gif')
        self.assertEqual(document.file_size, 3878)

    def test_send_document_resend(self):
        """Test telegram.Bot sendDocument method"""
        print('Testing bot.sendDocument - Resend by file_id')

        message = self._bot.sendDocument(chat_id=self._chat_id,
                                         document=self.document_file_id)

        document = message.document

        self.assertEqual(document.file_id, self.document_file_id)
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, self.file_name)
        self.assertEqual(document.mime_type, self.mime_type)

    def test_document_de_json(self):
        """Test Document.de_json() method"""
        print('Testing Document.de_json()')

        document = telegram.Document.de_json(self.json_dict)

        self.assertEqual(document.file_id, self.document_file_id)
        self.assertTrue(isinstance(document.thumb, telegram.PhotoSize))
        self.assertEqual(document.file_name, self.file_name)
        self.assertEqual(document.mime_type, self.mime_type)
        self.assertEqual(document.file_size, self.file_size)

    def test_document_to_json(self):
        """Test Document.to_json() method"""
        print('Testing Document.to_json()')

        document = telegram.Document.de_json(self.json_dict)

        self.assertTrue(self.is_json(document.to_json()))

    def test_document_to_dict(self):
        """Test Document.to_dict() method"""
        print('Testing Document.to_dict()')

        document = telegram.Document.de_json(self.json_dict)

        self.assertTrue(self.is_dict(document.to_dict()))
        self.assertEqual(document['file_id'], self.document_file_id)
        self.assertTrue(isinstance(document['thumb'], telegram.PhotoSize))
        self.assertEqual(document['file_name'], self.file_name)
        self.assertEqual(document['mime_type'], self.mime_type)
        self.assertEqual(document['file_size'], self.file_size)

    def test_error_send_document_empty_file(self):
        print('Testing bot.sendDocument - Null file')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['document'] = open(os.devnull, 'rb')

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendDocument(chat_id=self._chat_id,
                                                         **json_dict))

    def test_error_send_document_empty_file_id(self):
        print('Testing bot.sendDocument - Empty file_id')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['document'] = ''

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendDocument(chat_id=self._chat_id,
                                                         **json_dict))

    def test_error_document_without_required_args(self):
        print('Testing bot.sendDocument - Without required arguments')

        json_dict = self.json_dict

        del(json_dict['file_id'])

        self.assertRaises(TypeError,
                          lambda: self._bot.sendDocument(chat_id=self._chat_id,
                                                         **json_dict))

if __name__ == '__main__':
    unittest.main()
