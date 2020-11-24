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
from time import sleep, perf_counter

import pytest

from telegram import Bot
from telegram.ext import MessageQueue, DelayQueue, DelayQueueError
from telegram.ext.messagequeue import queuedmessage


class TestDelayQueue:
    N = 128
    burst_limit = 30
    time_limit_ms = 1000
    margin_ms = 0
    test_times = []
    test_flag = None

    @pytest.fixture(autouse=True)
    def reset(self):
        DelayQueue.INSTANCE_COUNT = 0
        self.test_flag = None

    def call(self):
        self.test_times.append(perf_counter())

    def callback_raises_exception(self):
        raise DelayQueueError('TestError')

    def test_auto_start_false(self):
        delay_queue = DelayQueue(autostart=False)
        assert not delay_queue.is_alive()

    def test_name(self):
        delay_queue = DelayQueue(autostart=False)
        assert delay_queue.name == 'DelayQueue-1'
        delay_queue = DelayQueue(autostart=False)
        assert delay_queue.name == 'DelayQueue-2'
        delay_queue = DelayQueue(name='test_queue', autostart=False)
        assert delay_queue.name == 'test_queue'

    def test_exc_route_deprecation(self, recwarn):
        with pytest.raises(ValueError, match='Only one of exc_route or '):
            DelayQueue(exc_route=True, error_handler=True, autostart=False)

        DelayQueue(exc_route=True, autostart=False)
        assert len(recwarn) == 1
        assert str(recwarn[0].message).startswith('The exc_route argument is')

    def test_delay_queue_limits(self):
        delay_queue = DelayQueue(
            burst_limit=self.burst_limit, time_limit_ms=self.time_limit_ms, autostart=True
        )
        assert delay_queue.is_alive() is True

        try:
            for _ in range(self.N):
                delay_queue.put(self.call, [], {})

            start_time = perf_counter()
            # wait up to 20 sec more than needed
            app_end_time = (
                (self.N * self.burst_limit / (1000 * self.time_limit_ms)) + start_time + 20
            )
            while not delay_queue._queue.empty() and perf_counter() < app_end_time:
                sleep(0.5)
            assert delay_queue._queue.empty() is True  # check loop exit condition

            delay_queue.stop()
            assert delay_queue.is_alive() is False

            assert self.test_times or self.N == 0
            passes, fails = [], []
            delta = (self.time_limit_ms - self.margin_ms) / 1000
            for start, stop in enumerate(range(self.burst_limit + 1, len(self.test_times))):
                part = self.test_times[start:stop]
                if (part[-1] - part[0]) >= delta:
                    passes.append(part)
                else:
                    fails.append(part)
            assert fails == []
        finally:
            delay_queue.stop()

    def test_put_errors(self):
        delay_queue = DelayQueue(autostart=False)
        with pytest.raises(DelayQueueError, match='stopped thread'):
            delay_queue.put(promise=True)

        delay_queue.start()
        try:
            with pytest.raises(ValueError, match='You must pass either'):
                delay_queue.put()
            with pytest.raises(ValueError, match='You must pass either'):
                delay_queue.put(promise=True, args=True, kwargs=True, func=True)
            with pytest.raises(ValueError, match='You must pass either'):
                delay_queue.put(args=True)
        finally:
            delay_queue.stop()

    def test_default_error_handler_without_dispatcher(self, monkeypatch):
        @staticmethod
        def exc_route(exception):
            self.test_flag = (
                isinstance(exception, DelayQueueError) and str(exception) == 'TestError'
            )

        monkeypatch.setattr(DelayQueue, '_default_exception_handler', exc_route)

        delay_queue = DelayQueue()
        try:
            delay_queue.put(self.callback_raises_exception, [], {})
            sleep(0.5)
            assert self.test_flag
        finally:
            delay_queue.stop()

    def test_custom_error_handler_without_dispatcher(self):
        def exc_route(exception):
            self.test_flag = (
                isinstance(exception, DelayQueueError) and str(exception) == 'TestError'
            )

        delay_queue = DelayQueue(exc_route=exc_route)
        try:
            delay_queue.put(self.callback_raises_exception, [], {})
            sleep(0.5)
            assert self.test_flag
        finally:
            delay_queue.stop()

    def test_custom_error_handler_with_dispatcher(self, cdp):
        def error_handler(_, context):
            self.test_flag = (
                isinstance(context.error, DelayQueueError) and str(context.error) == 'TestError'
            )

        cdp.add_error_handler(error_handler)
        delay_queue = DelayQueue()
        delay_queue.set_dispatcher(cdp)
        try:
            delay_queue.put(self.callback_raises_exception, [], {})
            sleep(0.5)
            assert self.test_flag
        finally:
            delay_queue.stop()

    def test_parent(self, monkeypatch):
        def put(*args, **kwargs):
            self.test_flag = bool(kwargs.pop('promise', False))

        parent = DelayQueue(name='parent')
        monkeypatch.setattr(parent, 'put', put)

        delay_queue = DelayQueue(parent=parent)
        try:
            delay_queue.put(self.call, [], {})
            sleep(0.5)
            assert self.test_flag
        finally:
            parent.stop()
            delay_queue.stop()


class TestMessageQueue:
    test_flag = None

    @pytest.fixture(autouse=True)
    def reset(self):
        DelayQueue.INSTANCE_COUNT = 0
        self.test_flag = None

    def call(self, arg, kwarg=None):
        self.test_flag = arg == 1 and kwarg == 'foo'

    def callback_raises_exception(self):
        raise DelayQueueError('TestError')

    def test_auto_start_false(self):
        message_queue = MessageQueue(autostart=False)
        assert not any(thread.is_alive() for thread in message_queue._delay_queues.values())

    def test_exc_route_deprecation(self, recwarn):
        with pytest.raises(ValueError, match='Only one of exc_route or '):
            MessageQueue(exc_route=True, error_handler=True, autostart=False)

        MessageQueue(exc_route=True, autostart=False)
        assert len(recwarn) == 1
        assert str(recwarn[0].message).startswith('The exc_route argument is')

    def test_add_delay_queue_autostart_false(self):
        message_queue = MessageQueue(autostart=False)
        delay_queue = DelayQueue(autostart=False, name='dq')
        try:
            message_queue.add_delay_queue(delay_queue)
            assert 'dq' in message_queue._delay_queues
            assert not any(thread.is_alive() for thread in message_queue._delay_queues.values())
            message_queue.start()
            assert all(thread.is_alive() for thread in message_queue._delay_queues.values())

            message_queue.stop()
            assert not any(thread.is_alive() for thread in message_queue._delay_queues.values())
        finally:
            delay_queue.stop()
            message_queue.stop()

    @pytest.mark.parametrize('autostart', [True, False])
    def test_add_delay_queue_autostart_true(self, autostart):
        message_queue = MessageQueue()
        delay_queue = DelayQueue(name='dq', autostart=autostart)
        try:
            message_queue.add_delay_queue(delay_queue)
            assert 'dq' in message_queue._delay_queues
            assert delay_queue.is_alive()
            assert all(thread.is_alive() for thread in message_queue._delay_queues.values())

            message_queue.stop()
            assert not any(thread.is_alive() for thread in message_queue._delay_queues.values())
        finally:
            delay_queue.stop()
            message_queue.stop()

    def test_add_delay_queue_dispatcher(self, dp):
        message_queue = MessageQueue(autostart=False)
        message_queue.set_dispatcher(dispatcher=dp)
        delay_queue = DelayQueue(autostart=False, name='dq')
        message_queue.add_delay_queue(delay_queue)
        assert delay_queue.dispatcher is dp

    @pytest.mark.parametrize('autostart', [True, False])
    def test_remove_delay_queue(self, autostart):
        message_queue = MessageQueue(autostart=autostart)
        delay_queue = DelayQueue(name='dq')
        try:
            message_queue.add_delay_queue(delay_queue)
            assert 'dq' in message_queue._delay_queues
            assert delay_queue.is_alive()

            message_queue.remove_delay_queue('dq')
            assert 'dq' not in message_queue._delay_queues
            if autostart:
                assert not delay_queue.is_alive()
        finally:
            delay_queue.stop()
            if autostart:
                message_queue.stop()

    def test_put(self):
        group_flag = None

        message_queue = MessageQueue()
        original_put = message_queue._delay_queues[MessageQueue.DEFAULT_QUEUE].put

        def put(*args, **kwargs):
            nonlocal group_flag
            group_flag = True
            return original_put(*args, **kwargs)

        message_queue._delay_queues[MessageQueue.GROUP_QUEUE].put = put

        try:
            message_queue.put(self.call, MessageQueue.GROUP_QUEUE, 1, kwarg='foo')
            sleep(0.5)
            assert self.test_flag is True
            # make sure that group queue was called, too
            assert group_flag is True
        finally:
            message_queue._delay_queues[MessageQueue.GROUP_QUEUE].put = original_put
            message_queue.stop()


@pytest.fixture(scope='function')
def mq_bot(bot, monkeypatch):
    class MQBot(Bot):
        def __init__(self, *args, **kwargs):
            self.test = None
            self.default_count = 0
            self.group_count = 0
            super().__init__(*args, **kwargs)
            # below 2 attributes should be provided for decorator usage
            self._is_messages_queued_default = True
            self._msg_queue = MessageQueue()

        @queuedmessage
        def test_method(self, input, *args, **kwargs):
            self.test = input

    bot = MQBot(token=bot.token)

    orig_default_put = bot._msg_queue._delay_queues[MessageQueue.DEFAULT_QUEUE].put
    orig_group_put = bot._msg_queue._delay_queues[MessageQueue.GROUP_QUEUE].put

    def step_default_counter(*args, **kwargs):
        orig_default_put(*args, **kwargs)
        bot.default_count += 1

    def step_group_counter(*args, **kwargs):
        orig_group_put(*args, **kwargs)
        bot.group_count += 1

    monkeypatch.setattr(
        bot._msg_queue._delay_queues[MessageQueue.DEFAULT_QUEUE], 'put', step_default_counter
    )
    monkeypatch.setattr(
        bot._msg_queue._delay_queues[MessageQueue.GROUP_QUEUE], 'put', step_group_counter
    )
    yield bot
    bot._msg_queue.stop()


class TestDecorator:
    def test_queued_kwarg(self, mq_bot):
        mq_bot.test_method('received', queued=False)
        sleep(0.5)
        assert mq_bot.default_count == 0
        assert mq_bot.group_count == 0
        assert mq_bot.test == 'received'

        mq_bot.test_method('received1')
        sleep(0.5)
        assert mq_bot.default_count == 1
        assert mq_bot.group_count == 0
        assert mq_bot.test == 'received1'

    def test_isgroup_kwarg(self, mq_bot):
        mq_bot.test_method('received', isgroup=False)
        sleep(0.5)
        assert mq_bot.default_count == 1
        assert mq_bot.group_count == 0
        assert mq_bot.test == 'received'

        mq_bot.test_method('received1', isgroup=True)
        sleep(0.5)
        assert mq_bot.default_count == 2
        assert mq_bot.group_count == 1
        assert mq_bot.test == 'received1'
