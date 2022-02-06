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
"""This module contains subclasses of :class:`collections.defaultdict` that keeps track of the
keys that where accessed.

.. versionadded:: 14.0

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
from typing import (
    TypeVar,
    DefaultDict,
    Callable,
    Set,
    ClassVar,
    Iterator,
    Optional,
    Union,
    Tuple,
    overload,
    MutableMapping,
    List,
    Mapping,
)
from collections import defaultdict

from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue

_VT = TypeVar('_VT')
_KT = TypeVar('_KT')
_T = TypeVar('_T')


# TODO: Implement tests for this class that cover all methods implemented by (Mutable)Mapping and
#   check if they give the correct behavior in terms of keeping track on the access. This includes
#   __eq__ & access through Key/ItemViews
#   We should also test that all this behavior stays the same when accessing the mapping through
#   a MappingProxyType
#   For methods like `pop`, `get`, `setdefault`, we should also check that we have the same
#   behavior as defaultdict


class TrackingDefaultDict(MutableMapping[_KT, _VT]):
    """DefaultDict that keeps track of which keys where accessed.

    Note:
        * ``key in tdd`` is not considered reading
        * ``setdefault()`` is considered both reading and writing depending on
           whether or not the key is present
        * ``pop`` is only considered writing, since the value is deleted instead of being changed

    Args:
        default_factory (Callable): Default factory for missing entries
        track_read (:obj:`bool`): Whether read access should be tracked. Deleting entries is
            not considered reading.
        track_write (:obj:`bool`): Whether write access should be tracked. Deleting entries is
            considered writing.
    """

    DELETED: ClassVar = object()
    """Special marker indicating that an entry was deleted."""

    __slots__ = ('_data', '_write_access_keys', '_read_access_keys', 'track_read', 'track_write')

    def __init__(self, default_factory: Callable[[], _VT], track_read: bool, track_write: bool):
        # The default_factory argument for defaultdict is positional only!
        self._data: DefaultDict[_KT, _VT] = defaultdict(default_factory)
        self.track_read = track_read
        self.track_write = track_write
        self._write_access_keys: Set[_KT] = set()
        self._read_access_keys: Set[_KT] = set()

    def __track_read(self, key: Union[_KT, Set[_KT]]) -> None:
        if self.track_read:
            if isinstance(key, set):
                self._read_access_keys |= key
            else:
                self._read_access_keys.add(key)

    def __track_write(self, key: Union[_KT, Set[_KT]]) -> None:
        if self.track_write:
            if isinstance(key, set):
                self._write_access_keys |= key
            else:
                self._write_access_keys.add(key)

    def __repr__(self) -> str:
        return repr(self._data)

    def __str__(self) -> str:
        return str(self._data)

    def __eq__(self, other: object) -> bool:
        return other == self._data

    def pop_accessed_read_keys(self) -> Set[_KT]:
        """Returns all keys that were read-accessed since the last time this method was called."""
        if not self.track_read:
            raise RuntimeError('Not tracking read access!')

        out = self._read_access_keys
        self._read_access_keys = set()
        return out

    def pop_accessed_write_keys(self) -> Set[_KT]:
        """Returns all keys that were write-accessed since the last time this method was called."""
        if not self.track_write:
            raise RuntimeError('Not tracking write access!')

        out = self._write_access_keys
        self._write_access_keys = set()
        return out

    def pop_accessed_read_items(self) -> List[Tuple[_KT, _VT]]:
        """
        Returns all keys & corresponding values as set of tuples that were read-accessed since
        the last time this method was called.
        """
        keys = self.pop_accessed_read_keys()
        return [(key, self._data[key]) for key in keys]

    def pop_accessed_write_items(self) -> List[Tuple[_KT, _VT]]:
        """
        Returns all keys & corresponding values as set of tuples that were write-accessed since
        the last time this method was called. If a key was deleted, the value will be
        :attr:`DELETED`.
        """
        keys = self.pop_accessed_write_keys()
        return [(key, self._data[key] if key in self._data else self.DELETED) for key in keys]

    # Implement abstract interface

    def __getitem__(self, key: _KT) -> _VT:
        item = self._data[key]
        self.__track_read(key)
        return item

    def __setitem__(self, key: _KT, value: _VT) -> None:
        self._data[key] = value
        self.__track_write(key)

    def __delitem__(self, key: _KT) -> None:
        del self._data[key]
        self.__track_write(key)

    def __iter__(self) -> Iterator[_KT]:
        for key in self._data:
            self.__track_read(key)
            yield key

    def __len__(self) -> int:
        return len(self._data)

    def update_no_track(self, mapping: Mapping[_KT, _VT]) -> None:
        return self._data.update(mapping)

    # Override some methods so that they fit better with the read/write access book keeping

    def __contains__(self, key: object) -> bool:
        return key in self._data

    # Mypy seems a bit inconsistent about what it wants as types for `default` and return value
    # so we just ignore a bit
    def pop(  # type: ignore[override]
        self, key: _KT, default: _VT = DEFAULT_NONE  # type: ignore[assignment]
    ) -> _VT:
        self.__track_write(key)
        if isinstance(default, DefaultValue):
            return self._data.pop(key)
        return self._data.pop(key, default=default)

    def clear(self) -> None:
        self.__track_write(set(self._data.keys()))
        self._data.clear()

    # Mypy seems a bit inconsistent about what it wants as types for `default` and return value
    # so we just ignore a bit
    def setdefault(self: 'TrackingDefaultDict[_KT, _T]', key: _KT, default: _T = None) -> _T:
        if key in self._data:
            self.__track_read(key)
            return self._data[key]

        self.__track_write(key)
        self._data[key] = default  # type: ignore[assignment]
        return default  # type: ignore[return-value]

    # Overriding to comply with the behavior of `defaultdict`

    @overload
    def get(self, key: _KT) -> Optional[_VT]:  # pylint: disable=arguments-differ
        ...

    @overload
    def get(self, key: _KT, default: _T) -> _T:  # pylint: disable=signature-differs
        ...

    def get(self, key: _KT, default: _T = None) -> Optional[Union[_VT, _T]]:
        if key in self:
            return self[key]
        return default
