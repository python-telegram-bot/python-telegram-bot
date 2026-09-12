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
"""This module contains an object that represents a Telegram InputRichMessage."""

from collections.abc import Sequence

from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.types import JSONDict


class InputRichMessage(TelegramObject):
    """Describes a rich message to be sent.

    Exactly one of :paramref:`html`, :paramref:`markdown`, or :paramref:`blocks` must be supplied.
    This initial send-side model accepts block and media dictionaries so applications can use new
    Bot API block variants without waiting for a library release for every variant.

    .. versionadded:: 22.9

    Args:
        html (:obj:`str`, optional): Rich content using Telegram's rich HTML syntax.
        markdown (:obj:`str`, optional): Rich content using Telegram's rich Markdown syntax.
        blocks (Sequence[:obj:`dict`], optional): Structured input-rich-block objects.
        media (Sequence[:obj:`dict`], optional): Media referenced from HTML or Markdown via
            ``tg://photo``, ``tg://video``, ``tg://document``, or ``tg://audio`` links.
        is_rtl (:obj:`bool`, optional): Whether the message is laid out right-to-left.
        skip_entity_detection (:obj:`bool`, optional): Disable automatic entity detection.
        api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to Telegram.

    Raises:
        ValueError: If not exactly one content representation is supplied.
    """

    __slots__ = ("blocks", "html", "is_rtl", "markdown", "media", "skip_entity_detection")

    def __init__(
        self,
        *,
        html: str | None = None,
        markdown: str | None = None,
        blocks: Sequence[JSONDict] | None = None,
        media: Sequence[JSONDict] | None = None,
        is_rtl: bool | None = None,
        skip_entity_detection: bool | None = None,
        api_kwargs: JSONDict | None = None,
    ):
        representations = (html is not None, markdown is not None, blocks is not None)
        if sum(representations) != 1:
            raise ValueError("Exactly one of html, markdown, or blocks must be supplied.")
        if blocks is not None and not blocks:
            raise ValueError("blocks must not be empty.")

        super().__init__(api_kwargs=api_kwargs)
        with self._unfrozen():
            self.html: str | None = html
            self.markdown: str | None = markdown
            self.blocks: tuple[JSONDict, ...] = parse_sequence_arg(blocks)
            self.media: tuple[JSONDict, ...] = parse_sequence_arg(media)
            self.is_rtl: bool | None = is_rtl
            self.skip_entity_detection: bool | None = skip_entity_detection
            self._id_attrs = (self.html, self.markdown, self.blocks)
