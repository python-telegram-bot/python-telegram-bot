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
InputLocationMessageContent"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InputLocationMessageContentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InputLocationMessageContent."""

    def setUp(self):
        self.latitude = 1.
        self.longitude = 2.

        self.json_dict = {
            'longitude': self.longitude,
            'latitude': self.latitude,
        }

    def test_ilmc_de_json(self):
        ilmc = telegram.InputLocationMessageContent.de_json(self.json_dict, self._bot)

        self.assertEqual(ilmc.longitude, self.longitude)
        self.assertEqual(ilmc.latitude, self.latitude)

    def test_ilmc_de_json_factory(self):
        ilmc = telegram.InputMessageContent.de_json(self.json_dict, self._bot)

        self.assertTrue(isinstance(ilmc, telegram.InputLocationMessageContent))

    def test_ilmc_de_json_factory_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['longitude'])
        # If none args are sent it will fall in a different condition
        # del (json_dict['latitude'])

        ilmc = telegram.InputMessageContent.de_json(json_dict, self._bot)

        self.assertFalse(ilmc)

    def test_ilmc_to_json(self):
        ilmc = telegram.InputLocationMessageContent.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(ilmc.to_json()))

    def test_ilmc_to_dict(self):
        ilmc = telegram.InputLocationMessageContent.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(ilmc))
        self.assertDictEqual(self.json_dict, ilmc)


if __name__ == '__main__':
    unittest.main()
