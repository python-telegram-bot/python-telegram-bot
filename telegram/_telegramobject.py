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
import inspect
import json
from collections.abc import Sized
from copy import deepcopy
from itertools import chain
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

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

        * ``telegram_object['from']`` will look up the key ``from_user``. This is to account for
          special cases like :attr:`Message.from_user` that deviate from the official Bot API.
        * Removed argument and attribute ``bot`` for several subclasses. Use
          :meth:`set_bot` and :meth:`get_bot` instead.
        * Removed the possibility to pass arbitrary keyword arguments for several subclasses.
        * String representations objects of this type was overhauled. See :meth:`__repr__` for
          details. As this class doesn't implement :meth:`object.__str__`, the default
          implementation will be used, which is equivalent to :meth:`__repr__`.

    Arguments:
        api_kwargs (Dict[:obj:`str`, any], optional): |toapikwargsarg|

            .. versionadded:: 20.0

    Attributes:
        api_kwargs (:obj:`types.MappingProxyType` [:obj:`str`, any]): |toapikwargsattr|

            .. versionadded:: 20.0

    """

    __slots__ = ("_id_attrs", "_bot", "_frozen", "api_kwargs")

    # Used to cache the names of the parameters of the __init__ method of the class
    # Must be a private attribute to avoid name clashes between subclasses
    __INIT_PARAMS: Set[str] = set()
    # Used to check if __INIT_PARAMS has been set for the current class. Unfortunately, we can't
    # just check if `__INIT_PARAMS is None`, since subclasses use the parent class' __INIT_PARAMS
    # unless it's overridden
    __INIT_PARAMS_CHECK: Optional[Type["TelegramObject"]] = None

    def __init__(self, *, api_kwargs: JSONDict = None) -> None:
        self._frozen: bool = False
        self._id_attrs: Tuple[object, ...] = ()
        self._bot: Optional["Bot"] = None
        # We don't do anything with api_kwargs here - see docstring of _apply_api_kwargs
        self.api_kwargs: Mapping[str, Any] = MappingProxyType(api_kwargs or {})

    def _freeze(self) -> None:
        self._frozen = True

    def _unfreeze(self) -> None:
        self._frozen = False

    def _apply_api_kwargs(self, api_kwargs: JSONDict) -> None:
        """Loops through the api kwargs and for every key that exists as attribute of the
        object (and is None), it moves the value from `api_kwargs` to the attribute.
        *Edits `api_kwargs` in pace!*

        This method is currently only called in the unpickling process, i.e. not on "normal" init.
        This is because
        * automating this is tricky to get right: It should be called at the *end* of the __init__,
          preferably only once at the end of the __init__ of the last child class. This could be
          done via __init_subclass__, but it's hard to not destroy the signature of __init__ in the
          process.
        * calling it manually in every __init__ is tedious
        * There probably is no use case for it anyway. If you manually initialize a TO subclass,
          then you can pass everything as proper argument.
        """
        # we convert to list to ensure that the list doesn't change length while we loop
        for key in list(api_kwargs.keys()):
            if getattr(self, key, True) is None:
                setattr(self, key, api_kwargs.pop(key))

    def __setattr__(self, key: str, value: object) -> None:
        # protected attributes can always be set for convenient internal use
        if (key == "_frozen") or (not getattr(self, "_frozen", True)) or key.startswith("_"):
            super().__setattr__(key, value)
            return

        raise AttributeError(
            f"Attribute `{key}` of class `{self.__class__.__name__}` can't be set!"
        )

    def __delattr__(self, key: str) -> None:
        # protected attributes can always be set for convenient internal use
        if (key == "_frozen") or (not getattr(self, "_frozen", True)) or key.startswith("_"):
            super().__delattr__(key)
            return

        raise AttributeError(
            f"Attribute `{key}` of class `{self.__class__.__name__}` can't be deleted!"
        )

    def __repr__(self) -> str:
        """Gives a string representation of this object in the form
        ``ClassName(attr_1=value_1, attr_2=value_2, ...)``, where attributes are omitted if they
        have the value :obj:`None` or empty instances of :class:`collections.abc.Sized` (e.g.
        :class:`list`, :class:`dict`, :class:`set`, :class:`str`, etc.).

        As this class doesn't implement :meth:`object.__str__`, the default implementation
        will be used, which is equivalent to :meth:`__repr__`.

        Returns:
            :obj:`str`
        """
        # * `__repr__` goal is to be unambiguous
        # * `__str__` goal is to be readable
        # * `str()` calls `__repr__`, if `__str__` is not defined
        # In our case "unambiguous" and "readable" largely coincide, so we can use the same logic.
        as_dict = self._get_attrs(recursive=False, include_private=False)

        if not self.api_kwargs:
            # Drop api_kwargs from the representation, if empty
            as_dict.pop("api_kwargs", None)

        contents = ", ".join(
            f"{k}={as_dict[k]!r}"
            for k in sorted(as_dict.keys())
            if (
                as_dict[k] is not None
                and not (
                    isinstance(as_dict[k], Sized)
                    and len(as_dict[k]) == 0  # type: ignore[arg-type]
                )
            )
        )
        return f"{self.__class__.__name__}({contents})"

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
        out = self._get_attrs(include_private=True, recursive=False, remove_bot=True)
        # MappingProxyType is not pickable, so we convert it to a dict and revert in
        # __setstate__
        out["api_kwargs"] = dict(self.api_kwargs)
        return out

    def __setstate__(self, state: dict) -> None:
        """
        This method is used for unpickling. The data, which is in the form a dictionary, is
        converted back into a class. Should be modified in place.
        """
        self._unfreeze()

        # Make sure that we have a `_bot` attribute. This is necessary, since __getstate__ omits
        # this as Bots are not pickable.
        setattr(self, "_bot", None)

        for key, val in state.items():
            if key == "_frozen":
                # Setting the frozen status to True would prevent the attributes from being set
                continue
            if key == "api_kwargs":
                # See below
                continue
            setattr(self, key, val)

        # For api_kwargs we first apply any kwargs that are already attributes of the object
        # and then set the rest as MappingProxyType attribute. Converting to MappingProxyType
        # is necessary, since __getstate__ converts it to a dict as MPT is not pickable.
        api_kwargs = state["api_kwargs"]
        self._apply_api_kwargs(api_kwargs)
        setattr(self, "api_kwargs", MappingProxyType(api_kwargs))

        # Apply freezing if necessary
        if state["_frozen"]:
            self._freeze()

    def __deepcopy__(self: Tele_co, memodict: dict) -> Tele_co:
        """This method deepcopies the object and sets the bot on the newly created copy."""
        bot = self._bot  # Save bot so we can set it after copying
        self.set_bot(None)  # set to None so it is not deepcopied
        cls = self.__class__
        result = cls.__new__(cls)  # create a new instance
        memodict[id(self)] = result  # save the id of the object in the dict

        attrs = self._get_attrs(include_private=True)  # get all its attributes
        setattr(result, "_frozen", False)  # unfreeze the new object for setting the attributes

        for k in attrs:  # now we set the attributes in the deepcopied object
            if k == "_frozen":
                # Setting the frozen status to True would prevent the attributes from being set
                continue
            if k == "api_kwargs":
                # Need to copy api_kwargs manually, since it's a MappingProxyType is not
                # pickable and deepcopy uses the pickle interface
                setattr(result, k, MappingProxyType(deepcopy(dict(self.api_kwargs), memodict)))
                continue

            setattr(result, k, deepcopy(getattr(self, k), memodict))

        # Apply freezing if necessary
        if self._frozen:
            result._freeze()

        result.set_bot(bot)  # Assign the bots back
        self.set_bot(bot)
        return result

    def _get_attrs(
        self,
        include_private: bool = False,
        recursive: bool = False,
        remove_bot: bool = False,
    ) -> Dict[str, Union[str, object]]:
        """This method is used for obtaining the attributes of the object.

        Args:
            include_private (:obj:`bool`): Whether the result should include private variables.
            recursive (:obj:`bool`): If :obj:`True`, will convert any ``TelegramObjects`` (if
                found) in the attributes to a dictionary. Else, preserves it as an object itself.
            remove_bot (:obj:`bool`): Whether the bot should be included in the result.

        Returns:
            :obj:`dict`: A dict where the keys are attribute names and values are their values.
        """
        data = {}

        # We want to get all attributes for the class, using self.__slots__ only includes the
        # attributes used by that class itself, and not its superclass(es). Hence, we get its MRO
        # and then get their attributes. The `[:-1]` slice excludes the `object` class
        all_slots = (s for c in self.__class__.__mro__[:-1] for s in c.__slots__)  # type: ignore
        # chain the class's slots with the user defined subclass __dict__ (class has no slots)
        for key in chain(self.__dict__, all_slots) if hasattr(self, "__dict__") else all_slots:
            if not include_private and key.startswith("_"):
                continue

            value = getattr(self, key, None)
            if value is not None:
                if recursive and hasattr(value, "to_dict"):
                    data[key] = value.to_dict(recursive=True)  # pylint: disable=no-member
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
        """Should be called by subclasses that override de_json to ensure that the input
        is not altered. Whoever calls de_json might still want to use the original input
        for something else.
        """
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
        return cls._de_json(data=data, bot=bot)

    @classmethod
    def _de_json(
        cls: Type[Tele_co], data: Optional[JSONDict], bot: "Bot", api_kwargs: JSONDict = None
    ) -> Optional[Tele_co]:
        if data is None:
            return None

        # try-except is significantly faster in case we already have a correct argument set
        try:
            obj = cls(**data, api_kwargs=api_kwargs)
        except TypeError as exc:
            if "__init__() got an unexpected keyword argument" not in str(exc):
                raise exc

            if cls.__INIT_PARAMS_CHECK is not cls:
                signature = inspect.signature(cls)
                cls.__INIT_PARAMS = set(signature.parameters.keys())
                cls.__INIT_PARAMS_CHECK = cls

            api_kwargs = api_kwargs or {}
            existing_kwargs: JSONDict = {}
            for key, value in data.items():
                (existing_kwargs if key in cls.__INIT_PARAMS else api_kwargs)[key] = value

            obj = cls(api_kwargs=api_kwargs, **existing_kwargs)

        obj.set_bot(bot=bot)
        return obj

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

        .. versionchanged:: 20.0
            Now includes all entries of :attr:`api_kwargs`.

        Returns:
            :obj:`str`
        """
        return json.dumps(self.to_dict())

    def to_dict(self, recursive: bool = True) -> JSONDict:
        """Gives representation of object as :obj:`dict`.

        .. versionchanged:: 20.0
            Now includes all entries of :attr:`api_kwargs`.

        Args:
            recursive (:obj:`bool`, optional): If :obj:`True`, will convert any TelegramObjects
                (if found) in the attributes to a dictionary. Else, preserves it as an object
                itself. Defaults to :obj:`True`.

                .. versionadded:: 20.0

        Returns:
            :obj:`dict`
        """
        out = self._get_attrs(recursive=recursive)
        out.update(out.pop("api_kwargs", {}))  # type: ignore[call-overload]
        return out

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
