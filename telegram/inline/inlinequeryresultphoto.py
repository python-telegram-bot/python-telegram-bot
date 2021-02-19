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
"""This module contains the classes that represent Telegram InlineQueryResultPhoto."""

from typing import TYPE_CHECKING, Any, Union, Tuple, List

from telegram import InlineQueryResult, MessageEntity
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import ODVInput

if TYPE_CHECKING:
    from telegram import InputMessageContent, ReplyMarkup


class InlineQueryResultPhoto(InlineQueryResult):
    """
    Represents a link to a photo. By default, this photo will be sent by the user with optional
    caption. Alternatively, you can use :attr:`input_message_content` to send a message with the
    specified content instead of the photo.

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
        caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
            entities that appear in the caption, which can be specified instead of
            :attr:`parse_mode`.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the photo.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

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
        caption_entities (List[:class:`telegram.MessageEntity`]): Optional. List of special
            entities that appear in the caption, which can be specified instead of
            :attr:`parse_mode`.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the photo.

    """

    __slots__ = (
        'photo_url',
        'reply_markup',
        'caption_entities',
        'photo_width',
        'caption',
        'title',
        'description',
        'parse_mode',
        'input_message_content',
        'photo_height',
        'thumb_url',
    )

    def __init__(
        self,
        id: str,  # pylint: disable=W0622
        photo_url: str,
        thumb_url: str,
        photo_width: int = None,
        photo_height: int = None,
        title: str = None,
        description: str = None,
        caption: str = None,
        reply_markup: 'ReplyMarkup' = None,
        input_message_content: 'InputMessageContent' = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[Tuple[MessageEntity, ...], List[MessageEntity]] = None,
        **_kwargs: Any,
    ):
        # Required
        super().__init__('photo', id)
        self.photo_url = photo_url
        self.thumb_url = thumb_url

        # Optionals
        self.photo_width = int(photo_width) if photo_width is not None else None
        self.photo_height = int(photo_height) if photo_height is not None else None
        self.title = title
        self.description = description
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
