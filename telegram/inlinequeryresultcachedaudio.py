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

"""This module contains the classes that represent Telegram
InlineQueryResultCachedAudio"""

from telegram import InlineQueryResult, InlineKeyboardMarkup, \
    InputMessageContent


class InlineQueryResultCachedAudio(InlineQueryResult):
    def __init__(self,
                 id,
                 audio_file_id,
                 reply_markup=None,
                 input_message_content=None):
        # Required
        super(InlineQueryResultCachedAudio, self).__init__('audio', id)
        self.audio_file_id = audio_file_id

        # Optionals
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data):
        data = super(InlineQueryResultCachedAudio,
                     InlineQueryResultCachedAudio).de_json(data)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(
            data.get('reply_markup'))
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'))

        return InlineQueryResultCachedAudio(**data)
