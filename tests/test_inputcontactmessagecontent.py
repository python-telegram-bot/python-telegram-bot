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
InputContactMessageContent"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InputContactMessageContentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InputContactMessageContent."""

    def setUp(self):
        self.phone_number = 'phone number'
        self.first_name = 'first name'
        self.last_name = 'last name'

        self.json_dict = {
            'first_name': self.first_name,
            'phone_number': self.phone_number,
            'last_name': self.last_name,
        }

    def test_icmc_de_json(self):
        icmc = telegram.InputContactMessageContent.de_json(self.json_dict, self._bot)

        self.assertEqual(icmc.first_name, self.first_name)
        self.assertEqual(icmc.phone_number, self.phone_number)
        self.assertEqual(icmc.last_name, self.last_name)

    def test_icmc_de_json_factory(self):
        icmc = telegram.InputMessageContent.de_json(self.json_dict, self._bot)

        self.assertTrue(isinstance(icmc, telegram.InputContactMessageContent))

    def test_icmc_de_json_factory_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['phone_number'])
        del (json_dict['first_name'])

        icmc = telegram.InputMessageContent.de_json(json_dict, self._bot)

        self.assertFalse(icmc)

    def test_icmc_to_json(self):
        icmc = telegram.InputContactMessageContent.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(icmc.to_json()))

    def test_icmc_to_dict(self):
        icmc = telegram.InputContactMessageContent.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(icmc))
        self.assertDictEqual(self.json_dict, icmc)


if __name__ == '__main__':
    unittest.main()
