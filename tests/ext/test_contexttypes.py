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

from telegram.ext import CallbackContext, ContextTypes
from tests.auxil.slots import mro_slots


class SubClass(CallbackContext):
    pass


class TestContextTypes:
    def test_slot_behaviour(self):
        instance = ContextTypes()
        for attr in instance.__slots__:
            assert getattr(instance, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(instance)) == len(set(mro_slots(instance))), "duplicate slot"

    def test_data_init(self):
        ct = ContextTypes(SubClass, int, float, bool)
        assert ct.context is SubClass
        assert ct.bot_data is int
        assert ct.chat_data is float
        assert ct.user_data is bool

        with pytest.raises(ValueError, match="subclass of CallbackContext"):
            ContextTypes(context=bool)

    def test_data_assignment(self):
        ct = ContextTypes()

        with pytest.raises(AttributeError):
            ct.bot_data = bool
        with pytest.raises(AttributeError):
            ct.user_data = bool
        with pytest.raises(AttributeError):
            ct.chat_data = bool
