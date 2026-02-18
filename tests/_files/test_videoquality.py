#!/usr/bin/env python
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

from telegram import PhotoSize, VideoQuality
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def videoquality_message_id():
    # a video message with qualities available
    # https://t.me/<channel_id>/375821
    return 375821


@pytest.fixture(scope="module")
async def videoquality_list(bot, chat_id, channel_id, videoquality_message_id):
    return (
        await bot.forward_message(chat_id, channel_id, videoquality_message_id, read_timeout=50)
    ).video.qualities


@pytest.fixture(scope="module")
def videoquality(videoquality_list):
    return videoquality_list[-1]


class VideoQualityTestBase:
    widths = [464]
    heights = [848]
    codecs = ["h264"]
    file_sizes = [405540]

    @property
    def width(self):
        return self.widths[-1]

    @property
    def height(self):
        return self.heights[-1]

    @property
    def codec(self):
        return self.codecs[-1]

    @property
    def file_size(self):
        return self.file_sizes[-1]


class TestVideoQualityWithoutRequest(VideoQualityTestBase):
    def test_qualities_available(self, videoquality_list):
        assert isinstance(videoquality_list, tuple)
        assert len(videoquality_list) > 0

    def test_slot_behaviour(self, videoquality):
        for attr in videoquality.__slots__:
            assert getattr(videoquality, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(videoquality)) == len(set(mro_slots(videoquality))), "duplicate slot"

    def test_creation(self, videoquality):
        assert isinstance(videoquality, VideoQuality)
        assert isinstance(videoquality.file_id, str)
        assert isinstance(videoquality.file_unique_id, str)
        assert videoquality.file_id
        assert videoquality.file_unique_id

    def test_expected_values(self, videoquality):
        assert videoquality.width in self.widths
        assert videoquality.height in self.heights
        assert videoquality.codec in self.codecs
        assert videoquality.file_size in self.file_sizes

    def test_de_json(self, offline_bot, videoquality):
        json_dict = {
            "file_id": videoquality.file_id,
            "file_unique_id": videoquality.file_unique_id,
            "width": self.width,
            "height": self.height,
            "codec": self.codec,
            "file_size": self.file_size,
        }
        json_videoquality = VideoQuality.de_json(json_dict, offline_bot)
        assert json_videoquality.api_kwargs == {}

        assert json_videoquality.file_id == videoquality.file_id
        assert json_videoquality.file_unique_id == videoquality.file_unique_id
        assert json_videoquality.width == self.width
        assert json_videoquality.height == self.height
        assert json_videoquality.codec == self.codec
        assert json_videoquality.file_size == self.file_size

    def test_to_dict(self, videoquality):
        videoquality_dict = videoquality.to_dict()

        assert isinstance(videoquality_dict, dict)
        assert videoquality_dict["file_id"] == videoquality.file_id
        assert videoquality_dict["file_unique_id"] == videoquality.file_unique_id
        assert videoquality_dict["width"] == videoquality.width
        assert videoquality_dict["height"] == videoquality.height
        assert videoquality_dict["codec"] == videoquality.codec
        assert videoquality_dict["file_size"] == videoquality.file_size

    def test_equality(self, videoquality):
        a = VideoQuality(
            videoquality.file_id,
            videoquality.file_unique_id,
            self.width,
            self.height,
            self.codec,
        )
        b = VideoQuality("", videoquality.file_unique_id, self.width, self.height, self.codec)
        c = VideoQuality(videoquality.file_id, videoquality.file_unique_id, 0, 0, self.codec)
        d = VideoQuality("", "", self.width, self.height, self.codec)
        e = PhotoSize(
            videoquality.file_id,
            videoquality.file_unique_id,
            self.width,
            self.height,
        )

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


class TestVideoWithRequest(VideoQualityTestBase):
    async def test_get_and_download(self, bot, videoquality, tmp_file):
        new_file = await bot.get_file(videoquality.file_id)

        assert new_file.file_size == videoquality.file_size
        assert new_file.file_unique_id == videoquality.file_unique_id
        assert new_file.file_path.startswith("https://")

        await new_file.download_to_drive(tmp_file)

        assert tmp_file.is_file()

    async def test_resend(self, bot, chat_id, videoquality):
        message = await bot.send_video(chat_id, videoquality.file_id)
        # Sending via file_id does not retain `qualities`.
        assert not message.video.qualities
