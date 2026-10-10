#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

import datetime as dtm

from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class WebhookInfo(TelegramObject):
    """This object represents a Telegram WebhookInfo.

    Contains information about the current status of a webhook.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`url`, :attr:`has_custom_certificate`,
    :attr:`pending_update_count`, :attr:`ip_address`, :attr:`last_error_date`,
    :attr:`last_error_message`, :attr:`max_connections`, :attr:`allowed_updates` and
    :attr:`last_synchronization_error_date` are equal.

    .. versionchanged:: 20.0
       :attr:`last_synchronization_error_date` is considered as well when comparing objects of
       this type in terms of equality.

    Args:
        url (:obj:`str`): Webhook URL, may be empty if webhook is not set up.
        has_custom_certificate (:obj:`bool`): :obj:`True`, if a custom certificate was provided for
            webhook certificate checks.
        pending_update_count (:obj:`int`): Number of updates awaiting delivery.
        ip_address (:obj:`str`, optional): Currently used webhook IP address.
        last_error_date (:class:`datetime.datetime`): Optional. Datetime for the most recent
            error that happened when trying to deliver an update via webhook.

            .. versionchanged:: 20.3
                |datetime_localization|
        last_error_message (:obj:`str`, optional): Error message in human-readable format for the
            most recent error that happened when trying to deliver an update via webhook.
        max_connections (:obj:`int`, optional): Maximum allowed number of simultaneous HTTPS
            connections to the webhook for update delivery.
        allowed_updates (Sequence[:obj:`str`], optional): A sequence of update types the bot is
            subscribed to. Defaults to all update types, except
            :attr:`~telegram.Update.chat_member`, :attr:`~telegram.Update.message_reaction`,
            and :attr:`~telegram.Update.message_reaction_count`.

            .. versionchanged:: 20.0
                |sequenceclassargs|

        last_synchronization_error_date (:class:`datetime.datetime`, optional): Datetime of the
            most recent error that happened when trying to synchronize available updates with
            Telegram datacenters.

            .. versionadded:: 20.0

            .. versionchanged:: 20.3
                |datetime_localization|
    Attributes:
        url (:obj:`str`): Webhook URL, may be empty if webhook is not set up.
        has_custom_certificate (:obj:`bool`): :obj:`True`, if a custom certificate was provided for
            webhook certificate checks.
        pending_update_count (:obj:`int`): Number of updates awaiting delivery.
        ip_address (:obj:`str`): Optional. Currently used webhook IP address.
        last_error_date (:class:`datetime.datetime`): Optional. Datetime for the most recent
            error that happened when trying to deliver an update via webhook.

            .. versionchanged:: 20.3
                |datetime_localization|
        last_error_message (:obj:`str`): Optional. Error message in human-readable format for the
            most recent error that happened when trying to deliver an update via webhook.
        max_connections (:obj:`int`): Optional. Maximum allowed number of simultaneous HTTPS
            connections to the webhook for update delivery.
        allowed_updates (tuple[:obj:`str`]): Optional. A tuple of update types the bot is
            subscribed to. Defaults to all update types, except
            :attr:`~telegram.Update.chat_member`, :attr:`~telegram.Update.message_reaction`,
            and :attr:`~telegram.Update.message_reaction_count`.

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        last_synchronization_error_date (:class:`datetime.datetime`, optional): Datetime of the
            most recent error that happened when trying to synchronize available updates with
            Telegram datacenters.

            .. versionadded:: 20.0

            .. versionchanged:: 20.3
                |datetime_localization|
    """

    # Required
    url: str = tg_field(compare=True)
    has_custom_certificate: bool = tg_field(compare=True)
    pending_update_count: int = tg_field(compare=True)
    # Optional
    last_error_date: dtm.datetime | None = tg_field(compare=True, default=None)
    last_error_message: str | None = tg_field(compare=True, default=None)
    max_connections: int | None = tg_field(compare=True, default=None)
    allowed_updates: tuple[str, ...] = tg_field(
        compare=True, default=None, converter=parse_sequence_arg
    )
    ip_address: str | None = tg_field(compare=True, default=None)
    last_synchronization_error_date: dtm.datetime | None = tg_field(compare=True, default=None)
