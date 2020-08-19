#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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

from dataclasses import dataclass
from telegram import TelegramObject
from typing import Any, List, Optional


@dataclass(eq=False)
class WebhookInfo(TelegramObject):
    """This object represents a Telegram WebhookInfo.

    Contains information about the current status of a webhook.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`url`, :attr:`has_custom_certificate`,
    :attr:`pending_update_count`, :attr:`last_error_date`, :attr:`last_error_message`,
    :attr:`max_connections` and :attr:`allowed_updates` are equal.

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

    # Required
    url: str
    has_custom_certificate: bool
    pending_update_count: int
    # Optionals
    last_error_date: Optional[int] = None
    last_error_message: Optional[str] = None
    max_connections: Optional[int] = None
    allowed_updates: Optional[List[str]] = None

    def __post_init__(self, **kwargs: Any) -> None:
        self._id_attrs = (
            self.url,
            self.has_custom_certificate,
            self.pending_update_count,
            self.last_error_date,
            self.last_error_message,
            self.max_connections,
            self.allowed_updates,
        )
