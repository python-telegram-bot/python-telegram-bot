#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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

from telegram import Bot, ShippingAddress, ShippingQuery, Update, User
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)


@pytest.fixture(scope="module")
def shipping_query(bot):
    sq = ShippingQuery(Space.id_, Space.from_user, Space.invoice_payload, Space.shipping_address)
    sq.set_bot(bot)
    return sq


class Space:
    id_ = "5"
    invoice_payload = "invoice_payload"
    from_user = User(0, "", False)
    shipping_address = ShippingAddress("GB", "", "London", "12 Grimmauld Place", "", "WC1")


class TestShippingQueryWithoutRequest:
    def test_slot_behaviour(self, shipping_query, mro_slots):
        inst = shipping_query
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "id": Space.id_,
            "invoice_payload": Space.invoice_payload,
            "from": Space.from_user.to_dict(),
            "shipping_address": Space.shipping_address.to_dict(),
        }
        shipping_query = ShippingQuery.de_json(json_dict, bot)
        assert shipping_query.api_kwargs == {}

        assert shipping_query.id == Space.id_
        assert shipping_query.invoice_payload == Space.invoice_payload
        assert shipping_query.from_user == Space.from_user
        assert shipping_query.shipping_address == Space.shipping_address
        assert shipping_query.get_bot() is bot

    def test_to_dict(self, shipping_query):
        shipping_query_dict = shipping_query.to_dict()

        assert isinstance(shipping_query_dict, dict)
        assert shipping_query_dict["id"] == shipping_query.id
        assert shipping_query_dict["invoice_payload"] == shipping_query.invoice_payload
        assert shipping_query_dict["from"] == shipping_query.from_user.to_dict()
        assert shipping_query_dict["shipping_address"] == shipping_query.shipping_address.to_dict()

    def test_equality(self):
        a = ShippingQuery(
            Space.id_, Space.from_user, Space.invoice_payload, Space.shipping_address
        )
        b = ShippingQuery(
            Space.id_, Space.from_user, Space.invoice_payload, Space.shipping_address
        )
        c = ShippingQuery(Space.id_, None, "", None)
        d = ShippingQuery(0, Space.from_user, Space.invoice_payload, Space.shipping_address)
        e = Update(Space.id_)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    async def test_answer(self, monkeypatch, shipping_query):
        async def make_assertion(*_, **kwargs):
            return kwargs["shipping_query_id"] == shipping_query.id

        assert check_shortcut_signature(
            ShippingQuery.answer, Bot.answer_shipping_query, ["shipping_query_id"], []
        )
        assert await check_shortcut_call(
            shipping_query.answer, shipping_query._bot, "answer_shipping_query"
        )
        assert await check_defaults_handling(shipping_query.answer, shipping_query._bot)

        monkeypatch.setattr(shipping_query._bot, "answer_shipping_query", make_assertion)
        assert await shipping_query.answer(ok=True)
