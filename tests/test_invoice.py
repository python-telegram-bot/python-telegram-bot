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
from flaky import flaky

from telegram import LabeledPrice, Invoice
from telegram.error import BadRequest


@pytest.fixture(scope='class')
def invoice():
    return Invoice(
        TestInvoice.title,
        TestInvoice.description,
        TestInvoice.start_parameter,
        TestInvoice.currency,
        TestInvoice.total_amount,
    )


class TestInvoice:
    payload = 'payload'
    prices = [LabeledPrice('Fish', 100), LabeledPrice('Fish Tax', 1000)]
    provider_data = """{"test":"test"}"""
    title = 'title'
    description = 'description'
    start_parameter = 'start_parameter'
    currency = 'EUR'
    total_amount = sum(p.amount for p in prices)
    max_tip_amount = 42
    suggested_tip_amounts = [13, 42]

    def test_slot_behaviour(self, invoice, mro_slots, recwarn):
        for attr in invoice.__slots__:
            assert getattr(invoice, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not invoice.__dict__, f"got missing slot(s): {invoice.__dict__}"
        assert len(mro_slots(invoice)) == len(set(mro_slots(invoice))), "duplicate slot"
        invoice.custom, invoice.title = 'should give warning', self.title
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self, bot):
        invoice_json = Invoice.de_json(
            {
                'title': TestInvoice.title,
                'description': TestInvoice.description,
                'start_parameter': TestInvoice.start_parameter,
                'currency': TestInvoice.currency,
                'total_amount': TestInvoice.total_amount,
            },
            bot,
        )

        assert invoice_json.title == self.title
        assert invoice_json.description == self.description
        assert invoice_json.start_parameter == self.start_parameter
        assert invoice_json.currency == self.currency
        assert invoice_json.total_amount == self.total_amount

    def test_to_dict(self, invoice):
        invoice_dict = invoice.to_dict()

        assert isinstance(invoice_dict, dict)
        assert invoice_dict['title'] == invoice.title
        assert invoice_dict['description'] == invoice.description
        assert invoice_dict['start_parameter'] == invoice.start_parameter
        assert invoice_dict['currency'] == invoice.currency
        assert invoice_dict['total_amount'] == invoice.total_amount

    @flaky(3, 1)
    def test_send_required_args_only(self, bot, chat_id, provider_token):
        message = bot.send_invoice(
            chat_id=chat_id,
            title=self.title,
            description=self.description,
            payload=self.payload,
            provider_token=provider_token,
            currency=self.currency,
            prices=self.prices,
        )

        assert message.invoice.currency == self.currency
        assert message.invoice.start_parameter == ''
        assert message.invoice.description == self.description
        assert message.invoice.title == self.title
        assert message.invoice.total_amount == self.total_amount

    @flaky(3, 1)
    def test_send_all_args(self, bot, chat_id, provider_token, monkeypatch):
        message = bot.send_invoice(
            chat_id,
            self.title,
            self.description,
            self.payload,
            provider_token,
            self.currency,
            self.prices,
            max_tip_amount=self.max_tip_amount,
            suggested_tip_amounts=self.suggested_tip_amounts,
            start_parameter=self.start_parameter,
            provider_data=self.provider_data,
            photo_url='https://raw.githubusercontent.com/'
            'python-telegram-bot/logos/master/'
            'logo/png/ptb-logo_240.png',
            photo_size=240,
            photo_width=240,
            photo_height=240,
            need_name=True,
            need_phone_number=True,
            need_email=True,
            need_shipping_address=True,
            send_phone_number_to_provider=True,
            send_email_to_provider=True,
            is_flexible=True,
        )

        assert message.invoice.currency == self.currency
        assert message.invoice.start_parameter == self.start_parameter
        assert message.invoice.description == self.description
        assert message.invoice.title == self.title
        assert message.invoice.total_amount == self.total_amount

        # We do this next one as safety guard to make sure that we pass all of the optional
        # parameters correctly because #2526 went unnoticed for 3 years …
        def make_assertion(*args, **_):
            kwargs = args[1]
            return (
                kwargs['chat_id'] == 'chat_id'
                and kwargs['title'] == 'title'
                and kwargs['description'] == 'description'
                and kwargs['payload'] == 'payload'
                and kwargs['provider_token'] == 'provider_token'
                and kwargs['currency'] == 'currency'
                and kwargs['prices'] == [p.to_dict() for p in self.prices]
                and kwargs['max_tip_amount'] == 'max_tip_amount'
                and kwargs['suggested_tip_amounts'] == 'suggested_tip_amounts'
                and kwargs['start_parameter'] == 'start_parameter'
                and kwargs['provider_data'] == 'provider_data'
                and kwargs['photo_url'] == 'photo_url'
                and kwargs['photo_size'] == 'photo_size'
                and kwargs['photo_width'] == 'photo_width'
                and kwargs['photo_height'] == 'photo_height'
                and kwargs['need_name'] == 'need_name'
                and kwargs['need_phone_number'] == 'need_phone_number'
                and kwargs['need_email'] == 'need_email'
                and kwargs['need_shipping_address'] == 'need_shipping_address'
                and kwargs['send_phone_number_to_provider'] == 'send_phone_number_to_provider'
                and kwargs['send_email_to_provider'] == 'send_email_to_provider'
                and kwargs['is_flexible'] == 'is_flexible'
            )

        monkeypatch.setattr(bot, '_message', make_assertion)
        assert bot.send_invoice(
            chat_id='chat_id',
            title='title',
            description='description',
            payload='payload',
            provider_token='provider_token',
            currency='currency',
            prices=self.prices,
            max_tip_amount='max_tip_amount',
            suggested_tip_amounts='suggested_tip_amounts',
            start_parameter='start_parameter',
            provider_data='provider_data',
            photo_url='photo_url',
            photo_size='photo_size',
            photo_width='photo_width',
            photo_height='photo_height',
            need_name='need_name',
            need_phone_number='need_phone_number',
            need_email='need_email',
            need_shipping_address='need_shipping_address',
            send_phone_number_to_provider='send_phone_number_to_provider',
            send_email_to_provider='send_email_to_provider',
            is_flexible='is_flexible',
        )

    def test_send_object_as_provider_data(self, monkeypatch, bot, chat_id, provider_token):
        def test(url, data, **kwargs):
            # depends on whether we're using ujson
            return data['provider_data'] in ['{"test_data": 123456789}', '{"test_data":123456789}']

        monkeypatch.setattr(bot.request, 'post', test)

        assert bot.send_invoice(
            chat_id,
            self.title,
            self.description,
            self.payload,
            provider_token,
            self.currency,
            self.prices,
            provider_data={'test_data': 123456789},
            start_parameter=self.start_parameter,
        )

    @flaky(3, 1)
    @pytest.mark.parametrize(
        'default_bot,custom',
        [
            ({'allow_sending_without_reply': True}, None),
            ({'allow_sending_without_reply': False}, None),
            ({'allow_sending_without_reply': False}, True),
        ],
        indirect=['default_bot'],
    )
    def test_send_invoice_default_allow_sending_without_reply(
        self, default_bot, chat_id, custom, provider_token
    ):
        reply_to_message = default_bot.send_message(chat_id, 'test')
        reply_to_message.delete()
        if custom is not None:
            message = default_bot.send_invoice(
                chat_id,
                self.title,
                self.description,
                self.payload,
                provider_token,
                self.currency,
                self.prices,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = default_bot.send_invoice(
                chat_id,
                self.title,
                self.description,
                self.payload,
                provider_token,
                self.currency,
                self.prices,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match='message not found'):
                default_bot.send_invoice(
                    chat_id,
                    self.title,
                    self.description,
                    self.payload,
                    provider_token,
                    self.currency,
                    self.prices,
                    reply_to_message_id=reply_to_message.message_id,
                )

    def test_equality(self):
        a = Invoice('invoice', 'desc', 'start', 'EUR', 7)
        b = Invoice('invoice', 'desc', 'start', 'EUR', 7)
        c = Invoice('invoices', 'description', 'stop', 'USD', 8)
        d = LabeledPrice('label', 5)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
