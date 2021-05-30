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

from telegram import ReplyKeyboardRemove


@pytest.fixture(scope='class')
def reply_keyboard_remove():
    return ReplyKeyboardRemove(selective=TestReplyKeyboardRemove.selective)


class TestReplyKeyboardRemove:
    remove_keyboard = True
    selective = True

    def test_slot_behaviour(self, reply_keyboard_remove, recwarn, mro_slots):
        inst = reply_keyboard_remove
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.selective = 'should give warning', self.selective
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    @flaky(3, 1)
    def test_send_message_with_reply_keyboard_remove(self, bot, chat_id, reply_keyboard_remove):
        message = bot.send_message(chat_id, 'Text', reply_markup=reply_keyboard_remove)

        assert message.text == 'Text'

    def test_expected_values(self, reply_keyboard_remove):
        assert reply_keyboard_remove.remove_keyboard == self.remove_keyboard
        assert reply_keyboard_remove.selective == self.selective

    def test_to_dict(self, reply_keyboard_remove):
        reply_keyboard_remove_dict = reply_keyboard_remove.to_dict()

        assert (
            reply_keyboard_remove_dict['remove_keyboard'] == reply_keyboard_remove.remove_keyboard
        )
        assert reply_keyboard_remove_dict['selective'] == reply_keyboard_remove.selective
