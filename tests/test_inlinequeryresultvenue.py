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
InlineQueryResultVenue"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultVenueTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultVenue."""

    def setUp(self):
        self._id = 'id'
        self.type = 'venue'
        self.latitude = 'latitude'
        self.longitude = 'longitude'
        self.title = 'title'
        self._address = 'address'  # nose binds self.address for testing
        self.foursquare_id = 'foursquare id'
        self.thumb_url = 'thumb url'
        self.thumb_width = 10
        self.thumb_height = 15
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])
        self.json_dict = {
            'id': self._id,
            'type': self.type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'title': self.title,
            'address': self._address,
            'foursquare_id': self.foursquare_id,
            'thumb_url': self.thumb_url,
            'thumb_width': self.thumb_width,
            'thumb_height': self.thumb_height,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_venue_de_json(self):
        venue = telegram.InlineQueryResultVenue.de_json(self.json_dict, self._bot)

        self.assertEqual(venue.id, self._id)
        self.assertEqual(venue.type, self.type)
        self.assertEqual(venue.latitude, self.latitude)
        self.assertEqual(venue.longitude, self.longitude)
        self.assertEqual(venue.title, self.title)
        self.assertEqual(venue.address, self._address)
        self.assertEqual(venue.foursquare_id, self.foursquare_id)
        self.assertEqual(venue.thumb_url, self.thumb_url)
        self.assertEqual(venue.thumb_width, self.thumb_width)
        self.assertEqual(venue.thumb_height, self.thumb_height)
        self.assertDictEqual(venue.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(venue.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_venue_to_json(self):
        venue = telegram.InlineQueryResultVenue.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(venue.to_json()))

    def test_venue_to_dict(self):
        venue = telegram.InlineQueryResultVenue.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(venue))
        self.assertDictEqual(self.json_dict, venue)

    def test_equality(self):
        a = telegram.InlineQueryResultVenue(self._id, self.longitude, self.latitude, self.title,
                                            self._address)
        b = telegram.InlineQueryResultVenue(self._id, self.longitude, self.latitude, self.title,
                                            self._address)
        c = telegram.InlineQueryResultVenue(self._id, "", self.latitude, self.title, self._address)
        d = telegram.InlineQueryResultVenue("", self.longitude, self.latitude, self.title,
                                            self._address)
        e = telegram.InlineQueryResultArticle(self._id, "", "")

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
