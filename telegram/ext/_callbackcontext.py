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
# pylint: disable=no-self-use
"""This module contains the CallbackContext class."""
from typing import TYPE_CHECKING, Coroutine, Dict, Generic, List, Match, NoReturn, Optional, Type

from telegram._callbackquery import CallbackQuery
from telegram._update import Update
from telegram.ext._extbot import ExtBot
from telegram.ext._utils.types import BD, BT, CD, UD

if TYPE_CHECKING:
    from asyncio import Queue
    from typing import Any

    from telegram.ext import Application, Job, JobQueue  # noqa: F401
    from telegram.ext._utils.types import CCT

_STORING_DATA_WIKI = (
    "https://github.com/python-telegram-bot/python-telegram-bot"
    "/wiki/Storing-bot%2C-user-and-chat-related-data"
)


class CallbackContext(Generic[BT, UD, CD, BD]):
    """
    This is a context object passed to the callback called by :class:`telegram.ext.BaseHandler`
    or by the :class:`telegram.ext.Application` in an error handler added by
    :attr:`telegram.ext.Application.add_error_handler` or to the callback of a
    :class:`telegram.ext.Job`.

    Note:
        :class:`telegram.ext.Application` will create a single context for an entire update. This
        means that if you got 2 handlers in different groups and they both get called, they will
        receive the same :class:`CallbackContext` object (of course with proper attributes like
        :attr:`matches` differing). This allows you to add custom attributes in a lower handler
        group callback, and then subsequently access those attributes in a higher handler group
        callback. Note that the attributes on :class:`CallbackContext` might change in the future,
        so make sure to use a fairly unique name for the attributes.

    Warning:
         Do not combine custom attributes with :paramref:`telegram.ext.BaseHandler.block` set to
         :obj:`False` or :attr:`telegram.ext.Application.concurrent_updates` set to
         :obj:`True`. Due to how those work, it will almost certainly execute the callbacks for an
         update out of order, and the attributes that you think you added will not be present.

    This class is a :class:`~typing.Generic` class and accepts four type variables:

    1. The type of :attr:`bot`. Must be :class:`telegram.Bot` or a subclass of that class.
    2. The type of :attr:`user_data` (if :attr:`user_data` is not :obj:`None`).
    3. The type of :attr:`chat_data` (if :attr:`chat_data` is not :obj:`None`).
    4. The type of :attr:`bot_data` (if :attr:`bot_data` is not :obj:`None`).

    .. seealso:: :attr:`telegram.ext.ContextTypes.DEFAULT_TYPE`

    Args:
        application (:class:`telegram.ext.Application`): The application associated with this
            context.
        chat_id (:obj:`int`, optional): The ID of the chat associated with this object. Used
            to provide :attr:`chat_data`.

            .. versionadded:: 20.0
        user_id (:obj:`int`, optional): The ID of the user associated with this object. Used
            to provide :attr:`user_data`.

            .. versionadded:: 20.0

    Attributes:
        coroutine (:term:`coroutine function`): Optional. Only present in error handlers if the
            error was caused by a coroutine run with :meth:`Application.create_task` or a handler
            callback with :attr:`block=False <BaseHandler.block>`.
        matches (List[:meth:`re.Match <re.Match.expand>`]): Optional. If the associated update
            originated from a :class:`filters.Regex`, this will contain a list of match objects for
            every pattern where ``re.search(pattern, string)`` returned a match. Note that filters
            short circuit, so combined regex filters will not always be evaluated.
        args (List[:obj:`str`]): Optional. Arguments passed to a command if the associated update
            is handled by :class:`telegram.ext.CommandHandler`, :class:`telegram.ext.PrefixHandler`
            or :class:`telegram.ext.StringCommandHandler`. It contains a list of the words in the
            text after the command, using any whitespace string as a delimiter.
        error (:exc:`Exception`): Optional. The error that was raised. Only present when passed
            to an error handler registered with :attr:`telegram.ext.Application.add_error_handler`.
        job (:class:`telegram.ext.Job`): Optional. The job which originated this callback.
            Only present when passed to the callback of :class:`telegram.ext.Job` or in error
            handlers if the error is caused by a job.

            .. versionchanged:: 20.0
                :attr:`job` is now also present in error handlers if the error is caused by a job.

    """

    __slots__ = (
        "_application",
        "_chat_id",
        "_user_id",
        "args",
        "matches",
        "error",
        "job",
        "coroutine",
        "__dict__",
    )

    def __init__(
        self: "CCT",
        application: "Application[BT, CCT, UD, CD, BD, Any]",
        chat_id: int = None,
        user_id: int = None,
    ):
        self._application = application
        self._chat_id = chat_id
        self._user_id = user_id
        self.args: Optional[List[str]] = None
        self.matches: Optional[List[Match]] = None
        self.error: Optional[Exception] = None
        self.job: Optional["Job"] = None
        self.coroutine: Optional[Coroutine] = None

    @property
    def application(self) -> "Application[BT, CCT, UD, CD, BD, Any]":
        """:class:`telegram.ext.Application`: The application associated with this context."""
        return self._application

    @property
    def bot_data(self) -> BD:
        """:obj:`ContextTypes.bot_data`: Optional. An object that can be used to keep any data in.
        For each update it will be the same :attr:`ContextTypes.bot_data`. Defaults to :obj:`dict`.
        """
        return self.application.bot_data

    @bot_data.setter
    def bot_data(self, value: object) -> NoReturn:
        raise AttributeError(
            f"You can not assign a new value to bot_data, see {_STORING_DATA_WIKI}"
        )

    @property
    def chat_data(self) -> Optional[CD]:
        """:obj:`ContextTypes.chat_data`: Optional. An object that can be used to keep any data in.
        For each update from the same chat id it will be the same :obj:`ContextTypes.chat_data`.
        Defaults to :obj:`dict`.

        Warning:
            When a group chat migrates to a supergroup, its chat id will change and the
            ``chat_data`` needs to be transferred. For details see our `wiki page
            <https://github.com/python-telegram-bot/python-telegram-bot/wiki/
            Storing-bot,-user-and-chat-related-data#chat-migration>`_.

        .. versionchanged:: 20.0
            The chat data is now also present in error handlers if the error is caused by a job.
        """
        if self._chat_id is not None:
            return self._application.chat_data[self._chat_id]
        return None

    @chat_data.setter
    def chat_data(self, value: object) -> NoReturn:
        raise AttributeError(
            f"You can not assign a new value to chat_data, see {_STORING_DATA_WIKI}"
        )

    @property
    def user_data(self) -> Optional[UD]:
        """:obj:`ContextTypes.user_data`: Optional. An object that can be used to keep any data in.
        For each update from the same user it will be the same :obj:`ContextTypes.user_data`.
        Defaults to :obj:`dict`.

        .. versionchanged:: 20.0
            The user data is now also present in error handlers if the error is caused by a job.
        """
        if self._user_id is not None:
            return self._application.user_data[self._user_id]
        return None

    @user_data.setter
    def user_data(self, value: object) -> NoReturn:
        raise AttributeError(
            f"You can not assign a new value to user_data, see {_STORING_DATA_WIKI}"
        )

    async def refresh_data(self) -> None:
        """If :attr:`application` uses persistence, calls
        :meth:`telegram.ext.BasePersistence.refresh_bot_data` on :attr:`bot_data`,
        :meth:`telegram.ext.BasePersistence.refresh_chat_data` on :attr:`chat_data` and
        :meth:`telegram.ext.BasePersistence.refresh_user_data` on :attr:`user_data`, if
        appropriate.

        Will be called by :meth:`telegram.ext.Application.process_update` and
        :meth:`telegram.ext.Job.run`.

        .. versionadded:: 13.6
        """
        if self.application.persistence:
            if self.application.persistence.store_data.bot_data:
                await self.application.persistence.refresh_bot_data(self.bot_data)
            if self.application.persistence.store_data.chat_data and self._chat_id is not None:
                await self.application.persistence.refresh_chat_data(
                    chat_id=self._chat_id, chat_data=self.chat_data
                )
            if self.application.persistence.store_data.user_data and self._user_id is not None:
                await self.application.persistence.refresh_user_data(
                    user_id=self._user_id, user_data=self.user_data
                )

    def drop_callback_data(self, callback_query: CallbackQuery) -> None:
        """
        Deletes the cached data for the specified callback query.

        .. versionadded:: 13.6

        Note:
            Will *not* raise exceptions in case the data is not found in the cache.
            *Will* raise :exc:`KeyError` in case the callback query can not be found in the cache.

        Args:
            callback_query (:class:`telegram.CallbackQuery`): The callback query.

        Raises:
            KeyError | RuntimeError: :exc:`KeyError`, if the callback query can not be found in
                the cache and :exc:`RuntimeError`, if the bot doesn't allow for arbitrary
                callback data.
        """
        if isinstance(self.bot, ExtBot):
            if not self.bot.arbitrary_callback_data:
                raise RuntimeError(
                    "This telegram.ext.ExtBot instance does not use arbitrary callback data."
                )
            self.bot.callback_data_cache.drop_data(callback_query)
        else:
            raise RuntimeError("telegram.Bot does not allow for arbitrary callback data.")

    @classmethod
    def from_error(
        cls: Type["CCT"],
        update: object,
        error: Exception,
        application: "Application[BT, CCT, UD, CD, BD, Any]",
        job: "Job" = None,
        coroutine: Coroutine = None,
    ) -> "CCT":
        """
        Constructs an instance of :class:`telegram.ext.CallbackContext` to be passed to the error
        handlers.

        .. seealso:: :meth:`telegram.ext.Application.add_error_handler`

        .. versionchanged:: 20.0
            Removed arguments ``async_args`` and ``async_kwargs``.

        Args:
            update (:obj:`object` | :class:`telegram.Update`): The update associated with the
                error. May be :obj:`None`, e.g. for errors in job callbacks.
            error (:obj:`Exception`): The error.
            application (:class:`telegram.ext.Application`): The application associated with this
                context.
            job (:class:`telegram.ext.Job`, optional): The job associated with the error.

                .. versionadded:: 20.0
            coroutine (:term:`coroutine function`, optional): The coroutine function associated
                with this error if the error was caused by a coroutine run with
                :meth:`Application.create_task` or a handler callback with
                :attr:`block=False <BaseHandler.block>`.

                .. versionadded:: 20.0

        Returns:
            :class:`telegram.ext.CallbackContext`
        """
        # update and job will never be present at the same time
        if update is not None:
            self = cls.from_update(update, application)
        elif job is not None:
            self = cls.from_job(job, application)
        else:
            self = cls(application)  # type: ignore

        self.error = error
        self.coroutine = coroutine
        return self

    @classmethod
    def from_update(
        cls: Type["CCT"],
        update: object,
        application: "Application[Any, CCT, Any, Any, Any, Any]",
    ) -> "CCT":
        """
        Constructs an instance of :class:`telegram.ext.CallbackContext` to be passed to the
        handlers.

        .. seealso:: :meth:`telegram.ext.Application.add_handler`

        Args:
            update (:obj:`object` | :class:`telegram.Update`): The update.
            application (:class:`telegram.ext.Application`): The application associated with this
                context.

        Returns:
            :class:`telegram.ext.CallbackContext`
        """
        if isinstance(update, Update):
            chat = update.effective_chat
            user = update.effective_user

            chat_id = chat.id if chat else None
            user_id = user.id if user else None

            return cls(application, chat_id=chat_id, user_id=user_id)  # type: ignore
        return cls(application)  # type: ignore

    @classmethod
    def from_job(
        cls: Type["CCT"],
        job: "Job",
        application: "Application[Any, CCT, Any, Any, Any, Any]",
    ) -> "CCT":
        """
        Constructs an instance of :class:`telegram.ext.CallbackContext` to be passed to a
        job callback.

        .. seealso:: :meth:`telegram.ext.JobQueue`

        Args:
            job (:class:`telegram.ext.Job`): The job.
            application (:class:`telegram.ext.Application`): The application associated with this
                context.

        Returns:
            :class:`telegram.ext.CallbackContext`
        """
        self = cls(application, chat_id=job.chat_id, user_id=job.user_id)  # type: ignore
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
    def bot(self) -> BT:
        """:class:`telegram.Bot`: The bot associated with this context."""
        return self._application.bot

    @property
    def job_queue(self) -> Optional["JobQueue"]:
        """
        :class:`telegram.ext.JobQueue`: The :class:`JobQueue` used by the
            :class:`telegram.ext.Application`.

        """
        return self._application.job_queue

    @property
    def update_queue(self) -> "Queue[object]":
        """
        :class:`asyncio.Queue`: The :class:`asyncio.Queue` instance used by the
            :class:`telegram.ext.Application` and (usually) the :class:`telegram.ext.Updater`
            associated with this context.

        """
        return self._application.update_queue

    @property
    def match(self) -> Optional[Match[str]]:
        """
        :meth:`re.Match <re.Match.expand>`: The first match from :attr:`matches`.
            Useful if you are only filtering using a single regex filter.
            Returns :obj:`None` if :attr:`matches` is empty.
        """
        try:
            return self.matches[0]  # type: ignore[index] # pylint: disable=unsubscriptable-object
        except (IndexError, TypeError):
            return None
