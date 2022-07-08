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


class AIORateLimiter(BaseRateLimiter):
    def __init__(self) -> None:
        self._base_limiter = AsyncLimiter(max_rate=1, time_period=1)
        self._group_limiter = AsyncLimiter(max_rate=1, time_period=3)

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def _run_request(
        self,
        group: bool,
        callback: Callable[..., Coroutine[Any, Any, Union[bool, JSONDict, None]]],
        args: Any,
        kwargs: Dict[str, Any],
    ) -> Union[bool, JSONDict, None]:
        async with self._base_limiter:
            async with (self._group_limiter if group else null_context()):
                return await callback(*args, **kwargs)

    async def process_request(
        self,
        callback: Callable[..., Coroutine[Any, Any, Union[bool, JSONDict, None]]],
        args: Any,
        kwargs: Dict[str, Any],
        data: Dict[str, Any],
        rate_limit_kwargs: Optional[Dict[str, Any]],
    ) -> Union[bool, JSONDict, None]:
        group = False
        chat_id = data.get("chat_id")
        if isinstance(chat_id, int) and chat_id < 0:
            group = True
        elif isinstance(chat_id, str):
            group = True

        try:
            return await self._run_request(
                group=group, callback=callback, args=args, kwargs=kwargs
            )
        except RetryAfter as exc:
            await asyncio.sleep(exc.retry_after + 0.1)
            return await self._run_request(
                group=group, callback=callback, args=args, kwargs=kwargs
            )
