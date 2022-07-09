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
        "_group_limiters",
        "_group_max_rate",
        "_group_time_period",
        "_logger",
        "_max_retries",
        "_retry_after_event",
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
        self._group_max_rate = group_max_rate
        self._group_time_period = group_time_period
        self._group_limiters: Dict[Union[str, int], AsyncLimiter] = {}
        self._max_retries = max_retries
        self._logger = logging.getLogger(__name__)
        self._retry_after_event = asyncio.Event()
        self._retry_after_event.set()

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    def _get_group_limiter(self, group_id: Union[str, int, bool]) -> AsyncLimiter:
        # Remove limiters that haven't been used for so long that they are at max capacity
        # We only do that if we have a lot of limiters lying around to avoid looping on every call
        # This is a minimal effort approach - a full-fledged cache could use a TTL approach
        # or at least adapt the threshold dynamically depending on the number of active limiters
        if len(self._group_limiters) > 512:
            for key, limiter in list(self._group_limiters.items()):
                if key == group_id:
                    continue
                if limiter.has_capacity(limiter.max_rate):
                    del self._group_limiters[key]

        if group_id not in self._group_limiters:
            self._group_limiters[group_id] = AsyncLimiter(
                max_rate=self._group_max_rate,
                time_period=self._group_time_period,
            )
        return self._group_limiters[group_id]

    async def _run_request(
        self,
        chat: bool,
        group: Union[str, int, bool],
        callback: Callable[..., Coroutine[Any, Any, Union[bool, JSONDict, None]]],
        args: Any,
        kwargs: Dict[str, Any],
    ) -> Union[bool, JSONDict, None]:
        async with (self._base_limiter if chat else null_context()):
            async with (self._get_group_limiter(group) if group else null_context()):
                # In case a retry_after was hit, we wait with processing the request
                await self._retry_after_event.wait()

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

        group: Union[int, str, bool] = False
        chat = False
        chat_id = data.get("chat_id")
        if (isinstance(chat_id, int) and chat_id < 0) or isinstance(chat_id, str):
            # string chat_id only works for channels and supergroups
            # We can't really channels from groups though ...
            group = chat_id
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
                # Make sure we don't allow other requests to be processed
                self._retry_after_event.clear()
                await asyncio.sleep(sleep)
            finally:
                # Allow other requests to be processed
                self._retry_after_event.set()
