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
"""Base class for Telegram Objects."""
try:
    import ujson as json
except ImportError:
    import json  # type: ignore[no-redef]

from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, Tuple

from telegram._utils.types import JSONDict
from telegram._utils.warnings import warn

if TYPE_CHECKING:
    from telegram import Bot

TO = TypeVar('TO', bound='TelegramObject', covariant=True)


class TelegramObject:
    """Base class for most Telegram objects."""

    # type hints in __new__ are not read by mypy (https://github.com/python/mypy/issues/1021). As a
    # workaround we can type hint instance variables in __new__ using a syntax defined in PEP 526 -
    # https://www.python.org/dev/peps/pep-0526/#class-and-instance-variable-annotations
    if TYPE_CHECKING:
        _id_attrs: Tuple[object, ...]
        _bot: Optional['Bot']
    # Adding slots reduces memory usage & allows for faster attribute access.
    # Only instance variables should be added to __slots__.
    __slots__ = (
        '_id_attrs',
        '_bot',
    )

    # pylint: disable=unused-argument
    def __new__(cls, *args: object, **kwargs: object) -> 'TelegramObject':
        # We add _id_attrs in __new__ instead of __init__ since we want to add this to the slots
        # w/o calling __init__ in all of the subclasses. This is what we also do in BaseFilter.
        instance = super().__new__(cls)
        instance._id_attrs = ()
        instance._bot = None
        return instance

    def __str__(self) -> str:
        return str(self.to_dict())

    def __getitem__(self, item: str) -> object:
        return getattr(self, item, None)

    @staticmethod
    def _parse_data(data: Optional[JSONDict]) -> Optional[JSONDict]:
        return None if data is None else data.copy()

    @classmethod
    def de_json(cls: Type[TO], data: Optional[JSONDict], bot: 'Bot') -> Optional[TO]:
        """Converts JSON data to a Telegram object.

        Args:
            data (Dict[:obj:`str`, ...]): The JSON data.
            bot (:class:`telegram.Bot`): The bot associated with this object.

        Returns:
            The Telegram object.

        """
        data = cls._parse_data(data)

        if data is None:
            return None

        if cls == TelegramObject:
            return cls()
        return cls(bot=bot, **data)

    @classmethod
    def de_list(cls: Type[TO], data: Optional[List[JSONDict]], bot: 'Bot') -> List[Optional[TO]]:
        """Converts JSON data to a list of Telegram objects.

        Args:
            data (Dict[:obj:`str`, ...]): The JSON data.
            bot (:class:`telegram.Bot`): The bot associated with these objects.

        Returns:
            A list of Telegram objects.

        """
        if not data:
            return []

        return [cls.de_json(d, bot) for d in data]

    def to_json(self) -> str:
        """Gives a JSON representation of object.

        Returns:
            :obj:`str`
        """
        return json.dumps(self.to_dict())

    def to_dict(self) -> JSONDict:
        """Gives representation of object as :obj:`dict`.

        Returns:
            :obj:`dict`
        """
        data = {}

        # We want to get all attributes for the class, using self.__slots__ only includes the
        # attributes used by that class itself, and not its superclass(es). Hence we get its MRO
        # and then get their attributes. The `[:-2]` slice excludes the `object` class & the
        # TelegramObject class itself.
        attrs = {attr for cls in self.__class__.__mro__[:-2] for attr in cls.__slots__}
        for key in attrs:
            if key == 'bot' or key.startswith('_'):
                continue

            value = getattr(self, key, None)
            if value is not None:
                if hasattr(value, 'to_dict'):
                    data[key] = value.to_dict()
                else:
                    data[key] = value

        if data.get('from_user'):
            data['from'] = data.pop('from_user', None)
        return data

    def get_bot(self) -> 'Bot':
        """Returns the :class:`telegram.Bot` instance associated with this object.

        .. seealso:: :meth: `set_bot`

        .. versionadded: 14.0

        Raises:
            RuntimeError: If no :class:`telegram.Bot` instance was set for this object.
        """
        if self._bot is None:
            raise RuntimeError(
                'This object has no bot associated with it. \
                Shortcuts cannot be used.'
            )
        return self._bot

    def set_bot(self, bot: Optional['Bot']) -> None:
        """Sets the :class:`telegram.Bot` instance associated with this object.

        .. seealso:: :meth: `get_bot`

        .. versionadded: 14.0

        Arguments:
            bot (:class:`telegram.Bot` | :obj:`None`): The bot instance.
        """
        self._bot = bot

    def __eq__(self, other: object) -> bool:
        # pylint: disable=no-member
        if isinstance(other, self.__class__):
            if self._id_attrs == ():
                warn(
                    f"Objects of type {self.__class__.__name__} can not be meaningfully tested for"
                    " equivalence.",
                    stacklevel=2,
                )
            if other._id_attrs == ():
                warn(
                    f"Objects of type {other.__class__.__name__} can not be meaningfully tested"
                    " for equivalence.",
                    stacklevel=2,
                )
            return self._id_attrs == other._id_attrs
        return super().__eq__(other)

    def __hash__(self) -> int:
        # pylint: disable=no-member
        if self._id_attrs:
            return hash((self.__class__, self._id_attrs))
        return super().__hash__()
