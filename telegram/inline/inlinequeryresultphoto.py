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
"""This module contains the classes that represent Telegram InlineQueryResultPhoto."""

from dataclasses import dataclass
from telegram import InlineQueryResult
from telegram.utils.helpers import DEFAULT_NONE, DefaultValue
from typing import Any, Optional, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import InputMessageContent, ReplyMarkup


@dataclass(eq=False)
class InlineQueryResultPhoto(InlineQueryResult):
    """
    Represents a link to a photo. By default, this photo will be sent by the user with optional
    caption. Alternatively, you can use :attr:`input_message_content` to send a message with the
    specified content instead of the photo.

    Attributes:
        type (:obj:`str`): 'photo'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        photo_url (:obj:`str`): A valid URL of the photo. Photo must be in jpeg format. Photo size
            must not exceed 5MB.
        thumb_url (:obj:`str`): URL of the thumbnail for the photo.
        photo_width (:obj:`int`): Optional. Width of the photo.
        photo_height (:obj:`int`): Optional. Height of the photo.
        title (:obj:`str`): Optional. Title for the result.
        description (:obj:`str`): Optional. Short description of the result.
        caption (:obj:`str`): Optional. Caption of the photo to be sent, 0-1024 characters after
            entities parsing.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the photo.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        photo_url (:obj:`str`): A valid URL of the photo. Photo must be in jpeg format. Photo size
            must not exceed 5MB.
        thumb_url (:obj:`str`): URL of the thumbnail for the photo.
        photo_width (:obj:`int`, optional): Width of the photo.
        photo_height (:obj:`int`, optional): Height of the photo.
        title (:obj:`str`, optional): Title for the result.
        description (:obj:`str`, optional): Short description of the result.
        caption (:obj:`str`, optional): Caption of the photo to be sent, 0-1024 characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the photo.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    # Required
    id: str
    photo_url: str
    thumb_url: str
    # Optionals
    photo_width: Optional[int] = None
    photo_height: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    reply_markup: Optional['ReplyMarkup'] = None
    input_message_content: Optional['InputMessageContent'] = None
    parse_mode: Optional[Union[str, DefaultValue]] = DEFAULT_NONE

    def __post_init__(self, **kwargs: Any) -> None:
        super().__init__('photo', self.id)
        self.photo_width = int(self.photo_width) if self.photo_width is not None else None
        self.photo_height = int(self.photo_height) if self.photo_height is not None else None
