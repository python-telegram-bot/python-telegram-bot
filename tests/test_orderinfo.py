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
OrderInfo"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class OrderInfoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram OrderInfo."""

    def setUp(self):
        self.name = 'name'
        self.phone_number = 'phone_number'
        self.email = 'email'
        self.shipping_address = telegram.ShippingAddress('GB', '', 'London', '12 Grimmauld Place',
                                                         '', 'WC1')

        self.json_dict = {
            'name': self.name,
            'phone_number': self.phone_number,
            'email': self.email,
            'shipping_address': self.shipping_address.to_dict()
        }

    def test_orderinfo_de_json(self):
        orderinfo = telegram.OrderInfo.de_json(self.json_dict, self._bot)

        self.assertEqual(orderinfo.name, self.name)
        self.assertEqual(orderinfo.phone_number, self.phone_number)
        self.assertEqual(orderinfo.email, self.email)
        self.assertEqual(orderinfo.shipping_address, self.shipping_address)

    def test_orderinfo_to_json(self):
        orderinfo = telegram.OrderInfo.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(orderinfo.to_json()))

    def test_orderinfo_to_dict(self):
        orderinfo = telegram.OrderInfo.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(orderinfo))
        self.assertDictEqual(self.json_dict, orderinfo)


if __name__ == '__main__':
    unittest.main()
