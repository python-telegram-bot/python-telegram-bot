#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2023
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
from typing import Callable


def call_after(function: Callable, after: Callable):
    """Run a callable after another has executed. Useful when trying to make sure that a function
    did actually run, but just monkeypatching it doesn't work because this would break some other
    functionality.

    Example usage:

    def test_stuff(self, bot, monkeypatch):

        def after(arg):
            # arg is the return value of `send_message`
            self.received = arg

        monkeypatch.setattr(bot, 'send_message', call_after(bot.send_message, after)

    """
    if asyncio.iscoroutinefunction(function):

        async def wrapped(*args, **kwargs):
            out = await function(*args, **kwargs)
            if asyncio.iscoroutinefunction(after):
                await after(out)
            else:
                after(out)
            return out

    else:

        def wrapped(*args, **kwargs):
            out = function(*args, **kwargs)
            after(out)
            return out

    return wrapped
