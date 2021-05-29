#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from telegram import User, ChatInviteLink
from telegram.utils.helpers import to_timestamp


@pytest.fixture(scope='class')
def creator():
    return User(1, 'First name', False)


@pytest.fixture(scope='class')
def invite_link(creator):
    return ChatInviteLink(
        TestChatInviteLink.link,
        creator,
        TestChatInviteLink.primary,
        TestChatInviteLink.revoked,
        expire_date=TestChatInviteLink.expire_date,
        member_limit=TestChatInviteLink.member_limit,
    )


class TestChatInviteLink:

    link = "thisialink"
    primary = True
    revoked = False
    expire_date = datetime.datetime.utcnow()
    member_limit = 42

    def test_slot_behaviour(self, recwarn, mro_slots, invite_link):
        for attr in invite_link.__slots__:
            assert getattr(invite_link, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not invite_link.__dict__, f"got missing slot(s): {invite_link.__dict__}"
        assert len(mro_slots(invite_link)) == len(set(mro_slots(invite_link))), "duplicate slot"
        invite_link.custom = 'should give warning'
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json_required_args(self, bot, creator):
        json_dict = {
            'invite_link': self.link,
            'creator': creator.to_dict(),
            'is_primary': self.primary,
            'is_revoked': self.revoked,
        }

        invite_link = ChatInviteLink.de_json(json_dict, bot)

        assert invite_link.invite_link == self.link
        assert invite_link.creator == creator
        assert invite_link.is_primary == self.primary
        assert invite_link.is_revoked == self.revoked

    def test_de_json_all_args(self, bot, creator):
        json_dict = {
            'invite_link': self.link,
            'creator': creator.to_dict(),
            'is_primary': self.primary,
            'is_revoked': self.revoked,
            'expire_date': to_timestamp(self.expire_date),
            'member_limit': self.member_limit,
        }

        invite_link = ChatInviteLink.de_json(json_dict, bot)

        assert invite_link.invite_link == self.link
        assert invite_link.creator == creator
        assert invite_link.is_primary == self.primary
        assert invite_link.is_revoked == self.revoked
        assert pytest.approx(invite_link.expire_date == self.expire_date)
        assert to_timestamp(invite_link.expire_date) == to_timestamp(self.expire_date)
        assert invite_link.member_limit == self.member_limit

    def test_to_dict(self, invite_link):
        invite_link_dict = invite_link.to_dict()
        assert isinstance(invite_link_dict, dict)
        assert invite_link_dict['creator'] == invite_link.creator.to_dict()
        assert invite_link_dict['invite_link'] == invite_link.invite_link
        assert invite_link_dict['is_primary'] == self.primary
        assert invite_link_dict['is_revoked'] == self.revoked
        assert invite_link_dict['expire_date'] == to_timestamp(self.expire_date)
        assert invite_link_dict['member_limit'] == self.member_limit

    def test_equality(self):
        a = ChatInviteLink("link", User(1, '', False), True, True)
        b = ChatInviteLink("link", User(1, '', False), True, True)
        d = ChatInviteLink("link", User(2, '', False), False, True)
        d2 = ChatInviteLink("notalink", User(1, '', False), False, True)
        d3 = ChatInviteLink("notalink", User(1, '', False), True, True)
        e = User(1, '', False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != d2
        assert hash(a) != hash(d2)

        assert d2 != d3
        assert hash(d2) != hash(d3)

        assert a != e
        assert hash(a) != hash(e)
