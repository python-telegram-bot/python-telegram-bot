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
"""This module contains the classes that represent Telegram InlineQueryResultLocation"""

from telegram import InlineQueryResult, InlineKeyboardMarkup, InputMessageContent


class InlineQueryResultLocation(InlineQueryResult):
    """Represents a location on a map. By default, the location will be sent by the user.
    Alternatively, you can use input_message_content to send a message with the specified content
    instead of the location.

    Attributes:
        latitude (float): Location latitude in degrees.
        longitude (float): Location longitude in degrees.
        title (str): Location title.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the location.
        thumb_url (Optional[str]): Url of the thumbnail for the result.
        thumb_width (Optional[int]): Thumbnail width.
        thumb_height (Optional[int]): Thumbnail height.

    Args:
        latitude (float): Location latitude in degrees.
        longitude (float): Location longitude in degrees.
        title (str): Location title.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the location.
        thumb_url (Optional[str]): Url of the thumbnail for the result.
        thumb_width (Optional[int]): Thumbnail width.
        thumb_height (Optional[int]): Thumbnail height.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 latitude,
                 longitude,
                 title,
                 reply_markup=None,
                 input_message_content=None,
                 thumb_url=None,
                 thumb_width=None,
                 thumb_height=None,
                 **kwargs):
        # Required
        super(InlineQueryResultLocation, self).__init__('location', id)
        self.latitude = latitude
        self.longitude = longitude
        self.title = title

        # Optionals
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content
        if thumb_url:
            self.thumb_url = thumb_url
        if thumb_width:
            self.thumb_width = thumb_width
        if thumb_height:
            self.thumb_height = thumb_height

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultLocation, InlineQueryResultLocation).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultLocation(**data)
