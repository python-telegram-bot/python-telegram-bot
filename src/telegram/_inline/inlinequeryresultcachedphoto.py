#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
"""This module contains the classes that represent Telegram InlineQueryResultPhoto"""
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._messageentity import MessageEntity
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import JSONDict, ODVInput
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultCachedPhoto(InlineQueryResult):
    """
    Represents a link to a photo stored on the Telegram servers. By default, this photo will be
    sent by the user with an optional caption. Alternatively, you can use
    :attr:`input_message_content` to send a message with the specified content instead
    of the photo.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Args:
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        photo_file_id (:obj:`str`): A valid file identifier of the photo.
        title (:obj:`str`, optional): Title for the result.
        description (:obj:`str`, optional): Short description of the result.
        caption (:obj:`str`, optional): Caption of the photo to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the photo.
        show_caption_above_media (:obj:`bool`, optional): Pass |show_cap_above_med|

            .. versionadded:: 21.3

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.PHOTO`.
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        photo_file_id (:obj:`str`): A valid file identifier of the photo.
        title (:obj:`str`): Optional. Title for the result.
        description (:obj:`str`): Optional. Short description of the result.
        caption (:obj:`str`): Optional. Caption of the photo to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
            entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the photo.
        show_caption_above_media (:obj:`bool`): Optional. |show_cap_above_med|

            .. versionadded:: 21.3

    """

    __slots__ = (
        "caption",
        "caption_entities",
        "description",
        "input_message_content",
        "parse_mode",
        "photo_file_id",
        "reply_markup",
        "show_caption_above_media",
        "title",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        photo_file_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        caption: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        input_message_content: Optional["InputMessageContent"] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence[MessageEntity]] = None,
        show_caption_above_media: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        # Required
        super().__init__(InlineQueryResultType.PHOTO, id, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.photo_file_id: str = photo_file_id

            # Optionals
            self.title: Optional[str] = title
            self.description: Optional[str] = description
            self.caption: Optional[str] = caption
            self.parse_mode: ODVInput[str] = parse_mode
            self.caption_entities: tuple[MessageEntity, ...] = parse_sequence_arg(caption_entities)
            self.reply_markup: Optional[InlineKeyboardMarkup] = reply_markup
            self.input_message_content: Optional[InputMessageContent] = input_message_content
            self.show_caption_above_media: Optional[bool] = show_caption_above_media
