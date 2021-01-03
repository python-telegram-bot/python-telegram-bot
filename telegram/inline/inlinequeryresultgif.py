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
# pylint: disable=W0622
"""This module contains the classes that represent Telegram InlineQueryResultGif."""

from typing import TYPE_CHECKING, Any, Union, Tuple, List

from telegram import InlineQueryResult, MessageEntity
from telegram.utils.helpers import DEFAULT_NONE, DefaultValue

if TYPE_CHECKING:
    from telegram import InputMessageContent, ReplyMarkup


class InlineQueryResultGif(InlineQueryResult):
    """
    Represents a link to an animated GIF file. By default, this animated GIF file will be sent by
    the user with optional caption. Alternatively, you can use :attr:`input_message_content` to
    send a message with the specified content instead of the animation.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        gif_url (:obj:`str`): A valid URL for the GIF file. File size must not exceed 1MB.
        gif_width (:obj:`int`, optional): Width of the GIF.
        gif_height (:obj:`int`, optional): Height of the GIF.
        gif_duration (:obj:`int`, optional): Duration of the GIF
        thumb_url (:obj:`str`): URL of the static (JPEG or GIF) or animated (MPEG4) thumbnail for
            the result.
        thumb_mime_type (:obj:`str`, optional): MIME type of the thumbnail, must be one of
            ``'image/jpeg'``, ``'image/gif'``, or ``'video/mp4'``. Defaults to ``'image/jpeg'``.
        title (:obj:`str`, optional): Title for the result.
        caption (:obj:`str`, optional): Caption of the GIF file to be sent, 0-1024 characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
            entities that appear in the caption, which can be specified instead of
            :attr:`parse_mode`.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the GIF animation.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        type (:obj:`str`): 'gif'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        gif_url (:obj:`str`): A valid URL for the GIF file. File size must not exceed 1MB.
        gif_width (:obj:`int`): Optional. Width of the GIF.
        gif_height (:obj:`int`): Optional. Height of the GIF.
        gif_duration (:obj:`int`): Optional. Duration of the GIF.
        thumb_url (:obj:`str`): URL of the static (JPEG or GIF) or animated (MPEG4) thumbnail for
            the result.
        thumb_mime_type (:obj:`str`): Optional. MIME type of the thumbnail.
        title (:obj:`str`): Optional. Title for the result.
        caption (:obj:`str`): Optional. Caption of the GIF file to be sent, 0-1024 characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        caption_entities (List[:class:`telegram.MessageEntity`]): Optional. List of special
            entities that appear in the caption, which can be specified instead of
            :attr:`parse_mode`.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the GIF animation.

    """

    def __init__(
        self,
        id: str,  # pylint: disable=W0622
        gif_url: str,
        thumb_url: str,
        gif_width: int = None,
        gif_height: int = None,
        title: str = None,
        caption: str = None,
        reply_markup: 'ReplyMarkup' = None,
        input_message_content: 'InputMessageContent' = None,
        gif_duration: int = None,
        parse_mode: Union[str, DefaultValue] = DEFAULT_NONE,
        thumb_mime_type: str = None,
        caption_entities: Union[Tuple[MessageEntity, ...], List[MessageEntity]] = None,
        **_kwargs: Any,
    ):

        # Required
        super().__init__('gif', id)
        self.gif_url = gif_url
        self.thumb_url = thumb_url

        # Optionals
        self.gif_width = gif_width
        self.gif_height = gif_height
        self.gif_duration = gif_duration
        self.title = title
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_mime_type = thumb_mime_type
