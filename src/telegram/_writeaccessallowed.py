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
"""This module contains objects related to the write access allowed service message."""

from telegram._telegramobject import TelegramObject
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class WriteAccessAllowed(TelegramObject):
    """
    This object represents a service message about a user allowing a bot to write messages after
    adding it to the attachment menu, launching a Web App from a link, or accepting an explicit
    request from a Web App sent by the method
    `requestWriteAccess <https://core.telegram.org/bots/webapps#initializing-mini-apps>`_.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`web_app_name` is equal.

    .. versionadded:: 20.0
    .. versionchanged:: 20.6
       Added custom equality comparison for objects of this class.

    Args:
        web_app_name (:obj:`str`, optional): Name of the Web App, if the access was granted when
            the Web App was launched from a link.

            .. versionadded:: 20.3
        from_request (:obj:`bool`, optional): :obj:`True`, if the access was granted after the user
         accepted an explicit request from a Web App sent by the method
         `requestWriteAccess <https://core.telegram.org/bots/webapps#initializing-mini-apps>`_.

         .. versionadded:: 20.6
        from_attachment_menu (:obj:`bool`, optional): :obj:`True`, if the access was granted when
         the bot was added to the attachment or side menu.

         .. versionadded:: 20.6

    Attributes:
        web_app_name (:obj:`str`): Optional. Name of the Web App, if the access was granted when
            the Web App was launched from a link.

            .. versionadded:: 20.3
        from_request (:obj:`bool`): Optional. :obj:`True`, if the access was granted after the user
            accepted an explicit request from a Web App.

            .. versionadded:: 20.6
        from_attachment_menu (:obj:`bool`): Optional. :obj:`True`, if the access was granted when
            the bot was added to the attachment or side menu.

            .. versionadded:: 20.6

    """

    web_app_name: str | None = tg_field(compare=True, default=None)
    from_request: bool | None = tg_field(default=None)
    from_attachment_menu: bool | None = tg_field(default=None)
