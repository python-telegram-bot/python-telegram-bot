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
"""Common base class for media objects"""
from typing import TYPE_CHECKING

from telegram._telegramobject import TelegramObject
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import JSONDict, ODVInput

if TYPE_CHECKING:
    from telegram import Bot, File


class _BaseMedium(TelegramObject):
    """Base class for objects representing the various media file types.
    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        file_size (:obj:`int`, optional): File size.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    Attributes:
        file_id (:obj:`str`): File identifier.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        file_size (:obj:`int`): Optional. File size.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    """

    __slots__ = ("file_id", "file_size", "file_unique_id")

    def __init__(
        self, file_id: str, file_unique_id: str, file_size: int = None, bot: "Bot" = None
    ):
        # Required
        self.file_id: str = str(file_id)
        self.file_unique_id = str(file_unique_id)
        # Optionals
        self.file_size = file_size
        self.set_bot(bot)

        self._id_attrs = (self.file_unique_id,)

    async def get_file(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "File":
        """Convenience wrapper over :attr:`telegram.Bot.get_file`

        For the documentation of the arguments, please see :meth:`telegram.Bot.get_file`.

        Returns:
            :class:`telegram.File`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        return await self.get_bot().get_file(
            file_id=self.file_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
