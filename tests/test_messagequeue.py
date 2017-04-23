'''This module contains telegram.ext.messagequeue test logic'''
from __future__ import print_function, division

import sys
import os
import time
import unittest

sys.path.insert(0, os.path.dirname(__file__) + os.sep + '..')
from tests.base import BaseTest

from telegram.ext import messagequeue as mq


class DelayQueueTest(BaseTest, unittest.TestCase):

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

    def setUp(self):
        print = self._print
        print('Self-test with N = {} msgs, burst_limit = {} msgs, '
              'time_limit = {:.2f} ms, margin = {:.2f} ms'
              ''.format(self._N, self._msglimit, self._timelimit, self._margin))
        self.testtimes = []

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
        self.assertTrue(dsp.is_alive())

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
        self.assertTrue(dsp._queue.empty())  # check loop exit condition

        dsp.stop()
        print('Dispatcher ' + ['stopped', '!NOT STOPPED!'][dsp.is_alive()] + ' @ ' + str(
            time.asctime()))
        self.assertFalse(dsp.is_alive())

        self.assertTrue(self.testtimes or self._N == 0)
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
        self.assertFalse(fails)


if __name__ == '__main__':
    unittest.main()
