#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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

from typing import TYPE_CHECKING, Optional

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class GameHighScore(TelegramObject):
    """This object represents one row of the high scores table for a game.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`position`, :attr:`user` and :attr:`score` are equal.

    Args:
        position (:obj:`int`): Position in high score table for the game.
        user (:class:`telegram.User`): User.
        score (:obj:`int`): Score.

    Attributes:
        position (:obj:`int`): Position in high score table for the game.
        user (:class:`telegram.User`): User.
        score (:obj:`int`): Score.

    """

    __slots__ = ("position", "user", "score")

    def __init__(self, position: int, user: User, score: int, *, api_kwargs: JSONDict = None):
        super().__init__(api_kwargs=api_kwargs)
        self.position = position
        self.user = user
        self.score = score

        self._id_attrs = (self.position, self.user, self.score)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["GameHighScore"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["user"] = User.de_json(data.get("user"), bot)

        return super().de_json(data=data, bot=bot)
