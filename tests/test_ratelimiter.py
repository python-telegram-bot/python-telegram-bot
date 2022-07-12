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

"""
We mostly test on directly on AIORateLimiter here, b/c BaseRateLimiter doesn't contain anything
notable
"""
import asyncio
import json
import os
import time

import pytest

from telegram import BotCommand, User
from telegram.constants import ParseMode
from telegram.error import RetryAfter
from telegram.ext import AIORateLimiter, BaseRateLimiter, Defaults, ExtBot
from telegram.request import BaseRequest, RequestData
from tests.conftest import env_var_2_bool

TEST_NO_RATE_LIMITER = env_var_2_bool(os.getenv("TEST_NO_RATE_LIMITER", False))


@pytest.mark.skipif(
    not TEST_NO_RATE_LIMITER, reason="Only relevant if the optional dependency is not installed"
)
class TestNoRateLimiter:
    def test_init(self):
        with pytest.raises(RuntimeError, match=r"python-telegram-bot\[rate-limiter\]"):
            AIORateLimiter()


class TestBaseRateLimiter:
    rl_received = None
    request_received = None

    async def test_no_rate_limiter(self, bot):
        with pytest.raises(ValueError, match="if a `ExtBot.rate_limiter` is set"):
            await bot.send_message(chat_id=42, text="test", rate_limit_args="something")

    async def test_argument_passing(self, bot_info, monkeypatch, bot):
        class TestRateLimiter(BaseRateLimiter):
            async def initialize(self) -> None:
                pass

            async def shutdown(self) -> None:
                pass

            async def process_request(
                self,
                callback,
                args,
                kwargs,
                endpoint,
                data,
                rate_limit_args,
            ):
                if TestBaseRateLimiter.rl_received is None:
                    TestBaseRateLimiter.rl_received = []
                TestBaseRateLimiter.rl_received.append((endpoint, data, rate_limit_args))
                return await callback(*args, **kwargs)

        class TestRequest(BaseRequest):
            async def initialize(self) -> None:
                pass

            async def shutdown(self) -> None:
                pass

            async def do_request(self, *args, **kwargs):
                if TestBaseRateLimiter.request_received is None:
                    TestBaseRateLimiter.request_received = []
                TestBaseRateLimiter.request_received.append((args, kwargs))
                # return bot.bot.to_dict() for the `get_me` call in `Bot.initialize`
                return 200, json.dumps({"ok": True, "result": bot.bot.to_dict()}).encode()

        defaults = Defaults(parse_mode=ParseMode.HTML)
        test_request = TestRequest()
        standard_bot = ExtBot(token=bot.token, defaults=defaults, request=test_request)
        rl_bot = ExtBot(
            token=bot.token,
            defaults=defaults,
            request=test_request,
            rate_limiter=TestRateLimiter(),
        )

        async with standard_bot:
            await standard_bot.set_my_commands(
                commands=[BotCommand("test", "test")], language_code="en"
            )
        async with rl_bot:
            await rl_bot.set_my_commands(
                commands=[BotCommand("test", "test")],
                language_code="en",
                rate_limit_args=(43, "test-1"),
            )

        assert len(self.rl_received) == 2
        assert self.rl_received[0] == ("getMe", {}, None)
        assert self.rl_received[1] == (
            "setMyCommands",
            dict(commands=[BotCommand("test", "test")], language_code="en"),
            (43, "test-1"),
        )
        assert len(self.request_received) == 4
        assert self.request_received[0][1]["url"].endswith("getMe")
        assert self.request_received[2][1]["url"].endswith("getMe")
        assert self.request_received[1][0] == self.request_received[3][0]
        assert self.request_received[1][1].keys() == self.request_received[3][1].keys()
        for key, value in self.request_received[1][1].items():
            if isinstance(value, RequestData):
                assert value.parameters == self.request_received[3][1][key].parameters
            else:
                assert value == self.request_received[3][1][key]


@pytest.mark.skipif(
    TEST_NO_RATE_LIMITER, reason="Only relevant if the optional dependency is installed"
)
class TestAIORateLimiter:
    count = 0
    call_times = []

    class CountRequest(BaseRequest):
        def __init__(self, retry_after=None):
            self.retry_after = retry_after

        async def initialize(self) -> None:
            pass

        async def shutdown(self) -> None:
            pass

        async def do_request(self, *args, **kwargs):
            TestAIORateLimiter.count += 1
            TestAIORateLimiter.call_times.append(time.time())
            if self.retry_after:
                raise RetryAfter(retry_after=1)
            else:
                # return bot.bot.to_dict() for the `get_me` call in `Bot.initialize`
                return (
                    200,
                    json.dumps(
                        {"ok": True, "result": User(id=1, first_name="bot", is_bot=True)}
                    ).encode(),
                )

    @pytest.fixture(autouse=True)
    def reset(self):
        self.count = 0
        TestAIORateLimiter.count = 0
        self.call_times = []
        TestAIORateLimiter.call_times = []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("max_retries", [0, 1, 4])
    async def test_max_retries(self, bot, max_retries):

        bot = ExtBot(
            token=bot.token,
            request=self.CountRequest(retry_after=1),
            rate_limiter=AIORateLimiter(
                max_retries=max_retries, overall_max_rate=0, group_max_rate=0
            ),
        )
        with pytest.raises(RetryAfter):
            await bot.get_me()

        # Check that we retried the request the correct number of times
        assert TestAIORateLimiter.count == max_retries + 1

        # Check that the retries were delayed correctly
        times = TestAIORateLimiter.call_times
        if len(times) <= 1:
            return
        delays = [j - i for i, j in zip(times[:-1], times[1:])]
        assert delays == pytest.approx([1.1 for _ in range(max_retries)], rel=0.05)

    @pytest.mark.asyncio
    async def test_delay_all_pending_on_retry(self, bot):
        # Makes sure that a RetryAfter blocks *all* pending requests
        bot = ExtBot(
            token=bot.token,
            request=self.CountRequest(retry_after=1),
            rate_limiter=AIORateLimiter(max_retries=1, overall_max_rate=0, group_max_rate=0),
        )
        task_1 = asyncio.create_task(bot.get_me())
        await asyncio.sleep(0.1)
        task_2 = asyncio.create_task(bot.get_me())

        assert not task_1.done()
        assert not task_2.done()

        await asyncio.sleep(1.1)
        assert isinstance(task_1.exception(), RetryAfter)
        assert not task_2.done()

        await asyncio.sleep(1.1)
        assert isinstance(task_2.exception(), RetryAfter)
