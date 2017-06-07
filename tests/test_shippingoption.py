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
ShippingOption"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ShippingOptionTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram ShippingOption."""

    def setUp(self):
        self.id = 'id'
        self.title = 'title'
        self.prices = [
            telegram.LabeledPrice('Fish Container', 100),
            telegram.LabeledPrice('Premium Fish Container', 1000)
        ]

        self.json_dict = {
            'id': self.id,
            'title': self.title,
            'prices': [x.to_dict() for x in self.prices]
        }

    def test_shippingoption_de_json(self):
        shippingoption = telegram.ShippingOption.de_json(self.json_dict, self._bot)

        self.assertEqual(shippingoption.id, self.id)
        self.assertEqual(shippingoption.title, self.title)
        self.assertEqual(shippingoption.prices, self.prices)

    def test_shippingoption_to_json(self):
        shippingoption = telegram.ShippingOption.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(shippingoption.to_json()))

    def test_shippingoption_to_dict(self):
        shippingoption = telegram.ShippingOption.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(shippingoption))
        self.assertDictEqual(self.json_dict, shippingoption)

    def test_equality(self):
        a = telegram.ShippingOption(self.id, self.title, self.prices)
        b = telegram.ShippingOption(self.id, self.title, self.prices)
        c = telegram.ShippingOption(self.id, '', [])
        d = telegram.ShippingOption(0, self.title, self.prices)
        e = telegram.Voice(self.id, 0)

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
