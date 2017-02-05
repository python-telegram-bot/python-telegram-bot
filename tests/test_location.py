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
"""This module contains an object that represents Tests for Telegram Location"""

import unittest
import sys

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest


class LocationTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Location."""

    def setUp(self):
        self.latitude = -23.691288
        self.longitude = -46.788279

        self.json_dict = {'latitude': self.latitude, 'longitude': self.longitude}

    def test_send_location_implicit_args(self):
        message = self._bot.sendLocation(self._chat_id, self.latitude, self.longitude)

        location = message.location

        self.assertEqual(location.latitude, self.latitude)
        self.assertEqual(location.longitude, self.longitude)

    def test_send_location_explicit_args(self):
        message = self._bot.sendLocation(
            chat_id=self._chat_id, latitude=self.latitude, longitude=self.longitude)

        location = message.location

        self.assertEqual(location.latitude, self.latitude)
        self.assertEqual(location.longitude, self.longitude)

    def test_location_de_json(self):
        location = telegram.Location.de_json(self.json_dict, self._bot)

        self.assertEqual(location.latitude, self.latitude)
        self.assertEqual(location.longitude, self.longitude)

    def test_location_to_json(self):
        location = telegram.Location.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(location.to_json()))

    def test_location_to_dict(self):
        location = telegram.Location.de_json(self.json_dict, self._bot)

        self.assertEqual(location['latitude'], self.latitude)
        self.assertEqual(location['longitude'], self.longitude)

    def test_error_send_location_empty_args(self):
        json_dict = self.json_dict

        json_dict['latitude'] = ''
        json_dict['longitude'] = ''

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendLocation(chat_id=self._chat_id,
                                                         **json_dict))

    def test_error_location_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['latitude'])
        del (json_dict['longitude'])

        self.assertRaises(TypeError,
                          lambda: self._bot.sendLocation(chat_id=self._chat_id,
                                                         **json_dict))

    @flaky(3, 1)
    def test_reply_location(self):
        """Test for Message.reply_location"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_location(self.latitude, self.longitude)

        self.assertEqual(message.location.latitude, self.latitude)
        self.assertEqual(message.location.longitude, self.longitude)


if __name__ == '__main__':
    unittest.main()
