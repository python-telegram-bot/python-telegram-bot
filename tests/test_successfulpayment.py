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
SuccessfulPayment"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class SuccessfulPaymentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram SuccessfulPayment."""

    def setUp(self):
        self.invoice_payload = 'invoice_payload'
        self.shipping_option_id = 'shipping_option_id'
        self.currency = 'EUR'
        self.total_amount = 100
        self.order_info = telegram.OrderInfo()
        self.telegram_payment_charge_id = 'telegram_payment_charge_id'
        self.provider_payment_charge_id = 'provider_payment_charge_id'

        self.json_dict = {
            'invoice_payload': self.invoice_payload,
            'shipping_option_id': self.shipping_option_id,
            'currency': self.currency,
            'total_amount': self.total_amount,
            'order_info': self.order_info.to_dict(),
            'telegram_payment_charge_id': self.telegram_payment_charge_id,
            'provider_payment_charge_id': self.provider_payment_charge_id
        }

    def test_successfulpayment_de_json(self):
        successfulpayment = telegram.SuccessfulPayment.de_json(self.json_dict, self._bot)

        self.assertEqual(successfulpayment.invoice_payload, self.invoice_payload)
        self.assertEqual(successfulpayment.shipping_option_id, self.shipping_option_id)
        self.assertEqual(successfulpayment.currency, self.currency)
        self.assertEqual(successfulpayment.order_info, self.order_info)
        self.assertEqual(successfulpayment.telegram_payment_charge_id,
                         self.telegram_payment_charge_id)
        self.assertEqual(successfulpayment.provider_payment_charge_id,
                         self.provider_payment_charge_id)

    def test_successfulpayment_to_json(self):
        successfulpayment = telegram.SuccessfulPayment.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(successfulpayment.to_json()))

    def test_successfulpayment_to_dict(self):
        successfulpayment = telegram.SuccessfulPayment.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(successfulpayment))
        self.assertDictEqual(self.json_dict, successfulpayment)

    def test_equality(self):
        a = telegram.SuccessfulPayment(self.currency, self.total_amount, self.invoice_payload,
                                       self.telegram_payment_charge_id,
                                       self.provider_payment_charge_id)
        b = telegram.SuccessfulPayment(self.currency, self.total_amount, self.invoice_payload,
                                       self.telegram_payment_charge_id,
                                       self.provider_payment_charge_id)
        c = telegram.SuccessfulPayment('', 0, '', self.telegram_payment_charge_id,
                                       self.provider_payment_charge_id)
        d = telegram.SuccessfulPayment(self.currency, self.total_amount, self.invoice_payload,
                                       self.telegram_payment_charge_id, '')

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertIsNot(a, b)

        self.assertEqual(a, c)
        self.assertEqual(hash(a), hash(c))

        self.assertNotEqual(a, d)
        self.assertNotEqual(hash(a), hash(d))


if __name__ == '__main__':
    unittest.main()
