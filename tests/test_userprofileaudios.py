#!/usr/bin/env python
#
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
from telegram import Audio, UserProfileAudios
from tests.auxil.slots import mro_slots


class UserProfileAudiosTestBase:
    total_count = 2
    audios = [
        Audio("file_id1", "unique_id1", 512, "file_name1"),
        Audio("file_id2", "unique_id2", 512, "file_name2"),
    ]


class TestUserProfileAudiosWithoutRequest(UserProfileAudiosTestBase):
    def test_slot_behaviour(self):
        inst = UserProfileAudios(self.total_count, self.audios)
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"total_count": 2, "audios": [x.to_dict() for x in self.audios]}
        user_profile_audios = UserProfileAudios.de_json(json_dict, offline_bot)
        assert user_profile_audios.api_kwargs == {}
        assert user_profile_audios.total_count == self.total_count
        assert user_profile_audios.audios == tuple(self.audios)

    def test_to_dict(self):
        user_profile_audios = UserProfileAudios(self.total_count, self.audios)
        user_profile_audios_dict = user_profile_audios.to_dict()
        assert user_profile_audios_dict["total_count"] == user_profile_audios.total_count
        for ix, x in enumerate(user_profile_audios_dict["audios"]):
            assert x == user_profile_audios.audios[ix].to_dict()

    def test_equality(self):
        a = UserProfileAudios(2, self.audios)
        b = UserProfileAudios(2, self.audios)
        c = UserProfileAudios(1, [self.audios[0]])
        d = Audio("file_id1", "unique_id1", 512, "file_name1")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
