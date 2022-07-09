#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2022
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
import asyncio
import contextlib
import logging
import sys
from typing import Any, AsyncIterator, Callable, Coroutine, Dict, Optional, Union

from aiolimiter import AsyncLimiter

from telegram._utils.types import JSONDict
from telegram.error import RetryAfter
from telegram.ext._baseratelimiter import BaseRateLimiter

if sys.version_info >= (3, 10):
    null_context = contextlib.nullcontext()
else:

    @contextlib.asynccontextmanager
    async def null_context() -> AsyncIterator[None]:
        yield None


class AIORateLimiter(BaseRateLimiter[Dict[str, Any]]):
    __slots__ = (
        "_base_limiter",
        "_group_limiter",
        "_max_retries",
        "_logger",
    )

    def __init__(
        self,
        overall_max_rate: float = 30,
        overall_time_period: float = 1,
        group_max_rate: float = 20,
        group_time_period: float = 60,
        max_retries: int = 0,
    ) -> None:
        self._base_limiter = AsyncLimiter(
            max_rate=overall_max_rate, time_period=overall_time_period
        )
        self._group_limiter = AsyncLimiter(max_rate=group_max_rate, time_period=group_time_period)
        self._max_retries = max_retries
        self._logger = logging.getLogger(__name__)

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def _run_request(
        self,
        chat: bool,
        group: bool,
        callback: Callable[..., Coroutine[Any, Any, Union[bool, JSONDict, None]]],
        args: Any,
        kwargs: Dict[str, Any],
    ) -> Union[bool, JSONDict, None]:
        async with (self._base_limiter if chat else null_context()):
            # the group limit is actually on a *per group* basis, so it would be better to use a
            # different limiter for each group.
            async with (self._group_limiter if group else null_context()):
                return await callback(*args, **kwargs)

    # mypy doesn't understand that the last run of the for loop raises an exception
    async def process_request(  # type: ignore[return]
        self,
        callback: Callable[..., Coroutine[Any, Any, Union[bool, JSONDict, None]]],
        args: Any,
        kwargs: Dict[str, Any],
        endpoint: str,
        data: Dict[str, Any],
        rate_limit_args: Optional[Dict[str, Any]],
    ) -> Union[bool, JSONDict, None]:
        max_retries = data.get("max_retries", self._max_retries)

        group = False
        chat = False
        chat_id = data.get("chat_id")
        if isinstance(chat_id, int) and chat_id < 0:
            group = True
            chat = True
        elif isinstance(chat_id, str):
            group = True
            chat = True

        for i in range(max_retries + 1):
            try:
                return await self._run_request(
                    chat=chat, group=group, callback=callback, args=args, kwargs=kwargs
                )
            except RetryAfter as exc:
                if i == max_retries:
                    self._logger.exception(
                        "Rate limit hit after maximum of %d retries", max_retries, exc_info=exc
                    )
                    raise exc

                sleep = exc.retry_after + 0.1
                self._logger.info("Rate limit hit. Retrying after %f seconds", sleep)
                await asyncio.sleep(sleep)
