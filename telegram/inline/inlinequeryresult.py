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
# pylint: disable=W0622
"""This module contains the classes that represent Telegram InlineQueryResult."""

from typing import Any

from telegram import TelegramObject
from telegram.utils.types import JSONDict


class InlineQueryResult(TelegramObject):
    """Baseclass for the InlineQueryResult* classes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Note:
        All URLs passed in inline query results will be available to end users and therefore must
        be assumed to be public.

    Args:
        type (:obj:`str`): Type of the result.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        type (:obj:`str`): Type of the result.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.

    """

    def __init__(self, type: str, id: str, **_kwargs: Any):
        # Required
        self.type = str(type)
        self.id = str(id)  # pylint: disable=C0103

        self._id_attrs = (self.id,)

    def to_dict(self) -> JSONDict:
        data = super().to_dict()

        # pylint: disable=E1101
        if (
            hasattr(self, 'caption_entities')
            and self.caption_entities  # type: ignore[attr-defined]
        ):
            data['caption_entities'] = [
                ce.to_dict() for ce in self.caption_entities  # type: ignore[attr-defined]
            ]

        return data
