#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
"""This module contains an object that represents a location to which a chat is connected."""

from typing import TYPE_CHECKING, Any, Optional

from telegram import TelegramObject
from telegram.utils.types import JSONDict

from .files.location import Location

if TYPE_CHECKING:
    from telegram import Bot


class ChatLocation(TelegramObject):
    """This object represents a location to which a chat is connected.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`location` is equal.

    Args:
        location (:class:`telegram.Location`): The location to which the supergroup is connected.
            Can't be a live location.
        address (:obj:`str`): Location address; 1-64 characters, as defined by the chat owner
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        location (:class:`telegram.Location`): The location to which the supergroup is connected.
        address (:obj:`str`): Location address, as defined by the chat owner

    """

    __slots__ = ('location', '_id_attrs', 'address')

    def __init__(
        self,
        location: Location,
        address: str,
        **_kwargs: Any,
    ):
        self.location = location
        self.address = address

        self._id_attrs = (self.location,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['ChatLocation']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['location'] = Location.de_json(data.get('location'), bot)

        return cls(bot=bot, **data)
