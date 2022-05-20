#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2022
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains a class that describes a single parameter of a request to the Bot API."""
import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from telegram._files.inputfile import InputFile
from telegram._files.inputmedia import InputMedia
from telegram._telegramobject import TelegramObject
from telegram._utils.datetime import to_timestamp
from telegram._utils.enum import StringEnum
from telegram._utils.types import UploadFileDict


@dataclass(repr=False, eq=False, order=False, frozen=True)
class RequestParameter:
    """Instances of this class represent a single parameter to be sent along with a request to
    the Bot API.

    .. versionadded:: 20.0

    Warning:
        This class intended is to be used internally by the library and *not* by the user. Changes
        to this class are not considered breaking changes and may not be documented in the
        changelog.

    Args:
        name (:obj:`str`): The name of the parameter.
        value (:obj:`object` | :obj:`None`): The value of the parameter. Must be JSON-dumpable.
        input_files (List[:class:`telegram.InputFile`], optional): A list of files that should be
            uploaded along with this parameter.

    Attributes:
        name (:obj:`str`): The name of the parameter.
        value (:obj:`object` | :obj:`None`): The value of the parameter.
        input_files (List[:class:`telegram.InputFile` | :obj:`None`): A list of files that should
            be uploaded along with this parameter.
    """

    __slots__ = ("name", "value", "input_files")

    name: str
    value: object
    input_files: Optional[List[InputFile]]

    @property
    def json_value(self) -> Optional[str]:
        """The JSON dumped :attr:`value` or :obj:`None` if :attr:`value` is :obj:`None`.
        The latter can currently only happen if :attr:`input_files` has exactly one element that
        must not be uploaded via an attach:// URI.
        """
        if isinstance(self.value, str):
            return self.value
        if self.value is None:
            return None
        return json.dumps(self.value)

    @property
    def multipart_data(self) -> Optional[UploadFileDict]:
        """A dict with the file data to upload, if any."""
        if not self.input_files:
            return None
        return {
            (input_file.attach_name or self.name): input_file.field_tuple
            for input_file in self.input_files
        }

    @staticmethod
    def _value_and_input_files_from_input(  # pylint: disable=too-many-return-statements
        value: object,
    ) -> Tuple[object, List[InputFile]]:
        """Converts `value` into something that we can json-dump. Returns two values:
        1. the JSON-dumpable value. Maybe be `None` in case the value is an InputFile which must
           not be uploaded via an attach:// URI
        2. A list of InputFiles that should be uploaded for this value

        Note that we handle files differently depending on whether attaching them via an URI of the
        form attach://<name> is documented to be allowed or not.
        There was some confusion whether this worked for all files, so that we stick to the
        documented ways for now.
        See https://github.com/tdlib/telegram-bot-api/issues/167 and
        https://github.com/tdlib/telegram-bot-api/issues/259

        This method only does some special casing for our own helper class StringEnum, but not
        for general enums. This is because:
        * tg.constants currently only uses IntEnum as second enum type and json dumping that
          is no problem
        * if a user passes a custom enum, it's unlikely that we can actually properly handle it
          even with some special casing.
        """
        if isinstance(value, datetime):
            return to_timestamp(value), []
        if isinstance(value, StringEnum):
            return value.value, []
        if isinstance(value, InputFile):
            if value.attach_uri:
                return value.attach_uri, [value]
            return None, [value]

        if isinstance(value, InputMedia) and isinstance(value.media, InputFile):
            # We call to_dict and change the returned dict instead of overriding
            # value.media in case the same value is reused for another request
            data = value.to_dict()
            if value.media.attach_uri:
                data["media"] = value.media.attach_uri
            else:
                data.pop("media", None)

            thumb = data.get("thumb", None)
            if isinstance(thumb, InputFile):
                if thumb.attach_uri:
                    data["thumb"] = thumb.attach_uri
                else:
                    data.pop("thumb", None)
                return data, [value.media, thumb]

            return data, [value.media]
        if isinstance(value, TelegramObject):
            # Needs to be last, because InputMedia is a subclass of TelegramObject
            return value.to_dict(), []
        return value, []

    @classmethod
    def from_input(cls, key: str, value: object) -> "RequestParameter":
        """Builds an instance of this class for a given key-value pair that represents the raw
        input as passed along from a method of :class:`telegram.Bot`.
        """
        if isinstance(value, list):
            param_values = []
            input_files = []
            for obj in value:
                param_value, input_file = cls._value_and_input_files_from_input(obj)
                if param_value is not None:
                    param_values.append(param_value)
                input_files.extend(input_file)
            return RequestParameter(
                name=key, value=param_values, input_files=input_files if input_files else None
            )

        param_value, input_files = cls._value_and_input_files_from_input(value)
        return RequestParameter(
            name=key, value=param_value, input_files=input_files if input_files else None
        )
