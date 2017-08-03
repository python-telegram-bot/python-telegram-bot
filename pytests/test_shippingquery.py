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

from telegram import Update, User, ShippingAddress, ShippingQuery

@pytest.fixture(scope='class')
def json_dict():
    return {
            'id': TestShippingQuery.id,
            'invoice_payload': TestShippingQuery.invoice_payload,
            'from': TestShippingQuery.from_user.to_dict(),
            'shipping_address': TestShippingQuery.shipping_address.to_dict()
        }

@pytest.fixture(scope='class')
def shipping_query():
   return ShippingQuery(id=TestShippingQuery.id, invoice_payload=TestShippingQuery.invoice_payload, from=TestShippingQuery.from_user, shipping_address=TestShippingQuery.shipping_address)

class TestShippingQuery:
    """This object represents Tests for Telegram ShippingQuery."""

    id = 5
    invoice_payload = 'invoice_payload'
    from_user = User(0, '')
    shipping_address = ShippingAddress('GB', '', 'London', '12 Grimmauld Place',
     '', 'WC1')
    
    
    
    def test_de_json(self):
        shippingquery = ShippingQuery.de_json(json_dict, bot)

        assert shippingquery.id == self.id
        assert shippingquery.invoice_payload == self.invoice_payload
        assert shippingquery.from_user == self.from_user
        assert shippingquery.shipping_address == self.shipping_address

    def test_to_json(self):
        shippingquery = ShippingQuery.de_json(json_dict, bot)

        json.loads(shippingquery.to_json())

    def test_to_dict(self):
        shippingquery = ShippingQuery.de_json(json_dict, bot).to_dict()

        assert isinstance(shippingquery, dict)
        assert json_dict == shippingquery

    def test_equality(self):
        a = ShippingQuery(self.id, self.from_user, self.invoice_payload,
                                   self.shipping_address)
        b = ShippingQuery(self.id, self.from_user, self.invoice_payload,
                                   self.shipping_address)
        c = ShippingQuery(self.id, None, '', None)
        d = ShippingQuery(0, self.from_user, self.invoice_payload, self.shipping_address)
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


