#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
# Daniyar Yeralin <devs@python-telegram-bot.org>
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
"""This module contains the class Typing, which sends typing action for Telegram bots intuitive."""
import asyncio
import contextlib
from types import TracebackType
from typing import Optional, Type, Union

from telegram import Bot
from telegram.constants import ChatAction


def _typing_callback(fut: asyncio.Future) -> None:
    """
    Dummy handler for typing task future.

    :param fut: The asyncio.Future object.
    """
    with contextlib.suppress(asyncio.CancelledError, Exception):
        fut.exception()


class Typing:
    """This is a context manager, utility class, which sends repeated ``ChatAction.TYPING``
    action every 5 seconds until the exit.

    .. code:: python
        async with context.bot.typing():
            # code

    Args:
        bot (:class:`telegram.Bot`): The bot instance to send typing action.
        chat_id (:obj:`int` | :obj:`str`): |chat_id_channel|

    """

    def __init__(self, bot: Bot, chat_id: Union[int, str]) -> None:
        self.bot = bot
        self.chat_id = chat_id
        self.loop = asyncio.get_running_loop()
        self.task: asyncio.Task

    async def typing_action(self) -> None:
        """
        Coroutine that sends a "typing..." action to the chat every 5 seconds.
        """
        while True:
            await self.bot.send_chat_action(chat_id=self.chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(5.0)

    async def __aenter__(self) -> None:
        """
        Coroutine that sets up the typing action task when entering an async context.
        """
        self.task = self.loop.create_task(self.typing_action())
        self.task.add_done_callback(_typing_callback)

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Coroutine that cancels the typing action task when exiting an async context.

        :param exc_type: The type of exception raised, if any.
        :param exc_val: The value of the exception raised, if any.
        :param exc_tb: The traceback of the exception raised, if any.
        """
        self.task.cancel()
