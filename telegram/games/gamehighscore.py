#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains an object that represents a Telegram GameHighScore."""

from telegram import TelegramObject, User


class GameHighScore(TelegramObject):
    """This object represents one row of the high scores table for a game.

    Attributes:
        position (:obj:`int`): Position in high score table for the game.
        user (:class:`telegram.User`): User.
        score (:obj:`int`): Score.

    Args:
        position (:obj:`int`): Position in high score table for the game.
        user (:class:`telegram.User`): User.
        score (:obj:`int`): Score.

    """

    def __init__(self, position, user, score):
        self.position = position
        self.user = user
        self.score = score

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(GameHighScore, cls).de_json(data, bot)

        data['user'] = User.de_json(data.get('user'), bot)

        return cls(**data)
