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
"""This module contains an object that represents Tests for Telegram User"""

import unittest
import sys

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest


class UserTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram User."""

    def setUp(self):
        self._id = 12173560
        self.first_name = "Leandro"
        self.last_name = "S."
        self.username = "leandrotoledo"
        self.language_code = "pt-BR"
        self.type = "private"

        self.json_dict = {
            'id': self._id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'language_code': self.language_code,
            'type': self.type
        }

    def test_user_de_json(self):
        user = telegram.User.de_json(self.json_dict, self._bot)

        self.assertEqual(user.id, self._id)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.language_code, self.language_code)
        self.assertEqual(user.type, self.type)

        self.assertEqual(user.name, '@leandrotoledo')

    def test_user_de_json_without_username(self):
        json_dict = self.json_dict

        del (json_dict['username'])

        user = telegram.User.de_json(self.json_dict, self._bot)

        self.assertEqual(user.id, self._id)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)
        self.assertEqual(user.type, self.type)

        self.assertEqual(user.name, '%s %s' % (self.first_name, self.last_name))

    def test_user_de_json_without_username_and_lastname(self):
        json_dict = self.json_dict

        del (json_dict['username'])
        del (json_dict['last_name'])

        user = telegram.User.de_json(self.json_dict, self._bot)

        self.assertEqual(user.id, self._id)
        self.assertEqual(user.first_name, self.first_name)

        self.assertEqual(user.name, self.first_name)

    def test_user_to_json(self):
        user = telegram.User.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(user.to_json()))

    def test_user_to_dict(self):
        user = telegram.User.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(user.to_dict()))
        self.assertEqual(user['id'], self._id)
        self.assertEqual(user['first_name'], self.first_name)
        self.assertEqual(user['last_name'], self.last_name)
        self.assertEqual(user['username'], self.username)
        self.assertEqual(user['language_code'], self.language_code)
        self.assertEqual(user['type'], self.type)

    @flaky(3, 1)
    def test_get_profile_photos(self):
        """Test for User.get_profile_photos"""
        self.json_dict['id'] = self._chat_id
        user = telegram.User.de_json(self.json_dict, self._bot)
        user.bot = self._bot

        result = user.get_profile_photos()

        self.assertNotEquals(result, None)

    def test_equality(self):
        a = telegram.User(self._id, self.first_name, self.last_name)
        b = telegram.User(self._id, self.first_name, self.last_name)
        c = telegram.User(self._id, self.first_name)
        d = telegram.User(0, self.first_name, self.last_name)
        e = telegram.Update(self._id)

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
