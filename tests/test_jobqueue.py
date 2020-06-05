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
import calendar
import datetime as dtm
import os
import sys
import time
from queue import Queue
from time import sleep

import pytest
import pytz
from apscheduler.schedulers import SchedulerNotRunningError
from flaky import flaky
from telegram.ext import JobQueue, Updater, Job, CallbackContext
from telegram.utils.deprecate import TelegramDeprecationWarning


@pytest.fixture(scope='function')
def job_queue(bot, _dp):
    jq = JobQueue()
    jq.set_dispatcher(_dp)
    jq.start()
    yield jq
    jq.stop()


@pytest.mark.skipif(os.getenv('GITHUB_ACTIONS', False) and os.name == 'nt',
                    reason="On windows precise timings are not accurate.")
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
        print('this is job_datetime_tests')
        self.job_time = time.time()

    def job_context_based_callback(self, context):
        if (isinstance(context, CallbackContext)
                and isinstance(context.job, Job)
                and isinstance(context.update_queue, Queue)
                and context.job.context == 2
                and context.chat_data is None
                and context.user_data is None
                and isinstance(context.bot_data, dict)
                and context.job_queue is not context.job.job_queue):
            self.result += 1

    def test_run_once(self, job_queue):
        job_queue.run_once(self.job_run_once, 0.01)
        sleep(0.02)
        assert self.result == 1

    def test_run_once_timezone(self, job_queue, timezone):
        """Test the correct handling of aware datetimes.
        Set the target datetime to utcnow + x hours (naive) with the timezone set to utc + x hours,
        which is equivalent to now.
        """
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        when = dtm.datetime.now(timezone)
        job_queue.run_once(self.job_run_once, when)
        sleep(0.001)
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

    def test_run_repeating_first_immediate(self, job_queue):
        job_queue.run_repeating(self.job_run_once, 0.1, first=0)
        sleep(0.05)
        assert self.result == 1

    def test_run_repeating_first_timezone(self, job_queue, timezone):
        """Test correct scheduling of job when passing a timezone-aware datetime as ``first``"""
        first = dtm.datetime.now(timezone)
        job_queue.run_repeating(self.job_run_once, 0.05, first=first)
        sleep(0.001)
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
            try:
                u.stop()
            except SchedulerNotRunningError:
                pass

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
        interval = dtm.timedelta(seconds=0.05)
        expected_time = time.time() + interval.total_seconds()

        job_queue.run_once(self.job_datetime_tests, interval)
        sleep(0.06)
        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_datetime(self, job_queue):
        # Testing running at a specific datetime
        delta, now = dtm.timedelta(seconds=0.05), dtm.datetime.now(pytz.utc)
        when = now + delta
        expected_time = (now + delta).timestamp()

        job_queue.run_once(self.job_datetime_tests, when)
        sleep(0.06)
        assert self.job_time == pytest.approx(expected_time)

    def test_time_unit_dt_time_today(self, job_queue):
        # Testing running at a specific time today
        delta, now = 0.05, dtm.datetime.now(pytz.utc)
        expected_time = now + dtm.timedelta(seconds=delta)
        when = expected_time.time()
        expected_time = expected_time.timestamp()

        job_queue.run_once(self.job_datetime_tests, when)
        sleep(0.06)
        assert self.job_time == pytest.approx(expected_time)

    def test_time_unit_dt_time_tomorrow(self, job_queue):
        # Testing running at a specific time that has passed today. Since we can't wait a day, we
        # test if the job's next scheduled execution time has been calculated correctly
        delta, now = -2, dtm.datetime.now(pytz.utc)
        when = (now + dtm.timedelta(seconds=delta)).time()
        expected_time = (now + dtm.timedelta(seconds=delta, days=1)).timestamp()

        job_queue.run_once(self.job_datetime_tests, when)
        scheduled_time = job_queue.jobs()[0].next_t.timestamp()
        assert scheduled_time == pytest.approx(expected_time)

    def test_run_daily(self, job_queue):
        delta, now = 1, dtm.datetime.now(pytz.utc)
        time_of_day = (now + dtm.timedelta(seconds=delta)).time()
        expected_reschedule_time = (now + dtm.timedelta(seconds=delta, days=1)).timestamp()

        job_queue.run_daily(self.job_run_once, time_of_day)
        sleep(delta + 0.1)
        assert self.result == 1
        scheduled_time = job_queue.jobs()[0].next_t.timestamp()
        assert scheduled_time == pytest.approx(expected_reschedule_time)

    def test_run_monthly(self, job_queue, timezone):
        delta, now = 1, dtm.datetime.now(timezone)
        expected_reschedule_time = now + dtm.timedelta(seconds=delta)
        time_of_day = expected_reschedule_time.time().replace(tzinfo=timezone)

        day = now.day
        expected_reschedule_time += dtm.timedelta(calendar.monthrange(now.year, now.month)[1])
        expected_reschedule_time = expected_reschedule_time.timestamp()

        job_queue.run_monthly(self.job_run_once, time_of_day, day)
        sleep(delta + 0.1)
        assert self.result == 1
        scheduled_time = job_queue.jobs()[0].next_t.timestamp()
        assert scheduled_time == pytest.approx(expected_reschedule_time)

    def test_get_jobs(self, job_queue):
        job1 = job_queue.run_once(self.job_run_once, 10, name='name1')
        job2 = job_queue.run_once(self.job_run_once, 10, name='name1')
        job3 = job_queue.run_once(self.job_run_once, 10, name='name2')

        assert job_queue.jobs() == (job1, job2, job3)
        assert job_queue.get_jobs_by_name('name1') == (job1, job2)
        assert job_queue.get_jobs_by_name('name2') == (job3,)

    @pytest.mark.skipif(sys.version_info < (3, 0), reason='pytest fails this for no reason')
    def test_bot_in_init_deprecation(self, bot):
        with pytest.warns(TelegramDeprecationWarning):
            JobQueue(bot)

    def test_context_based_callback(self, job_queue):
        job_queue._dispatcher.use_context = True

        job_queue.run_once(self.job_context_based_callback, 0.01, context=2)
        sleep(0.03)

        assert self.result == 1
        job_queue._dispatcher.use_context = False
