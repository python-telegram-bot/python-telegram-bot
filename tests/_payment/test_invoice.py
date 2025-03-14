#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
import asyncio
import datetime as dtm

import pytest

from telegram import Invoice, LabeledPrice, ReplyParameters
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.request import RequestData
from tests.auxil.build_messages import make_message
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def invoice():
    return Invoice(
        InvoiceTestBase.title,
        InvoiceTestBase.description,
        InvoiceTestBase.start_parameter,
        InvoiceTestBase.currency,
        InvoiceTestBase.total_amount,
    )


class InvoiceTestBase:
    payload = "payload"
    prices = [LabeledPrice("Fish", 100), LabeledPrice("Fish Tax", 1000)]
    provider_data = """{"test":"test"}"""
    title = "title"
    description = "description"
    start_parameter = "start_parameter"
    currency = "EUR"
    total_amount = sum(p.amount for p in prices)
    max_tip_amount = 42
    suggested_tip_amounts = [13, 42]


class TestInvoiceWithoutRequest(InvoiceTestBase):
    def test_slot_behaviour(self, invoice):
        for attr in invoice.__slots__:
            assert getattr(invoice, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(invoice)) == len(set(mro_slots(invoice))), "duplicate slot"

    def test_de_json(self, offline_bot):
        invoice_json = Invoice.de_json(
            {
                "title": self.title,
                "description": self.description,
                "start_parameter": self.start_parameter,
                "currency": self.currency,
                "total_amount": self.total_amount,
            },
            offline_bot,
        )
        assert invoice_json.api_kwargs == {}

        assert invoice_json.title == self.title
        assert invoice_json.description == self.description
        assert invoice_json.start_parameter == self.start_parameter
        assert invoice_json.currency == self.currency
        assert invoice_json.total_amount == self.total_amount

    def test_to_dict(self, invoice):
        invoice_dict = invoice.to_dict()

        assert isinstance(invoice_dict, dict)
        assert invoice_dict["title"] == invoice.title
        assert invoice_dict["description"] == invoice.description
        assert invoice_dict["start_parameter"] == invoice.start_parameter
        assert invoice_dict["currency"] == invoice.currency
        assert invoice_dict["total_amount"] == invoice.total_amount

    async def test_send_invoice_all_args_mock(self, offline_bot, monkeypatch):
        # We do this one as safety guard to make sure that we pass all of the optional
        # parameters correctly because #2526 went unnoticed for 3 years …
        async def make_assertion(*args, **_):
            kwargs = args[1]
            return all(kwargs[key] == key for key in kwargs)

        monkeypatch.setattr(offline_bot, "_send_message", make_assertion)
        assert await offline_bot.send_invoice(
            chat_id="chat_id",
            title="title",
            description="description",
            payload="payload",
            provider_token="provider_token",
            currency="currency",
            prices="prices",
            max_tip_amount="max_tip_amount",
            suggested_tip_amounts="suggested_tip_amounts",
            start_parameter="start_parameter",
            provider_data="provider_data",
            photo_url="photo_url",
            photo_size="photo_size",
            photo_width="photo_width",
            photo_height="photo_height",
            need_name="need_name",
            need_phone_number="need_phone_number",
            need_email="need_email",
            need_shipping_address="need_shipping_address",
            send_phone_number_to_provider="send_phone_number_to_provider",
            send_email_to_provider="send_email_to_provider",
            is_flexible="is_flexible",
            disable_notification=True,
            protect_content=True,
        )

    @pytest.mark.parametrize("subscription_period", [42, dtm.timedelta(seconds=42)])
    async def test_send_all_args_create_invoice_link(
        self, offline_bot, monkeypatch, subscription_period
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            kwargs = request_data.parameters
            sp = kwargs.pop("subscription_period") == 42
            return all(kwargs[i] == i for i in kwargs) and sp

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.create_invoice_link(
            title="title",
            description="description",
            payload="payload",
            provider_token="provider_token",
            currency="currency",
            prices="prices",
            max_tip_amount="max_tip_amount",
            suggested_tip_amounts="suggested_tip_amounts",
            provider_data="provider_data",
            photo_url="photo_url",
            photo_size="photo_size",
            photo_width="photo_width",
            photo_height="photo_height",
            need_name="need_name",
            need_phone_number="need_phone_number",
            need_email="need_email",
            need_shipping_address="need_shipping_address",
            send_phone_number_to_provider="send_phone_number_to_provider",
            send_email_to_provider="send_email_to_provider",
            is_flexible="is_flexible",
            business_connection_id="business_connection_id",
            subscription_period=subscription_period,
        )

    async def test_send_object_as_provider_data(
        self, monkeypatch, offline_bot, chat_id, provider_token
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters["provider_data"] == '{"test_data": 123456789}'

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)

        assert await offline_bot.send_invoice(
            chat_id,
            self.title,
            self.description,
            self.payload,
            provider_token,
            self.currency,
            self.prices,
            provider_data={"test_data": 123456789},
            start_parameter=self.start_parameter,
        )

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_invoice_default_quote_parse_mode(
        self, default_bot, chat_id, invoice, custom, monkeypatch, provider_token
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            assert request_data.parameters["reply_parameters"].get("quote_parse_mode") == (
                custom or default_bot.defaults.quote_parse_mode
            )
            return make_message("dummy reply").to_dict()

        kwargs = {"message_id": 1}
        if custom is not None:
            kwargs["quote_parse_mode"] = custom

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        await default_bot.send_invoice(
            chat_id,
            self.title,
            self.description,
            self.payload,
            provider_token,
            self.currency,
            self.prices,
            reply_parameters=ReplyParameters(**kwargs),
        )

    def test_equality(self):
        a = Invoice("invoice", "desc", "start", "EUR", 7)
        b = Invoice("invoice", "desc", "start", "EUR", 7)
        c = Invoice("invoices", "description", "stop", "USD", 8)
        d = LabeledPrice("label", 5)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


class TestInvoiceWithRequest(InvoiceTestBase):
    async def test_send_required_args_only(self, bot, chat_id, provider_token):
        message = await bot.send_invoice(
            chat_id=chat_id,
            title=self.title,
            description=self.description,
            payload=self.payload,
            provider_token=provider_token,
            currency=self.currency,
            prices=self.prices,
        )

        assert message.invoice.currency == self.currency
        assert not message.invoice.start_parameter
        assert message.invoice.description == self.description
        assert message.invoice.title == self.title
        assert message.invoice.total_amount == self.total_amount

        link = await bot.create_invoice_link(
            title=self.title,
            description=self.description,
            payload=self.payload,
            provider_token=provider_token,
            currency=self.currency,
            prices=self.prices,
        )

        assert isinstance(link, str)
        assert link

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_invoice_default_protect_content(
        self, chat_id, default_bot, provider_token
    ):
        tasks = asyncio.gather(
            *(
                default_bot.send_invoice(
                    chat_id,
                    self.title,
                    self.description,
                    self.payload,
                    self.currency,
                    self.prices,
                    provider_token,
                    **kwargs,
                )
                for kwargs in ({}, {"protect_content": False})
            )
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_invoice_default_allow_sending_without_reply(
        self, default_bot, chat_id, custom, provider_token
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_invoice(
                chat_id,
                self.title,
                self.description,
                self.payload,
                "XTR",
                [self.prices[0]],
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
            assert message.invoice.currency == "XTR"
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_invoice(
                chat_id,
                self.title,
                self.description,
                self.payload,
                self.currency,
                self.prices,
                provider_token,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to be replied not found"):
                await default_bot.send_invoice(
                    chat_id,
                    self.title,
                    self.description,
                    self.payload,
                    self.currency,
                    self.prices,
                    provider_token,
                    reply_to_message_id=reply_to_message.message_id,
                )

    async def test_send_all_args_send_invoice(self, bot, chat_id, provider_token):
        message = await bot.send_invoice(
            chat_id,
            self.title,
            self.description,
            self.payload,
            self.currency,
            self.prices,
            provider_token=provider_token,
            max_tip_amount=self.max_tip_amount,
            suggested_tip_amounts=self.suggested_tip_amounts,
            start_parameter=self.start_parameter,
            provider_data=self.provider_data,
            photo_url=(
                "https://raw.githubusercontent.com/"
                "python-telegram-bot/logos/master/logo/png/ptb-logo_240.png"
            ),
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
            disable_notification=True,
            protect_content=True,
        )

        for attr in message.invoice.__slots__:
            assert getattr(message.invoice, attr) == getattr(self, attr)
        assert message.has_protected_content
