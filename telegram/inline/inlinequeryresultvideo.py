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
"""This module contains the classes that represent Telegram InlineQueryResultVideo."""

from telegram import InlineQueryResult


class InlineQueryResultVideo(InlineQueryResult):
    """
    Represents a link to a page containing an embedded video player or a video file. By default,
    this video file will be sent by the user with an optional caption. Alternatively, you can use
    :attr:`input_message_content` to send a message with the specified content instead of
    the video.

    Attributes:
        type (:obj:`str`): 'video'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        video_url (:obj:`str`): A valid URL for the embedded video player or video file.
        mime_type (:obj:`str`): Mime type of the content of video url, "text/html" or "video/mp4".
        thumb_url (:obj:`str`): URL of the thumbnail (jpeg only) for the video.
        title (:obj:`str`): Title for the result.
        caption (:obj:`str`): Optional. Caption, 0-200 characters
        video_width (:obj:`int`): Optional. Video width.
        video_height (:obj:`int`): Optional. Video height.
        video_duration (:obj:`int`): Optional. Video duration in seconds.
        description (:obj:`str`): Optional. Short description of the result.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the video.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        video_url (:obj:`str`): A valid URL for the embedded video player or video file.
        mime_type (:obj:`str`): Mime type of the content of video url, "text/html" or "video/mp4".
        thumb_url (:obj:`str`): URL of the thumbnail (jpeg only) for the video.
        title (:obj:`str`): Title for the result.
        caption (:obj:`str`, optional): Caption, 0-200 characters.
        video_width (:obj:`int`, optional): Video width.
        video_height (:obj:`int`, optional): Video height.
        video_duration (:obj:`int`, optional): Video duration in seconds.
        description (:obj:`str`, optional): Short description of the result.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the video.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 video_url,
                 mime_type,
                 thumb_url,
                 title,
                 caption=None,
                 video_width=None,
                 video_height=None,
                 video_duration=None,
                 description=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):

        # Required
        super(InlineQueryResultVideo, self).__init__('video', id)
        self.video_url = video_url
        self.mime_type = mime_type
        self.thumb_url = thumb_url
        self.title = title

        # Optional
        if caption:
            self.caption = caption
        if video_width:
            self.video_width = video_width
        if video_height:
            self.video_height = video_height
        if video_duration:
            self.video_duration = video_duration
        if description:
            self.description = description
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content
