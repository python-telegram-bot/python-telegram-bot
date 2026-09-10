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
"""This module contains the DirectMessagesTopic class."""

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class DirectMessagesTopic(TelegramObject):
    """
    This class represents a topic for direct messages in a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`topic_id` and :attr:`user` is equal.

    .. versionadded:: 22.4

    Args:
        topic_id (:obj:`int`): Unique identifier of the topic. This number may have more than 32
            significant bits and some programming languages may have difficulty/silent defects in
            interpreting it. But it has at most 52 significant bits, so a 64-bit integer or
            double-precision float type are safe for storing this identifier.
        user (:class:`telegram.User`, optional): Information about the user that created the topic.

            .. hint::
                According to Telegram, this field is always present as of Bot API 9.2.

    Attributes:
        topic_id (:obj:`int`): Unique identifier of the topic. This number may have more than 32
            significant bits and some programming languages may have difficulty/silent defects in
            interpreting it. But it has at most 52 significant bits, so a 64-bit integer or
            double-precision float type are safe for storing this identifier.
        user (:class:`telegram.User`): Optional. Information about the user that created the topic.

            .. hint::
                According to Telegram, this field is always present as of Bot API 9.2.

    """

    # Required:
    topic_id: int = tg_field(compare=True)

    # Optionals:
    user: User | None = tg_field(compare=True, default=None)
