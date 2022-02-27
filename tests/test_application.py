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
import asyncio
from collections import defaultdict
from queue import Queue

import pytest

from telegram import Bot
from telegram.ext import (
    JobQueue,
    CallbackContext,
    ApplicationBuilder,
    Application,
    ContextTypes,
    PicklePersistence,
    Updater,
)

from telegram.error import TelegramError

from tests.conftest import make_message_update


class CustomContext(CallbackContext):
    pass


class TestApplication:
    message_update = make_message_update(message='Text')
    received = None
    count = 0

    @pytest.fixture(autouse=True, name='reset')
    def reset_fixture(self):
        self.reset()

    def reset(self):
        self.received = None
        self.count = 0

    async def error_handler_context(self, update, context):
        self.received = context.error.message

    async def error_handler_raise_error(self, update, context):
        raise Exception('Failing bigly')

    async def callback_increase_count(self, update, context):
        self.count += 1

    def callback_set_count(self, count):
        async def callback(update, context):
            self.count = count

        return callback

    async def callback_raise_error(self, update, context):
        raise TelegramError(update.message.text)

    async def callback_received(self, update, context):
        self.received = update.message

    async def callback_context(self, update, context):
        if (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(context.update_queue, Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.error, TelegramError)
        ):
            self.received = context.error.message

    def test_slot_behaviour(self, bot, mro_slots):
        app = ApplicationBuilder().bot(bot).build()
        for at in app.__slots__:
            at = f"_Application{at}" if at.startswith('__') and not at.endswith('__') else at
            assert getattr(app, at, 'err') != 'err', f"got extra slot '{at}'"
        assert len(mro_slots(app)) == len(set(mro_slots(app))), "duplicate slot"

    def test_manual_init_warning(self, recwarn, updater):
        Application(
            bot=None,
            update_queue=None,
            job_queue=None,
            persistence=None,
            context_types=ContextTypes(),
            updater=updater,
            concurrent_updates=False,
        )
        assert len(recwarn) == 1
        assert (
            str(recwarn[-1].message)
            == '`Application` instances should be built via the `ApplicationBuilder`.'
        )
        assert recwarn[0].filename == __file__, "stacklevel is incorrect!"

    @pytest.mark.parametrize(
        'concurrent_updates, expected', [(0, 0), (4, 4), (False, 0), (True, 4096)]
    )
    @pytest.mark.filterwarnings("ignore: `Application` instances should")
    def test_init(self, bot, concurrent_updates, expected):
        update_queue = asyncio.Queue()
        job_queue = JobQueue()
        persistence = PicklePersistence('file_path')
        context_types = ContextTypes()
        updater = Updater(bot=bot, update_queue=update_queue)
        app = Application(
            bot=bot,
            update_queue=update_queue,
            job_queue=job_queue,
            persistence=persistence,
            context_types=context_types,
            updater=updater,
            concurrent_updates=concurrent_updates,
        )
        assert app.bot is bot
        assert app.update_queue is update_queue
        assert app.job_queue is job_queue
        assert app.persistence is persistence
        assert app.context_types is context_types
        assert app.updater is updater
        assert app.update_queue is updater.update_queue
        assert app.bot is updater.bot
        assert app.concurrent_updates == expected

        # These should be done by the builder
        assert app.persistence.bot is None
        with pytest.raises(RuntimeError, match='No application was set'):
            app.job_queue.application

        with pytest.raises(ValueError, match='must be a non-negative'):
            Application(
                bot=bot,
                update_queue=update_queue,
                job_queue=job_queue,
                persistence=persistence,
                context_types=context_types,
                updater=updater,
                concurrent_updates=-1,
            )

    @pytest.mark.asyncio
    async def test_initialize(self, bot, monkeypatch):
        """Initialization of persistence is tested eslewhere"""
        # TODO: do this!
        self.test_flag = set()

        async def initialize_bot(*args, **kwargs):
            self.test_flag.add('bot')

        async def initialize_updater(*args, **kwargs):
            self.test_flag.add('updater')

        monkeypatch.setattr(Bot, 'initialize', initialize_bot)
        monkeypatch.setattr(Updater, 'initialize', initialize_updater)

        await ApplicationBuilder().token(bot.token).build().initialize()
        assert self.test_flag == {'bot', 'updater'}

    @pytest.mark.asyncio
    async def test_shutdown(self, bot, monkeypatch):
        """Studown of persistence is tested eslewhere"""
        # TODO: do this!
        self.test_flag = set()

        async def shutdown_bot(*args, **kwargs):
            self.test_flag.add('bot')

        async def shutdown_updater(*args, **kwargs):
            self.test_flag.add('updater')

        monkeypatch.setattr(Bot, 'shutdown', shutdown_bot)
        monkeypatch.setattr(Updater, 'shutdown', shutdown_updater)

        async with ApplicationBuilder().token(bot.token).build():
            pass
        assert self.test_flag == {'bot', 'updater'}

    @pytest.mark.asyncio
    async def test_multiple_inits_and_shutdowns(self, app, monkeypatch):
        self.received = defaultdict(int)

        async def initialize(*args, **kargs):
            self.received['init'] += 1

        async def shutdown(*args, **kwargs):
            self.received['shutdown'] += 1

        monkeypatch.setattr(app.bot, 'initialize', initialize)
        monkeypatch.setattr(app.bot, 'shutdown', shutdown)

        await app.initialize()
        await app.initialize()
        await app.initialize()
        await app.shutdown()
        await app.shutdown()
        await app.shutdown()

        # 2 instead of 1 since `Updater.initialize` also calls bot.init/shutdown
        assert self.received['init'] == 2
        assert self.received['shutdown'] == 2

    @pytest.mark.asyncio
    async def test_multiple_init_cycles(self, app):
        # nothing really to assert - this should just not fail
        async with app:
            await app.bot.get_me()
        async with app:
            await app.bot.get_me()

    @pytest.mark.asyncio
    async def test_start_without_initialize(self, app):
        with pytest.raises(RuntimeError, match='not initialized'):
            await app.start()

    @pytest.mark.asyncio
    async def test_shutdown_while_running(self, app):
        async with app:
            await app.start()
            with pytest.raises(RuntimeError, match='still running'):
                await app.shutdown()
            await app.stop()

    @pytest.mark.asyncio
    async def test_start_not_running_after_failure(self, app):
        class Event(asyncio.Event):
            def set(self) -> None:
                raise Exception('Test Exception')

        async with app:
            with pytest.raises(Exception, match='Test Exception'):
                await app.start(ready=Event())
            assert app.running is False

    @pytest.mark.asyncio
    async def test_context_manager(self, monkeypatch, app):
        self.test_flag = set()

        async def initialize(*args, **kwargs):
            self.test_flag.add('initialize')

        async def shutdown(*args, **kwargs):
            self.test_flag.add('stop')

        monkeypatch.setattr(Application, 'initialize', initialize)
        monkeypatch.setattr(Application, 'shutdown', shutdown)

        async with app:
            pass

        assert self.test_flag == {'initialize', 'stop'}

    @pytest.mark.asyncio
    async def test_context_manager_exception_on_init(self, monkeypatch, app):
        async def initialize(*args, **kwargs):
            raise RuntimeError('initialize')

        async def shutdown(*args):
            self.test_flag = 'stop'

        monkeypatch.setattr(Application, 'initialize', initialize)
        monkeypatch.setattr(Application, 'shutdown', shutdown)

        with pytest.raises(RuntimeError, match='initialize'):
            async with app:
                pass

        assert self.test_flag == 'stop'

    @pytest.mark.parametrize("data", ["chat_data", "user_data"])
    def test_chat_user_data_read_only(self, app, data):
        read_only_data = getattr(app, data)
        writable_data = getattr(app, f"_{data}")
        writable_data[123] = 321
        assert read_only_data == writable_data
        with pytest.raises(TypeError):
            read_only_data[111] = 123

    def test_builder(self, app):
        builder_1 = app.builder()
        builder_2 = app.builder()
        assert isinstance(builder_1, ApplicationBuilder)
        assert isinstance(builder_2, ApplicationBuilder)
        assert builder_1 is not builder_2

        # Make sure that setting a token doesn't raise an exception
        # i.e. check that the builders are "empty"/new
        builder_1.token(app.bot.token)
        builder_2.token(app.bot.token)

    #
    # def test_one_context_per_update(self, app):
    #     def one(update, context):
    #         if update.message.text == 'test':
    #             context.my_flag = True
    #
    #     def two(update, context):
    #         if update.message.text == 'test':
    #             if not hasattr(context, 'my_flag'):
    #                 pytest.fail()
    #         else:
    #             if hasattr(context, 'my_flag'):
    #                 pytest.fail()
    #
    #     app.add_handler(MessageHandler(filters.Regex('test'), one), group=1)
    #     app.add_handler(MessageHandler(None, two), group=2)
    #     u = Update(1, Message(1, None, None, None, text='test'))
    #     app.process_update(u)
    #     u.message.text = 'something'
    #     app.process_update(u)
    #
    # def test_error_handler(self, app):
    #     app.add_error_handler(self.error_handler_context)
    #     error = TelegramError('Unauthorized.')
    #     app.update_queue.put(error)
    #     sleep(0.1)
    #     assert self.received == 'Unauthorized.'
    #
    #     # Remove handler
    #     app.remove_error_handler(self.error_handler_context)
    #     self.reset()
    #
    #     app.update_queue.put(error)
    #     sleep(0.1)
    #     assert self.received is None
    #
    # def test_double_add_error_handler(self, app, caplog):
    #     app.add_error_handler(self.error_handler_context)
    #     with caplog.at_level(logging.DEBUG):
    #         app.add_error_handler(self.error_handler_context)
    #         assert len(caplog.records) == 1
    #         assert caplog.records[-1].getMessage().startswith(
    #         'The callback is already registered')
    #
    # def test_construction_with_bad_persistence(self, caplog, bot):
    #     class my_per:
    #         def __init__(self):
    #             self.store_data = PersistenceInput(False, False, False, False)
    #
    #     with pytest.raises(
    #         TypeError, match='persistence must be based on telegram.ext.BasePersistence'
    #     ):
    #         ApplicationBuilder().bot(bot).persistence(my_per()).build()
    #
    # def test_error_handler_that_raises_errors(self, app):
    #     """
    #     Make sure that errors raised in error handlers don't break the main loop of the
    #     application
    #     """
    #     handler_raise_error = MessageHandler(filters.ALL, self.callback_raise_error)
    #     handler_increase_count = MessageHandler(filters.ALL, self.callback_increase_count)
    #     error = TelegramError('Unauthorized.')
    #
    #     app.add_error_handler(self.error_handler_raise_error)
    #
    #     # From errors caused by handlers
    #     app.add_handler(handler_raise_error)
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #
    #     # From errors in the update_queue
    #     app.remove_handler(handler_raise_error)
    #     app.add_handler(handler_increase_count)
    #     app.update_queue.put(error)
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #
    #     assert self.count == 1
    #
    # @pytest.mark.parametrize(['block', 'expected_output'], [(True, 5), (False, 0)])
    # def test_default_run_async_error_handler(self, app, monkeypatch, block, expected_output):
    #     def mock_async_err_handler(*args, **kwargs):
    #         self.count = 5
    #
    #     # set defaults value to app.bot
    #     app.bot._defaults = Defaults(block=block)
    #     try:
    #         app.add_handler(MessageHandler(filters.ALL, self.callback_raise_error))
    #         app.add_error_handler(self.error_handler_context)
    #
    #         monkeypatch.setattr(app, 'block', mock_async_err_handler)
    #         app.process_update(self.message_update)
    #
    #         assert self.count == expected_output
    #
    #     finally:
    #         # reset app.bot.defaults values
    #         app.bot._defaults = None
    #
    # @pytest.mark.parametrize(
    #     ['block', 'expected_output'], [(True, 'running async'), (False, None)]
    # )
    # def test_default_run_async(self, monkeypatch, app, block, expected_output):
    #     def mock_run_async(*args, **kwargs):
    #         self.received = 'running async'
    #
    #     # set defaults value to app.bot
    #     app.bot._defaults = Defaults(block=block)
    #     try:
    #         app.add_handler(MessageHandler(filters.ALL, lambda u, c: None))
    #         monkeypatch.setattr(app, 'block', mock_run_async)
    #         app.process_update(self.message_update)
    #         assert self.received == expected_output
    #
    #     finally:
    #         # reset defaults value
    #         app.bot._defaults = None
    #
    # def test_run_async_multiple(self, bot, app, dp2):
    #     def get_application_name(q):
    #         q.put(current_thread().name)
    #
    #     q1 = Queue()
    #     q2 = Queue()
    #
    #     app.block(get_application_name, q1)
    #     dp2.block(get_application_name, q2)
    #
    #     sleep(0.1)
    #
    #     name1 = q1.get()
    #     name2 = q2.get()
    #
    #     assert name1 != name2
    #
    # def test_async_raises_application_handler_stop(self, app, recwarn):
    #     def callback(update, context):
    #         raise ApplicationHandlerStop()
    #
    #     app.add_handler(MessageHandler(filters.ALL, callback, block=True))
    #
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #     assert len(recwarn) == 1
    #     assert str(recwarn[-1].message).startswith(
    #         'ApplicationHandlerStop is not supported with async functions'
    #     )
    #
    # def test_add_async_handler(self, app):
    #     app.add_handler(
    #         MessageHandler(
    #             filters.ALL,
    #             self.callback_received,
    #             block=True,
    #         )
    #     )
    #
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #     assert self.received == self.message_update.message
    #
    # def test_run_async_no_error_handler(self, app, caplog):
    #     def func():
    #         raise RuntimeError('Async Error')
    #
    #     with caplog.at_level(logging.ERROR):
    #         app.block(func)
    #         sleep(0.1)
    #         assert len(caplog.records) == 1
    #         assert caplog.records[-1].getMessage().startswith('No error handlers are registered')
    #
    # def test_async_handler_async_error_handler_context(self, app):
    #     app.add_handler(MessageHandler(filters.ALL, self.callback_raise_error, block=True))
    #     app.add_error_handler(self.error_handler_context, block=True)
    #
    #     app.update_queue.put(self.message_update)
    #     sleep(2)
    #     assert self.received == self.message_update.message.text
    #
    # def test_async_handler_error_handler_that_raises_error(self, app, caplog):
    #     handler = MessageHandler(filters.ALL, self.callback_raise_error, block=True)
    #     app.add_handler(handler)
    #     app.add_error_handler(self.error_handler_raise_error, block=False)
    #
    #     with caplog.at_level(logging.ERROR):
    #         app.update_queue.put(self.message_update)
    #         sleep(0.1)
    #         assert len(caplog.records) == 1
    #         assert (
    #             caplog.records[-1].getMessage().startswith('An error was raised and an uncaught')
    #         )
    #
    #     # Make sure that the main loop still runs
    #     app.remove_handler(handler)
    #     app.add_handler(MessageHandler(filters.ALL, self.callback_increase_count, block=True))
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #     assert self.count == 1
    #
    # def test_async_handler_async_error_handler_that_raises_error(self, app, caplog):
    #     handler = MessageHandler(filters.ALL, self.callback_raise_error, block=True)
    #     app.add_handler(handler)
    #     app.add_error_handler(self.error_handler_raise_error, block=True)
    #
    #     with caplog.at_level(logging.ERROR):
    #         app.update_queue.put(self.message_update)
    #         sleep(0.1)
    #         assert len(caplog.records) == 1
    #         assert (
    #             caplog.records[-1].getMessage().startswith('An error was raised and an uncaught')
    #         )
    #
    #     # Make sure that the main loop still runs
    #     app.remove_handler(handler)
    #     app.add_handler(MessageHandler(filters.ALL, self.callback_increase_count, block=True))
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #     assert self.count == 1
    #
    # def test_error_in_handler(self, app):
    #     app.add_handler(MessageHandler(filters.ALL, self.callback_raise_error))
    #     app.add_error_handler(self.error_handler_context)
    #
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #     assert self.received == self.message_update.message.text
    #
    # def test_add_remove_handler(self, app):
    #     handler = MessageHandler(filters.ALL, self.callback_increase_count)
    #     app.add_handler(handler)
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #     assert self.count == 1
    #     app.remove_handler(handler)
    #     app.update_queue.put(self.message_update)
    #     assert self.count == 1
    #
    # def test_add_remove_handler_non_default_group(self, app):
    #     handler = MessageHandler(filters.ALL, self.callback_increase_count)
    #     app.add_handler(handler, group=2)
    #     with pytest.raises(KeyError):
    #         app.remove_handler(handler)
    #     app.remove_handler(handler, group=2)
    #
    # def test_error_start_twice(self, app):
    #     assert app.running
    #     app.start()
    #
    # def test_handler_order_in_group(self, app):
    #     app.add_handler(MessageHandler(filters.PHOTO, self.callback_set_count(1)))
    #     app.add_handler(MessageHandler(filters.ALL, self.callback_set_count(2)))
    #     app.add_handler(MessageHandler(filters.TEXT, self.callback_set_count(3)))
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #     assert self.count == 2
    #
    # def test_groups(self, app):
    #     app.add_handler(MessageHandler(filters.ALL, self.callback_increase_count))
    #     app.add_handler(MessageHandler(filters.ALL, self.callback_increase_count), group=2)
    #     app.add_handler(MessageHandler(filters.ALL, self.callback_increase_count), group=-1)
    #
    #     app.update_queue.put(self.message_update)
    #     sleep(0.1)
    #     assert self.count == 3
    #
    # def test_add_handlers_complex(self, app):
    #     """Tests both add_handler & add_handlers together & confirms the correct insertion
    #     order"""
    #     msg_handler_set_count = MessageHandler(filters.TEXT, self.callback_set_count(1))
    #     msg_handler_inc_count = MessageHandler(filters.PHOTO, self.callback_increase_count)
    #
    #     app.add_handler(msg_handler_set_count, 1)
    #     app.add_handlers((msg_handler_inc_count, msg_handler_inc_count), 1)
    #
    #     photo_update = Update(2, message=Message(2, None, None, photo=True))
    #     # Putting updates in the queue calls the callback
    #     app.update_queue.put(self.message_update)
    #     app.update_queue.put(photo_update)
    #     sleep(0.1)  # sleep is required otherwise there is random behaviour
    #
    #     # Test if handler was added to correct group with correct order-
    #     assert (
    #         self.count == 2
    #         and len(app.handlers[1]) == 3
    #         and app.handlers[1][0] is msg_handler_set_count
    #     )
    #
    #     # Now lets test add_handlers when `handlers` is a dict-
    #     voice_filter_handler_to_check = MessageHandler(filters.VOICE,
    #     self.callback_increase_count)
    #     app.add_handlers(
    #         handlers={
    #             1: [
    #                 MessageHandler(filters.USER, self.callback_increase_count),
    #                 voice_filter_handler_to_check,
    #             ],
    #             -1: [MessageHandler(filters.CAPTION, self.callback_set_count(2))],
    #         }
    #     )
    #
    #     user_update = Update(3, message=Message(3, None, None, from_user=User(1, 's', True)))
    #     voice_update = Update(4, message=Message(4, None, None, voice=True))
    #     app.update_queue.put(user_update)
    #     app.update_queue.put(voice_update)
    #     sleep(0.1)
    #
    #     assert (
    #         self.count == 4
    #         and len(app.handlers[1]) == 5
    #         and app.handlers[1][-1] is voice_filter_handler_to_check
    #     )
    #
    #     app.update_queue.put(Update(5, message=Message(5, None, None, caption='cap')))
    #     sleep(0.1)
    #
    #     assert self.count == 2 and len(app.handlers[-1]) == 1
    #
    #     # Now lets test the errors which can be produced-
    #     with pytest.raises(ValueError, match="The `group` argument"):
    #         app.add_handlers({2: [msg_handler_set_count]}, group=0)
    #     with pytest.raises(ValueError, match="Handlers for group 3"):
    #         app.add_handlers({3: msg_handler_set_count})
    #     with pytest.raises(ValueError, match="The `handlers` argument must be a sequence"):
    #         app.add_handlers({msg_handler_set_count})
    #
    # def test_add_handler_errors(self, app):
    #     handler = 'not a handler'
    #     with pytest.raises(TypeError, match='handler is not an instance of'):
    #         app.add_handler(handler)
    #
    #     handler = MessageHandler(filters.PHOTO, self.callback_set_count(1))
    #     with pytest.raises(TypeError, match='group is not int'):
    #         app.add_handler(handler, 'one')
    #
    # def test_flow_stop(self, app, bot):
    #     passed = []
    #
    #     def start1(b, u):
    #         passed.append('start1')
    #         raise ApplicationHandlerStop
    #
    #     def start2(b, u):
    #         passed.append('start2')
    #
    #     def start3(b, u):
    #         passed.append('start3')
    #
    #     def error(b, u, e):
    #         passed.append('error')
    #         passed.append(e)
    #
    #     update = Update(
    #         1,
    #         message=Message(
    #             1,
    #             None,
    #             None,
    #             None,
    #             text='/start',
    #             entities=[
    #                 MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #             ],
    #             bot=bot,
    #         ),
    #     )
    #
    #     # If Stop raised handlers in other groups should not be called.
    #     passed = []
    #     app.add_handler(CommandHandler('start', start1), 1)
    #     app.add_handler(CommandHandler('start', start3), 1)
    #     app.add_handler(CommandHandler('start', start2), 2)
    #     app.process_update(update)
    #     assert passed == ['start1']
    #
    # def test_exception_in_handler(self, app, bot):
    #     passed = []
    #     err = Exception('General exception')
    #
    #     def start1(u, c):
    #         passed.append('start1')
    #         raise err
    #
    #     def start2(u, c):
    #         passed.append('start2')
    #
    #     def start3(u, c):
    #         passed.append('start3')
    #
    #     def error(u, c):
    #         passed.append('error')
    #         passed.append(c.error)
    #
    #     update = Update(
    #         1,
    #         message=Message(
    #             1,
    #             None,
    #             None,
    #             None,
    #             text='/start',
    #             entities=[
    #                 MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #             ],
    #             bot=bot,
    #         ),
    #     )
    #
    #     # If an unhandled exception was caught, no further handlers from the same group should be
    #     # called. Also, the error handler should be called and receive the exception
    #     passed = []
    #     app.add_handler(CommandHandler('start', start1), 1)
    #     app.add_handler(CommandHandler('start', start2), 1)
    #     app.add_handler(CommandHandler('start', start3), 2)
    #     app.add_error_handler(error)
    #     app.process_update(update)
    #     assert passed == ['start1', 'error', err, 'start3']
    #
    # def test_telegram_error_in_handler(self, app, bot):
    #     passed = []
    #     err = TelegramError('Telegram error')
    #
    #     def start1(u, c):
    #         passed.append('start1')
    #         raise err
    #
    #     def start2(u, c):
    #         passed.append('start2')
    #
    #     def start3(u, c):
    #         passed.append('start3')
    #
    #     def error(u, c):
    #         passed.append('error')
    #         passed.append(c.error)
    #
    #     update = Update(
    #         1,
    #         message=Message(
    #             1,
    #             None,
    #             None,
    #             None,
    #             text='/start',
    #             entities=[
    #                 MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #             ],
    #             bot=bot,
    #         ),
    #     )
    #
    #     # If a TelegramException was caught, an error handler should be called and no further
    #     # handlers from the same group should be called.
    #     app.add_handler(CommandHandler('start', start1), 1)
    #     app.add_handler(CommandHandler('start', start2), 1)
    #     app.add_handler(CommandHandler('start', start3), 2)
    #     app.add_error_handler(error)
    #     app.process_update(update)
    #     assert passed == ['start1', 'error', err, 'start3']
    #     assert passed[2] is err
    #
    # def test_error_while_saving_chat_data(self, bot):
    #     increment = []
    #
    #     class OwnPersistence(BasePersistence):
    #         def get_callback_data(self):
    #             return None
    #
    #         def update_callback_data(self, data):
    #             raise Exception
    #
    #         def get_bot_data(self):
    #             return {}
    #
    #         def update_bot_data(self, data):
    #             raise Exception
    #
    #         def drop_chat_data(self, chat_id):
    #             pass
    #
    #         def drop_user_data(self, user_id):
    #             pass
    #
    #         def get_chat_data(self):
    #             return defaultdict(dict)
    #
    #         def update_chat_data(self, chat_id, data):
    #             raise Exception
    #
    #         def get_user_data(self):
    #             return defaultdict(dict)
    #
    #         def update_user_data(self, user_id, data):
    #             raise Exception
    #
    #         def get_conversations(self, name):
    #             pass
    #
    #         def update_conversation(self, name, key, new_state):
    #             pass
    #
    #         def refresh_user_data(self, user_id, user_data):
    #             pass
    #
    #         def refresh_chat_data(self, chat_id, chat_data):
    #             pass
    #
    #         def refresh_bot_data(self, bot_data):
    #             pass
    #
    #         def flush(self):
    #             pass
    #
    #     def start1(u, c):
    #         pass
    #
    #     def error(u, c):
    #         increment.append("error")
    #
    #     # If updating a user_data or chat_data from a persistence object throws an error,
    #     # the error handler should catch it
    #
    #     update = Update(
    #         1,
    #         message=Message(
    #             1,
    #             None,
    #             Chat(1, "lala"),
    #             from_user=User(1, "Test", False),
    #             text='/start',
    #             entities=[
    #                 MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #             ],
    #             bot=bot,
    #         ),
    #     )
    #     my_persistence = OwnPersistence()
    #     app = ApplicationBuilder().bot(bot).persistence(my_persistence).build()
    #     app.add_handler(CommandHandler('start', start1))
    #     app.add_error_handler(error)
    #     app.process_update(update)
    #     assert increment == ["error", "error", "error", "error"]
    #
    # def test_flow_stop_in_error_handler(self, app, bot):
    #     passed = []
    #     err = TelegramError('Telegram error')
    #
    #     def start1(u, c):
    #         passed.append('start1')
    #         raise err
    #
    #     def start2(u, c):
    #         passed.append('start2')
    #
    #     def start3(u, c):
    #         passed.append('start3')
    #
    #     def error(u, c):
    #         passed.append('error')
    #         passed.append(c.error)
    #         raise ApplicationHandlerStop
    #
    #     update = Update(
    #         1,
    #         message=Message(
    #             1,
    #             None,
    #             None,
    #             None,
    #             text='/start',
    #             entities=[
    #                 MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #             ],
    #             bot=bot,
    #         ),
    #     )
    #
    #     # If a TelegramException was caught, an error handler should be called and no further
    #     # handlers from the same group should be called.
    #     app.add_handler(CommandHandler('start', start1), 1)
    #     app.add_handler(CommandHandler('start', start2), 1)
    #     app.add_handler(CommandHandler('start', start3), 2)
    #     app.add_error_handler(error)
    #     app.process_update(update)
    #     assert passed == ['start1', 'error', err]
    #     assert passed[2] is err
    #
    # def test_sensible_worker_thread_names(self, dp2):
    #     thread_names = [thread.name for thread in dp2._Application__async_threads]
    #     for thread_name in thread_names:
    #         assert thread_name.startswith(f"Bot:{dp2.bot.id}:worker:")
    #
    # @pytest.mark.parametrize(
    #     'message',
    #     [
    #         Message(message_id=1, chat=Chat(id=2, type=None), migrate_from_chat_id=1, date=None),
    #         Message(message_id=1, chat=Chat(id=1, type=None), migrate_to_chat_id=2, date=None),
    #         Message(message_id=1, chat=Chat(id=1, type=None), date=None),
    #         None,
    #     ],
    # )
    # @pytest.mark.parametrize('old_chat_id', [None, 1, "1"])
    # @pytest.mark.parametrize('new_chat_id', [None, 2, "1"])
    # def test_migrate_chat_data(self, app, message: 'Message', old_chat_id: int,
    # new_chat_id: int):
    #     def call(match: str):
    #         with pytest.raises(ValueError, match=match):
    #             app.migrate_chat_data(
    #                 message=message, old_chat_id=old_chat_id, new_chat_id=new_chat_id
    #             )
    #
    #     if message and (old_chat_id or new_chat_id):
    #         call(r"^Message and chat_id pair are mutually exclusive$")
    #         return
    #
    #     if not any((message, old_chat_id, new_chat_id)):
    #         call(r"^chat_id pair or message must be passed$")
    #         return
    #
    #     if message:
    #         if message.migrate_from_chat_id is None and message.migrate_to_chat_id is None:
    #             call(r"^Invalid message instance")
    #             return
    #         effective_old_chat_id = message.migrate_from_chat_id or message.chat.id
    #         effective_new_chat_id = message.migrate_to_chat_id or message.chat.id
    #
    #     elif not (isinstance(old_chat_id, int) and isinstance(new_chat_id, int)):
    #         call(r"^old_chat_id and new_chat_id must be integers$")
    #         return
    #     else:
    #         effective_old_chat_id = old_chat_id
    #         effective_new_chat_id = new_chat_id
    #
    #     app.chat_data[effective_old_chat_id]['key'] = "test"
    #     app.migrate_chat_data(message=message, old_chat_id=old_chat_id, new_chat_id=new_chat_id)
    #     assert effective_old_chat_id not in app.chat_data
    #     assert app.chat_data[effective_new_chat_id]['key'] == "test"
    #
    # def test_error_while_persisting(self, app, caplog):
    #     class OwnPersistence(BasePersistence):
    #         def update(self, data):
    #             raise Exception('PersistenceError')
    #
    #         def update_callback_data(self, data):
    #             self.update(data)
    #
    #         def update_bot_data(self, data):
    #             self.update(data)
    #
    #         def update_chat_data(self, chat_id, data):
    #             self.update(data)
    #
    #         def update_user_data(self, user_id, data):
    #             self.update(data)
    #
    #         def drop_user_data(self, user_id):
    #             pass
    #
    #         def drop_chat_data(self, chat_id):
    #             pass
    #
    #         def get_chat_data(self):
    #             pass
    #
    #         def get_bot_data(self):
    #             pass
    #
    #         def get_user_data(self):
    #             pass
    #
    #         def get_callback_data(self):
    #             pass
    #
    #         def get_conversations(self, name):
    #             pass
    #
    #         def update_conversation(self, name, key, new_state):
    #             pass
    #
    #         def refresh_bot_data(self, bot_data):
    #             pass
    #
    #         def refresh_user_data(self, user_id, user_data):
    #             pass
    #
    #         def refresh_chat_data(self, chat_id, chat_data):
    #             pass
    #
    #         def flush(self):
    #             pass
    #
    #     def callback(update, context):
    #         pass
    #
    #     test_flag = []
    #
    #     def error(update, context):
    #         nonlocal test_flag
    #         test_flag.append(str(context.error) == 'PersistenceError')
    #         raise Exception('ErrorHandlingError')
    #
    #     update = Update(
    #         1, message=Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Text')
    #     )
    #     handler = MessageHandler(filters.ALL, callback)
    #     app.add_handler(handler)
    #     app.add_error_handler(error)
    #
    #     app.persistence = OwnPersistence()
    #
    #     with caplog.at_level(logging.ERROR):
    #         app.process_update(update)
    #
    #     assert test_flag == [True, True, True, True]
    #     assert len(caplog.records) == 4
    #     for record in caplog.records:
    #         message = record.getMessage()
    #         assert message.startswith('An error was raised and an uncaught')
    #
    # def test_persisting_no_user_no_chat(self, app):
    #     class OwnPersistence(BasePersistence):
    #         def __init__(self):
    #             super().__init__()
    #             self.test_flag_bot_data = False
    #             self.test_flag_chat_data = False
    #             self.test_flag_user_data = False
    #
    #         def update_bot_data(self, data):
    #             self.test_flag_bot_data = True
    #
    #         def update_chat_data(self, chat_id, data):
    #             self.test_flag_chat_data = True
    #
    #         def update_user_data(self, user_id, data):
    #             self.test_flag_user_data = True
    #
    #         def update_conversation(self, name, key, new_state):
    #             pass
    #
    #         def drop_chat_data(self, chat_id):
    #             pass
    #
    #         def drop_user_data(self, user_id):
    #             pass
    #
    #         def get_conversations(self, name):
    #             pass
    #
    #         def get_user_data(self):
    #             pass
    #
    #         def get_bot_data(self):
    #             pass
    #
    #         def get_chat_data(self):
    #             pass
    #
    #         def refresh_bot_data(self, bot_data):
    #             pass
    #
    #         def refresh_user_data(self, user_id, user_data):
    #             pass
    #
    #         def refresh_chat_data(self, chat_id, chat_data):
    #             pass
    #
    #         def get_callback_data(self):
    #             pass
    #
    #         def update_callback_data(self, data):
    #             pass
    #
    #         def flush(self):
    #             pass
    #
    #     def callback(update, context):
    #         pass
    #
    #     handler = MessageHandler(filters.ALL, callback)
    #     app.add_handler(handler)
    #     app.persistence = OwnPersistence()
    #
    #     update = Update(
    #         1, message=Message(1, None, None, from_user=User(1, '', False), text='Text')
    #     )
    #     app.process_update(update)
    #     assert app.persistence.test_flag_bot_data
    #     assert app.persistence.test_flag_user_data
    #     assert not app.persistence.test_flag_chat_data
    #
    #     app.persistence.test_flag_bot_data = False
    #     app.persistence.test_flag_user_data = False
    #     app.persistence.test_flag_chat_data = False
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
    #     app.process_update(update)
    #     assert app.persistence.test_flag_bot_data
    #     assert not app.persistence.test_flag_user_data
    #     assert app.persistence.test_flag_chat_data
    #
    # @pytest.mark.parametrize(
    #     "c_id,expected",
    #     [(321, {222: "remove_me"}), (111, {321: {'not_empty': 'no'}, 222: "remove_me"})],
    #     ids=["test chat_id removal", "test no key in data (no error)"],
    # )
    # def test_drop_chat_data(self, app, c_id, expected):
    #     app._chat_data.update({321: {'not_empty': 'no'}, 222: "remove_me"})
    #     app.drop_chat_data(c_id)
    #     assert app.chat_data == expected
    #
    # @pytest.mark.parametrize(
    #     "u_id,expected",
    #     [(321, {222: "remove_me"}), (111, {321: {'not_empty': 'no'}, 222: "remove_me"})],
    #     ids=["test user_id removal", "test no key in data (no error)"],
    # )
    # def test_drop_user_data(self, app, u_id, expected):
    #     app._user_data.update({321: {'not_empty': 'no'}, 222: "remove_me"})
    #     app.drop_user_data(u_id)
    #     assert app.user_data == expected
    #
    # def test_update_persistence_once_per_update(self, monkeypatch, app):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #
    #     for group in range(5):
    #         app.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)
    #
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text=None))
    #     app.process_update(update)
    #     assert self.count == 0
    #
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='text'))
    #     app.process_update(update)
    #     assert self.count == 1
    #
    # def test_update_persistence_all_async(self, monkeypatch, app):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args, **kwargs):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #     monkeypatch.setattr(app, 'block', dummy_callback)
    #
    #     for group in range(5):
    #         app.add_handler(
    #             MessageHandler(filters.TEXT, dummy_callback, block=True), group=group
    #         )
    #
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
    #     app.process_update(update)
    #     assert self.count == 0
    #
    #     app.bot._defaults = Defaults(block=True)
    #     try:
    #         for group in range(5):
    #             app.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)
    #
    #         update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None,
    #         text='Text'))
    #         app.process_update(update)
    #         assert self.count == 0
    #     finally:
    #         app.bot._defaults = None
    #
    # @pytest.mark.parametrize('block', [DEFAULT_FALSE, False])
    # def test_update_persistence_one_sync(self, monkeypatch, app, block):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args, **kwargs):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #     monkeypatch.setattr(app, 'block', dummy_callback)
    #
    #     for group in range(5):
    #         app.add_handler(
    #             MessageHandler(filters.TEXT, dummy_callback, block=True), group=group
    #         )
    #     app.add_handler(MessageHandler(filters.TEXT, dummy_callback, block=block),group=5)
    #
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
    #     app.process_update(update)
    #     assert self.count == 1
    #
    # @pytest.mark.parametrize('block,expected', [(DEFAULT_FALSE, 1), (False, 1), (True, 0)])
    # def test_update_persistence_defaults_async(self, monkeypatch, app, block, expected):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args, **kwargs):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #     monkeypatch.setattr(app, 'block', dummy_callback)
    #     app.bot._defaults = Defaults(block=block)
    #
    #     try:
    #         for group in range(5):
    #             app.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)
    #
    #         update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None,
    #         text='Text'))
    #         app.process_update(update)
    #         assert self.count == expected
    #     finally:
    #         app.bot._defaults = None
    #
    # def test_custom_context_init(self, bot):
    #     cc = ContextTypes(
    #         context=CustomContext,
    #         user_data=int,
    #         chat_data=float,
    #         bot_data=complex,
    #     )
    #
    #     application = ApplicationBuilder().bot(bot).context_types(cc).build()
    #
    #     assert isinstance(application.user_data[1], int)
    #     assert isinstance(application.chat_data[1], float)
    #     assert isinstance(application.bot_data, complex)
    #
    # def test_custom_context_error_handler(self, bot):
    #     def error_handler(_, context):
    #         self.received = (
    #             type(context),
    #             type(context.user_data),
    #             type(context.chat_data),
    #             type(context.bot_data),
    #         )
    #
    #     application = (
    #         ApplicationBuilder()
    #         .bot(bot)
    #         .context_types(
    #             ContextTypes(
    #                 context=CustomContext, bot_data=int, user_data=float, chat_data=complex
    #             )
    #         )
    #         .build()
    #     )
    #     application.add_error_handler(error_handler)
    #     application.add_handler(MessageHandler(filters.ALL, self.callback_raise_error))
    #
    #     application.process_update(self.message_update)
    #     sleep(0.1)
    #     assert self.received == (CustomContext, float, complex, int)
    #
    # def test_custom_context_handler_callback(self, bot):
    #     def callback(_, context):
    #         self.received = (
    #             type(context),
    #             type(context.user_data),
    #             type(context.chat_data),
    #             type(context.bot_data),
    #         )
    #
    #     application = (
    #         ApplicationBuilder()
    #         .bot(bot)
    #         .context_types(
    #             ContextTypes(
    #                 context=CustomContext, bot_data=int, user_data=float, chat_data=complex
    #             )
    #         )
    #         .build()
    #     )
    #     application.add_handler(MessageHandler(filters.ALL, callback))
    #
    #     application.process_update(self.message_update)
    #     sleep(0.1)
    #     assert self.received == (CustomContext, float, complex, int)
