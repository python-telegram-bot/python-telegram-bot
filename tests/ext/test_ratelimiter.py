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

"""
We mostly test on directly on AIORateLimiter here, b/c BaseRateLimiter doesn't contain anything
notable
"""
import asyncio
import json
import platform
import time
from datetime import datetime
from http import HTTPStatus

import pytest

from telegram import BotCommand, Chat, Message, User
from telegram.constants import ParseMode
from telegram.error import RetryAfter
from telegram.ext import AIORateLimiter, BaseRateLimiter, Defaults, ExtBot
from telegram.request import BaseRequest, RequestData
from tests.auxil.envvars import GITHUB_ACTION, TEST_WITH_OPT_DEPS


@pytest.mark.skipif(
    TEST_WITH_OPT_DEPS, reason="Only relevant if the optional dependency is not installed"
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
                commands=[BotCommand("test", "test")],
                language_code="en",
                api_kwargs={"api": "kwargs"},
            )
        async with rl_bot:
            await rl_bot.set_my_commands(
                commands=[BotCommand("test", "test")],
                language_code="en",
                rate_limit_args=(43, "test-1"),
                api_kwargs={"api": "kwargs"},
            )

        assert len(self.rl_received) == 2
        assert self.rl_received[0] == ("getMe", {}, None)
        assert self.rl_received[1] == (
            "setMyCommands",
            {"commands": [BotCommand("test", "test")], "language_code": "en", "api": "kwargs"},
            (43, "test-1"),
        )
        assert len(self.request_received) == 4
        # self.request_received[i] = i-th received request
        # self.request_received[i][0] = i-th received request's args
        # self.request_received[i][1] = i-th received request's kwargs
        assert self.request_received[0][1]["url"].endswith("getMe")
        assert self.request_received[2][1]["url"].endswith("getMe")
        assert self.request_received[1][0] == self.request_received[3][0]
        assert self.request_received[1][1].keys() == self.request_received[3][1].keys()
        for key, value in self.request_received[1][1].items():
            if isinstance(value, RequestData):
                assert value.parameters == self.request_received[3][1][key].parameters
                assert value.parameters["api"] == "kwargs"
            else:
                assert value == self.request_received[3][1][key]


@pytest.mark.skipif(
    not TEST_WITH_OPT_DEPS, reason="Only relevant if the optional dependency is installed"
)
@pytest.mark.skipif(
    bool(GITHUB_ACTION and platform.system() == "Darwin"),
    reason="The timings are apparently rather inaccurate on MacOS.",
)
@pytest.mark.flaky(10, 1)  # Timings aren't quite perfect
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

            url = kwargs.get("url").lower()
            if url.endswith("getme"):
                return (
                    HTTPStatus.OK,
                    json.dumps(
                        {"ok": True, "result": User(id=1, first_name="bot", is_bot=True).to_dict()}
                    ).encode(),
                )
            if url.endswith("sendmessage"):
                return (
                    HTTPStatus.OK,
                    json.dumps(
                        {
                            "ok": True,
                            "result": Message(
                                message_id=1, date=datetime.now(), chat=Chat(1, "chat")
                            ).to_dict(),
                        }
                    ).encode(),
                )
            return None

    @pytest.fixture(autouse=True)
    def _reset(self):
        self.count = 0
        TestAIORateLimiter.count = 0
        self.call_times = []
        TestAIORateLimiter.call_times = []

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

    @pytest.mark.parametrize("group_id", [-1, "-1", "@username"])
    @pytest.mark.parametrize("chat_id", [1, "1"])
    async def test_basic_rate_limiting(self, bot, group_id, chat_id):
        try:
            rl_bot = ExtBot(
                token=bot.token,
                request=self.CountRequest(retry_after=None),
                rate_limiter=AIORateLimiter(
                    overall_max_rate=1,
                    overall_time_period=1 / 4,
                    group_max_rate=1,
                    group_time_period=1 / 2,
                ),
            )

            async with rl_bot:
                non_group_tasks = {}
                group_tasks = {}
                for i in range(4):
                    group_tasks[i] = asyncio.create_task(
                        rl_bot.send_message(chat_id=group_id, text="test")
                    )
                for i in range(8):
                    non_group_tasks[i] = asyncio.create_task(
                        rl_bot.send_message(chat_id=chat_id, text="test")
                    )

                await asyncio.sleep(0.85)
                # We expect 5 requests:
                # 1: `get_me` from `async with rl_bot`
                # 2: `send_message` at time 0.00
                # 3: `send_message` at time 0.25
                # 4: `send_message` at time 0.50
                # 5: `send_message` at time 0.75
                assert TestAIORateLimiter.count == 5
                assert sum(1 for task in non_group_tasks.values() if task.done()) < 8
                assert sum(1 for task in group_tasks.values() if task.done()) < 4

                # 3 seconds after start
                await asyncio.sleep(3.1 - 0.85)
                assert all(task.done() for task in non_group_tasks.values())
                assert all(task.done() for task in group_tasks.values())

        finally:
            # cleanup
            await asyncio.gather(*non_group_tasks.values(), *group_tasks.values())
            TestAIORateLimiter.count = 0
            TestAIORateLimiter.call_times = []

    async def test_rate_limiting_no_chat_id(self, bot):
        try:
            rl_bot = ExtBot(
                token=bot.token,
                request=self.CountRequest(retry_after=None),
                rate_limiter=AIORateLimiter(
                    overall_max_rate=1,
                    overall_time_period=1 / 2,
                ),
            )

            async with rl_bot:
                non_chat_tasks = {}
                chat_tasks = {}
                for i in range(4):
                    chat_tasks[i] = asyncio.create_task(
                        rl_bot.send_message(chat_id=-1, text="test")
                    )
                for i in range(8):
                    non_chat_tasks[i] = asyncio.create_task(rl_bot.get_me())

                await asyncio.sleep(0.6)
                # We expect 11 requests:
                # 1: `get_me` from `async with rl_bot`
                # 2: `send_message` at time 0.00
                # 3: `send_message` at time 0.05
                # 4: 8 times `get_me`
                assert TestAIORateLimiter.count == 11
                assert sum(1 for task in non_chat_tasks.values() if task.done()) == 8
                assert sum(1 for task in chat_tasks.values() if task.done()) == 2

                # 1.6 seconds after start
                await asyncio.sleep(1.6 - 0.6)
                assert all(task.done() for task in non_chat_tasks.values())
                assert all(task.done() for task in chat_tasks.values())
        finally:
            # cleanup
            await asyncio.gather(*non_chat_tasks.values(), *chat_tasks.values())
            TestAIORateLimiter.count = 0
            TestAIORateLimiter.call_times = []

    @pytest.mark.parametrize("intermediate", [True, False])
    async def test_group_caching(self, bot, intermediate):
        try:
            max_rate = 1000
            rl_bot = ExtBot(
                token=bot.token,
                request=self.CountRequest(retry_after=None),
                rate_limiter=AIORateLimiter(
                    overall_max_rate=max_rate,
                    overall_time_period=1,
                    group_max_rate=max_rate,
                    group_time_period=1,
                ),
            )

            # Unfortunately, there is no reliable way to test this without checking the internals
            assert len(rl_bot.rate_limiter._group_limiters) == 0
            await asyncio.gather(
                *(rl_bot.send_message(chat_id=-(i + 1), text=f"{i}") for i in range(513))
            )
            if intermediate:
                await rl_bot.send_message(chat_id=-1, text="999")
                assert 1 <= len(rl_bot.rate_limiter._group_limiters) <= 513
            else:
                await asyncio.sleep(1)
                await rl_bot.send_message(chat_id=-1, text="999")
                assert len(rl_bot.rate_limiter._group_limiters) == 1
        finally:
            TestAIORateLimiter.count = 0
            TestAIORateLimiter.call_times = []
