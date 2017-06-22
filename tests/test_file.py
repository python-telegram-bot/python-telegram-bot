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
"""This module contains an object that represents Tests for Telegram File"""

import sys
import unittest
import os

sys.path.append('.')

import telegram
from tests.base import BaseTest


class FileTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram File."""

    def setUp(self):
        self.json_dict = {
            'file_id': "NOTVALIDDONTMATTER",
            'file_path':
            'https://api.telegram.org/file/bot133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0/document/file_3',
            'file_size': 28232
        }

    def test_file_de_json(self):
        new_file = telegram.File.de_json(self.json_dict, self._bot)

        self.assertEqual(new_file.file_id, self.json_dict['file_id'])
        self.assertEqual(new_file.file_path, self.json_dict['file_path'])
        self.assertEqual(new_file.file_size, self.json_dict['file_size'])

    def test_file_to_json(self):
        new_file = telegram.File.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(new_file.to_json()))

    def test_file_to_dict(self):
        new_file = telegram.File.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(new_file))
        self.assertEqual(new_file['file_id'], self.json_dict['file_id'])
        self.assertEqual(new_file['file_path'], self.json_dict['file_path'])
        self.assertEqual(new_file['file_size'], self.json_dict['file_size'])

    def test_error_get_empty_file_id(self):
        json_dict = self.json_dict
        json_dict['file_id'] = ''
        del (json_dict['file_path'])
        del (json_dict['file_size'])

        with self.assertRaises(telegram.TelegramError):
            self._bot.getFile(**json_dict)

    def test_error_file_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        del (json_dict['file_path'])
        del (json_dict['file_size'])

        with self.assertRaises(TypeError):
            self._bot.getFile(**json_dict)


    def test_equality(self):
        a = telegram.File("DOESNTMATTER", self._bot)
        b = telegram.File("DOESNTMATTER", self._bot)
        c = telegram.File("DOESNTMATTER", None)
        d = telegram.File("DOESNTMATTER2", self._bot)
        e = telegram.Voice("DOESNTMATTER", 0)

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
