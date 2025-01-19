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

from copy import deepcopy

import pytest

from telegram import (
    Dice,
    PaidMedia,
    PaidMediaInfo,
    PaidMediaPhoto,
    PaidMediaPreview,
    PaidMediaPurchased,
    PaidMediaVideo,
    PhotoSize,
    User,
    Video,
)
from telegram.constants import PaidMediaType
from tests.auxil.slots import mro_slots


@pytest.fixture
def paid_media():
    return PaidMedia(type=PaidMediaType.PHOTO)


class PaidMediaTestBase:
    type = PaidMediaType.PHOTO
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


class TestPaidMediaWithoutRequest(PaidMediaTestBase):
    def test_slot_behaviour(self, paid_media):
        inst = paid_media
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self, paid_media):
        assert type(PaidMedia("photo").type) is PaidMediaType
        assert PaidMedia("unknown").type == "unknown"

    def test_de_json(self, offline_bot):
        data = {"type": "unknown"}
        paid_media = PaidMedia.de_json(data, offline_bot)
        assert paid_media.api_kwargs == {}
        assert paid_media.type == "unknown"

    @pytest.mark.parametrize(
        ("pm_type", "subclass"),
        [
            ("photo", PaidMediaPhoto),
            ("video", PaidMediaVideo),
            ("preview", PaidMediaPreview),
        ],
    )
    def test_de_json_subclass(self, offline_bot, pm_type, subclass):
        json_dict = {
            "type": pm_type,
            "video": self.video.to_dict(),
            "photo": [p.to_dict() for p in self.photo],
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
        }
        pm = PaidMedia.de_json(json_dict, offline_bot)

        assert type(pm) is subclass
        assert set(pm.api_kwargs.keys()) == set(json_dict.keys()) - set(subclass.__slots__) - {
            "type"
        }
        assert pm.type == pm_type

    def test_to_dict(self, paid_media):
        assert paid_media.to_dict() == {"type": paid_media.type}

    def test_equality(self, paid_media):
        a = paid_media
        b = PaidMedia(self.type)
        c = PaidMedia("unknown")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def paid_media_photo():
    return PaidMediaPhoto(
        photo=TestPaidMediaPhotoWithoutRequest.photo,
    )


class TestPaidMediaPhotoWithoutRequest(PaidMediaTestBase):
    type = PaidMediaType.PHOTO

    def test_slot_behaviour(self, paid_media_photo):
        inst = paid_media_photo
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "photo": [p.to_dict() for p in self.photo],
        }
        pmp = PaidMediaPhoto.de_json(json_dict, offline_bot)
        assert pmp.photo == tuple(self.photo)
        assert pmp.api_kwargs == {}

    def test_to_dict(self, paid_media_photo):
        assert paid_media_photo.to_dict() == {
            "type": paid_media_photo.type,
            "photo": [p.to_dict() for p in self.photo],
        }

    def test_equality(self, paid_media_photo):
        a = paid_media_photo
        b = PaidMediaPhoto(deepcopy(self.photo))
        c = PaidMediaPhoto([PhotoSize("file_id", 640, 480, "file_unique_id")])
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def paid_media_video():
    return PaidMediaVideo(
        video=TestPaidMediaVideoWithoutRequest.video,
    )


class TestPaidMediaVideoWithoutRequest(PaidMediaTestBase):
    type = PaidMediaType.VIDEO

    def test_slot_behaviour(self, paid_media_video):
        inst = paid_media_video
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "video": self.video.to_dict(),
        }
        pmv = PaidMediaVideo.de_json(json_dict, offline_bot)
        assert pmv.video == self.video
        assert pmv.api_kwargs == {}

    def test_to_dict(self, paid_media_video):
        assert paid_media_video.to_dict() == {
            "type": self.type,
            "video": paid_media_video.video.to_dict(),
        }

    def test_equality(self, paid_media_video):
        a = paid_media_video
        b = PaidMediaVideo(
            video=deepcopy(self.video),
        )
        c = PaidMediaVideo(
            video=Video("test", "test_unique", 640, 480, 60),
        )
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def paid_media_preview():
    return PaidMediaPreview(
        width=TestPaidMediaPreviewWithoutRequest.width,
        height=TestPaidMediaPreviewWithoutRequest.height,
        duration=TestPaidMediaPreviewWithoutRequest.duration,
    )


class TestPaidMediaPreviewWithoutRequest(PaidMediaTestBase):
    type = PaidMediaType.PREVIEW

    def test_slot_behaviour(self, paid_media_preview):
        inst = paid_media_preview
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
        }
        pmp = PaidMediaPreview.de_json(json_dict, offline_bot)
        assert pmp.width == self.width
        assert pmp.height == self.height
        assert pmp.duration == self.duration
        assert pmp.api_kwargs == {}

    def test_to_dict(self, paid_media_preview):
        assert paid_media_preview.to_dict() == {
            "type": paid_media_preview.type,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
        }

    def test_equality(self, paid_media_preview):
        a = paid_media_preview
        b = PaidMediaPreview(
            width=self.width,
            height=self.height,
            duration=self.duration,
        )
        c = PaidMediaPreview(
            width=100,
            height=100,
            duration=100,
        )
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


# ===========================================================================================
# ===========================================================================================
# ===========================================================================================
# ===========================================================================================
# ===========================================================================================
# ===========================================================================================
# ===========================================================================================
# ===========================================================================================
# ===========================================================================================
# ===========================================================================================


@pytest.fixture(scope="module")
def paid_media_info():
    return PaidMediaInfo(
        star_count=PaidMediaInfoTestBase.star_count,
        paid_media=PaidMediaInfoTestBase.paid_media,
    )


@pytest.fixture(scope="module")
def paid_media_purchased():
    return PaidMediaPurchased(
        from_user=PaidMediaPurchasedTestBase.from_user,
        paid_media_payload=PaidMediaPurchasedTestBase.paid_media_payload,
    )


class PaidMediaInfoTestBase:
    star_count = 200
    paid_media = [
        PaidMediaVideo(
            video=Video(
                file_id="video_file_id",
                width=640,
                height=480,
                file_unique_id="file_unique_id",
                duration=60,
            )
        ),
        PaidMediaPhoto(
            photo=[
                PhotoSize(
                    file_id="photo_file_id",
                    width=640,
                    height=480,
                    file_unique_id="file_unique_id",
                )
            ]
        ),
    ]


class TestPaidMediaInfoWithoutRequest(PaidMediaInfoTestBase):
    def test_slot_behaviour(self, paid_media_info):
        inst = paid_media_info
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "star_count": self.star_count,
            "paid_media": [t.to_dict() for t in self.paid_media],
        }
        pmi = PaidMediaInfo.de_json(json_dict, offline_bot)
        assert pmi.paid_media == tuple(self.paid_media)
        assert pmi.star_count == self.star_count

    def test_to_dict(self, paid_media_info):
        assert paid_media_info.to_dict() == {
            "star_count": self.star_count,
            "paid_media": [t.to_dict() for t in self.paid_media],
        }

    def test_equality(self):
        pmi1 = PaidMediaInfo(star_count=self.star_count, paid_media=self.paid_media)
        pmi2 = PaidMediaInfo(star_count=self.star_count, paid_media=self.paid_media)
        pmi3 = PaidMediaInfo(star_count=100, paid_media=[self.paid_media[0]])

        assert pmi1 == pmi2
        assert hash(pmi1) == hash(pmi2)

        assert pmi1 != pmi3
        assert hash(pmi1) != hash(pmi3)


class PaidMediaPurchasedTestBase:
    from_user = User(1, "user", False)
    paid_media_payload = "payload"


class TestPaidMediaPurchasedWithoutRequest(PaidMediaPurchasedTestBase):
    def test_slot_behaviour(self, paid_media_purchased):
        inst = paid_media_purchased
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "from": self.from_user.to_dict(),
            "paid_media_payload": self.paid_media_payload,
        }
        pmp = PaidMediaPurchased.de_json(json_dict, bot)
        assert pmp.from_user == self.from_user
        assert pmp.paid_media_payload == self.paid_media_payload
        assert pmp.api_kwargs == {}

    def test_to_dict(self, paid_media_purchased):
        assert paid_media_purchased.to_dict() == {
            "from": self.from_user.to_dict(),
            "paid_media_payload": self.paid_media_payload,
        }

    def test_equality(self):
        pmp1 = PaidMediaPurchased(
            from_user=self.from_user,
            paid_media_payload=self.paid_media_payload,
        )
        pmp2 = PaidMediaPurchased(
            from_user=self.from_user,
            paid_media_payload=self.paid_media_payload,
        )
        pmp3 = PaidMediaPurchased(
            from_user=User(2, "user", False),
            paid_media_payload="other",
        )

        assert pmp1 == pmp2
        assert hash(pmp1) == hash(pmp2)

        assert pmp1 != pmp3
        assert hash(pmp1) != hash(pmp3)
