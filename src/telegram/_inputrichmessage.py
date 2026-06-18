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
"""This module contains the InputRichMessage class."""

from telegram._inline.inputmessagecontent import InputMessageContent
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class InputRichMessage(TelegramObject):
    """Describes a rich message to be sent.

    Rich messages support advanced structured formatting options like headings, lists, tables,
    media, block quotations, collapsible blocks, footnotes, and formulas. Exactly one of the
    arguments :paramref:`html` or :paramref:`markdown` must be used.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`html`, :attr:`markdown`, :attr:`is_rtl` and
    :attr:`skip_entity_detection` are equal.

    .. versionadded:: NEXT.VERSION

    Args:
        html (:obj:`str`, optional): Content of the rich message to send described using HTML
            formatting. See `rich message formatting options
            <https://core.telegram.org/bots/api#rich-message-formatting-options>`_ for more
            details.
        markdown (:obj:`str`, optional): Content of the rich message to send described using
            Markdown formatting. See `rich message formatting options
            <https://core.telegram.org/bots/api#rich-message-formatting-options>`_ for more
            details.
        is_rtl (:obj:`bool`, optional): Pass :obj:`True` if the rich message must be shown
            right-to-left.
        skip_entity_detection (:obj:`bool`, optional): Pass :obj:`True` to skip automatic detection
            of entities (e.g., URLs, email addresses, username mentions, hashtags, cashtags, bot
            commands, or phone numbers) in the text.

    Attributes:
        html (:obj:`str`): Optional. Content of the rich message to send described using HTML
            formatting.
        markdown (:obj:`str`): Optional. Content of the rich message to send described using
            Markdown formatting.
        is_rtl (:obj:`bool`): Optional. :obj:`True`, if the rich message must be shown
            right-to-left.
        skip_entity_detection (:obj:`bool`): Optional. :obj:`True`, to skip automatic detection of
            entities in the text.
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

        # Optionals
        self.html: str | None = html
        self.markdown: str | None = markdown
        self.is_rtl: bool | None = is_rtl
        self.skip_entity_detection: bool | None = skip_entity_detection

        self._id_attrs = (
            self.html,
            self.markdown,
            self.is_rtl,
            self.skip_entity_detection,
        )

        self._freeze()


class InputRichMessageContent(InputMessageContent):
    """Represents the content of a rich message to be sent as the result of an inline query.

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
