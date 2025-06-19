#!/usr/bin/env python
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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

import datetime as dtm

from telegram import MessageAutoDeleteTimerChanged, VideoChatEnded
from telegram.warnings import PTBDeprecationWarning
from tests.auxil.slots import mro_slots


class TestMessageAutoDeleteTimerChangedWithoutRequest:
    message_auto_delete_time = dtm.timedelta(seconds=100)

    def test_slot_behaviour(self):
        action = MessageAutoDeleteTimerChanged(self.message_auto_delete_time)
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self):
        json_dict = {
            "message_auto_delete_time": int(self.message_auto_delete_time.total_seconds())
        }
        madtc = MessageAutoDeleteTimerChanged.de_json(json_dict, None)
        assert madtc.api_kwargs == {}

        assert madtc._message_auto_delete_time == self.message_auto_delete_time

    def test_to_dict(self):
        madtc = MessageAutoDeleteTimerChanged(self.message_auto_delete_time)
        madtc_dict = madtc.to_dict()

        assert isinstance(madtc_dict, dict)
        assert madtc_dict["message_auto_delete_time"] == int(
            self.message_auto_delete_time.total_seconds()
        )
        assert isinstance(madtc_dict["message_auto_delete_time"], int)

    def test_time_period_properties(self, PTB_TIMEDELTA):
        message_auto_delete_time = MessageAutoDeleteTimerChanged(
            self.message_auto_delete_time
        ).message_auto_delete_time

        if PTB_TIMEDELTA:
            assert message_auto_delete_time == self.message_auto_delete_time
            assert isinstance(message_auto_delete_time, dtm.timedelta)
        else:
            assert message_auto_delete_time == int(self.message_auto_delete_time.total_seconds())
            assert isinstance(message_auto_delete_time, int)

    def test_time_period_int_deprecated(self, recwarn, PTB_TIMEDELTA):
        MessageAutoDeleteTimerChanged(self.message_auto_delete_time).message_auto_delete_time

        if PTB_TIMEDELTA:
            assert len(recwarn) == 0
        else:
            assert len(recwarn) == 1
            assert "`message_auto_delete_time` will be of type `datetime.timedelta`" in str(
                recwarn[0].message
            )
            assert recwarn[0].category is PTBDeprecationWarning

    def test_equality(self):
        a = MessageAutoDeleteTimerChanged(100)
        b = MessageAutoDeleteTimerChanged(100)
        c = MessageAutoDeleteTimerChanged(50)
        d = VideoChatEnded(25)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
