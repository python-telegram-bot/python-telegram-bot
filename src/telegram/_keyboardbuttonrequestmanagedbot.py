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
"""This module contains the object that represents a Telegram KeyboardButtonRequestManagedBot."""

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class KeyboardButtonRequestManagedBot(TelegramObject):
    """
    This object defines the parameters for the creation of a managed bot.
    Information about the created bot will be shared with the bot using the update
    managed_bot and a :obj:`telegram.Message` with the field
    :attr:`telegram.Message.managed_bot_created`.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`request_id` is equal.

    .. versionadded:: NEXT.VERSION

    Args:
        request_id (:obj:`int`): Signed 32-bit identifier of the request. Must be unique
            within the message.
        suggested_name (:obj:`str`, optional): Suggested name for the bot.
        suggested_username (:obj:`str`, optional): Suggested username for the bot.

    Attributes:
        request_id (:obj:`int`): Signed 32-bit identifier of the request. Must be unique
            within the message.
        suggested_name (:obj:`str`): Optional. Suggested name for the bot.
        suggested_username (:obj:`str`): Optional. Suggested username for the bot.
    """

    __slots__ = (
        "request_id",
        "suggested_name",
        "suggested_username",
    )

    def __init__(
        self,
        request_id: int,
        suggested_name: str | None = None,
        suggested_username: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.request_id: int = request_id
        # Optional
        self.suggested_name: str | None = suggested_name
        self.suggested_username: str | None = suggested_username

        self._id_attrs = (self.request_id,)
        self._freeze()
