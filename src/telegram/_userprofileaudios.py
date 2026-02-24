#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""This module contains an object that represents a Telegram UserProfileAudios."""

from collections.abc import Sequence
from typing import TYPE_CHECKING

from telegram._files.audio import Audio
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class UserProfileAudios(TelegramObject):
    """
    This object represents the audios displayed on a user's profile.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`total_count` and :attr:`audios` are equal.

    .. versionadded:: NEXT.VERSION

    Args:
        total_count (:obj:`int`): Total number of profile audios for the target user.
        audios (Sequence[:class:`telegram.Audio`]): Requested profile audios.

    Attributes:
        total_count (:obj:`int`): Total number of profile audios for the target user.
        audios (tuple[:class:`telegram.Audio`]): Requested profile audios.

    """

    __slots__ = ("audios", "total_count")

    def __init__(
        self,
        total_count: int,
        audios: Sequence[Audio],
        *,
        api_kwargs: JSONDict | None = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.total_count = total_count
        self.audios = tuple(audios)

        self._id_attrs = (self.total_count, self.audios)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "UserProfileAudios":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["audios"] = Audio.de_list(data.get("audios", []), bot)

        return super().de_json(data=data, bot=bot)
