#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
"""This module contains the BaseProcessor class."""
from abc import ABC, abstractmethod
from asyncio import BoundedSemaphore
from types import TracebackType
from typing import Any, Awaitable, Optional, Type, final


class BaseUpdateProcessor(ABC):
    """An abstract base class for update processors. You can use this class to implement
    your own update processor.

    .. seealso:: :wiki:`Concurrency`

    .. versionadded:: 20.4

    Args:
        max_concurrent_updates (:obj:`int`): The maximum number of updates to be processed
            concurrently. If this number is exceeded, new updates will be queued until the number
            of currently processed updates decreases.

    Raises:
        :exc:`ValueError`: If :paramref:`max_concurrent_updates` is a non-positive integer.
    """

    __slots__ = ("_max_concurrent_updates", "_semaphore")

    def __init__(self, max_concurrent_updates: int):
        self._max_concurrent_updates = max_concurrent_updates
        if self.max_concurrent_updates < 1:
            raise ValueError("`max_concurrent_updates` must be a positive integer!")
        self._semaphore = BoundedSemaphore(self.max_concurrent_updates)

    @property
    def max_concurrent_updates(self) -> int:
        """:obj:`int`: The maximum number of updates that can be processed concurrently."""
        return self._max_concurrent_updates

    @abstractmethod
    async def do_process_update(
        self,
        update: object,
        coroutine: "Awaitable[Any]",
    ) -> None:
        """Custom implementation of how to process an update. Must be implemented by a subclass.

        Warning:
            This method will be called by :meth:`process_update`. It should *not* be called
            manually.

        Args:
            update (:obj:`object`): The update to be processed.
            coroutine (:term:`Awaitable`): The coroutine that will be awaited to process the
                update.
        """

    @abstractmethod
    async def initialize(self) -> None:
        """Initializes the processor so resources can be allocated. Must be implemented by a
        subclass.

        .. seealso::
            :meth:`shutdown`
        """

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the processor so resources can be freed. Must be implemented by a subclass.

        .. seealso::
            :meth:`initialize`
        """

    @final
    async def process_update(
        self,
        update: object,
        coroutine: "Awaitable[Any]",
    ) -> None:
        """Calls :meth:`do_process_update` with a semaphore to limit the number of concurrent
        updates.

        Args:
            update (:obj:`object`): The update to be processed.
            coroutine (:term:`Awaitable`): The coroutine that will be awaited to process the
                update.
        """
        async with self._semaphore:
            await self.do_process_update(update, coroutine)

    async def __aenter__(self) -> "BaseUpdateProcessor":
        """Simple context manager which initializes the Processor."""
        try:
            await self.initialize()
            return self
        except Exception as exc:
            await self.shutdown()
            raise exc

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Shutdown the Processor from the context manager."""
        await self.shutdown()


class SimpleUpdateProcessor(BaseUpdateProcessor):
    """Instance of :class:`telegram.ext.BaseUpdateProcessor` that immediately awaits the
    coroutine, i.e. does not apply any additional processing. This is used by default when
    :attr:`telegram.ext.ApplicationBuilder.concurrent_updates` is :obj:`int`.

    .. versionadded:: 20.4
    """

    __slots__ = ()

    async def do_process_update(
        self,
        update: object,
        coroutine: "Awaitable[Any]",
    ) -> None:
        """Immediately awaits the coroutine, i.e. does not apply any additional processing.

        Args:
            update (:obj:`object`): The update to be processed.
            coroutine (:term:`Awaitable`): The coroutine that will be awaited to process the
                update.
        """
        await coroutine

    async def initialize(self) -> None:
        """Does nothing."""

    async def shutdown(self) -> None:
        """Does nothing."""
