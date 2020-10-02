#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
import pickle

from telegram import TelegramError
from telegram.error import Unauthorized, InvalidToken, NetworkError, BadRequest, TimedOut, \
    ChatMigrated, RetryAfter, Conflict


class TestErrorsPickling:
    def test_telegram_error(self):
        error = TelegramError("test message")
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is TelegramError
        assert unpickled.message == error.message

    def test_unauthorized(self):
        error = Unauthorized("test message")
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is Unauthorized
        assert unpickled.message == error.message

    def test_invalid_token(self):
        error = InvalidToken()
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is InvalidToken
        assert unpickled.message == error.message

    def test_network_error(self):
        error = NetworkError("test message")
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is NetworkError
        assert unpickled.message == error.message

    def test_bad_request(self):
        error = BadRequest("test message")
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is BadRequest
        assert unpickled.message == error.message

    def test_timed_out(self):
        error = TimedOut()
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is TimedOut
        assert unpickled.message == error.message

    def test_chat_migrated(self):
        error = ChatMigrated(1234)
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is ChatMigrated
        assert unpickled.message == error.message
        assert unpickled.new_chat_id == error.new_chat_id

    def test_retry_after(self):
        error = RetryAfter(12)
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is RetryAfter
        assert unpickled.message == error.message
        assert unpickled.retry_after == error.retry_after

    def test_conflict(self):
        error = Conflict("test message")
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is Conflict
        assert unpickled.message == error.message
