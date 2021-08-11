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
"""This module contains an object that represents a Telegram Proximity Alert."""
from typing import Any, Optional, TYPE_CHECKING

from telegram import TelegramObject, User
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class ProximityAlertTriggered(TelegramObject):
    """
    This object represents the content of a service message, sent whenever a user in the chat
    triggers a proximity alert set by another user.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`traveler`, :attr:`watcher` and :attr:`distance` are equal.

    Args:
        traveler (:class:`telegram.User`): User that triggered the alert
        watcher (:class:`telegram.User`): User that set the alert
        distance (:obj:`int`): The distance between the users

    Attributes:
        traveler (:class:`telegram.User`): User that triggered the alert
        watcher (:class:`telegram.User`): User that set the alert
        distance (:obj:`int`): The distance between the users

    """

    __slots__ = ('traveler', 'distance', 'watcher', '_id_attrs')

    def __init__(self, traveler: User, watcher: User, distance: int, **_kwargs: Any):
        self.traveler = traveler
        self.watcher = watcher
        self.distance = distance

        self._id_attrs = (self.traveler, self.watcher, self.distance)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['ProximityAlertTriggered']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['traveler'] = User.de_json(data.get('traveler'), bot)
        data['watcher'] = User.de_json(data.get('watcher'), bot)

        return cls(bot=bot, **data)
