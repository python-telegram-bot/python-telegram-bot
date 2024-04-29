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
import datetime

import pytest

from telegram import ChatInviteLink, User
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def creator():
    return User(1, "First name", False)


@pytest.fixture(scope="module")
def invite_link(creator):
    return ChatInviteLink(
        TestChatInviteLinkBase.link,
        creator,
        TestChatInviteLinkBase.creates_join_request,
        TestChatInviteLinkBase.primary,
        TestChatInviteLinkBase.revoked,
        expire_date=TestChatInviteLinkBase.expire_date,
        member_limit=TestChatInviteLinkBase.member_limit,
        name=TestChatInviteLinkBase.name,
        pending_join_request_count=TestChatInviteLinkBase.pending_join_request_count,
    )


class TestChatInviteLinkBase:
    link = "thisialink"
    creates_join_request = False
    primary = True
    revoked = False
    expire_date = datetime.datetime.now(datetime.timezone.utc)
    member_limit = 42
    name = "LinkName"
    pending_join_request_count = 42


class TestChatInviteLinkWithoutRequest(TestChatInviteLinkBase):
    def test_slot_behaviour(self, invite_link):
        for attr in invite_link.__slots__:
            assert getattr(invite_link, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(invite_link)) == len(set(mro_slots(invite_link))), "duplicate slot"

    def test_de_json_required_args(self, bot, creator):
        json_dict = {
            "invite_link": self.link,
            "creator": creator.to_dict(),
            "creates_join_request": self.creates_join_request,
            "is_primary": self.primary,
            "is_revoked": self.revoked,
        }

        invite_link = ChatInviteLink.de_json(json_dict, bot)
        assert invite_link.api_kwargs == {}

        assert invite_link.invite_link == self.link
        assert invite_link.creator == creator
        assert invite_link.creates_join_request == self.creates_join_request
        assert invite_link.is_primary == self.primary
        assert invite_link.is_revoked == self.revoked

    def test_de_json_all_args(self, bot, creator):
        json_dict = {
            "invite_link": self.link,
            "creator": creator.to_dict(),
            "creates_join_request": self.creates_join_request,
            "is_primary": self.primary,
            "is_revoked": self.revoked,
            "expire_date": to_timestamp(self.expire_date),
            "member_limit": self.member_limit,
            "name": self.name,
            "pending_join_request_count": str(self.pending_join_request_count),
        }

        invite_link = ChatInviteLink.de_json(json_dict, bot)
        assert invite_link.api_kwargs == {}

        assert invite_link.invite_link == self.link
        assert invite_link.creator == creator
        assert invite_link.creates_join_request == self.creates_join_request
        assert invite_link.is_primary == self.primary
        assert invite_link.is_revoked == self.revoked
        assert abs(invite_link.expire_date - self.expire_date) < datetime.timedelta(seconds=1)
        assert to_timestamp(invite_link.expire_date) == to_timestamp(self.expire_date)
        assert invite_link.member_limit == self.member_limit
        assert invite_link.name == self.name
        assert invite_link.pending_join_request_count == self.pending_join_request_count

    def test_de_json_localization(self, tz_bot, bot, raw_bot, creator):
        json_dict = {
            "invite_link": self.link,
            "creator": creator.to_dict(),
            "creates_join_request": self.creates_join_request,
            "is_primary": self.primary,
            "is_revoked": self.revoked,
            "expire_date": to_timestamp(self.expire_date),
            "member_limit": self.member_limit,
            "name": self.name,
            "pending_join_request_count": str(self.pending_join_request_count),
        }

        invite_link_raw = ChatInviteLink.de_json(json_dict, raw_bot)
        invite_link_bot = ChatInviteLink.de_json(json_dict, bot)
        invite_link_tz = ChatInviteLink.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        invite_offset = invite_link_tz.expire_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            invite_link_tz.expire_date.replace(tzinfo=None)
        )

        assert invite_link_raw.expire_date.tzinfo == UTC
        assert invite_link_bot.expire_date.tzinfo == UTC
        assert invite_offset == tz_bot_offset

    def test_to_dict(self, invite_link):
        invite_link_dict = invite_link.to_dict()
        assert isinstance(invite_link_dict, dict)
        assert invite_link_dict["creator"] == invite_link.creator.to_dict()
        assert invite_link_dict["invite_link"] == invite_link.invite_link
        assert invite_link_dict["creates_join_request"] == invite_link.creates_join_request
        assert invite_link_dict["is_primary"] == self.primary
        assert invite_link_dict["is_revoked"] == self.revoked
        assert invite_link_dict["expire_date"] == to_timestamp(self.expire_date)
        assert invite_link_dict["member_limit"] == self.member_limit
        assert invite_link_dict["name"] == self.name
        assert invite_link_dict["pending_join_request_count"] == self.pending_join_request_count

    def test_equality(self):
        a = ChatInviteLink("link", User(1, "", False), True, True, True)
        b = ChatInviteLink("link", User(1, "", False), True, True, True)
        c = ChatInviteLink("link", User(2, "", False), True, True, True)
        d1 = ChatInviteLink("link", User(1, "", False), False, True, True)
        d2 = ChatInviteLink("link", User(1, "", False), True, False, True)
        d3 = ChatInviteLink("link", User(1, "", False), True, True, False)
        e = ChatInviteLink("notalink", User(1, "", False), True, False, True)
        f = ChatInviteLink("notalink", User(1, "", False), True, True, True)
        g = User(1, "", False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d1
        assert hash(a) != hash(d1)

        assert a != d2
        assert hash(a) != hash(d2)

        assert d2 != d3
        assert hash(d2) != hash(d3)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)

        assert a != g
        assert hash(a) != hash(g)
