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

import pytest

from telegram import (
    Update,
    Message,
    Chat,
    User,
    Bot,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from telegram.ext import CallbackContext
from telegram.error import TelegramError

"""
CallbackContext.refresh_data is tested in TestBasePersistence
"""


class TestCallbackContext:
    def test_slot_behaviour(self, dp, mro_slots, recwarn):
        c = CallbackContext(dp)
        for attr in c.__slots__:
            assert getattr(c, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not c.__dict__, f"got missing slot(s): {c.__dict__}"
        assert len(mro_slots(c)) == len(set(mro_slots(c))), "duplicate slot"
        c.args = c.args
        assert len(recwarn) == 0, recwarn.list

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
        update = Update(
            0, message=Message(0, None, Chat(1, 'chat'), from_user=User(1, 'user', False))
        )

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

        update_other_user_chat = Update(
            0, message=Message(0, None, Chat(2, 'chat'), from_user=User(2, 'user', False))
        )

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

        update = Update(
            0, message=Message(0, None, Chat(1, 'chat'), from_user=User(1, 'user', False))
        )

        callback_context = CallbackContext.from_error(update, error, dp)

        assert callback_context.error is error
        assert callback_context.chat_data == {}
        assert callback_context.user_data == {}
        assert callback_context.bot_data is dp.bot_data
        assert callback_context.bot is dp.bot
        assert callback_context.job_queue is dp.job_queue
        assert callback_context.update_queue is dp.update_queue
        assert callback_context.async_args is None
        assert callback_context.async_kwargs is None

    def test_from_error_async_params(self, dp):
        error = TelegramError('test')

        args = [1, '2']
        kwargs = {'one': 1, 2: 'two'}

        callback_context = CallbackContext.from_error(
            None, error, dp, async_args=args, async_kwargs=kwargs
        )

        assert callback_context.error is error
        assert callback_context.async_args is args
        assert callback_context.async_kwargs is kwargs

    def test_match(self, dp):
        callback_context = CallbackContext(dp)

        assert callback_context.match is None

        callback_context.matches = ['test', 'blah']

        assert callback_context.match == 'test'

    def test_data_assignment(self, dp):
        update = Update(
            0, message=Message(0, None, Chat(1, 'chat'), from_user=User(1, 'user', False))
        )

        callback_context = CallbackContext.from_update(update, dp)

        with pytest.raises(AttributeError):
            callback_context.bot_data = {"test": 123}
        with pytest.raises(AttributeError):
            callback_context.user_data = {}
        with pytest.raises(AttributeError):
            callback_context.chat_data = "test"

    def test_dispatcher_attribute(self, dp):
        callback_context = CallbackContext(dp)
        assert callback_context.dispatcher == dp

    def test_drop_callback_data_exception(self, bot, dp):
        non_ext_bot = Bot(bot.token)
        update = Update(
            0, message=Message(0, None, Chat(1, 'chat'), from_user=User(1, 'user', False))
        )

        callback_context = CallbackContext.from_update(update, dp)

        with pytest.raises(RuntimeError, match='This telegram.ext.ExtBot instance does not'):
            callback_context.drop_callback_data(None)

        try:
            dp.bot = non_ext_bot
            with pytest.raises(RuntimeError, match='telegram.Bot does not allow for'):
                callback_context.drop_callback_data(None)
        finally:
            dp.bot = bot

    def test_drop_callback_data(self, dp, monkeypatch, chat_id):
        monkeypatch.setattr(dp.bot, 'arbitrary_callback_data', True)

        update = Update(
            0, message=Message(0, None, Chat(1, 'chat'), from_user=User(1, 'user', False))
        )

        callback_context = CallbackContext.from_update(update, dp)
        dp.bot.send_message(
            chat_id=chat_id,
            text='test',
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton('test', callback_data='callback_data')
            ),
        )
        keyboard_uuid = dp.bot.callback_data_cache.persistence_data[0][0][0]
        button_uuid = list(dp.bot.callback_data_cache.persistence_data[0][0][2])[0]
        callback_data = keyboard_uuid + button_uuid
        callback_query = CallbackQuery(
            id='1',
            from_user=None,
            chat_instance=None,
            data=callback_data,
        )
        dp.bot.callback_data_cache.process_callback_query(callback_query)

        try:
            assert len(dp.bot.callback_data_cache.persistence_data[0]) == 1
            assert list(dp.bot.callback_data_cache.persistence_data[1]) == ['1']

            callback_context.drop_callback_data(callback_query)
            assert dp.bot.callback_data_cache.persistence_data == ([], {})
        finally:
            dp.bot.callback_data_cache.clear_callback_data()
            dp.bot.callback_data_cache.clear_callback_queries()
