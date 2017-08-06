#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import pytest

from telegram import Bot, Update, Message, User, Chat, CallbackQuery, InlineQuery, \
    ChosenInlineResult, ShippingQuery, PreCheckoutQuery
from telegram.ext import StringCommandHandler

message = Message(1, User(1, ''), None, Chat(1, ''), text='Text')

params = [
    {'message': message},
    {'edited_message': message},
    {'callback_query': CallbackQuery(1, User(1, ''), 'chat', message=message)},
    {'channel_post': message},
    {'edited_channel_post': message},
    {'inline_query': InlineQuery(1, User(1, ''), '', '')},
    {'chosen_inline_result': ChosenInlineResult('id', User(1, ''), '')},
    {'shipping_query': ShippingQuery('id', User(1, ''), '', None)},
    {'pre_checkout_query': PreCheckoutQuery('id', User(1, ''), '', 0, '')},
    {'callback_query': CallbackQuery(1, User(1, ''), 'chat')}
]

ids = ('message', 'edited_message', 'callback_query', 'channel_post',
             'edited_channel_post', 'inline_query', 'chosen_inline_result',
             'shipping_query', 'pre_checkout_query', 'callback_query_without_message')

@pytest.fixture(params=params, ids=ids)
def false_update(request):
    return Update(update_id=1, **request.param)

class TestStringCommandHandler:
    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False


    def sch_basic_handler(self, bot, update):
        test_bot = isinstance(bot, Bot)
        test_update = isinstance(update, str)
        self.test_flag = test_bot and test_update

    def sch_queue_handler_1(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) or (update_queue is not None)

    def sch_queue_handler_2(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) and (update_queue is not None)

    def sch_pass_args_handler(self, bot, update, args):
        if update == '/test':
            self.test_flag = len(args) == 0
        else:
            self.test_flag = args == ['one', 'two']

    def test_basic(self, dp):
        handler = StringCommandHandler('test', self.sch_basic_handler)
        dp.add_handler(handler)

        assert handler.check_update('/test')
        dp.process_update('/test')
        assert self.test_flag

        assert not handler.check_update('/nottest')
        assert not handler.check_update('not /test in front')
        assert handler.check_update('/test followed by text')

    def test_pass_args(self, dp):
        handler = StringCommandHandler('test', self.sch_pass_args_handler, pass_args=True)
        dp.add_handler(handler)

        dp.process_update('/test')
        assert self.test_flag

        self.test_flag = False
        dp.process_update('/test one two')
        assert self.test_flag

    def test_pass_job_or_update_queue(self, dp):
        handler = StringCommandHandler('test', self.sch_queue_handler_1, pass_job_queue=True)
        dp.add_handler(handler)

        dp.process_update('/test')
        assert self.test_flag

        dp.remove_handler(handler)
        handler = StringCommandHandler('test', self.sch_queue_handler_1, pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update('/test')
        assert self.test_flag

        dp.remove_handler(handler)
        handler = StringCommandHandler('test', self.sch_queue_handler_2, pass_job_queue=True,
                                 pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update('/test')
        assert self.test_flag

    def test_other_update_types(self, false_update):
        handler = StringCommandHandler('test', self.sch_basic_handler)
        assert not handler.check_update(false_update)