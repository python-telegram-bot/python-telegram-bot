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
import datetime as dtm

import pytest

from telegram import (
    Dice,
    RevenueWithdrawalState,
    RevenueWithdrawalStateFailed,
    RevenueWithdrawalStatePending,
    RevenueWithdrawalStateSucceeded,
)
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import RevenueWithdrawalStateType
from tests.auxil.slots import mro_slots


@pytest.fixture
def revenue_withdrawal_state():
    return RevenueWithdrawalState(RevenueWithdrawalStateTestBase.state)


@pytest.fixture
def revenue_withdrawal_state_pending():
    return RevenueWithdrawalStatePending()


@pytest.fixture
def revenue_withdrawal_state_succeeded():
    return RevenueWithdrawalStateSucceeded(
        date=RevenueWithdrawalStateTestBase.date, url=RevenueWithdrawalStateTestBase.url
    )


@pytest.fixture
def revenue_withdrawal_state_failed():
    return RevenueWithdrawalStateFailed()


class RevenueWithdrawalStateTestBase:
    state = "failed"
    date = dtm.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC)
    url = "url"


class TestRevenueWithdrawalStateWithoutRequest(RevenueWithdrawalStateTestBase):
    def test_slot_behaviour(self, revenue_withdrawal_state):
        inst = revenue_withdrawal_state
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self):
        assert type(RevenueWithdrawalState("failed").type) is RevenueWithdrawalStateType
        assert RevenueWithdrawalState("unknown").type == "unknown"

    def test_de_json(self, offline_bot):
        json_dict = {"type": "unknown"}
        rws = RevenueWithdrawalState.de_json(json_dict, offline_bot)
        assert rws.api_kwargs == {}
        assert rws.type == "unknown"

    @pytest.mark.parametrize(
        ("state", "subclass"),
        [
            ("pending", RevenueWithdrawalStatePending),
            ("succeeded", RevenueWithdrawalStateSucceeded),
            ("failed", RevenueWithdrawalStateFailed),
        ],
    )
    def test_de_json_subclass(self, offline_bot, state, subclass):
        json_dict = {"type": state, "date": to_timestamp(self.date), "url": self.url}
        rws = RevenueWithdrawalState.de_json(json_dict, offline_bot)

        assert type(rws) is subclass
        assert set(rws.api_kwargs.keys()) == {"date", "url"} - set(subclass.__slots__)
        assert rws.type == state

    def test_to_dict(self, revenue_withdrawal_state):
        json_dict = revenue_withdrawal_state.to_dict()
        assert json_dict == {"type": self.state}

    def test_equality(self, revenue_withdrawal_state):
        a = revenue_withdrawal_state
        b = RevenueWithdrawalState(self.state)
        c = RevenueWithdrawalState("pending")
        d = Dice(value=1, emoji="🎲")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


class TestRevenueWithdrawalStatePendingWithoutRequest(RevenueWithdrawalStateTestBase):
    def test_slot_behaviour(self, revenue_withdrawal_state_pending):
        inst = revenue_withdrawal_state_pending
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {}
        rws = RevenueWithdrawalStatePending.de_json(json_dict, offline_bot)
        assert rws.api_kwargs == {}
        assert rws.type == "pending"

    def test_to_dict(self, revenue_withdrawal_state_pending):
        json_dict = revenue_withdrawal_state_pending.to_dict()
        assert json_dict == {"type": "pending"}

    def test_equality(self, revenue_withdrawal_state_pending):
        a = revenue_withdrawal_state_pending
        b = RevenueWithdrawalStatePending()
        c = RevenueWithdrawalState("unknown")
        d = Dice(value=1, emoji="🎲")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


class TestRevenueWithdrawalStateSucceededWithoutRequest(RevenueWithdrawalStateTestBase):
    state = RevenueWithdrawalStateType.SUCCEEDED

    def test_slot_behaviour(self, revenue_withdrawal_state_succeeded):
        inst = revenue_withdrawal_state_succeeded
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"date": to_timestamp(self.date), "url": self.url}
        rws = RevenueWithdrawalStateSucceeded.de_json(json_dict, offline_bot)
        assert rws.api_kwargs == {}
        assert rws.type == "succeeded"
        assert rws.date == self.date
        assert rws.url == self.url

    def test_to_dict(self, revenue_withdrawal_state_succeeded):
        json_dict = revenue_withdrawal_state_succeeded.to_dict()
        assert json_dict["type"] == "succeeded"
        assert json_dict["date"] == to_timestamp(self.date)
        assert json_dict["url"] == self.url

    def test_equality(self, revenue_withdrawal_state_succeeded):
        a = revenue_withdrawal_state_succeeded
        b = RevenueWithdrawalStateSucceeded(date=self.date, url=self.url)
        c = RevenueWithdrawalStateSucceeded(date=self.date, url="other_url")
        d = RevenueWithdrawalStateSucceeded(
            date=dtm.datetime(1900, 1, 1, 0, 0, 0, 0, tzinfo=UTC), url=self.url
        )
        e = Dice(value=1, emoji="🎲")

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


class TestRevenueWithdrawalStateFailedWithoutRequest(RevenueWithdrawalStateTestBase):
    state = RevenueWithdrawalStateType.FAILED

    def test_slot_behaviour(self, revenue_withdrawal_state_failed):
        inst = revenue_withdrawal_state_failed
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {}
        rws = RevenueWithdrawalStateFailed.de_json(json_dict, offline_bot)
        assert rws.api_kwargs == {}
        assert rws.type == "failed"

    def test_to_dict(self, revenue_withdrawal_state_failed):
        json_dict = revenue_withdrawal_state_failed.to_dict()
        assert json_dict == {"type": "failed"}

    def test_equality(self, revenue_withdrawal_state_failed):
        a = revenue_withdrawal_state_failed
        b = RevenueWithdrawalStateFailed()
        c = RevenueWithdrawalState("unknown")
        d = Dice(value=1, emoji="🎲")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
