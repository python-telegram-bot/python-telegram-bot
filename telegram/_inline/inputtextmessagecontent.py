#!/usr/bin/env python
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
"""This module contains the classes that represent Telegram InputTextMessageContent."""

from typing import Any, List, Tuple, Union

from telegram._inline.inputmessagecontent import InputMessageContent
from telegram._messageentity import MessageEntity
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import JSONDict, ODVInput


class InputTextMessageContent(InputMessageContent):
    """
    Represents the content of a text message to be sent as the result of an inline query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`message_text` is equal.

    .. seealso:: `Inline Example <examples.inlinebot.html>`_

    Args:
        message_text (:obj:`str`): Text of the message to be sent,
            1-:tg-const:`telegram.constants.MessageLimit.TEXT_LENGTH` characters after entities
            parsing.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in your bot's message. See the constants
            in :class:`telegram.constants.ParseMode` for the available modes.
        entities (List[:class:`telegram.MessageEntity`], optional): List of special
            entities that appear in the caption, which can be specified instead of
            :paramref:`parse_mode`.
        disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in the
            sent message.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        message_text (:obj:`str`): Text of the message to be sent,
            1-:tg-const:`telegram.constants.MessageLimit.TEXT_LENGTH` characters after entities
            parsing.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in your bot's message. See the constants
            in :class:`telegram.constants.ParseMode` for the available modes.
        entities (List[:class:`telegram.MessageEntity`]): Optional. List of special
            entities that appear in the caption, which can be specified instead of
            :paramref:`parse_mode`.
        disable_web_page_preview (:obj:`bool`): Optional. Disables link previews for links in the
            sent message.

    """

    __slots__ = ("disable_web_page_preview", "parse_mode", "entities", "message_text")

    def __init__(
        self,
        message_text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        entities: Union[Tuple[MessageEntity, ...], List[MessageEntity]] = None,
        **_kwargs: Any,
    ):
        # Required
        self.message_text = message_text
        # Optionals
        self.parse_mode = parse_mode
        self.entities = entities
        self.disable_web_page_preview = disable_web_page_preview

        self._id_attrs = (self.message_text,)

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()

        if self.entities:
            data["entities"] = [ce.to_dict() for ce in self.entities]

        return data
