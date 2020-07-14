#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2020
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

from telegram.ext import Defaults
from telegram import User


class TestDefault:
    def test_data_assignment(self, cdp):
        defaults = Defaults()

        with pytest.raises(AttributeError):
            defaults.parse_mode = True
        with pytest.raises(AttributeError):
            defaults.disable_notification = True
        with pytest.raises(AttributeError):
            defaults.disable_web_page_preview = True
        with pytest.raises(AttributeError):
            defaults.timeout = True
        with pytest.raises(AttributeError):
            defaults.quote = True

    def test_equality(self):
        a = Defaults(parse_mode='HTML', quote=True)
        b = Defaults(parse_mode='HTML', quote=True)
        c = Defaults(parse_mode='HTML', quote=False)
        d = Defaults(parse_mode='HTML', timeout=50)
        e = User(123, 'test_user', False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
