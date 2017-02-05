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
ChosenInlineResult"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ChosenInlineResultTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram ChosenInlineResult."""

    def setUp(self):
        user = telegram.User(1, 'First name')

        self.result_id = 'result id'
        self.from_user = user
        self.query = 'query text'

        self.json_dict = {
            'result_id': self.result_id,
            'from': self.from_user.to_dict(),
            'query': self.query
        }

    def test_choseninlineresult_de_json(self):
        result = telegram.ChosenInlineResult.de_json(self.json_dict, self._bot)

        self.assertEqual(result.result_id, self.result_id)
        self.assertDictEqual(result.from_user.to_dict(), self.from_user.to_dict())
        self.assertEqual(result.query, self.query)

    def test_choseninlineresult_to_json(self):
        result = telegram.ChosenInlineResult.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(result.to_json()))

    def test_choseninlineresult_to_dict(self):
        result = telegram.ChosenInlineResult.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(result))
        self.assertEqual(result['result_id'], self.result_id)
        self.assertEqual(result['from'], self.from_user.to_dict())
        self.assertEqual(result['query'], self.query)


if __name__ == '__main__':
    unittest.main()
