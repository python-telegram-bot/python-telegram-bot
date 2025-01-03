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
# along with this program. If not, see [http://www.gnu.org/licenses/].
import pytest

from telegram import AffiliateInfo, Chat, Dice, User
from tests.auxil.slots import mro_slots


@pytest.fixture
def affiliate_info():
    return AffiliateInfo(
        affiliate_user=AffiliateInfoTestBase.affiliate_user,
        affiliate_chat=AffiliateInfoTestBase.affiliate_chat,
        commission_per_mille=AffiliateInfoTestBase.commission_per_mille,
        amount=AffiliateInfoTestBase.amount,
        nanostar_amount=AffiliateInfoTestBase.nanostar_amount,
    )


class AffiliateInfoTestBase:
    affiliate_user = User(id=1, is_bot=True, first_name="affiliate_user", username="username")
    affiliate_chat = Chat(id=2, type="private", title="affiliate_chat")
    commission_per_mille = 13
    amount = 14
    nanostar_amount = -42


class TestAffiliateInfoWithoutRequest(AffiliateInfoTestBase):
    def test_slot_behaviour(self, affiliate_info):
        inst = affiliate_info
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "affiliate_user": self.affiliate_user.to_dict(),
            "affiliate_chat": self.affiliate_chat.to_dict(),
            "commission_per_mille": self.commission_per_mille,
            "amount": self.amount,
            "nanostar_amount": self.nanostar_amount,
        }
        ai = AffiliateInfo.de_json(json_dict, offline_bot)
        assert ai.api_kwargs == {}
        assert ai.affiliate_user == self.affiliate_user
        assert ai.affiliate_chat == self.affiliate_chat
        assert ai.commission_per_mille == self.commission_per_mille
        assert ai.amount == self.amount
        assert ai.nanostar_amount == self.nanostar_amount

    def test_to_dict(self, affiliate_info):
        ai_dict = affiliate_info.to_dict()

        assert isinstance(ai_dict, dict)
        assert ai_dict["affiliate_user"] == affiliate_info.affiliate_user.to_dict()
        assert ai_dict["affiliate_chat"] == affiliate_info.affiliate_chat.to_dict()
        assert ai_dict["commission_per_mille"] == affiliate_info.commission_per_mille
        assert ai_dict["amount"] == affiliate_info.amount
        assert ai_dict["nanostar_amount"] == affiliate_info.nanostar_amount

    def test_equality(self, affiliate_info, offline_bot):
        a = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        b = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        c = AffiliateInfo(
            affiliate_user=User(id=3, is_bot=True, first_name="first_name", username="username"),
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        d = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=Chat(id=3, type="private", title="title"),
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        e = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=1,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        f = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=1,
            nanostar_amount=self.nanostar_amount,
        )
        g = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=1,
        )
        h = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)

        assert a != g
        assert hash(a) != hash(g)

        assert a != h
        assert hash(a) != hash(h)
