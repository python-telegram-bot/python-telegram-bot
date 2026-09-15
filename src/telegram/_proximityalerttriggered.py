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
"""This module contains an object that represents a Telegram Proximity Alert."""

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
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

    traveler: User = tg_field(compare=True)
    watcher: User = tg_field(compare=True)
    distance: int = tg_field(compare=True)
