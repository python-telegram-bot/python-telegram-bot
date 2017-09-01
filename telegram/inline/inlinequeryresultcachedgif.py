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
"""This module contains the classes that represent Telegram InlineQueryResultCachedGif."""

from telegram import InlineQueryResult


class InlineQueryResultCachedGif(InlineQueryResult):
    """
    Represents a link to an animated GIF file stored on the Telegram servers. By default, this
    animated GIF file will be sent by the user with an optional caption. Alternatively, you can
    use :attr:`input_message_content` to send a message with specified content instead of
    the animation.

    Attributes:
        type (:obj:`str`): 'gif'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        gif_file_id (:obj:`str`): A valid file identifier for the GIF file.
        title (:obj:`str`): Optional. Title for the result.
        caption (:obj:`str`): Optional. Caption, 0-200 characters
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the gif.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        gif_file_id (:obj:`str`): A valid file identifier for the GIF file.
        title (:obj:`str`, optional): Title for the result.caption (:obj:`str`, optional):
        caption (:obj:`str`, optional): Caption, 0-200 characters
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the gif.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 gif_file_id,
                 title=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedGif, self).__init__('gif', id)
        self.gif_file_id = gif_file_id

        # Optionals
        if title:
            self.title = title
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content
