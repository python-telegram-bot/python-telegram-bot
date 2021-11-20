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
import logging
from queue import Queue
from threading import current_thread
from time import sleep

import pytest

from telegram import Message, User, Chat, Update, Bot, MessageEntity
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    JobQueue,
    filters,
    Defaults,
    CallbackContext,
    ContextTypes,
    BasePersistence,
    PersistenceInput,
    Dispatcher,
    DispatcherHandlerStop,
    DispatcherBuilder,
    UpdaterBuilder,
)

from telegram._utils.defaultvalue import DEFAULT_FALSE
from telegram.error import TelegramError
from tests.conftest import create_dp
from collections import defaultdict


@pytest.fixture(scope='function')
def dp2(bot):
    yield from create_dp(bot)


class CustomContext(CallbackContext):
    pass


class TestDispatcher:
    message_update = Update(
        1, message=Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Text')
    )
    received = None
    count = 0

    @pytest.fixture(autouse=True, name='reset')
    def reset_fixture(self):
        self.reset()

    def reset(self):
        self.received = None
        self.count = 0

    def error_handler_context(self, update, context):
        self.received = context.error.message

    def error_handler_raise_error(self, update, context):
        raise Exception('Failing bigly')

    def callback_increase_count(self, update, context):
        self.count += 1

    def callback_set_count(self, count):
        def callback(bot, update):
            self.count = count

        return callback

    def callback_raise_error(self, update, context):
        raise TelegramError(update.message.text)

    def callback_received(self, update, context):
        self.received = update.message

    def callback_context(self, update, context):
        if (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(context.update_queue, Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.error, TelegramError)
        ):
            self.received = context.error.message

    def test_slot_behaviour(self, bot, mro_slots):
        dp = DispatcherBuilder().bot(bot).build()
        for at in dp.__slots__:
            at = f"_Dispatcher{at}" if at.startswith('__') and not at.endswith('__') else at
            assert getattr(dp, at, 'err') != 'err', f"got extra slot '{at}'"
        assert len(mro_slots(dp)) == len(set(mro_slots(dp))), "duplicate slot"

    def test_manual_init_warning(self, recwarn):
        Dispatcher(
            bot=None,
            update_queue=None,
            workers=7,
            exception_event=None,
            job_queue=None,
            persistence=None,
            context_types=ContextTypes(),
        )
        assert len(recwarn) == 1
        assert (
            str(recwarn[-1].message)
            == '`Dispatcher` instances should be built via the `DispatcherBuilder`.'
        )
        assert recwarn[0].filename == __file__, "stacklevel is incorrect!"

    @pytest.mark.parametrize(
        'builder',
        (DispatcherBuilder(), UpdaterBuilder()),
        ids=('DispatcherBuilder', 'UpdaterBuilder'),
    )
    def test_less_than_one_worker_warning(self, dp, recwarn, builder):
        builder.bot(dp.bot).workers(0).build()
        assert len(recwarn) == 1
        assert (
            str(recwarn[0].message)
            == 'Asynchronous callbacks can not be processed without at least one worker thread.'
        )
        assert recwarn[0].filename == __file__, "stacklevel is incorrect!"

    def test_builder(self, dp):
        builder_1 = dp.builder()
        builder_2 = dp.builder()
        assert isinstance(builder_1, DispatcherBuilder)
        assert isinstance(builder_2, DispatcherBuilder)
        assert builder_1 is not builder_2

        # Make sure that setting a token doesn't raise an exception
        # i.e. check that the builders are "empty"/new
        builder_1.token(dp.bot.token)
        builder_2.token(dp.bot.token)

    def test_one_context_per_update(self, dp):
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

        dp.add_handler(MessageHandler(filters.Regex('test'), one), group=1)
        dp.add_handler(MessageHandler(None, two), group=2)
        u = Update(1, Message(1, None, None, None, text='test'))
        dp.process_update(u)
        u.message.text = 'something'
        dp.process_update(u)

    def test_error_handler(self, dp):
        dp.add_error_handler(self.error_handler_context)
        error = TelegramError('Unauthorized.')
        dp.update_queue.put(error)
        sleep(0.1)
        assert self.received == 'Unauthorized.'

        # Remove handler
        dp.remove_error_handler(self.error_handler_context)
        self.reset()

        dp.update_queue.put(error)
        sleep(0.1)
        assert self.received is None

    def test_double_add_error_handler(self, dp, caplog):
        dp.add_error_handler(self.error_handler_context)
        with caplog.at_level(logging.DEBUG):
            dp.add_error_handler(self.error_handler_context)
            assert len(caplog.records) == 1
            assert caplog.records[-1].getMessage().startswith('The callback is already registered')

    def test_construction_with_bad_persistence(self, caplog, bot):
        class my_per:
            def __init__(self):
                self.store_data = PersistenceInput(False, False, False, False)

        with pytest.raises(
            TypeError, match='persistence must be based on telegram.ext.BasePersistence'
        ):
            DispatcherBuilder().bot(bot).persistence(my_per()).build()

    def test_error_handler_that_raises_errors(self, dp):
        """
        Make sure that errors raised in error handlers don't break the main loop of the dispatcher
        """
        handler_raise_error = MessageHandler(filters.ALL, self.callback_raise_error)
        handler_increase_count = MessageHandler(filters.ALL, self.callback_increase_count)
        error = TelegramError('Unauthorized.')

        dp.add_error_handler(self.error_handler_raise_error)

        # From errors caused by handlers
        dp.add_handler(handler_raise_error)
        dp.update_queue.put(self.message_update)
        sleep(0.1)

        # From errors in the update_queue
        dp.remove_handler(handler_raise_error)
        dp.add_handler(handler_increase_count)
        dp.update_queue.put(error)
        dp.update_queue.put(self.message_update)
        sleep(0.1)

        assert self.count == 1

    @pytest.mark.parametrize(['run_async', 'expected_output'], [(True, 5), (False, 0)])
    def test_default_run_async_error_handler(self, dp, monkeypatch, run_async, expected_output):
        def mock_async_err_handler(*args, **kwargs):
            self.count = 5

        # set defaults value to dp.bot
        dp.bot._defaults = Defaults(run_async=run_async)
        try:
            dp.add_handler(MessageHandler(filters.ALL, self.callback_raise_error))
            dp.add_error_handler(self.error_handler_context)

            monkeypatch.setattr(dp, 'run_async', mock_async_err_handler)
            dp.process_update(self.message_update)

            assert self.count == expected_output

        finally:
            # reset dp.bot.defaults values
            dp.bot._defaults = None

    @pytest.mark.parametrize(
        ['run_async', 'expected_output'], [(True, 'running async'), (False, None)]
    )
    def test_default_run_async(self, monkeypatch, dp, run_async, expected_output):
        def mock_run_async(*args, **kwargs):
            self.received = 'running async'

        # set defaults value to dp.bot
        dp.bot._defaults = Defaults(run_async=run_async)
        try:
            dp.add_handler(MessageHandler(filters.ALL, lambda u, c: None))
            monkeypatch.setattr(dp, 'run_async', mock_run_async)
            dp.process_update(self.message_update)
            assert self.received == expected_output

        finally:
            # reset defaults value
            dp.bot._defaults = None

    def test_run_async_multiple(self, bot, dp, dp2):
        def get_dispatcher_name(q):
            q.put(current_thread().name)

        q1 = Queue()
        q2 = Queue()

        dp.run_async(get_dispatcher_name, q1)
        dp2.run_async(get_dispatcher_name, q2)

        sleep(0.1)

        name1 = q1.get()
        name2 = q2.get()

        assert name1 != name2

    def test_async_raises_dispatcher_handler_stop(self, dp, recwarn):
        def callback(update, context):
            raise DispatcherHandlerStop()

        dp.add_handler(MessageHandler(filters.ALL, callback, run_async=True))

        dp.update_queue.put(self.message_update)
        sleep(0.1)
        assert len(recwarn) == 1
        assert str(recwarn[-1].message).startswith(
            'DispatcherHandlerStop is not supported with async functions'
        )

    def test_add_async_handler(self, dp):
        dp.add_handler(
            MessageHandler(
                filters.ALL,
                self.callback_received,
                run_async=True,
            )
        )

        dp.update_queue.put(self.message_update)
        sleep(0.1)
        assert self.received == self.message_update.message

    def test_run_async_no_error_handler(self, dp, caplog):
        def func():
            raise RuntimeError('Async Error')

        with caplog.at_level(logging.ERROR):
            dp.run_async(func)
            sleep(0.1)
            assert len(caplog.records) == 1
            assert caplog.records[-1].getMessage().startswith('No error handlers are registered')

    def test_async_handler_async_error_handler_context(self, dp):
        dp.add_handler(MessageHandler(filters.ALL, self.callback_raise_error, run_async=True))
        dp.add_error_handler(self.error_handler_context, run_async=True)

        dp.update_queue.put(self.message_update)
        sleep(2)
        assert self.received == self.message_update.message.text

    def test_async_handler_error_handler_that_raises_error(self, dp, caplog):
        handler = MessageHandler(filters.ALL, self.callback_raise_error, run_async=True)
        dp.add_handler(handler)
        dp.add_error_handler(self.error_handler_raise_error, run_async=False)

        with caplog.at_level(logging.ERROR):
            dp.update_queue.put(self.message_update)
            sleep(0.1)
            assert len(caplog.records) == 1
            assert (
                caplog.records[-1].getMessage().startswith('An error was raised and an uncaught')
            )

        # Make sure that the main loop still runs
        dp.remove_handler(handler)
        dp.add_handler(MessageHandler(filters.ALL, self.callback_increase_count, run_async=True))
        dp.update_queue.put(self.message_update)
        sleep(0.1)
        assert self.count == 1

    def test_async_handler_async_error_handler_that_raises_error(self, dp, caplog):
        handler = MessageHandler(filters.ALL, self.callback_raise_error, run_async=True)
        dp.add_handler(handler)
        dp.add_error_handler(self.error_handler_raise_error, run_async=True)

        with caplog.at_level(logging.ERROR):
            dp.update_queue.put(self.message_update)
            sleep(0.1)
            assert len(caplog.records) == 1
            assert (
                caplog.records[-1].getMessage().startswith('An error was raised and an uncaught')
            )

        # Make sure that the main loop still runs
        dp.remove_handler(handler)
        dp.add_handler(MessageHandler(filters.ALL, self.callback_increase_count, run_async=True))
        dp.update_queue.put(self.message_update)
        sleep(0.1)
        assert self.count == 1

    def test_error_in_handler(self, dp):
        dp.add_handler(MessageHandler(filters.ALL, self.callback_raise_error))
        dp.add_error_handler(self.error_handler_context)

        dp.update_queue.put(self.message_update)
        sleep(0.1)
        assert self.received == self.message_update.message.text

    def test_add_remove_handler(self, dp):
        handler = MessageHandler(filters.ALL, self.callback_increase_count)
        dp.add_handler(handler)
        dp.update_queue.put(self.message_update)
        sleep(0.1)
        assert self.count == 1
        dp.remove_handler(handler)
        dp.update_queue.put(self.message_update)
        assert self.count == 1

    def test_add_remove_handler_non_default_group(self, dp):
        handler = MessageHandler(filters.ALL, self.callback_increase_count)
        dp.add_handler(handler, group=2)
        with pytest.raises(KeyError):
            dp.remove_handler(handler)
        dp.remove_handler(handler, group=2)

    def test_error_start_twice(self, dp):
        assert dp.running
        dp.start()

    def test_handler_order_in_group(self, dp):
        dp.add_handler(MessageHandler(filters.PHOTO, self.callback_set_count(1)))
        dp.add_handler(MessageHandler(filters.ALL, self.callback_set_count(2)))
        dp.add_handler(MessageHandler(filters.TEXT, self.callback_set_count(3)))
        dp.update_queue.put(self.message_update)
        sleep(0.1)
        assert self.count == 2

    def test_groups(self, dp):
        dp.add_handler(MessageHandler(filters.ALL, self.callback_increase_count))
        dp.add_handler(MessageHandler(filters.ALL, self.callback_increase_count), group=2)
        dp.add_handler(MessageHandler(filters.ALL, self.callback_increase_count), group=-1)

        dp.update_queue.put(self.message_update)
        sleep(0.1)
        assert self.count == 3

    def test_add_handler_errors(self, dp):
        handler = 'not a handler'
        with pytest.raises(TypeError, match='handler is not an instance of'):
            dp.add_handler(handler)

        handler = MessageHandler(filters.PHOTO, self.callback_set_count(1))
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

        update = Update(
            1,
            message=Message(
                1,
                None,
                None,
                None,
                text='/start',
                entities=[
                    MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
                ],
                bot=bot,
            ),
        )

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

        def start1(u, c):
            passed.append('start1')
            raise err

        def start2(u, c):
            passed.append('start2')

        def start3(u, c):
            passed.append('start3')

        def error(u, c):
            passed.append('error')
            passed.append(c.error)

        update = Update(
            1,
            message=Message(
                1,
                None,
                None,
                None,
                text='/start',
                entities=[
                    MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
                ],
                bot=bot,
            ),
        )

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

        def start1(u, c):
            passed.append('start1')
            raise err

        def start2(u, c):
            passed.append('start2')

        def start3(u, c):
            passed.append('start3')

        def error(u, c):
            passed.append('error')
            passed.append(c.error)

        update = Update(
            1,
            message=Message(
                1,
                None,
                None,
                None,
                text='/start',
                entities=[
                    MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
                ],
                bot=bot,
            ),
        )

        # If a TelegramException was caught, an error handler should be called and no further
        # handlers from the same group should be called.
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start2), 1)
        dp.add_handler(CommandHandler('start', start3), 2)
        dp.add_error_handler(error)
        dp.process_update(update)
        assert passed == ['start1', 'error', err, 'start3']
        assert passed[2] is err

    def test_error_while_saving_chat_data(self, bot):
        increment = []

        class OwnPersistence(BasePersistence):
            def get_callback_data(self):
                return None

            def update_callback_data(self, data):
                raise Exception

            def get_bot_data(self):
                return {}

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

            def get_conversations(self, name):
                pass

            def update_conversation(self, name, key, new_state):
                pass

            def refresh_user_data(self, user_id, user_data):
                pass

            def refresh_chat_data(self, chat_id, chat_data):
                pass

            def refresh_bot_data(self, bot_data):
                pass

            def flush(self):
                pass

        def start1(u, c):
            pass

        def error(u, c):
            increment.append("error")

        # If updating a user_data or chat_data from a persistence object throws an error,
        # the error handler should catch it

        update = Update(
            1,
            message=Message(
                1,
                None,
                Chat(1, "lala"),
                from_user=User(1, "Test", False),
                text='/start',
                entities=[
                    MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
                ],
                bot=bot,
            ),
        )
        my_persistence = OwnPersistence()
        dp = DispatcherBuilder().bot(bot).persistence(my_persistence).build()
        dp.add_handler(CommandHandler('start', start1))
        dp.add_error_handler(error)
        dp.process_update(update)
        assert increment == ["error", "error", "error", "error"]

    def test_flow_stop_in_error_handler(self, dp, bot):
        passed = []
        err = TelegramError('Telegram error')

        def start1(u, c):
            passed.append('start1')
            raise err

        def start2(u, c):
            passed.append('start2')

        def start3(u, c):
            passed.append('start3')

        def error(u, c):
            passed.append('error')
            passed.append(c.error)
            raise DispatcherHandlerStop

        update = Update(
            1,
            message=Message(
                1,
                None,
                None,
                None,
                text='/start',
                entities=[
                    MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
                ],
                bot=bot,
            ),
        )

        # If a TelegramException was caught, an error handler should be called and no further
        # handlers from the same group should be called.
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start2), 1)
        dp.add_handler(CommandHandler('start', start3), 2)
        dp.add_error_handler(error)
        dp.process_update(update)
        assert passed == ['start1', 'error', err]
        assert passed[2] is err

    def test_sensible_worker_thread_names(self, dp2):
        thread_names = [thread.name for thread in dp2._Dispatcher__async_threads]
        for thread_name in thread_names:
            assert thread_name.startswith(f"Bot:{dp2.bot.id}:worker:")

    def test_error_while_persisting(self, dp, caplog):
        class OwnPersistence(BasePersistence):
            def update(self, data):
                raise Exception('PersistenceError')

            def update_callback_data(self, data):
                self.update(data)

            def update_bot_data(self, data):
                self.update(data)

            def update_chat_data(self, chat_id, data):
                self.update(data)

            def update_user_data(self, user_id, data):
                self.update(data)

            def get_chat_data(self):
                pass

            def get_bot_data(self):
                pass

            def get_user_data(self):
                pass

            def get_callback_data(self):
                pass

            def get_conversations(self, name):
                pass

            def update_conversation(self, name, key, new_state):
                pass

            def refresh_bot_data(self, bot_data):
                pass

            def refresh_user_data(self, user_id, user_data):
                pass

            def refresh_chat_data(self, chat_id, chat_data):
                pass

            def flush(self):
                pass

        def callback(update, context):
            pass

        test_flag = []

        def error(update, context):
            nonlocal test_flag
            test_flag.append(str(context.error) == 'PersistenceError')
            raise Exception('ErrorHandlingError')

        update = Update(
            1, message=Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Text')
        )
        handler = MessageHandler(filters.ALL, callback)
        dp.add_handler(handler)
        dp.add_error_handler(error)

        dp.persistence = OwnPersistence()

        with caplog.at_level(logging.ERROR):
            dp.process_update(update)

        assert test_flag == [True, True, True, True]
        assert len(caplog.records) == 4
        for record in caplog.records:
            message = record.getMessage()
            assert message.startswith('An error was raised and an uncaught')

    def test_persisting_no_user_no_chat(self, dp):
        class OwnPersistence(BasePersistence):
            def __init__(self):
                super().__init__()
                self.test_flag_bot_data = False
                self.test_flag_chat_data = False
                self.test_flag_user_data = False

            def update_bot_data(self, data):
                self.test_flag_bot_data = True

            def update_chat_data(self, chat_id, data):
                self.test_flag_chat_data = True

            def update_user_data(self, user_id, data):
                self.test_flag_user_data = True

            def update_conversation(self, name, key, new_state):
                pass

            def get_conversations(self, name):
                pass

            def get_user_data(self):
                pass

            def get_bot_data(self):
                pass

            def get_chat_data(self):
                pass

            def refresh_bot_data(self, bot_data):
                pass

            def refresh_user_data(self, user_id, user_data):
                pass

            def refresh_chat_data(self, chat_id, chat_data):
                pass

            def get_callback_data(self):
                pass

            def update_callback_data(self, data):
                pass

            def flush(self):
                pass

        def callback(update, context):
            pass

        handler = MessageHandler(filters.ALL, callback)
        dp.add_handler(handler)
        dp.persistence = OwnPersistence()

        update = Update(
            1, message=Message(1, None, None, from_user=User(1, '', False), text='Text')
        )
        dp.process_update(update)
        assert dp.persistence.test_flag_bot_data
        assert dp.persistence.test_flag_user_data
        assert not dp.persistence.test_flag_chat_data

        dp.persistence.test_flag_bot_data = False
        dp.persistence.test_flag_user_data = False
        dp.persistence.test_flag_chat_data = False
        update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
        dp.process_update(update)
        assert dp.persistence.test_flag_bot_data
        assert not dp.persistence.test_flag_user_data
        assert dp.persistence.test_flag_chat_data

    def test_update_persistence_once_per_update(self, monkeypatch, dp):
        def update_persistence(*args, **kwargs):
            self.count += 1

        def dummy_callback(*args):
            pass

        monkeypatch.setattr(dp, 'update_persistence', update_persistence)

        for group in range(5):
            dp.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)

        update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text=None))
        dp.process_update(update)
        assert self.count == 0

        update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='text'))
        dp.process_update(update)
        assert self.count == 1

    def test_update_persistence_all_async(self, monkeypatch, dp):
        def update_persistence(*args, **kwargs):
            self.count += 1

        def dummy_callback(*args, **kwargs):
            pass

        monkeypatch.setattr(dp, 'update_persistence', update_persistence)
        monkeypatch.setattr(dp, 'run_async', dummy_callback)

        for group in range(5):
            dp.add_handler(
                MessageHandler(filters.TEXT, dummy_callback, run_async=True), group=group
            )

        update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
        dp.process_update(update)
        assert self.count == 0

        dp.bot._defaults = Defaults(run_async=True)
        try:
            for group in range(5):
                dp.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)

            update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
            dp.process_update(update)
            assert self.count == 0
        finally:
            dp.bot._defaults = None

    @pytest.mark.parametrize('run_async', [DEFAULT_FALSE, False])
    def test_update_persistence_one_sync(self, monkeypatch, dp, run_async):
        def update_persistence(*args, **kwargs):
            self.count += 1

        def dummy_callback(*args, **kwargs):
            pass

        monkeypatch.setattr(dp, 'update_persistence', update_persistence)
        monkeypatch.setattr(dp, 'run_async', dummy_callback)

        for group in range(5):
            dp.add_handler(
                MessageHandler(filters.TEXT, dummy_callback, run_async=True), group=group
            )
        dp.add_handler(MessageHandler(filters.TEXT, dummy_callback, run_async=run_async), group=5)

        update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
        dp.process_update(update)
        assert self.count == 1

    @pytest.mark.parametrize('run_async,expected', [(DEFAULT_FALSE, 1), (False, 1), (True, 0)])
    def test_update_persistence_defaults_async(self, monkeypatch, dp, run_async, expected):
        def update_persistence(*args, **kwargs):
            self.count += 1

        def dummy_callback(*args, **kwargs):
            pass

        monkeypatch.setattr(dp, 'update_persistence', update_persistence)
        monkeypatch.setattr(dp, 'run_async', dummy_callback)
        dp.bot._defaults = Defaults(run_async=run_async)

        try:
            for group in range(5):
                dp.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)

            update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
            dp.process_update(update)
            assert self.count == expected
        finally:
            dp.bot._defaults = None

    def test_custom_context_init(self, bot):
        cc = ContextTypes(
            context=CustomContext,
            user_data=int,
            chat_data=float,
            bot_data=complex,
        )

        dispatcher = DispatcherBuilder().bot(bot).context_types(cc).build()

        assert isinstance(dispatcher.user_data[1], int)
        assert isinstance(dispatcher.chat_data[1], float)
        assert isinstance(dispatcher.bot_data, complex)

    def test_custom_context_error_handler(self, bot):
        def error_handler(_, context):
            self.received = (
                type(context),
                type(context.user_data),
                type(context.chat_data),
                type(context.bot_data),
            )

        dispatcher = (
            DispatcherBuilder()
            .bot(bot)
            .context_types(
                ContextTypes(
                    context=CustomContext, bot_data=int, user_data=float, chat_data=complex
                )
            )
            .build()
        )
        dispatcher.add_error_handler(error_handler)
        dispatcher.add_handler(MessageHandler(filters.ALL, self.callback_raise_error))

        dispatcher.process_update(self.message_update)
        sleep(0.1)
        assert self.received == (CustomContext, float, complex, int)

    def test_custom_context_handler_callback(self, bot):
        def callback(_, context):
            self.received = (
                type(context),
                type(context.user_data),
                type(context.chat_data),
                type(context.bot_data),
            )

        dispatcher = (
            DispatcherBuilder()
            .bot(bot)
            .context_types(
                ContextTypes(
                    context=CustomContext, bot_data=int, user_data=float, chat_data=complex
                )
            )
            .build()
        )
        dispatcher.add_handler(MessageHandler(filters.ALL, callback))

        dispatcher.process_update(self.message_update)
        sleep(0.1)
        assert self.received == (CustomContext, float, complex, int)
