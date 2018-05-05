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

from telegram import Update, User, ShippingAddress, ShippingQuery


@pytest.fixture(scope='class')
def shipping_query(bot):
    return ShippingQuery(TestShippingQuery.id,
                         TestShippingQuery.from_user,
                         TestShippingQuery.invoice_payload,
                         TestShippingQuery.shipping_address,
                         bot=bot)


class TestShippingQuery(object):
    id = 5
    invoice_payload = 'invoice_payload'
    from_user = User(0, '', False)
    shipping_address = ShippingAddress('GB', '', 'London', '12 Grimmauld Place', '', 'WC1')

    def test_de_json(self, bot):
        json_dict = {
            'id': TestShippingQuery.id,
            'invoice_payload': TestShippingQuery.invoice_payload,
            'from': TestShippingQuery.from_user.to_dict(),
            'shipping_address': TestShippingQuery.shipping_address.to_dict()
        }
        shipping_query = ShippingQuery.de_json(json_dict, bot)

        assert shipping_query.id == self.id
        assert shipping_query.invoice_payload == self.invoice_payload
        assert shipping_query.from_user == self.from_user
        assert shipping_query.shipping_address == self.shipping_address

    def test_to_dict(self, shipping_query):
        shipping_query_dict = shipping_query.to_dict()

        assert isinstance(shipping_query_dict, dict)
        assert shipping_query_dict['id'] == shipping_query.id
        assert shipping_query_dict['invoice_payload'] == shipping_query.invoice_payload
        assert shipping_query_dict['from'] == shipping_query.from_user.to_dict()
        assert shipping_query_dict['shipping_address'] == shipping_query.shipping_address.to_dict()

    def test_answer(self, monkeypatch, shipping_query):
        def test(*args, **kwargs):
            return args[1] == shipping_query.id

        monkeypatch.setattr('telegram.Bot.answer_shipping_query', test)
        assert shipping_query.answer()

    def test_equality(self):
        a = ShippingQuery(self.id, self.from_user, self.invoice_payload, self.shipping_address)
        b = ShippingQuery(self.id, self.from_user, self.invoice_payload, self.shipping_address)
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
