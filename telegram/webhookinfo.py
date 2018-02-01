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
"""This module contains an object that represents a Telegram WebhookInfo."""

from telegram import TelegramObject


class WebhookInfo(TelegramObject):
    """This object represents a Telegram WebhookInfo.

    Contains information about the current status of a webhook.

    Attributes:
        url (:obj:`str`): Webhook URL.
        has_custom_certificate (:obj:`bool`): If a custom certificate was provided for webhook.
        pending_update_count (:obj:`int`): Number of updates awaiting delivery.
        last_error_date (:obj:`int`): Optional. Unix time for the most recent error that happened.
        last_error_message (:obj:`str`): Optional. Error message in human-readable format.
        max_connections (:obj:`int`): Optional. Maximum allowed number of simultaneous HTTPS
            connections.
        allowed_updates (List[:obj:`str`]): Optional. A list of update types the bot is subscribed
            to.

    Args:
        url (:obj:`str`): Webhook URL, may be empty if webhook is not set up.
        has_custom_certificate (:obj:`bool`): True, if a custom certificate was provided for
            webhook certificate checks.
        pending_update_count (:obj:`int`): Number of updates awaiting delivery.
        last_error_date (:obj:`int`, optional): Unix time for the most recent error that happened
            when trying todeliver an update via webhook.
        last_error_message (:obj:`str`, optional): Error message in human-readable format for the
            most recent error that happened when trying to deliver an update via webhook.
        max_connections (:obj:`int`, optional): Maximum allowed number of simultaneous HTTPS
            connections to the webhook for update delivery.
        allowed_updates (List[:obj:`str`], optional): A list of update types the bot is subscribed
            to. Defaults to all update types.

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

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)
