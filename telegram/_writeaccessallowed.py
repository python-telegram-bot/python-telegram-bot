#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
"""This module contains objects related to the write access allowed service message."""
from typing import Optional

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class WriteAccessAllowed(TelegramObject):
    """
    This object represents a service message about a user allowing a bot to write messages after
    adding the bot to the attachment menu or launching a Web App from a link.

    .. versionadded:: 20.0

    Args:
        web_app_name (:obj:`str`, optional): Name of the Web App which was launched from a link.

            .. versionadded:: 20.3

    Attributes:
        web_app_name (:obj:`str`): Optional. Name of the Web App which was launched from a link.

            .. versionadded:: 20.3

    """

    __slots__ = ("web_app_name",)

    def __init__(self, web_app_name: str = None, *, api_kwargs: JSONDict = None):
        super().__init__(api_kwargs=api_kwargs)
        self.web_app_name: Optional[str] = web_app_name

        self._freeze()
