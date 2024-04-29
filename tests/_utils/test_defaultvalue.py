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
import pytest

from telegram import User
from telegram._utils.defaultvalue import DefaultValue
from tests.auxil.slots import mro_slots


class TestDefaultValue:
    def test_slot_behaviour(self):
        inst = DefaultValue(1)
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_identity(self):
        df_1 = DefaultValue(1)
        df_2 = DefaultValue(2)
        assert df_1 is not df_2
        assert df_1 != df_2

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ({}, False),
            ({1: 2}, True),
            (None, False),
            (True, True),
            (1, True),
            (0, False),
            (False, False),
            ([], False),
            ([1], True),
        ],
    )
    def test_truthiness(self, value, expected):
        assert bool(DefaultValue(value)) == expected

    @pytest.mark.parametrize(
        "value", ["string", 1, True, [1, 2, 3], {1: 3}, DefaultValue(1), User(1, "first", False)]
    )
    def test_string_representations(self, value):
        df = DefaultValue(value)
        assert str(df) == f"DefaultValue({value})"
        assert repr(df) == repr(value)

    def test_as_function_argument(self):
        default_one = DefaultValue(1)

        def foo(arg=default_one):
            if arg is default_one:
                return 1
            return 2

        assert foo() == 1
        assert foo(None) == 2
        assert foo(1) == 2
