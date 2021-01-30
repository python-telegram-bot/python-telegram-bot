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
"""This module contains the BasePersistence class."""
import warnings
from abc import ABC, abstractmethod
from copy import copy
from typing import DefaultDict, Dict, Optional, Tuple, cast, ClassVar

from telegram import Bot

from telegram.utils.types import ConversationDict


class BasePersistence(ABC):
    """Interface class for adding persistence to your bot.
    Subclass this object for different implementations of a persistent bot.

    All relevant methods must be overwritten. This includes:

    * :meth:`get_bot_data`
    * :meth:`update_bot_data`
    * :meth:`get_chat_data`
    * :meth:`update_chat_data`
    * :meth:`get_user_data`
    * :meth:`update_user_data`
    * :meth:`get_conversations`
    * :meth:`update_conversation`
    * :meth:`flush`

    If you don't actually need one of those methods, a simple ``pass`` is enough. For example, if
    ``store_bot_data=False``, you don't need :meth:`get_bot_data` and :meth:`update_bot_data`.

    Warning:
        Persistence will try to replace :class:`telegram.Bot` instances by :attr:`REPLACED_BOT` and
        insert the bot set with :meth:`set_bot` upon loading of the data. This is to ensure that
        changes to the bot apply to the saved objects, too. If you change the bots token, this may
        lead to e.g. ``Chat not found`` errors. For the limitations on replacing bots see
        :meth:`replace_bot` and :meth:`insert_bot`.

    Note:
         :meth:`replace_bot` and :meth:`insert_bot` are used *independently* of the implementation
         of the :meth:`update/get_*` methods, i.e. you don't need to worry about it while
         implementing a custom persistence subclass.

    Args:
        store_user_data (:obj:`bool`, optional): Whether user_data should be saved by this
            persistence class. Default is :obj:`True`.
        store_chat_data (:obj:`bool`, optional): Whether chat_data should be saved by this
            persistence class. Default is :obj:`True` .
        store_bot_data (:obj:`bool`, optional): Whether bot_data should be saved by this
            persistence class. Default is :obj:`True` .

    Attributes:
        store_user_data (:obj:`bool`): Optional, Whether user_data should be saved by this
            persistence class.
        store_chat_data (:obj:`bool`): Optional. Whether chat_data should be saved by this
            persistence class.
        store_bot_data (:obj:`bool`): Optional. Whether bot_data should be saved by this
            persistence class.
    """

    def __new__(
        cls, *args: object, **kwargs: object  # pylint: disable=W0613
    ) -> 'BasePersistence':
        instance = super().__new__(cls)
        get_user_data = instance.get_user_data
        get_chat_data = instance.get_chat_data
        get_bot_data = instance.get_bot_data
        update_user_data = instance.update_user_data
        update_chat_data = instance.update_chat_data
        update_bot_data = instance.update_bot_data

        def get_user_data_insert_bot() -> DefaultDict[int, Dict[object, object]]:
            return instance.insert_bot(get_user_data())

        def get_chat_data_insert_bot() -> DefaultDict[int, Dict[object, object]]:
            return instance.insert_bot(get_chat_data())

        def get_bot_data_insert_bot() -> Dict[object, object]:
            return instance.insert_bot(get_bot_data())

        def update_user_data_replace_bot(user_id: int, data: Dict) -> None:
            return update_user_data(user_id, instance.replace_bot(data))

        def update_chat_data_replace_bot(chat_id: int, data: Dict) -> None:
            return update_chat_data(chat_id, instance.replace_bot(data))

        def update_bot_data_replace_bot(data: Dict) -> None:
            return update_bot_data(instance.replace_bot(data))

        instance.get_user_data = get_user_data_insert_bot
        instance.get_chat_data = get_chat_data_insert_bot
        instance.get_bot_data = get_bot_data_insert_bot
        instance.update_user_data = update_user_data_replace_bot
        instance.update_chat_data = update_chat_data_replace_bot
        instance.update_bot_data = update_bot_data_replace_bot
        return instance

    def __init__(
        self,
        store_user_data: bool = True,
        store_chat_data: bool = True,
        store_bot_data: bool = True,
    ):
        self.store_user_data = store_user_data
        self.store_chat_data = store_chat_data
        self.store_bot_data = store_bot_data
        self.bot: Bot = None  # type: ignore[assignment]

    def set_bot(self, bot: Bot) -> None:
        """Set the Bot to be used by this persistence instance.

        Args:
            bot (:class:`telegram.Bot`): The bot.
        """
        self.bot = bot

    @classmethod
    def replace_bot(cls, obj: object) -> object:
        """
        Replaces all instances of :class:`telegram.Bot` that occur within the passed object with
        :attr:`REPLACED_BOT`. Currently, this handles objects of type ``list``, ``tuple``, ``set``,
        ``frozenset``, ``dict``, ``defaultdict`` and objects that have a ``__dict__`` or
        ``__slot__`` attribute, excluding objects that can't be copied with `copy.copy`.

        Args:
            obj (:obj:`object`): The object

        Returns:
            :obj:`obj`: Copy of the object with Bot instances replaced.
        """
        return cls._replace_bot(obj, {})

    @classmethod
    def _replace_bot(cls, obj: object, memo: Dict[int, object]) -> object:  # pylint: disable=R0911
        obj_id = id(obj)
        if obj_id in memo:
            return memo[obj_id]

        if isinstance(obj, Bot):
            memo[obj_id] = cls.REPLACED_BOT
            return cls.REPLACED_BOT
        if isinstance(obj, (list, set)):
            # We copy the iterable here for thread safety, i.e. make sure the object we iterate
            # over doesn't change its length during the iteration
            temp_iterable = obj.copy()
            new_iterable = obj.__class__(cls._replace_bot(item, memo) for item in temp_iterable)
            memo[obj_id] = new_iterable
            return new_iterable
        if isinstance(obj, (tuple, frozenset)):
            # tuples and frozensets are immutable so we don't need to worry about thread safety
            new_immutable = obj.__class__(cls._replace_bot(item, memo) for item in obj)
            memo[obj_id] = new_immutable
            return new_immutable

        try:
            new_obj = copy(obj)
            memo[obj_id] = new_obj
        except Exception:
            warnings.warn(
                'BasePersistence.replace_bot does not handle objects that can not be copied. See '
                'the docs of BasePersistence.replace_bot for more information.',
                RuntimeWarning,
            )
            memo[obj_id] = obj
            return obj

        if isinstance(obj, dict):
            # We handle dicts via copy(obj) so we don't have to make a
            # difference between dict and defaultdict
            new_obj = cast(dict, new_obj)
            # We can't iterate over obj.items() due to thread safety, i.e. the dicts length may
            # change during the iteration
            temp_dict = new_obj.copy()
            new_obj.clear()
            for k, val in temp_dict.items():
                new_obj[cls._replace_bot(k, memo)] = cls._replace_bot(val, memo)
            memo[obj_id] = new_obj
            return new_obj
        if hasattr(obj, '__dict__'):
            for attr_name, attr in new_obj.__dict__.items():
                setattr(new_obj, attr_name, cls._replace_bot(attr, memo))
            memo[obj_id] = new_obj
            return new_obj
        if hasattr(obj, '__slots__'):
            for attr_name in new_obj.__slots__:
                setattr(
                    new_obj,
                    attr_name,
                    cls._replace_bot(cls._replace_bot(getattr(new_obj, attr_name), memo), memo),
                )
            memo[obj_id] = new_obj
            return new_obj

        return obj

    def insert_bot(self, obj: object) -> object:
        """
        Replaces all instances of :attr:`REPLACED_BOT` that occur within the passed object with
        :attr:`bot`. Currently, this handles objects of type ``list``, ``tuple``, ``set``,
        ``frozenset``, ``dict``, ``defaultdict`` and objects that have a ``__dict__`` or
        ``__slot__`` attribute, excluding objects that can't be copied with `copy.copy`.

        Args:
            obj (:obj:`object`): The object

        Returns:
            :obj:`obj`: Copy of the object with Bot instances inserted.
        """
        return self._insert_bot(obj, {})

    def _insert_bot(self, obj: object, memo: Dict[int, object]) -> object:  # pylint: disable=R0911
        obj_id = id(obj)
        if obj_id in memo:
            return memo[obj_id]

        if isinstance(obj, Bot):
            memo[obj_id] = self.bot
            return self.bot
        if isinstance(obj, str) and obj == self.REPLACED_BOT:
            memo[obj_id] = self.bot
            return self.bot
        if isinstance(obj, (list, set)):
            # We copy the iterable here for thread safety, i.e. make sure the object we iterate
            # over doesn't change its length during the iteration
            temp_iterable = obj.copy()
            new_iterable = obj.__class__(self._insert_bot(item, memo) for item in temp_iterable)
            memo[obj_id] = new_iterable
            return new_iterable
        if isinstance(obj, (tuple, frozenset)):
            # tuples and frozensets are immutable so we don't need to worry about thread safety
            new_immutable = obj.__class__(self._insert_bot(item, memo) for item in obj)
            memo[obj_id] = new_immutable
            return new_immutable

        try:
            new_obj = copy(obj)
        except Exception:
            warnings.warn(
                'BasePersistence.insert_bot does not handle objects that can not be copied. See '
                'the docs of BasePersistence.insert_bot for more information.',
                RuntimeWarning,
            )
            memo[obj_id] = obj
            return obj

        if isinstance(obj, dict):
            # We handle dicts via copy(obj) so we don't have to make a
            # difference between dict and defaultdict
            new_obj = cast(dict, new_obj)
            # We can't iterate over obj.items() due to thread safety, i.e. the dicts length may
            # change during the iteration
            temp_dict = new_obj.copy()
            new_obj.clear()
            for k, val in temp_dict.items():
                new_obj[self._insert_bot(k, memo)] = self._insert_bot(val, memo)
            memo[obj_id] = new_obj
            return new_obj
        if hasattr(obj, '__dict__'):
            for attr_name, attr in new_obj.__dict__.items():
                setattr(new_obj, attr_name, self._insert_bot(attr, memo))
            memo[obj_id] = new_obj
            return new_obj
        if hasattr(obj, '__slots__'):
            for attr_name in obj.__slots__:
                setattr(
                    new_obj,
                    attr_name,
                    self._insert_bot(self._insert_bot(getattr(new_obj, attr_name), memo), memo),
                )
            memo[obj_id] = new_obj
            return new_obj

        return obj

    @abstractmethod
    def get_user_data(self) -> DefaultDict[int, Dict[object, object]]:
        """ "Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the ``user_data`` if stored, or an empty
        ``defaultdict(dict)``.

        Returns:
            :obj:`defaultdict`: The restored user data.
        """

    @abstractmethod
    def get_chat_data(self) -> DefaultDict[int, Dict[object, object]]:
        """ "Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the ``chat_data`` if stored, or an empty
        ``defaultdict(dict)``.

        Returns:
            :obj:`defaultdict`: The restored chat data.
        """

    @abstractmethod
    def get_bot_data(self) -> Dict[object, object]:
        """ "Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the ``bot_data`` if stored, or an empty
        :obj:`dict`.

        Returns:
            :obj:`dict`: The restored bot data.
        """

    @abstractmethod
    def get_conversations(self, name: str) -> ConversationDict:
        """ "Will be called by :class:`telegram.ext.Dispatcher` when a
        :class:`telegram.ext.ConversationHandler` is added if
        :attr:`telegram.ext.ConversationHandler.persistent` is :obj:`True`.
        It should return the conversations for the handler with `name` or an empty :obj:`dict`

        Args:
            name (:obj:`str`): The handlers name.

        Returns:
            :obj:`dict`: The restored conversations for the handler.
        """

    @abstractmethod
    def update_conversation(
        self, name: str, key: Tuple[int, ...], new_state: Optional[object]
    ) -> None:
        """Will be called when a :attr:`telegram.ext.ConversationHandler.update_state`
        is called. This allows the storage of the new state in the persistence.

        Args:
            name (:obj:`str`): The handler's name.
            key (:obj:`tuple`): The key the state is changed for.
            new_state (:obj:`tuple` | :obj:`any`): The new state for the given key.
        """

    @abstractmethod
    def update_user_data(self, user_id: int, data: Dict) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.user_data` [user_id].
        """

    @abstractmethod
    def update_chat_data(self, chat_id: int, data: Dict) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.chat_data` [chat_id].
        """

    @abstractmethod
    def update_bot_data(self, data: Dict) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.bot_data` .
        """

    def flush(self) -> None:
        """Will be called by :class:`telegram.ext.Updater` upon receiving a stop signal. Gives the
        persistence a chance to finish up saving or close a database connection gracefully.
        """

    REPLACED_BOT: ClassVar[str] = 'bot_instance_replaced_by_ptb_persistence'
    """:obj:`str`: Placeholder for :class:`telegram.Bot` instances replaced in saved data."""
