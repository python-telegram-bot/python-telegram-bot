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
# pylint: disable=R0201
"""This module contains the CallbackContext class."""
from queue import Queue
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Match,
    NoReturn,
    Optional,
    Tuple,
    Union,
    Generic,
    Type,
    TypeVar,
)

from telegram import Update, CallbackQuery
from telegram.ext import ExtBot
from telegram.ext.utils.types import UD, CD, BD

if TYPE_CHECKING:
    from telegram import Bot
    from telegram.ext import Dispatcher, Job, JobQueue

CC = TypeVar('CC', bound='CallbackContext')


class CallbackContext(Generic[UD, CD, BD]):
    """
    This is a context object passed to the callback called by :class:`telegram.ext.Handler`
    or by the :class:`telegram.ext.Dispatcher` in an error handler added by
    :attr:`telegram.ext.Dispatcher.add_error_handler` or to the callback of a
    :class:`telegram.ext.Job`.

    Note:
        :class:`telegram.ext.Dispatcher` will create a single context for an entire update. This
        means that if you got 2 handlers in different groups and they both get called, they will
        get passed the same `CallbackContext` object (of course with proper attributes like
        `.matches` differing). This allows you to add custom attributes in a lower handler group
        callback, and then subsequently access those attributes in a higher handler group callback.
        Note that the attributes on `CallbackContext` might change in the future, so make sure to
        use a fairly unique name for the attributes.

    Warning:
         Do not combine custom attributes and ``@run_async``/
         :meth:`telegram.ext.Disptacher.run_async`. Due to how ``run_async`` works, it will
         almost certainly execute the callbacks for an update out of order, and the attributes
         that you think you added will not be present.

    Args:
        dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher associated with this context.

    Attributes:
        matches (List[:obj:`re match object`]): Optional. If the associated update originated from
            a regex-supported handler or had a :class:`Filters.regex`, this will contain a list of
            match objects for every pattern where ``re.search(pattern, string)`` returned a match.
            Note that filters short circuit, so combined regex filters will not always
            be evaluated.
        args (List[:obj:`str`]): Optional. Arguments passed to a command if the associated update
            is handled by :class:`telegram.ext.CommandHandler`, :class:`telegram.ext.PrefixHandler`
            or :class:`telegram.ext.StringCommandHandler`. It contains a list of the words in the
            text after the command, using any whitespace string as a delimiter.
        error (:obj:`Exception`): Optional. The error that was raised. Only present when passed
            to a error handler registered with :attr:`telegram.ext.Dispatcher.add_error_handler`.
        async_args (List[:obj:`object`]): Optional. Positional arguments of the function that
            raised the error. Only present when the raising function was run asynchronously using
            :meth:`telegram.ext.Dispatcher.run_async`.
        async_kwargs (Dict[:obj:`str`, :obj:`object`]): Optional. Keyword arguments of the function
            that raised the error. Only present when the raising function was run asynchronously
            using :meth:`telegram.ext.Dispatcher.run_async`.
        job (:class:`telegram.ext.Job`): Optional. The job which originated this callback.
            Only present when passed to the callback of :class:`telegram.ext.Job`.

    """

    __slots__ = (
        '_dispatcher',
        '_chat_id_and_data',
        '_user_id_and_data',
        'args',
        'matches',
        'error',
        'job',
        'async_args',
        'async_kwargs',
        '__dict__',
    )

    def __init__(self, dispatcher: 'Dispatcher'):
        """
        Args:
            dispatcher (:class:`telegram.ext.Dispatcher`):
        """
        if not dispatcher.use_context:
            raise ValueError(
                'CallbackContext should not be used with a non context aware ' 'dispatcher!'
            )
        self._dispatcher = dispatcher
        self._chat_id_and_data: Optional[Tuple[int, CD]] = None
        self._user_id_and_data: Optional[Tuple[int, UD]] = None
        self.args: Optional[List[str]] = None
        self.matches: Optional[List[Match]] = None
        self.error: Optional[Exception] = None
        self.job: Optional['Job'] = None
        self.async_args: Optional[Union[List, Tuple]] = None
        self.async_kwargs: Optional[Dict[str, object]] = None

    @property
    def dispatcher(self) -> 'Dispatcher':
        """:class:`telegram.ext.Dispatcher`: The dispatcher associated with this context."""
        return self._dispatcher

    @property
    def bot_data(self) -> BD:
        """:obj:`dict`: Optional. A dict that can be used to keep any data in. For each
        update it will be the same ``dict``.
        """
        return self.dispatcher.bot_data

    @bot_data.setter
    def bot_data(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to bot_data, see https://git.io/Jt6ic"
        )

    @property
    def chat_data(self) -> Optional[CD]:
        """:obj:`dict`: Optional. A dict that can be used to keep any data in. For each
        update from the same chat id it will be the same ``dict``.

        Warning:
            When a group chat migrates to a supergroup, its chat id will change and the
            ``chat_data`` needs to be transferred. For details see our `wiki page
            <https://github.com/python-telegram-bot/python-telegram-bot/wiki/
            Storing-bot,-user-and-chat-related-data#chat-migration>`_.
        """
        if self._chat_id_and_data:
            return self._chat_id_and_data[1]
        return None

    @chat_data.setter
    def chat_data(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to chat_data, see https://git.io/Jt6ic"
        )

    @property
    def user_data(self) -> Optional[UD]:
        """:obj:`dict`: Optional. A dict that can be used to keep any data in. For each
        update from the same user it will be the same ``dict``.
        """
        if self._user_id_and_data:
            return self._user_id_and_data[1]
        return None

    @user_data.setter
    def user_data(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to user_data, see https://git.io/Jt6ic"
        )

    def refresh_data(self) -> None:
        """If :attr:`dispatcher` uses persistence, calls
        :meth:`telegram.ext.BasePersistence.refresh_bot_data` on :attr:`bot_data`,
        :meth:`telegram.ext.BasePersistence.refresh_chat_data` on :attr:`chat_data` and
        :meth:`telegram.ext.BasePersistence.refresh_user_data` on :attr:`user_data`, if
        appropriate.

        .. versionadded:: 13.6
        """
        if self.dispatcher.persistence:
            if self.dispatcher.persistence.store_bot_data:
                self.dispatcher.persistence.refresh_bot_data(self.bot_data)
            if self.dispatcher.persistence.store_chat_data and self._chat_id_and_data is not None:
                self.dispatcher.persistence.refresh_chat_data(*self._chat_id_and_data)
            if self.dispatcher.persistence.store_user_data and self._user_id_and_data is not None:
                self.dispatcher.persistence.refresh_user_data(*self._user_id_and_data)

    def drop_callback_data(self, callback_query: CallbackQuery) -> None:
        """
        Deletes the cached data for the specified callback query.

        .. versionadded:: 13.6

        Note:
            Will *not* raise exceptions in case the data is not found in the cache.
            *Will* raise :class:`KeyError` in case the callback query can not be found in the
            cache.

        Args:
            callback_query (:class:`telegram.CallbackQuery`): The callback query.

        Raises:
            KeyError | RuntimeError: :class:`KeyError`, if the callback query can not be found in
                the cache and :class:`RuntimeError`, if the bot doesn't allow for arbitrary
                callback data.
        """
        if isinstance(self.bot, ExtBot):
            if not self.bot.arbitrary_callback_data:
                raise RuntimeError(
                    'This telegram.ext.ExtBot instance does not use arbitrary callback data.'
                )
            self.bot.callback_data_cache.drop_data(callback_query)
        else:
            raise RuntimeError('telegram.Bot does not allow for arbitrary callback data.')

    @classmethod
    def from_error(
        cls: Type[CC],
        update: object,
        error: Exception,
        dispatcher: 'Dispatcher',
        async_args: Union[List, Tuple] = None,
        async_kwargs: Dict[str, object] = None,
    ) -> CC:
        """
        Constructs an instance of :class:`telegram.ext.CallbackContext` to be passed to the error
        handlers.

        .. seealso:: :meth:`telegram.ext.Dispatcher.add_error_handler`

        Args:
            update (:obj:`object` | :class:`telegram.Update`): The update associated with the
                error. May be :obj:`None`, e.g. for errors in job callbacks.
            error (:obj:`Exception`): The error.
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher associated with this
                context.
            async_args (List[:obj:`object`]): Optional. Positional arguments of the function that
                raised the error. Pass only when the raising function was run asynchronously using
                :meth:`telegram.ext.Dispatcher.run_async`.
            async_kwargs (Dict[:obj:`str`, :obj:`object`]): Optional. Keyword arguments of the
                function that raised the error. Pass only when the raising function was run
                asynchronously using :meth:`telegram.ext.Dispatcher.run_async`.

        Returns:
            :class:`telegram.ext.CallbackContext`
        """
        self = cls.from_update(update, dispatcher)
        self.error = error
        self.async_args = async_args
        self.async_kwargs = async_kwargs
        return self

    @classmethod
    def from_update(cls: Type[CC], update: object, dispatcher: 'Dispatcher') -> CC:
        """
        Constructs an instance of :class:`telegram.ext.CallbackContext` to be passed to the
        handlers.

        .. seealso:: :meth:`telegram.ext.Dispatcher.add_handler`

        Args:
            update (:obj:`object` | :class:`telegram.Update`): The update.
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher associated with this
                context.

        Returns:
            :class:`telegram.ext.CallbackContext`
        """
        self = cls(dispatcher)

        if update is not None and isinstance(update, Update):
            chat = update.effective_chat
            user = update.effective_user

            if chat:
                self._chat_id_and_data = (
                    chat.id,
                    dispatcher.chat_data[chat.id],  # pylint: disable=W0212
                )
            if user:
                self._user_id_and_data = (
                    user.id,
                    dispatcher.user_data[user.id],  # pylint: disable=W0212
                )
        return self

    @classmethod
    def from_job(cls: Type[CC], job: 'Job', dispatcher: 'Dispatcher') -> CC:
        """
        Constructs an instance of :class:`telegram.ext.CallbackContext` to be passed to a
        job callback.

        .. seealso:: :meth:`telegram.ext.JobQueue`

        Args:
            job (:class:`telegram.ext.Job`): The job.
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher associated with this
                context.

        Returns:
            :class:`telegram.ext.CallbackContext`
        """
        self = cls(dispatcher)
        self.job = job
        return self

    def update(self, data: Dict[str, object]) -> None:
        """Updates ``self.__slots__`` with the passed data.

        Args:
            data (Dict[:obj:`str`, :obj:`object`]): The data.
        """
        for key, value in data.items():
            setattr(self, key, value)

    @property
    def bot(self) -> 'Bot':
        """:class:`telegram.Bot`: The bot associated with this context."""
        return self._dispatcher.bot

    @property
    def job_queue(self) -> Optional['JobQueue']:
        """
        :class:`telegram.ext.JobQueue`: The ``JobQueue`` used by the
            :class:`telegram.ext.Dispatcher` and (usually) the :class:`telegram.ext.Updater`
            associated with this context.

        """
        return self._dispatcher.job_queue

    @property
    def update_queue(self) -> Queue:
        """
        :class:`queue.Queue`: The ``Queue`` instance used by the
            :class:`telegram.ext.Dispatcher` and (usually) the :class:`telegram.ext.Updater`
            associated with this context.

        """
        return self._dispatcher.update_queue

    @property
    def match(self) -> Optional[Match[str]]:
        """
        `Regex match type`: The first match from :attr:`matches`.
            Useful if you are only filtering using a single regex filter.
            Returns `None` if :attr:`matches` is empty.
        """
        try:
            return self.matches[0]  # type: ignore[index] # pylint: disable=unsubscriptable-object
        except (IndexError, TypeError):
            return None
