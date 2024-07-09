#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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

from telegram import RefundedPayment
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def refunded_payment():
    return RefundedPayment(
        TestRefundedPaymentBase.currency,
        TestRefundedPaymentBase.total_amount,
        TestRefundedPaymentBase.invoice_payload,
        TestRefundedPaymentBase.telegram_payment_charge_id,
        TestRefundedPaymentBase.provider_payment_charge_id,
    )


class TestRefundedPaymentBase:
    invoice_payload = "invoice_payload"
    currency = "EUR"
    total_amount = 100
    telegram_payment_charge_id = "telegram_payment_charge_id"
    provider_payment_charge_id = "provider_payment_charge_id"


class TestRefundedPaymentWithoutRequest(TestRefundedPaymentBase):
    def test_slot_behaviour(self, refunded_payment):
        inst = refunded_payment
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "invoice_payload": self.invoice_payload,
            "currency": self.currency,
            "total_amount": self.total_amount,
            "telegram_payment_charge_id": self.telegram_payment_charge_id,
            "provider_payment_charge_id": self.provider_payment_charge_id,
        }
        refunded_payment = RefundedPayment.de_json(json_dict, bot)
        assert refunded_payment.api_kwargs == {}

        assert refunded_payment.invoice_payload == self.invoice_payload
        assert refunded_payment.currency == self.currency
        assert refunded_payment.total_amount == self.total_amount
        assert refunded_payment.telegram_payment_charge_id == self.telegram_payment_charge_id
        assert refunded_payment.provider_payment_charge_id == self.provider_payment_charge_id

    def test_to_dict(self, refunded_payment):
        refunded_payment_dict = refunded_payment.to_dict()

        assert isinstance(refunded_payment_dict, dict)
        assert refunded_payment_dict["invoice_payload"] == refunded_payment.invoice_payload
        assert refunded_payment_dict["currency"] == refunded_payment.currency
        assert refunded_payment_dict["total_amount"] == refunded_payment.total_amount
        assert (
            refunded_payment_dict["telegram_payment_charge_id"]
            == refunded_payment.telegram_payment_charge_id
        )
        assert (
            refunded_payment_dict["provider_payment_charge_id"]
            == refunded_payment.provider_payment_charge_id
        )

    def test_equality(self):
        a = RefundedPayment(
            self.currency,
            self.total_amount,
            self.invoice_payload,
            self.telegram_payment_charge_id,
            self.provider_payment_charge_id,
        )
        b = RefundedPayment(
            self.currency,
            self.total_amount,
            self.invoice_payload,
            self.telegram_payment_charge_id,
            self.provider_payment_charge_id,
        )
        c = RefundedPayment("", 0, "", self.telegram_payment_charge_id)
        d = RefundedPayment(
            self.currency,
            self.total_amount,
            self.invoice_payload,
            "",
        )

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)
