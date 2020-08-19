#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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

from dataclasses import dataclass
from telegram import InlineQueryResult
from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import InputMessageContent, ReplyMarkup


@dataclass(eq=False)
class InlineQueryResultArticle(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultArticle.

    Attributes:
        type (:obj:`str`): 'article'.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.ReplyMarkup`): Optional. Inline keyboard attached to
            the message.
        url (:obj:`str`): Optional. URL of the result.
        hide_url (:obj:`bool`): Optional. Pass True, if you don't want the URL to be shown in the
            message.
        description (:obj:`str`): Optional. Short description of the result.
        thumb_url (:obj:`str`): Optional. Url of the thumbnail for the result.
        thumb_width (:obj:`int`): Optional. Thumbnail width.
        thumb_height (:obj:`int`): Optional. Thumbnail height.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.ReplyMarkup`, optional): Inline keyboard attached to
            the message
        url (:obj:`str`, optional): URL of the result.
        hide_url (:obj:`bool`, optional): Pass True, if you don't want the URL to be shown in the
            message.
        description (:obj:`str`, optional): Short description of the result.
        thumb_url (:obj:`str`, optional): Url of the thumbnail for the result.
        thumb_width (:obj:`int`, optional): Thumbnail width.
        thumb_height (:obj:`int`, optional): Thumbnail height.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    # Required
    id: str
    title: str
    input_message_content: 'InputMessageContent'
    # Optional
    reply_markup: Optional['ReplyMarkup'] = None
    url: Optional[str] = None
    hide_url: Optional[bool] = None
    description: Optional[str] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None

    def __post_init__(self, **kwargs: Any) -> None:
        super().__init__('article', self.id)
