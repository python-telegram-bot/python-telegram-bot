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
"""This module contains the CallbackDataCache class."""
import logging
import time
from datetime import datetime
from collections import deque
from threading import Lock
from typing import Dict, Deque, Any, Tuple, Union, List
from uuid import uuid4

from telegram.utils.helpers import to_float_timestamp


class CallbackDataCache:
    """A custom LRU cache implementation for storing the callback data of a
     :class:`telegram.ext.Bot.`

    Warning:
        Not limiting :attr:`maxsize` may cause memory issues for long running bots. If you don't
        limit the size, you should be sure that every inline button is actually pressed or that
        you manually clear the cache using e.g. :meth:`clear`.

    Args:
        maxsize (:obj:`int`, optional): Maximum size of the cache. Pass :obj:`None` or 0 for
            unlimited size. Defaults to 1024.
        data (Dict[:obj:`str`, Tuple[:obj:`float`, :obj:`Any`], optional): Cached objects to
            initialize the cache with. For each unique identifier, the corresponding value must
            be a tuple containing the timestamp the object was stored at and the actual object.
            Must be consistent with the input for :attr:`queue`.
        queue (Deque[:obj:`str`], optional): Doubly linked list containing unique object
            identifiers to initialize the cache with. Should be in LRU order (left-to-right). Must
            be consistent with the input for :attr:`data`.

    Attributes:
        maxsize (:obj:`int` | :obj:`None`): maximum size of the cache. :obj:`None` or 0 mean
            unlimited size.

    """

    def __init__(
        self,
        maxsize: int = 1024,
        data: Dict[str, Tuple[float, Any]] = None,
        queue: Deque[str] = None,
    ):
        self.logger = logging.getLogger(__name__)

        if (data is None and queue is not None) or (data is not None and queue is None):
            raise ValueError('You must either pass both of data and queue or neither.')

        self.maxsize = maxsize
        self._data: Dict[str, Tuple[float, Any]] = data or {}
        # We set size to unlimited b/c we take of that manually
        # IMPORTANT: We always append left and pop right, if necessary
        self._deque: Deque[str] = queue or deque(maxlen=None)

        self.__lock = Lock()

    @property
    def persistence_data(self) -> Tuple[Dict[str, Tuple[float, Any]], Deque[str]]:
        """
        The data that needs to be persistence to allow caching callback data across bot reboots.

        Returns:
             Tuple[Dict[:obj:`str`, Tuple[:obj:`float`, :obj:`Any`]], Deque[:obj:`str`]]: The
                internal data as expected by
                :meth:`telegram.ext.BasePersistence.update_callback_data`.
        """
        with self.__lock:
            return self._data, self._deque

    @property
    def full(self) -> bool:
        """
        Whether the cache is full or not.
        """
        with self.__lock:
            return self.__full

    @property
    def __full(self) -> bool:
        if not self.maxsize:
            return False
        return len(self._deque) >= self.maxsize

    def put(self, obj: Any) -> str:
        """
        Puts the passed in the cache and returns a unique identifier that can be used to retrieve
        it later.

        Args:
            obj (:obj:`any`): The object to put.

        Returns:
            :obj:`str`: Unique identifier for the object.
        """
        with self.__lock:
            return self.__put(obj)

    def __put(self, obj: Any) -> str:
        if self.__full:
            remove = self._deque.pop()
            self._data.pop(remove)
            self.logger.debug('CallbackDataCache full. Dropping item %s', remove)

        uuid = str(uuid4())
        self._deque.appendleft(uuid)
        self._data[uuid] = (time.time(), obj)
        return uuid

    def pop(self, uuid: str) -> Any:
        """
        Retrieves the object identified by :attr:`uuid` and removes it from the cache.

        Args:
            uuid (:obj:`str`): Unique identifier for the object as returned by :meth:`put`.

        Returns:
            :obj:`any`: The object.

        Raises:
            IndexError: If the object can not be found.

        """
        with self.__lock:
            return self.__pop(uuid)

    def __pop(self, uuid: str) -> Any:
        try:
            obj = self._data.pop(uuid)[1]
        except KeyError as exc:
            raise IndexError(f'UUID {uuid} could not be found.') from exc

        self._deque.remove(uuid)
        return obj

    def clear(self, time_cutoff: Union[float, datetime] = None) -> List[Tuple[str, Any]]:
        """
        Clears the cache.

        Args:
            time_cutoff (:obj:`float` | :obj:`datetime.datetime`, optional): Pass a UNIX timestamp
                or a :obj:`datetime.datetime` to clear only entries which are older. Naive
                :obj:`datetime.datetime` objects will be assumed to be in UTC.

        Returns:
            List[Tuple[:obj:`str`, :obj:`any`]]: A list of tuples ``(uuid, obj)`` of the cleared
                objects and their identifiers. May be empty.

        """
        with self.__lock:
            if not time_cutoff:
                out = [(uuid, tpl[1]) for uuid, tpl in self._data.items()]
                self._data.clear()
                self._deque.clear()
                return out

            if isinstance(time_cutoff, datetime):
                effective_cutoff = to_float_timestamp(time_cutoff)
            else:
                effective_cutoff = time_cutoff

            out = [(uuid, tpl[1]) for uuid, tpl in self._data.items() if tpl[0] < effective_cutoff]
            for uuid, _ in out:
                self.__pop(uuid)

            return out
