#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
import pytest

from telegram import Update, Message, Chat, User, TelegramError
from telegram.ext import CallbackContext


class TestCallbackContext(object):

    def test_from_job(self, dp):
        job = dp.job_queue.run_once(lambda x: x, 10)

        callback_context = CallbackContext.from_job(job, dp)

        assert callback_context.job is job
        assert callback_context.chat_data is None
        assert callback_context.user_data is None
        assert callback_context.bot_data is dp.bot_data
        assert callback_context.bot is dp.bot
        assert callback_context.job_queue is dp.job_queue
        assert callback_context.update_queue is dp.update_queue

    def test_from_update(self, dp):
        update = Update(0, message=Message(0, User(1, 'user', False), None, Chat(1, 'chat')))

        callback_context = CallbackContext.from_update(update, dp)

        assert callback_context.chat_data == {}
        assert callback_context.user_data == {}
        assert callback_context.bot_data is dp.bot_data
        assert callback_context.bot is dp.bot
        assert callback_context.job_queue is dp.job_queue
        assert callback_context.update_queue is dp.update_queue

        callback_context_same_user_chat = CallbackContext.from_update(update, dp)

        callback_context.bot_data['test'] = 'bot'
        callback_context.chat_data['test'] = 'chat'
        callback_context.user_data['test'] = 'user'

        assert callback_context_same_user_chat.bot_data is callback_context.bot_data
        assert callback_context_same_user_chat.chat_data is callback_context.chat_data
        assert callback_context_same_user_chat.user_data is callback_context.user_data

        update_other_user_chat = Update(0, message=Message(0, User(2, 'user', False),
                                                           None, Chat(2, 'chat')))

        callback_context_other_user_chat = CallbackContext.from_update(update_other_user_chat, dp)

        assert callback_context_other_user_chat.bot_data is callback_context.bot_data
        assert callback_context_other_user_chat.chat_data is not callback_context.chat_data
        assert callback_context_other_user_chat.user_data is not callback_context.user_data

    def test_from_update_not_update(self, dp):
        callback_context = CallbackContext.from_update(None, dp)

        assert callback_context.chat_data is None
        assert callback_context.user_data is None
        assert callback_context.bot_data is dp.bot_data
        assert callback_context.bot is dp.bot
        assert callback_context.job_queue is dp.job_queue
        assert callback_context.update_queue is dp.update_queue

        callback_context = CallbackContext.from_update('', dp)

        assert callback_context.chat_data is None
        assert callback_context.user_data is None
        assert callback_context.bot_data is dp.bot_data
        assert callback_context.bot is dp.bot
        assert callback_context.job_queue is dp.job_queue
        assert callback_context.update_queue is dp.update_queue

    def test_from_error(self, dp):
        error = TelegramError('test')

        update = Update(0, message=Message(0, User(1, 'user', False), None, Chat(1, 'chat')))

        callback_context = CallbackContext.from_error(update, error, dp)

        assert callback_context.error is error
        assert callback_context.chat_data == {}
        assert callback_context.user_data == {}
        assert callback_context.bot_data is dp.bot_data
        assert callback_context.bot is dp.bot
        assert callback_context.job_queue is dp.job_queue
        assert callback_context.update_queue is dp.update_queue

    def test_match(self, dp):
        callback_context = CallbackContext(dp)

        assert callback_context.match is None

        callback_context.matches = ['test', 'blah']

        assert callback_context.match == 'test'

    def test_data_assignment(self, dp):
        update = Update(0, message=Message(0, User(1, 'user', False), None, Chat(1, 'chat')))

        callback_context = CallbackContext.from_update(update, dp)

        with pytest.raises(AttributeError):
            callback_context.chat_data = {"test": 123}
        with pytest.raises(AttributeError):
            callback_context.user_data = {}
        with pytest.raises(AttributeError):
            callback_context.chat_data = "test"

    def test_dispatcher_attribute(self, dp):
        callback_context = CallbackContext(dp)
        assert callback_context.dispatcher == dp
