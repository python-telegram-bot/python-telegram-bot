#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

import os
from time import sleep

import pytest

import telegram.ext.messagequeue as mq


@pytest.mark.skipif(os.getenv('APPVEYOR'), reason="On Appveyor precise timings are not accurate.")
class TestDelayQueue(object):
    N = 128
    burst_limit = 30
    time_limit_ms = 1000
    margin_ms = 0
    testtimes = []

    def call(self):
        self.testtimes.append(mq.curtime())

    def test_delayqueue_limits(self):
        dsp = mq.DelayQueue(burst_limit=self.burst_limit, time_limit_ms=self.time_limit_ms,
                            autostart=True)
        assert dsp.is_alive() is True

        for i in range(self.N):
            dsp(self.call)

        starttime = mq.curtime()
        # wait up to 20 sec more than needed
        app_endtime = ((self.N * self.burst_limit / (1000 * self.time_limit_ms)) + starttime + 20)
        while not dsp._queue.empty() and mq.curtime() < app_endtime:
            sleep(1)
        assert dsp._queue.empty() is True  # check loop exit condition

        dsp.stop()
        assert dsp.is_alive() is False

        assert self.testtimes or self.N == 0 is True
        passes, fails = [], []
        delta = (self.time_limit_ms - self.margin_ms) / 1000
        for start, stop in enumerate(range(self.burst_limit + 1, len(self.testtimes))):
            part = self.testtimes[start:stop]
            if (part[-1] - part[0]) >= delta:
                passes.append(part)
            else:
                fails.append(part)
        assert fails == []
