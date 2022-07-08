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
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Dict, Optional, Union

from telegram._utils.types import JSONDict


class BaseRateLimiter(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        ...

    @abstractmethod
    async def process_request(
        self,
        callback: Callable[..., Coroutine[Any, Any, Union[bool, JSONDict, None]]],
        args: Any,
        kwargs: Dict[str, Any],
        data: Dict[str, Any],
        rate_limit_kwargs: Optional[Dict[str, Any]],
    ) -> Union[bool, JSONDict, None]:
        ...
