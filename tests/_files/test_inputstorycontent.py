#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

import datetime as dtm

import pytest

from telegram import InputFile, InputStoryContent, InputStoryContentPhoto, InputStoryContentVideo
from telegram.constants import InputStoryContentType
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def input_story_content():
    return InputStoryContent(
        type=InputStoryContentTestBase.type,
    )


class InputStoryContentTestBase:
    type = InputStoryContent.PHOTO


class TestInputStoryContent(InputStoryContentTestBase):
    def test_slot_behaviour(self, input_story_content):
        inst = input_story_content
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self):
        assert type(InputStoryContent(type="video").type) is InputStoryContentType
        assert InputStoryContent(type="unknown").type == "unknown"


@pytest.fixture(scope="module")
def input_story_content_photo():
    return InputStoryContentPhoto(photo=InputStoryContentPhotoTestBase.photo.read_bytes())


class InputStoryContentPhotoTestBase:
    type = InputStoryContentType.PHOTO
    photo = data_file("telegram.jpg")


class TestInputStoryContentPhotoWithoutRequest(InputStoryContentPhotoTestBase):
    def test_slot_behaviour(self, input_story_content_photo):
        inst = input_story_content_photo
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_story_content_photo):
        inst = input_story_content_photo
        assert inst.type is self.type
        assert isinstance(inst.photo, InputFile)

    def test_to_dict(self, input_story_content_photo):
        inst = input_story_content_photo
        json_dict = inst.to_dict()
        assert json_dict["type"] is self.type
        assert json_dict["photo"] == inst.photo

    def test_with_photo_file(self, photo_file):
        inst = InputStoryContentPhoto(photo=photo_file)
        assert inst.type is self.type
        assert isinstance(inst.photo, InputFile)

    def test_with_local_files(self):
        inst = InputStoryContentPhoto(photo=data_file("telegram.jpg"))
        assert inst.photo == data_file("telegram.jpg").as_uri()


@pytest.fixture(scope="module")
def input_story_content_video():
    return InputStoryContentVideo(
        video=InputStoryContentVideoTestBase.video.read_bytes(),
        duration=InputStoryContentVideoTestBase.duration,
        cover_frame_timestamp=InputStoryContentVideoTestBase.cover_frame_timestamp,
        is_animation=InputStoryContentVideoTestBase.is_animation,
    )


class InputStoryContentVideoTestBase:
    type = InputStoryContentType.VIDEO
    video = data_file("telegram.mp4")
    duration = dtm.timedelta(seconds=30)
    cover_frame_timestamp = dtm.timedelta(seconds=15)
    is_animation = False


class TestInputStoryContentVideoWithoutRequest(InputStoryContentVideoTestBase):
    def test_slot_behaviour(self, input_story_content_video):
        inst = input_story_content_video
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_story_content_video):
        inst = input_story_content_video
        assert inst.type is self.type
        assert isinstance(inst.video, InputFile)
        assert inst.duration == self.duration
        assert inst.cover_frame_timestamp == self.cover_frame_timestamp
        assert inst.is_animation is self.is_animation

    def test_to_dict(self, input_story_content_video):
        inst = input_story_content_video
        json_dict = inst.to_dict()
        assert json_dict["type"] is self.type
        assert json_dict["video"] == inst.video
        assert json_dict["duration"] == self.duration.total_seconds()
        assert json_dict["cover_frame_timestamp"] == self.cover_frame_timestamp.total_seconds()
        assert json_dict["is_animation"] is self.is_animation

    @pytest.mark.parametrize(
        ("argument", "expected"),
        [(4, 4), (4.0, 4), (dtm.timedelta(seconds=4), 4), (4.5, 4.5)],
    )
    def test_to_dict_float_time_period(self, argument, expected):
        # We test that whole number conversion works properly. Only tested here but
        # relevant for some other classes too (e.g InputProfilePhotoAnimated.main_frame_timestamp)
        inst = InputStoryContentVideo(
            video=self.video.read_bytes(),
            duration=argument,
            cover_frame_timestamp=argument,
        )
        json_dict = inst.to_dict()

        assert json_dict["duration"] == expected
        assert type(json_dict["duration"]) is type(expected)
        assert json_dict["cover_frame_timestamp"] == expected
        assert type(json_dict["cover_frame_timestamp"]) is type(expected)

    def test_with_video_file(self, video_file):
        inst = InputStoryContentVideo(video=video_file)
        assert inst.type is self.type
        assert isinstance(inst.video, InputFile)

    def test_with_local_files(self):
        inst = InputStoryContentVideo(video=data_file("telegram.mp4"))
        assert inst.video == data_file("telegram.mp4").as_uri()

    @pytest.mark.parametrize("timestamp", [dtm.timedelta(seconds=60), 60, float(60)])
    @pytest.mark.parametrize("field", ["duration", "cover_frame_timestamp"])
    def test_time_period_arg_conversion(self, field, timestamp):
        inst = InputStoryContentVideo(
            video=self.video,
            **{field: timestamp},
        )
        value = getattr(inst, field)
        assert isinstance(value, dtm.timedelta)
        assert value == dtm.timedelta(seconds=60)

        inst = InputStoryContentVideo(
            video=self.video,
            **{field: None},
        )
        value = getattr(inst, field)
        assert value is None
