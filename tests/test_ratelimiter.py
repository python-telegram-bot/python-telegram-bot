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
import json
import os

import pytest

from telegram import BotCommand
from telegram.constants import ParseMode
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
    not TEST_NO_RATE_LIMITER, reason="Only relevant if the optional dependency is installed"
)
class TestAIORateLimiter:
    pass
