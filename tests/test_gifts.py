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
from collections.abc import Sequence

import pytest

from telegram import BotCommand, Gift, Gifts, MessageEntity, Sticker
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.request import RequestData
from tests.auxil.slots import mro_slots


@pytest.fixture
def gift(request):
    return Gift(
        id=GiftTestBase.id,
        sticker=GiftTestBase.sticker,
        star_count=GiftTestBase.star_count,
        total_count=GiftTestBase.total_count,
        remaining_count=GiftTestBase.remaining_count,
        upgrade_star_count=GiftTestBase.upgrade_star_count,
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
    upgrade_star_count = 10


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
            "upgrade_star_count": self.upgrade_star_count,
        }
        gift = Gift.de_json(json_dict, offline_bot)
        assert gift.api_kwargs == {}

        assert gift.id == self.id
        assert gift.sticker == self.sticker
        assert gift.star_count == self.star_count
        assert gift.total_count == self.total_count
        assert gift.remaining_count == self.remaining_count
        assert gift.upgrade_star_count == self.upgrade_star_count

    def test_to_dict(self, gift):
        gift_dict = gift.to_dict()

        assert isinstance(gift_dict, dict)
        assert gift_dict["id"] == self.id
        assert gift_dict["sticker"] == self.sticker.to_dict()
        assert gift_dict["star_count"] == self.star_count
        assert gift_dict["total_count"] == self.total_count
        assert gift_dict["remaining_count"] == self.remaining_count
        assert gift_dict["upgrade_star_count"] == self.upgrade_star_count

    def test_equality(self, gift):
        a = gift
        b = Gift(
            self.id,
            self.sticker,
            self.star_count,
            self.total_count,
            self.remaining_count,
            self.upgrade_star_count,
        )
        c = Gift(
            "other_uid",
            self.sticker,
            self.star_count,
            self.total_count,
            self.remaining_count,
            self.upgrade_star_count,
        )
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

    @pytest.mark.parametrize(
        "gift",
        [
            "gift_id",
            Gift(
                "gift_id",
                Sticker("file_id", "file_unique_id", 512, 512, False, False, "regular"),
                5,
                10,
                5,
                10,
            ),
        ],
        ids=["string", "Gift"],
    )
    async def test_send_gift(self, offline_bot, gift, monkeypatch):
        # We can't send actual gifts, so we just check that the correct parameters are passed
        text_entities = [
            MessageEntity(MessageEntity.TEXT_LINK, 0, 4, "url"),
            MessageEntity(MessageEntity.BOLD, 5, 9),
        ]

        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            user_id = request_data.parameters["user_id"] == "user_id"
            gift_id = request_data.parameters["gift_id"] == "gift_id"
            text = request_data.parameters["text"] == "text"
            text_parse_mode = request_data.parameters["text_parse_mode"] == "text_parse_mode"
            tes = request_data.parameters["text_entities"] == [
                me.to_dict() for me in text_entities
            ]
            pay_for_upgrade = request_data.parameters["pay_for_upgrade"] is True

            return user_id and gift_id and text and text_parse_mode and tes and pay_for_upgrade

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.send_gift(
            "user_id",
            gift,
            "text",
            text_parse_mode="text_parse_mode",
            text_entities=text_entities,
            pay_for_upgrade=True,
        )

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    @pytest.mark.parametrize(
        ("passed_value", "expected_value"),
        [(DEFAULT_NONE, "Markdown"), ("HTML", "HTML"), (None, None)],
    )
    async def test_send_gift_default_parse_mode(
        self, default_bot, monkeypatch, passed_value, expected_value
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters.get("text_parse_mode") == expected_value

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        kwargs = {
            "user_id": "user_id",
            "gift_id": "gift_id",
        }
        if passed_value is not DEFAULT_NONE:
            kwargs["text_parse_mode"] = passed_value

        assert await default_bot.send_gift(**kwargs)


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
            upgrade_star_count=5,
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
            upgrade_star_count=6,
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
            upgrade_star_count=7,
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
            assert de_json_gift.upgrade_star_count == original_gift.upgrade_star_count

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


class TestGiftsWithRequest(GiftTestBase):
    async def test_get_available_gifts(self, bot, chat_id):
        # We don't control the available gifts, so we can not make any better assertions
        assert isinstance(await bot.get_available_gifts(), Gifts)
