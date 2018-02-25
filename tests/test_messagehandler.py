#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from telegram import (Message, Update, Chat, Bot, User, CallbackQuery, InlineQuery,
                      ChosenInlineResult, ShippingQuery, PreCheckoutQuery)
from telegram.ext import Filters, MessageHandler

message = Message(1, User(1, '', False), None, Chat(1, ''), text='Text')

params = [
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
    {'inline_query': InlineQuery(1, User(1, '', False), '', '')},
    {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
    {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
    {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')}
]

ids = ('callback_query', 'inline_query', 'chosen_inline_result',
       'shipping_query', 'pre_checkout_query', 'callback_query_without_message')


@pytest.fixture(scope='class', params=params, ids=ids)
def false_update(request):
    return Update(update_id=1, **request.param)


@pytest.fixture(scope='class')
def message(bot):
    return Message(1, None, None, None, bot=bot)


class TestMessageHandler(object):
    test_flag = False

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def callback_basic(self, bot, update):
        test_bot = isinstance(bot, Bot)
        test_update = isinstance(update, Update)
        self.test_flag = test_bot and test_update

    def callback_data_1(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) or (chat_data is not None)

    def callback_data_2(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) and (chat_data is not None)

    def callback_queue_1(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) or (update_queue is not None)

    def callback_queue_2(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) and (update_queue is not None)

    def test_basic(self, dp, message):
        handler = MessageHandler(None, self.callback_basic)
        dp.add_handler(handler)

        assert handler.check_update(Update(0, message))
        dp.process_update(Update(0, message))
        assert self.test_flag

    def test_edited(self, message):
        handler = MessageHandler(None, self.callback_basic, edited_updates=True,
                                 message_updates=False, channel_post_updates=False)

        assert handler.check_update(Update(0, edited_message=message))
        assert not handler.check_update(Update(0, message=message))
        assert not handler.check_update(Update(0, channel_post=message))
        assert handler.check_update(Update(0, edited_channel_post=message))

    def test_channel_post(self, message):
        handler = MessageHandler(None, self.callback_basic, edited_updates=False,
                                 message_updates=False, channel_post_updates=True)

        assert not handler.check_update(Update(0, edited_message=message))
        assert not handler.check_update(Update(0, message=message))
        assert handler.check_update(Update(0, channel_post=message))
        assert not handler.check_update(Update(0, edited_channel_post=message))

    def test_multiple_flags(self, message):
        handler = MessageHandler(None, self.callback_basic, edited_updates=True,
                                 message_updates=True, channel_post_updates=True)

        assert handler.check_update(Update(0, edited_message=message))
        assert handler.check_update(Update(0, message=message))
        assert handler.check_update(Update(0, channel_post=message))
        assert handler.check_update(Update(0, edited_channel_post=message))

    def test_allow_edited(self, message):
        with pytest.warns(UserWarning):
            handler = MessageHandler(None, self.callback_basic, message_updates=True,
                                     allow_edited=True, channel_post_updates=False)

        assert handler.check_update(Update(0, edited_message=message))
        assert handler.check_update(Update(0, message=message))
        assert not handler.check_update(Update(0, channel_post=message))
        assert handler.check_update(Update(0, edited_channel_post=message))

    def test_none_allowed(self):
        with pytest.raises(ValueError, match='are all False'):
            MessageHandler(None, self.callback_basic, message_updates=False,
                           channel_post_updates=False, edited_updates=False)

    def test_with_filter(self, message):
        handler = MessageHandler(Filters.command, self.callback_basic)

        message.text = '/test'
        assert handler.check_update(Update(0, message))

        message.text = 'test'
        assert not handler.check_update(Update(0, message))

    def test_pass_user_or_chat_data(self, dp, message):
        handler = MessageHandler(None, self.callback_data_1, pass_user_data=True)
        dp.add_handler(handler)

        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = MessageHandler(None, self.callback_data_1, pass_chat_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = MessageHandler(None, self.callback_data_2, pass_chat_data=True,
                                 pass_user_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

    def test_pass_job_or_update_queue(self, dp, message):
        handler = MessageHandler(None, self.callback_queue_1, pass_job_queue=True)
        dp.add_handler(handler)

        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = MessageHandler(None, self.callback_queue_1, pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = MessageHandler(None, self.callback_queue_2, pass_job_queue=True,
                                 pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

    def test_other_update_types(self, false_update):
        handler = MessageHandler(None, self.callback_basic, edited_updates=True)
        assert not handler.check_update(false_update)
