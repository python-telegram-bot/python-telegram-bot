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
from copy import deepcopy

import pytest

from telegram import Dice, User
from telegram._files.sticker import Sticker
from telegram._gifts import Gift
from telegram._messageentity import MessageEntity
from telegram._ownedgift import OwnedGift, OwnedGiftRegular, OwnedGifts, OwnedGiftUnique
from telegram._uniquegift import (
    UniqueGift,
    UniqueGiftBackdrop,
    UniqueGiftBackdropColors,
    UniqueGiftModel,
    UniqueGiftSymbol,
)
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import OwnedGiftType
from tests.auxil.slots import mro_slots


@pytest.fixture
def owned_gift():
    return OwnedGift(type=OwnedGiftTestBase.type)


class OwnedGiftTestBase:
    type = OwnedGiftType.REGULAR
    gift = Gift(
        id="some_id",
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
    )
    unique_gift = UniqueGift(
        base_name="human_readable",
        name="unique_name",
        number=10,
        model=UniqueGiftModel(
            name="model_name",
            sticker=Sticker("file_id1", "file_unique_id1", 512, 512, False, False, "regular"),
            rarity_per_mille=10,
        ),
        symbol=UniqueGiftSymbol(
            name="symbol_name",
            sticker=Sticker("file_id2", "file_unique_id2", 512, 512, True, True, "mask"),
            rarity_per_mille=20,
        ),
        backdrop=UniqueGiftBackdrop(
            name="backdrop_name",
            colors=UniqueGiftBackdropColors(0x00FF00, 0xEE00FF, 0xAA22BB, 0x20FE8F),
            rarity_per_mille=30,
        ),
    )
    send_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)
    owned_gift_id = "not_real_id"
    sender_user = User(1, "test user", False)
    text = "test text"
    entities = (
        MessageEntity(MessageEntity.BOLD, 0, 4),
        MessageEntity(MessageEntity.ITALIC, 5, 8),
    )
    is_private = True
    is_saved = True
    can_be_upgraded = True
    was_refunded = False
    convert_star_count = 100
    prepaid_upgrade_star_count = 200
    can_be_transferred = True
    transfer_star_count = 300
    next_transfer_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)


class TestOwnedGiftWithoutRequest(OwnedGiftTestBase):
    def test_slot_behaviour(self, owned_gift):
        inst = owned_gift
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self, owned_gift):
        assert type(OwnedGift("regular").type) is OwnedGiftType
        assert OwnedGift("unknown").type == "unknown"

    def test_de_json(self, offline_bot):
        data = {"type": "unknown"}
        paid_media = OwnedGift.de_json(data, offline_bot)
        assert paid_media.api_kwargs == {}
        assert paid_media.type == "unknown"

    @pytest.mark.parametrize(
        ("og_type", "subclass", "gift"),
        [
            ("regular", OwnedGiftRegular, OwnedGiftTestBase.gift),
            ("unique", OwnedGiftUnique, OwnedGiftTestBase.unique_gift),
        ],
    )
    def test_de_json_subclass(self, offline_bot, og_type, subclass, gift):
        json_dict = {
            "type": og_type,
            "gift": gift.to_dict(),
            "send_date": to_timestamp(self.send_date),
            "owned_gift_id": self.owned_gift_id,
            "sender_user": self.sender_user.to_dict(),
            "text": self.text,
            "entities": [e.to_dict() for e in self.entities],
            "is_private": self.is_private,
            "is_saved": self.is_saved,
            "can_be_upgraded": self.can_be_upgraded,
            "was_refunded": self.was_refunded,
            "convert_star_count": self.convert_star_count,
            "prepaid_upgrade_star_count": self.prepaid_upgrade_star_count,
            "can_be_transferred": self.can_be_transferred,
            "transfer_star_count": self.transfer_star_count,
            "next_transfer_date": to_timestamp(self.next_transfer_date),
        }
        og = OwnedGift.de_json(json_dict, offline_bot)

        assert type(og) is subclass
        assert set(og.api_kwargs.keys()) == set(json_dict.keys()) - set(subclass.__slots__) - {
            "type"
        }
        assert og.type == og_type

    def test_to_dict(self, owned_gift):
        assert owned_gift.to_dict() == {"type": owned_gift.type}

    def test_equality(self, owned_gift):
        a = owned_gift
        b = OwnedGift(self.type)
        c = OwnedGift("unknown")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def owned_gift_regular():
    return OwnedGiftRegular(
        gift=TestOwnedGiftRegularWithoutRequest.gift,
        send_date=TestOwnedGiftRegularWithoutRequest.send_date,
        owned_gift_id=TestOwnedGiftRegularWithoutRequest.owned_gift_id,
        sender_user=TestOwnedGiftRegularWithoutRequest.sender_user,
        text=TestOwnedGiftRegularWithoutRequest.text,
        entities=TestOwnedGiftRegularWithoutRequest.entities,
        is_private=TestOwnedGiftRegularWithoutRequest.is_private,
        is_saved=TestOwnedGiftRegularWithoutRequest.is_saved,
        can_be_upgraded=TestOwnedGiftRegularWithoutRequest.can_be_upgraded,
        was_refunded=TestOwnedGiftRegularWithoutRequest.was_refunded,
        convert_star_count=TestOwnedGiftRegularWithoutRequest.convert_star_count,
        prepaid_upgrade_star_count=TestOwnedGiftRegularWithoutRequest.prepaid_upgrade_star_count,
    )


class TestOwnedGiftRegularWithoutRequest(OwnedGiftTestBase):
    type = OwnedGiftType.REGULAR

    def test_slot_behaviour(self, owned_gift_regular):
        inst = owned_gift_regular
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "gift": self.gift.to_dict(),
            "send_date": to_timestamp(self.send_date),
            "owned_gift_id": self.owned_gift_id,
            "sender_user": self.sender_user.to_dict(),
            "text": self.text,
            "entities": [e.to_dict() for e in self.entities],
            "is_private": self.is_private,
            "is_saved": self.is_saved,
            "can_be_upgraded": self.can_be_upgraded,
            "was_refunded": self.was_refunded,
            "convert_star_count": self.convert_star_count,
            "prepaid_upgrade_star_count": self.prepaid_upgrade_star_count,
        }
        ogr = OwnedGiftRegular.de_json(json_dict, offline_bot)
        assert ogr.gift == self.gift
        assert ogr.send_date == self.send_date
        assert ogr.owned_gift_id == self.owned_gift_id
        assert ogr.sender_user == self.sender_user
        assert ogr.text == self.text
        assert ogr.entities == self.entities
        assert ogr.is_private == self.is_private
        assert ogr.is_saved == self.is_saved
        assert ogr.can_be_upgraded == self.can_be_upgraded
        assert ogr.was_refunded == self.was_refunded
        assert ogr.convert_star_count == self.convert_star_count
        assert ogr.prepaid_upgrade_star_count == self.prepaid_upgrade_star_count
        assert ogr.api_kwargs == {}

    def test_to_dict(self, owned_gift_regular):
        json_dict = owned_gift_regular.to_dict()
        assert isinstance(json_dict, dict)
        assert json_dict["type"] == self.type
        assert json_dict["gift"] == self.gift.to_dict()
        assert json_dict["send_date"] == to_timestamp(self.send_date)
        assert json_dict["owned_gift_id"] == self.owned_gift_id
        assert json_dict["sender_user"] == self.sender_user.to_dict()
        assert json_dict["text"] == self.text
        assert json_dict["entities"] == [e.to_dict() for e in self.entities]
        assert json_dict["is_private"] == self.is_private
        assert json_dict["is_saved"] == self.is_saved
        assert json_dict["can_be_upgraded"] == self.can_be_upgraded
        assert json_dict["was_refunded"] == self.was_refunded
        assert json_dict["convert_star_count"] == self.convert_star_count
        assert json_dict["prepaid_upgrade_star_count"] == self.prepaid_upgrade_star_count

    def test_parse_entity(self, owned_gift_regular):
        entity = MessageEntity(MessageEntity.BOLD, 0, 4)

        assert owned_gift_regular.parse_entity(entity) == "test"

        with pytest.raises(RuntimeError, match="OwnedGiftRegular has no"):
            OwnedGiftRegular(
                gift=self.gift,
                send_date=self.send_date,
            ).parse_entity(entity)

    def test_parse_entities(self, owned_gift_regular):
        entity = MessageEntity(MessageEntity.BOLD, 0, 4)
        entity_2 = MessageEntity(MessageEntity.ITALIC, 5, 8)

        assert owned_gift_regular.parse_entities(MessageEntity.BOLD) == {entity: "test"}
        assert owned_gift_regular.parse_entities() == {entity: "test", entity_2: "text"}

        with pytest.raises(RuntimeError, match="OwnedGiftRegular has no"):
            OwnedGiftRegular(
                gift=self.gift,
                send_date=self.send_date,
            ).parse_entities()

    def test_equality(self, owned_gift_regular):
        a = owned_gift_regular
        b = OwnedGiftRegular(deepcopy(self.gift), deepcopy(self.send_date))
        c = OwnedGiftRegular(self.gift, self.send_date + dtm.timedelta(seconds=1))
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def owned_gift_unique():
    return OwnedGiftUnique(
        gift=TestOwnedGiftUniqueWithoutRequest.unique_gift,
        send_date=TestOwnedGiftUniqueWithoutRequest.send_date,
        owned_gift_id=TestOwnedGiftUniqueWithoutRequest.owned_gift_id,
        sender_user=TestOwnedGiftUniqueWithoutRequest.sender_user,
        is_saved=TestOwnedGiftUniqueWithoutRequest.is_saved,
        can_be_transferred=TestOwnedGiftUniqueWithoutRequest.can_be_transferred,
        transfer_star_count=TestOwnedGiftUniqueWithoutRequest.transfer_star_count,
        next_transfer_date=TestOwnedGiftUniqueWithoutRequest.next_transfer_date,
    )


class TestOwnedGiftUniqueWithoutRequest(OwnedGiftTestBase):
    type = OwnedGiftType.UNIQUE

    def test_slot_behaviour(self, owned_gift_unique):
        inst = owned_gift_unique
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "gift": self.unique_gift.to_dict(),
            "send_date": to_timestamp(self.send_date),
            "owned_gift_id": self.owned_gift_id,
            "sender_user": self.sender_user.to_dict(),
            "is_saved": self.is_saved,
            "can_be_transferred": self.can_be_transferred,
            "transfer_star_count": self.transfer_star_count,
            "next_transfer_date": to_timestamp(self.next_transfer_date),
        }
        ogu = OwnedGiftUnique.de_json(json_dict, offline_bot)
        assert ogu.gift == self.unique_gift
        assert ogu.send_date == self.send_date
        assert ogu.owned_gift_id == self.owned_gift_id
        assert ogu.sender_user == self.sender_user
        assert ogu.is_saved == self.is_saved
        assert ogu.can_be_transferred == self.can_be_transferred
        assert ogu.transfer_star_count == self.transfer_star_count
        assert ogu.next_transfer_date == self.next_transfer_date
        assert ogu.api_kwargs == {}

    def test_to_dict(self, owned_gift_unique):
        json_dict = owned_gift_unique.to_dict()
        assert isinstance(json_dict, dict)
        assert json_dict["type"] == self.type
        assert json_dict["gift"] == self.unique_gift.to_dict()
        assert json_dict["send_date"] == to_timestamp(self.send_date)
        assert json_dict["owned_gift_id"] == self.owned_gift_id
        assert json_dict["sender_user"] == self.sender_user.to_dict()
        assert json_dict["is_saved"] == self.is_saved
        assert json_dict["can_be_transferred"] == self.can_be_transferred
        assert json_dict["transfer_star_count"] == self.transfer_star_count
        assert json_dict["next_transfer_date"] == to_timestamp(self.next_transfer_date)

    def test_equality(self, owned_gift_unique):
        a = owned_gift_unique
        b = OwnedGiftUnique(deepcopy(self.unique_gift), deepcopy(self.send_date))
        c = OwnedGiftUnique(self.unique_gift, self.send_date + dtm.timedelta(seconds=1))
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def owned_gifts(request):
    return OwnedGifts(
        total_count=OwnedGiftsTestBase.total_count,
        gifts=OwnedGiftsTestBase.gifts,
        next_offset=OwnedGiftsTestBase.next_offset,
    )


class OwnedGiftsTestBase:
    total_count = 2
    next_offset = "next_offset_str"
    gifts: list[OwnedGift] = [
        OwnedGiftRegular(
            gift=Gift(
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
            send_date=dtm.datetime.now(tz=UTC).replace(microsecond=0),
            owned_gift_id="some_id_1",
        ),
        OwnedGiftUnique(
            gift=UniqueGift(
                base_name="human_readable",
                name="unique_name",
                number=10,
                model=UniqueGiftModel(
                    name="model_name",
                    sticker=Sticker(
                        "file_id1", "file_unique_id1", 512, 512, False, False, "regular"
                    ),
                    rarity_per_mille=10,
                ),
                symbol=UniqueGiftSymbol(
                    name="symbol_name",
                    sticker=Sticker("file_id2", "file_unique_id2", 512, 512, True, True, "mask"),
                    rarity_per_mille=20,
                ),
                backdrop=UniqueGiftBackdrop(
                    name="backdrop_name",
                    colors=UniqueGiftBackdropColors(0x00FF00, 0xEE00FF, 0xAA22BB, 0x20FE8F),
                    rarity_per_mille=30,
                ),
            ),
            send_date=dtm.datetime.now(tz=UTC).replace(microsecond=0),
            owned_gift_id="some_id_2",
        ),
    ]


class TestOwnedGiftsWithoutRequest(OwnedGiftsTestBase):
    def test_slot_behaviour(self, owned_gifts):
        for attr in owned_gifts.__slots__:
            assert getattr(owned_gifts, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(owned_gifts)) == len(set(mro_slots(owned_gifts))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "total_count": self.total_count,
            "gifts": [gift.to_dict() for gift in self.gifts],
            "next_offset": self.next_offset,
        }
        owned_gifts = OwnedGifts.de_json(json_dict, offline_bot)
        assert owned_gifts.api_kwargs == {}

        assert owned_gifts.total_count == self.total_count
        assert owned_gifts.gifts == tuple(self.gifts)
        assert type(owned_gifts.gifts[0]) is OwnedGiftRegular
        assert type(owned_gifts.gifts[1]) is OwnedGiftUnique
        assert owned_gifts.next_offset == self.next_offset

    def test_to_dict(self, owned_gifts):
        gifts_dict = owned_gifts.to_dict()

        assert isinstance(gifts_dict, dict)
        assert gifts_dict["total_count"] == self.total_count
        assert gifts_dict["gifts"] == [gift.to_dict() for gift in self.gifts]
        assert gifts_dict["next_offset"] == self.next_offset

    def test_equality(self, owned_gifts):
        a = owned_gifts
        b = OwnedGifts(self.total_count, self.gifts)
        c = OwnedGifts(self.total_count - 1, self.gifts[:1])
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
