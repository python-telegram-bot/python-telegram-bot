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
from flaky import flaky

from telegram import ForceReply, ReplyKeyboardRemove


@pytest.fixture(scope='class')
def force_reply():
    return ForceReply(
        TestForceReply.force_reply,
        TestForceReply.selective,
        TestForceReply.input_field_placeholder,
    )


class TestForceReply:
    force_reply = True
    selective = True
    input_field_placeholder = 'force replies can be annoying if not used properly'

    def test_slot_behaviour(self, force_reply, recwarn, mro_slots):
        for attr in force_reply.__slots__:
            assert getattr(force_reply, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not force_reply.__dict__, f"got missing slot(s): {force_reply.__dict__}"
        assert len(mro_slots(force_reply)) == len(set(mro_slots(force_reply))), "duplicate slot"
        force_reply.custom, force_reply.force_reply = 'should give warning', self.force_reply
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    @flaky(3, 1)
    def test_send_message_with_force_reply(self, bot, chat_id, force_reply):
        message = bot.send_message(chat_id, 'text', reply_markup=force_reply)

        assert message.text == 'text'

    def test_expected(self, force_reply):
        assert force_reply.force_reply == self.force_reply
        assert force_reply.selective == self.selective
        assert force_reply.input_field_placeholder == self.input_field_placeholder

    def test_to_dict(self, force_reply):
        force_reply_dict = force_reply.to_dict()

        assert isinstance(force_reply_dict, dict)
        assert force_reply_dict['force_reply'] == force_reply.force_reply
        assert force_reply_dict['selective'] == force_reply.selective
        assert force_reply_dict['input_field_placeholder'] == force_reply.input_field_placeholder

    def test_equality(self):
        a = ForceReply(True, False)
        b = ForceReply(False, False)
        c = ForceReply(True, True)
        d = ReplyKeyboardRemove()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
