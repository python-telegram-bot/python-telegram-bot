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
"""This module contains the classes that represent Telegram InlineQueryResultMpeg4Gif."""

from typing import TYPE_CHECKING, Any, List, Tuple, Union

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._messageentity import MessageEntity
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import ODVInput
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultMpeg4Gif(InlineQueryResult):
    """
    Represents a link to a video animation (H.264/MPEG-4 AVC video without sound). By default, this
    animated MPEG-4 file will be sent by the user with optional caption. Alternatively, you can
    use :attr:`input_message_content` to send a message with the specified content instead of the
    animation.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        mpeg4_url (:obj:`str`): A valid URL for the MP4 file. File size must not exceed 1MB.
        mpeg4_width (:obj:`int`, optional): Video width.
        mpeg4_height (:obj:`int`, optional): Video height.
        mpeg4_duration (:obj:`int`, optional): Video duration in seconds.
        thumb_url (:obj:`str`): URL of the static thumbnail (jpeg or gif) for the result.
        thumb_mime_type (:obj:`str`): Optional. MIME type of the thumbnail, must be one of
            ``'image/jpeg'``, ``'image/gif'``, or ``'video/mp4'``. Defaults to ``'image/jpeg'``.
        title (:obj:`str`, optional): Title for the result.
        caption (:obj:`str`, optional): Caption of the MPEG-4 file to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.constants.ParseMode` for the available modes.
        caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
            entities that appear in the caption, which can be specified instead of
            :paramref:`parse_mode`.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the video animation.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.MPEG4GIF`.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        mpeg4_url (:obj:`str`): A valid URL for the MP4 file. File size must not exceed 1MB.
        mpeg4_width (:obj:`int`): Optional. Video width.
        mpeg4_height (:obj:`int`): Optional. Video height.
        mpeg4_duration (:obj:`int`): Optional. Video duration in seconds.
        thumb_url (:obj:`str`): URL of the static (JPEG or GIF) or animated (MPEG4) thumbnail for
            the result.
        thumb_mime_type (:obj:`str`): Optional. MIME type of the thumbnail.
        title (:obj:`str`): Optional. Title for the result.
        caption (:obj:`str`): Optional. Caption of the MPEG-4 file to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.constants.ParseMode` for the available modes.
        caption_entities (List[:class:`telegram.MessageEntity`]): Optional. List of special
            entities that appear in the caption, which can be specified instead of
            :paramref:`parse_mode`.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the video animation.

    """

    __slots__ = (
        "reply_markup",
        "thumb_mime_type",
        "caption_entities",
        "mpeg4_duration",
        "mpeg4_width",
        "title",
        "caption",
        "parse_mode",
        "input_message_content",
        "mpeg4_url",
        "mpeg4_height",
        "thumb_url",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        mpeg4_url: str,
        thumb_url: str,
        mpeg4_width: int = None,
        mpeg4_height: int = None,
        title: str = None,
        caption: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        input_message_content: "InputMessageContent" = None,
        mpeg4_duration: int = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb_mime_type: str = None,
        caption_entities: Union[Tuple[MessageEntity, ...], List[MessageEntity]] = None,
        **_kwargs: Any,
    ):

        # Required
        super().__init__(InlineQueryResultType.MPEG4GIF, id)
        self.mpeg4_url = mpeg4_url
        self.thumb_url = thumb_url

        # Optional
        self.mpeg4_width = mpeg4_width
        self.mpeg4_height = mpeg4_height
        self.mpeg4_duration = mpeg4_duration
        self.title = title
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_mime_type = thumb_mime_type
