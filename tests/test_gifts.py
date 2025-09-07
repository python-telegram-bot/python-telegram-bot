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

from telegram import BotCommand, Chat, Gift, GiftInfo, Gifts, MessageEntity, Sticker
from telegram._gifts import AcceptedGiftTypes
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
        publisher_chat=GiftTestBase.publisher_chat,
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
    publisher_chat = Chat(1, Chat.PRIVATE)


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
            "publisher_chat": self.publisher_chat.to_dict(),
        }
        gift = Gift.de_json(json_dict, offline_bot)
        assert gift.api_kwargs == {}

        assert gift.id == self.id
        assert gift.sticker == self.sticker
        assert gift.star_count == self.star_count
        assert gift.total_count == self.total_count
        assert gift.remaining_count == self.remaining_count
        assert gift.upgrade_star_count == self.upgrade_star_count
        assert gift.publisher_chat == self.publisher_chat

    def test_to_dict(self, gift):
        gift_dict = gift.to_dict()

        assert isinstance(gift_dict, dict)
        assert gift_dict["id"] == self.id
        assert gift_dict["sticker"] == self.sticker.to_dict()
        assert gift_dict["star_count"] == self.star_count
        assert gift_dict["total_count"] == self.total_count
        assert gift_dict["remaining_count"] == self.remaining_count
        assert gift_dict["upgrade_star_count"] == self.upgrade_star_count
        assert gift_dict["publisher_chat"] == self.publisher_chat.to_dict()

    def test_equality(self, gift):
        a = gift
        b = Gift(
            self.id,
            self.sticker,
            self.star_count,
            self.total_count,
            self.remaining_count,
            self.upgrade_star_count,
            self.publisher_chat,
        )
        c = Gift(
            "other_uid",
            self.sticker,
            self.star_count,
            self.total_count,
            self.remaining_count,
            self.upgrade_star_count,
            self.publisher_chat,
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
    @pytest.mark.parametrize("id_name", ["user_id", "chat_id"])
    async def test_send_gift(self, offline_bot, gift, monkeypatch, id_name):
        # We can't send actual gifts, so we just check that the correct parameters are passed
        text_entities = [
            MessageEntity(MessageEntity.TEXT_LINK, 0, 4, "url"),
            MessageEntity(MessageEntity.BOLD, 5, 9),
        ]

        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            received_id = request_data.parameters[id_name] == id_name
            gift_id = request_data.parameters["gift_id"] == "gift_id"
            text = request_data.parameters["text"] == "text"
            text_parse_mode = request_data.parameters["text_parse_mode"] == "text_parse_mode"
            tes = request_data.parameters["text_entities"] == [
                me.to_dict() for me in text_entities
            ]
            pay_for_upgrade = request_data.parameters["pay_for_upgrade"] is True

            return received_id and gift_id and text and text_parse_mode and tes and pay_for_upgrade

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.send_gift(
            gift,
            "text",
            text_parse_mode="text_parse_mode",
            text_entities=text_entities,
            pay_for_upgrade=True,
            **{id_name: id_name},
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
            publisher_chat=Chat(5, Chat.PRIVATE),
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
            publisher_chat=Chat(6, Chat.PRIVATE),
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
            publisher_chat=Chat(7, Chat.PRIVATE),
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
            assert de_json_gift.publisher_chat == original_gift.publisher_chat

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


@pytest.fixture
def gift_info():
    return GiftInfo(
        gift=GiftInfoTestBase.gift,
        owned_gift_id=GiftInfoTestBase.owned_gift_id,
        convert_star_count=GiftInfoTestBase.convert_star_count,
        prepaid_upgrade_star_count=GiftInfoTestBase.prepaid_upgrade_star_count,
        can_be_upgraded=GiftInfoTestBase.can_be_upgraded,
        text=GiftInfoTestBase.text,
        entities=GiftInfoTestBase.entities,
        is_private=GiftInfoTestBase.is_private,
    )


class GiftInfoTestBase:
    gift = Gift(
        id="some_id",
        sticker=Sticker("file_id", "file_unique_id", 512, 512, False, False, "regular"),
        star_count=5,
        total_count=10,
        remaining_count=15,
        upgrade_star_count=20,
    )
    owned_gift_id = "some_owned_gift_id"
    convert_star_count = 100
    prepaid_upgrade_star_count = 200
    can_be_upgraded = True
    text = "test text"
    entities = (
        MessageEntity(MessageEntity.BOLD, 0, 4),
        MessageEntity(MessageEntity.ITALIC, 5, 8),
    )
    is_private = True


class TestGiftInfoWithoutRequest(GiftInfoTestBase):
    def test_slot_behaviour(self, gift_info):
        for attr in gift_info.__slots__:
            assert getattr(gift_info, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(gift_info)) == len(set(mro_slots(gift_info))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "gift": self.gift.to_dict(),
            "owned_gift_id": self.owned_gift_id,
            "convert_star_count": self.convert_star_count,
            "prepaid_upgrade_star_count": self.prepaid_upgrade_star_count,
            "can_be_upgraded": self.can_be_upgraded,
            "text": self.text,
            "entities": [e.to_dict() for e in self.entities],
            "is_private": self.is_private,
        }
        gift_info = GiftInfo.de_json(json_dict, offline_bot)
        assert gift_info.api_kwargs == {}
        assert gift_info.gift == self.gift
        assert gift_info.owned_gift_id == self.owned_gift_id
        assert gift_info.convert_star_count == self.convert_star_count
        assert gift_info.prepaid_upgrade_star_count == self.prepaid_upgrade_star_count
        assert gift_info.can_be_upgraded == self.can_be_upgraded
        assert gift_info.text == self.text
        assert gift_info.entities == self.entities
        assert gift_info.is_private == self.is_private

    def test_to_dict(self, gift_info):
        json_dict = gift_info.to_dict()
        assert json_dict["gift"] == self.gift.to_dict()
        assert json_dict["owned_gift_id"] == self.owned_gift_id
        assert json_dict["convert_star_count"] == self.convert_star_count
        assert json_dict["prepaid_upgrade_star_count"] == self.prepaid_upgrade_star_count
        assert json_dict["can_be_upgraded"] == self.can_be_upgraded
        assert json_dict["text"] == self.text
        assert json_dict["entities"] == [e.to_dict() for e in self.entities]
        assert json_dict["is_private"] == self.is_private

    def test_parse_entity(self, gift_info):
        entity = MessageEntity(MessageEntity.BOLD, 0, 4)

        assert gift_info.parse_entity(entity) == "test"

        with pytest.raises(RuntimeError, match="GiftInfo has no"):
            GiftInfo(
                gift=self.gift,
            ).parse_entity(entity)

    def test_parse_entities(self, gift_info):
        entity = MessageEntity(MessageEntity.BOLD, 0, 4)
        entity_2 = MessageEntity(MessageEntity.ITALIC, 5, 8)

        assert gift_info.parse_entities(MessageEntity.BOLD) == {entity: "test"}
        assert gift_info.parse_entities() == {entity: "test", entity_2: "text"}

        with pytest.raises(RuntimeError, match="GiftInfo has no"):
            GiftInfo(
                gift=self.gift,
            ).parse_entities()

    def test_equality(self, gift_info):
        a = gift_info
        b = GiftInfo(gift=self.gift)
        c = GiftInfo(
            gift=Gift(
                id="some_other_gift_id",
                sticker=Sticker("file_id", "file_unique_id", 512, 512, False, False, "regular"),
                star_count=5,
            ),
        )
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def accepted_gift_types():
    return AcceptedGiftTypes(
        unlimited_gifts=AcceptedGiftTypesTestBase.unlimited_gifts,
        limited_gifts=AcceptedGiftTypesTestBase.limited_gifts,
        unique_gifts=AcceptedGiftTypesTestBase.unique_gifts,
        premium_subscription=AcceptedGiftTypesTestBase.premium_subscription,
    )


class AcceptedGiftTypesTestBase:
    unlimited_gifts = False
    limited_gifts = True
    unique_gifts = True
    premium_subscription = True


class TestAcceptedGiftTypesWithoutRequest(AcceptedGiftTypesTestBase):
    def test_slot_behaviour(self, accepted_gift_types):
        for attr in accepted_gift_types.__slots__:
            assert getattr(accepted_gift_types, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(accepted_gift_types)) == len(set(mro_slots(accepted_gift_types))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot):
        json_dict = {
            "unlimited_gifts": self.unlimited_gifts,
            "limited_gifts": self.limited_gifts,
            "unique_gifts": self.unique_gifts,
            "premium_subscription": self.premium_subscription,
        }
        accepted_gift_types = AcceptedGiftTypes.de_json(json_dict, offline_bot)
        assert accepted_gift_types.api_kwargs == {}
        assert accepted_gift_types.unlimited_gifts == self.unlimited_gifts
        assert accepted_gift_types.limited_gifts == self.limited_gifts
        assert accepted_gift_types.unique_gifts == self.unique_gifts
        assert accepted_gift_types.premium_subscription == self.premium_subscription

    def test_to_dict(self, accepted_gift_types):
        json_dict = accepted_gift_types.to_dict()
        assert json_dict["unlimited_gifts"] == self.unlimited_gifts
        assert json_dict["limited_gifts"] == self.limited_gifts
        assert json_dict["unique_gifts"] == self.unique_gifts
        assert json_dict["premium_subscription"] == self.premium_subscription

    def test_equality(self, accepted_gift_types):
        a = accepted_gift_types
        b = AcceptedGiftTypes(
            self.unlimited_gifts, self.limited_gifts, self.unique_gifts, self.premium_subscription
        )
        c = AcceptedGiftTypes(
            not self.unlimited_gifts,
            self.limited_gifts,
            self.unique_gifts,
            self.premium_subscription,
        )
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
