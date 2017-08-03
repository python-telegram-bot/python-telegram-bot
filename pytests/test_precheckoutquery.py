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
import json

import pytest

from telegram import Update, User, PreCheckoutQuery, OrderInfo

@pytest.fixture(scope='class')
def json_dict():
    return {
            'id': TestPreCheckoutQuery.id,
            'invoice_payload': TestPreCheckoutQuery.invoice_payload,
            'shipping_option_id': TestPreCheckoutQuery.shipping_option_id,
            'currency': TestPreCheckoutQuery.currency,
            'total_amount': TestPreCheckoutQuery.total_amount,
            'from': TestPreCheckoutQuery.from_user.to_dict(),
            'order_info': TestPreCheckoutQuery.order_info.to_dict()
        }

@pytest.fixture(scope='class')
def pre_checkout_query():
   return PreCheckoutQuery(id=TestPreCheckoutQuery.id, invoice_payload=TestPreCheckoutQuery.invoice_payload, shipping_option_id=TestPreCheckoutQuery.shipping_option_id, currency=TestPreCheckoutQuery.currency, total_amount=TestPreCheckoutQuery.total_amount, from=TestPreCheckoutQuery.from_user, order_info=TestPreCheckoutQuery.order_info)

class TestPreCheckoutQuery:
    """This object represents Tests for Telegram PreCheckoutQuery."""

    id = 5
    invoice_payload = 'invoice_payload'
    shipping_option_id = 'shipping_option_id'
    currency = 'EUR'
    total_amount = 100
    from_user = User(0, '')
    order_info = OrderInfo()
    
    
    
    def test_de_json(self):
        precheckoutquery = PreCheckoutQuery.de_json(json_dict, bot)

        assert precheckoutquery.id == self.id
        assert precheckoutquery.invoice_payload == self.invoice_payload
        assert precheckoutquery.shipping_option_id == self.shipping_option_id
        assert precheckoutquery.currency == self.currency
        assert precheckoutquery.from_user == self.from_user
        assert precheckoutquery.order_info == self.order_info

    def test_to_json(self):
        precheckoutquery = PreCheckoutQuery.de_json(json_dict, bot)

        json.loads(precheckoutquery.to_json())

    def test_to_dict(self):
        precheckoutquery = PreCheckoutQuery.de_json(json_dict, bot).to_dict()

        assert isinstance(precheckoutquery, dict)
        assert json_dict == precheckoutquery

    def test_equality(self):
        a = PreCheckoutQuery(self.id, self.from_user, self.currency, self.total_amount,
                                      self.invoice_payload)
        b = PreCheckoutQuery(self.id, self.from_user, self.currency, self.total_amount,
                                      self.invoice_payload)
        c = PreCheckoutQuery(self.id, None, '', 0, '')
        d = PreCheckoutQuery(0, self.from_user, self.currency, self.total_amount,
                                      self.invoice_payload)
        e = Update(self.id)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


