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
"""This module contains the classes that represent Telegram InlineQueryResultVoice."""

from telegram import InlineQueryResult


class InlineQueryResultVoice(InlineQueryResult):
    """
    Represents a link to a voice recording in an .ogg container encoded with OPUS. By default,
    this voice recording will be sent by the user. Alternatively, you can use
    :attr:`input_message_content` to send a message with the specified content instead of the
    the voice message.

    Attributes:
        type (:obj:`str`): 'voice'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        voice_url (:obj:`str`): A valid URL for the voice recording.
        title (:obj:`str`): Voice message title.
        caption (:obj:`str`): Optional. Caption, 0-200 characters.
        voice_duration (:obj:`int`): Optional. Recording duration in seconds.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the voice.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        voice_url (:obj:`str`): A valid URL for the voice recording.
        title (:obj:`str`): Voice message title.
        caption (:obj:`str`, optional): Caption, 0-200 characters.
        voice_duration (:obj:`int`, optional): Recording duration in seconds.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the voice.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 voice_url,
                 title,
                 voice_duration=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):

        # Required
        super(InlineQueryResultVoice, self).__init__('voice', id)
        self.voice_url = voice_url
        self.title = title

        # Optional
        if voice_duration:
            self.voice_duration = voice_duration
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content
