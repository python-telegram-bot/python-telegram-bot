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


class TestBaseUpdateProcessor:
    def test_init_with_negative_max_concurrent_updates(self):
        with pytest.raises(ValueError, match="must be a positive integer"):
            BaseUpdateProcessor(-1)

    def test_max_concurrent_updates_property(self):
        processor = BaseUpdateProcessor(3)
        assert processor.max_concurrent_updates == 3

    async def test_process_update(self, one_time_bot):
        class MockProcessor(BaseUpdateProcessor):
            async def do_process_update(self, update, coroutine):
                pass

        processor = MockProcessor(5)
        application = ApplicationBuilder().concurrent_updates(processor).bot(one_time_bot).build()
        update = Update(1, None)

        async def coroutine():
            pass

        await application.update_queue.put(1)
        await processor.process_update(update, coroutine, application)
        assert not application.update_queue.empty()


class TestSimpleUpdateProcessor:
    async def test_do_process_update(self):
        processor = SimpleUpdateProcessor(1)
        update = Update(1, None)

        async def coroutine():
            pass

        await processor.do_process_update(update, coroutine())

    async def test_equality(self):
        processor1 = SimpleUpdateProcessor(1)
        processor2 = SimpleUpdateProcessor(1)
        assert processor1 == processor2
