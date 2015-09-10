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

"""This module contains a object that represents Tests for Telegram Update"""

import os
import unittest
import sys
sys.path.append('.')

import telegram
from tests.base import BaseTest


class UpdateTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Update."""

    def setUp(self):
        self.update_id = 868573637
        self.message = {'message_id': 319,
                        'from': {'id': 12173560,
                                 'first_name': "Leandro",
                                 'last_name': "S.",
                                 'username': "leandrotoledo"},
                        'chat': {'id': 12173560,
                                 'first_name': "Leandro",
                                 'last_name': "S.",
                                 'username': "leandrotoledo"},
                        'date': 1441644592,
                        'text': "Update Test"}

        self.json_dict = {
            'update_id': self.update_id,
            'message': self.message
        }

    def test_update_de_json(self):
        """Test Update.de_json() method"""
        print('Testing Update.de_json()')

        update = telegram.Update.de_json(self.json_dict)

        self.assertEqual(update.update_id, self.update_id)
        self.assertTrue(isinstance(update.message, telegram.Message))

    def test_update_to_json(self):
        """Test Update.to_json() method"""
        print('Testing Update.to_json()')

        update = telegram.Update.de_json(self.json_dict)

        self.assertTrue(self.is_json(update.to_json()))

    def test_update_to_dict(self):
        """Test Update.to_dict() method"""
        print('Testing Update.to_dict()')

        update = telegram.Update.de_json(self.json_dict)

        self.assertTrue(self.is_dict(update.to_dict()))
        self.assertEqual(update['update_id'], self.update_id)
        self.assertTrue(isinstance(update['message'], telegram.Message))

if __name__ == '__main__':
    unittest.main()
