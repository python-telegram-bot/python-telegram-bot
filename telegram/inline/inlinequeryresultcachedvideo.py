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
"""This module contains the classes that represent Telegram InlineQueryResultCachedVideo."""

from telegram import InlineQueryResult
from telegram.utils.helpers import DEFAULT_NONE, DefaultValue
from typing import Any, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import InputMessageContent, ReplyMarkup


class InlineQueryResultCachedVideo(InlineQueryResult):
    """
    Represents a link to a video file stored on the Telegram servers. By default, this video file
    will be sent by the user with an optional caption. Alternatively, you can use
    :attr:`input_message_content` to send a message with the specified content instead
    of the video.

    Attributes:
        type (:obj:`str`): 'video'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        video_file_id (:obj:`str`): A valid file identifier for the video file.
        title (:obj:`str`): Title for the result.
        description (:obj:`str`): Optional. Short description of the result.
        caption (:obj:`str`): Optional. Caption of the video to be sent, 0-1024 characters after
            entities parsing.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the video.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        video_file_id (:obj:`str`): A valid file identifier for the video file.
        title (:obj:`str`): Title for the result.
        description (:obj:`str`, optional): Short description of the result.
        caption (:obj:`str`, optional): Caption of the video to be sent, 0-1024 characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the video.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id: str,
                 video_file_id: str,
                 title: str,
                 description: str = None,
                 caption: str = None,
                 reply_markup: 'ReplyMarkup' = None,
                 input_message_content: 'InputMessageContent' = None,
                 parse_mode: Union[str, DefaultValue] = DEFAULT_NONE,
                 **kwargs: Any):
        # Required
        super().__init__('video', id)
        self.video_file_id = video_file_id
        self.title = title

        # Optionals
        self.description = description
        self.caption = caption
        self.parse_mode = parse_mode
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
