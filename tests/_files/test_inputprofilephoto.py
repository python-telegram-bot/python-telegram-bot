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
    InputFile,
    InputProfilePhoto,
    InputProfilePhotoAnimated,
    InputProfilePhotoStatic,
)
from telegram.constants import InputProfilePhotoType
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


class TestInputProfilePhotoWithoutRequest:
    def test_type_enum_conversion(self):
        instance = InputProfilePhoto(type="static")
        assert isinstance(instance.type, InputProfilePhotoType)
        assert instance.type is InputProfilePhotoType.STATIC

        instance = InputProfilePhoto(type="animated")
        assert isinstance(instance.type, InputProfilePhotoType)
        assert instance.type is InputProfilePhotoType.ANIMATED

        instance = InputProfilePhoto(type="unknown")
        assert isinstance(instance.type, str)
        assert instance.type == "unknown"


@pytest.fixture(scope="module")
def input_profile_photo_static():
    return InputProfilePhotoStatic(photo=InputProfilePhotoStaticTestBase.photo.read_bytes())


class InputProfilePhotoStaticTestBase:
    type_ = "static"
    photo = data_file("telegram.jpg")


class TestInputProfilePhotoStaticWithoutRequest(InputProfilePhotoStaticTestBase):
    def test_slot_behaviour(self, input_profile_photo_static):
        inst = input_profile_photo_static
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_profile_photo_static):
        inst = input_profile_photo_static
        assert inst.type == self.type_
        assert isinstance(inst.photo, InputFile)

    def test_to_dict(self, input_profile_photo_static):
        inst = input_profile_photo_static
        data = inst.to_dict()
        assert data["type"] == self.type_
        assert data["photo"] == inst.photo

    def test_with_local_file(self):
        inst = InputProfilePhotoStatic(photo=data_file("telegram.jpg"))
        assert inst.photo == data_file("telegram.jpg").as_uri()

    def test_type_enum_conversion(self, input_profile_photo_static):
        assert input_profile_photo_static.type is InputProfilePhotoType.STATIC


@pytest.fixture(scope="module")
def input_profile_photo_animated():
    return InputProfilePhotoAnimated(
        animation=InputProfilePhotoAnimatedTestBase.animation.read_bytes(),
        main_frame_timestamp=InputProfilePhotoAnimatedTestBase.main_frame_timestamp,
    )


class InputProfilePhotoAnimatedTestBase:
    type_ = "animated"
    animation = data_file("telegram2.mp4")
    main_frame_timestamp = dtm.timedelta(seconds=42, milliseconds=43)


class TestInputProfilePhotoAnimatedWithoutRequest(InputProfilePhotoAnimatedTestBase):
    def test_slot_behaviour(self, input_profile_photo_animated):
        inst = input_profile_photo_animated
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_profile_photo_animated):
        inst = input_profile_photo_animated
        assert inst.type == self.type_
        assert isinstance(inst.animation, InputFile)
        assert inst.main_frame_timestamp == self.main_frame_timestamp

    def test_to_dict(self, input_profile_photo_animated):
        inst = input_profile_photo_animated
        data = inst.to_dict()
        assert data["type"] == self.type_
        assert data["animation"] == inst.animation
        assert data["main_frame_timestamp"] == self.main_frame_timestamp.total_seconds()

    def test_with_local_file(self):
        inst = InputProfilePhotoAnimated(
            animation=data_file("telegram2.mp4"),
            main_frame_timestamp=self.main_frame_timestamp,
        )
        assert inst.animation == data_file("telegram2.mp4").as_uri()

    def test_type_enum_conversion(self, input_profile_photo_animated):
        assert input_profile_photo_animated.type is InputProfilePhotoType.ANIMATED

    @pytest.mark.parametrize(
        "timestamp",
        [
            dtm.timedelta(days=2),
            dtm.timedelta(seconds=2 * 24 * 60 * 60),
            2 * 24 * 60 * 60,
            float(2 * 24 * 60 * 60),
        ],
    )
    def test_main_frame_timestamp_conversion(self, timestamp):
        inst = InputProfilePhotoAnimated(
            animation=self.animation,
            main_frame_timestamp=timestamp,
        )
        assert isinstance(inst.main_frame_timestamp, dtm.timedelta)
        assert inst.main_frame_timestamp == dtm.timedelta(days=2)

        assert (
            InputProfilePhotoAnimated(
                animation=self.animation,
                main_frame_timestamp=None,
            ).main_frame_timestamp
            is None
        )
