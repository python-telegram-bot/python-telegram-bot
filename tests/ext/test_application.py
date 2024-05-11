#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
"""The integration of persistence into the application is tested in test_basepersistence.
"""
import asyncio
import inspect
import logging
import os
import platform
import signal
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path
from queue import Queue
from random import randrange
from threading import Thread
from typing import Optional

import pytest

from telegram import Bot, Chat, Message, MessageEntity, User
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ApplicationHandlerStop,
    BaseHandler,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    Defaults,
    JobQueue,
    MessageHandler,
    PicklePersistence,
    SimpleUpdateProcessor,
    TypeHandler,
    Updater,
    filters,
)
from telegram.warnings import PTBDeprecationWarning, PTBUserWarning
from tests.auxil.asyncio_helpers import call_after
from tests.auxil.build_messages import make_message_update
from tests.auxil.files import PROJECT_ROOT_PATH
from tests.auxil.networking import send_webhook_message
from tests.auxil.pytest_classes import make_bot
from tests.auxil.slots import mro_slots


class CustomContext(CallbackContext):
    pass


class TestApplication:
    """The integration of persistence into the application is tested in
    test_basepersistence.
    """

    message_update = make_message_update(message="Text")
    received = None
    count = 0

    @pytest.fixture(autouse=True, name="reset")
    def _reset_fixture(self):
        self.reset()

    def reset(self):
        self.received = None
        self.count = 0

    async def error_handler_context(self, update, context):
        self.received = context.error.message

    async def error_handler_raise_error(self, update, context):
        raise Exception("Failing bigly")

    async def callback_increase_count(self, update, context):
        self.count += 1

    def callback_set_count(self, count, sleep: Optional[float] = None):
        async def callback(update, context):
            if sleep:
                await asyncio.sleep(sleep)
            self.count = count

        return callback

    def callback_raise_error(self, error_message: str):
        async def callback(update, context):
            raise TelegramError(error_message)

        return callback

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

    async def test_slot_behaviour(self, one_time_bot):
        async with ApplicationBuilder().bot(one_time_bot).build() as app:
            for at in app.__slots__:
                attr = f"_Application{at}" if at.startswith("__") and not at.endswith("__") else at
                assert getattr(app, attr, "err") != "err", f"got extra slot '{attr}'"
            assert len(mro_slots(app)) == len(set(mro_slots(app))), "duplicate slot"

    def test_manual_init_warning(self, recwarn, updater):
        Application(
            bot=None,
            update_queue=None,
            job_queue=None,
            persistence=None,
            context_types=ContextTypes(),
            updater=updater,
            update_processor=False,
            post_init=None,
            post_shutdown=None,
            post_stop=None,
        )
        assert len(recwarn) == 1
        assert (
            str(recwarn[-1].message)
            == "`Application` instances should be built via the `ApplicationBuilder`."
        )
        assert recwarn[0].category is PTBUserWarning
        assert recwarn[0].filename == __file__, "stacklevel is incorrect!"

    @pytest.mark.filterwarnings("ignore: `Application` instances should")
    def test_init(self, one_time_bot):
        update_queue = asyncio.Queue()
        job_queue = JobQueue()
        persistence = PicklePersistence("file_path")
        context_types = ContextTypes()
        update_processor = SimpleUpdateProcessor(1)
        updater = Updater(bot=one_time_bot, update_queue=update_queue)

        async def post_init(application: Application) -> None:
            pass

        async def post_shutdown(application: Application) -> None:
            pass

        async def post_stop(application: Application) -> None:
            pass

        app = Application(
            bot=one_time_bot,
            update_queue=update_queue,
            job_queue=job_queue,
            persistence=persistence,
            context_types=context_types,
            updater=updater,
            update_processor=update_processor,
            post_init=post_init,
            post_shutdown=post_shutdown,
            post_stop=post_stop,
        )
        assert app.bot is one_time_bot
        assert app.update_queue is update_queue
        assert app.job_queue is job_queue
        assert app.persistence is persistence
        assert app.context_types is context_types
        assert app.updater is updater
        assert app.update_queue is updater.update_queue
        assert app.bot is updater.bot
        assert app.update_processor is update_processor
        assert app.post_init is post_init
        assert app.post_shutdown is post_shutdown
        assert app.post_stop is post_stop

        # These should be done by the builder
        assert app.persistence.bot is None
        with pytest.raises(RuntimeError, match="No application was set"):
            app.job_queue.application

        assert isinstance(app.bot_data, dict)
        assert isinstance(app.chat_data[1], dict)
        assert isinstance(app.user_data[1], dict)

    async def test_repr(self, app):
        assert repr(app) == f"PytestApplication[bot={app.bot!r}]"

    def test_job_queue(self, one_time_bot, app, recwarn):
        expected_warning = (
            "No `JobQueue` set up. To use `JobQueue`, you must install PTB via "
            '`pip install "python-telegram-bot[job-queue]"`.'
        )
        assert app.job_queue is app._job_queue
        application = ApplicationBuilder().bot(one_time_bot).job_queue(None).build()
        assert application.job_queue is None
        assert len(recwarn) == 1
        assert str(recwarn[0].message) == expected_warning
        assert recwarn[0].category is PTBUserWarning
        assert recwarn[0].filename == __file__, "wrong stacklevel"

    def test_custom_context_init(self, one_time_bot):
        cc = ContextTypes(
            context=CustomContext,
            user_data=int,
            chat_data=float,
            bot_data=complex,
        )

        application = ApplicationBuilder().bot(one_time_bot).context_types(cc).build()

        assert isinstance(application.user_data[1], int)
        assert isinstance(application.chat_data[1], float)
        assert isinstance(application.bot_data, complex)

    @pytest.mark.parametrize("updater", [True, False])
    async def test_initialize(self, one_time_bot, monkeypatch, updater):
        """Initialization of persistence is tested test_basepersistence"""
        self.test_flag = set()

        async def after_initialize_bot(*args, **kwargs):
            self.test_flag.add("bot")

        async def after_initialize_update_processor(*args, **kwargs):
            self.test_flag.add("update_processor")

        async def after_initialize_updater(*args, **kwargs):
            self.test_flag.add("updater")

        update_processor = SimpleUpdateProcessor(1)
        monkeypatch.setattr(Bot, "initialize", call_after(Bot.initialize, after_initialize_bot))
        monkeypatch.setattr(
            SimpleUpdateProcessor,
            "initialize",
            call_after(SimpleUpdateProcessor.initialize, after_initialize_update_processor),
        )
        monkeypatch.setattr(
            Updater, "initialize", call_after(Updater.initialize, after_initialize_updater)
        )
        if updater:
            app = (
                ApplicationBuilder().bot(one_time_bot).concurrent_updates(update_processor).build()
            )
            await app.initialize()
            assert self.test_flag == {"bot", "update_processor", "updater"}
            await app.shutdown()
        else:
            app = (
                ApplicationBuilder()
                .bot(one_time_bot)
                .updater(None)
                .concurrent_updates(update_processor)
                .build()
            )
            await app.initialize()
            assert self.test_flag == {"bot", "update_processor"}
            await app.shutdown()

    @pytest.mark.parametrize("updater", [True, False])
    async def test_shutdown(self, one_time_bot, monkeypatch, updater):
        """Shutdown of persistence is tested in test_basepersistence"""
        self.test_flag = set()

        def after_bot_shutdown(*args, **kwargs):
            self.test_flag.add("bot")

        def after_shutdown_update_processor(*args, **kwargs):
            self.test_flag.add("update_processor")

        def after_updater_shutdown(*args, **kwargs):
            self.test_flag.add("updater")

        update_processor = SimpleUpdateProcessor(1)
        monkeypatch.setattr(Bot, "shutdown", call_after(Bot.shutdown, after_bot_shutdown))
        monkeypatch.setattr(
            SimpleUpdateProcessor,
            "shutdown",
            call_after(SimpleUpdateProcessor.shutdown, after_shutdown_update_processor),
        )
        monkeypatch.setattr(
            Updater, "shutdown", call_after(Updater.shutdown, after_updater_shutdown)
        )

        if updater:
            async with ApplicationBuilder().bot(one_time_bot).concurrent_updates(
                update_processor
            ).build():
                pass
            assert self.test_flag == {"bot", "update_processor", "updater"}
        else:
            async with ApplicationBuilder().bot(one_time_bot).updater(None).concurrent_updates(
                update_processor
            ).build():
                pass
            assert self.test_flag == {"bot", "update_processor"}

    async def test_multiple_inits_and_shutdowns(self, app, monkeypatch):
        self.received = defaultdict(int)

        async def after_initialize(*args, **kargs):
            self.received["init"] += 1

        async def after_shutdown(*args, **kwargs):
            self.received["shutdown"] += 1

        monkeypatch.setattr(
            app.bot, "initialize", call_after(app.bot.initialize, after_initialize)
        )
        monkeypatch.setattr(app.bot, "shutdown", call_after(app.bot.shutdown, after_shutdown))

        await app.initialize()
        await app.initialize()
        await app.initialize()
        await app.shutdown()
        await app.shutdown()
        await app.shutdown()

        # 2 instead of 1 since `Updater.initialize` also calls bot.init/shutdown
        assert self.received["init"] == 2
        assert self.received["shutdown"] == 2

    async def test_multiple_init_cycles(self, app):
        # nothing really to assert - this should just not fail
        async with app:
            await app.bot.get_me()
        async with app:
            await app.bot.get_me()

    async def test_start_without_initialize(self, app):
        with pytest.raises(RuntimeError, match="not initialized"):
            await app.start()

    async def test_shutdown_while_running(self, app):
        async with app:
            await app.start()
            with pytest.raises(RuntimeError, match="still running"):
                await app.shutdown()
            await app.stop()

    async def test_start_not_running_after_failure(self, one_time_bot, monkeypatch):
        def start(_):
            raise Exception("Test Exception")

        monkeypatch.setattr(JobQueue, "start", start)
        app = ApplicationBuilder().bot(one_time_bot).job_queue(JobQueue()).build()

        async with app:
            with pytest.raises(Exception, match="Test Exception"):
                await app.start()
            assert app.running is False

    async def test_context_manager(self, monkeypatch, app):
        self.test_flag = set()

        async def after_initialize(*args, **kwargs):
            self.test_flag.add("initialize")

        async def after_shutdown(*args, **kwargs):
            self.test_flag.add("stop")

        monkeypatch.setattr(
            Application, "initialize", call_after(Application.initialize, after_initialize)
        )
        monkeypatch.setattr(
            Application, "shutdown", call_after(Application.shutdown, after_shutdown)
        )

        async with app:
            pass

        assert self.test_flag == {"initialize", "stop"}

    async def test_context_manager_exception_on_init(self, monkeypatch, app):
        async def after_initialize(*args, **kwargs):
            raise RuntimeError("initialize")

        async def after_shutdown(*args):
            self.test_flag = "stop"

        monkeypatch.setattr(
            Application, "initialize", call_after(Application.initialize, after_initialize)
        )
        monkeypatch.setattr(
            Application, "shutdown", call_after(Application.shutdown, after_shutdown)
        )

        with pytest.raises(RuntimeError, match="initialize"):
            async with app:
                pass

        assert self.test_flag == "stop"

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

    @pytest.mark.parametrize("job_queue", [True, False])
    @pytest.mark.filterwarnings("ignore::telegram.warnings.PTBUserWarning")
    async def test_start_stop_processing_updates(self, one_time_bot, job_queue):
        # TODO: repeat a similar test for create_task, persistence processing and job queue
        if job_queue:
            app = ApplicationBuilder().bot(one_time_bot).build()
        else:
            app = ApplicationBuilder().bot(one_time_bot).job_queue(None).build()

        async def callback(u, c):
            self.received = u

        assert not app.running
        assert not app.updater.running
        if job_queue:
            assert not app.job_queue.scheduler.running
        else:
            assert app.job_queue is None
        app.add_handler(TypeHandler(object, callback))

        await app.update_queue.put(1)
        await asyncio.sleep(0.05)
        assert not app.update_queue.empty()
        assert self.received is None

        async with app:
            await app.start()
            assert app.running
            tasks = asyncio.all_tasks()
            assert any(":update_fetcher" in task.get_name() for task in tasks)
            if job_queue:
                assert app.job_queue.scheduler.running
            else:
                assert app.job_queue is None
            # app.start() should not start the updater!
            assert not app.updater.running
            await asyncio.sleep(0.05)
            assert app.update_queue.empty()
            assert self.received == 1
            try:  # just in case start_polling times out
                await app.updater.start_polling()
            except TelegramError:
                pytest.xfail("start_polling timed out")
            else:
                await app.stop()
            assert not app.running
            # app.stop() should not stop the updater!
            assert app.updater.running
            if job_queue:
                assert not app.job_queue.scheduler.running
            else:
                assert app.job_queue is None
            await app.update_queue.put(2)
            await asyncio.sleep(0.05)
            assert not app.update_queue.empty()
            assert self.received != 2
            assert self.received == 1

            await app.updater.stop()

    async def test_error_start_stop_twice(self, app):
        async with app:
            await app.start()
            assert app.running
            with pytest.raises(RuntimeError, match="already running"):
                await app.start()

            await app.stop()
            assert not app.running
            with pytest.raises(RuntimeError, match="not running"):
                await app.stop()

    async def test_one_context_per_update(self, app):
        self.received = None

        async def one(update, context):
            self.received = context

        async def two(update, context):
            if update.message.text == "test":
                if context is not self.received:
                    pytest.fail("Expected same context object, got different")
            elif context is self.received:
                pytest.fail("First handler was wrongly called")

        async with app:
            app.add_handler(MessageHandler(filters.Regex("test"), one), group=1)
            app.add_handler(MessageHandler(filters.ALL, two), group=2)
            u = make_message_update(message="test")
            await app.process_update(u)
            self.received = None
            u = make_message_update(message="something")
            await app.process_update(u)

    def test_add_handler_errors(self, app):
        handler = "not a handler"
        with pytest.raises(TypeError, match="handler is not an instance of"):
            app.add_handler(handler)

        handler = MessageHandler(filters.PHOTO, self.callback_set_count(1))
        with pytest.raises(TypeError, match="group is not int"):
            app.add_handler(handler, "one")

    @pytest.mark.parametrize("group_empty", [True, False])
    async def test_add_remove_handler(self, app, group_empty):
        handler = MessageHandler(filters.ALL, self.callback_increase_count)
        app.add_handler(handler)
        if not group_empty:
            app.add_handler(handler)

        async with app:
            await app.start()
            await app.update_queue.put(self.message_update)
            await asyncio.sleep(0.05)
            assert self.count == 1
            app.remove_handler(handler)
            assert (0 in app.handlers) == (not group_empty)
            await app.update_queue.put(self.message_update)
            assert self.count == 1
            await app.stop()

    async def test_add_remove_handler_non_default_group(self, app):
        handler = MessageHandler(filters.ALL, self.callback_increase_count)
        app.add_handler(handler, group=2)
        with pytest.raises(KeyError):
            app.remove_handler(handler)
        app.remove_handler(handler, group=2)

    async def test_handler_order_in_group(self, app):
        app.add_handler(MessageHandler(filters.PHOTO, self.callback_set_count(1)))
        app.add_handler(MessageHandler(filters.ALL, self.callback_set_count(2)))
        app.add_handler(MessageHandler(filters.TEXT, self.callback_set_count(3)))
        async with app:
            await app.start()
            await app.update_queue.put(self.message_update)
            await asyncio.sleep(0.05)
            assert self.count == 2
            await app.stop()

    async def test_groups(self, app):
        app.add_handler(MessageHandler(filters.ALL, self.callback_increase_count))
        app.add_handler(MessageHandler(filters.ALL, self.callback_increase_count), group=2)
        app.add_handler(MessageHandler(filters.ALL, self.callback_increase_count), group=-1)

        async with app:
            await app.start()
            await app.update_queue.put(self.message_update)
            await asyncio.sleep(0.05)
            assert self.count == 3
            await app.stop()

    async def test_add_handlers(self, app):
        """Tests both add_handler & add_handlers together & confirms the correct insertion
        order"""
        msg_handler_set_count = MessageHandler(filters.TEXT, self.callback_set_count(1))
        msg_handler_inc_count = MessageHandler(filters.PHOTO, self.callback_increase_count)

        app.add_handler(msg_handler_set_count, 1)
        app.add_handlers((msg_handler_inc_count, msg_handler_inc_count), 1)

        photo_update = make_message_update(message=Message(2, None, None, photo=(True,)))

        async with app:
            await app.start()
            # Putting updates in the queue calls the callback
            await app.update_queue.put(self.message_update)
            await app.update_queue.put(photo_update)
            await asyncio.sleep(0.05)  # sleep is required otherwise there is random behaviour

            # Test if handler was added to correct group with correct order-
            assert self.count == 2
            assert len(app.handlers[1]) == 3
            assert app.handlers[1][0] is msg_handler_set_count

            # Now lets test add_handlers when `handlers` is a dict-
            voice_filter_handler_to_check = MessageHandler(
                filters.VOICE, self.callback_increase_count
            )
            app.add_handlers(
                handlers={
                    1: [
                        MessageHandler(filters.USER, self.callback_increase_count),
                        voice_filter_handler_to_check,
                    ],
                    -1: [MessageHandler(filters.CAPTION, self.callback_set_count(2))],
                }
            )

            user_update = make_message_update(
                message=Message(3, None, None, from_user=User(1, "s", True))
            )
            voice_update = make_message_update(message=Message(4, None, None, voice=True))
            await app.update_queue.put(user_update)
            await app.update_queue.put(voice_update)
            await asyncio.sleep(0.05)

            assert self.count == 4
            assert len(app.handlers[1]) == 5
            assert app.handlers[1][-1] is voice_filter_handler_to_check

            await app.update_queue.put(
                make_message_update(message=Message(5, None, None, caption="cap"))
            )
            await asyncio.sleep(0.05)

            assert self.count == 2
            assert len(app.handlers[-1]) == 1

            # Now lets test the errors which can be produced-
            with pytest.raises(ValueError, match="The `group` argument"):
                app.add_handlers({2: [msg_handler_set_count]}, group=0)
            with pytest.raises(ValueError, match="Handlers for group 3"):
                app.add_handlers({3: msg_handler_set_count})
            with pytest.raises(ValueError, match="The `handlers` argument must be a sequence"):
                app.add_handlers({msg_handler_set_count})

            await app.stop()

    async def test_check_update(self, app):
        class TestHandler(BaseHandler):
            def check_update(_, update: object):
                self.received = object()

            def handle_update(
                _,
                update,
                application,
                check_result,
                context,
            ):
                assert application is app
                assert check_result is not self.received

        async with app:
            app.add_handler(TestHandler("callback"))
            await app.start()
            await app.update_queue.put(object())
            await asyncio.sleep(0.05)
            await app.stop()

    async def test_flow_stop(self, app, one_time_bot):
        passed = []

        async def start1(b, u):
            passed.append("start1")
            raise ApplicationHandlerStop

        async def start2(b, u):
            passed.append("start2")

        async def start3(b, u):
            passed.append("start3")

        update = make_message_update(
            message=Message(
                1,
                None,
                None,
                None,
                text="/start",
                entities=[
                    MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len("/start"))
                ],
            ),
        )
        await one_time_bot.initialize()
        update.message.set_bot(one_time_bot)

        async with app:
            # If ApplicationHandlerStop raised handlers in other groups should not be called.
            passed = []
            app.add_handler(CommandHandler("start", start1), 1)
            app.add_handler(CommandHandler("start", start3), 1)
            app.add_handler(CommandHandler("start", start2), 2)
            await app.process_update(update)
            assert passed == ["start1"]

    async def test_flow_stop_by_error_handler(self, app):
        passed = []
        exception = Exception("General exception")

        async def start1(u, c):
            passed.append("start1")
            raise exception

        async def start2(u, c):
            passed.append("start2")

        async def start3(u, c):
            passed.append("start3")

        async def error(u, c):
            passed.append("error")
            passed.append(c.error)
            raise ApplicationHandlerStop

        async with app:
            # If ApplicationHandlerStop raised handlers in other groups should not be called.
            passed = []
            app.add_error_handler(error)
            app.add_handler(TypeHandler(object, start1), 1)
            app.add_handler(TypeHandler(object, start2), 1)
            app.add_handler(TypeHandler(object, start3), 2)
            await app.process_update(1)
            assert passed == ["start1", "error", exception]

    async def test_error_in_handler_part_1(self, app):
        app.add_handler(
            MessageHandler(
                filters.ALL,
                self.callback_raise_error(error_message=self.message_update.message.text),
            )
        )
        app.add_handler(MessageHandler(filters.ALL, self.callback_set_count(42)), group=1)
        app.add_error_handler(self.error_handler_context)

        async with app:
            await app.start()
            await app.update_queue.put(self.message_update)
            await asyncio.sleep(0.05)
            await app.stop()

        assert self.received == self.message_update.message.text
        # Higher groups should still be called
        assert self.count == 42

    async def test_error_in_handler_part_2(self, app, one_time_bot):
        passed = []
        err = Exception("General exception")

        async def start1(u, c):
            passed.append("start1")
            raise err

        async def start2(u, c):
            passed.append("start2")

        async def start3(u, c):
            passed.append("start3")

        async def error(u, c):
            passed.append("error")
            passed.append(c.error)

        update = make_message_update(
            message=Message(
                1,
                None,
                None,
                None,
                text="/start",
                entities=[
                    MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len("/start"))
                ],
            ),
        )
        await one_time_bot.initialize()
        update.message.set_bot(one_time_bot)

        async with app:
            # If an unhandled exception was caught, no further handlers from the same group should
            # be called. Also, the error handler should be called and receive the exception
            passed = []
            app.add_handler(CommandHandler("start", start1), 1)
            app.add_handler(CommandHandler("start", start2), 1)
            app.add_handler(CommandHandler("start", start3), 2)
            app.add_error_handler(error)
            await app.process_update(update)
            assert passed == ["start1", "error", err, "start3"]

    @pytest.mark.parametrize("block", [True, False])
    async def test_error_handler(self, app, block):
        app.add_error_handler(self.error_handler_context)
        app.add_handler(TypeHandler(object, self.callback_raise_error("TestError"), block=block))

        async with app:
            await app.start()
            await app.update_queue.put(1)
            await asyncio.sleep(0.05)
            assert self.received == "TestError"

            # Remove handler
            app.remove_error_handler(self.error_handler_context)
            self.reset()

            await app.update_queue.put(1)
            await asyncio.sleep(0.05)
            assert self.received is None

            await app.stop()

    def test_double_add_error_handler(self, app, caplog):
        app.add_error_handler(self.error_handler_context)
        with caplog.at_level(logging.DEBUG):
            app.add_error_handler(self.error_handler_context)
            assert len(caplog.records) == 1
            assert caplog.records[-1].name == "telegram.ext.Application"
            assert caplog.records[-1].getMessage().startswith("The callback is already registered")

    async def test_error_handler_that_raises_errors(self, app, caplog):
        """Make sure that errors raised in error handlers don't break the main loop of the
        application
        """
        handler_raise_error = TypeHandler(
            int, self.callback_raise_error(error_message="TestError")
        )
        handler_increase_count = TypeHandler(str, self.callback_increase_count)

        app.add_error_handler(self.error_handler_raise_error)
        app.add_handler(handler_raise_error)
        app.add_handler(handler_increase_count)

        with caplog.at_level(logging.ERROR):
            async with app:
                await app.start()
                await app.update_queue.put(1)
                await asyncio.sleep(0.05)
                assert self.count == 0
                assert self.received is None
                assert len(caplog.records) > 0
                assert any(
                    "uncaught error was raised while handling the error with an error_handler"
                    in record.getMessage()
                    and record.name == "telegram.ext.Application"
                    for record in caplog.records
                )

                await app.update_queue.put("1")
                self.received = None
                caplog.clear()
                await asyncio.sleep(0.05)
                assert self.count == 1
                assert self.received is None
                assert not caplog.records

                await app.stop()

    async def test_custom_context_error_handler(self, one_time_bot):
        async def error_handler(_, context):
            self.received = (
                type(context),
                type(context.user_data),
                type(context.chat_data),
                type(context.bot_data),
            )

        application = (
            ApplicationBuilder()
            .bot(one_time_bot)
            .context_types(
                ContextTypes(
                    context=CustomContext, bot_data=int, user_data=float, chat_data=complex
                )
            )
            .build()
        )
        application.add_error_handler(error_handler)
        application.add_handler(
            MessageHandler(filters.ALL, self.callback_raise_error("TestError"))
        )

        async with application:
            await application.process_update(self.message_update)
            await asyncio.sleep(0.05)
            assert self.received == (CustomContext, float, complex, int)

    async def test_custom_context_handler_callback(self, one_time_bot):
        async def callback(_, context):
            self.received = (
                type(context),
                type(context.user_data),
                type(context.chat_data),
                type(context.bot_data),
            )

        application = (
            ApplicationBuilder()
            .bot(one_time_bot)
            .context_types(
                ContextTypes(
                    context=CustomContext, bot_data=int, user_data=float, chat_data=complex
                )
            )
            .build()
        )
        application.add_handler(MessageHandler(filters.ALL, callback))

        async with application:
            await application.process_update(self.message_update)
            await asyncio.sleep(0.05)
            assert self.received == (CustomContext, float, complex, int)

    @pytest.mark.parametrize(
        ("check", "expected"),
        [(True, True), (None, False), (False, False), ({}, True), ("", True), ("check", True)],
    )
    async def test_check_update_handling(self, app, check, expected):
        class MyHandler(BaseHandler):
            def check_update(self, update: object):
                return check

            async def handle_update(
                _,
                update,
                application,
                check_result,
                context,
            ):
                await super().handle_update(
                    update=update,
                    application=application,
                    check_result=check_result,
                    context=context,
                )
                self.received = check_result

        async with app:
            app.add_handler(MyHandler(self.callback_increase_count))
            await app.process_update(1)
            assert self.count == (1 if expected else 0)
            if expected:
                assert self.received == check
            else:
                assert self.received is None

    async def test_non_blocking_handler(self, app):
        event = asyncio.Event()

        async def callback(update, context):
            await event.wait()
            self.count = 42

        app.add_handler(TypeHandler(object, callback, block=False))
        app.add_handler(TypeHandler(object, self.callback_increase_count), group=1)

        async with app:
            await app.start()
            await app.update_queue.put(1)
            task = asyncio.create_task(app.stop())
            await asyncio.sleep(0.05)
            tasks = asyncio.all_tasks()
            assert any(":process_update_non_blocking" in t.get_name() for t in tasks)
            assert self.count == 1
            # Make sure that app stops only once all non blocking callbacks are done
            assert not task.done()
            event.set()
            await asyncio.sleep(0.05)
            assert self.count == 42
            assert task.done()

    async def test_non_blocking_handler_applicationhandlerstop(self, app, recwarn):
        async def callback(update, context):
            raise ApplicationHandlerStop

        app.add_handler(TypeHandler(object, callback, block=False))

        async with app:
            await app.start()
            await app.update_queue.put(1)
            await asyncio.sleep(0.05)
            await app.stop()

        assert len(recwarn) == 1
        assert recwarn[0].category is PTBUserWarning
        assert (
            str(recwarn[0].message)
            == "ApplicationHandlerStop is not supported with handlers running non-blocking."
        )
        assert (
            Path(recwarn[0].filename) == PROJECT_ROOT_PATH / "telegram" / "ext" / "_application.py"
        ), "incorrect stacklevel!"

    async def test_non_blocking_no_error_handler(self, app, caplog):
        app.add_handler(TypeHandler(object, self.callback_raise_error("Test error"), block=False))

        with caplog.at_level(logging.ERROR):
            async with app:
                await app.start()
                await app.update_queue.put(1)
                await asyncio.sleep(0.05)
                assert len(caplog.records) == 1
                assert (
                    caplog.records[-1].getMessage().startswith("No error handlers are registered")
                )
                assert caplog.records[-1].name == "telegram.ext.Application"
                await app.stop()

    @pytest.mark.parametrize("handler_block", [True, False])
    async def test_non_blocking_error_handler(self, app, handler_block):
        event = asyncio.Event()

        async def async_error_handler(update, context):
            await event.wait()
            self.received = "done"

        async def normal_error_handler(update, context):
            self.count = 42

        app.add_error_handler(async_error_handler, block=False)
        app.add_error_handler(normal_error_handler)
        app.add_handler(TypeHandler(object, self.callback_raise_error("err"), block=handler_block))

        async with app:
            await app.start()
            await app.update_queue.put(self.message_update)
            task = asyncio.create_task(app.stop())
            await asyncio.sleep(0.05)
            tasks = asyncio.all_tasks()
            assert any(":process_error:non_blocking" in t.get_name() for t in tasks)
            assert self.count == 42
            assert self.received is None
            event.set()
            await asyncio.sleep(0.05)
            assert self.received == "done"
            assert task.done()

    @pytest.mark.parametrize("handler_block", [True, False])
    async def test_non_blocking_error_handler_applicationhandlerstop(
        self, app, recwarn, handler_block
    ):
        async def callback(update, context):
            raise RuntimeError

        async def error_handler(update, context):
            raise ApplicationHandlerStop

        app.add_handler(TypeHandler(object, callback, block=handler_block))
        app.add_error_handler(error_handler, block=False)

        async with app:
            await app.start()
            await app.update_queue.put(1)
            await asyncio.sleep(0.05)
            await app.stop()

        assert len(recwarn) == 1
        assert recwarn[0].category is PTBUserWarning
        assert (
            str(recwarn[0].message)
            == "ApplicationHandlerStop is not supported with handlers running non-blocking."
        )
        assert (
            Path(recwarn[0].filename) == PROJECT_ROOT_PATH / "telegram" / "ext" / "_application.py"
        ), "incorrect stacklevel!"

    @pytest.mark.parametrize(("block", "expected_output"), [(False, 0), (True, 5)])
    async def test_default_block_error_handler(self, bot_info, block, expected_output):
        async def error_handler(*args, **kwargs):
            await asyncio.sleep(0.1)
            self.count = 5

        bot = make_bot(bot_info, defaults=Defaults(block=block))
        app = Application.builder().bot(bot).build()
        async with app:
            app.add_handler(TypeHandler(object, self.callback_raise_error("error")))
            app.add_error_handler(error_handler)
            await app.process_update(1)
            await asyncio.sleep(0.05)
            assert self.count == expected_output
            await asyncio.sleep(0.1)
            assert self.count == 5

    @pytest.mark.parametrize(("block", "expected_output"), [(False, 0), (True, 5)])
    async def test_default_block_handler(self, bot_info, block, expected_output):
        bot = make_bot(bot_info, defaults=Defaults(block=block))
        app = Application.builder().bot(bot).build()
        async with app:
            app.add_handler(TypeHandler(object, self.callback_set_count(5, sleep=0.1)))
            await app.process_update(1)
            await asyncio.sleep(0.05)
            assert self.count == expected_output
            await asyncio.sleep(0.15)
            assert self.count == 5

    @pytest.mark.parametrize("handler_block", [True, False])
    @pytest.mark.parametrize("error_handler_block", [True, False])
    async def test_nonblocking_handler_raises_and_non_blocking_error_handler_raises(
        self, app, caplog, handler_block, error_handler_block
    ):
        handler = TypeHandler(object, self.callback_raise_error("error"), block=handler_block)
        app.add_handler(handler)
        app.add_error_handler(self.error_handler_raise_error, block=error_handler_block)

        async with app:
            await app.start()
            with caplog.at_level(logging.ERROR):
                await app.update_queue.put(1)
                await asyncio.sleep(0.05)
                assert len(caplog.records) == 1
                assert caplog.records[-1].name == "telegram.ext.Application"
                assert (
                    caplog.records[-1]
                    .getMessage()
                    .startswith("An error was raised and an uncaught")
                )

            # Make sure that the main loop still runs
            app.remove_handler(handler)
            app.add_handler(MessageHandler(filters.ALL, self.callback_increase_count, block=True))
            await app.update_queue.put(self.message_update)
            await asyncio.sleep(0.05)
            assert self.count == 1

            await app.stop()

    @pytest.mark.parametrize(
        "message",
        [
            Message(message_id=1, chat=Chat(id=2, type=None), migrate_from_chat_id=1, date=None),
            Message(message_id=1, chat=Chat(id=1, type=None), migrate_to_chat_id=2, date=None),
            Message(message_id=1, chat=Chat(id=1, type=None), date=None),
            None,
        ],
    )
    @pytest.mark.parametrize("old_chat_id", [None, 1, "1"])
    @pytest.mark.parametrize("new_chat_id", [None, 2, "1"])
    def test_migrate_chat_data(self, app, message: "Message", old_chat_id: int, new_chat_id: int):
        def call(match: str):
            with pytest.raises(ValueError, match=match):
                app.migrate_chat_data(
                    message=message, old_chat_id=old_chat_id, new_chat_id=new_chat_id
                )

        if message and (old_chat_id or new_chat_id):
            call(r"^Message and chat_id pair are mutually exclusive$")
            return

        if not any((message, old_chat_id, new_chat_id)):
            call(r"^chat_id pair or message must be passed$")
            return

        if message:
            if message.migrate_from_chat_id is None and message.migrate_to_chat_id is None:
                call(r"^Invalid message instance")
                return
            effective_old_chat_id = message.migrate_from_chat_id or message.chat.id
            effective_new_chat_id = message.migrate_to_chat_id or message.chat.id

        elif not (isinstance(old_chat_id, int) and isinstance(new_chat_id, int)):
            call(r"^old_chat_id and new_chat_id must be integers$")
            return
        else:
            effective_old_chat_id = old_chat_id
            effective_new_chat_id = new_chat_id

        app.chat_data[effective_old_chat_id]["key"] = "test"
        app.migrate_chat_data(message=message, old_chat_id=old_chat_id, new_chat_id=new_chat_id)
        assert effective_old_chat_id not in app.chat_data
        assert app.chat_data[effective_new_chat_id]["key"] == "test"

    @pytest.mark.parametrize(
        ("c_id", "expected"),
        [(321, {222: "remove_me"}), (111, {321: {"not_empty": "no"}, 222: "remove_me"})],
        ids=["test chat_id removal", "test no key in data (no error)"],
    )
    def test_drop_chat_data(self, app, c_id, expected):
        app._chat_data.update({321: {"not_empty": "no"}, 222: "remove_me"})
        app.drop_chat_data(c_id)
        assert app.chat_data == expected

    @pytest.mark.parametrize(
        ("u_id", "expected"),
        [(321, {222: "remove_me"}), (111, {321: {"not_empty": "no"}, 222: "remove_me"})],
        ids=["test user_id removal", "test no key in data (no error)"],
    )
    def test_drop_user_data(self, app, u_id, expected):
        app._user_data.update({321: {"not_empty": "no"}, 222: "remove_me"})
        app.drop_user_data(u_id)
        assert app.user_data == expected

    async def test_create_task_basic(self, app):
        async def callback():
            await asyncio.sleep(0.05)
            self.count = 42
            return 43

        task = app.create_task(callback(), name="test_task")
        assert task.get_name() == "test_task"
        await asyncio.sleep(0.01)
        assert not task.done()
        out = await task
        assert task.done()
        assert self.count == 42
        assert out == 43

    @pytest.mark.parametrize("running", [True, False])
    async def test_create_task_awaiting_warning(self, app, running, recwarn):
        async def callback():
            await asyncio.sleep(0.1)
            return 43

        async with app:
            if running:
                await app.start()

            task = app.create_task(callback())

            if running:
                assert len(recwarn) == 0
                assert not task.done()
                await app.stop()
                assert task.done()
                assert task.result() == 43
            else:
                assert len(recwarn) == 1
                assert recwarn[0].category is PTBUserWarning
                assert "won't be automatically awaited" in str(recwarn[0].message)
                assert recwarn[0].filename == __file__, "wrong stacklevel!"
                assert not task.done()
                await task

    @pytest.mark.parametrize("update", [None, object()])
    async def test_create_task_error_handling(self, app, update):
        exception = RuntimeError("TestError")

        async def callback():
            raise exception

        async def error(update_arg, context):
            self.received = update_arg, context.error

        app.add_error_handler(error)
        if update:
            task = app.create_task(callback(), update=update)
        else:
            task = app.create_task(callback())

        with pytest.raises(RuntimeError, match="TestError"):
            await task
        assert task.exception() is exception
        assert isinstance(self.received, tuple)
        assert self.received[0] is update
        assert self.received[1] is exception

    async def test_create_task_cancel_task(self, app):
        async def callback():
            await asyncio.sleep(5)

        async def error(update_arg, context):
            self.received = update_arg, context.error

        app.add_error_handler(error)
        async with app:
            await app.start()
            task = app.create_task(callback())
            await asyncio.sleep(0.05)
            task.cancel()

            with pytest.raises(asyncio.CancelledError):
                await task
            with pytest.raises(asyncio.CancelledError):
                assert task.exception()

            # Error handlers should not be called if task was cancelled
            assert self.received is None

            # make sure that the cancelled task doesn't block the stopping of the app
            await app.stop()

    async def test_await_create_task_tasks_on_stop(self, app):
        event_1 = asyncio.Event()
        event_2 = asyncio.Event()

        async def callback_1():
            await event_1.wait()

        async def callback_2():
            await event_2.wait()

        async with app:
            await app.start()
            task_1 = app.create_task(callback_1())
            task_2 = app.create_task(callback_2())
            event_2.set()
            await task_2
            assert not task_1.done()
            stop_task = asyncio.create_task(app.stop())
            assert not stop_task.done()
            await asyncio.sleep(0.1)
            assert not stop_task.done()
            event_1.set()
            await asyncio.sleep(0.05)
            assert stop_task.done()

    async def test_create_task_awaiting_future(self, app):
        async def callback():
            await asyncio.sleep(0.01)
            return 42

        # `asyncio.gather` returns an `asyncio.Future` and not an
        # `asyncio.Task`
        out = await app.create_task(asyncio.gather(callback()))
        assert out == [42]

    @pytest.mark.skipif(sys.version_info >= (3, 12), reason="generator coroutines are deprecated")
    async def test_create_task_awaiting_generator(self, app, recwarn):
        event = asyncio.Event()

        def gen():
            yield
            event.set()

        await app.create_task(gen())
        assert event.is_set()
        assert len(recwarn) == 2  # 1st warning is: tasks not being awaited when app isn't running
        assert recwarn[1].category is PTBDeprecationWarning
        assert "Generator-based coroutines are deprecated" in str(recwarn[1].message)

    async def test_no_update_processor(self, app):
        queue = asyncio.Queue()
        event_1 = asyncio.Event()
        event_2 = asyncio.Event()
        await queue.put(event_1)
        await queue.put(event_2)

        async def callback(u, c):
            await asyncio.sleep(0.1)
            event = await queue.get()
            event.set()

        app.add_handler(TypeHandler(object, callback))
        async with app:
            await app.start()
            await app.update_queue.put(1)
            await app.update_queue.put(2)
            assert not event_1.is_set()
            assert not event_2.is_set()
            await asyncio.sleep(0.15)
            assert event_1.is_set()
            assert not event_2.is_set()
            await asyncio.sleep(0.1)
            assert event_1.is_set()
            assert event_2.is_set()

            await app.stop()

    @pytest.mark.parametrize("update_processor", [15, 50, 100])
    async def test_update_processor(self, one_time_bot, update_processor):
        # We don't test with `True` since the large number of parallel coroutines quickly leads
        # to test instabilities
        app = Application.builder().bot(one_time_bot).concurrent_updates(update_processor).build()
        events = {
            i: asyncio.Event() for i in range(app.update_processor.max_concurrent_updates + 10)
        }
        queue = asyncio.Queue()
        for event in events.values():
            await queue.put(event)

        async def callback(u, c):
            await asyncio.sleep(0.5)
            (await queue.get()).set()

        app.add_handler(TypeHandler(object, callback))
        async with app:
            await app.start()
            for i in range(app.update_processor.max_concurrent_updates + 10):
                await app.update_queue.put(i)

            for i in range(app.update_processor.max_concurrent_updates + 10):
                assert not events[i].is_set()

            await asyncio.sleep(0.9)
            tasks = asyncio.all_tasks()
            assert any(":process_concurrent_update" in task.get_name() for task in tasks)
            for i in range(app.update_processor.max_concurrent_updates):
                assert events[i].is_set()
            for i in range(
                app.update_processor.max_concurrent_updates,
                app.update_processor.max_concurrent_updates + 10,
            ):
                assert not events[i].is_set()

            await asyncio.sleep(0.5)
            for i in range(app.update_processor.max_concurrent_updates + 10):
                assert events[i].is_set()

            await app.stop()

    async def test_update_processor_done_on_shutdown(self, one_time_bot):
        app = Application.builder().bot(one_time_bot).concurrent_updates(True).build()
        event = asyncio.Event()

        async def callback(update, context):
            await event.wait()

        app.add_handler(TypeHandler(object, callback))

        async with app:
            await app.start()
            await app.update_queue.put(1)
            stop_task = asyncio.create_task(app.stop())
            await asyncio.sleep(0.1)
            assert not stop_task.done()
            event.set()
            await asyncio.sleep(0.05)
            assert stop_task.done()

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_polling_basic(self, app, monkeypatch, caplog):
        exception_event = threading.Event()
        exception_testing_done = threading.Event()
        update_event = threading.Event()
        exception = TelegramError("This is a test error")
        assertions = {}

        async def get_updates(*args, **kwargs):
            if exception_event.is_set():
                raise exception

            # This makes sure that other coroutines have a chance of running as well
            if exception_testing_done.is_set() and app.updater.running:
                # the longer sleep makes sure that we can exit also while get_updates is running
                await asyncio.sleep(20)
            else:
                await asyncio.sleep(0.01)

            update_event.set()
            return [self.message_update]

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            # Check that everything's running
            assertions["app_running"] = app.running
            assertions["updater_running"] = app.updater.running
            assertions["job_queue_running"] = app.job_queue.scheduler.running

            # Check that we're getting updates
            update_event.wait()
            time.sleep(0.05)
            assertions["getting_updates"] = self.count == 42

            # Check that errors are properly handled during polling
            exception_event.set()
            time.sleep(0.05)
            assertions["exception_handling"] = self.received == exception.message
            exception_testing_done.set()

            # So that the get_updates call on shutdown doesn't fail
            exception_event.clear()

            time.sleep(1)
            os.kill(os.getpid(), signal.SIGINT)
            time.sleep(0.1)

            # # Assert that everything has stopped running
            assertions["app_not_running"] = not app.running
            assertions["updater_not_running"] = not app.updater.running
            assertions["job_queue_not_running"] = not app.job_queue.scheduler.running

        monkeypatch.setattr(app.bot, "get_updates", get_updates)
        app.add_error_handler(self.error_handler_context)
        app.add_handler(TypeHandler(object, self.callback_set_count(42)))

        thread = Thread(target=thread_target)
        thread.start()
        with caplog.at_level(logging.DEBUG):
            app.run_polling(drop_pending_updates=True, close_loop=False)
            thread.join()

        assert len(assertions) == 8
        for key, value in assertions.items():
            assert value, f"assertion '{key}' failed!"

        found_log = False
        for record in caplog.records:
            if "received stop signal" in record.getMessage() and record.levelno == logging.DEBUG:
                found_log = True
        assert found_log

    @pytest.mark.parametrize(
        "timeout_name",
        ["read_timeout", "connect_timeout", "write_timeout", "pool_timeout", "poll_interval"],
    )
    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_polling_timeout_deprecation_warnings(
        self, timeout_name, monkeypatch, recwarn, app
    ):
        async def get_updates(*args, **kwargs):
            # This makes sure that other coroutines have a chance of running as well
            await asyncio.sleep(0)
            return []

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            time.sleep(0.05)

            os.kill(os.getpid(), signal.SIGINT)

        monkeypatch.setattr(app.bot, "get_updates", get_updates)

        thread = Thread(target=thread_target)
        thread.start()

        kwargs = {timeout_name: 42}
        app.run_polling(drop_pending_updates=True, close_loop=False, **kwargs)
        thread.join()

        if timeout_name == "poll_interval":
            assert len(recwarn) == 0
            return

        assert len(recwarn) == 1
        assert "Setting timeouts via `Application.run_polling` is deprecated." in str(
            recwarn[0].message
        )
        assert recwarn[0].category is PTBDeprecationWarning
        assert recwarn[0].filename == __file__, "wrong stacklevel"

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_polling_post_init(self, one_time_bot, monkeypatch):
        events = []

        async def get_updates(*args, **kwargs):
            # This makes sure that other coroutines have a chance of running as well
            await asyncio.sleep(0)
            return []

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            os.kill(os.getpid(), signal.SIGINT)

        async def post_init(app: Application) -> None:
            events.append("post_init")

        app = Application.builder().bot(one_time_bot).post_init(post_init).build()
        app.bot._unfreeze()
        monkeypatch.setattr(app.bot, "get_updates", get_updates)
        monkeypatch.setattr(
            app, "initialize", call_after(app.initialize, lambda _: events.append("init"))
        )
        monkeypatch.setattr(
            app.updater,
            "start_polling",
            call_after(app.updater.start_polling, lambda _: events.append("start_polling")),
        )

        thread = Thread(target=thread_target)
        thread.start()
        app.run_polling(drop_pending_updates=True, close_loop=False)
        thread.join()
        assert events == ["init", "post_init", "start_polling"], "Wrong order of events detected!"

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_polling_post_shutdown(self, one_time_bot, monkeypatch):
        events = []

        async def get_updates(*args, **kwargs):
            # This makes sure that other coroutines have a chance of running as well
            await asyncio.sleep(0)
            return []

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            os.kill(os.getpid(), signal.SIGINT)

        async def post_shutdown(app: Application) -> None:
            events.append("post_shutdown")

        app = Application.builder().bot(one_time_bot).post_shutdown(post_shutdown).build()
        app.bot._unfreeze()
        monkeypatch.setattr(app.bot, "get_updates", get_updates)
        monkeypatch.setattr(
            app, "shutdown", call_after(app.shutdown, lambda _: events.append("shutdown"))
        )
        monkeypatch.setattr(
            app.updater,
            "shutdown",
            call_after(app.updater.shutdown, lambda _: events.append("updater.shutdown")),
        )

        thread = Thread(target=thread_target)
        thread.start()
        app.run_polling(drop_pending_updates=True, close_loop=False)
        thread.join()
        assert events == [
            "updater.shutdown",
            "shutdown",
            "post_shutdown",
        ], "Wrong order of events detected!"

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_polling_post_stop(self, bot, monkeypatch):
        events = []

        async def get_updates(*args, **kwargs):
            # This makes sure that other coroutines have a chance of running as well
            await asyncio.sleep(0)
            return []

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            os.kill(os.getpid(), signal.SIGINT)

        async def post_stop(app: Application) -> None:
            events.append("post_stop")

        app = Application.builder().token(bot.token).post_stop(post_stop).build()
        app.bot._unfreeze()
        monkeypatch.setattr(app.bot, "get_updates", get_updates)
        monkeypatch.setattr(app, "stop", call_after(app.stop, lambda _: events.append("stop")))
        monkeypatch.setattr(
            app.updater,
            "stop",
            call_after(app.updater.stop, lambda _: events.append("updater.stop")),
        )
        monkeypatch.setattr(
            app.updater,
            "shutdown",
            call_after(app.updater.shutdown, lambda _: events.append("updater.shutdown")),
        )

        thread = Thread(target=thread_target)
        thread.start()
        app.run_polling(drop_pending_updates=True, close_loop=False)
        thread.join()
        assert events == [
            "updater.stop",
            "stop",
            "post_stop",
            "updater.shutdown",
        ], "Wrong order of events detected!"

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_polling_parameters_passing(self, app, monkeypatch):
        # First check that the default values match and that we have all arguments there
        updater_signature = inspect.signature(app.updater.start_polling)
        app_signature = inspect.signature(app.run_polling)

        for name, param in updater_signature.parameters.items():
            if name == "error_callback":
                assert name not in app_signature.parameters
                continue
            assert name in app_signature.parameters
            assert param.kind == app_signature.parameters[name].kind
            assert param.default == app_signature.parameters[name].default

        # Check that we pass them correctly
        async def start_polling(_, **kwargs):
            self.received = kwargs
            return True

        async def stop(_, **kwargs):
            return True

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            time.sleep(0.1)
            os.kill(os.getpid(), signal.SIGINT)

        monkeypatch.setattr(Updater, "start_polling", start_polling)
        monkeypatch.setattr(Updater, "stop", stop)
        thread = Thread(target=thread_target)
        thread.start()
        app.run_polling(close_loop=False)
        thread.join()

        assert set(self.received.keys()) == set(updater_signature.parameters.keys())
        for name, param in updater_signature.parameters.items():
            if name == "error_callback":
                assert self.received[name] is not None
            else:
                assert self.received[name] == param.default

        expected = {
            name: name for name in updater_signature.parameters if name != "error_callback"
        }
        thread = Thread(target=thread_target)
        thread.start()
        app.run_polling(close_loop=False, **expected)
        thread.join()

        assert set(self.received.keys()) == set(updater_signature.parameters.keys())
        assert self.received.pop("error_callback", None)
        assert self.received == expected

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_webhook_basic(self, app, monkeypatch, caplog):
        assertions = {}

        async def delete_webhook(*args, **kwargs):
            return True

        async def set_webhook(*args, **kwargs):
            return True

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            # Check that everything's running
            assertions["app_running"] = app.running
            assertions["updater_running"] = app.updater.running
            assertions["job_queue_running"] = app.job_queue.scheduler.running

            # Check that we're getting updates
            loop = asyncio.new_event_loop()
            loop.run_until_complete(
                send_webhook_message(ip, port, self.message_update.to_json(), "TOKEN")
            )
            loop.close()
            time.sleep(0.05)
            assertions["getting_updates"] = self.count == 42

            os.kill(os.getpid(), signal.SIGINT)
            time.sleep(0.1)

            # # Assert that everything has stopped running
            assertions["app_not_running"] = not app.running
            assertions["updater_not_running"] = not app.updater.running
            assertions["job_queue_not_running"] = not app.job_queue.scheduler.running

        monkeypatch.setattr(app.bot, "set_webhook", set_webhook)
        monkeypatch.setattr(app.bot, "delete_webhook", delete_webhook)
        app.add_handler(TypeHandler(object, self.callback_set_count(42)))

        thread = Thread(target=thread_target)
        thread.start()

        ip = "127.0.0.1"
        port = randrange(1024, 49152)

        with caplog.at_level(logging.DEBUG):
            app.run_webhook(
                ip_address=ip,
                port=port,
                url_path="TOKEN",
                drop_pending_updates=True,
                close_loop=False,
            )
            thread.join()

        assert len(assertions) == 7
        for key, value in assertions.items():
            assert value, f"assertion '{key}' failed!"

        found_log = False
        for record in caplog.records:
            if "received stop signal" in record.getMessage() and record.levelno == logging.DEBUG:
                found_log = True
        assert found_log

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_webhook_post_init(self, one_time_bot, monkeypatch):
        events = []

        async def delete_webhook(*args, **kwargs):
            return True

        async def set_webhook(*args, **kwargs):
            return True

        async def get_updates(*args, **kwargs):
            # This makes sure that other coroutines have a chance of running as well
            await asyncio.sleep(0)
            return []

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            os.kill(os.getpid(), signal.SIGINT)

        async def post_init(app: Application) -> None:
            events.append("post_init")

        app = Application.builder().bot(one_time_bot).post_init(post_init).build()
        app.bot._unfreeze()
        monkeypatch.setattr(app.bot, "set_webhook", set_webhook)
        monkeypatch.setattr(app.bot, "delete_webhook", delete_webhook)
        monkeypatch.setattr(
            app, "initialize", call_after(app.initialize, lambda _: events.append("init"))
        )
        monkeypatch.setattr(
            app.updater,
            "start_webhook",
            call_after(app.updater.start_webhook, lambda _: events.append("start_webhook")),
        )

        thread = Thread(target=thread_target)
        thread.start()

        ip = "127.0.0.1"
        port = randrange(1024, 49152)

        app.run_webhook(
            ip_address=ip,
            port=port,
            url_path="TOKEN",
            drop_pending_updates=True,
            close_loop=False,
        )
        thread.join()
        assert events == ["init", "post_init", "start_webhook"], "Wrong order of events detected!"

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_webhook_post_shutdown(self, one_time_bot, monkeypatch):
        events = []

        async def delete_webhook(*args, **kwargs):
            return True

        async def set_webhook(*args, **kwargs):
            return True

        async def get_updates(*args, **kwargs):
            # This makes sure that other coroutines have a chance of running as well
            await asyncio.sleep(0)
            return []

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            os.kill(os.getpid(), signal.SIGINT)

        async def post_shutdown(app: Application) -> None:
            events.append("post_shutdown")

        app = Application.builder().bot(one_time_bot).post_shutdown(post_shutdown).build()
        app.bot._unfreeze()
        monkeypatch.setattr(app.bot, "set_webhook", set_webhook)
        monkeypatch.setattr(app.bot, "delete_webhook", delete_webhook)
        monkeypatch.setattr(
            app, "shutdown", call_after(app.shutdown, lambda _: events.append("shutdown"))
        )
        monkeypatch.setattr(
            app.updater,
            "shutdown",
            call_after(app.updater.shutdown, lambda _: events.append("updater.shutdown")),
        )

        thread = Thread(target=thread_target)
        thread.start()

        ip = "127.0.0.1"
        port = randrange(1024, 49152)

        app.run_webhook(
            ip_address=ip,
            port=port,
            url_path="TOKEN",
            drop_pending_updates=True,
            close_loop=False,
        )
        thread.join()
        assert events == [
            "updater.shutdown",
            "shutdown",
            "post_shutdown",
        ], "Wrong order of events detected!"

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_webhook_post_stop(self, bot, monkeypatch):
        events = []

        async def delete_webhook(*args, **kwargs):
            return True

        async def set_webhook(*args, **kwargs):
            return True

        async def get_updates(*args, **kwargs):
            # This makes sure that other coroutines have a chance of running as well
            await asyncio.sleep(0)
            return []

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            os.kill(os.getpid(), signal.SIGINT)

        async def post_stop(app: Application) -> None:
            events.append("post_stop")

        app = Application.builder().token(bot.token).post_stop(post_stop).build()
        app.bot._unfreeze()
        monkeypatch.setattr(app.bot, "set_webhook", set_webhook)
        monkeypatch.setattr(app.bot, "delete_webhook", delete_webhook)
        monkeypatch.setattr(app, "stop", call_after(app.stop, lambda _: events.append("stop")))
        monkeypatch.setattr(
            app.updater,
            "stop",
            call_after(app.updater.stop, lambda _: events.append("updater.stop")),
        )
        monkeypatch.setattr(
            app.updater,
            "shutdown",
            call_after(app.updater.shutdown, lambda _: events.append("updater.shutdown")),
        )

        thread = Thread(target=thread_target)
        thread.start()

        ip = "127.0.0.1"
        port = randrange(1024, 49152)

        app.run_webhook(
            ip_address=ip,
            port=port,
            url_path="TOKEN",
            drop_pending_updates=True,
            close_loop=False,
        )
        thread.join()
        assert events == [
            "updater.stop",
            "stop",
            "post_stop",
            "updater.shutdown",
        ], "Wrong order of events detected!"

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    def test_run_webhook_parameters_passing(self, one_time_bot, monkeypatch):
        # Check that we pass them correctly

        async def start_webhook(_, **kwargs):
            self.received = kwargs
            return True

        async def stop(_, **kwargs):
            return True

        # First check that the default values match and that we have all arguments there
        updater_signature = inspect.signature(Updater.start_webhook)

        monkeypatch.setattr(Updater, "start_webhook", start_webhook)
        monkeypatch.setattr(Updater, "stop", stop)
        app = ApplicationBuilder().bot(one_time_bot).build()
        app_signature = inspect.signature(app.run_webhook)

        for name, param in updater_signature.parameters.items():
            if name == "self":
                continue
            assert name in app_signature.parameters
            assert param.kind == app_signature.parameters[name].kind
            assert param.default == app_signature.parameters[name].default

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            time.sleep(0.1)
            os.kill(os.getpid(), signal.SIGINT)

        thread = Thread(target=thread_target)
        thread.start()
        app.run_webhook(close_loop=False)
        thread.join()

        assert set(self.received.keys()) == set(updater_signature.parameters.keys()) - {"self"}
        for name, param in updater_signature.parameters.items():
            if name == "self":
                continue
            assert self.received[name] == param.default

        expected = {name: name for name in updater_signature.parameters if name != "self"}
        thread = Thread(target=thread_target)
        thread.start()
        app.run_webhook(close_loop=False, **expected)
        thread.join()

        assert set(self.received.keys()) == set(expected.keys())
        assert self.received == expected

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Can't send signals without stopping whole process on windows",
    )
    async def test_cancellation_error_does_not_stop_polling(
        self, one_time_bot, monkeypatch, caplog
    ):
        """
        Ensures that hitting CTRL+C while polling *without* run_polling doesn't kill
        the update_fetcher loop such that a shutdown is still possible.
        This test is far from perfect, but it's the closest we can come with sane effort.
        """

        async def get_updates(*args, **kwargs):
            await asyncio.sleep(0)
            return [None]

        monkeypatch.setattr(one_time_bot, "get_updates", get_updates)
        app = ApplicationBuilder().bot(one_time_bot).build()

        original_get = app.update_queue.get
        raise_cancelled_error = threading.Event()

        async def get(*arg, **kwargs):
            await asyncio.sleep(0.05)
            if raise_cancelled_error.is_set():
                raise_cancelled_error.clear()
                raise asyncio.CancelledError("Mocked CancelledError")
            return await original_get(*arg, **kwargs)

        monkeypatch.setattr(app.update_queue, "get", get)

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            time.sleep(0.1)
            raise_cancelled_error.set()

        async with app:
            with caplog.at_level(logging.WARNING):
                thread = Thread(target=thread_target)
                await app.start()
                thread.start()
                assert thread.is_alive()
                raise_cancelled_error.wait()

                # The exit should have been caught and the app should still be running
                assert not thread.is_alive()
                assert app.running

                # Explicit shutdown is required
                await app.stop()
                thread.join()

        assert not thread.is_alive()
        assert not app.running

        # Make sure that we were warned about the necessity of a manual shutdown
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.name == "telegram.ext.Application"
        assert record.getMessage().startswith(
            "Fetching updates got a asyncio.CancelledError. Ignoring"
        )

    def test_run_without_updater(self, one_time_bot):
        app = ApplicationBuilder().bot(one_time_bot).updater(None).build()

        with pytest.raises(RuntimeError, match="only available if the application has an Updater"):
            app.run_webhook()

        with pytest.raises(RuntimeError, match="only available if the application has an Updater"):
            app.run_polling()

    @pytest.mark.parametrize("method", ["start", "initialize"])
    @pytest.mark.filterwarnings("ignore::telegram.warnings.PTBUserWarning")
    def test_run_error_in_application(self, one_time_bot, monkeypatch, method):
        shutdowns = []

        async def raise_method(*args, **kwargs):
            raise RuntimeError("Test Exception")

        def after_shutdown(name):
            def _after_shutdown(*args, **kwargs):
                shutdowns.append(name)

            return _after_shutdown

        monkeypatch.setattr(Application, method, raise_method)
        monkeypatch.setattr(
            Application,
            "shutdown",
            call_after(Application.shutdown, after_shutdown("application")),
        )
        monkeypatch.setattr(
            Updater, "shutdown", call_after(Updater.shutdown, after_shutdown("updater"))
        )
        app = ApplicationBuilder().bot(one_time_bot).build()
        with pytest.raises(RuntimeError, match="Test Exception"):
            app.run_polling(close_loop=False)

        assert not app.running
        assert not app.updater.running
        if method == "initialize":
            # If App.initialize fails, then App.shutdown pretty much does nothing, especially
            # doesn't call Updater.shutdown.
            assert set(shutdowns) == {"application"}
        else:
            assert set(shutdowns) == {"application", "updater"}

    @pytest.mark.parametrize("method", ["start_polling", "start_webhook"])
    @pytest.mark.filterwarnings("ignore::telegram.warnings.PTBUserWarning")
    def test_run_error_in_updater(self, one_time_bot, monkeypatch, method):
        shutdowns = []

        async def raise_method(*args, **kwargs):
            raise RuntimeError("Test Exception")

        def after_shutdown(name):
            def _after_shutdown(*args, **kwargs):
                shutdowns.append(name)

            return _after_shutdown

        monkeypatch.setattr(Updater, method, raise_method)
        monkeypatch.setattr(
            Application,
            "shutdown",
            call_after(Application.shutdown, after_shutdown("application")),
        )
        monkeypatch.setattr(
            Updater, "shutdown", call_after(Updater.shutdown, after_shutdown("updater"))
        )
        app = ApplicationBuilder().bot(one_time_bot).build()
        with pytest.raises(RuntimeError, match="Test Exception"):  # noqa: PT012
            if "polling" in method:
                app.run_polling(close_loop=False)
            else:
                app.run_webhook(close_loop=False)

        assert not app.running
        assert not app.updater.running
        assert set(shutdowns) == {"application", "updater"}

    @pytest.mark.skipif(
        platform.system() != "Windows",
        reason="Only really relevant on windows",
    )
    @pytest.mark.parametrize("method", ["start_polling", "start_webhook"])
    def test_run_stop_signal_warning_windows(self, one_time_bot, method, recwarn, monkeypatch):
        async def raise_method(*args, **kwargs):
            raise RuntimeError("Prevent Actually Running")

        monkeypatch.setattr(Application, "initialize", raise_method)
        app = ApplicationBuilder().bot(one_time_bot).build()

        with pytest.raises(RuntimeError, match="Prevent Actually Running"):  # noqa: PT012
            if "polling" in method:
                app.run_polling(close_loop=False, stop_signals=(signal.SIGINT,))
            else:
                app.run_webhook(close_loop=False, stop_signals=(signal.SIGTERM,))

        assert len(recwarn) >= 1
        found = False
        for record in recwarn:
            print(record)
            if str(record.message).startswith("Could not add signal handlers for the stop"):
                assert record.category is PTBUserWarning
                assert record.filename == __file__, "stacklevel is incorrect!"
                found = True
        assert found

        recwarn.clear()
        with pytest.raises(RuntimeError, match="Prevent Actually Running"):  # noqa: PT012
            if "polling" in method:
                app.run_polling(close_loop=False, stop_signals=None)
            else:
                app.run_webhook(close_loop=False, stop_signals=None)

        for record in recwarn:
            assert not str(record.message).startswith("Could not add signal handlers for the stop")

    @pytest.mark.flaky(3, 1)  # loop.call_later will error the test when a flood error is received
    def test_signal_handlers(self, app, monkeypatch):
        # this test should make sure that signal handlers are set by default on Linux + Mac,
        # and not on Windows.

        received_signals = []

        def signal_handler_test(*args, **kwargs):
            # args[0] is the signal, [1] the callback
            received_signals.append(args[0])

        loop = asyncio.get_event_loop()
        monkeypatch.setattr(loop, "add_signal_handler", signal_handler_test)

        def abort_app():
            raise SystemExit

        loop.call_later(0.6, abort_app)

        app.run_polling(close_loop=False)

        if platform.system() == "Windows":
            assert received_signals == []
        else:
            assert received_signals == [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]

        received_signals.clear()
        loop.call_later(0.8, abort_app)
        app.run_webhook(port=49152, webhook_url="example.com", close_loop=False)

        if platform.system() == "Windows":
            assert received_signals == []
        else:
            assert received_signals == [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]

    def test_stop_running_not_running(self, app, caplog):
        with caplog.at_level(logging.DEBUG):
            app.stop_running()

        assert len(caplog.records) == 1
        assert caplog.records[-1].name == "telegram.ext.Application"
        assert caplog.records[-1].getMessage().endswith("stop_running() does nothing.")

    @pytest.mark.parametrize("method", ["polling", "webhook"])
    def test_stop_running(self, one_time_bot, monkeypatch, method):
        # asyncio.Event() seems to be hard to use across different threads (awaiting in main
        # thread, setting in another thread), so we use threading.Event() instead.
        # This requires the use of run_in_executor, but that's fine.
        put_update_event = threading.Event()
        callback_done_event = threading.Event()
        called_stop_running = threading.Event()
        assertions = {}

        async def get_updates(*args, **kwargs):
            await asyncio.sleep(0)
            return []

        async def delete_webhook(*args, **kwargs):
            return True

        async def set_webhook(*args, **kwargs):
            return True

        async def post_init(app):
            # Simply calling app.update_queue.put_nowait(method) in the thread_target doesn't work
            # for some reason (probably threading magic), so we use an event from the thread_target
            # to put the update into the queue in the main thread.
            async def task(app):
                await asyncio.get_running_loop().run_in_executor(None, put_update_event.wait)
                await app.update_queue.put(method)

            app.create_task(task(app))

        app = ApplicationBuilder().bot(one_time_bot).post_init(post_init).build()
        monkeypatch.setattr(app.bot, "get_updates", get_updates)
        monkeypatch.setattr(app.bot, "set_webhook", set_webhook)
        monkeypatch.setattr(app.bot, "delete_webhook", delete_webhook)

        events = []
        monkeypatch.setattr(
            app.updater,
            "stop",
            call_after(app.updater.stop, lambda _: events.append("updater.stop")),
        )
        monkeypatch.setattr(
            app,
            "stop",
            call_after(app.stop, lambda _: events.append("app.stop")),
        )
        monkeypatch.setattr(
            app,
            "shutdown",
            call_after(app.shutdown, lambda _: events.append("app.shutdown")),
        )

        def thread_target():
            waited = 0
            while not app.running:
                time.sleep(0.05)
                waited += 0.05
                if waited > 5:
                    pytest.fail("App apparently won't start")

            time.sleep(0.1)
            assertions["called_stop_running_not_set"] = not called_stop_running.is_set()

            put_update_event.set()
            time.sleep(0.1)

            assertions["called_stop_running_set"] = called_stop_running.is_set()

            # App should have entered `stop` now but not finished it yet because the callback
            # is still running
            assertions["updater.stop_event"] = events == ["updater.stop"]
            assertions["app.running_False"] = not app.running

            callback_done_event.set()
            time.sleep(0.1)

            # Now that the update is fully handled, we expect the full shutdown
            assertions["events"] = events == ["updater.stop", "app.stop", "app.shutdown"]

        async def callback(update, context):
            context.application.stop_running()
            called_stop_running.set()
            await asyncio.get_running_loop().run_in_executor(None, callback_done_event.wait)

        app.add_handler(TypeHandler(object, callback))

        thread = Thread(target=thread_target)
        thread.start()

        if method == "polling":
            app.run_polling(close_loop=False, drop_pending_updates=True)
        else:
            ip = "127.0.0.1"
            port = randrange(1024, 49152)

            app.run_webhook(
                ip_address=ip,
                port=port,
                url_path="TOKEN",
                drop_pending_updates=False,
                close_loop=False,
            )

        thread.join()

        assert len(assertions) == 5
        for key, value in assertions.items():
            assert value, f"assertion '{key}' failed!"
