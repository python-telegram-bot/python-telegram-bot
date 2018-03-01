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
import datetime
import os
import time
from time import sleep

import pytest
from flaky import flaky

from telegram.ext import JobQueue, Updater, Job


@pytest.fixture(scope='function')
def job_queue(bot):
    jq = JobQueue(bot)
    jq.start()
    yield jq
    jq.stop()


@pytest.mark.skipif(os.getenv('APPVEYOR'), reason="On Appveyor precise timings are not accurate.")
@flaky(10, 1)  # Timings aren't quite perfect
class TestJobQueue(object):
    result = 0
    job_time = 0

    @pytest.fixture(autouse=True)
    def reset(self):
        self.result = 0
        self.job_time = 0

    def job_run_once(self, bot, job):
        self.result += 1

    def job_with_exception(self, bot, job):
        raise Exception('Test Error')

    def job_remove_self(self, bot, job):
        self.result += 1
        job.schedule_removal()

    def job_run_once_with_context(self, bot, job):
        self.result += job.context

    def job_datetime_tests(self, bot, job):
        self.job_time = time.time()

    def test_run_once(self, job_queue):
        job_queue.run_once(self.job_run_once, 0.01)
        sleep(0.02)
        assert self.result == 1

    def test_job_with_context(self, job_queue):
        job_queue.run_once(self.job_run_once_with_context, 0.01, context=5)
        sleep(0.02)
        assert self.result == 5

    def test_run_repeating(self, job_queue):
        job_queue.run_repeating(self.job_run_once, 0.02)
        sleep(0.05)
        assert self.result == 2

    def test_run_repeating_first(self, job_queue):
        job_queue.run_repeating(self.job_run_once, 0.05, first=0.2)
        sleep(0.15)
        assert self.result == 0
        sleep(0.07)
        assert self.result == 1

    def test_multiple(self, job_queue):
        job_queue.run_once(self.job_run_once, 0.01)
        job_queue.run_once(self.job_run_once, 0.02)
        job_queue.run_repeating(self.job_run_once, 0.02)
        sleep(0.055)
        assert self.result == 4

    def test_disabled(self, job_queue):
        j1 = job_queue.run_once(self.job_run_once, 0.1)
        j2 = job_queue.run_repeating(self.job_run_once, 0.05)

        j1.enabled = False
        j2.enabled = False

        sleep(0.06)

        assert self.result == 0

        j1.enabled = True

        sleep(0.2)

        assert self.result == 1

    def test_schedule_removal(self, job_queue):
        j1 = job_queue.run_once(self.job_run_once, 0.03)
        j2 = job_queue.run_repeating(self.job_run_once, 0.02)

        sleep(0.025)

        j1.schedule_removal()
        j2.schedule_removal()

        sleep(0.04)

        assert self.result == 1

    def test_schedule_removal_from_within(self, job_queue):
        job_queue.run_repeating(self.job_remove_self, 0.01)

        sleep(0.05)

        assert self.result == 1

    def test_longer_first(self, job_queue):
        job_queue.run_once(self.job_run_once, 0.02)
        job_queue.run_once(self.job_run_once, 0.01)

        sleep(0.015)

        assert self.result == 1

    def test_error(self, job_queue):
        job_queue.run_repeating(self.job_with_exception, 0.01)
        job_queue.run_repeating(self.job_run_once, 0.02)
        sleep(0.03)
        assert self.result == 1

    def test_in_updater(self, bot):
        u = Updater(bot=bot)
        u.job_queue.start()
        try:
            u.job_queue.run_repeating(self.job_run_once, 0.02)
            sleep(0.03)
            assert self.result == 1
            u.stop()
            sleep(1)
            assert self.result == 1
        finally:
            u.stop()

    def test_time_unit_int(self, job_queue):
        # Testing seconds in int
        delta = 0.05
        expected_time = time.time() + delta

        job_queue.run_once(self.job_datetime_tests, delta)
        sleep(0.06)
        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_timedelta(self, job_queue):
        # Testing seconds, minutes and hours as datetime.timedelta object
        # This is sufficient to test that it actually works.
        interval = datetime.timedelta(seconds=0.05)
        expected_time = time.time() + interval.total_seconds()

        job_queue.run_once(self.job_datetime_tests, interval)
        sleep(0.06)
        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_datetime(self, job_queue):
        # Testing running at a specific datetime
        delta = datetime.timedelta(seconds=0.05)
        when = datetime.datetime.now() + delta
        expected_time = time.time() + delta.total_seconds()

        job_queue.run_once(self.job_datetime_tests, when)
        sleep(0.06)
        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_time_today(self, job_queue):
        # Testing running at a specific time today
        delta = 0.05
        when = (datetime.datetime.now() + datetime.timedelta(seconds=delta)).time()
        expected_time = time.time() + delta

        job_queue.run_once(self.job_datetime_tests, when)
        sleep(0.06)
        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_time_tomorrow(self, job_queue):
        # Testing running at a specific time that has passed today. Since we can't wait a day, we
        # test if the jobs next_t has been calculated correctly
        delta = -2
        when = (datetime.datetime.now() + datetime.timedelta(seconds=delta)).time()
        expected_time = time.time() + delta + 60 * 60 * 24

        job_queue.run_once(self.job_datetime_tests, when)
        assert pytest.approx(job_queue._queue.get(False)[0]) == expected_time

    def test_run_daily(self, job_queue):
        delta = 0.5
        time_of_day = (datetime.datetime.now() + datetime.timedelta(seconds=delta)).time()
        expected_time = time.time() + 60 * 60 * 24 + delta

        job_queue.run_daily(self.job_run_once, time_of_day)
        sleep(0.6)
        assert self.result == 1
        assert pytest.approx(job_queue._queue.get(False)[0]) == expected_time

    def test_warnings(self, job_queue):
        j = Job(self.job_run_once, repeat=False)
        with pytest.raises(ValueError, match='can not be set to'):
            j.repeat = True
        j.interval = 15
        assert j.interval_seconds == 15
        j.repeat = True
        with pytest.raises(ValueError, match='can not be'):
            j.interval = None
        j.repeat = False
        with pytest.raises(ValueError, match='must be of type'):
            j.interval = 'every 3 minutes'
        j.interval = 15
        assert j.interval_seconds == 15

        with pytest.raises(ValueError, match='argument should be of type'):
            j.days = 'every day'
        with pytest.raises(ValueError, match='The elements of the'):
            j.days = ('mon', 'wed')
        with pytest.raises(ValueError, match='from 0 up to and'):
            j.days = (0, 6, 12, 14)

    def test_get_jobs(self, job_queue):
        job1 = job_queue.run_once(self.job_run_once, 10, name='name1')
        job2 = job_queue.run_once(self.job_run_once, 10, name='name1')
        job3 = job_queue.run_once(self.job_run_once, 10, name='name2')

        assert job_queue.jobs() == (job1, job2, job3)
        assert job_queue.get_jobs_by_name('name1') == (job1, job2)
        assert job_queue.get_jobs_by_name('name2') == (job3,)
