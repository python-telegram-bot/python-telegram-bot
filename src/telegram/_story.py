#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
"""This module contains an object related to a Telegram Story."""

from typing import TYPE_CHECKING, Optional

from telegram._chat import Chat
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class Story(TelegramObject):
    """
    This object represents a story.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`chat` and :attr:`id` are equal.

    .. versionadded:: 20.5

    .. versionchanged:: 21.0
        Added attributes :attr:`chat` and :attr:`id` and equality based on them.

    Args:
        chat (:class:`telegram.Chat`): Chat that posted the story.
        id (:obj:`int`): Unique identifier for the story in the chat.

    Attributes:
        chat (:class:`telegram.Chat`): Chat that posted the story.
        id (:obj:`int`): Unique identifier for the story in the chat.

    """

    __slots__ = (
        "chat",
        "id",
    )

    def __init__(
        self,
        chat: Chat,
        id: int,  # pylint: disable=redefined-builtin
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.chat: Chat = chat
        self.id: int = id

        self._id_attrs = (self.chat, self.id)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "Story":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["chat"] = Chat.de_json(data.get("chat", {}), bot)
        return super().de_json(data=data, bot=bot)
