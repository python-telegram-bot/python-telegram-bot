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
"""This module contains the classes that represent Telegram InlineQueryResultGif."""

from dataclasses import dataclass
from telegram import InlineQueryResult
from telegram.utils.helpers import DEFAULT_NONE, DefaultValue
from typing import Any, Optional, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import InputMessageContent, ReplyMarkup


@dataclass(eq=False)
class InlineQueryResultGif(InlineQueryResult):
    """
    Represents a link to an animated GIF file. By default, this animated GIF file will be sent by
    the user with optional caption. Alternatively, you can use :attr:`input_message_content` to
    send a message with the specified content instead of the animation.

    Attributes:
        type (:obj:`str`): 'gif'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        gif_url (:obj:`str`): A valid URL for the GIF file. File size must not exceed 1MB.
        gif_width (:obj:`int`): Optional. Width of the GIF.
        gif_height (:obj:`int`): Optional. Height of the GIF.
        gif_duration (:obj:`int`): Optional. Duration of the GIF.
        thumb_url (:obj:`str`): URL of the static thumbnail for the result (jpeg or gif).
        thumb_mime_type (:obj:`str`): Optional. MIME type of the thumbnail.
        title (:obj:`str`): Optional. Title for the result.
        caption (:obj:`str`): Optional. Caption of the GIF file to be sent, 0-1024 characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the GIF animation.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        gif_url (:obj:`str`): A valid URL for the GIF file. File size must not exceed 1MB.
        gif_width (:obj:`int`, optional): Width of the GIF.
        gif_height (:obj:`int`, optional): Height of the GIF.
        gif_duration (:obj:`int`, optional): Duration of the GIF
        thumb_url (:obj:`str`): URL of the static thumbnail for the result (jpeg or gif).
        thumb_mime_type (:obj:`str`): Optional. MIME type of the thumbnail, must be one of
            “image/jpeg”, “image/gif”, or “video/mp4”. Defaults to “image/jpeg”.
        title (:obj:`str`, optional): Title for the result.
        caption (:obj:`str`, optional): Caption of the GIF file to be sent, 0-1024 characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the GIF animation.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    # Required
    id: str
    gif_url: str
    thumb_url: str
    # Optionals
    gif_width: Optional[int] = None
    gif_height: Optional[int] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    reply_markup: Optional['ReplyMarkup'] = None
    input_message_content: Optional['InputMessageContent'] = None
    gif_duration: Optional[int] = None
    parse_mode: Optional[Union[str, DefaultValue]] = DEFAULT_NONE
    thumb_mime_type: Optional[str] = None

    def __post_init__(self, **kwargs: Any) -> None:
        super().__init__('gif', self.id)
