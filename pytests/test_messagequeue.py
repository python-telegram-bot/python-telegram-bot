#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import json

import pytest

from telegram import DelayQueue

class TestDelayQueue:

    def __init__(self, *args, **kwargs):
        self._N = kwargs.pop('N', 128)
        self._msglimit = kwargs.pop('burst_limit', 30)
        self._timelimit = kwargs.pop('time_limit_ms', 1000)
        self._margin = kwargs.pop('margin_ms', 0)
        isprint = kwargs.pop('isprint', False)

        def noprint(*args, **kwargs):
            pass

        self._print = print if isprint else noprint
        super(DelayQueueTest, self).__init__(*args, **kwargs)

    print = _print
    print('Self-test with N = {} msgs, burst_limit = {} msgs, '
      'time_limit = {:.2f} ms, margin = {:.2f} ms'
      ''.format(_N, _msglimit, _timelimit, _margin))
    testtimes = []
    
    def testcall():
            self.testtimes.append(mq.curtime())

        self.testcall = testcall

    def test_delayqueue_limits(self):
        '''Test that DelayQueue dispatched calls don't hit time-window limit'''
        print = self._print
        dsp = mq.DelayQueue(
            burst_limit=self._msglimit, time_limit_ms=self._timelimit, autostart=True)
        print('Started dispatcher {}\nStatus: {}'
              ''.format(dsp, ['inactive', 'active'][dsp.is_alive()]))
        assert dsp.is_alive() is True

        print('Dispatching {} calls @ {}'.format(self._N, time.asctime()))

        for i in range(self._N):
            dsp(self.testcall)

        print('Queue filled, waiting 4 dispatch finish @ ' + str(time.asctime()))

        starttime = mq.curtime()
        app_endtime = (
            (self._N * self._msglimit /
             (1000 * self._timelimit)) + starttime + 20)  # wait up to 20 sec more than needed
        while not dsp._queue.empty() and mq.curtime() < app_endtime:
            time.sleep(1)
        assert dsp._queue.empty() is True  # check loop exit condition

        dsp.stop()
        print('Dispatcher ' + ['stopped', '!NOT STOPPED!'][dsp.is_alive()] + ' @ ' + str(
            time.asctime()))
        assert dsp.is_alive() is False

        assert self.testtimes or self._N == 0 is True
        print('Calculating call time windows')
        passes, fails = [], []
        delta = (self._timelimit - self._margin) / 1000
        it = enumerate(range(self._msglimit + 1, len(self.testtimes)))
        for start, stop in it:
            part = self.testtimes[start:stop]
            if (part[-1] - part[0]) >= delta:
                passes.append(part)
            else:
                fails.append(part)

        print('Tested: {}, Passed: {}, Failed: {}'
              ''.format(len(passes + fails), len(passes), len(fails)))
        if fails:
            print('(!) Got mismatches: ' + ';\n'.join(map(str, fails)))
        assert fails is False


