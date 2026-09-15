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

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
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

    is_access_restricted: bool = tg_field(compare=True)
    added_users: tuple[User, ...] = tg_field(compare=True, converter=parse_sequence_arg)
