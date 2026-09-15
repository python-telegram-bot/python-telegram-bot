#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""This module contains tests for the network_retry_loop function.

Note:
    Most of the retry loop functionality is already covered in test_updater and test_application.
    These tests focus specifically on the max_retries behavior for different exception types
    and the error callback handling, which were added as part of the bug fix in #5030.
"""

import asyncio
import logging
import time

import pytest

from telegram.error import InvalidToken, RetryAfter, TelegramError, TimedOut
from telegram.ext._utils.networkloop import network_retry_loop


class TestNetworkRetryLoop:
    """Tests for the network_retry_loop function.

    Note:
        The general retry loop functionality is extensively tested in test_updater and
        test_application. These tests focus on the specific max_retries behavior for
        different exception types.
    """

    @pytest.mark.parametrize(
        ("exception_class", "exception_args"),
        [
            (RetryAfter, (1,)),
            (TimedOut, ("Test timeout",)),
        ],
        ids=["RetryAfter", "TimedOut"],
    )
    async def test_exception_respects_max_retries(self, exception_class, exception_args):
        """Test that RetryAfter and TimedOut exceptions respect max_retries limit."""
        call_count = 0

        async def action_with_exception():
            nonlocal call_count
            call_count += 1
            raise exception_class(*exception_args)

        with pytest.raises(exception_class):
            await network_retry_loop(
                action_cb=action_with_exception,
                description=f"Test {exception_class.__name__}",
                interval=0,
                max_retries=2,
            )

        # Should be called 3 times: initial call + 2 retries
        assert call_count == 3

    @pytest.mark.parametrize(
        ("exception_class", "exception_args"),
        [
            (RetryAfter, (1,)),
            (TimedOut, ("Test timeout",)),
        ],
        ids=["RetryAfter", "TimedOut"],
    )
    async def test_exception_with_zero_max_retries(self, exception_class, exception_args):
        """Test that RetryAfter and TimedOut with max_retries=0 don't retry."""
        call_count = 0

        async def action_with_exception():
            nonlocal call_count
            call_count += 1
            raise exception_class(*exception_args)

        with pytest.raises(exception_class):
            await network_retry_loop(
                action_cb=action_with_exception,
                description=f"Test {exception_class.__name__} no retries",
                interval=0,
                max_retries=0,
            )

        # Should be called only once with max_retries=0
        assert call_count == 1

    async def test_invalid_token_aborts_immediately(self):
        """Test that InvalidToken exceptions abort immediately without retries."""
        call_count = 0

        async def action_with_invalid_token():
            nonlocal call_count
            call_count += 1
            raise InvalidToken("Invalid token")

        with pytest.raises(InvalidToken):
            await network_retry_loop(
                action_cb=action_with_invalid_token,
                description="Test InvalidToken",
                interval=0,
                max_retries=5,
            )

        # Should be called only once, no retries for invalid token
        assert call_count == 1

    async def test_telegram_error_respects_max_retries(self):
        """Test that general TelegramError exceptions respect max_retries limit."""
        call_count = 0

        async def action_with_telegram_error():
            nonlocal call_count
            call_count += 1
            raise TelegramError("Test error")

        with pytest.raises(TelegramError):
            await network_retry_loop(
                action_cb=action_with_telegram_error,
                description="Test TelegramError",
                interval=0,
                max_retries=3,
            )

        # Should be called 4 times: initial call + 3 retries
        assert call_count == 4

    @pytest.mark.parametrize(
        ("exception_class", "exception_args"),
        [
            (RetryAfter, (1,)),
            (TimedOut, ("Test timeout",)),
            (InvalidToken, ("Invalid token",)),
        ],
        ids=["RetryAfter", "TimedOut", "InvalidToken"],
    )
    async def test_error_callback_not_called_for_specific_exceptions(
        self, exception_class, exception_args
    ):
        """Test that error callback is not called for RetryAfter, TimedOut, or InvalidToken."""
        error_callback_called = False

        def error_callback(exc):
            nonlocal error_callback_called
            error_callback_called = True

        async def action_with_exception():
            raise exception_class(*exception_args)

        with pytest.raises(exception_class):
            await network_retry_loop(
                action_cb=action_with_exception,
                on_err_cb=error_callback,
                description=f"Test {exception_class.__name__} callback",
                interval=0,
                max_retries=1,
            )

        assert not error_callback_called

    async def test_error_callback_called_for_telegram_error(self):
        """Test that error callback is called for general TelegramError exceptions."""
        error_callback_count = 0
        caught_exception = None

        def error_callback(exc):
            nonlocal error_callback_count, caught_exception
            error_callback_count += 1
            caught_exception = exc

        async def action_with_telegram_error():
            raise TelegramError("Test error")

        with pytest.raises(TelegramError):
            await network_retry_loop(
                action_cb=action_with_telegram_error,
                on_err_cb=error_callback,
                description="Test TelegramError callback",
                interval=0,
                max_retries=2,
            )

        # Should be called 3 times (initial + 2 retries)
        assert error_callback_count == 3
        assert isinstance(caught_exception, TelegramError)

    async def test_success_after_retries(self):
        """Test that action succeeds after some retries."""
        call_count = 0

        async def action_succeeds_on_third_try():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimedOut("Test timeout")
            # Success on third try

        await network_retry_loop(
            action_cb=action_succeeds_on_third_try,
            description="Test success after retries",
            interval=0,
            max_retries=5,
        )

        assert call_count == 3

    @pytest.mark.parametrize(
        ("exception_class", "exception_args", "success_after"),
        [
            (RetryAfter, (0.01,), 5),
            (TimedOut, ("Test timeout",), 4),
        ],
        ids=["RetryAfter", "TimedOut"],
    )
    async def test_exception_with_negative_max_retries(
        self, exception_class, exception_args, success_after
    ):
        """Test that exceptions with max_retries=-1 retry indefinitely until success."""
        call_count = 0

        async def action_succeeds_after_few_tries():
            nonlocal call_count
            call_count += 1
            if call_count < success_after:
                raise exception_class(*exception_args)
            # Success after specified tries

        await network_retry_loop(
            action_cb=action_succeeds_after_few_tries,
            description=f"Test {exception_class.__name__} infinite retries",
            interval=0,
            max_retries=-1,
        )

        assert call_count == success_after

    async def test_stop_event_interrupts_backoff_sleep(self, caplog):
        """Regression test for the bug where asyncio.sleep(cur_interval) during backoff was not
        interrupted by stop_event, causing shutdowns to hang for up to 30 seconds.

        Verifies that setting stop_event while the loop is sleeping between retries causes the
        loop to exit promptly instead of waiting for the full backoff duration.
        """
        caplog.set_level(logging.DEBUG)
        stop_event = asyncio.Event()

        # Use an interval that is long enough to be detectable but short enough to keep the
        # test suite fast.  If the fix regresses, the loop would sleep this full duration on
        # every retry; the wall-clock assertion below would then fail reliably.
        INTERVAL = 5.0
        error_handled = asyncio.Event()

        async def failing_action():
            raise TelegramError("Simulated network outage")

        def on_err(exc):
            error_handled.set()

        # Deterministically wait until the network_retry_loop has processed the error
        # and is about to enter its backoff sleep.
        async def trigger_stop():
            await error_handled.wait()
            # Yield to the event loop once more to ensure network_retry_loop has
            # entered `await asyncio.wait_for(...)` inside the backoff block.
            await asyncio.sleep(0)
            stop_event.set()

        trigger_task = asyncio.create_task(trigger_stop())
        t_start = time.perf_counter()
        await network_retry_loop(
            action_cb=failing_action,
            on_err_cb=on_err,
            description="test-backoff-interrupt",
            interval=INTERVAL,
            stop_event=stop_event,
            max_retries=-1,
            repeat_on_success=True,
        )
        elapsed = time.perf_counter() - t_start
        trigger_task.cancel()
        await asyncio.gather(trigger_task, return_exceptions=True)

        # The loop must exit well before the full INTERVAL; 1 s is a generous threshold.
        assert elapsed < 1.0, (
            f"Loop took {elapsed:.2f}s to exit after stop_event was set — "
            "stop_event is not interrupting the backoff sleep."
        )
        # Assert the specific log message to prove the loop broke from inside the backoff wait,
        # preventing a race condition where the stop_event might trigger an earlier exit check.
        assert "Stop event set during backoff sleep. Stopping loop." in caplog.text

    async def test_stop_event_breaks_repeat_on_success_loop(self):
        """Regression test for the bug where network_retry_loop would loop infinitely if
        repeat_on_success=True and stop_event was set during do_action().

        Verifies that when stop_event is set mid-action, the outer loop breaks cleanly
        and does not re-enter do_action() despite repeat_on_success being True.
        """
        stop_event = asyncio.Event()
        action_started = asyncio.Event()
        call_count = 0

        async def action():
            nonlocal call_count
            call_count += 1
            action_started.set()
            # Wait for cancellation by the stop_event
            await asyncio.sleep(60)

        async def trigger_stop():
            await action_started.wait()
            stop_event.set()

        trigger_task = asyncio.create_task(trigger_stop())
        await network_retry_loop(
            action_cb=action,
            description="test-break-repeat-loop",
            interval=0,
            stop_event=stop_event,
            max_retries=-1,
            repeat_on_success=True,
        )
        trigger_task.cancel()
        await asyncio.gather(trigger_task, return_exceptions=True)

        # If the bug were present, the loop would restart and call action() again.
        assert call_count == 1, f"Action was called {call_count} times, expected exactly 1."

    async def test_stop_event_breaks_repeat_on_success_after_successful_action(self):
        """Verifies that if an action completes successfully but stop_event is set,
        the loop breaks cleanly and does not repeat despite repeat_on_success=True.
        """
        stop_event = asyncio.Event()
        call_count = 0

        async def action():
            nonlocal call_count
            call_count += 1
            # Action completes successfully.
            # We set stop_event from within the action to simulate it being set
            # concurrently just before the action finishes.
            stop_event.set()

        await network_retry_loop(
            action_cb=action,
            description="test-break-repeat-after-success",
            interval=0,
            stop_event=stop_event,
            max_retries=-1,
            repeat_on_success=True,
        )

        assert call_count == 1, f"Action was called {call_count} times, expected exactly 1."

    async def test_no_pending_tasks_after_stop_event(self):
        """Regression test for the bug where pending tasks were only .cancel()ed but never
        awaited inside do_action(), leaving them in a pending state and producing
        'Task was destroyed but it is pending!' warnings from the garbage collector.

        Verifies that after stop_event fires mid-action, all asyncio tasks created by the loop
        are fully completed (not merely cancelled) before network_retry_loop returns.
        """
        stop_event = asyncio.Event()
        action_started = asyncio.Event()

        async def slow_action():
            action_started.set()
            # Simulate a slow in-flight HTTP call; will be cancelled via stop_event.
            await asyncio.sleep(5)

        tasks_before = set(asyncio.all_tasks())

        # Concurrently set stop_event the moment the slow action begins.
        async def trigger_stop():
            await action_started.wait()
            stop_event.set()

        trigger_task = asyncio.create_task(trigger_stop())
        await network_retry_loop(
            action_cb=slow_action,
            description="test-no-pending-tasks",
            interval=0,
            stop_event=stop_event,
            max_retries=-1,
            repeat_on_success=True,
        )
        trigger_task.cancel()
        await asyncio.gather(trigger_task, return_exceptions=True)

        tasks_after = asyncio.all_tasks() - tasks_before
        pending = {t for t in tasks_after if not t.done()}

        assert not pending, (
            f"{len(pending)} task(s) remain pending after network_retry_loop returned with "
            "stop_event set — cancelled tasks are not being properly awaited."
        )
