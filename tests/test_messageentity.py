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
"""This module contains an object that represents Tests for Telegram
MessageEntity"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class MessageEntityTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram MessageEntity."""

    def setUp(self):
        self.type = 'type'
        self.offset = 1
        self.length = 2
        self.url = 'url'

        self.json_dict = {
            'type': self.type,
            'offset': self.offset,
            'length': self.length,
            'url': self.url
        }

    def test_messageentity_de_json(self):
        entity = telegram.MessageEntity.de_json(self.json_dict, self._bot)

        self.assertEqual(entity.type, self.type)
        self.assertEqual(entity.offset, self.offset)
        self.assertEqual(entity.length, self.length)
        self.assertEqual(entity.url, self.url)

    def test_messageentity_to_json(self):
        entity = telegram.MessageEntity.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(entity.to_json()))

    def test_messageentity_to_dict(self):
        entity = telegram.MessageEntity.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(entity))
        self.assertDictEqual(self.json_dict, entity)


if __name__ == '__main__':
    unittest.main()
