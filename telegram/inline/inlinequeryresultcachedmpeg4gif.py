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
"""This module contains the classes that represent Telegram InlineQueryResultMpeg4Gif."""

from dataclasses import dataclass
from telegram import InlineQueryResult
from telegram.utils.helpers import DEFAULT_NONE, DefaultValue
from typing import Any, Optional, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import InputMessageContent, ReplyMarkup


@dataclass(eq=False)
class InlineQueryResultCachedMpeg4Gif(InlineQueryResult):
    """
    Represents a link to a video animation (H.264/MPEG-4 AVC video without sound) stored on the
    Telegram servers. By default, this animated MPEG-4 file will be sent by the user with an
    optional caption. Alternatively, you can use :attr:`input_message_content` to send a message
    with the specified content instead of the animation.

    Attributes:
        type (:obj:`str`): 'mpeg4_gif'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        mpeg4_file_id (:obj:`str`): A valid file identifier for the MP4 file.
        title (:obj:`str`): Optional. Title for the result.
        caption (:obj:`str`): Optional. Caption of the MPEG-4 file to be sent, 0-1024 characters
            after entities parsing.
        parse_mode (:obj:`str`): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the MPEG-4 file.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        mpeg4_file_id (:obj:`str`): A valid file identifier for the MP4 file.
        title (:obj:`str`, optional): Title for the result.
        caption (:obj:`str`, optional): Caption of the MPEG-4 file to be sent, 0-1024 characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the MPEG-4 file.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    # Required
    id: str
    mpeg4_file_id: str
    # Optionals
    title: Optional[str] = None
    caption: Optional[str] = None
    reply_markup: Optional['ReplyMarkup'] = None
    input_message_content: Optional['InputMessageContent'] = None
    parse_mode: Optional[Union[str, DefaultValue]] = DEFAULT_NONE

    def __post_init__(self, **kwargs: Any) -> None:
        super().__init__('mpeg4_gif', self.id)
