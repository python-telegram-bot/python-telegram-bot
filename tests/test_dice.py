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

from telegram import Dice, BotCommand


@pytest.fixture(scope="class", params=Dice.ALL_EMOJI)
def dice(request):
    return Dice(value=5, emoji=request.param)


class TestDice:
    value = 4

    def test_slot_behaviour(self, dice, recwarn, mro_slots):
        for attr in dice.__slots__:
            assert getattr(dice, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not dice.__dict__, f"got missing slot(s): {dice.__dict__}"
        assert len(mro_slots(dice)) == len(set(mro_slots(dice))), "duplicate slot"
        dice.custom, dice.value = 'should give warning', self.value
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    @pytest.mark.parametrize('emoji', Dice.ALL_EMOJI)
    def test_de_json(self, bot, emoji):
        json_dict = {'value': self.value, 'emoji': emoji}
        dice = Dice.de_json(json_dict, bot)

        assert dice.value == self.value
        assert dice.emoji == emoji
        assert Dice.de_json(None, bot) is None

    def test_to_dict(self, dice):
        dice_dict = dice.to_dict()

        assert isinstance(dice_dict, dict)
        assert dice_dict['value'] == dice.value
        assert dice_dict['emoji'] == dice.emoji

    def test_equality(self):
        a = Dice(3, '🎯')
        b = Dice(3, '🎯')
        c = Dice(3, '🎲')
        d = Dice(4, '🎯')
        e = BotCommand('start', 'description')

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
