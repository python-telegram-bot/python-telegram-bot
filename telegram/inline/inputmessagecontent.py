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
"""This module contains the classes that represent Telegram InputMessageContent."""

from telegram import TelegramObject


class InputMessageContent(TelegramObject):
    """Base class for Telegram InputMessageContent Objects.

    See: :class:`telegram.InputContactMessageContent`,
    :class:`telegram.InputLocationMessageContent`, :class:`telegram.InputTextMessageContent` and
    :class:`telegram.InputVenueMessageContent` for more details.

    """
    @property
    def _has_parse_mode(self) -> bool:
        return hasattr(self, 'parse_mode')

    @property
    def _has_disable_web_page_preview(self) -> bool:
        return hasattr(self, 'disable_web_page_preview')
