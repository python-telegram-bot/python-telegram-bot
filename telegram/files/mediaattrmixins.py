#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
"""Base class for Telegram InputMedia Objects."""


from typing import Optional, TYPE_CHECKING

from telegram.utils.files import parse_file_input
from telegram.utils.types import FileInput

if TYPE_CHECKING:
    from telegram import PhotoSize


class _WidthHeightMixin:
    def __init__(self, width: int, height: int):
        self.width: int = int(width)
        self.height: int = int(height)


class _DurationMixin:
    def __init__(self, duration: int):
        self.duration: int = duration


class _FileNameMixin:
    def __init__(self, file_name: str = None):
        self.file_name: Optional[str] = file_name


class _MimeTypeMixin:
    def __init__(self, mime_type: str = None):
        self.mime_type: Optional[str] = mime_type


class _TitleMixin:
    def __init__(self, title: str = None):
        self.title: Optional[str] = title


class _ThumbFiMixin:
    def __init__(self, thumb: FileInput = None):
        thumb = parse_file_input(thumb, attach=True) if thumb is not None else thumb
        self.thumb: Optional[FileInput] = thumb


class _ThumbPsMixin:
    def __init__(self, thumb: 'PhotoSize' = None):
        self.thumb: Optional['PhotoSize'] = thumb
