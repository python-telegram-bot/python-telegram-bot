#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
from typing import TYPE_CHECKING, Optional, Sequence, Tuple

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._messageentity import MessageEntity
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import JSONDict, ODVInput
from telegram._utils.warnings_transition import (
    warn_about_deprecated_arg_return_new_arg,
    warn_about_deprecated_attr_in_property,
)
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultDocument(InlineQueryResult):
    """
    Represents a link to a file. By default, this file will be sent by the user with an optional
    caption. Alternatively, you can use :attr:`input_message_content` to send a message with the
    specified content instead of the file. Currently, only .PDF and .ZIP files can be sent
    using this method.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Args:
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        title (:obj:`str`): Title for the result.
        caption (:obj:`str`, optional): Caption of the document to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        document_url (:obj:`str`): A valid URL for the file.
        mime_type (:obj:`str`): Mime type of the content of the file, either "application/pdf"
            or "application/zip".
        description (:obj:`str`, optional): Short description of the result.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the file.
        thumb_url (:obj:`str`, optional): URL of the thumbnail (JPEG only) for the file.

            .. deprecated:: 20.2
               |thumbargumentdeprecation| :paramref:`thumbnail_url`.
        thumb_width (:obj:`int`, optional): Thumbnail width.

            .. deprecated:: 20.2
               |thumbargumentdeprecation| :paramref:`thumbnail_width`.
        thumb_height (:obj:`int`, optional): Thumbnail height.

            .. deprecated:: 20.2
               |thumbargumentdeprecation| :paramref:`thumbnail_height`.
        thumbnail_url (:obj:`str`, optional): URL of the thumbnail (JPEG only) for the file.

            .. versionadded:: 20.2
        thumbnail_width (:obj:`int`, optional): Thumbnail width.

            .. versionadded:: 20.2
        thumbnail_height (:obj:`int`, optional): Thumbnail height.

            .. versionadded:: 20.2


    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.DOCUMENT`.
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        title (:obj:`str`): Title for the result.
        caption (:obj:`str`): Optional. Caption of the document to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        document_url (:obj:`str`): A valid URL for the file.
        mime_type (:obj:`str`): Mime type of the content of the file, either "application/pdf"
            or "application/zip".
        description (:obj:`str`): Optional. Short description of the result.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the file.
        thumbnail_url (:obj:`str`): Optional. URL of the thumbnail (JPEG only) for the file.

            .. versionadded:: 20.2
        thumbnail_width (:obj:`int`): Optional. Thumbnail width.

            .. versionadded:: 20.2
        thumbnail_height (:obj:`int`): Optional. Thumbnail height.

            .. versionadded:: 20.2

    """

    __slots__ = (
        "reply_markup",
        "caption_entities",
        "document_url",
        "thumbnail_width",
        "thumbnail_height",
        "caption",
        "title",
        "description",
        "parse_mode",
        "mime_type",
        "thumbnail_url",
        "input_message_content",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        document_url: str,
        title: str,
        mime_type: str,
        caption: Optional[str] = None,
        description: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        input_message_content: Optional["InputMessageContent"] = None,
        thumb_url: Optional[str] = None,
        thumb_width: Optional[int] = None,
        thumb_height: Optional[int] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence[MessageEntity]] = None,
        thumbnail_url: Optional[str] = None,
        thumbnail_width: Optional[int] = None,
        thumbnail_height: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        # Required
        super().__init__(InlineQueryResultType.DOCUMENT, id, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.document_url: str = document_url
            self.title: str = title
            self.mime_type: str = mime_type

            # Optionals
            self.caption: Optional[str] = caption
            self.parse_mode: ODVInput[str] = parse_mode
            self.caption_entities: Tuple[MessageEntity, ...] = parse_sequence_arg(caption_entities)
            self.description: Optional[str] = description
            self.reply_markup: Optional[InlineKeyboardMarkup] = reply_markup
            self.input_message_content: Optional[InputMessageContent] = input_message_content
            self.thumbnail_url: Optional[str] = warn_about_deprecated_arg_return_new_arg(
                deprecated_arg=thumb_url,
                new_arg=thumbnail_url,
                deprecated_arg_name="thumb_url",
                new_arg_name="thumbnail_url",
                bot_api_version="6.6",
            )
            self.thumbnail_width: Optional[int] = warn_about_deprecated_arg_return_new_arg(
                deprecated_arg=thumb_width,
                new_arg=thumbnail_width,
                deprecated_arg_name="thumb_width",
                new_arg_name="thumbnail_width",
                bot_api_version="6.6",
            )
            self.thumbnail_height: Optional[int] = warn_about_deprecated_arg_return_new_arg(
                deprecated_arg=thumb_height,
                new_arg=thumbnail_height,
                deprecated_arg_name="thumb_height",
                new_arg_name="thumbnail_height",
                bot_api_version="6.6",
            )

    @property
    def thumb_url(self) -> Optional[str]:
        """:obj:`str`: Optional. URL of the thumbnail (JPEG only) for the file.

        .. deprecated:: 20.2
           |thumbattributedeprecation| :attr:`thumbnail_url`.
        """
        warn_about_deprecated_attr_in_property(
            deprecated_attr_name="thumb_url",
            new_attr_name="thumbnail_url",
            bot_api_version="6.6",
        )
        return self.thumbnail_url

    @property
    def thumb_width(self) -> Optional[int]:
        """:obj:`str`: Optional. Thumbnail width.

        .. deprecated:: 20.2
           |thumbattributedeprecation| :attr:`thumbnail_width`.
        """
        warn_about_deprecated_attr_in_property(
            deprecated_attr_name="thumb_width",
            new_attr_name="thumbnail_width",
            bot_api_version="6.6",
        )
        return self.thumbnail_width

    @property
    def thumb_height(self) -> Optional[int]:
        """:obj:`str`: Optional. Thumbnail height.

        .. deprecated:: 20.2
           |thumbattributedeprecation| :attr:`thumbnail_height`.
        """
        warn_about_deprecated_attr_in_property(
            deprecated_attr_name="thumb_height",
            new_attr_name="thumbnail_height",
            bot_api_version="6.6",
        )
        return self.thumbnail_height
