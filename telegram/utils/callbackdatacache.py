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
from threading import Lock
from typing import Dict, Any, Tuple, Union, List, Optional, Iterator
from uuid import uuid4

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.utils.helpers import to_float_timestamp
from telegram.utils.types import CDCData


class Node:
    __slots__ = ('successor', 'predecessor', 'keyboard_uuid', 'button_uuids', 'access_time')

    def __init__(
        self,
        keyboard_uuid: str,
        button_uuids: List[str],
        access_time: float,
        predecessor: 'Node' = None,
        successor: 'Node' = None,
    ):
        self.predecessor = predecessor
        self.successor = successor
        self.keyboard_uuid = keyboard_uuid
        self.button_uuids = button_uuids
        self.access_time = access_time or time.time()


class CallbackDataCache:
    """A customized LRU cache implementation for storing the callback data of a
     :class:`telegram.ext.Bot.`

    Warning:
        Not limiting :attr:`maxsize` may cause memory issues for long running bots. If you don't
        limit the size, you should be sure that every inline button is actually pressed or that
        you manually clear the cache using e.g. :meth:`clear`.

    Args:
        maxsize (:obj:`int`, optional): Maximum number of keyboards of the cache. Pass :obj:`None`
            or 0 for unlimited size. Defaults to 1024.
        button_data (Dict[:obj:`str`, :obj:`Any`, optional): Cached objects to initialize the cache
            with. Must be consistent with the input for :attr:`lru_list`.
        lru_list (List[Tuple[:obj:`str`, List[:obj:`str`], :obj:`float`]], optional):
            Representation of the cached keyboard. Each entry must be a tuple of

            * The unique identifier of the keyboard
            * A list of the unique identifiers of the buttons contained in the keyboard
            * the timestamp the keyboard was used last at

            Must be sorted by the timestamp and must be consistent with :attr:`button_data`.

    Attributes:
        maxsize (:obj:`int` | :obj:`None`): maximum size of the cache. :obj:`None` or 0 mean
            unlimited size.

    """

    def __init__(
        self,
        maxsize: Optional[int] = 1024,
        button_data: Dict[str, Any] = None,
        lru_list: List[Tuple[str, List[str], float]] = None,
    ):
        self.logger = logging.getLogger(__name__)

        if (button_data is None and lru_list is not None) or (
            button_data is not None and lru_list is None
        ):
            raise ValueError('You must either pass both of button_data and lru_list or neither.')

        self.maxsize = maxsize
        self._keyboard_data: Dict[str, Node] = {}
        self._button_data: Dict[str, Any] = button_data or {}
        self._first_node: Optional[Node] = None
        self._last_node: Optional[Node] = None
        self.__lock = Lock()

        if lru_list:
            predecessor = None
            node = None
            for keyboard_uuid, button_uuids, access_time in lru_list:
                node = Node(
                    predecessor=predecessor,
                    keyboard_uuid=keyboard_uuid,
                    button_uuids=button_uuids,
                    access_time=access_time,
                )
                if not self._first_node:
                    self._first_node = node
                predecessor = node
                self._keyboard_data[keyboard_uuid] = node

            self._last_node = node

    def __iter(self) -> Iterator[Tuple[str, List[str], float]]:
        """
        list(self.__iter()) gives a static representation of the internal list. Should be a bit
        faster than a simple loop.
        """
        node = self._first_node
        while node:
            yield (
                node.keyboard_uuid,
                node.button_uuids,
                node.access_time,
            )
            node = node.successor

    @property
    def persistence_data(self) -> CDCData:
        """
        The data that needs to be persisted to allow caching callback data across bot reboots.
        """
        # While building a list from the nodes has linear runtime (in the number of nodes),
        # the runtime is bounded unless maxsize=None and it has the big upside of not throwing a
        # highly customized data structure at users trying to implement a custom persistence class
        with self.__lock:
            return self._button_data, list(self.__iter())

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
        return len(self._keyboard_data) >= self.maxsize

    def __drop_last(self) -> None:
        """Call to remove the last entry from the LRU cache"""
        if self._last_node:
            self.__drop_keyboard(self._last_node.keyboard_uuid)

    def __put_button(self, callback_data: Any, keyboard_uuid: str, button_uuids: List[str]) -> str:
        """
        Stores the data for a single button and appends the uuid to :attr:`button_uuids`.
        Finally returns the string that should be passed instead of the callback_data, which is
        ``keyboard_uuid + button_uuids``.
        """
        uuid = uuid4().hex
        self._button_data[uuid] = callback_data
        button_uuids.append(uuid)
        return f'{keyboard_uuid}{uuid}'

    def __put_node(self, keyboard_uuid: str, button_uuids: List[str]) -> None:
        """
        Inserts a new node into the list that holds the passed data.
        """
        new_node = Node(
            successor=self._first_node,
            keyboard_uuid=keyboard_uuid,
            button_uuids=button_uuids,
            access_time=time.time(),
        )
        if not self._first_node:
            self._last_node = new_node
        self._first_node = new_node
        self._keyboard_data[keyboard_uuid] = new_node

    def put_keyboard(self, reply_markup: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
        """
        Registers the reply markup to the cache. If any of the buttons have :attr:`callback_data`,
        stores that data and builds a new keyboard the the correspondingly replaced buttons.
        Otherwise does nothing and returns the original reply markup.

        Args:
            reply_markup (:class:`telegram.InlineKeyboardMarkup`): The keyboard.

        Returns:
            :class:`telegram.InlineKeyboardMarkup`: The keyboard to be passed to Telegram.

        """
        with self.__lock:
            return self.__put_keyboard(reply_markup)

    def __put_keyboard(self, reply_markup: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
        keyboard_uuid = uuid4().hex
        button_uuids: List[str] = []
        buttons = [
            [
                InlineKeyboardButton(
                    btn.text,
                    callback_data=self.__put_button(
                        btn.callback_data, keyboard_uuid, button_uuids
                    ),
                )
                if btn.callback_data
                else btn
                for btn in column
            ]
            for column in reply_markup.inline_keyboard
        ]

        if not button_uuids:
            return reply_markup

        if self.__full:
            self.logger.warning('CallbackDataCache full, dropping last keyboard.')
            self.__drop_last()

        self.__put_node(keyboard_uuid, button_uuids)
        return InlineKeyboardMarkup(buttons)

    def __update(self, keyboard_uuid: str) -> None:
        """
        Updates the timestamp of a keyboard and moves it to the top of the list.
        """
        node = self._keyboard_data[keyboard_uuid]

        if node is self._first_node:
            return

        if node.successor and node.predecessor:
            node.predecessor.successor = node.successor
        else:  # node is last node
            self._last_node = node.predecessor

        node.successor = self._first_node
        self._first_node = node
        node.access_time = time.time()

    def get_button_data(self, callback_data: str, update: bool = True) -> Any:
        """
        Looks up the stored :attr:`callback_data` for a button without deleting it from memory.

        Args:
            callback_data (:obj:`str`): The :attr:`callback_data` as contained in the button.
            update (:obj:`bool`, optional): Whether or not the keyboard the button is associated
                with should be marked as recently used. Defaults to :obj:`True`.

        Returns:
            The original :attr:`callback_data`.

        Raises:
            IndexError: If the button could not be found.

        """
        with self.__lock:
            data = self.__get_button_data(callback_data[32:])
            if update:
                self.__update(callback_data[:32])
            return data

    def __get_button_data(self, uuid: str) -> Any:
        try:
            return self._button_data[uuid]
        except KeyError as exc:
            raise IndexError(f'Button {uuid} could not be found.') from exc

    def drop_keyboard(self, callback_data: str) -> None:
        """
        Deletes the specified keyboard from the cache.

        Note:
            Will *not* raise exceptions in case the keyboard is not found.

        Args:
            callback_data (:obj:`str`): The :attr:`callback_data` as contained in one of the
                buttons associated with the keyboard.

        """
        with self.__lock:
            return self.__drop_keyboard(callback_data[:32])

    def __drop_keyboard(self, uuid: str) -> None:
        try:
            node = self._keyboard_data.pop(uuid)
        except KeyError:
            return

        for button_uuid in node.button_uuids:
            self._button_data.pop(button_uuid)

        if node.successor:
            node.successor.predecessor = node.predecessor
        else:  # node is last node
            self._last_node = node.predecessor

        if node.predecessor:
            node.predecessor.successor = node.successor
        else:  # node is first node
            self._first_node = node.successor

    def clear(self, time_cutoff: Union[float, datetime] = None) -> None:
        """
        Clears the cache.

        Args:
            time_cutoff (:obj:`float` | :obj:`datetime.datetime`, optional): Pass a UNIX timestamp
                or a :obj:`datetime.datetime` to clear only entries which are older. Naive
                :obj:`datetime.datetime` objects will be assumed to be in UTC.

        """
        with self.__lock:
            if not time_cutoff:
                self._first_node = None
                self._last_node = None
                self._keyboard_data.clear()
                self._button_data.clear()
                return

            if isinstance(time_cutoff, datetime):
                effective_cutoff = to_float_timestamp(time_cutoff)
            else:
                effective_cutoff = time_cutoff

            node = self._first_node
            while node:
                if node.access_time < effective_cutoff:
                    self.__drop_last()
                    node = node.predecessor
                else:
                    break
