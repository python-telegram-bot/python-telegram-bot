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
"""This module contains objects that represent Telegram Community and related service messages."""

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class Community(TelegramObject):
    """Represents a community (a group of chats).

    .. versionadded:: 22.9

    Args:
        id (:obj:`int`): Unique identifier for this community.
        name (:obj:`str`): Name of the community.

    Attributes:
        id (:obj:`int`): Unique identifier for this community.
        name (:obj:`str`): Name of the community.
    """

    __slots__ = ("id", "name")

    def __init__(
        self,
        id: int,  # pylint: disable=redefined-builtin
        name: str,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.id: int = id
        self.name: str = name

        self._id_attrs = (self.id,)

        self._freeze()


class CommunityChatJoined(TelegramObject):
    """Describes a service message about a chat being joined by a user from a community.

    .. versionadded:: 22.9

    Args:
        community (:class:`telegram.Community`): The community from which the chat was joined.

    Attributes:
        community (:class:`telegram.Community`): The community from which the chat was joined.
    """

    __slots__ = ("community",)

    def __init__(
        self,
        community: Community,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.community: Community = community

        self._id_attrs = (self.community,)

        self._freeze()
