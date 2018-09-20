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
from queue import Queue
from threading import current_thread
from time import sleep

import pytest

from telegram import TelegramError, Message, User, Chat, Update
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async, Dispatcher, DispatcherHandlerStop
from tests.conftest import create_dp


@pytest.fixture(scope='function')
def dp2(bot):
    for dp in create_dp(bot):
        yield dp


class TestDispatcher(object):
    message_update = Update(1,
                            message=Message(1, User(1, '', False), None, Chat(1, ''), text='Text'))
    received = None
    count = 0

    @pytest.fixture(autouse=True)
    def reset(self):
        self.received = None
        self.count = 0

    def error_handler(self, bot, update, error):
        self.received = error.message

    def error_handler_raise_error(self, bot, update, error):
        raise Exception('Failing bigly')

    def callback_increase_count(self, bot, update):
        self.count += 1

    def callback_set_count(self, count):
        def callback(bot, update):
            self.count = count

        return callback

    def callback_raise_error(self, bot, update):
        raise TelegramError(update.message.text)

    def callback_if_not_update_queue(self, bot, update, update_queue=None):
        if update_queue is not None:
            self.received = update.message

    def test_error_handler(self, dp):
        dp.add_error_handler(self.error_handler)
        error = TelegramError('Unauthorized.')
        dp.update_queue.put(error)
        sleep(.1)
        assert self.received == 'Unauthorized.'

        # Remove handler
        dp.remove_error_handler(self.error_handler)
        self.reset()

        dp.update_queue.put(error)
        sleep(.1)
        assert self.received is None

    def test_construction_with_bad_persistence(self, caplog, bot):
        class my_per:
            def __init__(self):
                self.store_user_data = False
                self.store_chat_data = False

        with pytest.raises(TypeError,
                           match='persistence should be based on telegram.ext.BasePersistence'):
            Dispatcher(bot, None, persistence=my_per())

    def test_error_handler_that_raises_errors(self, dp):
        """
        Make sure that errors raised in error handlers don't break the main loop of the dispatcher
        """
        handler_raise_error = MessageHandler(Filters.all, self.callback_raise_error)
        handler_increase_count = MessageHandler(Filters.all, self.callback_increase_count)
        error = TelegramError('Unauthorized.')

        dp.add_error_handler(self.error_handler_raise_error)

        # From errors caused by handlers
        dp.add_handler(handler_raise_error)
        dp.update_queue.put(self.message_update)
        sleep(.1)

        # From errors in the update_queue
        dp.remove_handler(handler_raise_error)
        dp.add_handler(handler_increase_count)
        dp.update_queue.put(error)
        dp.update_queue.put(self.message_update)
        sleep(.1)

        assert self.count == 1

    def test_run_async_multiple(self, bot, dp, dp2):
        def get_dispatcher_name(q):
            q.put(current_thread().name)

        q1 = Queue()
        q2 = Queue()

        dp.run_async(get_dispatcher_name, q1)
        dp2.run_async(get_dispatcher_name, q2)

        sleep(.1)

        name1 = q1.get()
        name2 = q2.get()

        assert name1 != name2

    def test_multiple_run_async_decorator(self, dp, dp2):
        # Make sure we got two dispatchers and that they are not the same
        assert isinstance(dp, Dispatcher)
        assert isinstance(dp2, Dispatcher)
        assert dp is not dp2

        @run_async
        def must_raise_runtime_error():
            pass

        with pytest.raises(RuntimeError):
            must_raise_runtime_error()

    def test_run_async_with_args(self, dp):
        dp.add_handler(MessageHandler(Filters.all,
                                      run_async(self.callback_if_not_update_queue),
                                      pass_update_queue=True))

        dp.update_queue.put(self.message_update)
        sleep(.1)
        assert self.received == self.message_update.message

    def test_error_in_handler(self, dp):
        dp.add_handler(MessageHandler(Filters.all, self.callback_raise_error))
        dp.add_error_handler(self.error_handler)

        dp.update_queue.put(self.message_update)
        sleep(.1)
        assert self.received == self.message_update.message.text

    def test_add_remove_handler(self, dp):
        handler = MessageHandler(Filters.all, self.callback_increase_count)
        dp.add_handler(handler)
        dp.update_queue.put(self.message_update)
        sleep(.1)
        assert self.count == 1
        dp.remove_handler(handler)
        dp.update_queue.put(self.message_update)
        assert self.count == 1

    def test_add_remove_handler_non_default_group(self, dp):
        handler = MessageHandler(Filters.all, self.callback_increase_count)
        dp.add_handler(handler, group=2)
        with pytest.raises(KeyError):
            dp.remove_handler(handler)
        dp.remove_handler(handler, group=2)

    def test_error_start_twice(self, dp):
        assert dp.running
        dp.start()

    def test_handler_order_in_group(self, dp):
        dp.add_handler(MessageHandler(Filters.photo, self.callback_set_count(1)))
        dp.add_handler(MessageHandler(Filters.all, self.callback_set_count(2)))
        dp.add_handler(MessageHandler(Filters.text, self.callback_set_count(3)))
        dp.update_queue.put(self.message_update)
        sleep(.1)
        assert self.count == 2

    def test_groups(self, dp):
        dp.add_handler(MessageHandler(Filters.all, self.callback_increase_count))
        dp.add_handler(MessageHandler(Filters.all, self.callback_increase_count), group=2)
        dp.add_handler(MessageHandler(Filters.all, self.callback_increase_count), group=-1)

        dp.update_queue.put(self.message_update)
        sleep(.1)
        assert self.count == 3

    def test_add_handler_errors(self, dp):
        handler = 'not a handler'
        with pytest.raises(TypeError, match='handler is not an instance of'):
            dp.add_handler(handler)

        handler = MessageHandler(Filters.photo, self.callback_set_count(1))
        with pytest.raises(TypeError, match='group is not int'):
            dp.add_handler(handler, 'one')

    def test_flow_stop(self, dp, bot):
        passed = []

        def start1(b, u):
            passed.append('start1')
            raise DispatcherHandlerStop

        def start2(b, u):
            passed.append('start2')

        def start3(b, u):
            passed.append('start3')

        def error(b, u, e):
            passed.append('error')
            passed.append(e)

        update = Update(1, message=Message(1, None, None, None, text='/start', bot=bot))

        # If Stop raised handlers in other groups should not be called.
        passed = []
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start3), 1)
        dp.add_handler(CommandHandler('start', start2), 2)
        dp.process_update(update)
        assert passed == ['start1']

    def test_exception_in_handler(self, dp, bot):
        passed = []

        def start1(b, u):
            passed.append('start1')
            raise Exception('General exception')

        def start2(b, u):
            passed.append('start2')

        def start3(b, u):
            passed.append('start3')

        def error(b, u, e):
            passed.append('error')
            passed.append(e)

        update = Update(1, message=Message(1, None, None, None, text='/start', bot=bot))

        # If an unhandled exception was caught, no further handlers from the same group should be
        # called.
        passed = []
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start2), 1)
        dp.add_handler(CommandHandler('start', start3), 2)
        dp.add_error_handler(error)
        dp.process_update(update)
        assert passed == ['start1', 'start3']

    def test_telegram_error_in_handler(self, dp, bot):
        passed = []
        err = TelegramError('Telegram error')

        def start1(b, u):
            passed.append('start1')
            raise err

        def start2(b, u):
            passed.append('start2')

        def start3(b, u):
            passed.append('start3')

        def error(b, u, e):
            passed.append('error')
            passed.append(e)

        update = Update(1, message=Message(1, None, None, None, text='/start', bot=bot))

        # If a TelegramException was caught, an error handler should be called and no further
        # handlers from the same group should be called.
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start2), 1)
        dp.add_handler(CommandHandler('start', start3), 2)
        dp.add_error_handler(error)
        dp.process_update(update)
        assert passed == ['start1', 'error', err, 'start3']
        assert passed[2] is err

    def test_flow_stop_in_error_handler(self, dp, bot):
        passed = []
        err = TelegramError('Telegram error')

        def start1(b, u):
            passed.append('start1')
            raise err

        def start2(b, u):
            passed.append('start2')

        def start3(b, u):
            passed.append('start3')

        def error(b, u, e):
            passed.append('error')
            passed.append(e)
            raise DispatcherHandlerStop

        update = Update(1, message=Message(1, None, None, None, text='/start', bot=bot))

        # If a TelegramException was caught, an error handler should be called and no further
        # handlers from the same group should be called.
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start2), 1)
        dp.add_handler(CommandHandler('start', start3), 2)
        dp.add_error_handler(error)
        dp.process_update(update)
        assert passed == ['start1', 'error', err]
        assert passed[2] is err
