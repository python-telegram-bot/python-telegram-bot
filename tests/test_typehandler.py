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
from collections import OrderedDict
from queue import Queue

import pytest

from telegram import Bot
from telegram.ext import TypeHandler, CallbackContext, JobQueue


class TestTypeHandler:
    test_flag = False

    def test_slot_behaviour(self, mro_slots):
        inst = TypeHandler(dict, self.callback_context)
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def callback_context(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, dict)
            and isinstance(context.update_queue, Queue)
            and isinstance(context.job_queue, JobQueue)
            and context.user_data is None
            and context.chat_data is None
            and isinstance(context.bot_data, dict)
        )

    def test_basic(self, dp):
        handler = TypeHandler(dict, self.callback_context)
        dp.add_handler(handler)

        assert handler.check_update({'a': 1, 'b': 2})
        assert not handler.check_update('not a dict')
        dp.process_update({'a': 1, 'b': 2})
        assert self.test_flag

    def test_strict(self):
        handler = TypeHandler(dict, self.callback_context, strict=True)
        o = OrderedDict({'a': 1, 'b': 2})
        assert handler.check_update({'a': 1, 'b': 2})
        assert not handler.check_update(o)

    def test_context(self, dp):
        handler = TypeHandler(dict, self.callback_context)
        dp.add_handler(handler)

        dp.process_update({'a': 1, 'b': 2})
        assert self.test_flag
