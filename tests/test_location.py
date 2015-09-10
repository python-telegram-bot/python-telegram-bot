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

"""This module contains a object that represents Tests for Telegram Location"""

import os
import unittest
import sys
sys.path.append('.')

import telegram
from tests.base import BaseTest


class LocationTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Location."""

    def setUp(self):
        self.latitude = -23.691288
        self.longitude = -46.788279

        self.json_dict = {
            'latitude': self.latitude,
            'longitude': self.longitude
        }

    def test_send_location_implicit_args(self):
        """Test telegram.Bot sendLocation method"""
        print('Testing bot.sendLocation - Implicit arguments')

        message = self._bot.sendLocation(self._chat_id,
                                         self.latitude,
                                         self.longitude)

        location = message.location

        self.assertEqual(location.latitude, self.latitude)
        self.assertEqual(location.longitude, self.longitude)

    def test_send_location_explicit_args(self):
        """Test telegram.Bot sendLocation method"""
        print('Testing bot.sendLocation - Explicit arguments')

        message = self._bot.sendLocation(chat_id=self._chat_id,
                                         latitude=self.latitude,
                                         longitude=self.longitude)

        location = message.location

        self.assertEqual(location.latitude, self.latitude)
        self.assertEqual(location.longitude, self.longitude)

    def test_location_de_json(self):
        """Test Location.de_json() method"""
        print('Testing Location.de_json()')

        location = telegram.Location.de_json(self.json_dict)

        self.assertEqual(location.latitude, self.latitude)
        self.assertEqual(location.longitude, self.longitude)

    def test_location_to_json(self):
        """Test Location.to_json() method"""
        print('Testing Location.to_json()')

        location = telegram.Location.de_json(self.json_dict)

        self.assertTrue(self.is_json(location.to_json()))

    def test_location_to_dict(self):
        """Test Location.to_dict() method"""
        print('Testing Location.to_dict()')

        location = telegram.Location.de_json(self.json_dict)

        self.assertEqual(location['latitude'], self.latitude)
        self.assertEqual(location['longitude'], self.longitude)

    def test_error_send_location_empty_args(self):
        print('Testing bot.sendLocation - Empty arguments')

        json_dict = self.json_dict

        json_dict['latitude'] = ''
        json_dict['longitude'] = ''

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendLocation(chat_id=self._chat_id,
                                                         **json_dict))

    def test_error_location_without_required_args(self):
        print('Testing bot.sendLocation - Without required arguments')

        json_dict = self.json_dict

        del(json_dict['latitude'])
        del(json_dict['longitude'])

        self.assertRaises(TypeError,
                          lambda: self._bot.sendLocation(chat_id=self._chat_id,
                                                         **json_dict))

if __name__ == '__main__':
    unittest.main()
