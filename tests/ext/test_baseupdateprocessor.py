#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
import pytest

from telegram import Update
from telegram.ext import ApplicationBuilder, BaseUpdateProcessor, SimpleUpdateProcessor
from tests.auxil.asyncio_helpers import call_after


def mock_processor():
    class MockProcessor(BaseUpdateProcessor):
        async def do_process_update(self, update, coroutine):
            pass

    return MockProcessor(5)


class TestBaseUpdateProcessor:
    @pytest.mark.parametrize("concurrent_updates", [0, -1])
    def test_init(self, concurrent_updates):
        processor = BaseUpdateProcessor(3)
        assert processor.max_concurrent_updates == 3
        with pytest.raises(ValueError, match="must be a positive integer"):
            BaseUpdateProcessor(concurrent_updates)

    async def test_process_update(self, one_time_bot):
        processor = mock_processor()
        application = ApplicationBuilder().concurrent_updates(processor).bot(one_time_bot).build()
        update = Update(1)

        async def coroutine():
            pass

        await application.update_queue.put(1)
        await processor.process_update(update, coroutine, application)
        assert not application.update_queue.empty()

    async def test_context_manager(self, monkeypatch):
        processor = mock_processor()
        self.test_flag = set()

        async def after_initialize(*args, **kwargs):
            self.test_flag.add("initialize")

        async def after_shutdown(*args, **kwargs):
            self.test_flag.add("stop")

        monkeypatch.setattr(
            BaseUpdateProcessor,
            "initialize",
            call_after(BaseUpdateProcessor.initialize, after_initialize),
        )
        monkeypatch.setattr(
            BaseUpdateProcessor,
            "shutdown",
            call_after(BaseUpdateProcessor.shutdown, after_shutdown),
        )

        async with processor:
            pass

        assert self.test_flag == {"initialize", "stop"}

    async def test_context_manager_exception_on_init(self, monkeypatch):
        async def initialize(*args, **kwargs):
            raise RuntimeError("initialize")

        async def shutdown(*args, **kwargs):
            self.test_flag = "shutdown"

        monkeypatch.setattr(BaseUpdateProcessor, "initialize", initialize)
        monkeypatch.setattr(BaseUpdateProcessor, "shutdown", shutdown)

        with pytest.raises(RuntimeError, match="initialize"):
            async with mock_processor():
                pass

        assert self.test_flag == "shutdown"


class TestSimpleUpdateProcessor:
    async def test_do_process_update(self):
        processor = SimpleUpdateProcessor(1)
        update = Update(1)

        async def coroutine():
            pass

        await processor.do_process_update(update, coroutine())
