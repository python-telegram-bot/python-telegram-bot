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

import pytest

from telegram import Location, ChatLocation, User


@pytest.fixture(scope='class')
def chat_location(bot):
    return ChatLocation(TestChatLocation.location, TestChatLocation.address)


class TestChatLocation:
    location = Location(123, 456)
    address = 'The Shire'

    def test_slot_behaviour(self, chat_location, recwarn, mro_slots):
        inst = chat_location
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.address = 'should give warning', self.address
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self, bot):
        json_dict = {
            'location': self.location.to_dict(),
            'address': self.address,
        }
        chat_location = ChatLocation.de_json(json_dict, bot)

        assert chat_location.location == self.location
        assert chat_location.address == self.address

    def test_to_dict(self, chat_location):
        chat_location_dict = chat_location.to_dict()

        assert isinstance(chat_location_dict, dict)
        assert chat_location_dict['location'] == chat_location.location.to_dict()
        assert chat_location_dict['address'] == chat_location.address

    def test_equality(self, chat_location):
        a = chat_location
        b = ChatLocation(self.location, self.address)
        c = ChatLocation(self.location, 'Mordor')
        d = ChatLocation(Location(456, 132), self.address)
        e = User(456, '', False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
