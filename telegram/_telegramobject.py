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
import json
from copy import deepcopy
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Type, TypeVar, Union

from telegram._utils.types import JSONDict
from telegram._utils.warnings import warn

if TYPE_CHECKING:
    from telegram import Bot

Tele_co = TypeVar("Tele_co", bound="TelegramObject", covariant=True)


class TelegramObject:
    """Base class for most Telegram objects.

    Objects of this type are subscriptable with strings, where ``telegram_object[attribute_name]``
    is equivalent to ``telegram_object.attribute_name``. If the object does not have an attribute
    with the appropriate name, a :exc:`KeyError` will be raised.

    When objects of this type are pickled, the :class:`~telegram.Bot` attribute associated with the
    object will be removed. However, when copying the object via :func:`copy.deepcopy`, the copy
    will have the *same* bot instance associated with it, i.e::

        assert telegram_object.get_bot() is copy.deepcopy(telegram_object).get_bot()

    .. versionchanged:: 20.0
        ``telegram_object['from']`` will look up the key ``from_user``. This is to account for
        special cases like :attr:`Message.from_user` that deviate from the official Bot API.
    """

    # type hints in __new__ are not read by mypy (https://github.com/python/mypy/issues/1021). As a
    # workaround we can type hint instance variables in __new__ using a syntax defined in PEP 526 -
    # https://www.python.org/dev/peps/pep-0526/#class-and-instance-variable-annotations
    if TYPE_CHECKING:
        _id_attrs: Tuple[object, ...]
        _bot: Optional["Bot"]
    # Adding slots reduces memory usage & allows for faster attribute access.
    # Only instance variables should be added to __slots__.
    __slots__ = ("_id_attrs", "_bot")

    # pylint: disable=unused-argument
    def __new__(cls, *args: object, **kwargs: object) -> "TelegramObject":
        # We add _id_attrs in __new__ instead of __init__ since we want to add this to the slots
        # w/o calling __init__ in all of the subclasses.
        instance = super().__new__(cls)
        instance._id_attrs = ()
        instance._bot = None
        return instance

    def __str__(self) -> str:
        return str(self.to_dict())

    def __getitem__(self, item: str) -> object:
        if item == "from":
            item = "from_user"
        try:
            return getattr(self, item)
        except AttributeError as exc:
            raise KeyError(
                f"Objects of type {self.__class__.__name__} don't have an attribute called "
                f"`{item}`."
            ) from exc

    def __getstate__(self) -> Dict[str, Union[str, object]]:
        """
        This method is used for pickling. We remove the bot attribute of the object since those
        are not pickable.
        """
        return self._get_attrs(include_private=True, recursive=False, remove_bot=True)

    def __setstate__(self, state: dict) -> None:
        """
        This method is used for unpickling. The data, which is in the form a dictionary, is
        converted back into a class. Should be modified in place.
        """
        for key, val in state.items():
            setattr(self, key, val)

    def __deepcopy__(self: Tele_co, memodict: dict) -> Tele_co:
        """This method deepcopies the object and sets the bot on the newly created copy."""
        bot = self._bot  # Save bot so we can set it after copying
        self.set_bot(None)  # set to None so it is not deepcopied
        cls = self.__class__
        result = cls.__new__(cls)  # create a new instance
        memodict[id(self)] = result  # save the id of the object in the dict

        attrs = self._get_attrs(include_private=True)  # get all its attributes

        for k in attrs:  # now we set the attributes in the deepcopied object
            setattr(result, k, deepcopy(getattr(self, k), memodict))

        result.set_bot(bot)  # Assign the bots back
        self.set_bot(bot)
        return result  # type: ignore[return-value]

    def _get_attrs(
        self,
        include_private: bool = False,
        recursive: bool = False,
        remove_bot: bool = False,
    ) -> Dict[str, Union[str, object]]:
        """This method is used for obtaining the attributes of the object.

        Args:
            include_private (:obj:`bool`): Whether the result should include private variables.
            recursive (:obj:`bool`): If :obj:`True`, will convert any TelegramObjects (if found) in
                the attributes to a dictionary. Else, preserves it as an object itself.
            remove_bot (:obj:`bool`): Whether the bot should be included in the result.

        Returns:
            :obj:`dict`: A dict where the keys are attribute names and values are their values.
        """
        data = {}

        if not recursive:
            try:
                # __dict__ has attrs from superclasses, so no need to put in the for loop below
                data.update(self.__dict__)
            except AttributeError:
                pass
        # We want to get all attributes for the class, using self.__slots__ only includes the
        # attributes used by that class itself, and not its superclass(es). Hence, we get its MRO
        # and then get their attributes. The `[:-1]` slice excludes the `object` class
        for cls in self.__class__.__mro__[:-1]:
            for key in cls.__slots__:  # type: ignore[attr-defined]
                if not include_private and key.startswith("_"):
                    continue

                value = getattr(self, key, None)
                if value is not None:
                    if recursive and hasattr(value, "to_dict"):
                        data[key] = value.to_dict()  # pylint: disable=no-member
                    else:
                        data[key] = value
                elif not recursive:
                    data[key] = value

        if recursive and data.get("from_user"):
            data["from"] = data.pop("from_user", None)
        if remove_bot:
            data.pop("_bot", None)
        return data

    @staticmethod
    def _parse_data(data: Optional[JSONDict]) -> Optional[JSONDict]:
        return None if data is None else data.copy()

    @classmethod
    def de_json(cls: Type[Tele_co], data: Optional[JSONDict], bot: "Bot") -> Optional[Tele_co]:
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
    def de_list(
        cls: Type[Tele_co], data: Optional[List[JSONDict]], bot: "Bot"
    ) -> List[Optional[Tele_co]]:
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
        return self._get_attrs(recursive=True)

    def get_bot(self) -> "Bot":
        """Returns the :class:`telegram.Bot` instance associated with this object.

        .. seealso:: :meth:`set_bot`

        .. versionadded: 20.0

        Raises:
            RuntimeError: If no :class:`telegram.Bot` instance was set for this object.
        """
        if self._bot is None:
            raise RuntimeError(
                "This object has no bot associated with it. Shortcuts cannot be used."
            )
        return self._bot

    def set_bot(self, bot: Optional["Bot"]) -> None:
        """Sets the :class:`telegram.Bot` instance associated with this object.

        .. seealso:: :meth:`get_bot`

        .. versionadded: 20.0

        Arguments:
            bot (:class:`telegram.Bot` | :obj:`None`): The bot instance.
        """
        self._bot = bot

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            if not self._id_attrs:
                warn(
                    f"Objects of type {self.__class__.__name__} can not be meaningfully tested for"
                    " equivalence.",
                    stacklevel=2,
                )
            if not other._id_attrs:
                warn(
                    f"Objects of type {other.__class__.__name__} can not be meaningfully tested"
                    " for equivalence.",
                    stacklevel=2,
                )
            return self._id_attrs == other._id_attrs
        return super().__eq__(other)

    def __hash__(self) -> int:
        if self._id_attrs:
            return hash((self.__class__, self._id_attrs))
        return super().__hash__()
