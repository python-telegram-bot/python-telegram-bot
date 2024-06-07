#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
from typing import TYPE_CHECKING, Optional, Sequence, Tuple

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._messageentity import MessageEntity
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import JSONDict, ODVInput
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultGif(InlineQueryResult):
    """
    Represents a link to an animated GIF file. By default, this animated GIF file will be sent by
    the user with optional caption. Alternatively, you can use :attr:`input_message_content` to
    send a message with the specified content instead of the animation.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionchanged:: 20.5
      |removed_thumb_wildcard_note|

    Args:
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        gif_url (:obj:`str`): A valid URL for the GIF file. File size must not exceed 1MB.
        gif_width (:obj:`int`, optional): Width of the GIF.
        gif_height (:obj:`int`, optional): Height of the GIF.
        gif_duration (:obj:`int`, optional): Duration of the GIF in seconds.
        thumbnail_url (:obj:`str`, optional): URL of the static (JPEG or GIF) or animated (MPEG4)
            thumbnail for the result.

            Warning:
                The Bot API does **not** define this as an optional argument. It is formally
                optional for backwards compatibility with the deprecated :paramref:`thumb_url`.
                If you pass neither :paramref:`thumbnail_url` nor :paramref:`thumb_url`,
                :class:`ValueError` will be raised.

            .. versionadded:: 20.2
        thumbnail_mime_type (:obj:`str`, optional): MIME type of the thumbnail, must be one of
            ``'image/jpeg'``, ``'image/gif'``, or ``'video/mp4'``. Defaults to ``'image/jpeg'``.

            .. versionadded:: 20.2
        title (:obj:`str`, optional): Title for the result.
        caption (:obj:`str`, optional): Caption of the GIF file to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the GIF animation.
        show_caption_above_media (:obj:`bool`, optional): Pass |show_cap_above_med|

            .. versionadded:: 21.3

    Raises:
        :class:`ValueError`: If neither :paramref:`thumbnail_url` nor :paramref:`thumb_url` is
            supplied or if both are supplied and are not equal.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.GIF`.
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        gif_url (:obj:`str`): A valid URL for the GIF file. File size must not exceed 1MB.
        gif_width (:obj:`int`): Optional. Width of the GIF.
        gif_height (:obj:`int`): Optional. Height of the GIF.
        gif_duration (:obj:`int`): Optional. Duration of the GIF in seconds.
        thumbnail_url (:obj:`str`): URL of the static (JPEG or GIF) or animated (MPEG4) thumbnail
            for the result.

            .. versionadded:: 20.2
        thumbnail_mime_type (:obj:`str`): Optional. MIME type of the thumbnail, must be one of
            ``'image/jpeg'``, ``'image/gif'``, or ``'video/mp4'``. Defaults to ``'image/jpeg'``.

            .. versionadded:: 20.2
        title (:obj:`str`): Optional. Title for the result.
        caption (:obj:`str`): Optional. Caption of the GIF file to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the GIF animation.
        show_caption_above_media (:obj:`bool`): Optional. |show_cap_above_med|

            .. versionadded:: 21.3

    """

    __slots__ = (
        "caption",
        "caption_entities",
        "gif_duration",
        "gif_height",
        "gif_url",
        "gif_width",
        "input_message_content",
        "parse_mode",
        "reply_markup",
        "show_caption_above_media",
        "thumbnail_mime_type",
        "thumbnail_url",
        "title",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        gif_url: str,
        thumbnail_url: str,
        gif_width: Optional[int] = None,
        gif_height: Optional[int] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        input_message_content: Optional["InputMessageContent"] = None,
        gif_duration: Optional[int] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence[MessageEntity]] = None,
        thumbnail_mime_type: Optional[str] = None,
        show_caption_above_media: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        # Required
        super().__init__(InlineQueryResultType.GIF, id, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.gif_url: str = gif_url
            self.thumbnail_url: str = thumbnail_url

            # Optionals
            self.gif_width: Optional[int] = gif_width
            self.gif_height: Optional[int] = gif_height
            self.gif_duration: Optional[int] = gif_duration
            self.title: Optional[str] = title
            self.caption: Optional[str] = caption
            self.parse_mode: ODVInput[str] = parse_mode
            self.caption_entities: Tuple[MessageEntity, ...] = parse_sequence_arg(caption_entities)
            self.reply_markup: Optional[InlineKeyboardMarkup] = reply_markup
            self.input_message_content: Optional[InputMessageContent] = input_message_content
            self.thumbnail_mime_type: Optional[str] = thumbnail_mime_type
            self.show_caption_above_media: Optional[bool] = show_caption_above_media
