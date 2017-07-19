#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains the classes that represent Telegram
InlineQueryResultMpeg4Gif"""

from telegram import InlineQueryResult, InlineKeyboardMarkup, InputMessageContent


class InlineQueryResultCachedMpeg4Gif(InlineQueryResult):
    """
    Represents a link to a video animation (H.264/MPEG-4 AVC video without sound) stored on the
    Telegram servers. By default, this animated MPEG-4 file will be sent by the user with an
    optional caption. Alternatively, you can use :attr:`input_message_content` to send a message
    with the specified content instead of the animation.

    Attributes:
        type (str): 'mpeg4_gif'.
        id (str): Unique identifier for this result, 1-64 bytes.
        mpeg4_file_id (str): A valid file identifier for the MP4 file.
        title (str): Optional. Title for the result.
        caption (str): Optional. Caption, 0-200 characters
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
                to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
                message to be sent instead of the MPEG-4 file.

    Args:
        id (str): Unique identifier for this result, 1-64 bytes.
        mpeg4_file_id (str): A valid file identifier for the MP4 file.
        title (Optional[str]): Title for the result.
        caption (Optional[str]): Caption, 0-200 characters
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
                to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
                message to be sent instead of the MPEG-4 file.
        **kwargs (dict): Arbitrary keyword arguments.
    """

    def __init__(self,
                 id,
                 mpeg4_file_id,
                 title=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedMpeg4Gif, self).__init__('mpeg4_gif', id)
        self.mpeg4_file_id = mpeg4_file_id

        # Optionals
        if title:
            self.title = title
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedMpeg4Gif,
                     InlineQueryResultCachedMpeg4Gif).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedMpeg4Gif(**data)
