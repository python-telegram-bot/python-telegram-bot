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
"""This module contains the classes that represent Telegram InlineQueryResultArticle."""

from typing import TYPE_CHECKING, Optional

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._utils.types import JSONDict
from telegram._utils.warnings_transition import (
    warn_about_deprecated_arg_return_new_arg,
    warn_about_deprecated_attr_in_property,
)
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultArticle(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultArticle.

    Examples:
        :any:`Inline Bot <examples.inlinebot>`

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
        hide_url (:obj:`bool`, optional): Pass :obj:`True`, if you don't want the URL to be shown
            in the message.
        description (:obj:`str`, optional): Short description of the result.
        thumb_url (:obj:`str`, optional): Url of the thumbnail for the result.

            .. deprecated:: 20.2
               |thumbargumentdeprecation| :paramref:`thumbnail_url`.
        thumb_width (:obj:`int`, optional): Thumbnail width.

            .. deprecated:: 20.2
               |thumbargumentdeprecation| :paramref:`thumbnail_width`.
        thumb_height (:obj:`int`, optional): Thumbnail height.

            .. deprecated:: 20.2
               |thumbargumentdeprecation| :paramref:`thumbnail_height`.
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
        hide_url (:obj:`bool`): Optional. Pass :obj:`True`, if you don't want the URL to be shown
            in the message.
        description (:obj:`str`): Optional. Short description of the result.
        thumbnail_url (:obj:`str`): Optional. Url of the thumbnail for the result.

            .. versionadded:: 20.2
        thumbnail_width (:obj:`int`): Optional. Thumbnail width.

            .. versionadded:: 20.2
        thumbnail_height (:obj:`int`): Optional. Thumbnail height.

            .. versionadded:: 20.2

    """

    __slots__ = (
        "reply_markup",
        "hide_url",
        "url",
        "title",
        "description",
        "input_message_content",
        "thumbnail_width",
        "thumbnail_height",
        "thumbnail_url",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        title: str,
        input_message_content: "InputMessageContent",
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        url: Optional[str] = None,
        hide_url: Optional[bool] = None,
        description: Optional[str] = None,
        thumb_url: Optional[str] = None,
        thumb_width: Optional[int] = None,
        thumb_height: Optional[int] = None,
        thumbnail_url: Optional[str] = None,
        thumbnail_width: Optional[int] = None,
        thumbnail_height: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        # Required
        super().__init__(InlineQueryResultType.ARTICLE, id, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.title: str = title
            self.input_message_content: InputMessageContent = input_message_content

            # Optional
            self.reply_markup: Optional[InlineKeyboardMarkup] = reply_markup
            self.url: Optional[str] = url
            self.hide_url: Optional[bool] = hide_url
            self.description: Optional[str] = description
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
        """:obj:`str`: Optional. Url of the thumbnail for the result.

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
