#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

import pytest

from telegram import OrderInfo, SuccessfulPayment


@pytest.fixture(scope='class')
def successful_payment():
    return SuccessfulPayment(TestSuccessfulPayment.currency,
                             TestSuccessfulPayment.total_amount,
                             TestSuccessfulPayment.invoice_payload,
                             TestSuccessfulPayment.telegram_payment_charge_id,
                             TestSuccessfulPayment.provider_payment_charge_id,
                             shipping_option_id=TestSuccessfulPayment.shipping_option_id,
                             order_info=TestSuccessfulPayment.order_info)


class TestSuccessfulPayment(object):
    invoice_payload = 'invoice_payload'
    shipping_option_id = 'shipping_option_id'
    currency = 'EUR'
    total_amount = 100
    order_info = OrderInfo()
    telegram_payment_charge_id = 'telegram_payment_charge_id'
    provider_payment_charge_id = 'provider_payment_charge_id'

    def test_de_json(self, bot):
        json_dict = {
            'invoice_payload': self.invoice_payload,
            'shipping_option_id': self.shipping_option_id,
            'currency': self.currency,
            'total_amount': self.total_amount,
            'order_info': self.order_info.to_dict(),
            'telegram_payment_charge_id': self.telegram_payment_charge_id,
            'provider_payment_charge_id': self.provider_payment_charge_id
        }
        successful_payment = SuccessfulPayment.de_json(json_dict, bot)

        assert successful_payment.invoice_payload == self.invoice_payload
        assert successful_payment.shipping_option_id == self.shipping_option_id
        assert successful_payment.currency == self.currency
        assert successful_payment.order_info == self.order_info
        assert successful_payment.telegram_payment_charge_id == self.telegram_payment_charge_id
        assert successful_payment.provider_payment_charge_id == self.provider_payment_charge_id

    def test_to_dict(self, successful_payment):
        successful_payment_dict = successful_payment.to_dict()

        assert isinstance(successful_payment_dict, dict)
        assert successful_payment_dict['invoice_payload'] == successful_payment.invoice_payload
        assert (successful_payment_dict['shipping_option_id']
                == successful_payment.shipping_option_id)
        assert successful_payment_dict['currency'] == successful_payment.currency
        assert successful_payment_dict['order_info'] == successful_payment.order_info.to_dict()
        assert (successful_payment_dict['telegram_payment_charge_id']
                == successful_payment.telegram_payment_charge_id)
        assert (successful_payment_dict['provider_payment_charge_id']
                == successful_payment.provider_payment_charge_id)

    def test_equality(self):
        a = SuccessfulPayment(self.currency, self.total_amount, self.invoice_payload,
                              self.telegram_payment_charge_id,
                              self.provider_payment_charge_id)
        b = SuccessfulPayment(self.currency, self.total_amount, self.invoice_payload,
                              self.telegram_payment_charge_id,
                              self.provider_payment_charge_id)
        c = SuccessfulPayment('', 0, '', self.telegram_payment_charge_id,
                              self.provider_payment_charge_id)
        d = SuccessfulPayment(self.currency, self.total_amount, self.invoice_payload,
                              self.telegram_payment_charge_id, '')

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)
