#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from telegram import TelegramError
from telegram.ext.utils.promise import Promise


class TestPromise:
    """
    Here we just test the things that are not covered by the other tests anyway
    """

    test_flag = False

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def test_call(self):
        def callback():
            self.test_flag = True

        promise = Promise(callback, [], {})
        promise()

        assert promise.done
        assert self.test_flag

    def test_run_with_exception(self):
        def callback():
            raise TelegramError('Error')

        promise = Promise(callback, [], {})
        promise.run()

        assert promise.done
        assert not self.test_flag
        assert isinstance(promise.exception, TelegramError)

    def test_wait_for_exception(self):
        def callback():
            raise TelegramError('Error')

        promise = Promise(callback, [], {})
        promise.run()

        with pytest.raises(TelegramError, match='Error'):
            promise.result()
