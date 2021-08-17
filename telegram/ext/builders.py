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
#
# Some of the type hints are just ridiculously long ...
# flake8: noqa: E501
# pylint: disable=C0301
"""This module contains the Builder classes for the telegram.ext module."""
from queue import Queue
from threading import Event
from typing import (
    TypeVar,
    Generic,
    TYPE_CHECKING,
    Callable,
    Any,
    Dict,
    Union,
    Optional,
    overload,
    cast,
)

from telegram import Bot
from telegram.ext import Dispatcher, JobQueue, Updater, ExtBot
from telegram.ext.utils.types import CCT, UD, CD, BD, BT, DefaultContextType, JQ, PT
from telegram.utils.request import Request

if TYPE_CHECKING:
    from telegram.ext import (
        Defaults,
        BasePersistence,
        ContextTypes,
        CallbackContext,
    )

# Type hinting is a bit complicated here because we try to get to a sane level of
# leveraging generics and therefore need a number of type variables.
ODT = TypeVar('ODT', bound=Union[None, Dispatcher])
DT = TypeVar('DT', bound=Dispatcher)
InputBT = TypeVar('InputBT', bound=Bot)
InputJQ = TypeVar('InputJQ', bound=Union[None, JobQueue])
InputPT = TypeVar('InputPT', bound=Union[None, 'BasePersistence'])
InputDT = TypeVar('InputDT', bound=Union[None, Dispatcher])
InputCCT = TypeVar('InputCCT', bound='CallbackContext')
InputUD = TypeVar('InputUD')
InputCD = TypeVar('InputCD')
InputBD = TypeVar('InputBD')
DefCCT = DefaultContextType  # type: ignore[misc]
BuilderType = TypeVar('BuilderType', bound='_BaseBuilder')
CT = TypeVar('CT', bound=Callable[..., Any])

if TYPE_CHECKING:
    InitBaseBuilder = _BaseBuilder[  # noqa: F821  # pylint: disable=E0601
        Dispatcher[ExtBot, DefCCT, Dict, Dict, Dict, JobQueue, None],
        ExtBot,
        DefCCT,
        Dict,
        Dict,
        Dict,
        JobQueue,
        None,
    ]


def _check_if_already_set(func: CT) -> CT:
    def _decorator(self, arg):  # type: ignore[no-untyped-def]
        arg_name = func.__name__.strip('_')
        if getattr(self, f'__{arg_name}_was_set') is True:
            raise self._exception_builder(arg_name)  # pylint: disable=W0212
        return func(self, arg)

    return cast(CT, _decorator)


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
    ('exception_event', 'exception_event'),
    ('job_queue', 'JobQueue instance'),
    ('persistence', 'persistence instance'),
    ('context_types', 'ContextTypes instance'),
] + _BOT_CHECKS


# Base class for all builders. We do this mainly to reduce code duplication, because e.g.
# the UpdaterBuilder has all method that the DispatcherBuilder has
class _BaseBuilder(Generic[ODT, BT, CCT, UD, CD, BD, JQ, PT]):
    # pylint reports false positives here:
    # pylint: disable=W0238

    def __init__(self: 'InitBaseBuilder'):
        # Instead of the *_was_set variables, we could work with e.g. __token = DEFAULT_NONE.
        # However, this would make type hinting a *lot* more involved and reasonable type hinting
        # accuracy is valuable for the builder classes.

        self.__token: str = ''
        self.__token_was_set = False
        self.__base_url: str = 'https://api.telegram.org/bot'
        self.__base_url_was_set = False
        self.__base_file_url: str = 'https://api.telegram.org/file/bot'
        self.__base_file_url_was_set = False
        self.__request_kwargs: Dict[str, Any] = {}
        self.__request_kwargs_was_set = False
        self.__request: Optional['Request'] = None
        self.__request_was_set = False
        self.__private_key: Optional[bytes] = None
        self.__private_key_was_set = False
        self.__private_key_password: Optional[bytes] = None
        self.__private_key_password_was_set = False
        self.__defaults: Optional['Defaults'] = None
        self.__defaults_was_set = False
        self.__arbitrary_callback_data: Union[bool, int] = False
        self.__arbitrary_callback_data_was_set = False
        self.__bot: Bot = None  # type: ignore[assignment]
        self.__bot_was_set = False
        self.__update_queue: Queue = Queue()
        self.__update_queue_was_set = False
        self.__workers: int = 4
        self.__workers_was_set = False
        self.__exception_event: Event = Event()
        self.__exception_event_was_set = False
        self.__job_queue: Optional['JobQueue'] = JobQueue()
        self.__job_queue_was_set = False
        self.__persistence: Optional['BasePersistence'] = None
        self.__persistence_was_set = False
        self.__context_types: Optional['ContextTypes'] = None
        self.__context_types_was_set = False
        self.__dispatcher: Optional['Dispatcher'] = None
        self.__dispatcher_was_set = False
        self.__user_sig_handler: Optional[Callable[[int, object], Any]] = None
        self.__user_sig_handler_was_set = False

    def _build_bot(self) -> Bot:
        if self.__token_was_set is False:
            raise RuntimeError('No bot token was set.')
        return Bot(
            token=self.__token,
            base_url=self.__base_url,
            base_file_url=self.__base_file_url,
            private_key=self.__private_key,
            private_key_password=self.__private_key_password,
        )

    def _build_ext_bot(self) -> ExtBot:
        if self.__token_was_set is False:
            raise RuntimeError('No bot token was set.')
        return ExtBot(
            token=self.__token,
            base_url=self.__base_url,
            base_file_url=self.__base_file_url,
            private_key=self.__private_key,
            private_key_password=self.__private_key_password,
            defaults=self.__defaults,
            arbitrary_callback_data=self.__arbitrary_callback_data,
        )

    def _build_dispatcher(
        self: '_BaseBuilder[ODT, BT, CCT, UD, CD, BD, JQ, PT]',
    ) -> Dispatcher[BT, CCT, UD, CD, BD, JQ, PT]:
        job_queue = JobQueue() if self.__job_queue_was_set is False else self.__job_queue

        dispatcher: Dispatcher[BT, CCT, UD, CD, BD, JQ, PT] = Dispatcher(
            bot=self.__bot if self.__bot_was_set is False else self._build_ext_bot(),
            update_queue=self.__update_queue,
            workers=self.__workers,
            exception_event=self.__exception_event,
            job_queue=job_queue,
            persistence=self.__persistence,
            builder_flag=True,
        )

        if isinstance(job_queue, JobQueue):
            job_queue.set_dispatcher(dispatcher)

        return dispatcher

    def _build_updater(
        self: '_BaseBuilder[ODT, BT, Any, Any, Any, Any, Any, Any]',
    ) -> Updater[BT, ODT]:
        if self.__dispatcher_was_set is False:
            dispatcher = self._build_dispatcher()
            return Updater(
                dispatcher=dispatcher,
                builder_flag=True,
            )
        return Updater(
            dispatcher=self.__dispatcher,
            bot=self.__bot or self._build_ext_bot(),
            update_queue=self.__update_queue,
            builder_flag=True,
        )

    @staticmethod
    def _exception_builder(arg_1: str, arg_2: str = None) -> RuntimeError:
        if not arg_2:
            return RuntimeError(f'The parameter `{arg_1}` was already set.')
        return RuntimeError(f'The parameter `{arg_1}` can only be set, if the no {arg_2} was set.')

    @_check_if_already_set
    def _token(self: BuilderType, token: str) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('token', 'bot instance')
        if self.__dispatcher:
            raise self._exception_builder('token', 'Dispatcher instance')
        self.__token = token
        self.__token_was_set = True
        return self

    @_check_if_already_set
    def _base_url(self: BuilderType, base_url: str) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('base_url', 'bot instance')
        self.__base_url = base_url
        self.__base_url_was_set = True
        return self

    @_check_if_already_set
    def _base_file_url(self: BuilderType, base_file_url: str) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('_base_file_url', 'bot instance')
        self.__base_file_url = base_file_url
        self.__base_file_url_was_set = True
        return self

    @_check_if_already_set
    def _request_kwargs(self: BuilderType, request_kwargs: Dict[str, Any]) -> BuilderType:
        if self.__request:
            raise self._exception_builder('request_kwargs', 'Request instance')
        if self.__bot:
            raise self._exception_builder('request_kwargs', 'bot instance')
        self.__request_kwargs = request_kwargs
        self.__request_kwargs_was_set = True
        return self

    @_check_if_already_set
    def _request(self: BuilderType, request: Request) -> BuilderType:
        if self.__request_kwargs:
            raise self._exception_builder('request', 'request_kwargs')
        if self.__bot:
            raise self._exception_builder('request', 'bot instance')
        self.__request = request
        self.__request_was_set = True
        return self

    @_check_if_already_set
    def _private_key(self: BuilderType, private_key: bytes) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('private_key', 'bot instance')
        self.__private_key = private_key
        self.__private_key_was_set = True
        return self

    @_check_if_already_set
    def _private_key_password(self: BuilderType, private_key_password: bytes) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('private_key_password', 'bot instance')
        self.__private_key_password = private_key_password
        self.__private_key_password_was_set = True
        return self

    @_check_if_already_set
    def _defaults(self: BuilderType, defaults: 'Defaults') -> BuilderType:
        if self.__bot:
            raise self._exception_builder('defaults', 'bot instance')
        self.__defaults = defaults
        self.__defaults_was_set = True
        return self

    @_check_if_already_set
    def _arbitrary_callback_data(
        self: BuilderType, arbitrary_callback_data: Union[bool, int]
    ) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('arbitrary_callback_data', 'bot instance')
        self.__arbitrary_callback_data = arbitrary_callback_data
        self.__arbitrary_callback_data_was_set = True
        return self

    @_check_if_already_set
    def _bot(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, '
        'JQ, PT]',
        bot: InputBT,
    ) -> '_BaseBuilder[Dispatcher[InputBT, CCT, UD, CD, BD, JQ, PT], InputBT, CCT, UD, CD, BD, JQ, PT]':
        for attr, error in _BOT_CHECKS:
            if getattr(self, f'__{attr}'):
                raise self._exception_builder('bot', error)
        self.__bot = bot
        self.__bot_was_set = True
        return self  # type: ignore[return-value]

    @_check_if_already_set
    def _update_queue(self: BuilderType, update_queue: Queue) -> BuilderType:
        if self.__dispatcher:
            raise self._exception_builder('update_queue', 'Dispatcher instance')
        self.__update_queue = update_queue
        self.__update_queue_was_set = True
        return self

    @_check_if_already_set
    def _workers(self: BuilderType, workers: int) -> BuilderType:
        if self.__dispatcher:
            raise self._exception_builder('workers', 'Dispatcher instance')
        self.__workers = workers
        self.__workers_was_set = True
        return self

    @_check_if_already_set
    def _exception_event(self: BuilderType, exception_event: Event) -> BuilderType:
        if self.__dispatcher:
            raise self._exception_builder('exception_event', 'Dispatcher instance')
        self.__exception_event = exception_event
        self.__exception_event_was_set = True
        return self

    @_check_if_already_set
    def _job_queue(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        job_queue: InputJQ,
    ) -> '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, InputJQ, PT], BT, CCT, UD, CD, BD, InputJQ, PT]':
        if self.__dispatcher:
            raise self._exception_builder('job_queue', 'Dispatcher instance')
        self.__job_queue = job_queue
        self.__job_queue_was_set = True
        return self  # type: ignore[return-value]

    @_check_if_already_set
    def _persistence(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        persistence: InputPT,
    ) -> '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, InputPT], BT, CCT, UD, CD, BD, JQ, InputPT]':
        if self.__dispatcher:
            raise self._exception_builder('persistence', 'Dispatcher instance')
        self.__persistence = persistence
        self.__persistence_was_set = True
        return self  # type: ignore[return-value]

    @_check_if_already_set
    def _context_types(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        context_types: 'ContextTypes[InputCCT, InputUD, InputCD, InputBD]',
    ) -> '_BaseBuilder[Dispatcher[BT, InputCCT, InputUD, InputCD, InputBD, JQ, PT], BT, InputCCT, InputUD, InputCD, InputBD, JQ, PT]':
        if self.__dispatcher:
            raise self._exception_builder('context_types', 'Dispatcher instance')
        self.__context_types = context_types
        self.__context_types_was_set = True
        return self  # type: ignore[return-value]

    @overload
    def _dispatcher(
        self: '_BaseBuilder[ODT, BT, CCT, UD, CD, BD, JQ, PT]', dispatcher: None
    ) -> '_BaseBuilder[None, BT, CCT, UD, CD, BD, JQ, PT]':
        ...

    @overload
    def _dispatcher(
        self: BuilderType, dispatcher: Dispatcher[BT, CCT, UD, CD, BD, JQ, PT]
    ) -> '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]':
        ...

    @_check_if_already_set  # type: ignore[misc]
    def _dispatcher(
        self: BuilderType, dispatcher: Optional[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT]]
    ) -> '_BaseBuilder[Optional[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT]], BT, CCT, UD, CD, BD, JQ, PT]':
        for attr, error in _DISPATCHER_CHECKS:
            if getattr(self, f'__{attr}'):
                raise self._exception_builder('dispatcher', error)
        self.__dispatcher = dispatcher
        self.__dispatcher_was_set = True
        return self

    @_check_if_already_set
    def _user_sig_handler(
        self: BuilderType, user_sig_handler: Callable[[int, object], Any]
    ) -> BuilderType:
        if self.__dispatcher:
            raise self._exception_builder('user_sig_handler', 'Dispatcher instance')
        self.__user_sig_handler = user_sig_handler
        self.__user_sig_handler_was_set = True
        return self
