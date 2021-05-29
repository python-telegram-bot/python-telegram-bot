#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from telegram import ShippingAddress, OrderInfo


@pytest.fixture(scope='class')
def order_info():
    return OrderInfo(
        TestOrderInfo.name,
        TestOrderInfo.phone_number,
        TestOrderInfo.email,
        TestOrderInfo.shipping_address,
    )


class TestOrderInfo:
    name = 'name'
    phone_number = 'phone_number'
    email = 'email'
    shipping_address = ShippingAddress('GB', '', 'London', '12 Grimmauld Place', '', 'WC1')

    def test_slot_behaviour(self, order_info, mro_slots, recwarn):
        for attr in order_info.__slots__:
            assert getattr(order_info, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not order_info.__dict__, f"got missing slot(s): {order_info.__dict__}"
        assert len(mro_slots(order_info)) == len(set(mro_slots(order_info))), "duplicate slot"
        order_info.custom, order_info.name = 'should give warning', self.name
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self, bot):
        json_dict = {
            'name': TestOrderInfo.name,
            'phone_number': TestOrderInfo.phone_number,
            'email': TestOrderInfo.email,
            'shipping_address': TestOrderInfo.shipping_address.to_dict(),
        }
        order_info = OrderInfo.de_json(json_dict, bot)

        assert order_info.name == self.name
        assert order_info.phone_number == self.phone_number
        assert order_info.email == self.email
        assert order_info.shipping_address == self.shipping_address

    def test_to_dict(self, order_info):
        order_info_dict = order_info.to_dict()

        assert isinstance(order_info_dict, dict)
        assert order_info_dict['name'] == order_info.name
        assert order_info_dict['phone_number'] == order_info.phone_number
        assert order_info_dict['email'] == order_info.email
        assert order_info_dict['shipping_address'] == order_info.shipping_address.to_dict()

    def test_equality(self):
        a = OrderInfo(
            'name',
            'number',
            'mail',
            ShippingAddress('GB', '', 'London', '12 Grimmauld Place', '', 'WC1'),
        )
        b = OrderInfo(
            'name',
            'number',
            'mail',
            ShippingAddress('GB', '', 'London', '12 Grimmauld Place', '', 'WC1'),
        )
        c = OrderInfo(
            'name',
            'number',
            'mail',
            ShippingAddress('GB', '', 'London', '13 Grimmauld Place', '', 'WC1'),
        )
        d = OrderInfo(
            'name',
            'number',
            'e-mail',
            ShippingAddress('GB', '', 'London', '12 Grimmauld Place', '', 'WC1'),
        )
        e = ShippingAddress('GB', '', 'London', '12 Grimmauld Place', '', 'WC1')

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
