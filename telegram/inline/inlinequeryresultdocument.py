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
"""This module contains the classes that represent Telegram InlineQueryResultDocument"""

from typing import TYPE_CHECKING, Any, Union, Tuple, List

from telegram import InlineQueryResult, MessageEntity
from telegram.utils.helpers import DEFAULT_NONE, DefaultValue

if TYPE_CHECKING:
    from telegram import InputMessageContent, ReplyMarkup


class InlineQueryResultDocument(InlineQueryResult):
    """
    Represents a link to a file. By default, this file will be sent by the user with an optional
    caption. Alternatively, you can use :attr:`input_message_content` to send a message with the
    specified content instead of the file. Currently, only .PDF and .ZIP files can be sent
    using this method.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        title (:obj:`str`): Title for the result.
        caption (:obj:`str`, optional): Caption of the document to be sent, 0-1024 characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
            entities that appear in the caption, which can be specified instead of
            :attr:`parse_mode`.
        document_url (:obj:`str`): A valid URL for the file.
        mime_type (:obj:`str`): Mime type of the content of the file, either "application/pdf"
            or "application/zip".
        description (:obj:`str`, optional): Short description of the result.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the file.
        thumb_url (:obj:`str`, optional): URL of the thumbnail (jpeg only) for the file.
        thumb_width (:obj:`int`, optional): Thumbnail width.
        thumb_height (:obj:`int`, optional): Thumbnail height.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        type (:obj:`str`): 'document'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        title (:obj:`str`): Title for the result.
        caption (:obj:`str`): Optional. Caption of the document to be sent, 0-1024 characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        caption_entities (List[:class:`telegram.MessageEntity`]): Optional. List of special
            entities that appear in the caption, which can be specified instead of
            :attr:`parse_mode`.
        document_url (:obj:`str`): A valid URL for the file.
        mime_type (:obj:`str`): Mime type of the content of the file, either "application/pdf"
            or "application/zip".
        description (:obj:`str`): Optional. Short description of the result.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the file.
        thumb_url (:obj:`str`): Optional. URL of the thumbnail (jpeg only) for the file.
        thumb_width (:obj:`int`): Optional. Thumbnail width.
        thumb_height (:obj:`int`): Optional. Thumbnail height.

    """

    def __init__(
        self,
        id: str,  # pylint: disable=W0622
        document_url: str,
        title: str,
        mime_type: str,
        caption: str = None,
        description: str = None,
        reply_markup: 'ReplyMarkup' = None,
        input_message_content: 'InputMessageContent' = None,
        thumb_url: str = None,
        thumb_width: int = None,
        thumb_height: int = None,
        parse_mode: Union[str, DefaultValue] = DEFAULT_NONE,
        caption_entities: Union[Tuple[MessageEntity, ...], List[MessageEntity]] = None,
        **_kwargs: Any,
    ):
        # Required
        super().__init__('document', id)
        self.document_url = document_url
        self.title = title
        self.mime_type = mime_type

        # Optionals
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.description = description
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
