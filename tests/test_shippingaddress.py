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

from telegram import ShippingAddress


@pytest.fixture(scope='class')
def shipping_address():
    return ShippingAddress(TestShippingAddress.country_code,
                           TestShippingAddress.state,
                           TestShippingAddress.city,
                           TestShippingAddress.street_line1,
                           TestShippingAddress.street_line2,
                           TestShippingAddress.post_code)


class TestShippingAddress(object):
    country_code = 'GB'
    state = 'state'
    city = 'London'
    street_line1 = '12 Grimmauld Place'
    street_line2 = 'street_line2'
    post_code = 'WC1'

    def test_de_json(self, bot):
        json_dict = {
            'country_code': self.country_code,
            'state': self.state,
            'city': self.city,
            'street_line1': self.street_line1,
            'street_line2': self.street_line2,
            'post_code': self.post_code
        }
        shipping_address = ShippingAddress.de_json(json_dict, bot)

        assert shipping_address.country_code == self.country_code
        assert shipping_address.state == self.state
        assert shipping_address.city == self.city
        assert shipping_address.street_line1 == self.street_line1
        assert shipping_address.street_line2 == self.street_line2
        assert shipping_address.post_code == self.post_code

    def test_to_dict(self, shipping_address):
        shipping_address_dict = shipping_address.to_dict()

        assert isinstance(shipping_address_dict, dict)
        assert shipping_address_dict['country_code'] == shipping_address.country_code
        assert shipping_address_dict['state'] == shipping_address.state
        assert shipping_address_dict['city'] == shipping_address.city
        assert shipping_address_dict['street_line1'] == shipping_address.street_line1
        assert shipping_address_dict['street_line2'] == shipping_address.street_line2
        assert shipping_address_dict['post_code'] == shipping_address.post_code

    def test_equality(self):
        a = ShippingAddress(self.country_code, self.state, self.city, self.street_line1,
                            self.street_line2, self.post_code)
        b = ShippingAddress(self.country_code, self.state, self.city, self.street_line1,
                            self.street_line2, self.post_code)
        d = ShippingAddress('', self.state, self.city, self.street_line1,
                            self.street_line2, self.post_code)
        d2 = ShippingAddress(self.country_code, '', self.city, self.street_line1,
                             self.street_line2, self.post_code)
        d3 = ShippingAddress(self.country_code, self.state, '', self.street_line1,
                             self.street_line2, self.post_code)
        d4 = ShippingAddress(self.country_code, self.state, self.city, '',
                             self.street_line2, self.post_code)
        d5 = ShippingAddress(self.country_code, self.state, self.city, self.street_line1,
                             '', self.post_code)
        d6 = ShippingAddress(self.country_code, self.state, self.city, self.street_line1,
                             self.street_line2, '')

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != d2
        assert hash(a) != hash(d2)

        assert a != d3
        assert hash(a) != hash(d3)

        assert a != d4
        assert hash(a) != hash(d4)

        assert a != d5
        assert hash(a) != hash(d5)

        assert a != d6
        assert hash(6) != hash(d6)
