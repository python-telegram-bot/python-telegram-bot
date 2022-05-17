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
# This file is written by Yagel Ashkenazi <123yagel@gmail.com>

import asyncio
from ctypes import Union
from sys import stderr
from types import GeneratorType
from typing import Callable, Any

from telegram import Update
from telegram.ext import BaseHandler
from telegram.ext._utils.types import CCT, UT
from telegram.ext.filters import BaseFilter


class _EasyBotConversation:
    """Save and manage state for EasyConversation for one chat"""

    __slots__ = ('main_callback', 'error_callback', '_asyncio_task', '_semaphore', '_updates')

    def __init__(self, main_callback, error_callback):
        self.main_callback = main_callback
        self.error_callback = error_callback
        self._asyncio_task: Union[GeneratorType, None] = None
        self._semaphore = asyncio.Semaphore(0)
        self._updates = []

    async def _callback_wrapper(self, callback, context):
        try:
            await callback(context)
        except Exception as e:
            await self.error_callback(e, context)

    def start_bot(self, context):
        async def get_update():
            await self._semaphore.acquire()
            context.last_update = self._updates.pop()  # Eww
            return context.last_update

        context.get_update = get_update  # context new function TODO: in new Context class or so

        self._asyncio_task = asyncio.create_task(self._callback_wrapper(self.main_callback, context))

    def running(self):
        return self._asyncio_task is not None and not self._asyncio_task.done()

    def got_update(self, update, context):
        self._updates.insert(0, update)
        self._semaphore.release()
        if not self.running():
            self.start_bot(context)


class EasyConversationHandler(BaseHandler[Update, CCT]):
    """Handler for functional-conversation bots"""

    __slots__ = ('main_callback', 'error_callback', 'first_message_filter', '_conversations')

    def __init__(
            self,
            main_callback: Callable[[CCT], Any],
            first_message_filter: BaseFilter = None,
            error_callback: Callable[[CCT, Exception], Any] = None
    ):
        super(EasyConversationHandler, self).__init__(callback=lambda u, c: '')
        self.main_callback = main_callback

        if first_message_filter is None:
            first_message_filter = BaseFilter()
        if error_callback is None:
            error_callback = self.default_error_callback

        self.error_callback = error_callback
        self.first_message_filter = first_message_filter

        self._conversations = {}

    def check_update(self, update: Update) -> bool:
        if update.effective_chat.id in self._conversations and self._conversations[update.effective_chat.id].running():
            return True
        if self.first_message_filter.check_update(update):
            return True
        return False

    @staticmethod
    async def default_error_callback(e: Exception, context_unused):
        import traceback
        stderr.write('No error handler set for EasyConversationHandler, so printing error')
        stderr.write(''.join(traceback.format_exception(None, e, e.__traceback__)))

    async def handle_update(
            self,
            update: UT,
            application: "Application",
            check_result: object,
            context: CCT,
    ):
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance. Calls :attr:`callback` along with its respectful
        arguments. To work with the :class:`telegram.ext.ConversationHandler`, this method
        returns the value returned from :attr:`callback`.
        Note that it can be overridden if needed by the subclassing handler.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be handled.
            application (:class:`telegram.ext.Application`): The calling application.
            check_result (:class:`object`): The result from :meth:`check_update`.
            context (:class:`telegram.ext.CallbackContext`): The context as provided by
                the application.

        """
        chat_id = update.effective_chat.id
        if chat_id not in self._conversations:
            # First time here?
            self._conversations[chat_id] = _EasyBotConversation(self.main_callback, self.error_callback)

        self._conversations[chat_id].got_update(update, context)
