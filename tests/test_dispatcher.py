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
import sys
from queue import Queue
from threading import current_thread
from time import sleep

import pytest

from telegram import TelegramError, Message, User, Chat, Update, Bot, MessageEntity
from telegram.ext import (MessageHandler, Filters, CommandHandler, CallbackContext,
                          JobQueue, BasePersistence)
from telegram.ext.dispatcher import run_async, Dispatcher, DispatcherHandlerStop
from telegram.utils.deprecate import TelegramDeprecationWarning
from tests.conftest import create_dp
from collections import defaultdict


@pytest.fixture(scope='function')
def dp2(bot):
    for dp in create_dp(bot):
        yield dp


class TestDispatcher(object):
    message_update = Update(1,
                            message=Message(1, User(1, '', False), None, Chat(1, ''), text='Text'))
    received = None
    count = 0

    @pytest.fixture(autouse=True, name='reset')
    def reset_fixture(self):
        self.reset()

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

    def callback_context(self, update, context):
        if (isinstance(context, CallbackContext)
                and isinstance(context.bot, Bot)
                and isinstance(context.update_queue, Queue)
                and isinstance(context.job_queue, JobQueue)
                and isinstance(context.error, TelegramError)):
            self.received = context.error.message

    def test_one_context_per_update(self, cdp):
        def one(update, context):
            if update.message.text == 'test':
                context.my_flag = True

        def two(update, context):
            if update.message.text == 'test':
                if not hasattr(context, 'my_flag'):
                    pytest.fail()
            else:
                if hasattr(context, 'my_flag'):
                    pytest.fail()

        cdp.add_handler(MessageHandler(Filters.regex('test'), one), group=1)
        cdp.add_handler(MessageHandler(None, two), group=2)
        u = Update(1, Message(1, None, None, None, text='test'))
        cdp.process_update(u)
        u.message.text = 'something'
        cdp.process_update(u)

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
                self.store_bot_data = False

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

        update = Update(1, message=Message(1, None, None, None, text='/start',
                                           entities=[MessageEntity(type=MessageEntity.BOT_COMMAND,
                                                                   offset=0,
                                                                   length=len('/start'))],
                                           bot=bot))

        # If Stop raised handlers in other groups should not be called.
        passed = []
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start3), 1)
        dp.add_handler(CommandHandler('start', start2), 2)
        dp.process_update(update)
        assert passed == ['start1']

    def test_exception_in_handler(self, dp, bot):
        passed = []
        err = Exception('General exception')

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

        update = Update(1, message=Message(1, None, None, None, text='/start',
                                           entities=[MessageEntity(type=MessageEntity.BOT_COMMAND,
                                                                   offset=0,
                                                                   length=len('/start'))],
                                           bot=bot))

        # If an unhandled exception was caught, no further handlers from the same group should be
        # called. Also, the error handler should be called and receive the exception
        passed = []
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start2), 1)
        dp.add_handler(CommandHandler('start', start3), 2)
        dp.add_error_handler(error)
        dp.process_update(update)
        assert passed == ['start1', 'error', err, 'start3']

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

        update = Update(1, message=Message(1, None, None, None, text='/start',
                                           entities=[MessageEntity(type=MessageEntity.BOT_COMMAND,
                                                                   offset=0,
                                                                   length=len('/start'))],
                                           bot=bot))

        # If a TelegramException was caught, an error handler should be called and no further
        # handlers from the same group should be called.
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start2), 1)
        dp.add_handler(CommandHandler('start', start3), 2)
        dp.add_error_handler(error)
        dp.process_update(update)
        assert passed == ['start1', 'error', err, 'start3']
        assert passed[2] is err

    def test_error_while_saving_chat_data(self, dp, bot):
        increment = []

        class OwnPersistence(BasePersistence):
            def __init__(self):
                super(BasePersistence, self).__init__()
                self.store_user_data = True
                self.store_chat_data = True
                self.store_bot_data = True

            def get_bot_data(self):
                return dict()

            def update_bot_data(self, data):
                raise Exception

            def get_chat_data(self):
                return defaultdict(dict)

            def update_chat_data(self, chat_id, data):
                raise Exception

            def get_user_data(self):
                return defaultdict(dict)

            def update_user_data(self, user_id, data):
                raise Exception

        def start1(b, u):
            pass

        def error(b, u, e):
            increment.append("error")

        # If updating a user_data or chat_data from a persistence object throws an error,
        # the error handler should catch it

        update = Update(1, message=Message(1, User(1, "Test", False), None, Chat(1, "lala"),
                                           text='/start',
                                           entities=[MessageEntity(type=MessageEntity.BOT_COMMAND,
                                                                   offset=0,
                                                                   length=len('/start'))],
                                           bot=bot))
        my_persistence = OwnPersistence()
        dp = Dispatcher(bot, None, persistence=my_persistence)
        dp.add_handler(CommandHandler('start', start1))
        dp.add_error_handler(error)
        dp.process_update(update)
        assert increment == ["error", "error", "error"]

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

        update = Update(1, message=Message(1, None, None, None, text='/start',
                                           entities=[MessageEntity(type=MessageEntity.BOT_COMMAND,
                                                                   offset=0,
                                                                   length=len('/start'))],
                                           bot=bot))

        # If a TelegramException was caught, an error handler should be called and no further
        # handlers from the same group should be called.
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start2), 1)
        dp.add_handler(CommandHandler('start', start3), 2)
        dp.add_error_handler(error)
        dp.process_update(update)
        assert passed == ['start1', 'error', err]
        assert passed[2] is err

    def test_error_handler_context(self, cdp):
        cdp.add_error_handler(self.callback_context)

        error = TelegramError('Unauthorized.')
        cdp.update_queue.put(error)
        sleep(.1)
        assert self.received == 'Unauthorized.'

    def test_sensible_worker_thread_names(self, dp2):
        thread_names = [thread.name for thread in getattr(dp2, '_Dispatcher__async_threads')]
        print(thread_names)
        for thread_name in thread_names:
            assert thread_name.startswith("Bot:{}:worker:".format(dp2.bot.id))

    @pytest.mark.skipif(sys.version_info < (3, 0), reason='pytest fails this for no reason')
    def test_non_context_deprecation(self, dp):
        with pytest.warns(TelegramDeprecationWarning):
            Dispatcher(dp.bot, dp.update_queue, job_queue=dp.job_queue, workers=0,
                       use_context=False)

    def test_error_while_persisting(self, cdp, monkeypatch):
        class OwnPersistence(BasePersistence):
            def __init__(self):
                super(OwnPersistence, self).__init__()
                self.store_user_data = True
                self.store_chat_data = True
                self.store_bot_data = True

            def update(self, data):
                raise Exception('PersistenceError')

            def update_bot_data(self, data):
                self.update(data)

            def update_chat_data(self, chat_id, data):
                self.update(data)

            def update_user_data(self, user_id, data):
                self.update(data)

        def callback(update, context):
            pass

        test_flag = False

        def error(update, context):
            nonlocal test_flag
            test_flag = str(context.error) == 'PersistenceError'
            raise Exception('ErrorHandlingError')

        def logger(message):
            assert 'uncaught error was raised while handling' in message

        update = Update(1, message=Message(1, User(1, '', False), None, Chat(1, ''), text='Text'))
        handler = MessageHandler(Filters.all, callback)
        cdp.add_handler(handler)
        cdp.add_error_handler(error)
        monkeypatch.setattr(cdp.logger, 'exception', logger)

        cdp.persistence = OwnPersistence()
        cdp.process_update(update)
        assert test_flag

    def test_persisting_no_user_no_chat(self, cdp):
        class OwnPersistence(BasePersistence):
            def __init__(self):
                super(OwnPersistence, self).__init__()
                self.store_user_data = True
                self.store_chat_data = True
                self.store_bot_data = True
                self.test_flag_bot_data = False
                self.test_flag_chat_data = False
                self.test_flag_user_data = False

            def update_bot_data(self, data):
                self.test_flag_bot_data = True

            def update_chat_data(self, chat_id, data):
                self.test_flag_chat_data = True

            def update_user_data(self, user_id, data):
                self.test_flag_user_data = True

        def callback(update, context):
            pass

        handler = MessageHandler(Filters.all, callback)
        cdp.add_handler(handler)
        cdp.persistence = OwnPersistence()

        update = Update(1, message=Message(1, User(1, '', False), None, None, text='Text'))
        cdp.process_update(update)
        assert cdp.persistence.test_flag_bot_data
        assert cdp.persistence.test_flag_user_data
        assert not cdp.persistence.test_flag_chat_data

        cdp.persistence.test_flag_bot_data = False
        cdp.persistence.test_flag_user_data = False
        cdp.persistence.test_flag_chat_data = False
        update = Update(1, message=Message(1, None, None, Chat(1, ''), text='Text'))
        cdp.process_update(update)
        assert cdp.persistence.test_flag_bot_data
        assert not cdp.persistence.test_flag_user_data
        assert cdp.persistence.test_flag_chat_data
