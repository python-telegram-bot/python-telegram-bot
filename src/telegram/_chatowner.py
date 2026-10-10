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

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class ChatOwnerChanged(TelegramObject):
    """This object represents a service message about an ownership change in the chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`new_owner` is equal.

    .. versionadded:: 22.7

    Args:
        new_owner (:class:`telegram.User`): The new owner of the chat

    Attributes:
        new_owner (:class:`telegram.User`): The new owner of the chat

    """

    new_owner: User = tg_field(compare=True)


@tg_dataclass()
class ChatOwnerLeft(TelegramObject):
    """This object represents a service message about the chat owner leaving the chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`new_owner` is equal.

    .. versionadded:: 22.7

    Args:
        new_owner (:class:`telegram.User`, optional): The user who will become the new owner of the
            chat if the previous owner does not return to the chat

    Attributes:
        new_owner (:class:`telegram.User`): Optional. The user who will become the new owner of the
            chat if the previous owner does not return to the chat

    """

    new_owner: User | None = tg_field(compare=True, default=None)
