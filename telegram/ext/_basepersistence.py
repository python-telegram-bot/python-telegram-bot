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
from typing import Dict, Optional, Tuple, Generic, NamedTuple

from telegram import Bot
from telegram.ext import ExtBot

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
    * :meth:`drop_chat_data`
    * :meth:`get_user_data`
    * :meth:`update_user_data`
    * :meth:`refresh_user_data`
    * :meth:`drop_user_data`
    * :meth:`get_callback_data`
    * :meth:`update_callback_data`
    * :meth:`get_conversations`
    * :meth:`update_conversation`
    * :meth:`flush`

    If you don't actually need one of those methods, a simple :keyword:`pass` is enough.
    For example, if you don't store ``bot_data``, you don't need :meth:`get_bot_data`,
    :meth:`update_bot_data` or :meth:`refresh_bot_data`.

    Note:
       You should avoid saving :class:`telegram.Bot` instances. This is because if you change e.g.
       the bots token, this won't propagate to the serialized instances and may lead to exceptions.

       To prevent this, the implementation may use :attr:`bot` to replace bot instances with a
       placeholder before serialization and insert :attr:`bot` back when loading the data.
       Since :attr:`bot` will be set when the process starts, this will be the up-to-date bot
       instance.

       If the persistence implementation does not take care of this, you should make sure not to
       store any bot instances in the data that will be persisted. E.g. in case of
       :class:`telegram.TelegramObject`, one may call :meth:`set_bot` to ensure that shortcuts like
       :meth:`telegram.Message.reply_text` are available.

    .. versionchanged:: 14.0
        * The parameters and attributes ``store_*_data`` were replaced by :attr:`store_data`.
        * ``insert/replace_bot`` was dropped. Serialization of bot instances now needs to be
          handled by the specific implementation - see above note.

    Args:
        store_data (:class:`PersistenceInput`, optional): Specifies which kinds of data will be
            saved by this persistence instance. By default, all available kinds of data will be
            saved.

    Attributes:
        store_data (:class:`PersistenceInput`): Specifies which kinds of data will be saved by this
            persistence instance.
        bot (:class:`telegram.Bot`): The bot associated with the persistence.
    """

    __slots__ = ('bot', 'store_data')

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
