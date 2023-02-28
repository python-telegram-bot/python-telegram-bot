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

from telegram import ChatPermissions, User
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def chat_permissions():
    return ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_change_info=True,
        can_invite_users=True,
        can_pin_messages=True,
        can_manage_topics=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
    )


class TestChatPermissionsBase:
    can_send_messages = True
    can_send_media_messages = True
    can_send_polls = True
    can_send_other_messages = False
    can_add_web_page_previews = False
    can_change_info = False
    can_invite_users = None
    can_pin_messages = None
    can_manage_topics = None
    can_send_audios = True
    can_send_documents = False
    can_send_photos = None
    can_send_videos = True
    can_send_video_notes = False
    can_send_voice_notes = None


class TestChatPermissionsWithoutRequest(TestChatPermissionsBase):
    def test_slot_behaviour(self, chat_permissions):
        inst = chat_permissions
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "can_send_messages": self.can_send_messages,
            "can_send_media_messages": self.can_send_media_messages,
            "can_send_polls": self.can_send_polls,
            "can_send_other_messages": self.can_send_other_messages,
            "can_add_web_page_previews": self.can_add_web_page_previews,
            "can_change_info": self.can_change_info,
            "can_invite_users": self.can_invite_users,
            "can_pin_messages": self.can_pin_messages,
            "can_send_audios": self.can_send_audios,
            "can_send_documents": self.can_send_documents,
            "can_send_photos": self.can_send_photos,
            "can_send_videos": self.can_send_videos,
            "can_send_video_notes": self.can_send_video_notes,
            "can_send_voice_notes": self.can_send_voice_notes,
        }
        permissions = ChatPermissions.de_json(json_dict, bot)
        assert permissions.api_kwargs == {}

        assert permissions.can_send_messages == self.can_send_messages
        assert permissions.can_send_media_messages == self.can_send_media_messages
        assert permissions.can_send_polls == self.can_send_polls
        assert permissions.can_send_other_messages == self.can_send_other_messages
        assert permissions.can_add_web_page_previews == self.can_add_web_page_previews
        assert permissions.can_change_info == self.can_change_info
        assert permissions.can_invite_users == self.can_invite_users
        assert permissions.can_pin_messages == self.can_pin_messages
        assert permissions.can_manage_topics == self.can_manage_topics
        assert permissions.can_send_audios == self.can_send_audios
        assert permissions.can_send_documents == self.can_send_documents
        assert permissions.can_send_photos == self.can_send_photos
        assert permissions.can_send_videos == self.can_send_videos
        assert permissions.can_send_video_notes == self.can_send_video_notes
        assert permissions.can_send_voice_notes == self.can_send_voice_notes

    def test_to_dict(self, chat_permissions):
        permissions_dict = chat_permissions.to_dict()

        assert isinstance(permissions_dict, dict)
        assert permissions_dict["can_send_messages"] == chat_permissions.can_send_messages
        assert (
            permissions_dict["can_send_media_messages"] == chat_permissions.can_send_media_messages
        )
        assert permissions_dict["can_send_polls"] == chat_permissions.can_send_polls
        assert (
            permissions_dict["can_send_other_messages"] == chat_permissions.can_send_other_messages
        )
        assert (
            permissions_dict["can_add_web_page_previews"]
            == chat_permissions.can_add_web_page_previews
        )
        assert permissions_dict["can_change_info"] == chat_permissions.can_change_info
        assert permissions_dict["can_invite_users"] == chat_permissions.can_invite_users
        assert permissions_dict["can_pin_messages"] == chat_permissions.can_pin_messages
        assert permissions_dict["can_manage_topics"] == chat_permissions.can_manage_topics
        assert permissions_dict["can_send_audios"] == chat_permissions.can_send_audios
        assert permissions_dict["can_send_documents"] == chat_permissions.can_send_documents
        assert permissions_dict["can_send_photos"] == chat_permissions.can_send_photos
        assert permissions_dict["can_send_videos"] == chat_permissions.can_send_videos
        assert permissions_dict["can_send_video_notes"] == chat_permissions.can_send_video_notes
        assert permissions_dict["can_send_voice_notes"] == chat_permissions.can_send_voice_notes

    def test_equality(self):
        a = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=False,
        )
        b = ChatPermissions(
            can_send_polls=True,
            can_send_other_messages=False,
            can_send_messages=True,
            can_send_media_messages=True,
        )
        c = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=False,
        )
        d = User(123, "", False)
        e = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=False,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
        )

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        # we expect this to be true since we don't compare these in V20
        assert a == e
        assert hash(a) == hash(e)

    def test_all_permissions(self):
        f = ChatPermissions()
        t = ChatPermissions.all_permissions()
        # if the dirs are the same, the attributes will all be there
        assert dir(f) == dir(t)
        # now we just need to check that all attributes are True. _id_attrs returns all values,
        # if a new one is added without defaulting to True, this will fail
        for key in t.__slots__:
            assert t[key] is True
        # and as a finisher, make sure the default is different.
        assert f != t

    def test_no_permissions(self):
        f = ChatPermissions()
        t = ChatPermissions.no_permissions()
        # if the dirs are the same, the attributes will all be there
        assert dir(f) == dir(t)
        # now we just need to check that all attributes are True. _id_attrs returns all values,
        # if a new one is added without defaulting to False, this will fail
        for key in t.__slots__:
            assert t[key] is False
        # and as a finisher, make sure the default is different.
        assert f != t

    def test_equality_warning(self, recwarn, chat_permissions):
        recwarn.clear()
        assert chat_permissions == chat_permissions

        assert str(recwarn[0].message) == (
            "In v21, granular media settings will be considered as well when comparing"
            " ChatPermissions instances."
        )
