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
"""This module contains a object that represents Tests for Telegram Venue"""

import sys

if sys.version_info[0:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class VenueTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Venue."""

    def setUp(self):
        self.location = telegram.Location(longitude=1., latitude=0.)
        self.title = 'title'
        self.address = 'address'
        self.foursquare_id = 'foursquare id'

        self.json_dict = {
            'location': self.location.to_dict(),
            'title': self.title,
            'address': self.address,
            'foursquare_id': self.foursquare_id
        }

    def test_sticker_de_json(self):
        sticker = telegram.Venue.de_json(self.json_dict)

        self.assertTrue(isinstance(sticker.location, telegram.Location))
        self.assertEqual(sticker.title, self.title)
        self.assertEqual(sticker.address, self.address)
        self.assertEqual(sticker.foursquare_id, self.foursquare_id)

    def test_sticker_to_json(self):
        sticker = telegram.Venue.de_json(self.json_dict)

        self.assertTrue(self.is_json(sticker.to_json()))

    def test_sticker_to_dict(self):
        sticker = telegram.Venue.de_json(self.json_dict).to_dict()

        self.assertTrue(self.is_dict(sticker))
        self.assertDictEqual(self.json_dict, sticker)


if __name__ == '__main__':
    unittest.main()
