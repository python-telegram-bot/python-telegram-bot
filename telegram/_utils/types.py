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
"""This module contains custom typing aliases for internal use within the library.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
from pathlib import Path
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Collection,
    Dict,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from telegram import (
        ForceReply,
        InlineKeyboardMarkup,
        InputFile,
        ReplyKeyboardMarkup,
        ReplyKeyboardRemove,
    )
    from telegram._utils.defaultvalue import DefaultValue

FileLike = Union[IO[bytes], "InputFile"]
"""Either a bytes-stream (e.g. open file handler) or a :class:`telegram.InputFile`."""

FilePathInput = Union[str, Path]
"""A filepath either as string or as :obj:`pathlib.Path` object."""

FileInput = Union[FilePathInput, FileLike, bytes, str]
"""Valid input for passing files to Telegram. Either a file id as string, a file like object,
a local file path as string, :class:`pathlib.Path` or the file contents as :obj:`bytes`."""

JSONDict = Dict[str, Any]
"""Dictionary containing response from Telegram or data to send to the API."""

DVValueType = TypeVar("DVValueType")  # pylint: disable=invalid-name
DVType = Union[DVValueType, "DefaultValue[DVValueType]"]
"""Generic type for a variable which can be either `type` or `DefaultVaule[type]`."""
ODVInput = Optional[Union["DefaultValue[DVValueType]", DVValueType, "DefaultValue[None]"]]
"""Generic type for bot method parameters which can have defaults. ``ODVInput[type]`` is the same
as ``Optional[Union[DefaultValue[type], type, DefaultValue[None]]``."""
DVInput = Union["DefaultValue[DVValueType]", DVValueType, "DefaultValue[None]"]
"""Generic type for bot method parameters which can have defaults. ``DVInput[type]`` is the same
as ``Union[DefaultValue[type], type, DefaultValue[None]]``."""

RT = TypeVar("RT")
SCT = Union[RT, Collection[RT]]  # pylint: disable=invalid-name
"""Single instance or collection of instances."""

ReplyMarkup = Union[
    "InlineKeyboardMarkup", "ReplyKeyboardMarkup", "ReplyKeyboardRemove", "ForceReply"
]
"""Type alias for reply markup objects.

.. versionadded:: 20.0
"""

FieldTuple = Tuple[str, bytes, str]
"""Alias for return type of `InputFile.field_tuple`."""
UploadFileDict = Dict[str, FieldTuple]
"""Dictionary containing file data to be uploaded to the API."""

HTTPVersion = Literal["1.1", "2.0", "2"]
"""Allowed HTTP versions.

.. versionadded:: 20.4"""

CorrectOptionID = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

MarkdownVersion = Literal[1, 2]

SocketOpt = Union[
    Tuple[int, int, int],
    Tuple[int, int, Union[bytes, bytearray]],
    Tuple[int, int, None, int],
]
