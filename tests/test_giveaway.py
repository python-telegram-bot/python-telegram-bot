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

import datetime as dtm

import pytest

from telegram import (
    BotCommand,
    Chat,
    Giveaway,
    GiveawayCompleted,
    GiveawayCreated,
    GiveawayWinners,
    Message,
    User,
)
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def giveaway():
    return Giveaway(
        chats=[Chat(1, Chat.CHANNEL), Chat(2, Chat.SUPERGROUP)],
        winners_selection_date=TestGiveawayWithoutRequest.winners_selection_date,
        winner_count=TestGiveawayWithoutRequest.winner_count,
        only_new_members=TestGiveawayWithoutRequest.only_new_members,
        has_public_winners=TestGiveawayWithoutRequest.has_public_winners,
        prize_description=TestGiveawayWithoutRequest.prize_description,
        country_codes=TestGiveawayWithoutRequest.country_codes,
        premium_subscription_month_count=(
            TestGiveawayWithoutRequest.premium_subscription_month_count
        ),
    )


class TestGiveawayWithoutRequest:
    chats = [Chat(1, Chat.CHANNEL), Chat(2, Chat.SUPERGROUP)]
    winners_selection_date = dtm.datetime.now(dtm.timezone.utc).replace(microsecond=0)
    winner_count = 42
    only_new_members = True
    has_public_winners = True
    prize_description = "prize_description"
    country_codes = ["DE", "US"]
    premium_subscription_month_count = 3

    def test_slot_behaviour(self, giveaway):
        for attr in giveaway.__slots__:
            assert getattr(giveaway, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(giveaway)) == len(set(mro_slots(giveaway))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "chats": [chat.to_dict() for chat in self.chats],
            "winners_selection_date": to_timestamp(self.winners_selection_date),
            "winner_count": self.winner_count,
            "only_new_members": self.only_new_members,
            "has_public_winners": self.has_public_winners,
            "prize_description": self.prize_description,
            "country_codes": self.country_codes,
            "premium_subscription_month_count": self.premium_subscription_month_count,
        }

        giveaway = Giveaway.de_json(json_dict, bot)
        assert giveaway.api_kwargs == {}

        assert giveaway.chats == tuple(self.chats)
        assert giveaway.winners_selection_date == self.winners_selection_date
        assert giveaway.winner_count == self.winner_count
        assert giveaway.only_new_members == self.only_new_members
        assert giveaway.has_public_winners == self.has_public_winners
        assert giveaway.prize_description == self.prize_description
        assert giveaway.country_codes == tuple(self.country_codes)
        assert giveaway.premium_subscription_month_count == self.premium_subscription_month_count

        assert Giveaway.de_json(None, bot) is None

    def test_de_json_localization(self, tz_bot, bot, raw_bot):
        json_dict = {
            "chats": [chat.to_dict() for chat in self.chats],
            "winners_selection_date": to_timestamp(self.winners_selection_date),
            "winner_count": self.winner_count,
            "only_new_members": self.only_new_members,
            "has_public_winners": self.has_public_winners,
            "prize_description": self.prize_description,
            "country_codes": self.country_codes,
            "premium_subscription_month_count": self.premium_subscription_month_count,
        }

        giveaway_raw = Giveaway.de_json(json_dict, raw_bot)
        giveaway_bot = Giveaway.de_json(json_dict, bot)
        giveaway_bot_tz = Giveaway.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        giveaway_bot_tz_offset = giveaway_bot_tz.winners_selection_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            giveaway_bot_tz.winners_selection_date.replace(tzinfo=None)
        )

        assert giveaway_raw.winners_selection_date.tzinfo == UTC
        assert giveaway_bot.winners_selection_date.tzinfo == UTC
        assert giveaway_bot_tz_offset == tz_bot_offset

    def test_to_dict(self, giveaway):
        giveaway_dict = giveaway.to_dict()

        assert isinstance(giveaway_dict, dict)
        assert giveaway_dict["chats"] == [chat.to_dict() for chat in self.chats]
        assert giveaway_dict["winners_selection_date"] == to_timestamp(self.winners_selection_date)
        assert giveaway_dict["winner_count"] == self.winner_count
        assert giveaway_dict["only_new_members"] == self.only_new_members
        assert giveaway_dict["has_public_winners"] == self.has_public_winners
        assert giveaway_dict["prize_description"] == self.prize_description
        assert giveaway_dict["country_codes"] == self.country_codes
        assert (
            giveaway_dict["premium_subscription_month_count"]
            == self.premium_subscription_month_count
        )

    def test_equality(self, giveaway):
        a = giveaway
        b = Giveaway(
            chats=self.chats,
            winners_selection_date=self.winners_selection_date,
            winner_count=self.winner_count,
        )
        c = Giveaway(
            chats=self.chats,
            winners_selection_date=self.winners_selection_date + dtm.timedelta(seconds=100),
            winner_count=self.winner_count,
        )
        d = Giveaway(
            chats=self.chats, winners_selection_date=self.winners_selection_date, winner_count=17
        )
        e = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


class TestGiveawayCreatedWithoutRequest:
    def test_slot_behaviour(self):
        giveaway_created = GiveawayCreated()
        for attr in giveaway_created.__slots__:
            assert getattr(giveaway_created, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(giveaway_created)) == len(
            set(mro_slots(giveaway_created))
        ), "duplicate slot"


@pytest.fixture(scope="module")
def giveaway_winners():
    return GiveawayWinners(
        chat=TestGiveawayWinnersWithoutRequest.chat,
        giveaway_message_id=TestGiveawayWinnersWithoutRequest.giveaway_message_id,
        winners_selection_date=TestGiveawayWinnersWithoutRequest.winners_selection_date,
        winner_count=TestGiveawayWinnersWithoutRequest.winner_count,
        winners=TestGiveawayWinnersWithoutRequest.winners,
        only_new_members=TestGiveawayWinnersWithoutRequest.only_new_members,
        prize_description=TestGiveawayWinnersWithoutRequest.prize_description,
        premium_subscription_month_count=(
            TestGiveawayWinnersWithoutRequest.premium_subscription_month_count
        ),
        additional_chat_count=TestGiveawayWinnersWithoutRequest.additional_chat_count,
        unclaimed_prize_count=TestGiveawayWinnersWithoutRequest.unclaimed_prize_count,
        was_refunded=TestGiveawayWinnersWithoutRequest.was_refunded,
    )


class TestGiveawayWinnersWithoutRequest:
    chat = Chat(1, Chat.CHANNEL)
    giveaway_message_id = 123456789
    winners_selection_date = dtm.datetime.now(dtm.timezone.utc).replace(microsecond=0)
    winner_count = 42
    winners = [User(1, "user1", False), User(2, "user2", False)]
    additional_chat_count = 2
    premium_subscription_month_count = 3
    unclaimed_prize_count = 4
    only_new_members = True
    was_refunded = True
    prize_description = "prize_description"

    def test_slot_behaviour(self, giveaway_winners):
        for attr in giveaway_winners.__slots__:
            assert getattr(giveaway_winners, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(giveaway_winners)) == len(
            set(mro_slots(giveaway_winners))
        ), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "chat": self.chat.to_dict(),
            "giveaway_message_id": self.giveaway_message_id,
            "winners_selection_date": to_timestamp(self.winners_selection_date),
            "winner_count": self.winner_count,
            "winners": [winner.to_dict() for winner in self.winners],
            "additional_chat_count": self.additional_chat_count,
            "premium_subscription_month_count": self.premium_subscription_month_count,
            "unclaimed_prize_count": self.unclaimed_prize_count,
            "only_new_members": self.only_new_members,
            "was_refunded": self.was_refunded,
            "prize_description": self.prize_description,
        }

        giveaway_winners = GiveawayWinners.de_json(json_dict, bot)
        assert giveaway_winners.api_kwargs == {}

        assert giveaway_winners.chat == self.chat
        assert giveaway_winners.giveaway_message_id == self.giveaway_message_id
        assert giveaway_winners.winners_selection_date == self.winners_selection_date
        assert giveaway_winners.winner_count == self.winner_count
        assert giveaway_winners.winners == tuple(self.winners)
        assert giveaway_winners.additional_chat_count == self.additional_chat_count
        assert (
            giveaway_winners.premium_subscription_month_count
            == self.premium_subscription_month_count
        )
        assert giveaway_winners.unclaimed_prize_count == self.unclaimed_prize_count
        assert giveaway_winners.only_new_members == self.only_new_members
        assert giveaway_winners.was_refunded == self.was_refunded
        assert giveaway_winners.prize_description == self.prize_description

        assert GiveawayWinners.de_json(None, bot) is None

    def test_de_json_localization(self, tz_bot, bot, raw_bot):
        json_dict = {
            "chat": self.chat.to_dict(),
            "giveaway_message_id": self.giveaway_message_id,
            "winners_selection_date": to_timestamp(self.winners_selection_date),
            "winner_count": self.winner_count,
            "winners": [winner.to_dict() for winner in self.winners],
        }

        giveaway_winners_raw = GiveawayWinners.de_json(json_dict, raw_bot)
        giveaway_winners_bot = GiveawayWinners.de_json(json_dict, bot)
        giveaway_winners_bot_tz = GiveawayWinners.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        giveaway_winners_bot_tz_offset = giveaway_winners_bot_tz.winners_selection_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            giveaway_winners_bot_tz.winners_selection_date.replace(tzinfo=None)
        )

        assert giveaway_winners_raw.winners_selection_date.tzinfo == UTC
        assert giveaway_winners_bot.winners_selection_date.tzinfo == UTC
        assert giveaway_winners_bot_tz_offset == tz_bot_offset

    def test_to_dict(self, giveaway_winners):
        giveaway_winners_dict = giveaway_winners.to_dict()

        assert isinstance(giveaway_winners_dict, dict)
        assert giveaway_winners_dict["chat"] == self.chat.to_dict()
        assert giveaway_winners_dict["giveaway_message_id"] == self.giveaway_message_id
        assert giveaway_winners_dict["winners_selection_date"] == to_timestamp(
            self.winners_selection_date
        )
        assert giveaway_winners_dict["winner_count"] == self.winner_count
        assert giveaway_winners_dict["winners"] == [winner.to_dict() for winner in self.winners]
        assert giveaway_winners_dict["additional_chat_count"] == self.additional_chat_count
        assert (
            giveaway_winners_dict["premium_subscription_month_count"]
            == self.premium_subscription_month_count
        )
        assert giveaway_winners_dict["unclaimed_prize_count"] == self.unclaimed_prize_count
        assert giveaway_winners_dict["only_new_members"] == self.only_new_members
        assert giveaway_winners_dict["was_refunded"] == self.was_refunded
        assert giveaway_winners_dict["prize_description"] == self.prize_description

    def test_equality(self, giveaway_winners):
        a = giveaway_winners
        b = GiveawayWinners(
            chat=self.chat,
            giveaway_message_id=self.giveaway_message_id,
            winners_selection_date=self.winners_selection_date,
            winner_count=self.winner_count,
            winners=self.winners,
        )
        c = GiveawayWinners(
            chat=self.chat,
            giveaway_message_id=self.giveaway_message_id,
            winners_selection_date=self.winners_selection_date + dtm.timedelta(seconds=100),
            winner_count=self.winner_count,
            winners=self.winners,
        )
        d = GiveawayWinners(
            chat=self.chat,
            giveaway_message_id=self.giveaway_message_id,
            winners_selection_date=self.winners_selection_date,
            winner_count=17,
            winners=self.winners,
        )
        e = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def giveaway_completed():
    return GiveawayCompleted(
        winner_count=TestGiveawayCompletedWithoutRequest.winner_count,
        unclaimed_prize_count=TestGiveawayCompletedWithoutRequest.unclaimed_prize_count,
        giveaway_message=TestGiveawayCompletedWithoutRequest.giveaway_message,
    )


class TestGiveawayCompletedWithoutRequest:
    winner_count = 42
    unclaimed_prize_count = 4
    giveaway_message = Message(
        message_id=1,
        date=dtm.datetime.now(dtm.timezone.utc),
        text="giveaway_message",
        chat=Chat(1, Chat.CHANNEL),
        from_user=User(1, "user1", False),
    )

    def test_slot_behaviour(self, giveaway_completed):
        for attr in giveaway_completed.__slots__:
            assert getattr(giveaway_completed, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(giveaway_completed)) == len(
            set(mro_slots(giveaway_completed))
        ), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "winner_count": self.winner_count,
            "unclaimed_prize_count": self.unclaimed_prize_count,
            "giveaway_message": self.giveaway_message.to_dict(),
        }

        giveaway_completed = GiveawayCompleted.de_json(json_dict, bot)
        assert giveaway_completed.api_kwargs == {}

        assert giveaway_completed.winner_count == self.winner_count
        assert giveaway_completed.unclaimed_prize_count == self.unclaimed_prize_count
        assert giveaway_completed.giveaway_message == self.giveaway_message

        assert GiveawayCompleted.de_json(None, bot) is None

    def test_to_dict(self, giveaway_completed):
        giveaway_completed_dict = giveaway_completed.to_dict()

        assert isinstance(giveaway_completed_dict, dict)
        assert giveaway_completed_dict["winner_count"] == self.winner_count
        assert giveaway_completed_dict["unclaimed_prize_count"] == self.unclaimed_prize_count
        assert giveaway_completed_dict["giveaway_message"] == self.giveaway_message.to_dict()

    def test_equality(self, giveaway_completed):
        a = giveaway_completed
        b = GiveawayCompleted(
            winner_count=self.winner_count,
            unclaimed_prize_count=self.unclaimed_prize_count,
            giveaway_message=self.giveaway_message,
        )
        c = GiveawayCompleted(
            winner_count=self.winner_count + 30,
            unclaimed_prize_count=self.unclaimed_prize_count,
        )
        d = GiveawayCompleted(
            winner_count=self.winner_count,
            unclaimed_prize_count=17,
            giveaway_message=self.giveaway_message,
        )
        e = GiveawayCompleted(
            winner_count=self.winner_count + 1,
            unclaimed_prize_count=self.unclaimed_prize_count,
        )
        f = BotCommand("start", "description")

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
