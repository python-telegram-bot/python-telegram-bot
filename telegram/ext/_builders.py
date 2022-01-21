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
# pylint: disable=line-too-long
"""This module contains the Builder classes for the telegram.ext module."""
from pathlib import Path
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
    Type,
)

from telegram import Bot
from telegram.request import Request
from telegram._utils.types import ODVInput, DVInput, FilePathInput
from telegram._utils.warnings import warn
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue, DEFAULT_FALSE
from telegram.ext import Dispatcher, JobQueue, Updater, ExtBot, ContextTypes, CallbackContext
from telegram.ext._utils.types import CCT, UD, CD, BD, BT, JQ, PT

if TYPE_CHECKING:
    from telegram.ext import (
        Defaults,
        BasePersistence,
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
BuilderType = TypeVar('BuilderType', bound='_BaseBuilder')
CT = TypeVar('CT', bound=Callable[..., Any])

if TYPE_CHECKING:
    DEF_CCT = CallbackContext.DEFAULT_TYPE  # type: ignore[misc]
    InitBaseBuilder = _BaseBuilder[  # noqa: F821  # pylint: disable=used-before-assignment
        Dispatcher[ExtBot, DEF_CCT, Dict, Dict, Dict, JobQueue, None],
        ExtBot,
        DEF_CCT,
        Dict,
        Dict,
        Dict,
        JobQueue,
        None,
    ]
    InitUpdaterBuilder = UpdaterBuilder[  # noqa: F821  # pylint: disable=used-before-assignment
        Dispatcher[ExtBot, DEF_CCT, Dict, Dict, Dict, JobQueue, None],
        ExtBot,
        DEF_CCT,
        Dict,
        Dict,
        Dict,
        JobQueue,
        None,
    ]
    InitDispatcherBuilder = (
        DispatcherBuilder[  # noqa: F821  # pylint: disable=used-before-assignment
            Dispatcher[ExtBot, DEF_CCT, Dict, Dict, Dict, JobQueue, None],
            ExtBot,
            DEF_CCT,
            Dict,
            Dict,
            Dict,
            JobQueue,
            None,
        ]
    )


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
]

_DISPATCHER_CHECKS = [
    ('bot', 'bot instance'),
    ('update_queue', 'update_queue'),
    ('workers', 'workers'),
    ('exception_event', 'exception_event'),
    ('job_queue', 'JobQueue instance'),
    ('persistence', 'persistence instance'),
    ('context_types', 'ContextTypes instance'),
    ('dispatcher_class', 'Dispatcher Class'),
] + _BOT_CHECKS
_DISPATCHER_CHECKS.remove(('dispatcher', 'Dispatcher instance'))

_TWO_ARGS_REQ = "The parameter `{}` may only be set, if no {} was set."


# Base class for all builders. We do this mainly to reduce code duplication, because e.g.
# the UpdaterBuilder has all method that the DispatcherBuilder has
class _BaseBuilder(Generic[ODT, BT, CCT, UD, CD, BD, JQ, PT]):
    # pylint reports false positives here:

    __slots__ = (
        '_token',
        '_base_url',
        '_base_file_url',
        '_request_kwargs',
        '_request',
        '_private_key',
        '_private_key_password',
        '_defaults',
        '_arbitrary_callback_data',
        '_bot',
        '_update_queue',
        '_workers',
        '_exception_event',
        '_job_queue',
        '_persistence',
        '_context_types',
        '_dispatcher',
        '_user_signal_handler',
        '_dispatcher_class',
        '_dispatcher_kwargs',
        '_updater_class',
        '_updater_kwargs',
    )

    def __init__(self: 'InitBaseBuilder'):
        self._token: DVInput[str] = DefaultValue('')
        self._base_url: DVInput[str] = DefaultValue('https://api.telegram.org/bot')
        self._base_file_url: DVInput[str] = DefaultValue('https://api.telegram.org/file/bot')
        self._request_kwargs: DVInput[Dict[str, Any]] = DefaultValue({})
        self._request: ODVInput['Request'] = DEFAULT_NONE
        self._private_key: ODVInput[bytes] = DEFAULT_NONE
        self._private_key_password: ODVInput[bytes] = DEFAULT_NONE
        self._defaults: ODVInput['Defaults'] = DEFAULT_NONE
        self._arbitrary_callback_data: DVInput[Union[bool, int]] = DEFAULT_FALSE
        self._bot: Bot = DEFAULT_NONE  # type: ignore[assignment]
        self._update_queue: DVInput[Queue] = DefaultValue(Queue())
        self._workers: DVInput[int] = DefaultValue(4)
        self._exception_event: DVInput[Event] = DefaultValue(Event())
        self._job_queue: ODVInput['JobQueue'] = DefaultValue(JobQueue())
        self._persistence: ODVInput['BasePersistence'] = DEFAULT_NONE
        self._context_types: DVInput[ContextTypes] = DefaultValue(ContextTypes())
        self._dispatcher: ODVInput['Dispatcher'] = DEFAULT_NONE
        self._user_signal_handler: Optional[Callable[[int, object], Any]] = None
        self._dispatcher_class: DVInput[Type[Dispatcher]] = DefaultValue(Dispatcher)
        self._dispatcher_kwargs: Dict[str, object] = {}
        self._updater_class: Type[Updater] = Updater
        self._updater_kwargs: Dict[str, object] = {}

    @staticmethod
    def _get_connection_pool_size(workers: DVInput[int]) -> int:
        # For the standard use case (Updater + Dispatcher + Bot)
        # we need a connection pool the size of:
        # * for each of the workers
        # * 1 for Dispatcher
        # * 1 for Updater (even if webhook is used, we can spare a connection)
        # * 1 for JobQueue
        # * 1 for main thread
        return DefaultValue.get_value(workers) + 4

    def _build_ext_bot(self) -> ExtBot:
        if isinstance(self._token, DefaultValue):
            raise RuntimeError('No bot token was set.')

        if not isinstance(self._request, DefaultValue):
            request = self._request
        else:
            request_kwargs = DefaultValue.get_value(self._request_kwargs)
            if (
                'con_pool_size'
                not in request_kwargs  # pylint: disable=unsupported-membership-test
            ):
                request_kwargs[  # pylint: disable=unsupported-assignment-operation
                    'con_pool_size'
                ] = self._get_connection_pool_size(self._workers)
            request = Request(**request_kwargs)  # pylint: disable=not-a-mapping

        return ExtBot(
            token=self._token,
            base_url=DefaultValue.get_value(self._base_url),
            base_file_url=DefaultValue.get_value(self._base_file_url),
            private_key=DefaultValue.get_value(self._private_key),
            private_key_password=DefaultValue.get_value(self._private_key_password),
            defaults=DefaultValue.get_value(self._defaults),
            arbitrary_callback_data=DefaultValue.get_value(self._arbitrary_callback_data),
            request=request,
        )

    def _build_dispatcher(
        self: '_BaseBuilder[ODT, BT, CCT, UD, CD, BD, JQ, PT]', stack_level: int = 3
    ) -> Dispatcher[BT, CCT, UD, CD, BD, JQ, PT]:
        job_queue = DefaultValue.get_value(self._job_queue)
        dispatcher: Dispatcher[
            BT, CCT, UD, CD, BD, JQ, PT
        ] = DefaultValue.get_value(  # type: ignore[call-arg]  # pylint: disable=not-callable
            self._dispatcher_class
        )(
            bot=self._bot if self._bot is not DEFAULT_NONE else self._build_ext_bot(),
            update_queue=DefaultValue.get_value(self._update_queue),
            workers=DefaultValue.get_value(self._workers),
            exception_event=DefaultValue.get_value(self._exception_event),
            job_queue=job_queue,
            persistence=DefaultValue.get_value(self._persistence),
            context_types=DefaultValue.get_value(self._context_types),
            stack_level=stack_level + 1,
            **self._dispatcher_kwargs,
        )

        if job_queue is not None:
            job_queue.set_dispatcher(dispatcher)

        con_pool_size = self._get_connection_pool_size(self._workers)
        actual_size = dispatcher.bot.request.con_pool_size
        if actual_size < con_pool_size:
            warn(
                f'The Connection pool of Request object is smaller ({actual_size}) than the '
                f'recommended value of {con_pool_size}.',
                stacklevel=stack_level,
            )

        return dispatcher

    def _build_updater(
        self: '_BaseBuilder[ODT, BT, Any, Any, Any, Any, Any, Any]',
    ) -> Updater[BT, ODT]:
        if isinstance(self._dispatcher, DefaultValue):
            dispatcher = self._build_dispatcher(stack_level=4)
            return self._updater_class(
                dispatcher=dispatcher,
                user_signal_handler=self._user_signal_handler,
                exception_event=dispatcher.exception_event,
                **self._updater_kwargs,  # type: ignore[arg-type]
            )

        if self._dispatcher:
            exception_event = self._dispatcher.exception_event
            bot = self._dispatcher.bot
        else:
            exception_event = DefaultValue.get_value(self._exception_event)
            bot = self._bot or self._build_ext_bot()

        return self._updater_class(  # type: ignore[call-arg]
            dispatcher=self._dispatcher,
            bot=bot,
            update_queue=DefaultValue.get_value(self._update_queue),
            user_signal_handler=self._user_signal_handler,
            exception_event=exception_event,
            **self._updater_kwargs,
        )

    @property
    def _dispatcher_check(self) -> bool:
        return self._dispatcher not in (DEFAULT_NONE, None)

    def _set_dispatcher_class(
        self: BuilderType, dispatcher_class: Type[Dispatcher], kwargs: Dict[str, object] = None
    ) -> BuilderType:
        if self._dispatcher is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('dispatcher_class', 'Dispatcher instance'))
        self._dispatcher_class = dispatcher_class
        self._dispatcher_kwargs = kwargs or {}
        return self

    def _set_updater_class(
        self: BuilderType, updater_class: Type[Updater], kwargs: Dict[str, object] = None
    ) -> BuilderType:
        self._updater_class = updater_class
        self._updater_kwargs = kwargs or {}
        return self

    def _set_token(self: BuilderType, token: str) -> BuilderType:
        if self._bot is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('token', 'bot instance'))
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('token', 'Dispatcher instance'))
        self._token = token
        return self

    def _set_base_url(self: BuilderType, base_url: str) -> BuilderType:
        if self._bot is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('base_url', 'bot instance'))
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('base_url', 'Dispatcher instance'))
        self._base_url = base_url
        return self

    def _set_base_file_url(self: BuilderType, base_file_url: str) -> BuilderType:
        if self._bot is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('base_file_url', 'bot instance'))
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('base_file_url', 'Dispatcher instance'))
        self._base_file_url = base_file_url
        return self

    def _set_request_kwargs(self: BuilderType, request_kwargs: Dict[str, Any]) -> BuilderType:
        if self._request is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('request_kwargs', 'Request instance'))
        if self._bot is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('request_kwargs', 'bot instance'))
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('request_kwargs', 'Dispatcher instance'))
        self._request_kwargs = request_kwargs
        return self

    def _set_request(self: BuilderType, request: Request) -> BuilderType:
        if not isinstance(self._request_kwargs, DefaultValue):
            raise RuntimeError(_TWO_ARGS_REQ.format('request', 'request_kwargs'))
        if self._bot is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('request', 'bot instance'))
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('request', 'Dispatcher instance'))
        self._request = request
        return self

    def _set_private_key(
        self: BuilderType,
        private_key: Union[bytes, FilePathInput],
        password: Union[bytes, FilePathInput] = None,
    ) -> BuilderType:
        if self._bot is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('private_key', 'bot instance'))
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('private_key', 'Dispatcher instance'))

        self._private_key = (
            private_key if isinstance(private_key, bytes) else Path(private_key).read_bytes()
        )
        if password is None or isinstance(password, bytes):
            self._private_key_password = password
        else:
            self._private_key_password = Path(password).read_bytes()

        return self

    def _set_defaults(self: BuilderType, defaults: 'Defaults') -> BuilderType:
        if self._bot is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('defaults', 'bot instance'))
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('defaults', 'Dispatcher instance'))
        self._defaults = defaults
        return self

    def _set_arbitrary_callback_data(
        self: BuilderType, arbitrary_callback_data: Union[bool, int]
    ) -> BuilderType:
        if self._bot is not DEFAULT_NONE:
            raise RuntimeError(_TWO_ARGS_REQ.format('arbitrary_callback_data', 'bot instance'))
        if self._dispatcher_check:
            raise RuntimeError(
                _TWO_ARGS_REQ.format('arbitrary_callback_data', 'Dispatcher instance')
            )
        self._arbitrary_callback_data = arbitrary_callback_data
        return self

    def _set_bot(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, '
        'JQ, PT]',
        bot: InBT,
    ) -> '_BaseBuilder[Dispatcher[InBT, CCT, UD, CD, BD, JQ, PT], InBT, CCT, UD, CD, BD, JQ, PT]':
        for attr, error in _BOT_CHECKS:
            if (
                not isinstance(getattr(self, f'_{attr}'), DefaultValue)
                if attr != 'dispatcher'
                else self._dispatcher_check
            ):
                raise RuntimeError(_TWO_ARGS_REQ.format('bot', error))
        self._bot = bot
        return self  # type: ignore[return-value]

    def _set_update_queue(self: BuilderType, update_queue: Queue) -> BuilderType:
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('update_queue', 'Dispatcher instance'))
        self._update_queue = update_queue
        return self

    def _set_workers(self: BuilderType, workers: int) -> BuilderType:
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('workers', 'Dispatcher instance'))
        self._workers = workers
        return self

    def _set_exception_event(self: BuilderType, exception_event: Event) -> BuilderType:
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('exception_event', 'Dispatcher instance'))
        self._exception_event = exception_event
        return self

    def _set_job_queue(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        job_queue: InJQ,
    ) -> '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, InJQ, PT], BT, CCT, UD, CD, BD, InJQ, PT]':
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('job_queue', 'Dispatcher instance'))
        self._job_queue = job_queue
        return self  # type: ignore[return-value]

    def _set_persistence(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        persistence: InPT,
    ) -> '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, InPT], BT, CCT, UD, CD, BD, JQ, InPT]':
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('persistence', 'Dispatcher instance'))
        self._persistence = persistence
        return self  # type: ignore[return-value]

    def _set_context_types(
        self: '_BaseBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        context_types: 'ContextTypes[InCCT, InUD, InCD, InBD]',
    ) -> '_BaseBuilder[Dispatcher[BT, InCCT, InUD, InCD, InBD, JQ, PT], BT, InCCT, InUD, InCD, InBD, JQ, PT]':
        if self._dispatcher_check:
            raise RuntimeError(_TWO_ARGS_REQ.format('context_types', 'Dispatcher instance'))
        self._context_types = context_types
        return self  # type: ignore[return-value]

    @overload
    def _set_dispatcher(
        self: '_BaseBuilder[ODT, BT, CCT, UD, CD, BD, JQ, PT]', dispatcher: None
    ) -> '_BaseBuilder[None, BT, CCT, UD, CD, BD, JQ, PT]':
        ...

    @overload
    def _set_dispatcher(
        self: BuilderType, dispatcher: Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]
    ) -> '_BaseBuilder[Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT], InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]':
        ...

    def _set_dispatcher(  # type: ignore[misc]
        self: BuilderType,
        dispatcher: Optional[Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]],
    ) -> '_BaseBuilder[Optional[Dispatcher[InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]], InBT, InCCT, InUD, InCD, InBD, InJQ, InPT]':
        for attr, error in _DISPATCHER_CHECKS:
            if not isinstance(getattr(self, f'_{attr}'), DefaultValue):
                raise RuntimeError(_TWO_ARGS_REQ.format('dispatcher', error))
        self._dispatcher = dispatcher
        return self

    def _set_user_signal_handler(
        self: BuilderType, user_signal_handler: Callable[[int, object], Any]
    ) -> BuilderType:
        self._user_signal_handler = user_signal_handler
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
        * Some arguments are mutually exclusive. E.g. after calling :meth:`token`, you can't set
          a custom bot with :meth:`bot` and vice versa.
        * Unless a custom :class:`telegram.Bot` instance is set via :meth:`bot`, :meth:`build` will
          use :class:`telegram.ext.ExtBot` for the bot.

    .. seealso::
        :class:`telegram.ext.UpdaterBuilder`

    .. _`builder pattern`: https://en.wikipedia.org/wiki/Builder_pattern.
    """

    __slots__ = ()

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

    def dispatcher_class(
        self: BuilderType, dispatcher_class: Type[Dispatcher], kwargs: Dict[str, object] = None
    ) -> BuilderType:
        """Sets a custom subclass to be used instead of :class:`telegram.ext.Dispatcher`. The
        subclasses ``__init__`` should look like this

        .. code:: python

            def __init__(self, custom_arg_1, custom_arg_2, ..., **kwargs):
                super().__init__(**kwargs)
                self.custom_arg_1 = custom_arg_1
                self.custom_arg_2 = custom_arg_2

        Args:
            dispatcher_class (:obj:`type`): A subclass of  :class:`telegram.ext.Dispatcher`
            kwargs (Dict[:obj:`str`, :obj:`object`], optional): Keyword arguments for the
                initialization. Defaults to an empty dict.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_dispatcher_class(dispatcher_class, kwargs)

    def token(self: BuilderType, token: str) -> BuilderType:
        """Sets the token to be used for :attr:`telegram.ext.Dispatcher.bot`.

        Args:
            token (:obj:`str`): The token.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_token(token)

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
        return self._set_base_url(base_url)

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
        return self._set_base_file_url(base_file_url)

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
        return self._set_request_kwargs(request_kwargs)

    def request(self: BuilderType, request: Request) -> BuilderType:
        """Sets a :class:`telegram.utils.Request` object to be used for
        :attr:`telegram.ext.Dispatcher.bot`.

        .. seealso:: :meth:`request_kwargs`

        Args:
            request (:class:`telegram.utils.Request`): The request object.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_request(request)

    def private_key(
        self: BuilderType,
        private_key: Union[bytes, FilePathInput],
        password: Union[bytes, FilePathInput] = None,
    ) -> BuilderType:
        """Sets the private key and corresponding password for decryption of telegram passport data
        to be used for :attr:`telegram.ext.Dispatcher.bot`.

        .. seealso:: `passportbot.py <https://github.com/python-telegram-bot/python-telegram-bot\
            /tree/master/examples#passportbotpy>`_, `Telegram Passports <https://github.com/python-telegram-bot\
            /python-telegram-bot/wiki/Telegram-Passport>`_

        Args:
            private_key (:obj:`bytes` | :obj:`str` | :obj:`pathlib.Path`): The private key or the
                file path of a file that contains the key. In the latter case, the file's content
                will be read automatically.
            password (:obj:`bytes` | :obj:`str` | :obj:`pathlib.Path`, optional): The corresponding
                password or the file path of a file that contains the password. In the latter case,
                the file's content will be read automatically.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_private_key(private_key=private_key, password=password)

    def defaults(self: BuilderType, defaults: 'Defaults') -> BuilderType:
        """Sets the :class:`telegram.ext.Defaults` object to be used for
        :attr:`telegram.ext.Dispatcher.bot`.

        .. seealso:: `Adding Defaults <https://github.com/python-telegram-bot/python-telegram-bot\
            /wiki/Adding-defaults-to-your-bot>`_

        Args:
            defaults (:class:`telegram.ext.Defaults`): The defaults.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_defaults(defaults)

    def arbitrary_callback_data(
        self: BuilderType, arbitrary_callback_data: Union[bool, int]
    ) -> BuilderType:
        """Specifies whether :attr:`telegram.ext.Dispatcher.bot` should allow arbitrary objects as
        callback data for :class:`telegram.InlineKeyboardButton` and how many keyboards should be
        cached in memory. If not called, only strings can be used as callback data and no data will
        be stored in memory.

        .. seealso:: `Arbitrary callback_data <https://github.com/python-telegram-bot\
            /python-telegram-bot/wiki/Arbitrary-callback_data>`_,
            `arbitrarycallbackdatabot.py <https://github.com/python-telegram-bot\
                /python-telegram-bot/tree/master/examples#arbitrarycallbackdatabotpy>`_

        Args:
            arbitrary_callback_data (:obj:`bool` | :obj:`int`): If :obj:`True` is passed, the
                default cache size of 1024 will be used. Pass an integer to specify a different
                cache size.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_arbitrary_callback_data(arbitrary_callback_data)

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
        return self._set_bot(bot)  # type: ignore[return-value]

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
        return self._set_update_queue(update_queue)

    def workers(self: BuilderType, workers: int) -> BuilderType:
        """Sets the number of worker threads to be used for
        :meth:`telegram.ext.Dispatcher.run_async`, i.e. the number of callbacks that can be run
        asynchronously at the same time.

         .. seealso:: :attr:`telegram.ext.Handler.run_sync`,
             :attr:`telegram.ext.Defaults.run_async`

        Args:
            workers (:obj:`int`): The number of worker threads.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_workers(workers)

    def exception_event(self: BuilderType, exception_event: Event) -> BuilderType:
        """Sets a :class:`threading.Event` instance to be used for
        :attr:`telegram.ext.Dispatcher.exception_event`. When this event is set, the dispatcher
        will stop processing updates. If not called, an event will be instantiated.
        If the dispatcher is passed to :meth:`telegram.ext.UpdaterBuilder.dispatcher`, then this
        event will also be used for :attr:`telegram.ext.Updater.exception_event`.

         .. seealso:: :attr:`telegram.ext.Updater.exception_event`,
             :meth:`telegram.ext.UpdaterBuilder.exception_event`

        Args:
            exception_event (:class:`threading.Event`): The event.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_exception_event(exception_event)

    def job_queue(
        self: 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        job_queue: InJQ,
    ) -> 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, InJQ, PT], BT, CCT, UD, CD, BD, InJQ, PT]':
        """Sets a :class:`telegram.ext.JobQueue` instance to be used for
        :attr:`telegram.ext.Dispatcher.job_queue`. If not called, a job queue will be instantiated.

        .. seealso:: `JobQueue <https://github.com/python-telegram-bot/python-telegram-bot/wiki\
            /Extensions-%E2%80%93-JobQueue>`_, `timerbot.py <https://github.com\
                /python-telegram-bot/python-telegram-bot/tree/master/examples#timerbotpy>`_

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
        return self._set_job_queue(job_queue)  # type: ignore[return-value]

    def persistence(
        self: 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        persistence: InPT,
    ) -> 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, InPT], BT, CCT, UD, CD, BD, JQ, InPT]':
        """Sets a :class:`telegram.ext.BasePersistence` instance to be used for
        :attr:`telegram.ext.Dispatcher.persistence`.

        .. seealso:: `Making your bot persistent <https://github.com/python-telegram-bot/python-telegram-bot\
            /wiki/Making-your-bot-persistent>`_,
            `persistentconversationbot.py <https://github.com/python-telegram-bot/python-telegram-bot/tree\
                /master/examples#persistentconversationbotpy>`_

        Warning:
            If a :class:`telegram.ext.ContextTypes` instance is set via :meth:`context_types`,
            the persistence instance must use the same types!

        Args:
            persistence (:class:`telegram.ext.BasePersistence`, optional): The persistence
                instance.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_persistence(persistence)  # type: ignore[return-value]

    def context_types(
        self: 'DispatcherBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        context_types: 'ContextTypes[InCCT, InUD, InCD, InBD]',
    ) -> 'DispatcherBuilder[Dispatcher[BT, InCCT, InUD, InCD, InBD, JQ, PT], BT, InCCT, InUD, InCD, InBD, JQ, PT]':
        """Sets a :class:`telegram.ext.ContextTypes` instance to be used for
        :attr:`telegram.ext.Dispatcher.context_types`.

        .. seealso:: `contexttypesbot.py <https://github.com/python-telegram-bot/python-telegram-bot/tree/master\
            /examples#contexttypesbotpy>`_

        Args:
            context_types (:class:`telegram.ext.ContextTypes`, optional): The context types.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_context_types(context_types)  # type: ignore[return-value]


class UpdaterBuilder(_BaseBuilder[ODT, BT, CCT, UD, CD, BD, JQ, PT]):
    """This class serves as initializer for :class:`telegram.ext.Updater` via the so called
    `builder pattern`_. To build an :class:`telegram.ext.Updater`, one first initializes an
    instance of this class. Arguments for the :class:`telegram.ext.Updater` to build are then
    added by subsequently calling the methods of the builder. Finally, the
    :class:`telegram.ext.Updater` is built by calling :meth:`build`. In the simplest case this
    can look like the following example.

    Example:
        .. code:: python

            updater = UpdaterBuilder().token('TOKEN').build()

    Please see the description of the individual methods for information on which arguments can be
    set and what the defaults are when not called. When no default is mentioned, the argument will
    not be used by default.

    Note:
        * Some arguments are mutually exclusive. E.g. after calling :meth:`token`, you can't set
          a custom bot with :meth:`bot` and vice versa.
        * Unless a custom :class:`telegram.Bot` instance is set via :meth:`bot`, :meth:`build` will
          use :class:`telegram.ext.ExtBot` for the bot.

    .. seealso::
        :class:`telegram.ext.DispatcherBuilder`

    .. _`builder pattern`: https://en.wikipedia.org/wiki/Builder_pattern.
    """

    __slots__ = ()

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

    def dispatcher_class(
        self: BuilderType, dispatcher_class: Type[Dispatcher], kwargs: Dict[str, object] = None
    ) -> BuilderType:
        """Sets a custom subclass to be used instead of :class:`telegram.ext.Dispatcher`. The
        subclasses ``__init__`` should look like this

        .. code:: python

            def __init__(self, custom_arg_1, custom_arg_2, ..., **kwargs):
                super().__init__(**kwargs)
                self.custom_arg_1 = custom_arg_1
                self.custom_arg_2 = custom_arg_2

        Args:
            dispatcher_class (:obj:`type`): A subclass of  :class:`telegram.ext.Dispatcher`
            kwargs (Dict[:obj:`str`, :obj:`object`], optional): Keyword arguments for the
                initialization. Defaults to an empty dict.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_dispatcher_class(dispatcher_class, kwargs)

    def updater_class(
        self: BuilderType, updater_class: Type[Updater], kwargs: Dict[str, object] = None
    ) -> BuilderType:
        """Sets a custom subclass to be used instead of :class:`telegram.ext.Updater`. The
        subclasses ``__init__`` should look like this

        .. code:: python

            def __init__(self, custom_arg_1, custom_arg_2, ..., **kwargs):
                super().__init__(**kwargs)
                self.custom_arg_1 = custom_arg_1
                self.custom_arg_2 = custom_arg_2

        Args:
            updater_class (:obj:`type`): A subclass of  :class:`telegram.ext.Updater`
            kwargs (Dict[:obj:`str`, :obj:`object`], optional): Keyword arguments for the
                initialization. Defaults to an empty dict.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._set_updater_class(updater_class, kwargs)

    def token(self: BuilderType, token: str) -> BuilderType:
        """Sets the token to be used for :attr:`telegram.ext.Updater.bot`.

        Args:
            token (:obj:`str`): The token.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._set_token(token)

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
        return self._set_base_url(base_url)

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
        return self._set_base_file_url(base_file_url)

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
        return self._set_request_kwargs(request_kwargs)

    def request(self: BuilderType, request: Request) -> BuilderType:
        """Sets a :class:`telegram.utils.Request` object to be used for
        :attr:`telegram.ext.Updater.bot`.

        .. seealso:: :meth:`request_kwargs`

        Args:
            request (:class:`telegram.utils.Request`): The request object.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._set_request(request)

    def private_key(
        self: BuilderType,
        private_key: Union[bytes, FilePathInput],
        password: Union[bytes, FilePathInput] = None,
    ) -> BuilderType:
        """Sets the private key and corresponding password for decryption of telegram passport data
        to be used for :attr:`telegram.ext.Updater.bot`.

        .. seealso:: `passportbot.py <https://github.com/python-telegram-bot/python-telegram-bot\
            /tree/master/examples#passportbotpy>`_, `Telegram Passports <https://github.com/python-telegram-bot\
            /python-telegram-bot/wiki/Telegram-Passport>`_

        Args:
            private_key (:obj:`bytes` | :obj:`str` | :obj:`pathlib.Path`): The private key or the
                file path of a file that contains the key. In the latter case, the file's content
                will be read automatically.
            password (:obj:`bytes` | :obj:`str` | :obj:`pathlib.Path`, optional): The corresponding
                password or the file path of a file that contains the password. In the latter case,
                the file's content will be read automatically.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._set_private_key(private_key=private_key, password=password)

    def defaults(self: BuilderType, defaults: 'Defaults') -> BuilderType:
        """Sets the :class:`telegram.ext.Defaults` object to be used for
        :attr:`telegram.ext.Updater.bot`.

        .. seealso:: `Adding Defaults <https://github.com/python-telegram-bot/python-telegram-bot\
            /wiki/Adding-defaults-to-your-bot>`_

        Args:
            defaults (:class:`telegram.ext.Defaults`): The defaults.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._set_defaults(defaults)

    def arbitrary_callback_data(
        self: BuilderType, arbitrary_callback_data: Union[bool, int]
    ) -> BuilderType:
        """Specifies whether :attr:`telegram.ext.Updater.bot` should allow arbitrary objects as
        callback data for :class:`telegram.InlineKeyboardButton` and how many keyboards should be
        cached in memory. If not called, only strings can be used as callback data and no data will
        be stored in memory.

        .. seealso:: `Arbitrary callback_data <https://github.com/python-telegram-bot\
            /python-telegram-bot/wiki/Arbitrary-callback_data>`_,
            `arbitrarycallbackdatabot.py <https://github.com/python-telegram-bot\
                /python-telegram-bot/tree/master/examples#arbitrarycallbackdatabotpy>`_

        Args:
            arbitrary_callback_data (:obj:`bool` | :obj:`int`): If :obj:`True` is passed, the
                default cache size of 1024 will be used. Pass an integer to specify a different
                cache size.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._set_arbitrary_callback_data(arbitrary_callback_data)

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
        return self._set_bot(bot)  # type: ignore[return-value]

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
        return self._set_update_queue(update_queue)

    def workers(self: BuilderType, workers: int) -> BuilderType:
        """Sets the number of worker threads to be used for
        :meth:`telegram.ext.Dispatcher.run_async`, i.e. the number of callbacks that can be run
        asynchronously at the same time.

         .. seealso:: :attr:`telegram.ext.Handler.run_sync`,
             :attr:`telegram.ext.Defaults.run_async`

        Args:
            workers (:obj:`int`): The number of worker threads.

        Returns:
            :class:`DispatcherBuilder`: The same builder with the updated argument.
        """
        return self._set_workers(workers)

    def exception_event(self: BuilderType, exception_event: Event) -> BuilderType:
        """Sets a :class:`threading.Event` instance to be used by the
        :class:`telegram.ext.Updater`. When an unhandled exception happens while fetching updates,
        this event will be set and the ``Updater`` will stop fetching for updates. If not called,
        an event will be instantiated.
        If :meth:`dispatcher` is not called, this event will also be used for
        :attr:`telegram.ext.Dispatcher.exception_event`.

         .. seealso:: :attr:`telegram.ext.Dispatcher.exception_event`,
             :meth:`telegram.ext.DispatcherBuilder.exception_event`

        Args:
            exception_event (:class:`threading.Event`): The event.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._set_exception_event(exception_event)

    def job_queue(
        self: 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        job_queue: InJQ,
    ) -> 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, InJQ, PT], BT, CCT, UD, CD, BD, InJQ, PT]':
        """Sets a :class:`telegram.ext.JobQueue` instance to be used for the
        :attr:`telegram.ext.Updater.dispatcher`. If not called, a job queue will be instantiated.

        .. seealso:: `JobQueue <https://github.com/python-telegram-bot/python-telegram-bot\
            /wiki/Extensions-%E2%80%93-JobQueue>`_, `timerbot.py <https://github.com\
                /python-telegram-bot/python-telegram-bot/tree/master/examples#timerbotpy>`_,
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
        return self._set_job_queue(job_queue)  # type: ignore[return-value]

    def persistence(
        self: 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        persistence: InPT,
    ) -> 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, InPT], BT, CCT, UD, CD, BD, JQ, InPT]':
        """Sets a :class:`telegram.ext.BasePersistence` instance to be used for the
        :attr:`telegram.ext.Updater.dispatcher`.

        .. seealso:: `Making your bot persistent <https://github.com/python-telegram-bot\
            /python-telegram-bot/wiki/Making-your-bot-persistent>`_,
            `persistentconversationbot.py <https://github.com/python-telegram-bot\
                /python-telegram-bot/tree/master/examples#persistentconversationbotpy>`_,
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
        return self._set_persistence(persistence)  # type: ignore[return-value]

    def context_types(
        self: 'UpdaterBuilder[Dispatcher[BT, CCT, UD, CD, BD, JQ, PT], BT, CCT, UD, CD, BD, JQ, PT]',
        context_types: 'ContextTypes[InCCT, InUD, InCD, InBD]',
    ) -> 'UpdaterBuilder[Dispatcher[BT, InCCT, InUD, InCD, InBD, JQ, PT], BT, InCCT, InUD, InCD, InBD, JQ, PT]':
        """Sets a :class:`telegram.ext.ContextTypes` instance to be used for the
        :attr:`telegram.ext.Updater.dispatcher`.

        .. seealso:: `contexttypesbot.py <https://github.com/python-telegram-bot/python-telegram-bot/tree\
            /master/examples#contexttypesbotpy>`_,
            :attr:`telegram.ext.Dispatcher.context_types`.

        Args:
            context_types (:class:`telegram.ext.ContextTypes`, optional): The context types.

        Returns:
            :class:`UpdaterBuilder`: The same builder with the updated argument.
        """
        return self._set_context_types(context_types)  # type: ignore[return-value]

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
        :attr:`telegram.ext.Updater.dispatcher`.
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
        return self._set_dispatcher(dispatcher)  # type: ignore[return-value]

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
        return self._set_user_signal_handler(user_signal_handler)
