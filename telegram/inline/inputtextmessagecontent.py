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
"""This module contains the classes that represent Telegram InputTextMessageContent."""

from telegram import InputMessageContent


class InputTextMessageContent(InputMessageContent):
    """
    Represents the content of a text message to be sent as the result of an inline query.

    Attributes:
        message_text (:obj:`str`): Text of the message to be sent, 1-4096 characters.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in your bot's message.
        disable_web_page_preview (:obj:`bool`): Optional. Disables link previews for links in the
            sent message.

    Args:
        message_text (:obj:`str`): Text of the message to be sent, 1-4096 characters.  Also found
            as :attr:`telegram.constants.MAX_MESSAGE_LENGTH`.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in your bot's message.
        disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in the
            sent message.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, message_text, parse_mode=None, disable_web_page_preview=None, **kwargs):
        # Required
        self.message_text = message_text
        # Optionals
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
