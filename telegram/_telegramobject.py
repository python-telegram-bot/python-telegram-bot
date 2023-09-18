#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
import datetime
import inspect
import json
from collections.abc import Sized
from contextlib import contextmanager
from copy import deepcopy
from itertools import chain
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from telegram._utils.datetime import to_timestamp
from telegram._utils.types import JSONDict
from telegram._utils.warnings import warn

if TYPE_CHECKING:
    from telegram import Bot

Tele_co = TypeVar("Tele_co", bound="TelegramObject", covariant=True)


class TelegramObject:
    """Base class for most Telegram objects.

    Objects of this type are subscriptable with strings. See :meth:`__getitem__` for more details.
    The :mod:`pickle` and :func:`~copy.deepcopy` behavior of objects of this type are defined by
    :meth:`__getstate__`, :meth:`__setstate__` and :meth:`__deepcopy__`.

    Tip:
        Objects of this type can be serialized via Python's :mod:`pickle` module and pickled
        objects from one version of PTB are usually loadable in future versions. However, we can
        not guarantee that this compatibility will always be provided. At least a manual one-time
        conversion of the data may be needed on major updates of the library.

    .. versionchanged:: 20.0

        * Removed argument and attribute ``bot`` for several subclasses. Use
          :meth:`set_bot` and :meth:`get_bot` instead.
        * Removed the possibility to pass arbitrary keyword arguments for several subclasses.
        * String representations objects of this type was overhauled. See :meth:`__repr__` for
          details. As this class doesn't implement :meth:`object.__str__`, the default
          implementation will be used, which is equivalent to :meth:`__repr__`.
        * Objects of this class (or subclasses) are now immutable. This means that you can't set
          or delete attributes anymore. Moreover, attributes that were formerly of type
          :obj:`list` are now of type :obj:`tuple`.

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
    __INIT_PARAMS: ClassVar[Set[str]] = set()
    # Used to check if __INIT_PARAMS has been set for the current class. Unfortunately, we can't
    # just check if `__INIT_PARAMS is None`, since subclasses use the parent class' __INIT_PARAMS
    # unless it's overridden
    __INIT_PARAMS_CHECK: Optional[Type["TelegramObject"]] = None

    def __init__(self, *, api_kwargs: Optional[JSONDict] = None) -> None:
        # Setting _frozen to `False` here means that classes without arguments still need to
        # implement __init__. However, with `True` would mean increased usage of
        # `with self._unfrozen()` in the `__init__` of subclasses and we have fewer empty
        # classes than classes with arguments.
        self._frozen: bool = False
        self._id_attrs: Tuple[object, ...] = ()
        self._bot: Optional[Bot] = None
        # We don't do anything with api_kwargs here - see docstring of _apply_api_kwargs
        self.api_kwargs: Mapping[str, Any] = MappingProxyType(api_kwargs or {})

    def __eq__(self, other: object) -> bool:
        """Compares this object with :paramref:`other` in terms of equality.
        If this object and :paramref:`other` are `not` objects of the same class,
        this comparison will fall back to Python's default implementation of :meth:`object.__eq__`.
        Otherwise, both objects may be compared in terms of equality, if the corresponding
        subclass of :class:`TelegramObject` has defined a set of attributes to compare and
        the objects are considered to be equal, if all of these attributes are equal.
        If the subclass has not defined a set of attributes to compare, a warning will be issued.

        Tip:
            If instances of a class in the :mod:`telegram` module are comparable in terms of
            equality, the documentation of the class will state the attributes that will be used
            for this comparison.

        Args:
            other (:obj:`object`): The object to compare with.

        Returns:
            :obj:`bool`

        """
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
        """Builds a hash value for this object such that the hash of two objects is equal if and
        only if the objects are equal in terms of :meth:`__eq__`.

        Returns:
            :obj:`int`
        """
        if self._id_attrs:
            return hash((self.__class__, self._id_attrs))
        return super().__hash__()

    def __setattr__(self, key: str, value: object) -> None:
        """Overrides :meth:`object.__setattr__` to prevent the overriding of attributes.

        Raises:
            :exc:`AttributeError`
        """
        # protected attributes can always be set for convenient internal use
        if key[0] == "_" or not getattr(self, "_frozen", True):
            super().__setattr__(key, value)
            return

        raise AttributeError(
            f"Attribute `{key}` of class `{self.__class__.__name__}` can't be set!"
        )

    def __delattr__(self, key: str) -> None:
        """Overrides :meth:`object.__delattr__` to prevent the deletion of attributes.

        Raises:
            :exc:`AttributeError`
        """
        # protected attributes can always be set for convenient internal use
        if key[0] == "_" or not getattr(self, "_frozen", True):
            super().__delattr__(key)
            return

        raise AttributeError(
            f"Attribute `{key}` of class `{self.__class__.__name__}` can't be deleted!"
        )

    def __repr__(self) -> str:
        """Gives a string representation of this object in the form
        ``ClassName(attr_1=value_1, attr_2=value_2, ...)``, where attributes are omitted if they
        have the value :obj:`None` or are empty instances of :class:`collections.abc.Sized` (e.g.
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
        else:
            # Otherwise, we want to skip the "mappingproxy" part of the repr
            as_dict["api_kwargs"] = dict(self.api_kwargs)

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
        """
        Objects of this type are subscriptable with strings, where
        ``telegram_object["attribute_name"]`` is equivalent to ``telegram_object.attribute_name``.

        Tip:
            This is useful for dynamic attribute lookup, i.e. ``telegram_object[arg]`` where the
            value of ``arg`` is determined at runtime.
            In all other cases, it's recommended to use the dot notation instead, i.e.
            ``telegram_object.attribute_name``.

        .. versionchanged:: 20.0

            ``telegram_object['from']`` will look up the key ``from_user``. This is to account for
            special cases like :attr:`Message.from_user` that deviate from the official Bot API.

        Args:
            item (:obj:`str`): The name of the attribute to look up.

        Returns:
            :obj:`object`

        Raises:
            :exc:`KeyError`: If the object does not have an attribute with the appropriate name.
        """
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
        Overrides :meth:`object.__getstate__` to customize the pickling process of objects of this
        type.
        The returned state does `not` contain the :class:`telegram.Bot` instance set with
        :meth:`set_bot` (if any), as it can't be pickled.

        Returns:
            state (Dict[:obj:`str`, :obj:`object`]): The state of the object.
        """
        out = self._get_attrs(include_private=True, recursive=False, remove_bot=True)
        # MappingProxyType is not pickable, so we convert it to a dict and revert in
        # __setstate__
        out["api_kwargs"] = dict(self.api_kwargs)
        return out

    def __setstate__(self, state: Dict[str, object]) -> None:
        """
        Overrides :meth:`object.__setstate__` to customize the unpickling process of objects of
        this type. Modifies the object in-place.

        If any data was stored in the :attr:`api_kwargs` of the pickled object, this method checks
        if the class now has dedicated attributes for those keys and moves the values from
        :attr:`api_kwargs` to the dedicated attributes.
        This can happen, if serialized data is loaded with a new version of this library, where
        the new version was updated to account for updates of the Telegram Bot API.

        If on the contrary an attribute was removed from the class, the value is not discarded but
        made available via :attr:`api_kwargs`.

        Args:
            state (:obj:`dict`): The data to set as attributes of this object.
        """
        self._unfreeze()

        # Make sure that we have a `_bot` attribute. This is necessary, since __getstate__ omits
        # this as Bots are not pickable.
        self._bot = None

        # get api_kwargs first because we may need to add entries to it (see try-except below)
        api_kwargs = cast(Dict[str, object], state.pop("api_kwargs", {}))
        # get _frozen before the loop to avoid setting it to True in the loop
        frozen = state.pop("_frozen", False)

        for key, val in state.items():
            try:
                setattr(self, key, val)
            except AttributeError:
                # catch cases when old attributes are removed from new versions
                api_kwargs[key] = val  # add it to api_kwargs as fallback

        # For api_kwargs we first apply any kwargs that are already attributes of the object
        # and then set the rest as MappingProxyType attribute. Converting to MappingProxyType
        # is necessary, since __getstate__ converts it to a dict as MPT is not pickable.
        self._apply_api_kwargs(api_kwargs)
        self.api_kwargs = MappingProxyType(api_kwargs)

        # Apply freezing if necessary
        # we .get(…) the setting for backwards compatibility with objects that were pickled
        # before the freeze feature was introduced
        if frozen:
            self._freeze()

    def __deepcopy__(self: Tele_co, memodict: Dict[int, object]) -> Tele_co:
        """
        Customizes how :func:`copy.deepcopy` processes objects of this type.
        The only difference to the default implementation is that the :class:`telegram.Bot`
        instance set via :meth:`set_bot` (if any) is not copied, but shared between the original
        and the copy, i.e.::

            assert telegram_object.get_bot() is copy.deepcopy(telegram_object).get_bot()

        Args:
            memodict (:obj:`dict`): A dictionary that maps objects to their copies.

        Returns:
            :obj:`telegram.TelegramObject`: The copied object.
        """
        bot = self._bot  # Save bot so we can set it after copying
        self.set_bot(None)  # set to None so it is not deepcopied
        cls = self.__class__
        result = cls.__new__(cls)  # create a new instance
        memodict[id(self)] = result  # save the id of the object in the dict

        result._frozen = False  # unfreeze the new object for setting the attributes

        # now we set the attributes in the deepcopied object
        for k in self._get_attrs_names(include_private=True):
            if k == "_frozen":
                # Setting the frozen status to True would prevent the attributes from being set
                continue
            if k == "api_kwargs":
                # Need to copy api_kwargs manually, since it's a MappingProxyType is not
                # pickable and deepcopy uses the pickle interface
                setattr(result, k, MappingProxyType(deepcopy(dict(self.api_kwargs), memodict)))
                continue

            try:
                setattr(result, k, deepcopy(getattr(self, k), memodict))
            except AttributeError:
                # Skip missing attributes. This can happen if the object was loaded from a pickle
                # file that was created with an older version of the library, where the class
                # did not have the attribute yet.
                continue

        # Apply freezing if necessary
        if self._frozen:
            result._freeze()

        result.set_bot(bot)  # Assign the bots back
        self.set_bot(bot)
        return result

    @staticmethod
    def _parse_data(data: Optional[JSONDict]) -> Optional[JSONDict]:
        """Should be called by subclasses that override de_json to ensure that the input
        is not altered. Whoever calls de_json might still want to use the original input
        for something else.
        """
        return None if data is None else data.copy()

    @classmethod
    def _de_json(
        cls: Type[Tele_co],
        data: Optional[JSONDict],
        bot: "Bot",
        api_kwargs: Optional[JSONDict] = None,
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
    def de_list(
        cls: Type[Tele_co], data: Optional[List[JSONDict]], bot: "Bot"
    ) -> Tuple[Tele_co, ...]:
        """Converts a list of JSON objects to a tuple of Telegram objects.

        .. versionchanged:: 20.0

           * Returns a tuple instead of a list.
           * Filters out any :obj:`None` values.

        Args:
            data (List[Dict[:obj:`str`, ...]]): The JSON data.
            bot (:class:`telegram.Bot`): The bot associated with these objects.

        Returns:
            A tuple of Telegram objects.

        """
        if not data:
            return ()

        return tuple(obj for obj in (cls.de_json(d, bot) for d in data) if obj is not None)

    @contextmanager
    def _unfrozen(self: Tele_co) -> Iterator[Tele_co]:
        """Context manager to temporarily unfreeze the object. For internal use only.

        Note:
            with to._unfrozen() as other_to:
                assert to is other_to
        """
        self._unfreeze()
        yield self
        self._freeze()

    def _freeze(self) -> None:
        self._frozen = True

    def _unfreeze(self) -> None:
        self._frozen = False

    def _apply_api_kwargs(self, api_kwargs: JSONDict) -> None:
        """Loops through the api kwargs and for every key that exists as attribute of the
        object (and is None), it moves the value from `api_kwargs` to the attribute.
        *Edits `api_kwargs` in place!*

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

    def _get_attrs_names(self, include_private: bool) -> Iterator[str]:
        """
        Returns the names of the attributes of this object. This is used to determine which
        attributes should be serialized when pickling the object.

        Args:
            include_private (:obj:`bool`): Whether to include private attributes.

        Returns:
            Iterator[:obj:`str`]: An iterator over the names of the attributes of this object.
        """
        # We want to get all attributes for the class, using self.__slots__ only includes the
        # attributes used by that class itself, and not its superclass(es). Hence, we get its MRO
        # and then get their attributes. The `[:-1]` slice excludes the `object` class
        all_slots = (s for c in self.__class__.__mro__[:-1] for s in c.__slots__)  # type: ignore
        # chain the class's slots with the user defined subclass __dict__ (class has no slots)
        all_attrs = (
            chain(all_slots, self.__dict__.keys()) if hasattr(self, "__dict__") else all_slots
        )

        if include_private:
            return all_attrs
        return (attr for attr in all_attrs if not attr.startswith("_"))

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

        for key in self._get_attrs_names(include_private=include_private):
            value = getattr(self, key, None)
            if value is not None:
                if recursive and hasattr(value, "to_dict"):
                    data[key] = value.to_dict(recursive=True)
                else:
                    data[key] = value
            elif not recursive:
                data[key] = value

        if recursive and data.get("from_user"):
            data["from"] = data.pop("from_user", None)
        if remove_bot:
            data.pop("_bot", None)
        return data

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

            * Now includes all entries of :attr:`api_kwargs`.
            * Attributes whose values are empty sequences are no longer included.

        Args:
            recursive (:obj:`bool`, optional): If :obj:`True`, will convert any TelegramObjects
                (if found) in the attributes to a dictionary. Else, preserves it as an object
                itself. Defaults to :obj:`True`.

                .. versionadded:: 20.0

        Returns:
            :obj:`dict`
        """
        out = self._get_attrs(recursive=recursive)

        # Now we should convert TGObjects to dicts inside objects such as sequences, and convert
        # datetimes to timestamps. This mostly eliminates the need for subclasses to override
        # `to_dict`
        pop_keys: Set[str] = set()
        for key, value in out.items():
            if isinstance(value, (tuple, list)):
                if not value:
                    # not popping directly to avoid changing the dict size during iteration
                    pop_keys.add(key)
                    continue

                val = []  # empty list to append our converted values to
                for item in value:
                    if hasattr(item, "to_dict"):
                        val.append(item.to_dict(recursive=recursive))
                    # This branch is useful for e.g. Tuple[Tuple[PhotoSize|KeyboardButton]]
                    elif isinstance(item, (tuple, list)):
                        val.append(
                            [
                                i.to_dict(recursive=recursive) if hasattr(i, "to_dict") else i
                                for i in item
                            ]
                        )
                    else:  # if it's not a TGObject, just append it. E.g. [TGObject, 2]
                        val.append(item)
                out[key] = val

            elif isinstance(value, datetime.datetime):
                out[key] = to_timestamp(value)

        for key in pop_keys:
            out.pop(key)

        # Effectively "unpack" api_kwargs into `out`:
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
