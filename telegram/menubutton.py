#!/usr/bin/env python
# pylint: disable=too-few-public-methods
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
from typing import Any, ClassVar, Optional, TYPE_CHECKING, Dict, Type

from telegram import TelegramObject, constants, WebAppInfo
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


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

    .. versionadded:: 13.12

    Args:
        type (:obj:`str`): Type of menu button that the instance represents.

    Attributes:
        type (:obj:`str`): Type of menu button that the instance represents.
    """

    __slots__ = ('type', '_id_attrs')

    def __init__(self, type: str, **_kwargs: Any):  # pylint: disable=redefined-builtin
        self.type = type

        self._id_attrs = (self.type,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['MenuButton']:
        """Converts JSON data to the appropriate :class:`MenuButton` object, i.e. takes
        care of selecting the correct subclass.

        Args:
            data (Dict[:obj:`str`, ...]): The JSON data.
            bot (:class:`telegram.Bot`): The bot associated with this object.

        Returns:
            The Telegram object.

        """
        data = cls._parse_data(data)

        if not data:
            return None

        _class_mapping: Dict[str, Type['MenuButton']] = {
            cls.COMMANDS: MenuButtonCommands,
            cls.WEB_APP: MenuButtonWebApp,
            cls.DEFAULT: MenuButtonDefault,
        }

        if cls is MenuButton and data['type'] in _class_mapping:
            return _class_mapping[data['type']].de_json(data, bot=bot)
        return cls(**data, bot=bot)

    COMMANDS: ClassVar[str] = constants.MENU_BUTTON_COMMANDS
    """:const:`telegram.constants.MENU_BUTTON_COMMANDS`"""
    WEB_APP: ClassVar[str] = constants.MENU_BUTTON_WEB_APP
    """:const:`telegram.constants.MENU_BUTTON_WEB_APP`"""
    DEFAULT: ClassVar[str] = constants.MENU_BUTTON_DEFAULT
    """:const:`telegram.constants.MENU_BUTTON_DEFAULT`"""


class MenuButtonCommands(MenuButton):
    """Represents a menu button, which opens the bot's list of commands.

    .. versionadded:: 13.12

    Attributes:
        type (:obj:`str`): :const:`telegram.constants.MENU_BUTTON_COMMANDS`.
    """

    __slots__ = ()

    def __init__(self, **_kwargs: Any):
        super().__init__(type=constants.MENU_BUTTON_COMMANDS)


class MenuButtonWebApp(MenuButton):
    """Represents a menu button, which launches a
    `Web App <https://core.telegram.org/bots/webapps>`_.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type`, :attr:`text` and :attr:`web_app`
    are equal.

    .. versionadded:: 13.12

    Args:
        text (:obj:`str`): Text of the button.
        web_app (:class:`telegram.WebAppInfo`): Description of the Web App that will be launched
            when the user presses the button. The Web App will be able to send an arbitrary
            message on behalf of the user using the method :meth:`~telegram.Bot.answerWebAppQuery`.

    Attributes:
        type (:obj:`str`): :const:`telegram.constants.MENU_BUTTON_WEB_APP`.
        text (:obj:`str`): Text of the button.
        web_app (:class:`telegram.WebAppInfo`): Description of the Web App that will be launched
            when the user presses the button. The Web App will be able to send an arbitrary
            message on behalf of the user using the method :meth:`~telegram.Bot.answerWebAppQuery`.
    """

    __slots__ = (
        'text',
        'web_app',
    )

    def __init__(self, text: str, web_app: WebAppInfo, **_kwargs: Any):
        super().__init__(type=constants.MENU_BUTTON_WEB_APP)
        self.text = text
        self.web_app = web_app

        self._id_attrs = (self.type, self.text, self.web_app)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['MenuButtonWebApp']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['web_app'] = WebAppInfo.de_json(data.get('web_app'), bot)

        return cls(bot=bot, **data)

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()
        data['web_app'] = self.web_app.to_dict()
        return data


class MenuButtonDefault(MenuButton):
    """Describes that no specific value for the menu button was set.

    .. versionadded:: 13.12

    Attributes:
        type (:obj:`str`): :const:`telegram.constants.MENU_BUTTON_DEFAULT`.
    """

    __slots__ = ()

    def __init__(self, **_kwargs: Any):
        super().__init__(type=constants.MENU_BUTTON_DEFAULT)
