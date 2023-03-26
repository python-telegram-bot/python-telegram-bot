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

from telegram import InputSticker, MaskPosition
from telegram._files.inputfile import InputFile
from tests._files.test_sticker import video_sticker_file  # noqa: F401
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def input_sticker():
    return InputSticker(
        sticker=TestInputStickerBase.sticker,
        emoji_list=TestInputStickerBase.emoji_list,
        mask_position=TestInputStickerBase.mask_position,
        keywords=TestInputStickerBase.keywords,
    )


class TestInputStickerBase:
    sticker = "fake_file_id"
    emoji_list = ("👍", "👎")
    mask_position = MaskPosition("forehead", 0.5, 0.5, 0.5)
    keywords = ("thumbsup", "thumbsdown")


class TestInputStickerNoRequest(TestInputStickerBase):
    def test_slot_behaviour(self, input_sticker):
        inst = input_sticker
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_sticker):
        assert input_sticker.sticker == self.sticker
        assert isinstance(input_sticker.sticker, str)
        assert input_sticker.emoji_list == self.emoji_list
        assert input_sticker.mask_position == self.mask_position
        assert input_sticker.keywords == self.keywords

    def test_attributes_tuple(self, input_sticker):
        assert isinstance(input_sticker.keywords, tuple)
        assert isinstance(input_sticker.emoji_list, tuple)
        a = InputSticker("sticker", ["emoji"])
        assert isinstance(a.emoji_list, tuple)
        assert a.keywords == ()

    def test_to_dict(self, input_sticker):
        input_sticker_dict = input_sticker.to_dict()

        assert isinstance(input_sticker_dict, dict)
        assert input_sticker_dict["sticker"] == input_sticker.sticker
        assert input_sticker_dict["emoji_list"] == list(input_sticker.emoji_list)
        assert input_sticker_dict["mask_position"] == input_sticker.mask_position.to_dict()
        assert input_sticker_dict["keywords"] == list(input_sticker.keywords)

    def test_with_sticker_input_types(self, video_sticker_file):  # noqa: F811
        sticker = InputSticker(sticker=video_sticker_file, emoji_list=["👍"])
        assert isinstance(sticker.sticker, InputFile)
        sticker = InputSticker(data_file("telegram_video_sticker.webm"), ["👍"])
        assert sticker.sticker == data_file("telegram_video_sticker.webm").as_uri()
