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
from collections.abc import Sequence

import pytest

from telegram import BotCommand, Gift, Gifts, Sticker
from tests.auxil.slots import mro_slots


@pytest.fixture
def gift(request):
    return Gift(
        id=GiftTestBase.id,
        sticker=GiftTestBase.sticker,
        star_count=GiftTestBase.star_count,
        total_count=GiftTestBase.total_count,
        remaining_count=GiftTestBase.remaining_count,
    )


class GiftTestBase:
    id = "some_id"
    sticker = Sticker(
        file_id="file_id",
        file_unique_id="file_unique_id",
        width=512,
        height=512,
        is_animated=False,
        is_video=False,
        type="regular",
    )
    star_count = 5
    total_count = 10
    remaining_count = 5


class TestGiftWithoutRequest(GiftTestBase):
    def test_slot_behaviour(self, gift):
        for attr in gift.__slots__:
            assert getattr(gift, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(gift)) == len(set(mro_slots(gift))), "duplicate slot"

    def test_de_json(self, offline_bot, gift):
        json_dict = {
            "id": self.id,
            "sticker": self.sticker.to_dict(),
            "star_count": self.star_count,
            "total_count": self.total_count,
            "remaining_count": self.remaining_count,
        }
        gift = Gift.de_json(json_dict, offline_bot)
        assert gift.api_kwargs == {}

        assert gift.id == self.id
        assert gift.sticker == self.sticker
        assert gift.star_count == self.star_count
        assert gift.total_count == self.total_count
        assert gift.remaining_count == self.remaining_count

        assert Gift.de_json(None, offline_bot) is None

    def test_to_dict(self, gift):
        gift_dict = gift.to_dict()

        assert isinstance(gift_dict, dict)
        assert gift_dict["id"] == self.id
        assert gift_dict["sticker"] == self.sticker.to_dict()
        assert gift_dict["star_count"] == self.star_count
        assert gift_dict["total_count"] == self.total_count
        assert gift_dict["remaining_count"] == self.remaining_count

    def test_equality(self, gift):
        a = gift
        b = Gift(self.id, self.sticker, self.star_count, self.total_count, self.remaining_count)
        c = Gift(
            "other_uid", self.sticker, self.star_count, self.total_count, self.remaining_count
        )
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def gifts(request):
    return Gifts(gifts=GiftsTestBase.gifts)


class GiftsTestBase:
    gifts: Sequence[Gift] = [
        Gift(
            id="id1",
            sticker=Sticker(
                file_id="file_id",
                file_unique_id="file_unique_id",
                width=512,
                height=512,
                is_animated=False,
                is_video=False,
                type="regular",
            ),
            star_count=5,
            total_count=5,
            remaining_count=5,
        ),
        Gift(
            id="id2",
            sticker=Sticker(
                file_id="file_id",
                file_unique_id="file_unique_id",
                width=512,
                height=512,
                is_animated=False,
                is_video=False,
                type="regular",
            ),
            star_count=6,
            total_count=6,
            remaining_count=6,
        ),
        Gift(
            id="id3",
            sticker=Sticker(
                file_id="file_id",
                file_unique_id="file_unique_id",
                width=512,
                height=512,
                is_animated=False,
                is_video=False,
                type="regular",
            ),
            star_count=7,
            total_count=7,
            remaining_count=7,
        ),
    ]


class TestGiftsWithoutRequest(GiftsTestBase):
    def test_slot_behaviour(self, gifts):
        for attr in gifts.__slots__:
            assert getattr(gifts, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(gifts)) == len(set(mro_slots(gifts))), "duplicate slot"

    def test_de_json(self, offline_bot, gifts):
        json_dict = {"gifts": [gift.to_dict() for gift in self.gifts]}
        gifts = Gifts.de_json(json_dict, offline_bot)
        assert gifts.api_kwargs == {}

        assert gifts.gifts == tuple(self.gifts)
        for de_json_gift, original_gift in zip(gifts.gifts, self.gifts):
            assert de_json_gift.id == original_gift.id
            assert de_json_gift.sticker == original_gift.sticker
            assert de_json_gift.star_count == original_gift.star_count
            assert de_json_gift.total_count == original_gift.total_count
            assert de_json_gift.remaining_count == original_gift.remaining_count

        assert Gifts.de_json(None, offline_bot) is None

    def test_to_dict(self, gifts):
        gifts_dict = gifts.to_dict()

        assert isinstance(gifts_dict, dict)
        assert gifts_dict["gifts"] == [gift.to_dict() for gift in self.gifts]

    def test_equality(self, gifts):
        a = gifts
        b = Gifts(self.gifts)
        c = Gifts(self.gifts[:2])
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
