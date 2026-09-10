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
"""This module contains the classes that represent Telegram InlineQueryResultCachedAudio."""

from typing import TYPE_CHECKING

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._messageentity import MessageEntity
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import ODVInput
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


@tg_dataclass()
class InlineQueryResultCachedAudio(InlineQueryResult):
    """
    Represents a link to an mp3 audio file stored on the Telegram servers. By default, this audio
    file will be sent by the user. Alternatively, you can use :attr:`input_message_content` to
    send a message with the specified content instead of the audio.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Args:
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        audio_file_id (:obj:`str`): A valid file identifier for the audio file.
        caption (:obj:`str`, optional): Caption,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after entities
            parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the audio.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.AUDIO`.
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        audio_file_id (:obj:`str`): A valid file identifier for the audio file.
        caption (:obj:`str`): Optional. Caption,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after entities
            parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the audio.

    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=InlineQueryResultType.AUDIO)
    # Required
    audio_file_id: str = tg_field()
    # Optional
    caption: str | None = tg_field(default=None)
    reply_markup: InlineKeyboardMarkup | None = tg_field(default=None)
    input_message_content: "InputMessageContent | None" = tg_field(default=None)
    parse_mode: ODVInput[str] = tg_field(default=DEFAULT_NONE)
    caption_entities: tuple[MessageEntity, ...] = tg_field(
        default=None, converter=parse_sequence_arg
    )
