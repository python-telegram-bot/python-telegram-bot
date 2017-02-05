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
"""This module contains an object that represents Tests for Telegram
InlineQuery"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQuery."""

    def setUp(self):
        user = telegram.User(1, 'First name')
        location = telegram.Location(8.8, 53.1)

        self.id = 'id'
        self.from_user = user
        self.query = 'query text'
        self.offset = 'offset'
        self.location = location

        self.json_dict = {
            'id': self.id,
            'from': self.from_user.to_dict(),
            'query': self.query,
            'offset': self.offset,
            'location': self.location.to_dict()
        }

    def test_inlinequery_de_json(self):
        inlinequery = telegram.InlineQuery.de_json(self.json_dict, self._bot)

        self.assertEqual(inlinequery.id, self.id)
        self.assertDictEqual(inlinequery.from_user.to_dict(), self.from_user.to_dict())
        self.assertDictEqual(inlinequery.location.to_dict(), self.location.to_dict())
        self.assertEqual(inlinequery.query, self.query)
        self.assertEqual(inlinequery.offset, self.offset)

    def test_inlinequery_to_json(self):
        inlinequery = telegram.InlineQuery.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(inlinequery.to_json()))

    def test_inlinequery_to_dict(self):
        inlinequery = telegram.InlineQuery.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(inlinequery))
        self.assertDictEqual(inlinequery, self.json_dict)


if __name__ == '__main__':
    unittest.main()
