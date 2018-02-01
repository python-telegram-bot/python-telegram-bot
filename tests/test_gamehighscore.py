#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from telegram import GameHighScore, User


@pytest.fixture(scope='class')
def game_highscore():
    return GameHighScore(TestGameHighScore.position,
                         TestGameHighScore.user,
                         TestGameHighScore.score)


class TestGameHighScore(object):
    position = 12
    user = User(2, 'test user', False)
    score = 42

    def test_de_json(self, bot):
        json_dict = {'position': self.position,
                     'user': self.user.to_dict(),
                     'score': self.score}
        highscore = GameHighScore.de_json(json_dict, bot)

        assert highscore.position == self.position
        assert highscore.user == self.user
        assert highscore.score == self.score

    def test_to_dict(self, game_highscore):
        game_highscore_dict = game_highscore.to_dict()

        assert isinstance(game_highscore_dict, dict)
        assert game_highscore_dict['position'] == game_highscore.position
        assert game_highscore_dict['user'] == game_highscore.user.to_dict()
        assert game_highscore_dict['score'] == game_highscore.score
