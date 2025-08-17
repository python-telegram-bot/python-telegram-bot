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

from telegram import (
    BotCommand,
    Chat,
    Sticker,
    UniqueGift,
    UniqueGiftBackdrop,
    UniqueGiftBackdropColors,
    UniqueGiftInfo,
    UniqueGiftModel,
    UniqueGiftSymbol,
)
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import UniqueGiftInfoOrigin
from tests.auxil.slots import mro_slots


@pytest.fixture
def unique_gift():
    return UniqueGift(
        base_name=UniqueGiftTestBase.base_name,
        name=UniqueGiftTestBase.name,
        number=UniqueGiftTestBase.number,
        model=UniqueGiftTestBase.model,
        symbol=UniqueGiftTestBase.symbol,
        backdrop=UniqueGiftTestBase.backdrop,
        publisher_chat=UniqueGiftTestBase.publisher_chat,
    )


class UniqueGiftTestBase:
    base_name = "human_readable"
    name = "unique_name"
    number = 10
    model = UniqueGiftModel(
        name="model_name",
        sticker=Sticker("file_id1", "file_unique_id1", 512, 512, False, False, "regular"),
        rarity_per_mille=10,
    )
    symbol = UniqueGiftSymbol(
        name="symbol_name",
        sticker=Sticker("file_id2", "file_unique_id2", 512, 512, True, True, "mask"),
        rarity_per_mille=20,
    )
    backdrop = UniqueGiftBackdrop(
        name="backdrop_name",
        colors=UniqueGiftBackdropColors(0x00FF00, 0xEE00FF, 0xAA22BB, 0x20FE8F),
        rarity_per_mille=30,
    )
    publisher_chat = Chat(1, Chat.PRIVATE)


class TestUniqueGiftWithoutRequest(UniqueGiftTestBase):
    def test_slot_behaviour(self, unique_gift):
        for attr in unique_gift.__slots__:
            assert getattr(unique_gift, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(unique_gift)) == len(set(mro_slots(unique_gift))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "base_name": self.base_name,
            "name": self.name,
            "number": self.number,
            "model": self.model.to_dict(),
            "symbol": self.symbol.to_dict(),
            "backdrop": self.backdrop.to_dict(),
            "publisher_chat": self.publisher_chat.to_dict(),
        }
        unique_gift = UniqueGift.de_json(json_dict, offline_bot)
        assert unique_gift.api_kwargs == {}

        assert unique_gift.base_name == self.base_name
        assert unique_gift.name == self.name
        assert unique_gift.number == self.number
        assert unique_gift.model == self.model
        assert unique_gift.symbol == self.symbol
        assert unique_gift.backdrop == self.backdrop
        assert unique_gift.publisher_chat == self.publisher_chat

    def test_to_dict(self, unique_gift):
        gift_dict = unique_gift.to_dict()

        assert isinstance(gift_dict, dict)
        assert gift_dict["base_name"] == self.base_name
        assert gift_dict["name"] == self.name
        assert gift_dict["number"] == self.number
        assert gift_dict["model"] == self.model.to_dict()
        assert gift_dict["symbol"] == self.symbol.to_dict()
        assert gift_dict["backdrop"] == self.backdrop.to_dict()
        assert gift_dict["publisher_chat"] == self.publisher_chat.to_dict()

    def test_equality(self, unique_gift):
        a = unique_gift
        b = UniqueGift(
            self.base_name,
            self.name,
            self.number,
            self.model,
            self.symbol,
            self.backdrop,
            self.publisher_chat,
        )
        c = UniqueGift(
            "other_base_name",
            self.name,
            self.number,
            self.model,
            self.symbol,
            self.backdrop,
            self.publisher_chat,
        )
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def unique_gift_model():
    return UniqueGiftModel(
        name=UniqueGiftModelTestBase.name,
        sticker=UniqueGiftModelTestBase.sticker,
        rarity_per_mille=UniqueGiftModelTestBase.rarity_per_mille,
    )


class UniqueGiftModelTestBase:
    name = "model_name"
    sticker = Sticker("file_id", "file_unique_id", 512, 512, False, False, "regular")
    rarity_per_mille = 10


class TestUniqueGiftModelWithoutRequest(UniqueGiftModelTestBase):
    def test_slot_behaviour(self, unique_gift_model):
        for attr in unique_gift_model.__slots__:
            assert getattr(unique_gift_model, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(unique_gift_model)) == len(set(mro_slots(unique_gift_model))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot):
        json_dict = {
            "name": self.name,
            "sticker": self.sticker.to_dict(),
            "rarity_per_mille": self.rarity_per_mille,
        }
        unique_gift_model = UniqueGiftModel.de_json(json_dict, offline_bot)
        assert unique_gift_model.api_kwargs == {}
        assert unique_gift_model.name == self.name
        assert unique_gift_model.sticker == self.sticker
        assert unique_gift_model.rarity_per_mille == self.rarity_per_mille

    def test_to_dict(self, unique_gift_model):
        json_dict = unique_gift_model.to_dict()
        assert json_dict["name"] == self.name
        assert json_dict["sticker"] == self.sticker.to_dict()
        assert json_dict["rarity_per_mille"] == self.rarity_per_mille

    def test_equality(self, unique_gift_model):
        a = unique_gift_model
        b = UniqueGiftModel(self.name, self.sticker, self.rarity_per_mille)
        c = UniqueGiftModel("other_name", self.sticker, self.rarity_per_mille)
        d = UniqueGiftSymbol(self.name, self.sticker, self.rarity_per_mille)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def unique_gift_symbol():
    return UniqueGiftSymbol(
        name=UniqueGiftSymbolTestBase.name,
        sticker=UniqueGiftSymbolTestBase.sticker,
        rarity_per_mille=UniqueGiftSymbolTestBase.rarity_per_mille,
    )


class UniqueGiftSymbolTestBase:
    name = "symbol_name"
    sticker = Sticker("file_id", "file_unique_id", 512, 512, False, False, "regular")
    rarity_per_mille = 20


class TestUniqueGiftSymbolWithoutRequest(UniqueGiftSymbolTestBase):
    def test_slot_behaviour(self, unique_gift_symbol):
        for attr in unique_gift_symbol.__slots__:
            assert getattr(unique_gift_symbol, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(unique_gift_symbol)) == len(set(mro_slots(unique_gift_symbol))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot):
        json_dict = {
            "name": self.name,
            "sticker": self.sticker.to_dict(),
            "rarity_per_mille": self.rarity_per_mille,
        }
        unique_gift_symbol = UniqueGiftSymbol.de_json(json_dict, offline_bot)
        assert unique_gift_symbol.api_kwargs == {}
        assert unique_gift_symbol.name == self.name
        assert unique_gift_symbol.sticker == self.sticker
        assert unique_gift_symbol.rarity_per_mille == self.rarity_per_mille

    def test_to_dict(self, unique_gift_symbol):
        json_dict = unique_gift_symbol.to_dict()
        assert json_dict["name"] == self.name
        assert json_dict["sticker"] == self.sticker.to_dict()
        assert json_dict["rarity_per_mille"] == self.rarity_per_mille

    def test_equality(self, unique_gift_symbol):
        a = unique_gift_symbol
        b = UniqueGiftSymbol(self.name, self.sticker, self.rarity_per_mille)
        c = UniqueGiftSymbol("other_name", self.sticker, self.rarity_per_mille)
        d = UniqueGiftModel(self.name, self.sticker, self.rarity_per_mille)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def unique_gift_backdrop():
    return UniqueGiftBackdrop(
        name=UniqueGiftBackdropTestBase.name,
        colors=UniqueGiftBackdropTestBase.colors,
        rarity_per_mille=UniqueGiftBackdropTestBase.rarity_per_mille,
    )


class UniqueGiftBackdropTestBase:
    name = "backdrop_name"
    colors = UniqueGiftBackdropColors(0x00FF00, 0xEE00FF, 0xAA22BB, 0x20FE8F)
    rarity_per_mille = 30


class TestUniqueGiftBackdropWithoutRequest(UniqueGiftBackdropTestBase):
    def test_slot_behaviour(self, unique_gift_backdrop):
        for attr in unique_gift_backdrop.__slots__:
            assert getattr(unique_gift_backdrop, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(unique_gift_backdrop)) == len(set(mro_slots(unique_gift_backdrop))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot):
        json_dict = {
            "name": self.name,
            "colors": self.colors.to_dict(),
            "rarity_per_mille": self.rarity_per_mille,
        }
        unique_gift_backdrop = UniqueGiftBackdrop.de_json(json_dict, offline_bot)
        assert unique_gift_backdrop.api_kwargs == {}
        assert unique_gift_backdrop.name == self.name
        assert unique_gift_backdrop.colors == self.colors
        assert unique_gift_backdrop.rarity_per_mille == self.rarity_per_mille

    def test_to_dict(self, unique_gift_backdrop):
        json_dict = unique_gift_backdrop.to_dict()
        assert json_dict["name"] == self.name
        assert json_dict["colors"] == self.colors.to_dict()
        assert json_dict["rarity_per_mille"] == self.rarity_per_mille

    def test_equality(self, unique_gift_backdrop):
        a = unique_gift_backdrop
        b = UniqueGiftBackdrop(self.name, self.colors, self.rarity_per_mille)
        c = UniqueGiftBackdrop("other_name", self.colors, self.rarity_per_mille)
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def unique_gift_backdrop_colors():
    return UniqueGiftBackdropColors(
        center_color=UniqueGiftBackdropColorsTestBase.center_color,
        edge_color=UniqueGiftBackdropColorsTestBase.edge_color,
        symbol_color=UniqueGiftBackdropColorsTestBase.symbol_color,
        text_color=UniqueGiftBackdropColorsTestBase.text_color,
    )


class UniqueGiftBackdropColorsTestBase:
    center_color = 0x00FF00
    edge_color = 0xEE00FF
    symbol_color = 0xAA22BB
    text_color = 0x20FE8F


class TestUniqueGiftBackdropColorsWithoutRequest(UniqueGiftBackdropColorsTestBase):
    def test_slot_behaviour(self, unique_gift_backdrop_colors):
        for attr in unique_gift_backdrop_colors.__slots__:
            assert getattr(unique_gift_backdrop_colors, attr, "err") != "err", (
                f"got extra slot '{attr}'"
            )
        assert len(mro_slots(unique_gift_backdrop_colors)) == len(
            set(mro_slots(unique_gift_backdrop_colors))
        ), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "center_color": self.center_color,
            "edge_color": self.edge_color,
            "symbol_color": self.symbol_color,
            "text_color": self.text_color,
        }
        unique_gift_backdrop_colors = UniqueGiftBackdropColors.de_json(json_dict, offline_bot)
        assert unique_gift_backdrop_colors.api_kwargs == {}
        assert unique_gift_backdrop_colors.center_color == self.center_color
        assert unique_gift_backdrop_colors.edge_color == self.edge_color
        assert unique_gift_backdrop_colors.symbol_color == self.symbol_color
        assert unique_gift_backdrop_colors.text_color == self.text_color

    def test_to_dict(self, unique_gift_backdrop_colors):
        json_dict = unique_gift_backdrop_colors.to_dict()
        assert json_dict["center_color"] == self.center_color
        assert json_dict["edge_color"] == self.edge_color
        assert json_dict["symbol_color"] == self.symbol_color
        assert json_dict["text_color"] == self.text_color

    def test_equality(self, unique_gift_backdrop_colors):
        a = unique_gift_backdrop_colors
        b = UniqueGiftBackdropColors(
            center_color=self.center_color,
            edge_color=self.edge_color,
            symbol_color=self.symbol_color,
            text_color=self.text_color,
        )
        c = UniqueGiftBackdropColors(
            center_color=0x000000,
            edge_color=self.edge_color,
            symbol_color=self.symbol_color,
            text_color=self.text_color,
        )
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def unique_gift_info():
    return UniqueGiftInfo(
        gift=UniqueGiftInfoTestBase.gift,
        origin=UniqueGiftInfoTestBase.origin,
        owned_gift_id=UniqueGiftInfoTestBase.owned_gift_id,
        transfer_star_count=UniqueGiftInfoTestBase.transfer_star_count,
        last_resale_star_count=UniqueGiftInfoTestBase.last_resale_star_count,
        next_transfer_date=UniqueGiftInfoTestBase.next_transfer_date,
    )


class UniqueGiftInfoTestBase:
    gift = UniqueGift(
        "human_readable_name",
        "unique_name",
        10,
        UniqueGiftModel(
            name="model_name",
            sticker=Sticker("file_id1", "file_unique_id1", 512, 512, False, False, "regular"),
            rarity_per_mille=10,
        ),
        UniqueGiftSymbol(
            name="symbol_name",
            sticker=Sticker("file_id2", "file_unique_id2", 512, 512, True, True, "mask"),
            rarity_per_mille=20,
        ),
        UniqueGiftBackdrop(
            name="backdrop_name",
            colors=UniqueGiftBackdropColors(0x00FF00, 0xEE00FF, 0xAA22BB, 0x20FE8F),
            rarity_per_mille=2,
        ),
    )
    origin = UniqueGiftInfo.UPGRADE
    owned_gift_id = "some_id"
    transfer_star_count = 10
    last_resale_star_count = 5
    next_transfer_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)


class TestUniqueGiftInfoWithoutRequest(UniqueGiftInfoTestBase):
    def test_slot_behaviour(self, unique_gift_info):
        for attr in unique_gift_info.__slots__:
            assert getattr(unique_gift_info, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(unique_gift_info)) == len(set(mro_slots(unique_gift_info))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot):
        json_dict = {
            "gift": self.gift.to_dict(),
            "origin": self.origin,
            "owned_gift_id": self.owned_gift_id,
            "transfer_star_count": self.transfer_star_count,
            "last_resale_star_count": self.last_resale_star_count,
            "next_transfer_date": to_timestamp(self.next_transfer_date),
        }
        unique_gift_info = UniqueGiftInfo.de_json(json_dict, offline_bot)
        assert unique_gift_info.api_kwargs == {}
        assert unique_gift_info.gift == self.gift
        assert unique_gift_info.origin == self.origin
        assert unique_gift_info.owned_gift_id == self.owned_gift_id
        assert unique_gift_info.transfer_star_count == self.transfer_star_count
        assert unique_gift_info.last_resale_star_count == self.last_resale_star_count
        assert unique_gift_info.next_transfer_date == self.next_transfer_date

    def test_de_json_localization(self, tz_bot, offline_bot, raw_bot):
        json_dict = {
            "gift": self.gift.to_dict(),
            "origin": self.origin,
            "owned_gift_id": self.owned_gift_id,
            "transfer_star_count": self.transfer_star_count,
            "last_resale_star_count": self.last_resale_star_count,
            "next_transfer_date": to_timestamp(self.next_transfer_date),
        }

        unique_gift_info_raw = UniqueGiftInfo.de_json(json_dict, raw_bot)
        unique_gift_info_offline = UniqueGiftInfo.de_json(json_dict, offline_bot)
        unique_gift_info_tz = UniqueGiftInfo.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        unique_gift_info_tz_offset = unique_gift_info_tz.next_transfer_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            unique_gift_info_tz.next_transfer_date.replace(tzinfo=None)
        )

        assert unique_gift_info_raw.next_transfer_date.tzinfo == UTC
        assert unique_gift_info_offline.next_transfer_date.tzinfo == UTC
        assert unique_gift_info_tz_offset == tz_bot_offset

    def test_to_dict(self, unique_gift_info):
        json_dict = unique_gift_info.to_dict()
        assert json_dict["gift"] == self.gift.to_dict()
        assert json_dict["origin"] == self.origin
        assert json_dict["owned_gift_id"] == self.owned_gift_id
        assert json_dict["transfer_star_count"] == self.transfer_star_count
        assert json_dict["last_resale_star_count"] == self.last_resale_star_count
        assert json_dict["next_transfer_date"] == to_timestamp(self.next_transfer_date)

    def test_enum_type_conversion(self, unique_gift_info):
        assert type(unique_gift_info.origin) is UniqueGiftInfoOrigin
        assert unique_gift_info.origin == UniqueGiftInfoOrigin.UPGRADE

    def test_equality(self, unique_gift_info):
        a = unique_gift_info
        b = UniqueGiftInfo(self.gift, self.origin, self.owned_gift_id, self.transfer_star_count)
        c = UniqueGiftInfo(
            self.gift, UniqueGiftInfo.TRANSFER, self.owned_gift_id, self.transfer_star_count
        )
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
