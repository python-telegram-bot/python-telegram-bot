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
from abc import abstractmethod
from asyncio import BoundedSemaphore
from types import TracebackType
from typing import Any, Awaitable, Optional, Type


class BaseUpdateProcessor:
    def __init__(self, max_concurrent_updates: int):
        self._max_concurrent_updates = max_concurrent_updates
        if self.max_concurrent_updates < 0:
            raise ValueError("max_concurrent_updates must be a non-negative integer!")
        self.semaphore = BoundedSemaphore(self.max_concurrent_updates or 1)

    @property
    def max_concurrent_updates(self) -> int:
        return self._max_concurrent_updates

    @abstractmethod
    async def process_update(
        self,
        update: object,
        coroutine: "Awaitable[Any]",
    ) -> None:
        pass

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass

    async def do_process_update(
        self,
        update: object,
        coroutine: "Awaitable[Any]",
    ) -> None:
        async with self.semaphore:
            await self.process_update(update, coroutine)

    async def __aenter__(self) -> "BaseUpdateProcessor":
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
        await self.shutdown()


class SimpleUpdateProcessor(BaseUpdateProcessor):
    async def process_update(
        self,
        update: object,
        coroutine: "Awaitable[Any]",
    ) -> None:
        await coroutine

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass
