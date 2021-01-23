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
import logging
import time
from collections import deque
from datetime import datetime

import pytest
import pytz

from telegram.ext.utils.callbackdatacache import CallbackDataCache


@pytest.fixture(scope='function')
def callback_data_cache():
    return CallbackDataCache()


class TestCallbackDataCache:
    @pytest.mark.parametrize('maxsize', [0, None, 1, 5, 2048])
    def test_init(self, maxsize):
        assert CallbackDataCache().maxsize == 1024
        ccd = CallbackDataCache(maxsize=maxsize)
        assert ccd.maxsize == maxsize
        assert isinstance(ccd._data, dict)
        assert isinstance(ccd._deque, deque)
        maxsize, data, queue = ccd.persistence_data
        assert data is ccd._data
        assert queue is ccd._deque
        assert maxsize == ccd.maxsize

    @pytest.mark.parametrize('data,queue', [({}, None), (None, deque())])
    def test_init_error(self, data, queue):
        with pytest.raises(ValueError, match='You must either pass both'):
            CallbackDataCache(data=data, queue=queue)

    @pytest.mark.parametrize('maxsize', [0, None])
    def test_full_unlimited(self, maxsize):
        ccd = CallbackDataCache(maxsize=maxsize)
        assert not ccd.full
        for i in range(100):
            ccd.put(i)
            assert not ccd.full

    def test_put(self, callback_data_cache):
        obj = {1: 'foo'}
        now = time.time()
        uuid = callback_data_cache.put(obj)
        _, data, queue = callback_data_cache.persistence_data
        assert queue == deque((uuid,))
        assert list(data.keys()) == [uuid]
        assert pytest.approx(data[uuid][0]) == now
        assert data[uuid][1] is obj

    def test_put_full(self, caplog):
        ccd = CallbackDataCache(1)
        uuid_foo = ccd.put('foo')
        assert ccd.full

        with caplog.at_level(logging.DEBUG):
            now = time.time()
            uuid_bar = ccd.put('bar')

        assert len(caplog.records) == 1
        assert uuid_foo in caplog.records[-1].getMessage()
        assert ccd.full

        _, data, queue = ccd.persistence_data
        assert queue == deque((uuid_bar,))
        assert list(data.keys()) == [uuid_bar]
        assert pytest.approx(data[uuid_bar][0]) == now
        assert data[uuid_bar][1] == 'bar'

    def test_pop(self, callback_data_cache):
        obj = {1: 'foo'}
        uuid = callback_data_cache.put(obj)
        result = callback_data_cache.pop(uuid)

        assert result is obj
        _, data, queue = callback_data_cache.persistence_data
        assert uuid not in data
        assert uuid not in queue

        with pytest.raises(IndexError, match=uuid):
            callback_data_cache.pop(uuid)

    def test_clear_all(self, callback_data_cache):
        expected = [callback_data_cache.put(i) for i in range(100)]
        out = callback_data_cache.clear()

        assert len(expected) == len(out)
        assert callback_data_cache.persistence_data == (1024, {}, deque())

        for idx, uuid in enumerate(expected):
            assert out[idx][0] == uuid
            assert out[idx][1] == idx

    @pytest.mark.parametrize('method', ['time', 'datetime'])
    def test_clear_cutoff(self, callback_data_cache, method):
        expected = [callback_data_cache.put(i) for i in range(100)]

        time.sleep(0.2)
        cutoff = time.time() if method == 'time' else datetime.now(pytz.utc)
        time.sleep(0.1)

        remaining = [callback_data_cache.put(i) for i in 'abcdefg']
        out = callback_data_cache.clear(cutoff)

        assert len(expected) == len(out)
        for idx, uuid in enumerate(expected):
            assert out[idx][0] == uuid
            assert out[idx][1] == idx
        for uuid in remaining:
            assert uuid in callback_data_cache._data
            assert uuid in callback_data_cache._deque

        assert all(obj in callback_data_cache._data for obj in remaining)
