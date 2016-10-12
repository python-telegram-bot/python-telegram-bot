#!/usr/bin/env python
# encoding: utf-8
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
"""This module contains a object that represents Tests for Telegram Message"""

import sys
import unittest

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest


class MessageTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram MessageTest."""

    def test_parse_entity(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = telegram.MessageEntity(type=telegram.MessageEntity.URL, offset=13, length=17)
        message = telegram.Message(
            message_id=1, from_user=None, date=None, chat=None, text=text, entities=[entity])
        self.assertEqual(message.parse_entity(entity), 'http://google.com')

    def test_parse_entities(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = telegram.MessageEntity(type=telegram.MessageEntity.URL, offset=13, length=17)
        entity_2 = telegram.MessageEntity(type=telegram.MessageEntity.BOLD, offset=13, length=1)
        message = telegram.Message(
            message_id=1,
            from_user=None,
            date=None,
            chat=None,
            text=text,
            entities=[entity_2, entity])
        self.assertDictEqual(
            message.parse_entities(telegram.MessageEntity.URL), {entity: 'http://google.com'})
        self.assertDictEqual(message.parse_entities(),
                             {entity: 'http://google.com',
                              entity_2: 'h'})

    @flaky(3, 1)
    def test_reply_text(self):
        """Test for Message.reply_text"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_text('Testing class method')

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, 'Testing class method')

    @flaky(3, 1)
    def test_forward(self):
        """Test for Message.forward"""
        message = self._bot.sendMessage(self._chat_id, 'Testing class method')
        message = message.forward(self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, 'Testing class method')


if __name__ == '__main__':
    unittest.main()
