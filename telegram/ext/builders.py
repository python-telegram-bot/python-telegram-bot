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
InBT = TypeVar('InBT', bound=Bot)
InJQ = TypeVar('InJQ', bound=Union[None, JobQueue])
InPT = TypeVar('InPT', bound=Union[None, 'BasePersistence'])
InDT = TypeVar('InDT', bound=Union[None, Dispatcher])
InCCT = TypeVar('InCCT', bound='CallbackContext')
InUD = TypeVar('InUD')
InCD = TypeVar('InCD')
InBD = TypeVar('InBD')
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
    InitUpdaterBuilder = UpdaterBuilder[  # noqa: F821  # pylint: disable=E0601
        Dispatcher[ExtBot, DefCCT, Dict, Dict, Dict, JobQueue, None],
        ExtBot,
        DefCCT,
        Dict,
        Dict,
        Dict,
        JobQueue,
        None,
    ]
    InitDispatcherBuilder = DispatcherBuilder[  # noqa: F821  # pylint: disable=E0601
        Dispatcher[ExtBot, DefCCT, Dict, Dict, Dict, JobQueue, None],
        ExtBot,
        DefCCT,
        Dict,
        Dict,
        Dict,
        JobQueue,
        None,
    ]


def check_if_already_set(func: CT) -> CT:
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
        self.__user_signal_handler: Optional[Callable[[int, object], Any]] = None
        self.__user_signal_handler_was_set = False

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

    @check_if_already_set
    def _token(self: BuilderType, token: str) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('token', 'bot instance')
        if self.__dispatcher:
            raise self._exception_builder('token', 'Dispatcher instance')
        self.__token = token
        self.__token_was_set = True
        return self

    @check_if_already_set
    def _base_url(self: BuilderType, base_url: str) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('base_url', 'bot instance')
        self.__base_url = base_url
        self.__base_url_was_set = True
        return self

    @check_if_already_set
    def _base_file_url(self: BuilderType, base_file_url: str) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('_base_file_url', 'bot instance')
        self.__base_file_url = base_file_url
        self.__base_file_url_was_set = True
        return self

    @check_if_already_set
    def _request_kwargs(self: BuilderType, request_kwargs: Dict[str, Any]) -> BuilderType:
        if self.__request:
            raise self._exception_builder('request_kwargs', 'Request instance')
        if self.__bot:
            raise self._exception_builder('request_kwargs', 'bot instance')
        self.__request_kwargs = request_kwargs
        self.__request_kwargs_was_set = True
        return self

    @check_if_already_set
    def _request(self: BuilderType, request: Request) -> BuilderType:
        if self.__request_kwargs:
            raise self._exception_builder('request', 'request_kwargs')
        if self.__bot:
            raise self._exception_builder('request', 'bot instance')
        self.__request = request
        self.__request_was_set = True
        return self

    @check_if_already_set
    def _private_key(self: BuilderType, private_key: bytes) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('private_key', 'bot instance')
        self.__private_key = private_key
        self.__private_key_was_set = True
        return self

    @check_if_already_set
    def _private_key_password(self: BuilderType, private_key_password: bytes) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('private_key_password', 'bot instance')
        self.__private_key_password = private_key_password
        self.__private_key_password_was_set = True
        return self

    @check_if_already_set
    def _defaults(self: BuilderType, defaults: 'Defaults') -> BuilderType:
        if self.__bot:
            raise self._exception_builder('defaults', 'bot instance')
        self.__defaults = defaults
        self.__defaults_was_set = True
        return self

    @check_if_already_set
    def _arbitrary_callback_data(
        self: BuilderType, arbitrary_callback_data: Union[bool, int]
    ) -> BuilderType:
        if self.__bot:
            raise self._exception_builder('arbitrary_callback_data', 'bot instance')
        self.__arbitrary_callback_data = arbitrary_callback_data
        self.__arbitrary_callback_data_was_set = True
        return self

    @check_if_already_set
    def _bot(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, '
        'JQ, PT]',
        bot: InBT,
    ) -> '_BaseBuilder[Dispatcher[InBT, CCT, UD, CD, BD, JQ, PT], InBT, CCT, UD, CD, BD, JQ, PT]':
        for attr, error in _BOT_CHECKS:
            if getattr(self, f'__{attr}'):
                raise self._exception_builder('bot', error)
        self.__bot = bot
        self.__bot_was_set = True
        return self  # type: ignore[return-value]

    @check_if_already_set
    def _update_queue(self: BuilderType, update_queue: Queue) -> BuilderType:
        if self.__dispatcher:
            raise self._exception_builder('update_queue', 'Dispatcher instance')
        self.__update_queue = update_queue
        self.__update_queue_was_set = True
        return self

    @check_if_already_set
    def _workers(self: BuilderType, workers: int) -> BuilderType:
        if self.__dispatcher:
            raise self._exception_builder('workers', 'Dispatcher instance')
        self.__workers = workers
        self.__workers_was_set = True
        return self

    @check_if_already_set
    def _exception_event(self: BuilderType, exception_event: Event) -> BuilderType:
        if self.__dispatcher:
            raise self._exception_builder('exception_event', 'Dispatcher instance')
        self.__exception_event = exception_event
        self.__exception_event_was_set = True
        return self

    @check_if_already_set
    def _job_queue(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        job_queue: InJQ,
    ) -> '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, InJQ, PT], BT, CCT, UD, CD, BD, InJQ, PT]':
        if self.__dispatcher:
            raise self._exception_builder('job_queue', 'Dispatcher instance')
        self.__job_queue = job_queue
        self.__job_queue_was_set = True
        return self  # type: ignore[return-value]

    @check_if_already_set
    def _persistence(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        persistence: InPT,
    ) -> '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, InPT], BT, CCT, UD, CD, BD, JQ, InPT]':
        if self.__dispatcher:
            raise self._exception_builder('persistence', 'Dispatcher instance')
        self.__persistence = persistence
        self.__persistence_was_set = True
        return self  # type: ignore[return-value]

    @check_if_already_set
    def _context_types(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        context_types: 'ContextTypes[InCCT, InUD, InCD, InBD]',
    ) -> '_BaseBuilder[Dispatcher[BT, InCCT, InUD, InCD, InBD, JQ, PT], BT, InCCT, InUD, InCD, InBD, JQ, PT]':
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
        self: BuilderType, dispatcher: Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]
    ) -> '_BaseBuilder[Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT], InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]':
        ...

    @check_if_already_set  # type: ignore[misc]
    def _dispatcher(
        self: BuilderType,
        dispatcher: Optional[Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]],
    ) -> '_BaseBuilder[Optional[Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]], InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]':
        for attr, error in _DISPATCHER_CHECKS:
            if getattr(self, f'__{attr}'):
                raise self._exception_builder('dispatcher', error)
        self.__dispatcher = dispatcher
        self.__dispatcher_was_set = True
        return self

    @check_if_already_set
    def _user_signal_handler(
        self: BuilderType, user_signal_handler: Callable[[int, object], Any]
    ) -> BuilderType:
        if self.__dispatcher:
            raise self._exception_builder('user_signal_handler', 'Dispatcher instance')
        self.__user_signal_handler = user_signal_handler
        self.__user_signal_handler_was_set = True
        return self


class DispatcherBuilder(_BaseBuilder[ODT, BT, CCT, UD, CD, BD, JQ, PT]):
    """This class serves as initializer for :class:`telegram.ext.Dispatcher` via the so called
    `builder pattern`_. To build a :class:`telegram.ext.Dispatcher`, one first initializes an
    instance of this class. Arguments for the :class:`telegram.ext.Dispatcher` to build are then
    added by subsequently calling the methods of the builder. Finally, the
    :class:`telegram.ext.Dispatcher` is built by calling :meth:`build`. In the simplest case this
    can look like the following example.

    Example:
        .. code:: python

            dispatcher = DispatcherBuilder().token('TOKEN').build()

    Please see the description of the individual methods for information on which arguments can be
    set and what the defaults are when not called. When no default is mentioned, the argument will
    not be used by default.

    Note:
        * Each method can be called at most once, e.g. you can't override arguments that were
          already set.
        * Some arguments are mutually exclusive. E.g. after calling :meth:`token`, you can't set
          a custom bot with :meth:`bot` and vice versa.
        * Unless a custom :class:`telegram.Bot` instance is set via :meth:`bot`, :meth:`build` will
          use :class:`telegram.ext.ExtBot` for the bot.

    .. seealso::
        :class:`telegram.ext.UpdaterBuilder`

    .. _`builder pattern`: https://en.wikipedia.org/wiki/Builder_pattern.
    """

    # The init is just here for mypy
    def __init__(self: 'InitDispatcherBuilder'):
        super().__init__()

    def build(
        self: 'DispatcherBuilder[ODT, BT, CCT, UD, CD, BD, JQ, PT]',
    ) -> Dispatcher[BT, CCT, UD, CD, BD, JQ, PT]:
        """Builds a :class:`telegram.ext.Dispatcher` with the provided arguments.

        Returns:
            :class:`telegram.ext.Dispatcher`
        """
        return self._build_dispatcher()

    def token(self: BuilderType, token: str) -> BuilderType:
        """Sets the token to be used for :attr:`telegram.ext.Dispatcher.bot`.

        Args:
            token (:obj:`str`): The token.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._token(token)

    def base_url(self: BuilderType, base_url: str) -> BuilderType:
        """Sets the base URL to be used for :attr:`telegram.ext.Dispatcher.bot`. If not called,
        will default to ``'https://api.telegram.org/bot'``.

        .. seealso:: :attr:`telegram.Bot.base_url`, `Local Bot API Server <https://github.com/\
            python-telegram-bot/python-telegram-bot/wiki/Local-Bot-API-Server>`_,
            :meth:`base_url`

        Args:
            base_url (:obj:`str`): The URL.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._base_url(base_url)

    def base_file_url(self: BuilderType, base_file_url: str) -> BuilderType:
        """Sets the base file URL to be used for :attr:`telegram.ext.Dispatcher.bot`. If not
        called, will default to ``'https://api.telegram.org/file/bot'``.

        .. seealso:: :attr:`telegram.Bot.base_file_url`, `Local Bot API Server <https://github.com\
            /python-telegram-bot/python-telegram-bot/wiki/Local-Bot-API-Server>`_,
            :meth:`base_file_url`

        Args:
            base_file_url (:obj:`str`): The URL.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._base_file_url(base_file_url)

    def request_kwargs(self: BuilderType, request_kwargs: Dict[str, Any]) -> BuilderType:
        """Sets keyword arguments that will be passed to the :class:`telegram.utils.Request` object
        that is created when :attr:`telegram.ext.Dispatcher.bot` is created. If not called, no
        keyword arguments will be passed.

        .. seealso:: :meth:`request`

        Args:
            request_kwargs (Dict[:obj:`str`, :obj:`object`]): The keyword arguments.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._request_kwargs(request_kwargs)

    def request(self: BuilderType, request: Request) -> BuilderType:
        """Sets a :class:`telegram.utils.Request` object to be used for
        :attr:`telegram.ext.Dispatcher.bot`.

        .. seealso:: :meth:`request_kwargs`

        Args:
            request (:class:`telegram.utils.Request`): The request object.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._request(request)

    def private_key(self: BuilderType, private_key: bytes) -> BuilderType:
        """Sets the private key for decryption of telegram passport data to be used for
        :attr:`telegram.ext.Dispatcher.bot`.

        .. seealso:: `passportbot.py <https://github.com/python-telegram-bot/python-telegram-bot\
            /tree/master/examples#passportbotpy>`_, `Telegram Passports <https://git.io/fAvYd>`_

        Note:
            Must be used together with :meth:`private_key_password`.

        Args:
            private_key (:obj:`bytes`): The private key.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._private_key(private_key)

    def private_key_password(self: BuilderType, private_key_password: bytes) -> BuilderType:
        """Sets the private key password for decryption of telegram passport data to be used for
        :attr:`telegram.ext.Dispatcher.bot`.

        .. seealso:: `passportbot.py <https://github.com/python-telegram-bot/python-telegram-bot\
            /tree/master/examples#passportbotpy>`_, `Telegram Passports <https://git.io/fAvYd>`_

        Note:
            Must be used together with :meth:`private_key`.

        Args:
            private_key_password (:obj:`bytes`): The private key password.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._private_key_password(private_key_password)

    def defaults(self: BuilderType, defaults: 'Defaults') -> BuilderType:
        """Sets the :class:`telegram.ext.Defaults` object to be used for
        :attr:`telegram.ext.Dispatcher.bot`.

        .. seealso:: `Adding Defaults <https://git.io/J0FGR>`_

        Args:
            defaults (:class:`telegram.ext.Defaults`): The defaults.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._defaults(defaults)

    def arbitrary_callback_data(
        self: BuilderType, arbitrary_callback_data: Union[bool, int]
    ) -> BuilderType:
        """Specifies whether :attr:`telegram.ext.Dispatcher.bot` should allow arbitrary objects as
        callback data for :class:`telegram.InlineKeyboardButton` and how many keyboards should be
        cached in memory. If not called, only strings can be used as callback data and no data will
        be stored in memory.

        .. seealso:: `Arbitrary callback_data <https://git.io/JGBDI>`_,
            `arbitrarycallbackdatabot.py <https://git.io/J0FBv>`_

        Args:
            arbitrary_callback_data (:obj:`bool` | :obj:`int`): If :obj:`True` is passed, the
                default cache size of 1024 will be used. Pass an integer to specify a different
                cache size.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._arbitrary_callback_data(arbitrary_callback_data)

    def bot(
        self: 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, '
        'JQ, PT]',
        bot: InBT,
    ) -> 'DispatcherBuilder[Dispatcher[InBT, CCT, UD, CD, BD, JQ, PT], InBT, CCT, UD, CD, BD, JQ, PT]':
        """Sets a :class:`telegram.Bot` instance to be used for
        :attr:`telegram.ext.Dispatcher.bot`. Instances of subclasses like
        :class:`telegram.ext.ExtBot` are also valid.

        Args:
            bot (:class:`telegram.Bot`): The bot.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._bot(bot)  # type: ignore[return-value]

    def update_queue(self: BuilderType, update_queue: Queue) -> BuilderType:
        """Sets a :class:`queue.Queue` instance to be used for
        :attr:`telegram.ext.Dispatcher.update_queue`, i.e. the queue that the dispatcher will fetch
        updates from. If not called, a queue will be instantiated.

         .. seealso:: :attr:`telegram.ext.Updater.update_queue`,
             :meth:`telegram.ext.UpdaterBuilder.update_queue`

        Args:
            update_queue (:class:`queue.Queue`): The queue.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._update_queue(update_queue)

    def workers(self: BuilderType, workers: int) -> BuilderType:
        """`Dummy text b/c this will be dropped anyway`"""
        return self._workers(workers)

    def exception_event(self: BuilderType, exception_event: Event) -> BuilderType:
        """Sets a :class:`threading.Event` instance to be used for
        :attr:`telegram.ext.Dispatcher.exception_event`. When this event is set, the dispatcher
        will stop processing updates. If not called, an event will be instantiated.

         .. seealso:: :attr:`telegram.ext.Updater.exception_event`,
             :meth:`telegram.ext.UpdaterBuilder.exception_event`

        Args:
            exception_event (:class:`threading.Event`): The event.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._exception_event(exception_event)

    def job_queue(
        self: 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        job_queue: InJQ,
    ) -> 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, InJQ, PT], BT, CCT, UD, CD, BD, InJQ, PT]':
        """Sets a :class:`telegram.ext.JobQueue` instance to be used for
        :attr:`telegram.ext.Dispatcher.job_queue`. If not called, a job queue will be instantiated.

        .. seealso:: `JobQueue <https://git.io/J0FCN>`_, `timerbot.py <https://git.io/J0FWf>`_

        Note:
            * :meth:`telegram.ext.JobQueue.set_dispatcher` will be called automatically by
              :meth:`build`.
            * The job queue will be automatically started and stopped by
              :meth:`telegram.ext.Dispatcher.start` and :meth:`telegram.ext.Dispatcher.stop`,
              respectively.
            * When passing :obj:`None`,
              :attr:`telegram.ext.ConversationHandler.conversation_timeout` can not be used, as
              this uses :attr:`telegram.ext.Dispatcher.job_queue` internally.

        Args:
            job_queue (:class:`telegram.ext.JobQueue`, optional): The job queue. Pass :obj:`None`
                if you don't want to use a job queue.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._job_queue(job_queue)  # type: ignore[return-value]

    def persistence(
        self: 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        persistence: InPT,
    ) -> 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, InPT], BT, CCT, UD, CD, BD, JQ, InPT]':
        """Sets a :class:`telegram.ext.BasePersistence` instance to be used for
        :attr:`telegram.ext.Dispatcher.persistence`.

        .. seealso:: `Making your bot persistent <https://git.io/J0FWM>`_,
            `persistentconversationbot.py <https://git.io/J0FW7>`_

        Warning:
            If a :class:`telegram.ext.ContextTypes` instance is set via :meth:`context_types`,
            the persistence instance must use the same types!

        Args:
            persistence (:class:`telegram.ext.BasePersistence`, optional): The persistence
                instance.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._persistence(persistence)  # type: ignore[return-value]

    def context_types(
        self: 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        context_types: 'ContextTypes[InCCT, InUD, InCD, InBD]',
    ) -> 'DispatcherBuilder[Dispatcher[BT, InCCT, InUD, InCD, InBD, JQ, PT], BT, InCCT, InUD, InCD, InBD, JQ, PT]':
        """Sets a :class:`telegram.ext.ContextTypes` instance to be used for
        :attr:`telegram.ext.Dispatcher.context_types`.

        .. seealso:: `contexttypesbot.py <https://git.io/J0F8d>`_

        Args:
            context_types (:class:`telegram.ext.ContextTypes`, optional): The context types.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._context_types(context_types)  # type: ignore[return-value]


class UpdaterBuilder(_BaseBuilder[ODT, BT, CCT, UD, CD, BD, JQ, PT]):
    """This class serves as initializer for :class:`telegram.ext.Updater` via the so called
    `builder pattern`_. To build an :class:`telegram.ext.Updater`, one first initializes an
    instance of this class. Arguments for the :class:`telegram.ext.Updater` to build are then
    added by subsequently calling the methods of the builder. Finally, the
    :class:`telegram.ext.Updater` is built by calling :meth:`build`. In the simplest case this
    can look like the following example.

    Example:
        .. code:: python

            dispatcher = UpdaterBuilder().token('TOKEN').build()

    Please see the description of the individual methods for information on which arguments can be
    set and what the defaults are when not called. When no default is mentioned, the argument will
    not be used by default.

    Note:
        * Each method can be called at most once, e.g. you can't override arguments that were
          already set.
        * Some arguments are mutually exclusive. E.g. after calling :meth:`token`, you can't set
          a custom bot with :meth:`bot` and vice versa.
        * Unless a custom :class:`telegram.Bot` instance is set via :meth:`bot`, :meth:`build` will
          use :class:`telegram.ext.ExtBot` for the bot.

    .. seealso::
        :class:`telegram.ext.DispatcherBuilder`

    .. _`builder pattern`: https://en.wikipedia.org/wiki/Builder_pattern.
    """

    # The init is just here for mypy
    def __init__(self: 'InitUpdaterBuilder'):
        super().__init__()

    def build(
        self: 'UpdaterBuilder[ODT, BT, Any, Any, Any, Any, Any, Any]',
    ) -> Updater[BT, ODT]:
        """Builds a :class:`telegram.ext.Updater` with the provided arguments.

        Returns:
            :class:`telegram.ext.Updater`
        """
        return self._build_updater()

    def token(self: BuilderType, token: str) -> BuilderType:
        """Sets the token to be used for :attr:`telegram.ext.Updater.bot`.

        Args:
            token (:obj:`str`): The token.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._token(token)

    def base_url(self: BuilderType, base_url: str) -> BuilderType:
        """Sets the base URL to be used for :attr:`telegram.ext.Updater.bot`. If not called,
        will default to ``'https://api.telegram.org/bot'``.

        .. seealso:: :attr:`telegram.Bot.base_url`, `Local Bot API Server <https://github.com/\
            python-telegram-bot/python-telegram-bot/wiki/Local-Bot-API-Server>`_,
            :meth:`base_url`

        Args:
            base_url (:obj:`str`): The URL.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._base_url(base_url)

    def base_file_url(self: BuilderType, base_file_url: str) -> BuilderType:
        """Sets the base file URL to be used for :attr:`telegram.ext.Updater.bot`. If not
        called, will default to ``'https://api.telegram.org/file/bot'``.

        .. seealso:: :attr:`telegram.Bot.base_file_url`, `Local Bot API Server <https://github.com\
            /python-telegram-bot/python-telegram-bot/wiki/Local-Bot-API-Server>`_,
            :meth:`base_file_url`

        Args:
            base_file_url (:obj:`str`): The URL.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._base_file_url(base_file_url)

    def request_kwargs(self: BuilderType, request_kwargs: Dict[str, Any]) -> BuilderType:
        """Sets keyword arguments that will be passed to the :class:`telegram.utils.Request` object
        that is created when :attr:`telegram.ext.Updater.bot` is created. If not called, no
        keyword arguments will be passed.

        .. seealso:: :meth:`request`

        Args:
            request_kwargs (Dict[:obj:`str`, :obj:`object`]): The keyword arguments.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._request_kwargs(request_kwargs)

    def request(self: BuilderType, request: Request) -> BuilderType:
        """Sets a :class:`telegram.utils.Request` object to be used for
        :attr:`telegram.ext.Updater.bot`.

        .. seealso:: :meth:`request_kwargs`

        Args:
            request (:class:`telegram.utils.Request`): The request object.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._request(request)

    def private_key(self: BuilderType, private_key: bytes) -> BuilderType:
        """Sets the private key for decryption of telegram passport data to be used for
        :attr:`telegram.ext.Updater.bot`.

        .. seealso:: `passportbot.py <https://github.com/python-telegram-bot/python-telegram-bot\
            /tree/master/examples#passportbotpy>`_, `Telegram Passports <https://git.io/fAvYd>`_

        Note:
            Must be used together with :meth:`private_key_password`.

        Args:
            private_key (:obj:`bytes`): The private key.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._private_key(private_key)

    def private_key_password(self: BuilderType, private_key_password: bytes) -> BuilderType:
        """Sets the private key password for decryption of telegram passport data to be used for
        :attr:`telegram.ext.Updater.bot`.

        .. seealso:: `passportbot.py <https://github.com/python-telegram-bot/python-telegram-bot\
            /tree/master/examples#passportbotpy>`_, `Telegram Passports <https://git.io/fAvYd>`_

        Note:
            Must be used together with :meth:`private_key`.

        Args:
            private_key_password (:obj:`bytes`): The private key password.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._private_key_password(private_key_password)

    def defaults(self: BuilderType, defaults: 'Defaults') -> BuilderType:
        """Sets the :class:`telegram.ext.Defaults` object to be used for
        :attr:`telegram.ext.Updater.bot`.

        .. seealso:: `Adding Defaults <https://git.io/J0FGR>`_

        Args:
            defaults (:class:`telegram.ext.Defaults`): The defaults.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._defaults(defaults)

    def arbitrary_callback_data(
        self: BuilderType, arbitrary_callback_data: Union[bool, int]
    ) -> BuilderType:
        """Specifies whether :attr:`telegram.ext.Updater.bot` should allow arbitrary objects as
        callback data for :class:`telegram.InlineKeyboardButton` and how many keyboards should be
        cached in memory. If not called, only strings can be used as callback data and no data will
        be stored in memory.

        .. seealso:: `Arbitrary callback_data <https://git.io/JGBDI>`_,
            `arbitrarycallbackdatabot.py <https://git.io/J0FBv>`_

        Args:
            arbitrary_callback_data (:obj:`bool` | :obj:`int`): If :obj:`True` is passed, the
                default cache size of 1024 will be used. Pass an integer to specify a different
                cache size.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._arbitrary_callback_data(arbitrary_callback_data)

    def bot(
        self: 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, '
        'JQ, PT]',
        bot: InBT,
    ) -> 'UpdaterBuilder[Dispatcher[InBT, CCT, UD, CD, BD, JQ, PT], InBT, CCT, UD, CD, BD, JQ, PT]':
        """Sets a :class:`telegram.Bot` instance to be used for
        :attr:`telegram.ext.Updater.bot`. Instances of subclasses like
        :class:`telegram.ext.ExtBot` are also valid.

        Args:
            bot (:class:`telegram.Bot`): The bot.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._bot(bot)  # type: ignore[return-value]

    def update_queue(self: BuilderType, update_queue: Queue) -> BuilderType:
        """Sets a :class:`queue.Queue` instance to be used for
        :attr:`telegram.ext.Updater.update_queue`, i.e. the queue that the fetched updates will
        be queued into. If not called, a queue will be instantiated.
        If :meth:`dispatcher` is not called, this queue will also be used for
        :attr:`telegram.ext.Dispatcher.update_queue`.

         .. seealso:: :attr:`telegram.ext.Dispatcher.update_queue`,
             :meth:`telegram.ext.DispatcherBuilder.update_queue`

        Args:
            update_queue (:class:`queue.Queue`): The queue.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._update_queue(update_queue)

    def workers(self: BuilderType, workers: int) -> BuilderType:
        """`Dummy text b/c this will be dropped anyway`"""
        return self._workers(workers)

    def exception_event(self: BuilderType, exception_event: Event) -> BuilderType:
        """Sets a :class:`threading.Event` instance to be used by the
        :class:`telegram.ext.Updater`. When an exception happens while fetching updates, this event
        will be set and the ``Updater`` will stop fetching for updates. If not called, an event
        will be instantiated.
        If :meth:`dispatcher` is not called, this event will also be used for
        :attr:`telegram.ext.Dispatcher.exception_event`.

         .. seealso:: :attr:`telegram.ext.Dispatcher.exception_event`,
             :meth:`telegram.ext.DispatcherBuilder.exception_event`

        Args:
            exception_event (:class:`threading.Event`): The event.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._exception_event(exception_event)

    def job_queue(
        self: 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        job_queue: InJQ,
    ) -> 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, InJQ, PT], BT, CCT, UD, CD, BD, InJQ, PT]':
        """Sets a :class:`telegram.ext.JobQueue` instance to be used for the
        :attr:`telegram.ext.Updater.dispatcher`. If not called, a job queue will be instantiated.

        .. seealso:: `JobQueue <https://git.io/J0FCN>`_, `timerbot.py <https://git.io/J0FWf>`_,
            :attr:`telegram.ext.Dispatcher.job_queue`

        Note:
            * :meth:`telegram.ext.JobQueue.set_dispatcher` will be called automatically by
              :meth:`build`.
            * The job queue will be automatically started/stopped by starting/stopping the
              ``Updater``, which automatically calls :meth:`telegram.ext.Dispatcher.start`
              and :meth:`telegram.ext.Dispatcher.stop`, respectively.
            * When passing :obj:`None`,
              :attr:`telegram.ext.ConversationHandler.conversation_timeout` can not be used, as
              this uses :attr:`telegram.ext.Dispatcher.job_queue` internally.

        Args:
            job_queue (:class:`telegram.ext.JobQueue`, optional): The job queue. Pass :obj:`None`
                if you don't want to use a job queue.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._job_queue(job_queue)  # type: ignore[return-value]

    def persistence(
        self: 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        persistence: InPT,
    ) -> 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, InPT], BT, CCT, UD, CD, BD, JQ, InPT]':
        """Sets a :class:`telegram.ext.BasePersistence` instance to be used for the
        :attr:`telegram.ext.Updater.dispatcher`.

        .. seealso:: `Making your bot persistent <https://git.io/J0FWM>`_,
            `persistentconversationbot.py <https://git.io/J0FW7>`_,
            :attr:`telegram.ext.Dispatcher.persistence`

        Warning:
            If a :class:`telegram.ext.ContextTypes` instance is set via :meth:`context_types`,
            the persistence instance must use the same types!

        Args:
            persistence (:class:`telegram.ext.BasePersistence`, optional): The persistence
                instance.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._persistence(persistence)  # type: ignore[return-value]

    def context_types(
        self: 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        context_types: 'ContextTypes[InCCT, InUD, InCD, InBD]',
    ) -> 'UpdaterBuilder[Dispatcher[BT, InCCT, InUD, InCD, InBD, JQ, PT], BT, InCCT, InUD, InCD, InBD, JQ, PT]':
        """Sets a :class:`telegram.ext.ContextTypes` instance to be used for the
        :attr:`telegram.ext.Updater.dispatcher`.

        .. seealso:: `contexttypesbot.py <https://git.io/J0F8d>`_,
            :attr:`telegram.ext.Dispatcher.context_types`.

        Args:
            context_types (:class:`telegram.ext.ContextTypes`, optional): The context types.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._context_types(context_types)  # type: ignore[return-value]

    @overload
    def dispatcher(
        self: 'UpdaterBuilder[ODT, BT, CCT, UD, CD, BD, JQ, PT]', dispatcher: None
    ) -> 'UpdaterBuilder[None, BT, CCT, UD, CD, BD, JQ, PT]':
        ...

    @overload
    def dispatcher(
        self: BuilderType, dispatcher: Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]
    ) -> 'UpdaterBuilder[Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT], InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]':
        ...

    def dispatcher(  # type: ignore[misc]
        self: BuilderType,
        dispatcher: Optional[Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]],
    ) -> 'UpdaterBuilder[Optional[Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]], InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]':
        """Sets a :class:`telegram.ext.Dispatcher` instance to be used for
        :attr:`telegram.ext.Updater.dispatcher`. If not called, a queue will be instantiated.
        The dispatchers :attr:`telegram.ext.Dispatcher.bot`,
        :attr:`telegram.ext.Dispatcher.update_queue` and
        :attr:`telegram.ext.Dispatcher.exception_event` will be used for the respective arguments
        of the updater.
        If not called, a dispatcher will be instantiated.

        Args:
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._dispatcher(dispatcher)  # type: ignore[return-value]

    def user_signal_handler(
        self: BuilderType, user_signal_handler: Callable[[int, object], Any]
    ) -> BuilderType:
        """Sets a callback to be used for :attr:`telegram.ext.Updater.user_signal_handler`.
        The callback will be called when :meth:`telegram.ext.Updater.idle()` receives a signal.
        It will be called with the two arguments ``signum, frame`` as for the
        :meth:`signal.signal` of the standard library.

        Note:
            Signal handlers are an advanced feature that come with some culprits and are not thread
            safe. This should therefore only be used for tasks like closing threads or database
            connections on shutdown. Note that for many tasks a viable alternative is to simply
            put your code *after* calling :meth:`telegram.ext.Updater.idle`. In this case it will
            be executed after the updater has shut down.

        Args:
            user_signal_handler (Callable[signum, frame]): The signal handler.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._user_signal_handler(user_signal_handler)
