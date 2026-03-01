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
"""This module contains an object that represents a chat owner change in the chat."""

from typing import TYPE_CHECKING

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import de_json_optional
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class ChatOwnerChanged(TelegramObject):
    """This object represents a service message about an ownership change in the chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`new_owner` is equal.

    Args:
        new_owner (:class:`telegram.User`): The user which will be the new owner of the chat if
            the previous owner does not return to the chat

    Attributes:
        new_owner (:class:`telegram.User`): The user which will be the new owner of the chat if
            the previous owner does not return to the chat

    """

    __slots__ = ("new_owner",)

    def __init__(
        self,
        new_owner: User,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.new_owner: User = new_owner

        self._id_attrs = (self.new_owner,)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "ChatOwnerChanged":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["new_owner"] = de_json_optional(data.get("new_owner"), User, bot)

        return super().de_json(data=data, bot=bot)


class ChatOwnerLeft(TelegramObject):
    """This object represents a service message about the chat owner leaving the chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`new_owner` is equal.

    Args:
        new_owner (:class:`telegram.User`, optional): The user which will be the new owner of the
            chat if the previous owner does not return to the chat

    Attributes:
        new_owner (:class:`telegram.User`): Optional. The user which will be the new owner of the
            chat if the previous owner does not return to the chat

    """

    __slots__ = ("new_owner",)

    def __init__(
        self,
        new_owner: User | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.new_owner: User | None = new_owner

        self._id_attrs = (self.new_owner,)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "ChatOwnerLeft":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["new_owner"] = de_json_optional(data.get("new_owner"), User, bot)

        return super().de_json(data=data, bot=bot)
