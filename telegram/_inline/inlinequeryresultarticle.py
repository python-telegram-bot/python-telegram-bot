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
"""This module contains the classes that represent Telegram InlineQueryResultArticle."""

from typing import TYPE_CHECKING

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._utils.types import JSONDict
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultArticle(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultArticle.

    .. seealso:: `Inline Example <examples.inlinebot.html>`_

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        url (:obj:`str`, optional): URL of the result.
        hide_url (:obj:`bool`, optional): Pass :obj:`True`, if you don't want the URL to be shown
            in the message.
        description (:obj:`str`, optional): Short description of the result.
        thumb_url (:obj:`str`, optional): Url of the thumbnail for the result.
        thumb_width (:obj:`int`, optional): Thumbnail width.
        thumb_height (:obj:`int`, optional): Thumbnail height.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.ARTICLE`.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        url (:obj:`str`): Optional. URL of the result.
        hide_url (:obj:`bool`): Optional. Pass :obj:`True`, if you don't want the URL to be shown
            in the message.
        description (:obj:`str`): Optional. Short description of the result.
        thumb_url (:obj:`str`): Optional. Url of the thumbnail for the result.
        thumb_width (:obj:`int`): Optional. Thumbnail width.
        thumb_height (:obj:`int`): Optional. Thumbnail height.

    """

    __slots__ = (
        "reply_markup",
        "thumb_width",
        "thumb_height",
        "hide_url",
        "url",
        "title",
        "description",
        "input_message_content",
        "thumb_url",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        title: str,
        input_message_content: "InputMessageContent",
        reply_markup: InlineKeyboardMarkup = None,
        url: str = None,
        hide_url: bool = None,
        description: str = None,
        thumb_url: str = None,
        thumb_width: int = None,
        thumb_height: int = None,
        *,
        api_kwargs: JSONDict = None,
    ):

        # Required
        super().__init__(InlineQueryResultType.ARTICLE, id, api_kwargs=api_kwargs)
        self.title = title
        self.input_message_content = input_message_content

        # Optional
        self.reply_markup = reply_markup
        self.url = url
        self.hide_url = hide_url
        self.description = description
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
