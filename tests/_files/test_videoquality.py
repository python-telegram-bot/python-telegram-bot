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
def video_quality_message_id():
    # A video message with exactly one available video quality:
    # https://t.me/pythontelegrambottests/375821
    # See discussion: https://t.me/pythontelegrambotdev/1782
    return 375821


@pytest.fixture(scope="module")
async def video_quality_list(bot, chat_id, channel_id, video_quality_message_id):
    return (
        await bot.forward_message(chat_id, channel_id, video_quality_message_id, read_timeout=50)
    ).video.qualities


@pytest.fixture(scope="module")
def video_quality(video_quality_list):
    return video_quality_list[-1]


class VideoQualityTestBase:
    # These values are tied to the forwarded video and must remain unchanged
    width = 464
    height = 848
    codec = "h264"
    file_size = 405540


class TestVideoQualityWithoutRequest(VideoQualityTestBase):
    def test_qualities_available(self, video_quality_list):
        assert isinstance(video_quality_list, tuple)
        # Subsequent tests relie on the forwarded video
        # having exactly one video quality.
        assert len(video_quality_list) == 1

    def test_slot_behaviour(self, video_quality):
        for attr in video_quality.__slots__:
            assert getattr(video_quality, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(video_quality)) == len(set(mro_slots(video_quality))), (
            "duplicate slot"
        )

    def test_creation(self, video_quality):
        assert isinstance(video_quality, VideoQuality)
        assert isinstance(video_quality.file_id, str)
        assert isinstance(video_quality.file_unique_id, str)
        assert video_quality.file_id
        assert video_quality.file_unique_id

    def test_expected_values(self, video_quality):
        assert video_quality.width == self.width
        assert video_quality.height == self.height
        assert video_quality.codec == self.codec
        assert video_quality.file_size == self.file_size

    def test_de_json(self, offline_bot, video_quality):
        json_dict = {
            "file_id": video_quality.file_id,
            "file_unique_id": video_quality.file_unique_id,
            "width": self.width,
            "height": self.height,
            "codec": self.codec,
            "file_size": self.file_size,
        }
        json_videoquality = VideoQuality.de_json(json_dict, offline_bot)
        assert json_videoquality.api_kwargs == {}

        assert json_videoquality.file_id == video_quality.file_id
        assert json_videoquality.file_unique_id == video_quality.file_unique_id
        assert json_videoquality.width == self.width
        assert json_videoquality.height == self.height
        assert json_videoquality.codec == self.codec
        assert json_videoquality.file_size == self.file_size

    def test_to_dict(self, video_quality):
        videoquality_dict = video_quality.to_dict()

        assert isinstance(videoquality_dict, dict)
        assert videoquality_dict["file_id"] == video_quality.file_id
        assert videoquality_dict["file_unique_id"] == video_quality.file_unique_id
        assert videoquality_dict["width"] == video_quality.width
        assert videoquality_dict["height"] == video_quality.height
        assert videoquality_dict["codec"] == video_quality.codec
        assert videoquality_dict["file_size"] == video_quality.file_size

    def test_equality(self, video_quality):
        a = VideoQuality(
            video_quality.file_id,
            video_quality.file_unique_id,
            self.width,
            self.height,
            self.codec,
        )
        b = VideoQuality("", video_quality.file_unique_id, self.width, self.height, self.codec)
        c = VideoQuality(video_quality.file_id, video_quality.file_unique_id, 0, 0, self.codec)
        d = VideoQuality("", "", self.width, self.height, self.codec)
        e = PhotoSize(
            video_quality.file_id,
            video_quality.file_unique_id,
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
    async def test_get_and_download(self, bot, video_quality, tmp_file):
        new_file = await bot.get_file(video_quality.file_id)

        assert new_file.file_size == video_quality.file_size
        assert new_file.file_unique_id == video_quality.file_unique_id
        assert new_file.file_path.startswith("https://")

        await new_file.download_to_drive(tmp_file)

        assert tmp_file.is_file()

    async def test_resend(self, bot, chat_id, video_quality):
        message = await bot.send_video(chat_id, video_quality.file_id)

        assert message.video.file_id == video_quality.file_id
        assert message.video.file_unique_id == video_quality.file_unique_id
