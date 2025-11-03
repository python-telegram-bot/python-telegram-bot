#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
"""This module contains tests for the network_retry_loop function."""
import asyncio
from datetime import timedelta

import pytest

from telegram.error import InvalidToken, RetryAfter, TelegramError, TimedOut
from telegram.ext._utils.networkloop import network_retry_loop


class TestNetworkRetryLoop:
    """Tests for the network_retry_loop function."""

    async def test_retry_after_respects_max_retries(self):
        """Test that RetryAfter exceptions respect max_retries limit."""
        call_count = 0

        async def action_with_retry_after():
            nonlocal call_count
            call_count += 1
            raise RetryAfter(1)

        with pytest.raises(RetryAfter):
            await network_retry_loop(
                action_cb=action_with_retry_after,
                description="Test RetryAfter",
                interval=0,
                max_retries=2,
            )

        # Should be called 3 times: initial call + 2 retries
        assert call_count == 3

    async def test_timed_out_respects_max_retries(self):
        """Test that TimedOut exceptions respect max_retries limit."""
        call_count = 0

        async def action_with_timeout():
            nonlocal call_count
            call_count += 1
            raise TimedOut("Test timeout")

        with pytest.raises(TimedOut):
            await network_retry_loop(
                action_cb=action_with_timeout,
                description="Test TimedOut",
                interval=0,
                max_retries=2,
            )

        # Should be called 3 times: initial call + 2 retries
        assert call_count == 3

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

    async def test_retry_after_with_zero_max_retries(self):
        """Test that RetryAfter with max_retries=0 doesn't retry."""
        call_count = 0

        async def action_with_retry_after():
            nonlocal call_count
            call_count += 1
            raise RetryAfter(1)

        with pytest.raises(RetryAfter):
            await network_retry_loop(
                action_cb=action_with_retry_after,
                description="Test RetryAfter no retries",
                interval=0,
                max_retries=0,
            )

        # Should be called only once with max_retries=0
        assert call_count == 1

    async def test_timed_out_with_zero_max_retries(self):
        """Test that TimedOut with max_retries=0 doesn't retry."""
        call_count = 0

        async def action_with_timeout():
            nonlocal call_count
            call_count += 1
            raise TimedOut("Test timeout")

        with pytest.raises(TimedOut):
            await network_retry_loop(
                action_cb=action_with_timeout,
                description="Test TimedOut no retries",
                interval=0,
                max_retries=0,
            )

        # Should be called only once with max_retries=0
        assert call_count == 1

    async def test_error_callback_not_called_for_retry_after(self):
        """Test that error callback is not called for RetryAfter exceptions."""
        error_callback_called = False

        def error_callback(exc):
            nonlocal error_callback_called
            error_callback_called = True

        async def action_with_retry_after():
            raise RetryAfter(1)

        with pytest.raises(RetryAfter):
            await network_retry_loop(
                action_cb=action_with_retry_after,
                on_err_cb=error_callback,
                description="Test RetryAfter callback",
                interval=0,
                max_retries=1,
            )

        assert not error_callback_called

    async def test_error_callback_not_called_for_timed_out(self):
        """Test that error callback is not called for TimedOut exceptions."""
        error_callback_called = False

        def error_callback(exc):
            nonlocal error_callback_called
            error_callback_called = True

        async def action_with_timeout():
            raise TimedOut("Test timeout")

        with pytest.raises(TimedOut):
            await network_retry_loop(
                action_cb=action_with_timeout,
                on_err_cb=error_callback,
                description="Test TimedOut callback",
                interval=0,
                max_retries=1,
            )

        assert not error_callback_called

    async def test_error_callback_not_called_for_invalid_token(self):
        """Test that error callback is not called for InvalidToken exceptions."""
        error_callback_called = False

        def error_callback(exc):
            nonlocal error_callback_called
            error_callback_called = True

        async def action_with_invalid_token():
            raise InvalidToken("Invalid token")

        with pytest.raises(InvalidToken):
            await network_retry_loop(
                action_cb=action_with_invalid_token,
                on_err_cb=error_callback,
                description="Test InvalidToken callback",
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

    async def test_retry_after_with_negative_max_retries(self):
        """Test that RetryAfter with max_retries=-1 retries indefinitely until success."""
        call_count = 0

        async def action_succeeds_after_few_tries():
            nonlocal call_count
            call_count += 1
            if call_count < 5:
                raise RetryAfter(0.01)
            # Success after 5 tries

        await network_retry_loop(
            action_cb=action_succeeds_after_few_tries,
            description="Test RetryAfter infinite retries",
            interval=0,
            max_retries=-1,
        )

        assert call_count == 5

    async def test_timed_out_with_negative_max_retries(self):
        """Test that TimedOut with max_retries=-1 retries indefinitely until success."""
        call_count = 0

        async def action_succeeds_after_few_tries():
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise TimedOut("Test timeout")
            # Success after 4 tries

        await network_retry_loop(
            action_cb=action_succeeds_after_few_tries,
            description="Test TimedOut infinite retries",
            interval=0,
            max_retries=-1,
        )

        assert call_count == 4
