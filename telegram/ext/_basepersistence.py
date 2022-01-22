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
"""This module contains the BasePersistence class."""
from abc import ABC, abstractmethod
from copy import copy
from typing import Dict, Optional, Tuple, cast, ClassVar, Generic, NamedTuple

from telegram import Bot
from telegram.ext import ExtBot

from telegram.warnings import PTBRuntimeWarning
from telegram._utils.warnings import warn
from telegram.ext._utils.types import UD, CD, BD, ConversationDict, CDCData


class PersistenceInput(NamedTuple):  # skipcq: PYL-E0239
    """Convenience wrapper to group boolean input for :class:`BasePersistence`.

    Args:
        bot_data (:obj:`bool`, optional): Whether the setting should be applied for ``bot_data``.
            Defaults to :obj:`True`.
        chat_data (:obj:`bool`, optional): Whether the setting should be applied for ``chat_data``.
            Defaults to :obj:`True`.
        user_data (:obj:`bool`, optional): Whether the setting should be applied for ``user_data``.
            Defaults to :obj:`True`.
        callback_data (:obj:`bool`, optional): Whether the setting should be applied for
            ``callback_data``. Defaults to :obj:`True`.

    Attributes:
        bot_data (:obj:`bool`): Whether the setting should be applied for ``bot_data``.
        chat_data (:obj:`bool`): Whether the setting should be applied for ``chat_data``.
        user_data (:obj:`bool`): Whether the setting should be applied for ``user_data``.
        callback_data (:obj:`bool`): Whether the setting should be applied for ``callback_data``.

    """

    bot_data: bool = True
    chat_data: bool = True
    user_data: bool = True
    callback_data: bool = True


class BasePersistence(Generic[UD, CD, BD], ABC):
    """Interface class for adding persistence to your bot.
    Subclass this object for different implementations of a persistent bot.

    Attention:
        The interface provided by this class is intended to be accessed exclusively by
        :class:`~telegram.ext.Dispatcher`. Calling any of the methods below manually might
        interfere with the integration of persistence into :class:`~telegram.ext.Dispatcher`.

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
    you don't store ``bot_data``, you don't need :meth:`get_bot_data`, :meth:`update_bot_data` or
    :meth:`refresh_bot_data`.

    Warning:
        Persistence will try to replace :class:`telegram.Bot` instances by :attr:`REPLACED_BOT` and
        insert the bot set with :meth:`set_bot` upon loading of the data. This is to ensure that
        changes to the bot apply to the saved objects, too. If you change the bots token, this may
        lead to e.g. ``Chat not found`` errors. For the limitations on replacing bots see
        :meth:`replace_bot` and :meth:`insert_bot`.

    Note:
         :meth:`replace_bot` and :meth:`insert_bot` are used *independently* of the implementation
         of the ``update/get_*`` methods, i.e. you don't need to worry about it while
         implementing a custom persistence subclass.

    .. versionchanged:: 14.0
        The parameters and attributes ``store_*_data`` were replaced by :attr:`store_data`.

    Args:
        store_data (:class:`PersistenceInput`, optional): Specifies which kinds of data will be
            saved by this persistence instance. By default, all available kinds of data will be
            saved.

    Attributes:
        store_data (:class:`PersistenceInput`): Specifies which kinds of data will be saved by this
            persistence instance.
    """

    __slots__ = (
        'bot',
        'store_data',
        '__dict__',  # __dict__ is included because we replace methods in the __new__
    )

    def __new__(
        cls, *args: object, **kwargs: object  # pylint: disable=unused-argument
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

        def get_user_data_insert_bot() -> Dict[int, UD]:
            return instance.insert_bot(get_user_data())

        def get_chat_data_insert_bot() -> Dict[int, CD]:
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

        # Adds to __dict__
        setattr(instance, 'get_user_data', get_user_data_insert_bot)
        setattr(instance, 'get_chat_data', get_chat_data_insert_bot)
        setattr(instance, 'get_bot_data', get_bot_data_insert_bot)
        setattr(instance, 'get_callback_data', get_callback_data_insert_bot)
        setattr(instance, 'update_user_data', update_user_data_replace_bot)
        setattr(instance, 'update_chat_data', update_chat_data_replace_bot)
        setattr(instance, 'update_bot_data', update_bot_data_replace_bot)
        setattr(instance, 'update_callback_data', update_callback_data_replace_bot)
        return instance

    def __init__(self, store_data: PersistenceInput = None):
        self.store_data = store_data or PersistenceInput()

        self.bot: Bot = None  # type: ignore[assignment]

    def set_bot(self, bot: Bot) -> None:
        """Set the Bot to be used by this persistence instance.

        Args:
            bot (:class:`telegram.Bot`): The bot.
        """
        if self.store_data.callback_data and not isinstance(bot, ExtBot):
            raise TypeError('callback_data can only be stored when using telegram.ext.ExtBot.')

        self.bot = bot

    @classmethod
    def replace_bot(cls, obj: object) -> object:
        """
        Replaces all instances of :class:`telegram.Bot` that occur within the passed object with
        :attr:`REPLACED_BOT`. Currently, this handles objects of type :class:`list`,
        :class:`tuple`, :class:`set`, :class:`frozenset`, :class:`dict`,
        :class:`collections.defaultdict` and objects that have a :attr:`~object.__dict__` or
        :data:`~object.__slots__` attribute, excluding classes and objects that can't be copied
        with :func:`copy.copy`. If the parsing of an object fails, the object will be returned
        unchanged and the error will be logged.

        Args:
            obj (:obj:`object`): The object

        Returns:
            :class:`object`: Copy of the object with Bot instances replaced.
        """
        return cls._replace_bot(obj, {})

    @classmethod
    def _replace_bot(  # pylint: disable=too-many-return-statements
        cls, obj: object, memo: Dict[int, object]
    ) -> object:
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
            warn(
                f'BasePersistence.replace_bot does not handle classes such as {obj.__name__!r}. '
                'See the docs of BasePersistence.replace_bot for more information.',
                PTBRuntimeWarning,
            )
            return obj

        try:
            new_obj = copy(obj)
            memo[obj_id] = new_obj
        except Exception:
            warn(
                'BasePersistence.replace_bot does not handle objects that can not be copied. See '
                'the docs of BasePersistence.replace_bot for more information.',
                PTBRuntimeWarning,
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
                if '__dict__' in obj.__slots__:
                    # In this case, we have already covered the case that obj has __dict__
                    # Note that obj may have a __dict__ even if it's not in __slots__!
                    memo[obj_id] = new_obj
                    return new_obj
            if hasattr(obj, '__dict__'):
                for attr_name, attr in new_obj.__dict__.items():
                    setattr(new_obj, attr_name, cls._replace_bot(attr, memo))
                memo[obj_id] = new_obj
                return new_obj
        except Exception as exception:
            warn(
                f'Parsing of an object failed with the following exception: {exception}. '
                f'See the docs of BasePersistence.replace_bot for more information.',
                PTBRuntimeWarning,
            )

        memo[obj_id] = obj
        return obj

    def insert_bot(self, obj: object) -> object:
        """
        Replaces all instances of :attr:`REPLACED_BOT` that occur within the passed object with
        :paramref:`bot`. Currently, this handles objects of type :class:`list`,
        :class:`tuple`, :class:`set`, :class:`frozenset`, :class:`dict`,
        :class:`collections.defaultdict` and objects that have a :attr:`~object.__dict__` or
        :data:`~object.__slots__` attribute, excluding classes and objects that can't be copied
        with :func:`copy.copy`. If the parsing of an object fails, the object will be returned
        unchanged and the error will be logged.

        Args:
            obj (:obj:`object`): The object

        Returns:
            :class:`object`: Copy of the object with Bot instances inserted.
        """
        return self._insert_bot(obj, {})

    # pylint: disable=too-many-return-statements
    def _insert_bot(self, obj: object, memo: Dict[int, object]) -> object:
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
            warn(
                f'BasePersistence.insert_bot does not handle classes such as {obj.__name__!r}. '
                'See the docs of BasePersistence.insert_bot for more information.',
                PTBRuntimeWarning,
            )
            return obj

        try:
            new_obj = copy(obj)
        except Exception:
            warn(
                'BasePersistence.insert_bot does not handle objects that can not be copied. See '
                'the docs of BasePersistence.insert_bot for more information.',
                PTBRuntimeWarning,
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
                if '__dict__' in obj.__slots__:
                    # In this case, we have already covered the case that obj has __dict__
                    # Note that obj may have a __dict__ even if it's not in __slots__!
                    memo[obj_id] = new_obj
                    return new_obj
            if hasattr(obj, '__dict__'):
                for attr_name, attr in new_obj.__dict__.items():
                    setattr(new_obj, attr_name, self._insert_bot(attr, memo))
                memo[obj_id] = new_obj
                return new_obj
        except Exception as exception:
            warn(
                f'Parsing of an object failed with the following exception: {exception}. '
                f'See the docs of BasePersistence.insert_bot for more information.',
                PTBRuntimeWarning,
            )

        memo[obj_id] = obj
        return obj

    @abstractmethod
    def get_user_data(self) -> Dict[int, UD]:
        """Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the ``user_data`` if stored, or an empty
        :obj:`dict`. In the latter case, the dictionary should produce values
        corresponding to one of the following:

          * :obj:`dict`
          * The type from :attr:`telegram.ext.ContextTypes.user_data`
            if :class:`telegram.ext.ContextTypes` is used.

        .. versionchanged:: 14.0
            This method may now return a :obj:`dict` instead of a :obj:`collections.defaultdict`

        Returns:
            Dict[:obj:`int`, :obj:`dict` | :attr:`telegram.ext.ContextTypes.user_data`]:
                The restored user data.
        """

    @abstractmethod
    def get_chat_data(self) -> Dict[int, CD]:
        """Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the ``chat_data`` if stored, or an empty
        :obj:`dict`. In the latter case, the dictionary should produce values
        corresponding to one of the following:

          * :obj:`dict`
          * The type from :attr:`telegram.ext.ContextTypes.chat_data`
            if :class:`telegram.ext.ContextTypes` is used.

        .. versionchanged:: 14.0
            This method may now return a :obj:`dict` instead of a :obj:`collections.defaultdict`

        Returns:
            Dict[:obj:`int`, :obj:`dict` | :attr:`telegram.ext.ContextTypes.chat_data`]:
                The restored chat data.
        """

    @abstractmethod
    def get_bot_data(self) -> BD:
        """Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. It should return the ``bot_data`` if stored, or an empty
        :obj:`dict`. In the latter case, the :obj:`dict` should produce values
        corresponding to one of the following:

          * :obj:`dict`
          * The type from :attr:`telegram.ext.ContextTypes.bot_data`
            if :class:`telegram.ext.ContextTypes` are used.

        Returns:
            Dict[:obj:`int`, :obj:`dict` | :attr:`telegram.ext.ContextTypes.bot_data`]:
                The restored bot data.
        """

    @abstractmethod
    def get_callback_data(self) -> Optional[CDCData]:
        """Will be called by :class:`telegram.ext.Dispatcher` upon creation with a
        persistence object. If callback data was stored, it should be returned.

        .. versionadded:: 13.6

        .. versionchanged:: 14.0
           Changed this method into an ``@abstractmethod``.

        Returns:
            Optional[Tuple[List[Tuple[:obj:`str`, :obj:`float`, \
                Dict[:obj:`str`, :class:`object`]]], Dict[:obj:`str`, :obj:`str`]]]:
                The restored meta data or :obj:`None`, if no data was stored.
        """

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
            new_state (:obj:`tuple` | :class:`object`): The new state for the given key.
        """

    @abstractmethod
    def update_user_data(self, user_id: int, data: UD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:obj:`dict` | :attr:`telegram.ext.ContextTypes.user_data`):
                The :attr:`telegram.ext.Dispatcher.user_data` ``[user_id]``.
        """

    @abstractmethod
    def update_chat_data(self, chat_id: int, data: CD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:obj:`dict` | :attr:`telegram.ext.ContextTypes.chat_data`):
                The :attr:`telegram.ext.Dispatcher.chat_data` ``[chat_id]``.
        """

    @abstractmethod
    def update_bot_data(self, data: BD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        Args:
            data (:obj:`dict` | :attr:`telegram.ext.ContextTypes.bot_data`):
                The :attr:`telegram.ext.Dispatcher.bot_data`.
        """

    @abstractmethod
    def update_callback_data(self, data: CDCData) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` after a handler has
        handled an update.

        .. versionadded:: 13.6

        .. versionchanged:: 14.0
           Changed this method into an ``@abstractmethod``.

        Args:
            data (Optional[Tuple[List[Tuple[:obj:`str`, :obj:`float`, \
                Dict[:obj:`str`, :obj:`Any`]]], Dict[:obj:`str`, :obj:`str`]]]):
                The relevant data to restore :class:`telegram.ext.CallbackDataCache`.
        """

    @abstractmethod
    def drop_chat_data(self, chat_id: int) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher`, when using
        :meth:`~telegram.ext.Dispatcher.drop_chat_data`.

        .. versionadded:: 14.0

        Args:
            chat_id (:obj:`int`): The chat id to delete from the persistence.
        """

    @abstractmethod
    def drop_user_data(self, user_id: int) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher`, when using
        :meth:`~telegram.ext.Dispatcher.drop_user_data`.

        .. versionadded:: 14.0

        Args:
            user_id (:obj:`int`): The user id to delete from the persistence.
        """

    @abstractmethod
    def refresh_user_data(self, user_id: int, user_data: UD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` before passing the
        :attr:`~telegram.ext.Dispatcher.user_data` to a callback. Can be used to update data stored
        in :attr:`~telegram.ext.Dispatcher.user_data` from an external source.

        .. versionadded:: 13.6

        .. versionchanged:: 14.0
           Changed this method into an ``@abstractmethod``.

        Args:
            user_id (:obj:`int`): The user ID this :attr:`~telegram.ext.Dispatcher.user_data` is
                associated with.
            user_data (:obj:`dict` | :attr:`telegram.ext.ContextTypes.user_data`):
                The ``user_data`` of a single user.
        """

    @abstractmethod
    def refresh_chat_data(self, chat_id: int, chat_data: CD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` before passing the
        :attr:`~telegram.ext.Dispatcher.chat_data` to a callback. Can be used to update data stored
        in :attr:`~telegram.ext.Dispatcher.chat_data` from an external source.

        .. versionadded:: 13.6

        .. versionchanged:: 14.0
           Changed this method into an ``@abstractmethod``.

        Args:
            chat_id (:obj:`int`): The chat ID this :attr:`~telegram.ext.Dispatcher.chat_data` is
                associated with.
            chat_data (:obj:`dict` | :attr:`telegram.ext.ContextTypes.chat_data`):
                The ``chat_data`` of a single chat.
        """

    @abstractmethod
    def refresh_bot_data(self, bot_data: BD) -> None:
        """Will be called by the :class:`telegram.ext.Dispatcher` before passing the
        :attr:`~telegram.ext.Dispatcher.bot_data` to a callback. Can be used to update data stored
        in :attr:`~telegram.ext.Dispatcher.bot_data` from an external source.

        .. versionadded:: 13.6

        .. versionchanged:: 14.0
           Changed this method into an ``@abstractmethod``.

        Args:
            bot_data (:obj:`dict` | :attr:`telegram.ext.ContextTypes.bot_data`):
                The ``bot_data``.
        """

    @abstractmethod
    def flush(self) -> None:
        """Will be called by :class:`telegram.ext.Updater` upon receiving a stop signal. Gives the
        persistence a chance to finish up saving or close a database connection gracefully.

        .. versionchanged:: 14.0
           Changed this method into an ``@abstractmethod``.
        """

    REPLACED_BOT: ClassVar[str] = 'bot_instance_replaced_by_ptb_persistence'
    """:obj:`str`: Placeholder for :class:`telegram.Bot` instances replaced in saved data."""
