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

from telegram import KeyboardButtonPollType, Poll


@pytest.fixture(scope='class')
def keyboard_button_poll_type():
    return KeyboardButtonPollType(TestKeyboardButtonPollType.type)


class TestKeyboardButtonPollType(object):
    type = Poll.QUIZ

    def test_to_dict(self, keyboard_button_poll_type):
        keyboard_button_poll_type_dict = keyboard_button_poll_type.to_dict()
        assert isinstance(keyboard_button_poll_type_dict, dict)
        assert keyboard_button_poll_type_dict['type'] == self.type

    def test_equality(self):
        a = KeyboardButtonPollType(Poll.QUIZ)
        b = KeyboardButtonPollType(Poll.QUIZ)
        c = KeyboardButtonPollType(Poll.REGULAR)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)
