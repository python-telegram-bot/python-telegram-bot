#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2021
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
"""This module contains the Builder classes for the telegram.ext module."""
from abc import ABC
from queue import Queue
from threading import Event
from typing import TypeVar, Generic, Type, TYPE_CHECKING, Callable, Any, Dict, Union

from telegram import Bot
from telegram.ext.utils.types import CCT, UD, CD, BD
from telegram.utils.helpers import DefaultValue, DEFAULT_NONE
from telegram.utils.request import Request

if TYPE_CHECKING:
    from telegram.ext import (
        Defaults,
        BasePersistence,
        JobQueue,
        Dispatcher,
        ContextTypes,
        CallbackContext,
        ExtBot,
        Updater,
    )

Cls = TypeVar('Cls')
CT = Callable[
    ['_BaseBuilder[Cls, CCT, Dict, Dict, Dict]', object],
    '_BaseBuilder[Cls, CCT, Dict, Dict, Dict]',
]
DefCCT = 'CallbackContext[Dict, Dict, Dict]'
DefBaseBuilder = '_BaseBuilder[Cls, DefCCT, Dict, Dict, Dict]'
InputType = TypeVar('InputType')
Undefined = Union[DefaultValue[None], InputType]


def _check_if_already_set(func: CT) -> CT:
    def _decorator(self: DefBaseBuilder, arg: object) -> DefBaseBuilder:
        arg_name = func.__name__.strip('_')
        if getattr(self, f'__{arg_name}') is not DEFAULT_NONE:
            raise self._exception_builder(arg_name)
        return func(self, arg)

    return _decorator


_BOT_CHECKS = [
    ('dispatcher', 'Dispatcher instance'),
    ('request', 'Request instance'),
    ('request_kwargs', 'request_kwargs'),
    ('base_file_url', 'base_file_url'),
    ('base_url', 'base_url'),
    ('token', 'token'),
    ('defaults', 'Defaults instance'),
    ('arbitrary_callback_data', 'arbitrary_callback_data'),
    ('private_key', 'private_key'),
    ('private_key_password', 'private_key_password'),
]

_DISPATCHER_CHECKS = [
    ('update_queue', 'update_queue'),
    ('workers', 'workers'),
    ('exception_event', 'exeception_event'),
    ('job_queue', 'JobQueue instance'),
    ('persistence', 'persistence instance'),
    ('context_types', 'ContextTypes instance'),
] + _BOT_CHECKS


# Base class for all builders. We do this mainly to reduce code duplication, because e.g.
# the UpdaterBuilder has all method that the DispatcherBuilder has
class _BaseBuilder(Generic[Cls, CCT, UD, CD, BD], ABC):
    def __init__(
        self: DefBaseBuilder,
        cls: Type[Cls],
    ):
        self.__cls = cls

        self.__token: Undefined[str] = DEFAULT_NONE
        self.__base_url: Undefined[str] = DEFAULT_NONE
        self.__base_file_url: Undefined[str] = DEFAULT_NONE
        self.__request_kwargs: Undefined[Dict[str, Any]] = DEFAULT_NONE
        self.__request: Undefined['Request'] = DEFAULT_NONE
        self.__private_key: Undefined[bytes] = DEFAULT_NONE
        self.__private_key_password: Undefined[bytes] = DEFAULT_NONE
        self.__defaults: Undefined['Defaults'] = DEFAULT_NONE
        self.__arbitrary_callback_data: Undefined[Union[bool, int]] = DEFAULT_NONE
        self.__bot: Undefined[Bot] = DEFAULT_NONE
        self.__update_queue: Undefined[Queue] = DEFAULT_NONE
        self.__workers: Undefined[int] = DEFAULT_NONE
        self.__exception_event: Undefined[Event] = DEFAULT_NONE
        self.__job_queue: Undefined['JobQueue'] = DEFAULT_NONE
        self.__persistence: Undefined[BasePersistence] = DEFAULT_NONE
        self.__context_types: Undefined[ContextTypes[CCT, UD, CD, BD]] = DEFAULT_NONE
        self.__dispatcher: Undefined['Dispatcher'] = DEFAULT_NONE
        self.__user_sig_handler: Undefined[Callable[[int, object], Any]] = DEFAULT_NONE

    def _build_bot(self) -> ExtBot:
        if self.__token is DEFAULT_NONE:
            raise RuntimeError('No bot token was set.')
        return ExtBot(
            token=self.__token,  # type: ignore[arg-type]
            base_url=self.__base_url or 'https://api.telegram.org/bot',
            base_file_url=self.__base_file_url or 'https://api.telegram.org/file/bot',
            private_key=self.__private_key or None,  # type: ignore[arg-type]
            private_key_password=self.__private_key_password or None,  # type: ignore[arg-type]
            defaults=self.__defaults or '',  # type: ignore[arg-type]
            arbitrary_callback_data=self.__arbitrary_callback_data or '',  # type: ignore[arg-type]
        )

    def _build_dispatcher(self) -> Dispatcher:
        job_queue = JobQueue() if self.__job_queue is DEFAULT_NONE else self.__job_queue

        dispatcher = Dispatcher(
            bot=self.__bot or self._build_bot(),
            update_queue=self.__update_queue or Queue(),
            workers=self.__workers or 4,
            exception_event=self.__exception_event or Event(),
            job_queue=job_queue,
            persistence=self.__persistence or None,
        )

        if isinstance(job_queue, JobQueue):
            job_queue.set_dispatcher(dispatcher)

        return dispatcher

    def _build_updater(self) -> Updater:
        if self.__dispatcher is DEFAULT_NONE:
            dispatcher = self._build_dispatcher()
            return Updater(dispatcher=dispatcher)
        if self.__dispatcher:
            return Updater(dispatcher=self.__dispatcher)
        return Updater(
            bot=self.__bot or self._build_bot(), update_queue=self.__update_queue or Queue()
        )

    @staticmethod
    def _exception_builder(arg_1: str, arg_2: str = None) -> RuntimeError:
        if not arg_2:
            return RuntimeError(f'The parameter `{arg_1}` was already set.')
        return RuntimeError(f'The parameter `{arg_1}` can only be set, if the no {arg_2} was set.')

    @_check_if_already_set
    def _token(self, token: str) -> DefBaseBuilder:
        if self.__bot:
            raise self._exception_builder('token', 'bot instance')
        if self.__dispatcher:
            raise self._exception_builder('token', 'Dispatcher instance')
        self.__token = token
        return self

    @_check_if_already_set
    def _base_url(self, base_url: str) -> DefBaseBuilder:
        if self.__bot:
            raise self._exception_builder('base_url', 'bot instance')
        self.__base_url = base_url
        return self

    @_check_if_already_set
    def _base_file_url(self, base_file_url: str) -> DefBaseBuilder:
        if self.__bot:
            raise self._exception_builder('_base_file_url', 'bot instance')
        self.__base_file_url = base_file_url
        return self

    @_check_if_already_set
    def _request_kwargs(self, request_kwargs: Dict[str, Any]) -> DefBaseBuilder:
        if self.__request:
            raise self._exception_builder('request_kwargs', 'Request instance')
        if self.__bot:
            raise self._exception_builder('request_kwargs', 'bot instance')
        self.__request_kwargs = request_kwargs
        return self

    @_check_if_already_set
    def _request(self, request: Request) -> DefBaseBuilder:
        if self.__request_kwargs:
            raise self._exception_builder('request', 'request_kwargs')
        if self.__bot:
            raise self._exception_builder('request', 'bot instance')
        self.__request = request
        return self

    @_check_if_already_set
    def _private_key(self, private_key: bytes) -> DefBaseBuilder:
        if self.__bot:
            raise self._exception_builder('private_key', 'bot instance')
        self.__private_key = private_key
        return self

    @_check_if_already_set
    def _private_key_password(self, private_key_password: bytes) -> DefBaseBuilder:
        if self.__bot:
            raise self._exception_builder('private_key_password', 'bot instance')
        self.__private_key_password = private_key_password
        return self

    @_check_if_already_set
    def _defaults(self, defaults: Defaults) -> DefBaseBuilder:
        if self.__bot:
            raise self._exception_builder('defaults', 'bot instance')
        self.__defaults = defaults
        return self

    @_check_if_already_set
    def _arbitrary_callback_data(
        self, arbitrary_callback_data: Union[bool, int]
    ) -> DefBaseBuilder:
        if self.__bot:
            raise self._exception_builder('arbitrary_callback_data', 'bot instance')
        self.__arbitrary_callback_data = arbitrary_callback_data
        return self

    @_check_if_already_set
    def _bot(self, bot: Bot) -> DefBaseBuilder:
        for attr, error in _BOT_CHECKS:
            if getattr(self, f'__{attr}'):
                raise self._exception_builder('bot', error)
        self.__bot = bot
        return self

    @_check_if_already_set
    def _update_queue(self, update_queue: Queue) -> DefBaseBuilder:
        if self.__dispatcher:
            raise self._exception_builder('update_queue', 'Dispatcher instance')
        self.__update_queue = update_queue
        return self

    @_check_if_already_set
    def _workers(self, workers: int) -> DefBaseBuilder:
        if self.__dispatcher:
            raise self._exception_builder('workers', 'Dispatcher instance')
        self.__workers = workers
        return self

    @_check_if_already_set
    def _exception_event(self, exception_event: Event) -> DefBaseBuilder:
        if self.__dispatcher:
            raise self._exception_builder('exception_event', 'Dispatcher instance')
        self.__exception_event = exception_event
        return self

    @_check_if_already_set
    def _job_queue(self, job_queue: JobQueue) -> DefBaseBuilder:
        if self.__dispatcher:
            raise self._exception_builder('job_queue', 'Dispatcher instance')
        self.__job_queue = job_queue
        return self

    @_check_if_already_set
    def _persistence(self, persistence: BasePersistence) -> DefBaseBuilder:
        if self.__dispatcher:
            raise self._exception_builder('persistence', 'Dispatcher instance')
        self.__persistence = persistence
        return self

    @_check_if_already_set
    def _context_types(
        self, context_types: ContextTypes[CCT, UD, CD, BD]
    ) -> '_BaseBuilder[Cls, ContextTypes[CCT, UD, CD, BD], UD, CD, BD]':
        if self.__dispatcher:
            raise self._exception_builder('context_types', 'Dispatcher instance')
        self.__context_types = context_types
        return self

    @_check_if_already_set
    def _dispatcher(self, dispatcher: Dispatcher) -> DefBaseBuilder:
        for attr, error in _DISPATCHER_CHECKS:
            if getattr(self, f'__{attr}'):
                raise self._exception_builder('dispatcher', error)
        self.__dispatcher = dispatcher
        return self

    @_check_if_already_set
    def _user_sig_handler(self, user_sig_handler: Callable[[int, object], Any]) -> DefBaseBuilder:
        if self.__dispatcher:
            raise self._exception_builder('user_sig_handler', 'Dispatcher instance')
        self.__user_sig_handler = user_sig_handler
        return self
