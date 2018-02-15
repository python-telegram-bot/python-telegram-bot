#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from telegram import InlineQueryResult


class InlineQueryResultMpeg4Gif(InlineQueryResult):
    """
    Represents a link to a video animation (H.264/MPEG-4 AVC video without sound). By default, this
    animated MPEG-4 file will be sent by the user with optional caption. Alternatively, you can
    use :attr:`input_message_content` to send a message with the specified content instead of the
    animation.

    Attributes:
        type (:obj:`str`): 'mpeg4_gif'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        mpeg4_url (:obj:`str`): A valid URL for the MP4 file. File size must not exceed 1MB.
        mpeg4_width (:obj:`int`): Optional. Video width.
        mpeg4_height (:obj:`int`): Optional. Video height.
        mpeg4_duration (:obj:`int`): Optional. Video duration.
        thumb_url (:obj:`str`): URL of the static thumbnail (jpeg or gif) for the result.
        title (:obj:`str`): Optional. Title for the result.
        caption (:obj:`str`): Optional. Caption, 0-200 characters
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption.. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the MPEG-4 file.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        mpeg4_url (:obj:`str`): A valid URL for the MP4 file. File size must not exceed 1MB.
        mpeg4_width (:obj:`int`, optional): Video width.
        mpeg4_height (:obj:`int`, optional): Video height.
        mpeg4_duration (:obj:`int`, optional): Video duration.
        thumb_url (:obj:`str`): URL of the static thumbnail (jpeg or gif) for the result.
        title (:obj:`str`, optional): Title for the result.
        caption (:obj:`str`, optional): Caption, 0-200 characters
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption.. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the MPEG-4 file.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 mpeg4_url,
                 thumb_url,
                 mpeg4_width=None,
                 mpeg4_height=None,
                 title=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 mpeg4_duration=None,
                 parse_mode=None,
                 **kwargs):

        # Required
        super(InlineQueryResultMpeg4Gif, self).__init__('mpeg4_gif', id)
        self.mpeg4_url = mpeg4_url
        self.thumb_url = thumb_url

        # Optional
        if mpeg4_width:
            self.mpeg4_width = mpeg4_width
        if mpeg4_height:
            self.mpeg4_height = mpeg4_height
        if mpeg4_duration:
            self.mpeg4_duration = mpeg4_duration
        if title:
            self.title = title
        if caption:
            self.caption = caption
        if parse_mode:
            self.parse_mode = parse_mode
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content
