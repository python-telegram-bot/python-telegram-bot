#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
"""Base class for Telegram Objects."""
try:
    import ujson as json
except ImportError:
    import json  # type: ignore[no-redef]

import warnings

from telegram.utils.types import JSONDict
from typing import Tuple, Any, Optional, Type, TypeVar, TYPE_CHECKING, List

if TYPE_CHECKING:
    from telegram import Bot

TO = TypeVar('TO', bound='TelegramObject', covariant=True)


class TelegramObject:
    """Base class for most telegram objects."""

    # def __init__(self, *args: Any, **kwargs: Any):
    #     pass

    _id_attrs: Tuple[Any, ...] = ()

    def __str__(self) -> str:
        return str(self.to_dict())

    def __getitem__(self, item: str) -> Any:
        return self.__dict__[item]

    @staticmethod
    def parse_data(data: Optional[JSONDict]) -> Optional[JSONDict]:
        if not data:
            return None
        return data.copy()

    @classmethod
    def de_json(cls: Type[TO], data: Optional[JSONDict], bot: 'Bot') -> Optional[TO]:
        data = cls.parse_data(data)

        if not data:
            return None

        if cls == TelegramObject:
            return cls()
        else:
            return cls(bot=bot, **data)  # type: ignore[call-arg]

    @classmethod
    def de_list(cls: Type[TO],
                data: Optional[List[JSONDict]],
                bot: 'Bot') -> List[Optional[TO]]:
        if not data:
            return []

        return [cls.de_json(d, bot) for d in data]

    def to_json(self) -> str:
        """
        Returns:
            :obj:`str`

        """

        return json.dumps(self.to_dict())

    def to_dict(self) -> JSONDict:
        data = dict()

        for key in iter(self.__dict__):
            if key == 'bot' or key.startswith('_'):
                continue

            value = self.__dict__[key]
            if value is not None:
                if hasattr(value, 'to_dict'):
                    data[key] = value.to_dict()
                else:
                    data[key] = value

        if data.get('from_user'):
            data['from'] = data.pop('from_user', None)
        return data

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            if self._id_attrs == ():
                warnings.warn("Objects of type {} can not be meaningfully tested for "
                              "equivalence.".format(self.__class__.__name__))
            if other._id_attrs == ():
                warnings.warn("Objects of type {} can not be meaningfully tested for "
                              "equivalence.".format(other.__class__.__name__))
            return self._id_attrs == other._id_attrs
        return super().__eq__(other)  # pylint: disable=no-member

    def __hash__(self) -> int:
        if self._id_attrs:
            return hash((self.__class__, self._id_attrs))  # pylint: disable=no-member
        return super().__hash__()
