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
"""This module contains the classes that represent InputMessageContents"""

from telegram import TelegramObject


class InputMessageContent(TelegramObject):
    """Base class for Telegram InputMessageContent Objects"""

    @staticmethod
    def de_json(data, bot):
        data = super(InputMessageContent, InputMessageContent).de_json(data, bot)

        if not data:
            return None

        try:
            return InputTextMessageContent.de_json(data, bot)
        except TypeError:
            pass

        try:
            return InputVenueMessageContent.de_json(data, bot)
        except TypeError:
            pass

        try:
            return InputLocationMessageContent.de_json(data, bot)
        except TypeError:
            pass

        try:
            return InputContactMessageContent.de_json(data, bot)
        except TypeError:
            pass

        return None


class InputTextMessageContent(InputMessageContent):
    """Base class for Telegram InputTextMessageContent Objects"""

    def __init__(self, message_text, parse_mode=None, disable_web_page_preview=None, **kwargs):
        # Required
        self.message_text = message_text
        # Optionals
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview

    @staticmethod
    def de_json(data, bot):
        return InputTextMessageContent(**data)


class InputVenueMessageContent(InputMessageContent):
    """Base class for Telegram InputVenueMessageContent Objects"""

    def __init__(self, latitude, longitude, title, address, foursquare_id=None, **kwargs):
        # Required
        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.address = address
        # Optionals
        self.foursquare_id = foursquare_id

    @staticmethod
    def de_json(data, bot):
        return InputVenueMessageContent(**data)


class InputLocationMessageContent(InputMessageContent):
    """Base class for Telegram InputLocationMessageContent Objects"""

    def __init__(self, latitude, longitude, **kwargs):
        # Required
        self.latitude = latitude
        self.longitude = longitude

    @staticmethod
    def de_json(data, bot):
        return InputLocationMessageContent(**data)


class InputContactMessageContent(InputMessageContent):
    """Base class for Telegram InputContactMessageContent Objects"""

    def __init__(self, phone_number, first_name, last_name=None, **kwargs):
        # Required
        self.phone_number = phone_number
        self.first_name = first_name
        # Optionals
        self.last_name = last_name

    @staticmethod
    def de_json(data, bot):
        return InputContactMessageContent(**data)
