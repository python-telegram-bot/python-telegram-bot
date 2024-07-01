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
# along with this program. If not, see [http://www.gnu.org/licenses/].

from copy import deepcopy

import pytest

from telegram import (
    Dice,
    PaidMedia,
    PaidMediaInfo,
    PaidMediaPhoto,
    PaidMediaPreview,
    PaidMediaVideo,
    PhotoSize,
    Video,
)
from telegram.constants import PaidMediaType
from tests.auxil.slots import mro_slots


@pytest.fixture(
    scope="module",
    params=[
        PaidMedia.PREVIEW,
        PaidMedia.PHOTO,
        PaidMedia.VIDEO,
    ],
)
def pm_scope_type(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        PaidMediaPreview,
        PaidMediaPhoto,
        PaidMediaVideo,
    ],
    ids=[
        PaidMedia.PREVIEW,
        PaidMedia.PHOTO,
        PaidMedia.VIDEO,
    ],
)
def pm_scope_class(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        (
            PaidMediaPreview,
            PaidMedia.PREVIEW,
        ),
        (
            PaidMediaPhoto,
            PaidMedia.PHOTO,
        ),
        (
            PaidMediaVideo,
            PaidMedia.VIDEO,
        ),
    ],
    ids=[
        PaidMedia.PREVIEW,
        PaidMedia.PHOTO,
        PaidMedia.VIDEO,
    ],
)
def pm_scope_class_and_type(request):
    return request.param


@pytest.fixture(scope="module")
def paid_media(pm_scope_class_and_type):
    # We use de_json here so that we don't have to worry about which class gets which arguments
    return pm_scope_class_and_type[0].de_json(
        {
            "type": pm_scope_class_and_type[1],
            "width": TestPaidMediaBase.width,
            "height": TestPaidMediaBase.height,
            "duration": TestPaidMediaBase.duration,
            "video": TestPaidMediaBase.video.to_dict(),
            "photo": [p.to_dict() for p in TestPaidMediaBase.photo],
        },
        bot=None,
    )


def paid_media_video():
    return PaidMediaVideo(video=TestPaidMediaBase.video)


def paid_media_photo():
    return PaidMediaPhoto(photo=TestPaidMediaBase.photo)


@pytest.fixture(scope="module")
def paid_media_info():
    return PaidMediaInfo(
        star_count=TestPaidMediaInfoBase.star_count,
        paid_media=[paid_media_video(), paid_media_photo()],
    )


class TestPaidMediaBase:
    width = 640
    height = 480
    duration = 60
    video = Video(
        file_id="video_file_id",
        width=640,
        height=480,
        file_unique_id="file_unique_id",
        duration=60,
    )
    photo = (
        PhotoSize(
            file_id="photo_file_id",
            width=640,
            height=480,
            file_unique_id="file_unique_id",
        ),
    )


class TestPaidMediaWithoutRequest(TestPaidMediaBase):
    def test_slot_behaviour(self, paid_media):
        inst = paid_media
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, pm_scope_class_and_type):
        cls = pm_scope_class_and_type[0]
        type_ = pm_scope_class_and_type[1]

        json_dict = {
            "type": type_,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "video": self.video.to_dict(),
            "photo": [p.to_dict() for p in self.photo],
        }
        pm = PaidMedia.de_json(json_dict, bot)
        assert set(pm.api_kwargs.keys()) == {
            "width",
            "height",
            "duration",
            "video",
            "photo",
        } - set(cls.__slots__)

        assert isinstance(pm, PaidMedia)
        assert type(pm) is cls
        assert pm.type == type_
        if "width" in cls.__slots__:
            assert pm.width == self.width
            assert pm.height == self.height
            assert pm.duration == self.duration
        if "video" in cls.__slots__:
            assert pm.video == self.video
        if "photo" in cls.__slots__:
            assert pm.photo == self.photo

        assert cls.de_json(None, bot) is None
        assert PaidMedia.de_json({}, bot) is None

    def test_de_json_invalid_type(self, bot):
        json_dict = {
            "type": "invalid",
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "video": self.video.to_dict(),
            "photo": [p.to_dict() for p in self.photo],
        }
        pm = PaidMedia.de_json(json_dict, bot)
        assert pm.api_kwargs == {
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "video": self.video.to_dict(),
            "photo": [p.to_dict() for p in self.photo],
        }

        assert type(pm) is PaidMedia
        assert pm.type == "invalid"

    def test_de_json_subclass(self, pm_scope_class, bot):
        """This makes sure that e.g. PaidMediaPreivew(data) never returns a
        TransactionPartnerPhoto instance."""
        json_dict = {
            "type": "invalid",
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "video": self.video.to_dict(),
            "photo": [p.to_dict() for p in self.photo],
        }
        assert type(pm_scope_class.de_json(json_dict, bot)) is pm_scope_class

    def test_to_dict(self, paid_media):
        pm_dict = paid_media.to_dict()

        assert isinstance(pm_dict, dict)
        assert pm_dict["type"] == paid_media.type
        if hasattr(paid_media_info, "width"):
            assert pm_dict["width"] == paid_media.width
            assert pm_dict["height"] == paid_media.height
            assert pm_dict["duration"] == paid_media.duration
        if hasattr(paid_media_info, "video"):
            assert pm_dict["video"] == paid_media.video.to_dict()
        if hasattr(paid_media_info, "photo"):
            assert pm_dict["photo"] == [p.to_dict() for p in paid_media.photo]

    def test_type_enum_conversion(self):
        assert type(PaidMedia("video").type) is PaidMediaType
        assert PaidMedia("unknown").type == "unknown"

    def test_equality(self, paid_media, bot):
        a = PaidMedia("base_type")
        b = PaidMedia("base_type")
        c = paid_media
        d = deepcopy(paid_media)
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)

        if hasattr(c, "video"):
            json_dict = c.to_dict()
            json_dict["video"] = Video("different", "d2", 1, 1, 1).to_dict()
            f = c.__class__.de_json(json_dict, bot)

            assert c != f
            assert hash(c) != hash(f)

        if hasattr(c, "photo"):
            json_dict = c.to_dict()
            json_dict["photo"] = [PhotoSize("different", "d2", 1, 1, 1).to_dict()]
            f = c.__class__.de_json(json_dict, bot)

            assert c != f
            assert hash(c) != hash(f)


class TestPaidMediaInfoBase:
    star_count = 200
    paid_media = [paid_media_video(), paid_media_photo()]


class TestPaidMediaInfoWithoutRequest(TestPaidMediaInfoBase):
    def test_slot_behaviour(self, paid_media_info):
        inst = paid_media_info
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "star_count": self.star_count,
            "paid_media": [t.to_dict() for t in self.paid_media],
        }
        pmi = PaidMediaInfo.de_json(json_dict, bot)
        pmi_none = PaidMediaInfo.de_json(None, bot)
        assert pmi.paid_media == tuple(self.paid_media)
        assert pmi.star_count == self.star_count
        assert pmi_none is None

    def test_to_dict(self, paid_media_info):
        assert paid_media_info.to_dict() == {
            "star_count": self.star_count,
            "paid_media": [t.to_dict() for t in self.paid_media],
        }

    def test_equality(self):
        pmi1 = PaidMediaInfo(
            star_count=self.star_count, paid_media=[paid_media_video(), paid_media_photo()]
        )
        pmi2 = PaidMediaInfo(
            star_count=self.star_count, paid_media=[paid_media_video(), paid_media_photo()]
        )
        pmi3 = PaidMediaInfo(star_count=100, paid_media=[paid_media_photo()])

        assert pmi1 == pmi2
        assert hash(pmi1) == hash(pmi2)

        assert pmi1 != pmi3
        assert hash(pmi1) != hash(pmi3)
