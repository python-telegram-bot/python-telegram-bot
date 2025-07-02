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
"""This module contains the Promise class."""

import logging
from threading import Event
from typing import Callable, List, Optional, Tuple, TypeVar, Union

from telegram.utils.deprecate import set_new_attribute_deprecated
from telegram.utils.types import JSONDict

RT = TypeVar('RT')


logger = logging.getLogger(__name__)


class Promise:
    """A simple Promise implementation for use with the run_async decorator, DelayQueue etc.

    Args:
        pooled_function (:obj:`callable`): The callable that will be called concurrently.
        args (:obj:`list` | :obj:`tuple`): Positional arguments for :attr:`pooled_function`.
        kwargs (:obj:`dict`): Keyword arguments for :attr:`pooled_function`.
        update (:class:`telegram.Update` | :obj:`object`, optional): The update this promise is
            associated with.
        error_handling (:obj:`bool`, optional): Whether exceptions raised by :attr:`func`
            may be handled by error handlers. Defaults to :obj:`True`.

    Attributes:
        pooled_function (:obj:`callable`): The callable that will be called concurrently.
        args (:obj:`list` | :obj:`tuple`): Positional arguments for :attr:`pooled_function`.
        kwargs (:obj:`dict`): Keyword arguments for :attr:`pooled_function`.
        done (:obj:`threading.Event`): Is set when the result is available.
        update (:class:`telegram.Update` | :obj:`object`): Optional. The update this promise is
            associated with.
        error_handling (:obj:`bool`): Optional. Whether exceptions raised by :attr:`func`
            may be handled by error handlers. Defaults to :obj:`True`.

    """

    __slots__ = (
        'pooled_function',
        'args',
        'kwargs',
        'update',
        'error_handling',
        'done',
        '_done_callback',
        '_result',
        '_exception',
        '__dict__',
    )

    # TODO: Remove error_handling parameter once we drop the @run_async decorator
    def __init__(
        self,
        pooled_function: Callable[..., RT],
        args: Union[List, Tuple],
        kwargs: JSONDict,
        update: object = None,
        error_handling: bool = True,
    ):
        self.pooled_function = pooled_function
        self.args = args
        self.kwargs = kwargs
        self.update = update
        self.error_handling = error_handling
        self.done = Event()
        self._done_callback: Optional[Callable] = None
        self._result: Optional[RT] = None
        self._exception: Optional[Exception] = None

    def __setattr__(self, key: str, value: object) -> None:
        set_new_attribute_deprecated(self, key, value)

    def run(self) -> None:
        """Calls the :attr:`pooled_function` callable."""
        try:
            self._result = self.pooled_function(*self.args, **self.kwargs)

        except Exception as exc:
            self._exception = exc

        finally:
            self.done.set()
            if self._exception is None and self._done_callback:
                try:
                    self._done_callback(self.result())
                except Exception as exc:
                    logger.warning(
                        "`done_callback` of a Promise raised the following exception."
                        " The exception won't be handled by error handlers."
                    )
                    logger.warning("Full traceback:", exc_info=exc)

    def __call__(self) -> None:
        self.run()

    def result(self, timeout: float = None) -> Optional[RT]:
        """Return the result of the ``Promise``.

        Args:
            timeout (:obj:`float`, optional): Maximum time in seconds to wait for the result to be
                calculated. ``None`` means indefinite. Default is ``None``.

        Returns:
            Returns the return value of :attr:`pooled_function` or ``None`` if the ``timeout``
            expires.

        Raises:
            object exception raised by :attr:`pooled_function`.
        """
        self.done.wait(timeout=timeout)
        if self._exception is not None:
            raise self._exception  # pylint: disable=raising-bad-type
        return self._result

    def add_done_callback(self, callback: Callable) -> None:
        """
        Callback to be run when :class:`telegram.ext.utils.promise.Promise` becomes done.

        Note:
            Callback won't be called if :attr:`pooled_function`
            raises an exception.

        Args:
            callback (:obj:`callable`): The callable that will be called when promise is done.
            callback will be called by passing ``Promise.result()`` as only positional argument.

        """
        if self.done.wait(0):
            callback(self.result())
        else:
            self._done_callback = callback

    @property
    def exception(self) -> Optional[Exception]:
        """The exception raised by :attr:`pooled_function` or ``None`` if no exception has been
        raised (yet).
        """
        return self._exception
