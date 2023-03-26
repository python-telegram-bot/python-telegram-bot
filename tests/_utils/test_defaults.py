#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
import inspect

import pytest

from telegram import User
from telegram.ext import Defaults
from tests.auxil.envvars import TEST_WITH_OPT_DEPS
from tests.auxil.slots import mro_slots


class TestDefault:
    def test_slot_behaviour(self):
        a = Defaults(parse_mode="HTML", quote=True)
        for attr in a.__slots__:
            assert getattr(a, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(a)) == len(set(mro_slots(a))), "duplicate slot"

    def test_utc(self):
        defaults = Defaults()
        if not TEST_WITH_OPT_DEPS:
            assert defaults.tzinfo is dtm.timezone.utc
        else:
            assert defaults.tzinfo is not dtm.timezone.utc

    def test_data_assignment(self):
        defaults = Defaults()

        for name, _val in inspect.getmembers(Defaults, lambda x: isinstance(x, property)):
            with pytest.raises(AttributeError):
                setattr(defaults, name, True)

    def test_equality(self):
        a = Defaults(parse_mode="HTML", quote=True)
        b = Defaults(parse_mode="HTML", quote=True)
        c = Defaults(parse_mode="HTML", quote=True, protect_content=True)
        d = Defaults(parse_mode="HTML", protect_content=True)
        e = User(123, "test_user", False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
