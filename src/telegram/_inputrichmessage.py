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
"""This module contains objects that are related to Telegram input rich messages."""

from telegram._inline.inputmessagecontent import InputMessageContent
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class InputRichMessage(TelegramObject):
    """
    Describes a rich message to be sent.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`html` and :attr:`markdown` are equal.

    .. versionadded:: NEXT.VERSION

    Args:
        html (:obj:`str`, optional): Content of the rich message to send described using HTML
            formatting. Mutually exclusive with :paramref:`markdown`.
        markdown (:obj:`str`, optional): Content of the rich message to send described using
            Markdown formatting. Mutually exclusive with :paramref:`html`.
        is_rtl (:obj:`bool`, optional): Pass :obj:`True` if the rich message must be shown
            right-to-left.
        skip_entity_detection (:obj:`bool`, optional): Pass :obj:`True` to skip automatic
            detection of entities in the text.

    Attributes:
        html (:obj:`str`): Optional. Content of the rich message to send described using HTML
            formatting.
        markdown (:obj:`str`): Optional. Content of the rich message to send described using
            Markdown formatting.
        is_rtl (:obj:`bool`): Optional. :obj:`True`, if the rich message must be shown
            right-to-left.
        skip_entity_detection (:obj:`bool`): Optional. :obj:`True`, if automatic detection of
            entities in the text should be skipped.
    """

    __slots__ = ("html", "is_rtl", "markdown", "skip_entity_detection")

    def __init__(
        self,
        html: str | None = None,
        markdown: str | None = None,
        is_rtl: bool | None = None,
        skip_entity_detection: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.html: str | None = html
        self.markdown: str | None = markdown
        self.is_rtl: bool | None = is_rtl
        self.skip_entity_detection: bool | None = skip_entity_detection

        self._id_attrs = (self.html, self.markdown)

        self._freeze()


class InputRichMessageContent(InputMessageContent):
    """
    Represents the content of a rich message to be sent as the result of an inline query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`rich_message` is equal.

    .. versionadded:: NEXT.VERSION

    Args:
        rich_message (:class:`telegram.InputRichMessage`): The message to be sent.

    Attributes:
        rich_message (:class:`telegram.InputRichMessage`): The message to be sent.
    """

    __slots__ = ("rich_message",)

    def __init__(
        self,
        rich_message: InputRichMessage,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        with self._unfrozen():
            self.rich_message: InputRichMessage = rich_message
            self._id_attrs = (self.rich_message,)
