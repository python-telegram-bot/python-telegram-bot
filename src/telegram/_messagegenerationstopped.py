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
"""This module contains an object that represents a Telegram MessageGenerationStopped."""

from telegram._chat import Chat
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class MessageGenerationStopped(TelegramObject):
    """This object describes an update about a user stopping message generation.

    .. versionadded:: 22.9

    Args:
        chat (:class:`telegram.Chat`): Chat in which the message is generated.
        draft_id (:obj:`int`): Unique identifier of the message draft which was stopped.
        message_thread_id (:obj:`int`, optional): Unique identifier of the message thread in
            which the message is generated.

    Attributes:
        chat (:class:`telegram.Chat`): Chat in which the message is generated.
        draft_id (:obj:`int`): Unique identifier of the message draft which was stopped.
        message_thread_id (:obj:`int`): Optional. Unique identifier of the message thread in
            which the message is generated.
    """

    __slots__ = ("chat", "draft_id", "message_thread_id")

    def __init__(
        self,
        chat: Chat,
        draft_id: int,
        message_thread_id: int | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.chat: Chat = chat
        self.draft_id: int = draft_id
        self.message_thread_id: int | None = message_thread_id

        self._id_attrs = (self.chat, self.draft_id)

        self._freeze()
