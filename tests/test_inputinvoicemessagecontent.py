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

from telegram import (
    InputInvoiceMessageContent,
    LabeledPrice,
    InputTextMessageContent,
)


@pytest.fixture(scope='class')
def input_invoice_message_content():
    return InputInvoiceMessageContent(
        title=TestInputInvoiceMessageContent.title,
        description=TestInputInvoiceMessageContent.description,
        payload=TestInputInvoiceMessageContent.payload,
        provider_token=TestInputInvoiceMessageContent.provider_token,
        currency=TestInputInvoiceMessageContent.currency,
        prices=TestInputInvoiceMessageContent.prices,
        max_tip_amount=TestInputInvoiceMessageContent.max_tip_amount,
        suggested_tip_amounts=TestInputInvoiceMessageContent.suggested_tip_amounts,
        provider_data=TestInputInvoiceMessageContent.provider_data,
        photo_url=TestInputInvoiceMessageContent.photo_url,
        photo_size=TestInputInvoiceMessageContent.photo_size,
        photo_width=TestInputInvoiceMessageContent.photo_width,
        photo_height=TestInputInvoiceMessageContent.photo_height,
        need_name=TestInputInvoiceMessageContent.need_name,
        need_phone_number=TestInputInvoiceMessageContent.need_phone_number,
        need_email=TestInputInvoiceMessageContent.need_email,
        need_shipping_address=TestInputInvoiceMessageContent.need_shipping_address,
        send_phone_number_to_provider=TestInputInvoiceMessageContent.send_phone_number_to_provider,
        send_email_to_provider=TestInputInvoiceMessageContent.send_email_to_provider,
        is_flexible=TestInputInvoiceMessageContent.is_flexible,
    )


class TestInputInvoiceMessageContent:
    title = 'invoice title'
    description = 'invoice description'
    payload = 'invoice payload'
    provider_token = 'provider token'
    currency = 'PTBCoin'
    prices = [LabeledPrice('label1', 42), LabeledPrice('label2', 314)]
    max_tip_amount = 420
    suggested_tip_amounts = ['314', '256']
    provider_data = 'provider data'
    photo_url = 'photo_url'
    photo_size = '314'
    photo_width = '420'
    photo_height = '256'
    need_name = True
    need_phone_number = True
    need_email = True
    need_shipping_address = True
    send_phone_number_to_provider = True
    send_email_to_provider = True
    is_flexible = True

    def test_slot_behaviour(self, input_invoice_message_content, recwarn, mro_slots):
        inst = input_invoice_message_content
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.title = 'should give warning', self.title
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_expected_values(self, input_invoice_message_content):
        assert input_invoice_message_content.title == self.title
        assert input_invoice_message_content.description == self.description
        assert input_invoice_message_content.payload == self.payload
        assert input_invoice_message_content.provider_token == self.provider_token
        assert input_invoice_message_content.currency == self.currency
        assert input_invoice_message_content.prices == self.prices
        assert input_invoice_message_content.max_tip_amount == self.max_tip_amount
        assert input_invoice_message_content.suggested_tip_amounts == [
            int(amount) for amount in self.suggested_tip_amounts
        ]
        assert input_invoice_message_content.provider_data == self.provider_data
        assert input_invoice_message_content.photo_url == self.photo_url
        assert input_invoice_message_content.photo_size == int(self.photo_size)
        assert input_invoice_message_content.photo_width == int(self.photo_width)
        assert input_invoice_message_content.photo_height == int(self.photo_height)
        assert input_invoice_message_content.need_name == self.need_name
        assert input_invoice_message_content.need_phone_number == self.need_phone_number
        assert input_invoice_message_content.need_email == self.need_email
        assert input_invoice_message_content.need_shipping_address == self.need_shipping_address
        assert (
            input_invoice_message_content.send_phone_number_to_provider
            == self.send_phone_number_to_provider
        )
        assert input_invoice_message_content.send_email_to_provider == self.send_email_to_provider
        assert input_invoice_message_content.is_flexible == self.is_flexible

    def test_to_dict(self, input_invoice_message_content):
        input_invoice_message_content_dict = input_invoice_message_content.to_dict()

        assert isinstance(input_invoice_message_content_dict, dict)
        assert input_invoice_message_content_dict['title'] == input_invoice_message_content.title
        assert (
            input_invoice_message_content_dict['description']
            == input_invoice_message_content.description
        )
        assert (
            input_invoice_message_content_dict['payload'] == input_invoice_message_content.payload
        )
        assert (
            input_invoice_message_content_dict['provider_token']
            == input_invoice_message_content.provider_token
        )
        assert (
            input_invoice_message_content_dict['currency']
            == input_invoice_message_content.currency
        )
        assert input_invoice_message_content_dict['prices'] == [
            price.to_dict() for price in input_invoice_message_content.prices
        ]
        assert (
            input_invoice_message_content_dict['max_tip_amount']
            == input_invoice_message_content.max_tip_amount
        )
        assert (
            input_invoice_message_content_dict['suggested_tip_amounts']
            == input_invoice_message_content.suggested_tip_amounts
        )
        assert (
            input_invoice_message_content_dict['provider_data']
            == input_invoice_message_content.provider_data
        )
        assert (
            input_invoice_message_content_dict['photo_url']
            == input_invoice_message_content.photo_url
        )
        assert (
            input_invoice_message_content_dict['photo_size']
            == input_invoice_message_content.photo_size
        )
        assert (
            input_invoice_message_content_dict['photo_width']
            == input_invoice_message_content.photo_width
        )
        assert (
            input_invoice_message_content_dict['photo_height']
            == input_invoice_message_content.photo_height
        )
        assert (
            input_invoice_message_content_dict['need_name']
            == input_invoice_message_content.need_name
        )
        assert (
            input_invoice_message_content_dict['need_phone_number']
            == input_invoice_message_content.need_phone_number
        )
        assert (
            input_invoice_message_content_dict['need_email']
            == input_invoice_message_content.need_email
        )
        assert (
            input_invoice_message_content_dict['need_shipping_address']
            == input_invoice_message_content.need_shipping_address
        )
        assert (
            input_invoice_message_content_dict['send_phone_number_to_provider']
            == input_invoice_message_content.send_phone_number_to_provider
        )
        assert (
            input_invoice_message_content_dict['send_email_to_provider']
            == input_invoice_message_content.send_email_to_provider
        )
        assert (
            input_invoice_message_content_dict['is_flexible']
            == input_invoice_message_content.is_flexible
        )

    def test_de_json(self, bot):
        assert InputInvoiceMessageContent.de_json({}, bot=bot) is None

        json_dict = {
            'title': self.title,
            'description': self.description,
            'payload': self.payload,
            'provider_token': self.provider_token,
            'currency': self.currency,
            'prices': [price.to_dict() for price in self.prices],
            'max_tip_amount': self.max_tip_amount,
            'suggested_tip_amounts': self.suggested_tip_amounts,
            'provider_data': self.provider_data,
            'photo_url': self.photo_url,
            'photo_size': self.photo_size,
            'photo_width': self.photo_width,
            'photo_height': self.photo_height,
            'need_name': self.need_name,
            'need_phone_number': self.need_phone_number,
            'need_email': self.need_email,
            'need_shipping_address': self.need_shipping_address,
            'send_phone_number_to_provider': self.send_phone_number_to_provider,
            'send_email_to_provider': self.send_email_to_provider,
            'is_flexible': self.is_flexible,
        }

        input_invoice_message_content = InputInvoiceMessageContent.de_json(json_dict, bot=bot)

        assert input_invoice_message_content.title == self.title
        assert input_invoice_message_content.description == self.description
        assert input_invoice_message_content.payload == self.payload
        assert input_invoice_message_content.provider_token == self.provider_token
        assert input_invoice_message_content.currency == self.currency
        assert input_invoice_message_content.prices == self.prices
        assert input_invoice_message_content.max_tip_amount == self.max_tip_amount
        assert input_invoice_message_content.suggested_tip_amounts == [
            int(amount) for amount in self.suggested_tip_amounts
        ]
        assert input_invoice_message_content.provider_data == self.provider_data
        assert input_invoice_message_content.photo_url == self.photo_url
        assert input_invoice_message_content.photo_size == int(self.photo_size)
        assert input_invoice_message_content.photo_width == int(self.photo_width)
        assert input_invoice_message_content.photo_height == int(self.photo_height)
        assert input_invoice_message_content.need_name == self.need_name
        assert input_invoice_message_content.need_phone_number == self.need_phone_number
        assert input_invoice_message_content.need_email == self.need_email
        assert input_invoice_message_content.need_shipping_address == self.need_shipping_address
        assert (
            input_invoice_message_content.send_phone_number_to_provider
            == self.send_phone_number_to_provider
        )
        assert input_invoice_message_content.send_email_to_provider == self.send_email_to_provider
        assert input_invoice_message_content.is_flexible == self.is_flexible

    def test_equality(self):
        a = InputInvoiceMessageContent(
            self.title,
            self.description,
            self.payload,
            self.provider_token,
            self.currency,
            self.prices,
        )
        b = InputInvoiceMessageContent(
            self.title,
            self.description,
            self.payload,
            self.provider_token,
            self.currency,
            self.prices,
            max_tip_amount=100,
            provider_data='foobar',
        )
        c = InputInvoiceMessageContent(
            self.title,
            self.description,
            self.payload,
            self.provider_token,
            self.currency,
            # the first prices amount & the second lebal changed
            [LabeledPrice('label1', 24), LabeledPrice('label22', 314)],
        )
        d = InputInvoiceMessageContent(
            self.title,
            self.description,
            'different_payload',
            self.provider_token,
            self.currency,
            self.prices,
        )
        e = InputTextMessageContent('text')

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
