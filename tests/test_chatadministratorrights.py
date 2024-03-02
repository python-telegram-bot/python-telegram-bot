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
import pytest

from telegram import ChatAdministratorRights
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def chat_admin_rights():
    return ChatAdministratorRights(
        can_change_info=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_pin_messages=True,
        can_promote_members=True,
        can_restrict_members=True,
        can_post_messages=True,
        can_edit_messages=True,
        can_manage_chat=True,
        can_manage_video_chats=True,
        can_manage_topics=True,
        is_anonymous=True,
        can_post_stories=True,
        can_edit_stories=True,
        can_delete_stories=True,
    )


class TestChatAdministratorRightsWithoutRequest:
    def test_slot_behaviour(self, chat_admin_rights):
        inst = chat_admin_rights
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, chat_admin_rights):
        json_dict = {
            "can_change_info": True,
            "can_delete_messages": True,
            "can_invite_users": True,
            "can_pin_messages": True,
            "can_promote_members": True,
            "can_restrict_members": True,
            "can_post_messages": True,
            "can_edit_messages": True,
            "can_manage_chat": True,
            "can_manage_video_chats": True,
            "can_manage_topics": True,
            "is_anonymous": True,
            "can_post_stories": True,
            "can_edit_stories": True,
            "can_delete_stories": True,
        }
        chat_administrator_rights_de = ChatAdministratorRights.de_json(json_dict, bot)
        assert chat_administrator_rights_de.api_kwargs == {}

        assert chat_admin_rights == chat_administrator_rights_de

    def test_to_dict(self, chat_admin_rights):
        car = chat_admin_rights
        admin_rights_dict = car.to_dict()

        assert isinstance(admin_rights_dict, dict)
        assert admin_rights_dict["can_change_info"] == car.can_change_info
        assert admin_rights_dict["can_delete_messages"] == car.can_delete_messages
        assert admin_rights_dict["can_invite_users"] == car.can_invite_users
        assert admin_rights_dict["can_pin_messages"] == car.can_pin_messages
        assert admin_rights_dict["can_promote_members"] == car.can_promote_members
        assert admin_rights_dict["can_restrict_members"] == car.can_restrict_members
        assert admin_rights_dict["can_post_messages"] == car.can_post_messages
        assert admin_rights_dict["can_edit_messages"] == car.can_edit_messages
        assert admin_rights_dict["can_manage_chat"] == car.can_manage_chat
        assert admin_rights_dict["is_anonymous"] == car.is_anonymous
        assert admin_rights_dict["can_manage_video_chats"] == car.can_manage_video_chats
        assert admin_rights_dict["can_manage_topics"] == car.can_manage_topics
        assert admin_rights_dict["can_post_stories"] == car.can_post_stories
        assert admin_rights_dict["can_edit_stories"] == car.can_edit_stories
        assert admin_rights_dict["can_delete_stories"] == car.can_delete_stories

    def test_equality(self):
        a = ChatAdministratorRights(
            True,
            *((False,) * 11),
            can_post_stories=False,
            can_edit_stories=False,
            can_delete_stories=False,
        )
        b = ChatAdministratorRights(
            True,
            *((False,) * 11),
            can_post_stories=False,
            can_edit_stories=False,
            can_delete_stories=False,
        )
        c = ChatAdministratorRights(
            *(False,) * 12,
            can_post_stories=False,
            can_edit_stories=False,
            can_delete_stories=False,
        )
        d = ChatAdministratorRights(
            True,
            True,
            *((False,) * 10),
            can_post_stories=False,
            can_edit_stories=False,
            can_delete_stories=False,
        )
        e = ChatAdministratorRights(
            True,
            True,
            *((False,) * 10),
            can_post_stories=False,
            can_edit_stories=False,
            can_delete_stories=False,
        )

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert d == e
        assert hash(d) == hash(e)

    def test_all_rights(self):
        f = ChatAdministratorRights(
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            can_post_stories=True,
            can_edit_stories=True,
            can_delete_stories=True,
        )
        t = ChatAdministratorRights.all_rights()
        # if the dirs are the same, the attributes will all be there
        assert dir(f) == dir(t)
        # now we just need to check that all attributes are True. __slots__ returns all values,
        # if a new one is added without defaulting to True, this will fail
        for key in t.__slots__:
            assert t[key] is True
        # and as a finisher, make sure the default is different.
        assert f != t

    def test_no_rights(self):
        f = ChatAdministratorRights(
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            can_post_stories=False,
            can_edit_stories=False,
            can_delete_stories=False,
        )
        t = ChatAdministratorRights.no_rights()
        # if the dirs are the same, the attributes will all be there
        assert dir(f) == dir(t)
        # now we just need to check that all attributes are True. __slots__ returns all values,
        # if a new one is added without defaulting to True, this will fail
        for key in t.__slots__:
            assert t[key] is False
        # and as a finisher, make sure the default is different.
        assert f != t

    def test_depreciation_typeerror(self):
        with pytest.raises(TypeError, match="must be set in order"):
            ChatAdministratorRights(
                *(False,) * 12,
            )
        with pytest.raises(TypeError, match="must be set in order"):
            ChatAdministratorRights(*(False,) * 12, can_edit_stories=True)
        with pytest.raises(TypeError, match="must be set in order"):
            ChatAdministratorRights(*(False,) * 12, can_post_stories=True)
        with pytest.raises(TypeError, match="must be set in order"):
            ChatAdministratorRights(*(False,) * 12, can_delete_stories=True)
        with pytest.raises(TypeError, match="must be set in order"):
            ChatAdministratorRights(*(False,) * 12, can_edit_stories=True, can_post_stories=True)
        with pytest.raises(TypeError, match="must be set in order"):
            ChatAdministratorRights(*(False,) * 12, can_delete_stories=True, can_post_stories=True)
