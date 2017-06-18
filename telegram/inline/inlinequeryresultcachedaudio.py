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
InlineQueryResultCachedAudio"""

from telegram import InlineQueryResult, InlineKeyboardMarkup, InputMessageContent


class InlineQueryResultCachedAudio(InlineQueryResult):
    """Represents a link to an mp3 audio file stored on the Telegram servers. By default, this
    audio file will be sent by the user. Alternatively, you can use input_message_content to send a
    message with the specified content instead of the audio.

    Attributes:
        id (str):
        audio_file_id (str):
        caption (Optional[str]):
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]):
        input_message_content (Optional[:class:`telegram.input_message_content`]):

    Deprecated: 4.0
        message_text (str): Use :class:`InputTextMessageContent` instead.

        parse_mode (str): Use :class:`InputTextMessageContent` instead.

        disable_web_page_preview (bool): Use :class:`InputTextMessageContent` instead.

    Args:
        audio_file_id (str):
        caption (Optional[str]):
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]):
        input_message_content (Optional[:class:`telegram.input_message_content`]):
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 audio_file_id,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedAudio, self).__init__('audio', id)
        self.audio_file_id = audio_file_id

        # Optionals
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedAudio, InlineQueryResultCachedAudio).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedAudio(**data)
