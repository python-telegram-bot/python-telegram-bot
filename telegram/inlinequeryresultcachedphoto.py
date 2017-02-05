#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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

from telegram import InlineQueryResult, InlineKeyboardMarkup, InputMessageContent


class InlineQueryResultCachedPhoto(InlineQueryResult):
    """Represents a link to a photo stored on the Telegram servers. By default, this photo will be
    sent by the user with an optional caption. Alternatively, you can use input_message_content to
    send a message with the specified content instead of the photo.

    Attributes:
        photo_file_id (str): A valid file identifier of the photo.
        title (Optional[str]): Title for the result.
        description (Optional[str]): Short description of the result.
        caption (Optional[str]): Caption of the photo to be sent, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the photo

    Args:
        id (str):
        photo_file_id (str):
        title (Optional[str]):
        description (Optional[str]):
        caption (Optional[str]):
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]):
        input_message_content (Optional[:class:`telegram.InputMessageContent`]):
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 photo_file_id,
                 title=None,
                 description=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedPhoto, self).__init__('photo', id)
        self.photo_file_id = photo_file_id

        # Optionals
        if title:
            self.title = title
        if description:
            self.description = description
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedPhoto, InlineQueryResultCachedPhoto).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedPhoto(**data)
