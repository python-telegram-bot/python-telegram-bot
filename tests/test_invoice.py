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
Invoice"""

import sys
import unittest

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest, timeout


class InvoiceTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Invoice."""

    def setUp(self):
        self.payload = 'payload'
        self.provider_token = self._payment_provider_token
        self.prices = [telegram.LabeledPrice('Fish', 100), telegram.LabeledPrice('Fish Tax', 1000)]

        self.title = 'title'
        self.description = 'description'
        self.start_parameter = 'start_parameter'
        self.currency = 'EUR'
        self.total_amount = sum([p.amount for p in self.prices])

        self.json_dict = {
            'title': self.title,
            'description': self.description,
            'start_parameter': self.start_parameter,
            'currency': self.currency,
            'total_amount': self.total_amount
        }

    def test_invoice_de_json(self):
        invoice = telegram.Invoice.de_json(self.json_dict, self._bot)

        self.assertEqual(invoice.title, self.title)
        self.assertEqual(invoice.description, self.description)
        self.assertEqual(invoice.start_parameter, self.start_parameter)
        self.assertEqual(invoice.currency, self.currency)
        self.assertEqual(invoice.total_amount, self.total_amount)

    def test_invoice_to_json(self):
        invoice = telegram.Invoice.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(invoice.to_json()))

    def test_invoice_to_dict(self):
        invoice = telegram.Invoice.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(invoice))
        self.assertDictEqual(self.json_dict, invoice)

    @flaky(3, 1)
    @timeout(10)
    def test_send_invoice_required_args_only(self):
        message = self._bot.send_invoice(self._chat_id, self.title, self.description, self.payload,
                                         self.provider_token, self.start_parameter, self.currency,
                                         self.prices)
        invoice = message.invoice

        self.assertEqual(invoice.currency, self.currency)
        self.assertEqual(invoice.start_parameter, self.start_parameter)
        self.assertEqual(invoice.description, self.description)
        self.assertEqual(invoice.title, self.title)
        self.assertEqual(invoice.total_amount, self.total_amount)

    @flaky(3, 1)
    @timeout(10)
    def test_send_invoice_all_args(self):
        message = self._bot.send_invoice(
            self._chat_id,
            self.title,
            self.description,
            self.payload,
            self.provider_token,
            self.start_parameter,
            self.currency,
            self.prices,
            photo_url='https://raw.githubusercontent.com/'
            'python-telegram-bot/logos/master/'
            'logo/png/ptb-logo_240.png',
            photo_size=240,
            photo_width=240,
            photo_height=240,
            need_name=True,
            need_phone_number=True,
            need_shipping_address=True,
            is_flexible=True)
        invoice = message.invoice

        self.assertEqual(invoice.currency, self.currency)
        self.assertEqual(invoice.start_parameter, self.start_parameter)
        self.assertEqual(invoice.description, self.description)
        self.assertEqual(invoice.title, self.title)
        self.assertEqual(invoice.total_amount, self.total_amount)


if __name__ == '__main__':
    unittest.main()
