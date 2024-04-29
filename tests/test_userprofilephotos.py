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
# along with this program.  If not, see [http://www.gnu.org/licenses/].
from telegram import PhotoSize, UserProfilePhotos
from tests.auxil.slots import mro_slots


class TestUserProfilePhotosBase:
    total_count = 2
    photos = [
        [
            PhotoSize("file_id1", "file_un_id1", 512, 512),
            PhotoSize("file_id2", "file_un_id1", 512, 512),
        ],
        [
            PhotoSize("file_id3", "file_un_id3", 512, 512),
            PhotoSize("file_id4", "file_un_id4", 512, 512),
        ],
    ]


class TestUserProfilePhotosWithoutRequest(TestUserProfilePhotosBase):
    def test_slot_behaviour(self):
        inst = UserProfilePhotos(self.total_count, self.photos)
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {"total_count": 2, "photos": [[y.to_dict() for y in x] for x in self.photos]}
        user_profile_photos = UserProfilePhotos.de_json(json_dict, bot)
        assert user_profile_photos.api_kwargs == {}
        assert user_profile_photos.total_count == self.total_count
        assert user_profile_photos.photos == tuple(tuple(p) for p in self.photos)

    def test_to_dict(self):
        user_profile_photos = UserProfilePhotos(self.total_count, self.photos)
        user_profile_photos_dict = user_profile_photos.to_dict()
        assert user_profile_photos_dict["total_count"] == user_profile_photos.total_count
        for ix, x in enumerate(user_profile_photos_dict["photos"]):
            for iy, y in enumerate(x):
                assert y == user_profile_photos.photos[ix][iy].to_dict()

    def test_equality(self):
        a = UserProfilePhotos(2, self.photos)
        b = UserProfilePhotos(2, self.photos)
        c = UserProfilePhotos(1, [self.photos[0]])
        d = PhotoSize("file_id1", "unique_id", 512, 512)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
