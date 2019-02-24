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
from freezegun import freeze_time
import pytest
from flaky import flaky

from telegram.ext import JobQueue, Updater, Job


DAY = 24 * 60 * 60


@pytest.fixture(scope='function')
def job_queue(bot):
    jq = JobQueue(bot)
    jq.start()
    yield jq
    jq.stop()


@pytest.fixture(scope='function')
def frozen_jq(bot):
    with freeze_time(datetime.datetime.now()) as frozen_time:
        jq = JobQueue(bot)
        jq.start()
        yield jq, frozen_time
        jq.stop()


def tick_seconds(frozen_time, seconds):
    """Simulate that we have traveled `seconds` in time."""
    frozen_time.tick(delta=datetime.timedelta(seconds=seconds))


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
        self.result += 1

    def test_run_once(self, frozen_jq):
        jq, fztime = frozen_jq
        jq.run_once(self.job_run_once, 10)

        # Simulate that 0.03 seconds have passed
        tick_seconds(fztime, 11)

        # Run due jobs
        jq.tick()

        assert self.result == 1

    def test_job_with_context(self, frozen_jq):
        jq, fz_time = frozen_jq
        jq.run_once(self.job_run_once_with_context, 10, context=5)

        tick_seconds(fz_time, 11)

        # Run due jobs
        jq.tick()

        assert self.result == 5

    def test_run_repeating(self, frozen_jq):
        job_queue, fz_time = frozen_jq
        job_queue.run_repeating(self.job_run_once, 2)

        tick_seconds(fz_time, 5)
        job_queue.tick()

        assert self.result == 2

    def test_run_repeating_first(self, frozen_jq):
        job_queue, fz_time = frozen_jq
        job_queue.run_repeating(self.job_run_once, 1, first=2)

        tick_seconds(fz_time, 1.5)
        job_queue.tick()
        assert self.result == 0

        tick_seconds(fz_time, 1)
        job_queue.tick()
        assert self.result == 1

    def test_multiple(self, frozen_jq):
        job_queue, fz_time = frozen_jq
        job_queue.run_once(self.job_run_once, 1)
        job_queue.run_once(self.job_run_once, 2)
        job_queue.run_repeating(self.job_run_once, 2)

        tick_seconds(fz_time, 5)
        job_queue.tick()
        assert self.result == 4

    def test_disabled(self, frozen_jq):
        job_queue, fz_time = frozen_jq
        j1 = job_queue.run_once(self.job_run_once, 10)
        j2 = job_queue.run_repeating(self.job_run_once, 5)

        j1.enabled = False
        j2.enabled = False

        tick_seconds(fz_time, 11)
        job_queue.tick()
        assert self.result == 0

        j2.enabled = True

        tick_seconds(fz_time, 6)
        job_queue.tick()

        assert len(job_queue.jobs()) == 1
        assert self.result == 1

    def test_schedule_removal(self, frozen_jq):
        job_queue, fz_time = frozen_jq
        j1 = job_queue.run_once(self.job_run_once, 5)
        j2 = job_queue.run_repeating(self.job_run_once, 3)

        tick_seconds(fz_time, 3.5)
        job_queue.tick()
        assert self.result == 1

        j1.schedule_removal()
        j2.schedule_removal()

        tick_seconds(fz_time, 2)
        job_queue.tick()

        assert self.result == 1

    def test_schedule_removal_from_within(self, frozen_jq):
        job_queue, fz_time = frozen_jq
        job_queue.run_repeating(self.job_remove_self, 1)

        tick_seconds(fz_time, 5)
        job_queue.tick()

        assert self.result == 1

    def test_longer_first(self, frozen_jq):
        job_queue, fz_time = frozen_jq
        job_queue.run_once(self.job_run_once, 5)
        job_queue.run_once(self.job_run_once, 3)

        tick_seconds(fz_time, 4)
        job_queue.tick()

        assert self.result == 1

    def test_error(self, frozen_jq):
        job_queue, fz_time = frozen_jq
        job_queue.run_repeating(self.job_with_exception, 1)
        job_queue.run_repeating(self.job_run_once, 2)

        tick_seconds(fz_time, 3)
        job_queue.tick()

        assert self.result == 1

    def test_in_updater(self, bot):
        with freeze_time(datetime.datetime.now()) as fz_time:
            u = Updater(bot=bot)
            u.job_queue.start()
            try:
                u.job_queue.run_repeating(self.job_run_once, 2)
                tick_seconds(fz_time, 3)
                u.job_queue.tick()
                assert self.result == 1
                u.stop()
                tick_seconds(fz_time, 5)
                assert self.result == 1
            finally:
                u.stop()

    def test_time_unit_float(self, frozen_jq):
        # Testing seconds in float
        delta = 0.05
        expected_time = time.time() + delta

        job_queue, fz_time = frozen_jq
        job_queue.run_once(self.job_datetime_tests, delta)

        tick_seconds(fz_time, 0.06)

        job_queue.tick()

        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_timedelta(self, frozen_jq):
        # Testing seconds, minutes and hours as datetime.timedelta object
        # This is sufficient to test that it actually works.
        interval = datetime.timedelta(seconds=5)
        expected_time = time.time() + interval.total_seconds()

        job_queue, fz_time = frozen_jq
        job_queue.run_once(self.job_datetime_tests, interval)

        tick_seconds(fz_time, 6)

        job_queue.tick()

        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_datetime(self, frozen_jq):
        # Testing running at a specific datetime
        delta = datetime.timedelta(seconds=0.05)
        when = datetime.datetime.now() + delta
        expected_time = time.time() + delta.total_seconds()

        job_queue, fz_time = frozen_jq
        job_queue.run_once(self.job_datetime_tests, when)

        tick_seconds(fz_time, 0.06)

        job_queue.tick()

        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_time_today(self, frozen_jq):
        # Testing running at a specific time today
        delta = 0.05
        when = (datetime.datetime.now() + datetime.timedelta(seconds=delta)).time()
        expected_time = time.time() + delta

        job_queue, fz_time = frozen_jq
        job_queue.run_once(self.job_datetime_tests, when)

        tick_seconds(fz_time, 0.06)

        job_queue.tick()

        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_time_tomorrow(self, frozen_jq):
        delta = -2
        when = (datetime.datetime.now() + datetime.timedelta(seconds=delta)).time()
        expected_time = time.time() + delta + DAY

        job_queue, fz_time = frozen_jq
        job_queue.run_once(self.job_datetime_tests, when)

        # Simulate a day has passed
        tick_seconds(fz_time, DAY)

        # Run scheduled jobs
        job_queue.tick()

        assert pytest.approx(self.job_time) == expected_time

    def test_run_daily(self, frozen_jq):
        delta = 0.5
        time_of_day = (datetime.datetime.now() + datetime.timedelta(seconds=delta)).time()

        job_queue, fz_time = frozen_jq
        job_queue.run_daily(self.job_run_once, time_of_day)

        tick_seconds(fz_time, 7 * DAY)

        job_queue.tick()

        assert self.result == 7

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
