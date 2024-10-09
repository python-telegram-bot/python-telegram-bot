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
"""This module contains an object that represents a Encrypted PassportFile."""

from typing import TYPE_CHECKING, Optional

from telegram._telegramobject import TelegramObject
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import JSONDict, ODVInput
from telegram._utils.warnings import warn
from telegram.warnings import PTBDeprecationWarning

if TYPE_CHECKING:
    from telegram import Bot, File, FileCredentials


class PassportFile(TelegramObject):
    """
    This object represents a file uploaded to Telegram Passport. Currently all Telegram Passport
    files are in JPEG format when decrypted and don't exceed 10MB.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        file_size (:obj:`int`): File size in bytes.
        file_date (:obj:`int`): Unix time when the file was uploaded.

            .. deprecated:: 20.6
                This argument will only accept a datetime instead of an integer in future
                major versions.

    Attributes:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        file_size (:obj:`int`): File size in bytes.
    """

    __slots__ = (
        "_credentials",
        "_file_date",
        "file_id",
        "file_size",
        "file_unique_id",
    )

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        file_date: int,
        file_size: int,
        credentials: Optional["FileCredentials"] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        # Required
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.file_size: int = file_size
        self._file_date: int = file_date
        # Optionals

        self._credentials: Optional[FileCredentials] = credentials

        self._id_attrs = (self.file_unique_id,)

        self._freeze()

    def to_dict(self, recursive: bool = True) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict` for details."""
        data = super().to_dict(recursive)
        data["file_date"] = self._file_date
        return data

    @property
    def file_date(self) -> int:
        """:obj:`int`: Unix time when the file was uploaded.

        .. deprecated:: 20.6
            This attribute will return a datetime instead of a integer in future major versions.
        """
        warn(
            PTBDeprecationWarning(
                "20.6",
                "The attribute `file_date` will return a datetime instead of an integer in future"
                " major versions.",
            ),
            stacklevel=2,
        )
        return self._file_date

    @classmethod
    def de_json_decrypted(
        cls, data: Optional[JSONDict], bot: Optional["Bot"], credentials: "FileCredentials"
    ) -> Optional["PassportFile"]:
        """Variant of :meth:`telegram.TelegramObject.de_json` that also takes into account
        passport credentials.

        Args:
            data (dict[:obj:`str`, ...]): The JSON data.
            bot (:class:`telegram.Bot` | :obj:`None`): The bot associated with these object.
                May be :obj:`None`, in which case shortcut methods will not be available.

                .. versionchanged:: 21.4
                   :paramref:`bot` is now optional and defaults to :obj:`None`

                .. deprecated:: 21.4
                   This argument will be converted to an optional argument in future versions.
            credentials (:class:`telegram.FileCredentials`): The credentials

        Returns:
            :class:`telegram.PassportFile`:

        """
        data = cls._parse_data(data)

        if not data:
            return None

        data["credentials"] = credentials

        return super().de_json(data=data, bot=bot)

    @classmethod
    def de_list_decrypted(
        cls,
        data: Optional[list[JSONDict]],
        bot: Optional["Bot"],
        credentials: list["FileCredentials"],
    ) -> tuple[Optional["PassportFile"], ...]:
        """Variant of :meth:`telegram.TelegramObject.de_list` that also takes into account
        passport credentials.

        .. versionchanged:: 20.0

           * Returns a tuple instead of a list.
           * Filters out any :obj:`None` values

        Args:
            data (list[dict[:obj:`str`, ...]]): The JSON data.
            bot (:class:`telegram.Bot` | :obj:`None`): The bot associated with these object.
                May be :obj:`None`, in which case shortcut methods will not be available.

                .. versionchanged:: 21.4
                   :paramref:`bot` is now optional and defaults to :obj:`None`

                .. deprecated:: 21.4
                   This argument will be converted to an optional argument in future versions.
            credentials (:class:`telegram.FileCredentials`): The credentials

        Returns:
            tuple[:class:`telegram.PassportFile`]:

        """
        if not data:
            return ()

        return tuple(
            obj
            for obj in (
                cls.de_json_decrypted(passport_file, bot, credentials[i])
                for i, passport_file in enumerate(data)
            )
            if obj is not None
        )

    async def get_file(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "File":
        """
        Wrapper over :meth:`telegram.Bot.get_file`. Will automatically assign the correct
        credentials to the returned :class:`telegram.File` if originating from
        :attr:`telegram.PassportData.decrypted_data`.

        For the documentation of the arguments, please see :meth:`telegram.Bot.get_file`.

        Returns:
            :class:`telegram.File`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        file = await self.get_bot().get_file(
            file_id=self.file_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        if self._credentials:
            file.set_credentials(self._credentials)
        return file
