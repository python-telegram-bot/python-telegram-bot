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
ShippingAddress"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ShippingAddressTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram ShippingAddress."""

    def setUp(self):
        self.country_code = 'GB'
        self.state = 'state'
        self.city = 'London'
        self.street_line1 = '12 Grimmauld Place'
        self.street_line2 = 'street_line2'
        self.post_code = 'WC1'

        self.json_dict = {
            'country_code': self.country_code,
            'state': self.state,
            'city': self.city,
            'street_line1': self.street_line1,
            'street_line2': self.street_line2,
            'post_code': self.post_code
        }

    def test_shippingaddress_de_json(self):
        shippingaddress = telegram.ShippingAddress.de_json(self.json_dict, self._bot)

        self.assertEqual(shippingaddress.country_code, self.country_code)
        self.assertEqual(shippingaddress.state, self.state)
        self.assertEqual(shippingaddress.city, self.city)
        self.assertEqual(shippingaddress.street_line1, self.street_line1)
        self.assertEqual(shippingaddress.street_line2, self.street_line2)
        self.assertEqual(shippingaddress.post_code, self.post_code)

    def test_shippingaddress_to_json(self):
        shippingaddress = telegram.ShippingAddress.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(shippingaddress.to_json()))

    def test_shippingaddress_to_dict(self):
        shippingaddress = telegram.ShippingAddress.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(shippingaddress))
        self.assertDictEqual(self.json_dict, shippingaddress)

    def test_equality(self):
        a = telegram.ShippingAddress(self.country_code, self.state, self.city, self.street_line1,
                                     self.street_line2, self.post_code)
        b = telegram.ShippingAddress(self.country_code, self.state, self.city, self.street_line1,
                                     self.street_line2, self.post_code)
        d = telegram.ShippingAddress('', self.state, self.city, self.street_line1,
                                     self.street_line2, self.post_code)
        d2 = telegram.ShippingAddress(self.country_code, '', self.city, self.street_line1,
                                      self.street_line2, self.post_code)
        d3 = telegram.ShippingAddress(self.country_code, self.state, '', self.street_line1,
                                      self.street_line2, self.post_code)
        d4 = telegram.ShippingAddress(self.country_code, self.state, self.city, '',
                                      self.street_line2, self.post_code)
        d5 = telegram.ShippingAddress(self.country_code, self.state, self.city, self.street_line1,
                                      '', self.post_code)
        d6 = telegram.ShippingAddress(self.country_code, self.state, self.city, self.street_line1,
                                      self.street_line2, '')

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertIsNot(a, b)

        self.assertNotEqual(a, d)
        self.assertNotEqual(hash(a), hash(d))

        self.assertNotEqual(a, d2)
        self.assertNotEqual(hash(a), hash(d2))

        self.assertNotEqual(a, d3)
        self.assertNotEqual(hash(a), hash(d3))

        self.assertNotEqual(a, d4)
        self.assertNotEqual(hash(a), hash(d4))

        self.assertNotEqual(a, d5)
        self.assertNotEqual(hash(a), hash(d5))

        self.assertNotEqual(a, d6)
        self.assertNotEqual(hash(6), hash(d6))


if __name__ == '__main__':
    unittest.main()
