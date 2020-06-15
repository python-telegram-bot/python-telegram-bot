#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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

from telegram import Dice


@pytest.fixture(scope="class",
                params=Dice.ALL_EMOJI)
def dice(request):
    return Dice(value=5, emoji=request.param)


class TestDice:
    value = 4

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
