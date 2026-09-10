#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

import datetime as dtm
from typing import TYPE_CHECKING

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._messageentity import MessageEntity
from telegram._utils.argumentparsing import parse_sequence_arg, to_timedelta
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.datetime import get_timedelta_value
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import ODVInput
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


@tg_dataclass()
class InlineQueryResultMpeg4Gif(InlineQueryResult):
    """
    Represents a link to a video animation (H.264/MPEG-4 AVC video without sound). By default, this
    animated MPEG-4 file will be sent by the user with optional caption. Alternatively, you can
    use :attr:`input_message_content` to send a message with the specified content instead of the
    animation.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionchanged:: 20.5
        |removed_thumb_wildcard_note|

    Args:
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        mpeg4_url (:obj:`str`): A valid URL for the MP4 file.
        mpeg4_width (:obj:`int`, optional): Video width.
        mpeg4_height (:obj:`int`, optional): Video height.
        mpeg4_duration (:obj:`int` | :class:`datetime.timedelta`, optional): Video duration
            in seconds.

            .. versionchanged:: v22.2
                |time-period-input|
        thumbnail_url (:obj:`str`): URL of the static (JPEG or GIF) or animated (MPEG4)
            thumbnail for the result.

            .. versionadded:: 20.2

            .. versionchanged:: 20.5
              |thumbnail_url_mandatory|

        thumbnail_mime_type (:obj:`str`, optional): MIME type of the thumbnail, must be one of
            ``'image/jpeg'``, ``'image/gif'``, or ``'video/mp4'``. Defaults to ``'image/jpeg'``.

            .. versionadded:: 20.2
        title (:obj:`str`, optional): Title for the result.
        caption (:obj:`str`, optional): Caption of the MPEG-4 file to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional):
            |captionentitiesattr|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the video animation.
        show_caption_above_media (:obj:`bool`, optional): Pass |show_cap_above_med|

            .. versionadded:: 21.3

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.MPEG4GIF`.
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        mpeg4_url (:obj:`str`): A valid URL for the MP4 file.
        mpeg4_width (:obj:`int`): Optional. Video width.
        mpeg4_height (:obj:`int`): Optional. Video height.
        mpeg4_duration (:obj:`int` | :class:`datetime.timedelta`): Optional. Video duration
            in seconds.

            .. deprecated:: v22.2
                |time-period-int-deprecated|
        thumbnail_url (:obj:`str`): URL of the static (JPEG or GIF) or animated (MPEG4) thumbnail
            for the result.

            .. versionadded:: 20.2
        thumbnail_mime_type (:obj:`str`): Optional. MIME type of the thumbnail, must be one of
            ``'image/jpeg'``, ``'image/gif'``, or ``'video/mp4'``. Defaults to ``'image/jpeg'``.

            .. versionadded:: 20.2
        title (:obj:`str`): Optional. Title for the result.
        caption (:obj:`str`): Optional. Caption of the MPEG-4 file to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |caption_entities|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|

        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the video animation.
        show_caption_above_media (:obj:`bool`): Optional. |show_cap_above_med|

            .. versionadded:: 21.3
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=InlineQueryResultType.MPEG4GIF)
    # Required
    mpeg4_url: str = tg_field()
    thumbnail_url: str = tg_field()
    # Optional
    mpeg4_width: int | None = tg_field(default=None)
    mpeg4_height: int | None = tg_field(default=None)
    title: str | None = tg_field(default=None)
    caption: str | None = tg_field(default=None)
    reply_markup: InlineKeyboardMarkup | None = tg_field(default=None)
    input_message_content: "InputMessageContent | None" = tg_field(default=None)
    _mpeg4_duration: dtm.timedelta | None = tg_field(
        default=None, alias="mpeg4_duration", converter=to_timedelta
    )
    parse_mode: ODVInput[str] = tg_field(default=DEFAULT_NONE)
    caption_entities: tuple[MessageEntity, ...] = tg_field(
        default=None, converter=parse_sequence_arg
    )
    thumbnail_mime_type: str | None = tg_field(default=None)
    show_caption_above_media: bool | None = tg_field(default=None)

    @property
    def mpeg4_duration(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(self._mpeg4_duration, attribute="mpeg4_duration")
