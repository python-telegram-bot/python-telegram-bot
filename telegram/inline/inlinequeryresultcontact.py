#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
"""This module contains the classes that represent Telegram InlineQueryResultContact."""

from dataclasses import dataclass
from telegram import InlineQueryResult
from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import ReplyMarkup, InputMessageContent


@dataclass(eq=False)
class InlineQueryResultContact(InlineQueryResult):
    """
    Represents a contact with a phone number. By default, this contact will be sent by the user.
    Alternatively, you can use :attr:`input_message_content` to send a message with the specified
    content instead of the contact.

    Attributes:
        type (:obj:`str`): 'contact'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        phone_number (:obj:`str`): Contact's phone number.
        first_name (:obj:`str`): Contact's first name.
        last_name (:obj:`str`): Optional. Contact's last name.
        vcard (:obj:`str`): Optional. Additional data about the contact in the form of a vCard,
            0-2048 bytes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the contact.
        thumb_url (:obj:`str`): Optional. Url of the thumbnail for the result.
        thumb_width (:obj:`int`): Optional. Thumbnail width.
        thumb_height (:obj:`int`): Optional. Thumbnail height.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        phone_number (:obj:`str`): Contact's phone number.
        first_name (:obj:`str`): Contact's first name.
        last_name (:obj:`str`, optional): Contact's last name.
        vcard (:obj:`str`, optional): Additional data about the contact in the form of a vCard,
            0-2048 bytes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the contact.
        thumb_url (:obj:`str`, optional): Url of the thumbnail for the result.
        thumb_width (:obj:`int`, optional): Thumbnail width.
        thumb_height (:obj:`int`, optional): Thumbnail height.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    # Required
    id: str
    phone_number: str
    first_name: str
    # Optionals
    last_name: Optional[str] = None
    reply_markup: Optional['ReplyMarkup'] = None
    input_message_content: Optional['InputMessageContent'] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None
    vcard: Optional[str] = None

    def __post_init__(self, **kwargs: Any) -> None:
        super().__init__('contact', self.id)
