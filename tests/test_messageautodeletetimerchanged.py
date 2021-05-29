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

from telegram import MessageAutoDeleteTimerChanged, VoiceChatEnded


class TestMessageAutoDeleteTimerChanged:
    message_auto_delete_time = 100

    def test_slot_behaviour(self, recwarn, mro_slots):
        action = MessageAutoDeleteTimerChanged(self.message_auto_delete_time)
        for attr in action.__slots__:
            assert getattr(action, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not action.__dict__, f"got missing slot(s): {action.__dict__}"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"
        action.custom = 'should give warning'
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self):
        json_dict = {'message_auto_delete_time': self.message_auto_delete_time}
        madtc = MessageAutoDeleteTimerChanged.de_json(json_dict, None)

        assert madtc.message_auto_delete_time == self.message_auto_delete_time

    def test_to_dict(self):
        madtc = MessageAutoDeleteTimerChanged(self.message_auto_delete_time)
        madtc_dict = madtc.to_dict()

        assert isinstance(madtc_dict, dict)
        assert madtc_dict["message_auto_delete_time"] == self.message_auto_delete_time

    def test_equality(self):
        a = MessageAutoDeleteTimerChanged(100)
        b = MessageAutoDeleteTimerChanged(100)
        c = MessageAutoDeleteTimerChanged(50)
        d = VoiceChatEnded(25)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
