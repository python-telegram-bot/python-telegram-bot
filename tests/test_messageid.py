#!/usr/bin/env python
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
from telegram import MessageId, User


@pytest.fixture(scope="class")
def message_id():
    return MessageId(message_id=TestMessageId.m_id)


class TestMessageId:
    m_id = 1234

    def test_slot_behaviour(self, message_id, recwarn, mro_slots):
        for attr in message_id.__slots__:
            assert getattr(message_id, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not message_id.__dict__, f"got missing slot(s): {message_id.__dict__}"
        assert len(mro_slots(message_id)) == len(set(mro_slots(message_id))), "duplicate slot"
        message_id.custom, message_id.message_id = 'should give warning', self.m_id
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self):
        json_dict = {'message_id': self.m_id}
        message_id = MessageId.de_json(json_dict, None)

        assert message_id.message_id == self.m_id

    def test_to_dict(self, message_id):
        message_id_dict = message_id.to_dict()

        assert isinstance(message_id_dict, dict)
        assert message_id_dict['message_id'] == message_id.message_id

    def test_equality(self):
        a = MessageId(message_id=1)
        b = MessageId(message_id=1)
        c = MessageId(message_id=2)
        d = User(id=1, first_name='name', is_bot=False)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
