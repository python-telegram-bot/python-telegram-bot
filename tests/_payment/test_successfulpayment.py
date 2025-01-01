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
import datetime as dtm

import pytest

from telegram import OrderInfo, SuccessfulPayment
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def successful_payment():
    return SuccessfulPayment(
        SuccessfulPaymentTestBase.currency,
        SuccessfulPaymentTestBase.total_amount,
        SuccessfulPaymentTestBase.invoice_payload,
        SuccessfulPaymentTestBase.telegram_payment_charge_id,
        SuccessfulPaymentTestBase.provider_payment_charge_id,
        shipping_option_id=SuccessfulPaymentTestBase.shipping_option_id,
        order_info=SuccessfulPaymentTestBase.order_info,
        subscription_expiration_date=SuccessfulPaymentTestBase.subscription_expiration_date,
        is_recurring=SuccessfulPaymentTestBase.is_recurring,
        is_first_recurring=SuccessfulPaymentTestBase.is_first_recurring,
    )


class SuccessfulPaymentTestBase:
    invoice_payload = "invoice_payload"
    shipping_option_id = "shipping_option_id"
    currency = "EUR"
    total_amount = 100
    order_info = OrderInfo()
    telegram_payment_charge_id = "telegram_payment_charge_id"
    provider_payment_charge_id = "provider_payment_charge_id"
    subscription_expiration_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)
    is_recurring = True
    is_first_recurring = True


class TestSuccessfulPaymentWithoutRequest(SuccessfulPaymentTestBase):
    def test_slot_behaviour(self, successful_payment):
        inst = successful_payment
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "invoice_payload": self.invoice_payload,
            "shipping_option_id": self.shipping_option_id,
            "currency": self.currency,
            "total_amount": self.total_amount,
            "order_info": self.order_info.to_dict(),
            "telegram_payment_charge_id": self.telegram_payment_charge_id,
            "provider_payment_charge_id": self.provider_payment_charge_id,
            "subscription_expiration_date": to_timestamp(self.subscription_expiration_date),
            "is_recurring": self.is_recurring,
            "is_first_recurring": self.is_first_recurring,
        }
        successful_payment = SuccessfulPayment.de_json(json_dict, offline_bot)
        assert successful_payment.api_kwargs == {}

        assert successful_payment.invoice_payload == self.invoice_payload
        assert successful_payment.shipping_option_id == self.shipping_option_id
        assert successful_payment.currency == self.currency
        assert successful_payment.total_amount == self.total_amount
        assert successful_payment.order_info == self.order_info
        assert successful_payment.telegram_payment_charge_id == self.telegram_payment_charge_id
        assert successful_payment.provider_payment_charge_id == self.provider_payment_charge_id
        assert successful_payment.subscription_expiration_date == self.subscription_expiration_date
        assert successful_payment.is_recurring == self.is_recurring
        assert successful_payment.is_first_recurring == self.is_first_recurring

    def test_de_json_localization(self, offline_bot, raw_bot, tz_bot):
        json_dict = {
            "invoice_payload": self.invoice_payload,
            "currency": self.currency,
            "total_amount": self.total_amount,
            "telegram_payment_charge_id": self.telegram_payment_charge_id,
            "provider_payment_charge_id": self.provider_payment_charge_id,
            "subscription_expiration_date": to_timestamp(self.subscription_expiration_date),
        }
        successful_payment = SuccessfulPayment.de_json(json_dict, offline_bot)
        successful_payment_raw = SuccessfulPayment.de_json(json_dict, raw_bot)
        successful_payment_tz = SuccessfulPayment.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        date_offset = successful_payment_tz.subscription_expiration_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            successful_payment_tz.subscription_expiration_date.replace(tzinfo=None)
        )

        assert successful_payment_raw.subscription_expiration_date.tzinfo == UTC
        assert successful_payment.subscription_expiration_date.tzinfo == UTC
        assert date_offset == tz_bot_offset

    def test_to_dict(self, successful_payment):
        successful_payment_dict = successful_payment.to_dict()

        assert isinstance(successful_payment_dict, dict)
        assert successful_payment_dict["invoice_payload"] == successful_payment.invoice_payload
        assert (
            successful_payment_dict["shipping_option_id"] == successful_payment.shipping_option_id
        )
        assert successful_payment_dict["currency"] == successful_payment.currency
        assert successful_payment_dict["total_amount"] == successful_payment.total_amount
        assert successful_payment_dict["order_info"] == successful_payment.order_info.to_dict()
        assert (
            successful_payment_dict["telegram_payment_charge_id"]
            == successful_payment.telegram_payment_charge_id
        )
        assert (
            successful_payment_dict["provider_payment_charge_id"]
            == successful_payment.provider_payment_charge_id
        )
        assert successful_payment_dict["subscription_expiration_date"] == to_timestamp(
            successful_payment.subscription_expiration_date
        )
        assert successful_payment_dict["is_recurring"] == successful_payment.is_recurring
        assert (
            successful_payment_dict["is_first_recurring"] == successful_payment.is_first_recurring
        )

    def test_equality(self):
        a = SuccessfulPayment(
            self.currency,
            self.total_amount,
            self.invoice_payload,
            self.telegram_payment_charge_id,
            self.provider_payment_charge_id,
        )
        b = SuccessfulPayment(
            self.currency,
            self.total_amount,
            self.invoice_payload,
            self.telegram_payment_charge_id,
            self.provider_payment_charge_id,
        )
        c = SuccessfulPayment(
            "", 0, "", self.telegram_payment_charge_id, self.provider_payment_charge_id
        )
        d = SuccessfulPayment(
            self.currency,
            self.total_amount,
            self.invoice_payload,
            self.telegram_payment_charge_id,
            "",
        )

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)
