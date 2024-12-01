#!/usr/bin/env python
# pylint: disable=redefined-builtin
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
# along with this program.  If not, see [http://www.gnu.org/licenses/]
"""This module contains classes related to gifs sent by bots."""
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional

from telegram._files.sticker import Sticker
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class Gift(TelegramObject):
    """This object represents a gift that can be sent by the bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`id` is equal.

    .. versionadded:: 21.8

    Args:
        id (:obj:`str`): Unique identifier of the gift
        sticker (:class:`~telegram.Sticker`): The sticker that represents the gift
        star_count (:obj:`int`): The number of Telegram Stars that must be paid to send the sticker
        total_count (:obj:`int`, optional): The total number of the gifts of this type that can be
            sent; for limited gifts only
        remaining_count (:obj:`int`, optional): The number of remaining gifts of this type that can
            be sent; for limited gifts only

    Attributes:
        id (:obj:`str`): Unique identifier of the gift
        sticker (:class:`~telegram.Sticker`): The sticker that represents the gift
        star_count (:obj:`int`): The number of Telegram Stars that must be paid to send the sticker
        total_count (:obj:`int`): Optional. The total number of the gifts of this type that can be
            sent; for limited gifts only
        remaining_count (:obj:`int`): Optional. The number of remaining gifts of this type that can
            be sent; for limited gifts only

    """

    __slots__ = ("id", "remaining_count", "star_count", "sticker", "total_count")

    def __init__(
        self,
        id: str,
        sticker: Sticker,
        star_count: int,
        total_count: Optional[int] = None,
        remaining_count: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.id: str = id
        self.sticker: Sticker = sticker
        self.star_count: int = star_count
        self.total_count: Optional[int] = total_count
        self.remaining_count: Optional[int] = remaining_count

        self._id_attrs = (self.id,)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: Optional["Bot"] = None) -> Optional["Gift"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["sticker"] = Sticker.de_json(data.get("sticker"), bot)
        return cls(**data)


class Gifts(TelegramObject):
    """This object represent a list of gifts.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`gifts` are equal.

    .. versionadded:: 21.8

    Args:
        gifts (Sequence[:class:`Gift`]): The sequence of gifts

    Attributes:
        gifts (tuple[:class:`Gift`]): The sequence of gifts

    """

    __slots__ = ("gifts",)

    def __init__(
        self,
        gifts: Sequence[Gift],
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.gifts: tuple[Gift, ...] = parse_sequence_arg(gifts)

        self._id_attrs = (self.gifts,)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: Optional["Bot"] = None) -> Optional["Gifts"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["gifts"] = Gift.de_list(data.get("gifts"), bot)
        return cls(**data)
