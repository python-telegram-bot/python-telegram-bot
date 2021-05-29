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

from telegram import BotCommand, Dice


@pytest.fixture(scope="class")
def bot_command():
    return BotCommand(command='start', description='A command')


class TestBotCommand:
    command = 'start'
    description = 'A command'

    def test_slot_behaviour(self, bot_command, recwarn, mro_slots):
        for attr in bot_command.__slots__:
            assert getattr(bot_command, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not bot_command.__dict__, f"got missing slot(s): {bot_command.__dict__}"
        assert len(mro_slots(bot_command)) == len(set(mro_slots(bot_command))), "duplicate slot"
        bot_command.custom, bot_command.command = 'should give warning', self.command
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self, bot):
        json_dict = {'command': self.command, 'description': self.description}
        bot_command = BotCommand.de_json(json_dict, bot)

        assert bot_command.command == self.command
        assert bot_command.description == self.description

        assert BotCommand.de_json(None, bot) is None

    def test_to_dict(self, bot_command):
        bot_command_dict = bot_command.to_dict()

        assert isinstance(bot_command_dict, dict)
        assert bot_command_dict['command'] == bot_command.command
        assert bot_command_dict['description'] == bot_command.description

    def test_equality(self):
        a = BotCommand('start', 'some description')
        b = BotCommand('start', 'some description')
        c = BotCommand('start', 'some other description')
        d = BotCommand('hepl', 'some description')
        e = Dice(4, 'emoji')

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
