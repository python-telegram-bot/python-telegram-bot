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

from telegram import Message, Update, Chat, Bot
from telegram.ext import CommandHandler, Filters


@pytest.fixture(scope='function')
def message(bot):
    return Message(1, None, None, None, bot=bot)


class TestCommandHandler:
    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def ch_basic_handler(self, bot, update):
        test_bot = isinstance(bot, Bot)
        test_update = isinstance(update, Update)
        self.test_flag = test_bot and test_update

    def ch_data_handler_1(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) or (chat_data is not None)

    def ch_data_handler_2(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) and (chat_data is not None)

    def ch_queue_handler_1(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) or (update_queue is not None)

    def ch_queue_handler_2(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) and (update_queue is not None)

    def ch_test6(self, bot, update, args):
        if update.message.text == '/test':
            self.test_flag = len(args) == 0
        elif update.message.text == '/test@{}'.format(bot.username):
            self.test_flag = len(args) == 0
        else:
            self.test_flag = args == ['one', 'two']

    def test_basic(self, dp, message):
        handler = CommandHandler('test', self.ch_basic_handler)
        dp.add_handler(handler)

        message.text = '/test'
        assert handler.check_update(Update(0, message))
        dp.process_update(Update(0, message))
        assert self.test_flag

        message.text = '/nottest'
        assert not handler.check_update(Update(0, message))

        message.text = 'test'
        assert not handler.check_update(Update(0, message))

        message.text = 'not /test at start'
        assert not handler.check_update(Update(0, message))

    def test_command_list(self, message):
        handler = CommandHandler(['test', 'start'], self.ch_basic_handler)

        message.text = '/test'
        assert handler.check_update(Update(0, message))

        message.text = '/start'
        assert handler.check_update(Update(0, message))

        message.text = '/stop'
        assert not handler.check_update(Update(0, message))

    def test_edited(self, message):
        handler = CommandHandler('test', self.ch_basic_handler, allow_edited=False)

        message.text = '/test'
        assert handler.check_update(Update(0, message))
        assert not handler.check_update(Update(0, edited_message=message))
        handler.allow_edited = True
        assert handler.check_update(Update(0, message))
        assert handler.check_update(Update(0, edited_message=message))

    def test_with_dispatcher(self, dp, message):
        handler = CommandHandler('test', self.ch_basic_handler)
        dp.add_handler(handler)

        message.text = '/test'
        dp.process_update(Update(0, message))
        assert self.test_flag

    def test_directed_commands(self, message):
        handler = CommandHandler('test', self.ch_basic_handler)

        message.text = '/test@{}'.format(message.bot.username)
        assert handler.check_update(Update(0, message))

        message.text = '/test@otherbot'
        assert not handler.check_update(Update(0, message))

    def test_with_filter(self, message):
        handler = CommandHandler('test', self.ch_basic_handler, Filters.group)

        message.chat = Chat(-23, 'group')
        message.text = '/test'
        assert handler.check_update(Update(0, message))

        message.chat = Chat(23, 'private')
        assert not handler.check_update(Update(0, message))

    def test_pass_args(self, dp, message):
        handler = CommandHandler('test', self.ch_test6, pass_args=True)
        dp.add_handler(handler)

        message.text = '/test'
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        self.test_flag = False
        message.text = '/test@{}'.format(message.bot.username)
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        self.test_flag = False
        message.text = '/test one two'
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        self.test_flag = False
        message.text = '/test@{} one two'.format(message.bot.username)
        dp.process_update(Update(0, message=message))
        assert self.test_flag

    def test_pass_user_or_chat_data(self, dp, message):
        handler = CommandHandler('test', self.ch_data_handler_1, pass_user_data=True)
        dp.add_handler(handler)

        message.text = '/test'
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CommandHandler('test', self.ch_data_handler_1, pass_chat_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CommandHandler('test', self.ch_data_handler_2, pass_chat_data=True, pass_user_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

    def test_pass_job_or_update_queue(self, dp, message):
        handler = CommandHandler('test', self.ch_queue_handler_1, pass_job_queue=True)
        dp.add_handler(handler)

        message.text = '/test'
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CommandHandler('test', self.ch_queue_handler_1, pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CommandHandler('test', self.ch_queue_handler_2, pass_job_queue=True,
                                 pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag
