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

from sys import version_info as py_ver

from telegram.ext import Handler


class TestHandler:
    def test_slot_behaviour(self, recwarn, mro_slots):
        class SubclassHandler(Handler):
            __slots__ = ()

            def __init__(self):
                super().__init__(lambda x: None)

            def check_update(self, update: object):
                pass

        inst = SubclassHandler()
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        assert '__dict__' not in Handler.__slots__ if py_ver < (3, 7) else True, 'dict in abc'
        inst.custom = 'should not give warning'
        assert len(recwarn) == 0, recwarn.list
