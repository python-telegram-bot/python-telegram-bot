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
InputVenueMessageContent"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InputVenueMessageContentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InputVenueMessageContent."""

    def setUp(self):
        self.latitude = 1.
        self.longitude = 2.
        self.title = 'title'
        self._address = 'address'  # nose binds self.address for testing
        self.foursquare_id = 'foursquare id'

        self.json_dict = {
            'longitude': self.longitude,
            'latitude': self.latitude,
            'title': self.title,
            'address': self._address,
            'foursquare_id': self.foursquare_id,
        }

    def test_ivmc_de_json(self):
        ivmc = telegram.InputVenueMessageContent.de_json(self.json_dict, self._bot)

        self.assertEqual(ivmc.longitude, self.longitude)
        self.assertEqual(ivmc.latitude, self.latitude)
        self.assertEqual(ivmc.title, self.title)
        self.assertEqual(ivmc.address, self._address)
        self.assertEqual(ivmc.foursquare_id, self.foursquare_id)

    def test_ivmc_de_json_factory(self):
        ivmc = telegram.InputMessageContent.de_json(self.json_dict, self._bot)

        self.assertTrue(isinstance(ivmc, telegram.InputVenueMessageContent))

    def test_ivmc_de_json_factory_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['longitude'])
        del (json_dict['latitude'])
        del (json_dict['title'])
        del (json_dict['address'])

        ivmc = telegram.InputMessageContent.de_json(json_dict, self._bot)

        self.assertFalse(ivmc)

    def test_ivmc_to_json(self):
        ivmc = telegram.InputVenueMessageContent.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(ivmc.to_json()))

    def test_ivmc_to_dict(self):
        ivmc = telegram.InputVenueMessageContent.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(ivmc))
        self.assertDictEqual(self.json_dict, ivmc)


if __name__ == '__main__':
    unittest.main()
