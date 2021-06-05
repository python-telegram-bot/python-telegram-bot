#!/usr/bin/env python

#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2021
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].

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
from typing import Dict, Tuple, Union, Optional, MutableMapping, TYPE_CHECKING, cast
from uuid import uuid4

from cachetools import LRUCache  # pylint: disable=E0401

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    TelegramError,
    CallbackQuery,
    Message,
    User,
)
from telegram.utils.helpers import to_float_timestamp
from telegram.ext.utils.types import CDCData

if TYPE_CHECKING:
    from telegram.ext import ExtBot


class InvalidCallbackData(TelegramError):
    """
    Raised when the received callback data has been tempered with or deleted from cache.

    .. versionadded:: 13.6

    Args:
        callback_data (:obj:`int`, optional): The button data of which the callback data could not
            be found.

    Attributes:
        callback_data (:obj:`int`): Optional. The button data of which the callback data could not
            be found.
    """

    __slots__ = ('callback_data',)

    def __init__(self, callback_data: str = None) -> None:
        super().__init__(
            'The object belonging to this callback_data was deleted or the callback_data was '
            'manipulated.'
        )
        self.callback_data = callback_data

    def __reduce__(self) -> Tuple[type, Tuple[Optional[str]]]:  # type: ignore[override]
        return self.__class__, (self.callback_data,)


class _KeyboardData:
    __slots__ = ('keyboard_uuid', 'button_data', 'access_time')

    def __init__(
        self, keyboard_uuid: str, access_time: float = None, button_data: Dict[str, object] = None
    ):
        self.keyboard_uuid = keyboard_uuid
        self.button_data = button_data or {}
        self.access_time = access_time or time.time()

    def update_access_time(self) -> None:
        """Updates the access time with the current time."""
        self.access_time = time.time()

    def to_tuple(self) -> Tuple[str, float, Dict[str, object]]:
        """Gives a tuple representation consisting of the keyboard uuid, the access time and the
        button data.
        """
        return self.keyboard_uuid, self.access_time, self.button_data


class CallbackDataCache:
    """A custom cache for storing the callback data of a :class:`telegram.ext.ExtBot`. Internally,
    it keeps two mappings with fixed maximum size:

        * One for mapping the data received in callback queries to the cached objects
        * One for mapping the IDs of received callback queries to the cached objects

    The second mapping allows to manually drop data that has been cached for keyboards of messages
    sent via inline mode.
    If necessary, will drop the least recently used items.

    .. versionadded:: 13.6

    Args:
        bot (:class:`telegram.ext.ExtBot`): The bot this cache is for.
        maxsize (:obj:`int`, optional): Maximum number of items in each of the internal mappings.
            Defaults to 1024.
        persistent_data (:obj:`telegram.ext.utils.types.CDCData`, optional): Data to initialize
            the cache with, as returned by :meth:`telegram.ext.BasePersistence.get_callback_data`.

    Attributes:
        bot (:class:`telegram.ext.ExtBot`): The bot this cache is for.
        maxsize (:obj:`int`): maximum size of the cache.

    """

    __slots__ = ('bot', 'maxsize', '_keyboard_data', '_callback_queries', '__lock', 'logger')

    def __init__(
        self,
        bot: 'ExtBot',
        maxsize: int = 1024,
        persistent_data: CDCData = None,
    ):
        self.logger = logging.getLogger(__name__)

        self.bot = bot
        self.maxsize = maxsize
        self._keyboard_data: MutableMapping[str, _KeyboardData] = LRUCache(maxsize=maxsize)
        self._callback_queries: MutableMapping[str, str] = LRUCache(maxsize=maxsize)
        self.__lock = Lock()

        if persistent_data:
            keyboard_data, callback_queries = persistent_data
            for key, value in callback_queries.items():
                self._callback_queries[key] = value
            for uuid, access_time, data in keyboard_data:
                self._keyboard_data[uuid] = _KeyboardData(
                    keyboard_uuid=uuid, access_time=access_time, button_data=data
                )

    @property
    def persistence_data(self) -> CDCData:
        """:obj:`telegram.ext.utils.types.CDCData`: The data that needs to be persisted to allow
        caching callback data across bot reboots.
        """
        # While building a list/dict from the LRUCaches has linear runtime (in the number of
        # entries), the runtime is bounded by maxsize and it has the big upside of not throwing a
        # highly customized data structure at users trying to implement a custom persistence class
        with self.__lock:
            return [data.to_tuple() for data in self._keyboard_data.values()], dict(
                self._callback_queries.items()
            )

    def process_keyboard(self, reply_markup: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
        """Registers the reply markup to the cache. If any of the buttons have
        :attr:`callback_data`, stores that data and builds a new keyboard with the correspondingly
        replaced buttons. Otherwise does nothing and returns the original reply markup.

        Args:
            reply_markup (:class:`telegram.InlineKeyboardMarkup`): The keyboard.

        Returns:
            :class:`telegram.InlineKeyboardMarkup`: The keyboard to be passed to Telegram.

        """
        with self.__lock:
            return self.__process_keyboard(reply_markup)

    def __process_keyboard(self, reply_markup: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
        keyboard_uuid = uuid4().hex
        keyboard_data = _KeyboardData(keyboard_uuid)

        # Built a new nested list of buttons by replacing the callback data if needed
        buttons = [
            [
                # We create a new button instead of replacing callback_data in case the
                # same object is used elsewhere
                InlineKeyboardButton(
                    btn.text,
                    callback_data=self.__put_button(btn.callback_data, keyboard_data),
                )
                if btn.callback_data
                else btn
                for btn in column
            ]
            for column in reply_markup.inline_keyboard
        ]

        if not keyboard_data.button_data:
            # If we arrive here, no data had to be replaced and we can return the input
            return reply_markup

        self._keyboard_data[keyboard_uuid] = keyboard_data
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def __put_button(callback_data: object, keyboard_data: _KeyboardData) -> str:
        """Stores the data for a single button in :attr:`keyboard_data`.
        Returns the string that should be passed instead of the callback_data, which is
        ``keyboard_uuid + button_uuids``.
        """
        uuid = uuid4().hex
        keyboard_data.button_data[uuid] = callback_data
        return f'{keyboard_data.keyboard_uuid}{uuid}'

    def __get_keyboard_uuid_and_button_data(
        self, callback_data: str
    ) -> Union[Tuple[str, object], Tuple[None, InvalidCallbackData]]:
        keyboard, button = self.extract_uuids(callback_data)
        try:
            # we get the values before calling update() in case KeyErrors are raised
            # we don't want to update in that case
            keyboard_data = self._keyboard_data[keyboard]
            button_data = keyboard_data.button_data[button]
            # Update the timestamp for the LRU
            keyboard_data.update_access_time()
            return keyboard, button_data
        except KeyError:
            return None, InvalidCallbackData(callback_data)

    @staticmethod
    def extract_uuids(callback_data: str) -> Tuple[str, str]:
        """Extracts the keyboard uuid and the button uuid from the given ``callback_data``.

        Args:
            callback_data (:obj:`str`): The ``callback_data`` as present in the button.

        Returns:
            (:obj:`str`, :obj:`str`): Tuple of keyboard and button uuid

        """
        # Extract the uuids as put in __put_button
        return callback_data[:32], callback_data[32:]

    def process_message(self, message: Message) -> None:
        """Replaces the data in the inline keyboard attached to the message with the cached
        objects, if necessary. If the data could not be found,
        :class:`telegram.ext.InvalidCallbackData` will be inserted.

        Note:
            Checks :attr:`telegram.Message.via_bot` and :attr:`telegram.Message.from_user` to check
            if the reply markup (if any) was actually sent by this caches bot. If it was not, the
            message will be returned unchanged.

            Note that this will fail for channel posts, as :attr:`telegram.Message.from_user` is
            :obj:`None` for those! In the corresponding reply markups the callback data will be
            replaced by :class:`telegram.ext.InvalidCallbackData`.

        Warning:
            * Does *not* consider :attr:`telegram.Message.reply_to_message` and
              :attr:`telegram.Message.pinned_message`. Pass them to these method separately.
            * *In place*, i.e. the passed :class:`telegram.Message` will be changed!

        Args:
            message (:class:`telegram.Message`): The message.

        """
        with self.__lock:
            self.__process_message(message)

    def __process_message(self, message: Message) -> Optional[str]:
        """As documented in process_message, but returns the uuid of the attached keyboard, if any,
        which is relevant for process_callback_query.

        **IN PLACE**
        """
        if not message.reply_markup:
            return None

        if message.via_bot:
            sender: Optional[User] = message.via_bot
        elif message.from_user:
            sender = message.from_user
        else:
            sender = None

        if sender is not None and sender != self.bot.bot:
            return None

        keyboard_uuid = None

        for row in message.reply_markup.inline_keyboard:
            for button in row:
                if button.callback_data:
                    button_data = cast(str, button.callback_data)
                    keyboard_id, callback_data = self.__get_keyboard_uuid_and_button_data(
                        button_data
                    )
                    # update_callback_data makes sure that the _id_attrs are updated
                    button.update_callback_data(callback_data)

                    # This is lazy loaded. The firsts time we find a button
                    # we load the associated keyboard - afterwards, there is
                    if not keyboard_uuid and not isinstance(callback_data, InvalidCallbackData):
                        keyboard_uuid = keyboard_id

        return keyboard_uuid

    def process_callback_query(self, callback_query: CallbackQuery) -> None:
        """Replaces the data in the callback query and the attached messages keyboard with the
        cached objects, if necessary. If the data could not be found,
        :class:`telegram.ext.InvalidCallbackData` will be inserted.
        If :attr:`callback_query.data` or :attr:`callback_query.message` is present, this also
        saves the callback queries ID in order to be able to resolve it to the stored data.

        Note:
            Also considers inserts data into the buttons of
            :attr:`telegram.Message.reply_to_message` and :attr:`telegram.Message.pinned_message`
            if necessary.

        Warning:
            *In place*, i.e. the passed :class:`telegram.CallbackQuery` will be changed!

        Args:
            callback_query (:class:`telegram.CallbackQuery`): The callback query.

        """
        with self.__lock:
            mapped = False

            if callback_query.data:
                data = callback_query.data

                # Get the cached callback data for the CallbackQuery
                keyboard_uuid, button_data = self.__get_keyboard_uuid_and_button_data(data)
                callback_query.data = button_data  # type: ignore[assignment]

                # Map the callback queries ID to the keyboards UUID for later use
                if not mapped and not isinstance(button_data, InvalidCallbackData):
                    self._callback_queries[callback_query.id] = keyboard_uuid  # type: ignore
                    mapped = True

            # Get the cached callback data for the inline keyboard attached to the
            # CallbackQuery.
            if callback_query.message:
                self.__process_message(callback_query.message)
                for message in (
                    callback_query.message.pinned_message,
                    callback_query.message.reply_to_message,
                ):
                    if message:
                        self.__process_message(message)

    def drop_data(self, callback_query: CallbackQuery) -> None:
        """Deletes the data for the specified callback query.

        Note:
            Will *not* raise exceptions in case the callback data is not found in the cache.
            *Will* raise :class:`KeyError` in case the callback query can not be found in the
            cache.

        Args:
            callback_query (:class:`telegram.CallbackQuery`): The callback query.

        Raises:
            KeyError: If the callback query can not be found in the cache
        """
        with self.__lock:
            try:
                keyboard_uuid = self._callback_queries.pop(callback_query.id)
                self.__drop_keyboard(keyboard_uuid)
            except KeyError as exc:
                raise KeyError('CallbackQuery was not found in cache.') from exc

    def __drop_keyboard(self, keyboard_uuid: str) -> None:
        try:
            self._keyboard_data.pop(keyboard_uuid)
        except KeyError:
            return

    def clear_callback_data(self, time_cutoff: Union[float, datetime] = None) -> None:
        """Clears the stored callback data.

        Args:
            time_cutoff (:obj:`float` | :obj:`datetime.datetime`, optional): Pass a UNIX timestamp
                or a :obj:`datetime.datetime` to clear only entries which are older.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used.

        """
        with self.__lock:
            self.__clear(self._keyboard_data, time_cutoff=time_cutoff)

    def clear_callback_queries(self) -> None:
        """Clears the stored callback query IDs."""
        with self.__lock:
            self.__clear(self._callback_queries)

    def __clear(self, mapping: MutableMapping, time_cutoff: Union[float, datetime] = None) -> None:
        if not time_cutoff:
            mapping.clear()
            return

        if isinstance(time_cutoff, datetime):
            effective_cutoff = to_float_timestamp(
                time_cutoff, tzinfo=self.bot.defaults.tzinfo if self.bot.defaults else None
            )
        else:
            effective_cutoff = time_cutoff

        # We need a list instead of a generator here, as the list doesn't change it's size
        # during the iteration
        to_drop = [key for key, data in mapping.items() if data.access_time < effective_cutoff]
        for key in to_drop:
            mapping.pop(key)
