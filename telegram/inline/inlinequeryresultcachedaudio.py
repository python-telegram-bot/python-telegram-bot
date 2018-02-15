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
"""This module contains the classes that represent Telegram InlineQueryResultCachedAudio."""

from telegram import InlineQueryResult


class InlineQueryResultCachedAudio(InlineQueryResult):
    """
    Represents a link to an mp3 audio file stored on the Telegram servers. By default, this audio
    file will be sent by the user. Alternatively, you can use :attr:`input_message_content` to
    send amessage with the specified content instead of the audio.

    Attributes:
        type (:obj:`str`): 'audio'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        audio_file_id (:obj:`str`): A valid file identifier for the audio file.
        caption (:obj:`str`): Optional. Caption, 0-200 characters
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption.. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the audio.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        audio_file_id (:obj:`str`): A valid file identifier for the audio file.
        caption (:obj:`str`, optional): Caption, 0-200 characters
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption.. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the audio.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 audio_file_id,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 parse_mode=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedAudio, self).__init__('audio', id)
        self.audio_file_id = audio_file_id

        # Optionals
        if caption:
            self.caption = caption
        if parse_mode:
            self.parse_mode = parse_mode
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content
