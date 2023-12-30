#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
"""This module contains the LinkPreviewOptions class."""


from typing import Optional

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class LinkPreviewOptions(TelegramObject):
    """
    Describes the options used for link preview generation.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`is_disabled`, :attr:`url`, :attr:`prefer_small_media`,
    :attr:`prefer_large_media`, and :attr:`show_above_text` are equal.

    .. versionadded:: NEXT.VERSION

    Args:
        is_disabled (:obj:`bool`, optional): :obj:`True`, if the link preview is disabled.
        url (:obj:`str`, optional): The URL to use for the link preview. If empty, then the first
            URL found in the message text will be used.
        prefer_small_media (:obj:`bool`, optional): :obj:`True`, if the media in the link preview
            is supposed to be shrunk; ignored if the URL isn't explicitly specified or media size
            change isn't supported for the preview.
        prefer_large_media (:obj:`bool`, optional): :obj:`True`, if the media in the link preview
            is supposed to be enlarged; ignored if the URL isn't explicitly specified or media
            size change isn't supported for the preview.
        show_above_text (:obj:`bool`, optional): :obj:`True`, if the link preview must be shown
            above the message text; otherwise, the link preview will be shown below the message
            text.

    Attributes:
        is_disabled (:obj:`bool`): Optional. :obj:`True`, if the link preview is disabled.
        url (:obj:`str`): Optional. The URL to use for the link preview. If empty, then the first
            URL found in the message text will be used.
        prefer_small_media (:obj:`bool`): Optional. :obj:`True`, if the media in the link preview
            is supposed to be shrunk; ignored if the URL isn't explicitly specified or media size
            change isn't supported for the preview.
        prefer_large_media (:obj:`bool`): Optional. :obj:`True`, if the media in the link preview
            is supposed to be enlarged; ignored if the URL isn't explicitly specified or media size
            change isn't supported for the preview.
        show_above_text (:obj:`bool`): Optional. :obj:`True`, if the link preview must be shown
            above the message text; otherwise, the link preview will be shown below the message
            text.
    """

    __slots__ = (
        "is_disabled",
        "url",
        "prefer_small_media",
        "prefer_large_media",
        "show_above_text",
    )

    def __init__(
        self,
        is_disabled: Optional[bool] = None,
        url: Optional[str] = None,
        prefer_small_media: Optional[bool] = None,
        prefer_large_media: Optional[bool] = None,
        show_above_text: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        # Optionals

        self.is_disabled = is_disabled
        self.url = url
        self.prefer_small_media = prefer_small_media
        self.prefer_large_media = prefer_large_media
        self.show_above_text = show_above_text

        self._id_attrs = (
            self.is_disabled,
            self.url,
            self.prefer_small_media,
            self.prefer_large_media,
            self.show_above_text,
        )
        self._freeze()
