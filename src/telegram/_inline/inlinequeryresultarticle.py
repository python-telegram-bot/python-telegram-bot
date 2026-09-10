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
"""This module contains the classes that represent Telegram InlineQueryResultArticle."""

from typing import TYPE_CHECKING

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


@tg_dataclass()
class InlineQueryResultArticle(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultArticle.

    Examples:
        :any:`Inline Bot <examples.inlinebot>`

    .. versionchanged:: 20.5
      Removed the deprecated arguments and attributes ``thumb_*``.

    .. versionchanged:: 21.11
        Removed the deprecated argument and attribute ``hide_url``.

    Args:
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        url (:obj:`str`, optional): URL of the result.

            Tip:
                Pass an empty string as URL if you don't want the URL to be shown in the message.
        description (:obj:`str`, optional): Short description of the result.
        thumbnail_url (:obj:`str`, optional): Url of the thumbnail for the result.

            .. versionadded:: 20.2
        thumbnail_width (:obj:`int`, optional): Thumbnail width.

            .. versionadded:: 20.2
        thumbnail_height (:obj:`int`, optional): Thumbnail height.

            .. versionadded:: 20.2

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.ARTICLE`.
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        url (:obj:`str`): Optional. URL of the result.
        description (:obj:`str`): Optional. Short description of the result.
        thumbnail_url (:obj:`str`): Optional. Url of the thumbnail for the result.

            .. versionadded:: 20.2
        thumbnail_width (:obj:`int`): Optional. Thumbnail width.

            .. versionadded:: 20.2
        thumbnail_height (:obj:`int`): Optional. Thumbnail height.

            .. versionadded:: 20.2

    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=InlineQueryResultType.ARTICLE)
    # Required
    title: str = tg_field()
    input_message_content: "InputMessageContent" = tg_field()
    # Optional
    reply_markup: InlineKeyboardMarkup | None = tg_field(default=None)
    url: str | None = tg_field(default=None)
    description: str | None = tg_field(default=None)
    thumbnail_url: str | None = tg_field(default=None)
    thumbnail_width: int | None = tg_field(default=None)
    thumbnail_height: int | None = tg_field(default=None)
