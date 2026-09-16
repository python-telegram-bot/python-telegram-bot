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
"""This module contains an object that represents a Telegram EphemeralMessageParameters."""

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class EphemeralMessageParameters(TelegramObject):
    """This object contains parameters of the ephemeral message to send.

    .. versionadded:: 22.9

    Args:
        receiver_user_id (:obj:`int`): Identifier of the user who will receive the message.
        callback_query_id (:obj:`str`, optional): Identifier of the callback query which triggered
            the message, if any.
        replace_callback_query_message (:obj:`bool`, optional): Pass :obj:`True` if the ephemeral
            message must be shown in place of the original message.

    Attributes:
        receiver_user_id (:obj:`int`): Identifier of the user who will receive the message.
        callback_query_id (:obj:`str`): Optional. Identifier of the callback query which triggered
            the message, if any.
        replace_callback_query_message (:obj:`bool`): Optional. Pass :obj:`True` if the ephemeral
            message must be shown in place of the original message.
    """

    __slots__ = (
        "callback_query_id",
        "receiver_user_id",
        "replace_callback_query_message",
    )

    def __init__(
        self,
        receiver_user_id: int,
        callback_query_id: str | None = None,
        replace_callback_query_message: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.receiver_user_id: int = receiver_user_id
        self.callback_query_id: str | None = callback_query_id
        self.replace_callback_query_message: bool | None = replace_callback_query_message

        self._id_attrs = (
            self.receiver_user_id,
            self.callback_query_id,
            self.replace_callback_query_message,
        )

        self._freeze()
