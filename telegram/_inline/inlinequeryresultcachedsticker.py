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
"""This module contains the classes that represent Telegram InlineQueryResultCachedSticker."""

from typing import TYPE_CHECKING, Any

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultCachedSticker(InlineQueryResult):
    """
    Represents a link to a sticker stored on the Telegram servers. By default, this sticker will
    be sent by the user. Alternatively, you can use :attr:`input_message_content` to send a
    message with the specified content instead of the sticker.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        sticker_file_id (:obj:`str`): A valid file identifier of the sticker.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the sticker.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.STICKER`.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        sticker_file_id (:obj:`str`): A valid file identifier of the sticker.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the sticker.

    """

    __slots__ = ("reply_markup", "input_message_content", "sticker_file_id")

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        sticker_file_id: str,
        reply_markup: InlineKeyboardMarkup = None,
        input_message_content: "InputMessageContent" = None,
        **_kwargs: Any,
    ):
        # Required
        super().__init__(InlineQueryResultType.STICKER, id)
        self.sticker_file_id = sticker_file_id

        # Optionals
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
