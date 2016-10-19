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
InlineQueryResultLocation"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultLocationTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultLocation."""

    def setUp(self):
        self.id = 'id'
        self.type = 'location'
        self.latitude = 'latitude'
        self.longitude = 'longitude'
        self.title = 'title'
        self.thumb_url = 'thumb url'
        self.thumb_width = 10
        self.thumb_height = 15
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])
        self.json_dict = {
            'id': self.id,
            'type': self.type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'title': self.title,
            'thumb_url': self.thumb_url,
            'thumb_width': self.thumb_width,
            'thumb_height': self.thumb_height,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_location_de_json(self):
        location = telegram.InlineQueryResultLocation.de_json(self.json_dict, self._bot)

        self.assertEqual(location.id, self.id)
        self.assertEqual(location.type, self.type)
        self.assertEqual(location.latitude, self.latitude)
        self.assertEqual(location.longitude, self.longitude)
        self.assertEqual(location.title, self.title)
        self.assertEqual(location.thumb_url, self.thumb_url)
        self.assertEqual(location.thumb_width, self.thumb_width)
        self.assertEqual(location.thumb_height, self.thumb_height)
        self.assertDictEqual(location.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(location.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_location_to_json(self):
        location = telegram.InlineQueryResultLocation.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(location.to_json()))

    def test_location_to_dict(self):
        location = telegram.InlineQueryResultLocation.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(location))
        self.assertDictEqual(self.json_dict, location)


if __name__ == '__main__':
    unittest.main()
