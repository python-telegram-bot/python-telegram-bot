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

from telegram import ShippingAddress, OrderInfo

@pytest.fixture(scope='class')
def json_dict():
    return {
            'name': TestOrderInfo.name,
            'phone_number': TestOrderInfo.phone_number,
            'email': TestOrderInfo.email,
            'shipping_address': TestOrderInfo.shipping_address.to_dict()
        }

@pytest.fixture(scope='class')
def order_info():
   return OrderInfo(name=TestOrderInfo.name, phone_number=TestOrderInfo.phone_number, email=TestOrderInfo.email, shipping_address=TestOrderInfo.shipping_address)

class TestOrderInfo:
    """This object represents Tests for Telegram OrderInfo."""

    name = 'name'
    phone_number = 'phone_number'
    email = 'email'
    shipping_address = ShippingAddress('GB', '', 'London', '12 Grimmauld Place',
     '', 'WC1')
    
    
    
    def test_de_json(self):
        orderinfo = OrderInfo.de_json(json_dict, bot)

        assert orderinfo.name == self.name
        assert orderinfo.phone_number == self.phone_number
        assert orderinfo.email == self.email
        assert orderinfo.shipping_address == self.shipping_address

    def test_to_json(self):
        orderinfo = OrderInfo.de_json(json_dict, bot)

        json.loads(orderinfo.to_json())

    def test_to_dict(self):
        orderinfo = OrderInfo.de_json(json_dict, bot).to_dict()

        assert isinstance(orderinfo, dict)
        assert json_dict == orderinfo


