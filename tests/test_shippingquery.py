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
ShippingQuery"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ShippingQueryTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram ShippingQuery."""

    def setUp(self):
        self._id = 5
        self.invoice_payload = 'invoice_payload'
        self.from_user = telegram.User(0, '')
        self.shipping_address = telegram.ShippingAddress('GB', '', 'London', '12 Grimmauld Place',
                                                         '', 'WC1')

        self.json_dict = {
            'id': self._id,
            'invoice_payload': self.invoice_payload,
            'from': self.from_user.to_dict(),
            'shipping_address': self.shipping_address.to_dict()
        }

    def test_shippingquery_de_json(self):
        shippingquery = telegram.ShippingQuery.de_json(self.json_dict, self._bot)

        self.assertEqual(shippingquery.id, self._id)
        self.assertEqual(shippingquery.invoice_payload, self.invoice_payload)
        self.assertEqual(shippingquery.from_user, self.from_user)
        self.assertEqual(shippingquery.shipping_address, self.shipping_address)

    def test_shippingquery_to_json(self):
        shippingquery = telegram.ShippingQuery.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(shippingquery.to_json()))

    def test_shippingquery_to_dict(self):
        shippingquery = telegram.ShippingQuery.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(shippingquery))
        self.assertDictEqual(self.json_dict, shippingquery)

    def test_equality(self):
        a = telegram.ShippingQuery(self._id, self.from_user, self.invoice_payload,
                                   self.shipping_address)
        b = telegram.ShippingQuery(self._id, self.from_user, self.invoice_payload,
                                   self.shipping_address)
        c = telegram.ShippingQuery(self._id, None, '', None)
        d = telegram.ShippingQuery(0, self.from_user, self.invoice_payload, self.shipping_address)
        e = telegram.Update(self._id)

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
