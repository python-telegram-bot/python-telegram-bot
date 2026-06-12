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
"""This module contains an object that represents a Telegram Bot Access Settings."""

from collections.abc import Sequence
from typing import TYPE_CHECKING

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import de_list_optional, parse_sequence_arg
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class BotAccessSettings(TelegramObject):
    """
    This object describes the access settings of a bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`is_access_restricted` and :attr:`added_users` are equal.

    .. versionadded:: 22.8

    Args:
        is_access_restricted (:obj:`bool`): :obj:`True`, if only selected users can access the bot.
            The bot's owner can always access it.
        added_users (Sequence[:class:`telegram.User`], optional): The list of other users who
            have access to the bot if the access is restricted.

    Attributes:
        is_access_restricted (:obj:`bool`): :obj:`True`, if only selected users can access the bot.
            The bot's owner can always access it.
        added_users (Sequence[:class:`telegram.User`]): Optional. The list of other users who
            have access to the bot if the access is restricted.
    """

    __slots__ = ("added_users", "is_access_restricted")

    def __init__(
        self,
        is_access_restricted: bool,
        added_users: Sequence[User] | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.is_access_restricted: bool = is_access_restricted
        self.added_users: tuple[User, ...] = parse_sequence_arg(added_users)

        self._id_attrs = (self.is_access_restricted, self.added_users)
        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "BotAccessSettings":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)
        data["added_users"] = de_list_optional(data.get("added_users"), User, bot)

        return super().de_json(data=data, bot=bot)
