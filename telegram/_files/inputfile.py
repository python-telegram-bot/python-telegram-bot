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
"""This module contains an object that represents a Telegram InputFile."""

import logging
import mimetypes
from pathlib import Path
from typing import IO, Optional, Union
from uuid import uuid4

from telegram._utils.types import FieldTuple

_DEFAULT_MIME_TYPE = "application/octet-stream"
logger = logging.getLogger(__name__)


class InputFile:
    """This object represents a Telegram InputFile.

    .. versionchanged:: 20.0

        * The former attribute ``attach`` was renamed to :attr:`attach_name`.
        * Method ``is_image`` was removed. If you pass :obj:`bytes` to :paramref:`obj` and would
          like to have the mime type automatically guessed, please pass :paramref:`filename`
          in addition.

    Args:
        obj (:term:`file object` | :obj:`bytes` | :obj:`str`): An open file descriptor or the files
            content as bytes or string.

            Note:
                If :paramref:`obj` is a string, it will be encoded as bytes via
                :external:obj:`obj.encode('utf-8') <str.encode>`.

            .. versionchanged:: 20.0
                Accept string input.
        filename (:obj:`str`, optional): Filename for this InputFile.
        attach (:obj:`bool`, optional): Pass :obj:`True` if the parameter this file belongs to in
            the request to Telegram should point to the multipart data via an ``attach://`` URI.
            Defaults to `False`.

    Attributes:
        input_file_content (:obj:`bytes`): The binary content of the file to send.
        attach_name (:obj:`str`): Optional. If present, the parameter this file belongs to in
            the request to Telegram should point to the multipart data via a an URI of the form
            ``attach://<attach_name>`` URI.
        filename (:obj:`str`): Filename for the file to be sent.
        mimetype (:obj:`str`): The mimetype inferred from the file to be sent.

    """

    __slots__ = ("filename", "attach_name", "input_file_content", "mimetype")

    def __init__(
        self, obj: Union[IO[bytes], bytes, str], filename: str = None, attach: bool = False
    ):
        if isinstance(obj, bytes):
            self.input_file_content = obj
        elif isinstance(obj, str):
            self.input_file_content = obj.encode("utf-8")
        else:
            self.input_file_content = obj.read()
        self.attach_name: Optional[str] = "attached" + uuid4().hex if attach else None

        if (
            not filename
            and hasattr(obj, "name")
            and not isinstance(obj.name, int)  # type: ignore[union-attr]
        ):
            filename = Path(obj.name).name  # type: ignore[union-attr]

        if filename:
            self.mimetype = mimetypes.guess_type(filename, strict=False)[0] or _DEFAULT_MIME_TYPE
        else:
            self.mimetype = _DEFAULT_MIME_TYPE

        self.filename = filename or self.mimetype.replace("/", ".")

    @property
    def field_tuple(self) -> FieldTuple:
        """Field tuple representing the contents of the file for upload to the Telegram servers.

        Returns:
            Tuple[:obj:`str`, :obj:`bytes`, :obj:`str`]:
        """
        return self.filename, self.input_file_content, self.mimetype

    @property
    def attach_uri(self) -> Optional[str]:
        """URI to insert into the JSON data for uploading the file. Returns :obj:`None`, if
        :attr:`attach_name` is :obj:`None`.
        """
        return f"attach://{self.attach_name}" if self.attach_name else None
