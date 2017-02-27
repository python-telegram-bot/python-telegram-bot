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
"""This module contains an object that represents a Telegram WebhookInfo."""

from telegram import TelegramObject


class WebhookInfo(TelegramObject):
    """This object represents a Telegram WebhookInfo.

    Attributes:
        url (str): Webhook URL, may be empty if webhook is not set up.
        has_custom_certificate (bool):
        pending_update_count (int):
        last_error_date (int):
        last_error_message (str):

    Args:
        url (str): Webhook URL, may be empty if webhook is not set up.
        has_custom_certificate (bool):
        pending_update_count (int):
        last_error_date (Optional[int]):
        last_error_message (Optional[str]):

    """

    def __init__(self,
                 url,
                 has_custom_certificate,
                 pending_update_count,
                 last_error_date=None,
                 last_error_message=None,
                 max_connections=None,
                 allowed_updates=None,
                 **kwargs):
        # Required
        self.url = url
        self.has_custom_certificate = has_custom_certificate
        self.pending_update_count = pending_update_count
        self.last_error_date = last_error_date
        self.last_error_message = last_error_message
        self.max_connections = max_connections
        self.allowed_updates = allowed_updates

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.WebhookInfo:

        """
        if not data:
            return None

        return WebhookInfo(**data)
