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
"""This module contains the classes that represent Telegram InlineQueryResultContact."""

from typing import TYPE_CHECKING

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._utils.types import JSONDict
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultContact(InlineQueryResult):
    """
    Represents a contact with a phone number. By default, this contact will be sent by the user.
    Alternatively, you can use :attr:`input_message_content` to send a message with the specified
    content instead of the contact.

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

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.CONTACT`.
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

    """

    __slots__ = (
        "reply_markup",
        "thumb_width",
        "thumb_height",
        "vcard",
        "first_name",
        "last_name",
        "phone_number",
        "input_message_content",
        "thumb_url",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        phone_number: str,
        first_name: str,
        last_name: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        input_message_content: "InputMessageContent" = None,
        thumb_url: str = None,
        thumb_width: int = None,
        thumb_height: int = None,
        vcard: str = None,
        *,
        api_kwargs: JSONDict = None,
    ):
        # Required
        super().__init__(InlineQueryResultType.CONTACT, id, api_kwargs=api_kwargs)
        self.phone_number = phone_number
        self.first_name = first_name

        # Optionals
        self.last_name = last_name
        self.vcard = vcard
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
