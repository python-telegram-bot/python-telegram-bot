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
from sys import version_info as py_ver
from abc import ABC, abstractmethod
from copy import copy
from typing import Dict, Optional, Tuple, cast, ClassVar, Generic, DefaultDict

from telegram.utils.deprecate import set_new_attribute_deprecated

from telegram import Bot
import telegram.ext.extbot

from telegram.ext.utils.types import UD, CD, BD, ConversationDict, CDCData


class BasePersistence(Generic[UD, CD, BD], ABC):
    """Interface class for adding persistence to your bot.
    Subclass this object for different implementations of a persistent bot.

    All relevant methods must be overwritten. This includes:

    * :meth:`get_bot_data`
    * :meth:`update_bot_data`
    * :meth:`refresh_bot_data`
    * :meth:`get_chat_data`
    * :meth:`update_chat_data`
    * :meth:`refresh_chat_data`
    * :meth:`get_user_data`
    * :meth:`update_user_data`
    * :meth:`refresh_user_data`
    * :meth:`get_callback_data`
    * :meth:`update_callback_data`
    * :meth:`get_conversations`
    * :meth:`update_conversation`
    * :meth:`flush`

    If you don't actually need one of those methods, a simple ``pass`` is enough. For example, if
    ``store_bot_data=False``, you don't need :meth:`get_bot_data`, :meth:`update_bot_data` or
    :meth:`refresh_bot_data`.

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
            persistence class. Default is :obj:`True`.
        store_callback_data (:obj:`bool`, optional): Whether callback_data should be saved by this
            persistence class. Default is :obj:`False`.

            .. versionadded:: 13.6

    Attributes:
        store_user_data (:obj:`bool`): Optional, Whether user_data should be saved by this
            persistence class.
        store_chat_data (:obj:`bool`): Optional. Whether chat_data should be saved by this
            persistence class.
        store_bot_data (:obj:`bool`): Optional. Whether bot_data should be saved by this
            persistence class.
        store_callback_data (:obj:`bool`): Optional. Whether callback_data should be saved by this
            persistence class.

            .. versionadded:: 13.6
    """

    # Apparently Py 3.7 and below have '__dict__' in ABC
    if py_ver < (3, 7):
        __slots__ = (
            'store_user_data',
            'store_chat_data',
            'store_bot_data',
            'store_callback_data',
            'bot',
        )
    else:
        __slots__ = (
            'store_user_data',  # type: ignore[assignment]
            'store_chat_data',
            'store_bot_data',
            'store_callback_data',
            'bot',
            '__dict__',
        )

    def __new__(
        cls, *args: object, **kwargs: object  # pylint: disable=W0613
    ) -> 'BasePersistence':
        """This overrides the get_* and update_* methods to use insert/replace_bot.
        That has the side effect that we always pass deepcopied data to those methods, so in
        Pickle/DictPersistence we don't have to worry about copying the data again.

        Note: This doesn't hold for second tuple-entry of callback_data. That's a Dict[str, str],
        so no bots to replace anyway.
        """
        instance = super().__new__(cls)
        get_user_data = instance.get_user_data
        get_chat_data = instance.get_chat_data
        get_bot_data = instance.get_bot_data
        get_callback_data = instance.get_callback_data
        update_user_data = instance.update_user_data
        update_chat_data = instance.update_chat_data
        update_bot_data = instance.update_bot_data
        update_callback_data = instance.update_callback_data

        def get_user_data_insert_bot() -> DefaultDict[int, UD]:
            return instance.insert_bot(get_user_data())

        def get_chat_data_insert_bot() -> DefaultDict[int, CD]:
            return instance.insert_bot(get_chat_data())

        def get_bot_data_insert_bot() -> BD:
            return instance.insert_bot(get_bot_data())

        def get_callback_data_insert_bot() -> Optional[CDCData]:
            cdc_data = get_callback_data()
            if cdc_data is None:
                return None
            return instance.insert_bot(cdc_data[0]), cdc_data[1]

        def update_user_data_replace_bot(user_id: int, data: UD) -> None:
            return update_user_data(user_id, instance.replace_bot(data))

        def update_chat_data_replace_bot(chat_id: int, data: CD) -> None:
            return update_chat_data(chat_id, instance.replace_bot(data))

        def update_bot_data_replace_bot(data: BD) -> None:
            return update_bot_data(instance.replace_bot(data))

        def update_callback_data_replace_bot(data: CDCData) -> None:
            obj_data, queue = data
            return update_callback_data((instance.replace_bot(obj_data), queue))

        # We want to ignore TGDeprecation warnings so we use obj.__setattr__. Adds to __dict__
        object.__setattr__(instance, 'get_user_data', get_user_data_insert_bot)
        object.__setattr__(instance, 'get_chat_data', get_chat_data_insert_bot)
        object.__setattr__(instance, 'get_bot_data', get_bot_data_insert_bot)
        object.__setattr__(instance, 'get_callback_data', get_callback_data_insert_bot)
        object.__setattr__(instance, 'update_user_data', update_user_data_replace_bot)
        object.__setattr__(instance, 'update_chat_data', update_chat_data_replace_bot)
        object.__setattr__(instance, 'update_bot_data', update_bot_data_replace_bot)
        object.__setattr__(instance, 'update_callback_data', update_callback_data_replace_bot)
        return instance

    def __init__(
        self,
        store_user_data: bool = True,
        store_chat_data: bool = True,
        store_bot_data: bool = True,
        store_callback_data: bool = False,
    ):
        self.store_user_data = store_user_data
        self.store_chat_data = store_chat_data
        self.store_bot_data = store_bot_data
        self.store_callback_data = store_callback_data
        self.bot: Bot = None  # type: ignore[assignment]

    def __setattr__(self, key: str, value: object) -> None:
        # Allow user defined subclasses to have custom attributes.
        if issubclass(self.__class__, BasePersistence) and self.__class__.__name__ not in {
            'DictPersistence',
            'PicklePersistence',
        }:
            object.__setattr__(self, key, value)
            return
        set_new_attribute_deprecated(self, key, value)

    def set_bot(self, bot: Bot) -> None:
        """Set the Bot to be used by this persistence instance.

        Args:
            bot (:class:`telegram.Bot`): The bot.
        """
        if self.store_callback_data and not isinstance(bot, telegram.ext.extbot.ExtBot):
            raise TypeError('store_callback_data can only be used with telegram.ext.ExtBot.')

        self.bot = bot

    @classmethod
    def replace_bot(cls, obj: object) -> object:
        """
        Replaces all instances of :class:`telegram.Bot` that occur within the passed object with
        :attr:`REPLACED_BOT`. Currently, this handles objects of type ``list``, ``tuple``, ``set``,
        ``frozenset``, ``dict``, ``defaultdict`` and objects that have a ``__dict__`` or
        ``__slots__`` attribute, excluding classes and objects that can't be copied with
        ``copy.copy``. If the parsing of an object fails, the object will be returned unchanged and
        the error will be logged.

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
        if isinstance(obj, type):
            # classes usually do have a __dict__, but it's not writable
            warnings.warn(
                'BasePersistence.replace_bot does not handle classes. See '
                'the docs of BasePersistence.replace_bot for more information.',
                RuntimeWarning,
            )
            return obj

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
        # if '__dict__' in obj.__slots__, we already cover this here, that's why the
        # __dict__ case comes below
        try:
            if hasattr(obj, '__slots__'):
                for attr_name in new_obj.__slots__:
                    setattr(
                        new_obj,
                        attr_name,
                        cls._replace_bot(
                            cls._replace_bot(getattr(new_obj, attr_name), memo), memo
                        ),
                    )
                memo[obj_id] = new_obj
                return new_obj
            if hasattr(obj, '__dict__'):
                for attr_name, attr in new_obj.__dict__.items():
                    setattr(new_obj, attr_name, cls._replace_bot(attr, memo))
                memo[obj_id] = new_obj
                return new_obj
        except Exception as exception:
            warnings.warn(
                f'Parsing of an object failed with the following exception: {exception}. '
                f'See the docs of BasePersistence.replace_bot for more information.',
                RuntimeWarning,
            )
            memo[obj_id] = obj
            return obj

        return obj

    def insert_bot(self, obj: object) -> object:
        """
        Replaces all instances of :attr:`REPLACED_BOT` that occur within the passed object with
        :attr:`bot`. Currently, this handles objects of type ``list``, ``tuple``, ``set``,
        ``frozenset``, ``dict``, ``defaultdict`` and objects that have a ``__dict__`` or
        ``__slots__`` attribute, excluding classes and objects that can't be copied with
        ``copy.copy``. If the parsing of an object fails, the object will be returned unchanged and
        the error will be logged.

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
        if isinstance(obj, type):
            # classes usually do have a __dict__, but it's not writable
            warnings.warn(
                'BasePersistence.insert_bot does not handle classes. See '
                'the docs of BasePersistence.insert_bot for more information.',
                RuntimeWarning,
            )
            return obj

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
        # if '__dict__' in obj.__slots__, we already cover this here, that's why the
        # __dict__ case comes below
        try:
            if hasattr(obj, '__slots__'):
                for attr_name in obj.__slots__:
                    setattr(
                        new_obj,
                        attr_name,
                        self._insert_bot(
                            self._insert_bot(getattr(new_obj, attr_name), memo), memo
                        ),
                    )
                memo[obj_id] = new_obj
                return new_obj
            if hasattr(obj, '__dict__'):
                for attr_name, attr in new_obj.__dict__.items():
                    setattr(new_obj, attr_name, self._insert_bot(attr, memo))
                memo[obj_id] = new_obj
                return new_obj
        except Exception as exception:
            warnings.warn(
                f'Parsing of an object failed with the following exception: {exception}. '
                f'See the docs of BasePersistence.insert_bot for more information.',
                RuntimeWarning,
            )
            memo[obj_id] = obj
            return obj

        return obj

    @abstractmethod
    def get_user_data(self) -> DefaultDict[int, UD]:
        """Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the ``user_data`` if stored, or an empty
        :obj:`defaultdict(telegram.ext.utils.types.UD)` with integer keys.

        Returns:
            DefaultDict[:obj:`int`, :class:`telegram.ext.utils.types.UD`]: The restored user data.
        """

    @abstractmethod
    def get_chat_data(self) -> DefaultDict[int, CD]:
        """Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the ``chat_data`` if stored, or an empty
        :obj:`defaultdict(telegram.ext.utils.types.CD)` with integer keys.

        Returns:
            DefaultDict[:obj:`int`, :class:`telegram.ext.utils.types.CD`]: The restored chat data.
        """

    @abstractmethod
    def get_bot_data(self) -> BD:
        """Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the ``bot_data`` if stored, or an empty
        :class:`telegram.ext.utils.types.BD`.

        Returns:
            :class:`telegram.ext.utils.types.BD`: The restored bot data.
        """

    def get_callback_data(self) -> Optional[CDCData]:
        """Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. If callback data was stored, it should be returned.

        .. versionadded:: 13.6

        Returns:
            Optional[:class:`telegram.ext.utils.types.CDCData`]: The restored meta data or
            :obj:`None`, if no data was stored.
        """
        raise NotImplementedError

    @abstractmethod
    def get_conversations(self, name: str) -> ConversationDict:
        """Will be called by :class:`telegram.ext.Dispatcher` when a
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
        """Will be called when a :class:`telegram.ext.ConversationHandler` changes states.
        This allows the storage of the new state in the persistence.

        Args:
            name (:obj:`str`): The handler's name.
            key (:obj:`tuple`): The key the state is changed for.
            new_state (:obj:`tuple` | :obj:`any`): The new state for the given key.
        """

    @abstractmethod
    def update_user_data(self, user_id: int, data: UD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:class:`telegram.ext.utils.types.UD`): The
                :attr:`telegram.ext.Dispatcher.user_data` ``[user_id]``.
        """

    @abstractmethod
    def update_chat_data(self, chat_id: int, data: CD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:class:`telegram.ext.utils.types.CD`): The
                :attr:`telegram.ext.Dispatcher.chat_data` ``[chat_id]``.
        """

    @abstractmethod
    def update_bot_data(self, data: BD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            data (:class:`telegram.ext.utils.types.BD`): The
                :attr:`telegram.ext.Dispatcher.bot_data`.
        """

    def refresh_user_data(self, user_id: int, user_data: UD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` before passing the
        :attr:`user_data` to a callback. Can be used to update data stored in :attr:`user_data`
        from an external source.

        .. versionadded:: 13.6

        Args:
            user_id (:obj:`int`): The user ID this :attr:`user_data` is associated with.
            user_data (:class:`telegram.ext.utils.types.UD`): The ``user_data`` of a single user.
        """

    def refresh_chat_data(self, chat_id: int, chat_data: CD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` before passing the
        :attr:`chat_data` to a callback. Can be used to update data stored in :attr:`chat_data`
        from an external source.

        .. versionadded:: 13.6

        Args:
            chat_id (:obj:`int`): The chat ID this :attr:`chat_data` is associated with.
            chat_data (:class:`telegram.ext.utils.types.CD`): The ``chat_data`` of a single chat.
        """

    def refresh_bot_data(self, bot_data: BD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` before passing the
        :attr:`bot_data` to a callback. Can be used to update data stored in :attr:`bot_data`
        from an external source.

        .. versionadded:: 13.6

        Args:
            bot_data (:class:`telegram.ext.utils.types.BD`): The ``bot_data``.
        """

    def update_callback_data(self, data: CDCData) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        .. versionadded:: 13.6

        Args:
            data (:class:`telegram.ext.utils.types.CDCData`): The relevant data to restore
                :class:`telegram.ext.CallbackDataCache`.
        """
        raise NotImplementedError

    def flush(self) -> None:
        """Will be called by :class:`telegram.ext.Updater` upon receiving a stop signal. Gives the
        persistence a chance to finish up saving or close a database connection gracefully.
        """

    REPLACED_BOT: ClassVar[str] = 'bot_instance_replaced_by_ptb_persistence'
    """:obj:`str`: Placeholder for :class:`telegram.Bot` instances replaced in saved data."""
