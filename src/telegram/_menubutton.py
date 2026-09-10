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
"""This module contains objects related to Telegram menu buttons."""

from typing import ClassVar

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._webappinfo import WebAppInfo


@tg_dataclass()
class MenuButton(TelegramObject):
    """This object describes the bot's menu button in a private chat. It should be one of

    * :class:`telegram.MenuButtonCommands`
    * :class:`telegram.MenuButtonWebApp`
    * :class:`telegram.MenuButtonDefault`

    If a menu button other than :class:`telegram.MenuButtonDefault` is set for a private chat,
    then it is applied in the chat. Otherwise the default menu button is applied. By default, the
    menu button opens the list of bot commands.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal. For subclasses with additional attributes,
    the notion of equality is overridden.

    .. versionadded:: 20.0

    Args:
        type (:obj:`str`): Type of menu button that the instance represents.

    Attributes:
        type (:obj:`str`): Type of menu button that the instance represents.
    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "commands": "MenuButtonCommands",
            "web_app": "MenuButtonWebApp",
            "default": "MenuButtonDefault",
        },
    )

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.MenuButtonType, value, value)

    type: str = tg_field(compare=True, converter=_type_converter)

    COMMANDS: ClassVar[str] = constants.MenuButtonType.COMMANDS
    """:const:`telegram.constants.MenuButtonType.COMMANDS`"""
    WEB_APP: ClassVar[str] = constants.MenuButtonType.WEB_APP
    """:const:`telegram.constants.MenuButtonType.WEB_APP`"""
    DEFAULT: ClassVar[str] = constants.MenuButtonType.DEFAULT
    """:const:`telegram.constants.MenuButtonType.DEFAULT`"""


@tg_dataclass()
class MenuButtonCommands(MenuButton):
    """Represents a menu button, which opens the bot's list of commands.

    .. include:: inclusions/menu_button_command_video.rst

    .. versionadded:: 20.0
    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.MenuButtonType.COMMANDS`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=MenuButton.COMMANDS)


@tg_dataclass()
class MenuButtonWebApp(MenuButton):
    """Represents a menu button, which launches a
    `Web App <https://core.telegram.org/bots/webapps>`_.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type`, :attr:`text` and :attr:`web_app`
    are equal.

    .. versionadded:: 20.0

    Args:
        text (:obj:`str`): Text of the button.
        web_app (:class:`telegram.WebAppInfo`): Description of the Web App that will be launched
            when the user presses the button. The Web App will be able to send an arbitrary
            message on behalf of the user using the method :meth:`~telegram.Bot.answerWebAppQuery`
            of :class:`~telegram.Bot`. Alternatively, a ``t.me`` link to a Web App of the bot can
            be specified in the object instead of the Web App's URL, in which case the Web App
            will be opened as if the user pressed the link.


    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.MenuButtonType.WEB_APP`.
        text (:obj:`str`): Text of the button.
        web_app (:class:`telegram.WebAppInfo`): Description of the Web App that will be launched
            when the user presses the button. The Web App will be able to send an arbitrary
            message on behalf of the user using the method :meth:`~telegram.Bot.answerWebAppQuery`
            of :class:`~telegram.Bot`. Alternatively, a ``t.me`` link to a Web App of the bot can
            be specified in the object instead of the Web App's URL, in which case the Web App
            will be opened as if the user pressed the link.
    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=MenuButton.WEB_APP)

    text: str = tg_field(compare=True)
    web_app: WebAppInfo = tg_field(compare=True)


@tg_dataclass()
class MenuButtonDefault(MenuButton):
    """Describes that no specific value for the menu button was set.

    .. versionadded:: 20.0
    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.MenuButtonType.DEFAULT`.
    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=MenuButton.DEFAULT)
