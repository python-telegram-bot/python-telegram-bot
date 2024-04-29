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
"""Here we run tests directly with SimpleUpdateProcessor because that's easier than providing dummy
implementations for SimpleUpdateProcessor and we want to test SimpleUpdateProcessor anyway."""
import asyncio

import pytest

from telegram import Update
from telegram.ext import SimpleUpdateProcessor
from tests.auxil.asyncio_helpers import call_after
from tests.auxil.slots import mro_slots


@pytest.fixture()
def mock_processor():
    class MockProcessor(SimpleUpdateProcessor):
        test_flag = False

        async def do_process_update(self, update, coroutine):
            await coroutine
            self.test_flag = True

    return MockProcessor(5)


class TestSimpleUpdateProcessor:
    def test_slot_behaviour(self):
        inst = SimpleUpdateProcessor(1)
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.mark.parametrize("concurrent_updates", [0, -1])
    def test_init(self, concurrent_updates):
        processor = SimpleUpdateProcessor(3)
        assert processor.max_concurrent_updates == 3
        with pytest.raises(ValueError, match="must be a positive integer"):
            SimpleUpdateProcessor(concurrent_updates)

    async def test_process_update(self, mock_processor):
        """Test that process_update calls do_process_update."""
        update = Update(1)

        async def coroutine():
            pass

        await mock_processor.process_update(update, coroutine())
        # This flag is set in the mock processor in do_process_update, telling us that
        # do_process_update was called.
        assert mock_processor.test_flag

    async def test_do_process_update(self):
        """Test that do_process_update calls the coroutine."""
        processor = SimpleUpdateProcessor(1)
        update = Update(1)
        test_flag = False

        async def coroutine():
            nonlocal test_flag
            test_flag = True

        await processor.do_process_update(update, coroutine())
        assert test_flag

    async def test_max_concurrent_updates_enforcement(self, mock_processor):
        """Test that max_concurrent_updates is enforced, i.e. that the processor will run
        at most max_concurrent_updates coroutines at the same time."""
        count = 2 * mock_processor.max_concurrent_updates
        events = {i: asyncio.Event() for i in range(count)}
        queue = asyncio.Queue()
        for event in events.values():
            await queue.put(event)

        async def callback():
            await asyncio.sleep(0.5)
            (await queue.get()).set()

        # We start several calls to `process_update` at the same time, each of them taking
        # 0.5 seconds to complete. We know that they are completed when the corresponding
        # event is set.
        tasks = [
            asyncio.create_task(mock_processor.process_update(update=_, coroutine=callback()))
            for _ in range(count)
        ]

        # Right now we expect no event to be set
        for i in range(count):
            assert not events[i].is_set()

        # After 0.5 seconds (+ some buffer), we expect that exactly max_concurrent_updates
        # events are set.
        await asyncio.sleep(0.75)
        for i in range(mock_processor.max_concurrent_updates):
            assert events[i].is_set()
        for i in range(
            mock_processor.max_concurrent_updates,
            count,
        ):
            assert not events[i].is_set()

        # After wating another 0.5 seconds, we expect that the next max_concurrent_updates
        # events are set.
        await asyncio.sleep(0.5)
        for i in range(count):
            assert events[i].is_set()

        # Sanity check: we expect that all tasks are completed.
        await asyncio.gather(*tasks)

    async def test_context_manager(self, monkeypatch, mock_processor):
        self.test_flag = set()

        async def after_initialize(*args, **kwargs):
            self.test_flag.add("initialize")

        async def after_shutdown(*args, **kwargs):
            self.test_flag.add("stop")

        monkeypatch.setattr(
            SimpleUpdateProcessor,
            "initialize",
            call_after(SimpleUpdateProcessor.initialize, after_initialize),
        )
        monkeypatch.setattr(
            SimpleUpdateProcessor,
            "shutdown",
            call_after(SimpleUpdateProcessor.shutdown, after_shutdown),
        )

        async with mock_processor:
            pass

        assert self.test_flag == {"initialize", "stop"}

    async def test_context_manager_exception_on_init(self, monkeypatch, mock_processor):
        async def initialize(*args, **kwargs):
            raise RuntimeError("initialize")

        async def shutdown(*args, **kwargs):
            self.test_flag = "shutdown"

        monkeypatch.setattr(SimpleUpdateProcessor, "initialize", initialize)
        monkeypatch.setattr(SimpleUpdateProcessor, "shutdown", shutdown)

        with pytest.raises(RuntimeError, match="initialize"):
            async with mock_processor:
                pass

        assert self.test_flag == "shutdown"
