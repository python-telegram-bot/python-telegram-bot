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
PreCheckoutQuery"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class PreCheckoutQueryTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram PreCheckoutQuery."""

    def setUp(self):
        self._id = 5
        self.invoice_payload = 'invoice_payload'
        self.shipping_option_id = 'shipping_option_id'
        self.currency = 'EUR'
        self.total_amount = 100
        self.from_user = telegram.User(0, '')
        self.order_info = telegram.OrderInfo()

        self.json_dict = {
            'id': self._id,
            'invoice_payload': self.invoice_payload,
            'shipping_option_id': self.shipping_option_id,
            'currency': self.currency,
            'total_amount': self.total_amount,
            'from': self.from_user.to_dict(),
            'order_info': self.order_info.to_dict()
        }

    def test_precheckoutquery_de_json(self):
        precheckoutquery = telegram.PreCheckoutQuery.de_json(self.json_dict, self._bot)

        self.assertEqual(precheckoutquery.id, self._id)
        self.assertEqual(precheckoutquery.invoice_payload, self.invoice_payload)
        self.assertEqual(precheckoutquery.shipping_option_id, self.shipping_option_id)
        self.assertEqual(precheckoutquery.currency, self.currency)
        self.assertEqual(precheckoutquery.from_user, self.from_user)
        self.assertEqual(precheckoutquery.order_info, self.order_info)

    def test_precheckoutquery_to_json(self):
        precheckoutquery = telegram.PreCheckoutQuery.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(precheckoutquery.to_json()))

    def test_precheckoutquery_to_dict(self):
        precheckoutquery = telegram.PreCheckoutQuery.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(precheckoutquery))
        self.assertDictEqual(self.json_dict, precheckoutquery)

    def test_equality(self):
        a = telegram.PreCheckoutQuery(self._id, self.from_user, self.currency, self.total_amount,
                                      self.invoice_payload)
        b = telegram.PreCheckoutQuery(self._id, self.from_user, self.currency, self.total_amount,
                                      self.invoice_payload)
        c = telegram.PreCheckoutQuery(self._id, None, '', 0, '')
        d = telegram.PreCheckoutQuery(0, self.from_user, self.currency, self.total_amount,
                                      self.invoice_payload)
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
