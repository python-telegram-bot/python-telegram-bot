#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
"""This module contains an object that represents a Telegram KeyboardButton."""

from typing import Any

from telegram import TelegramObject, KeyboardButtonPollType


class KeyboardButton(TelegramObject):
    """
    This object represents one button of the reply keyboard. For simple text buttons String can be
    used instead of this object to specify text of the button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`text`, :attr:`request_contact`, :attr:`request_location` and
    :attr:`request_poll` are equal.

    Note:
        * Optional fields are mutually exclusive.
        * :attr:`request_contact` and :attr:`request_location` options will only work in Telegram
          versions released after 9 April, 2016. Older clients will ignore them.
        * :attr:`request_poll` option will only work in Telegram versions released after 23
          January, 2020. Older clients will receive unsupported message.

    Args:
        text (:obj:`str`): Text of the button. If none of the optional fields are used, it will be
            sent to the bot as a message when the button is pressed.
        request_contact (:obj:`bool`, optional): If :obj:`True`, the user's phone number will be
            sent as a contact when the button is pressed. Available in private chats only.
        request_location (:obj:`bool`, optional): If :obj:`True`, the user's current location will
            be sent when the button is pressed. Available in private chats only.
        request_poll (:class:`KeyboardButtonPollType`, optional): If specified, the user will be
            asked to create a poll and send it to the bot when the button is pressed. Available in
            private chats only.

    Attributes:
        text (:obj:`str`): Text of the button.
        request_contact (:obj:`bool`): Optional. The user's phone number will be sent.
        request_location (:obj:`bool`): Optional. The user's current location will be sent.
        request_poll (:class:`KeyboardButtonPollType`): Optional. If the user should create a poll.

    """

    __slots__ = ('request_location', 'request_contact', 'request_poll', 'text', '_id_attrs')

    def __init__(
        self,
        text: str,
        request_contact: bool = None,
        request_location: bool = None,
        request_poll: KeyboardButtonPollType = None,
        **_kwargs: Any,
    ):
        # Required
        self.text = text
        # Optionals
        self.request_contact = request_contact
        self.request_location = request_location
        self.request_poll = request_poll

        self._id_attrs = (
            self.text,
            self.request_contact,
            self.request_location,
            self.request_poll,
        )
