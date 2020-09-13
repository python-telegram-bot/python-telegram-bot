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
"""This module contains the BasePersistence class."""

from abc import ABC, abstractmethod
from collections import defaultdict
from copy import copy

from telegram import Bot

from typing import DefaultDict, Dict, Any, Tuple, Optional, cast
from telegram.utils.types import ConversationDict


class BasePersistence(ABC):
    """Interface class for adding persistence to your bot.
    Subclass this object for different implementations of a persistent bot.

    All relevant methods must be overwritten. This means:

    * If :attr:`store_bot_data` is :obj:`True` you must overwrite :meth:`get_bot_data` and
      :meth:`update_bot_data`.
    * If :attr:`store_chat_data` is :obj:`True` you must overwrite :meth:`get_chat_data` and
      :meth:`update_chat_data`.
    * If :attr:`store_user_data` is :obj:`True` you must overwrite :meth:`get_user_data` and
      :meth:`update_user_data`.
    * If you want to store conversation data with :class:`telegram.ext.ConversationHandler`, you
      must overwrite :meth:`get_conversations` and :meth:`update_conversation`.
    * :meth:`flush` will be called when the bot is shutdown.

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

    Attributes:
        store_user_data (:obj:`bool`): Optional, Whether user_data should be saved by this
            persistence class.
        store_chat_data (:obj:`bool`): Optional. Whether chat_data should be saved by this
            persistence class.
        store_bot_data (:obj:`bool`): Optional. Whether bot_data should be saved by this
            persistence class.

    Args:
        store_user_data (:obj:`bool`, optional): Whether user_data should be saved by this
            persistence class. Default is :obj:`True`.
        store_chat_data (:obj:`bool`, optional): Whether chat_data should be saved by this
            persistence class. Default is :obj:`True` .
        store_bot_data (:obj:`bool`, optional): Whether bot_data should be saved by this
            persistence class. Default is :obj:`True` .
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> 'BasePersistence':
        instance = super().__new__(cls)
        get_user_data = instance.get_user_data
        get_chat_data = instance.get_chat_data
        get_bot_data = instance.get_bot_data
        update_user_data = instance.update_user_data
        update_chat_data = instance.update_chat_data
        update_bot_data = instance.update_bot_data

        def get_user_data_insert_bot() -> DefaultDict[int, Dict[Any, Any]]:
            return instance.insert_bot(get_user_data())

        def get_chat_data_insert_bot() -> DefaultDict[int, Dict[Any, Any]]:
            return instance.insert_bot(get_chat_data())

        def get_bot_data_insert_bot() -> Dict[Any, Any]:
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

    def __init__(self,
                 store_user_data: bool = True,
                 store_chat_data: bool = True,
                 store_bot_data: bool = True):
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
        ``__slot__`` attribute.

        Args:
            obj (:obj:`object`): The object

        Returns:
            :obj:`obj`: Copy of the object with Bot instances replaced.
        """
        if isinstance(obj, Bot):
            return cls.REPLACED_BOT
        if isinstance(obj, (list, tuple, set, frozenset)):
            return obj.__class__(cls.replace_bot(item) for item in obj)

        new_obj = copy(obj)
        if isinstance(obj, (dict, defaultdict)):
            new_obj = cast(dict, new_obj)
            new_obj.clear()
            for k, v in obj.items():
                new_obj[cls.replace_bot(k)] = cls.replace_bot(v)
            return new_obj
        if hasattr(obj, '__dict__'):
            for attr_name, attr in new_obj.__dict__.items():
                setattr(new_obj, attr_name, cls.replace_bot(attr))
            return new_obj
        if hasattr(obj, '__slots__'):
            for attr_name in new_obj.__slots__:
                setattr(new_obj, attr_name,
                        cls.replace_bot(cls.replace_bot(getattr(new_obj, attr_name))))
            return new_obj

        return obj

    def insert_bot(self, obj: object) -> object:
        """
        Replaces all instances of :attr:`REPLACED_BOT` that occur within the passed object with
        :attr:`bot`. Currently, this handles objects of type ``list``, ``tuple``, ``set``,
        ``frozenset``, ``dict``, ``defaultdict`` and objects that have a ``__dict__`` or
        ``__slot__`` attribute.

        Args:
            obj (:obj:`object`): The object

        Returns:
            :obj:`obj`: Copy of the object with Bot instances inserted.
        """
        if isinstance(obj, Bot):
            return self.bot
        if obj == self.REPLACED_BOT:
            return self.bot
        if isinstance(obj, (list, tuple, set, frozenset)):
            return obj.__class__(self.insert_bot(item) for item in obj)

        new_obj = copy(obj)
        if isinstance(obj, (dict, defaultdict)):
            new_obj = cast(dict, new_obj)
            new_obj.clear()
            for k, v in obj.items():
                new_obj[self.insert_bot(k)] = self.insert_bot(v)
            return new_obj
        if hasattr(obj, '__dict__'):
            for attr_name, attr in new_obj.__dict__.items():
                setattr(new_obj, attr_name, self.insert_bot(attr))
            return new_obj
        if hasattr(obj, '__slots__'):
            for attr_name in obj.__slots__:
                setattr(new_obj, attr_name,
                        self.insert_bot(self.insert_bot(getattr(new_obj, attr_name))))
            return new_obj
        return obj

    @abstractmethod
    def get_user_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        """"Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the user_data if stored, or an empty
        ``defaultdict(dict)``.

        Returns:
            :obj:`defaultdict`: The restored user data.
        """

    @abstractmethod
    def get_chat_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        """"Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the chat_data if stored, or an empty
        ``defaultdict(dict)``.

        Returns:
            :obj:`defaultdict`: The restored chat data.
        """

    @abstractmethod
    def get_bot_data(self) -> Dict[Any, Any]:
        """"Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the bot_data if stored, or an empty
        :obj:`dict`.

        Returns:
            :obj:`dict`: The restored bot data.
        """

    @abstractmethod
    def get_conversations(self, name: str) -> ConversationDict:
        """"Will be called by :class:`telegram.ext.Dispatcher` when a
        :class:`telegram.ext.ConversationHandler` is added if
        :attr:`telegram.ext.ConversationHandler.persistent` is :obj:`True`.
        It should return the conversations for the handler with `name` or an empty :obj:`dict`

        Args:
            name (:obj:`str`): The handlers name.

        Returns:
            :obj:`dict`: The restored conversations for the handler.
        """

    @abstractmethod
    def update_conversation(self,
                            name: str, key: Tuple[int, ...],
                            new_state: Optional[object]) -> None:
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
        persistence a chance to finish up saving or close a database connection gracefully. If this
        is not of any importance just pass will be sufficient.
        """
        pass

    REPLACED_BOT = 'bot_instance_replaced_by_ptb_persistence'
    """:obj:`str`: Placeholder for :class:`telegram.Bot` instances replaced in saved data."""
