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
# pylint: disable=redefined-builtin
"""This module contains the classes that represent Telegram InlineQueryResult."""

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class InlineQueryResult(TelegramObject):
    """Baseclass for the InlineQueryResult* classes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Note:
        All URLs passed in inline query results will be available to end users and therefore must
        be assumed to be *public*.

    Args:
        type (:obj:`str`): Type of the result.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.

    Attributes:
        type (:obj:`str`): Type of the result.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.

    """

    __slots__ = ("type", "id")

    def __init__(self, type: str, id: str, *, api_kwargs: JSONDict = None):
        super().__init__(api_kwargs=api_kwargs)

        # Required
        self.type = type
        self.id = str(id)  # pylint: disable=invalid-name

        self._id_attrs = (self.id,)

    def to_dict(self, recursive: bool = True) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict(recursive=recursive)

        # pylint: disable=no-member
        if (
            hasattr(self, "caption_entities")
            and self.caption_entities  # type: ignore[attr-defined]
        ):
            data["caption_entities"] = [
                ce.to_dict() for ce in self.caption_entities  # type: ignore[attr-defined]
            ]

        return data
