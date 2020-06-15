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
import time
from queue import Queue
from time import sleep

import pytest
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
class TestJobQueue:
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

    def job_context_based_callback(self, context):
        if (isinstance(context, CallbackContext)
                and isinstance(context.job, Job)
                and isinstance(context.update_queue, Queue)
                and context.job.context == 2
                and context.chat_data is None
                and context.user_data is None
                and isinstance(context.bot_data, dict)
                and context.job_queue is context.job.job_queue):
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
        when = (dtm.datetime.utcnow() + timezone.utcoffset(None)).replace(tzinfo=timezone)
        job_queue.run_once(self.job_run_once, when)
        sleep(0.001)
        assert self.result == 1

    def test_run_once_no_time_spec(self, job_queue):
        # test that an appropiate exception is raised if a job is attempted to be scheduled
        # without specifying a time
        with pytest.raises(ValueError):
            job_queue.run_once(self.job_run_once, when=None)

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
        first = (dtm.datetime.utcnow() + timezone.utcoffset(None)).replace(tzinfo=timezone)
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
        interval = dtm.timedelta(seconds=0.05)
        expected_time = time.time() + interval.total_seconds()

        job_queue.run_once(self.job_datetime_tests, interval)
        sleep(0.06)
        assert pytest.approx(self.job_time) == expected_time

    def test_time_unit_dt_datetime(self, job_queue):
        # Testing running at a specific datetime
        delta, now = dtm.timedelta(seconds=0.05), time.time()
        when = dtm.datetime.utcfromtimestamp(now) + delta
        expected_time = now + delta.total_seconds()

        job_queue.run_once(self.job_datetime_tests, when)
        sleep(0.06)
        assert self.job_time == pytest.approx(expected_time)

    def test_time_unit_dt_time_today(self, job_queue):
        # Testing running at a specific time today
        delta, now = 0.05, time.time()
        when = (dtm.datetime.utcfromtimestamp(now) + dtm.timedelta(seconds=delta)).time()
        expected_time = now + delta

        job_queue.run_once(self.job_datetime_tests, when)
        sleep(0.06)
        assert self.job_time == pytest.approx(expected_time)

    def test_time_unit_dt_time_tomorrow(self, job_queue):
        # Testing running at a specific time that has passed today. Since we can't wait a day, we
        # test if the job's next scheduled execution time has been calculated correctly
        delta, now = -2, time.time()
        when = (dtm.datetime.utcfromtimestamp(now) + dtm.timedelta(seconds=delta)).time()
        expected_time = now + delta + 60 * 60 * 24

        job_queue.run_once(self.job_datetime_tests, when)
        assert job_queue._queue.get(False)[0] == pytest.approx(expected_time)

    def test_run_daily(self, job_queue):
        delta, now = 0.1, time.time()
        time_of_day = (dtm.datetime.utcfromtimestamp(now) + dtm.timedelta(seconds=delta)).time()
        expected_reschedule_time = now + delta + 24 * 60 * 60

        job_queue.run_daily(self.job_run_once, time_of_day)
        sleep(0.2)
        assert self.result == 1
        assert job_queue._queue.get(False)[0] == pytest.approx(expected_reschedule_time)

    def test_run_daily_with_timezone(self, job_queue):
        """test that the weekday is retrieved based on the job's timezone
        We set a job to run at the current UTC time of day (plus a small delay buffer) with a
        timezone that is---approximately (see below)---UTC +24, and set it to run on the weekday
        after the current UTC weekday. The job should therefore be executed now (because in UTC+24,
        the time of day is the same as the current weekday is the one after the current UTC
        weekday).
        """
        now = time.time()
        utcnow = dtm.datetime.utcfromtimestamp(now)
        delta = 0.1

        # must subtract one minute because the UTC offset has to be strictly less than 24h
        # thus this test will xpass if run in the interval [00:00, 00:01) UTC time
        # (because target time will be 23:59 UTC, so local and target weekday will be the same)
        target_tzinfo = dtm.timezone(dtm.timedelta(days=1, minutes=-1))
        target_datetime = (utcnow + dtm.timedelta(days=1, minutes=-1, seconds=delta)).replace(
            tzinfo=target_tzinfo)
        target_time = target_datetime.timetz()
        target_weekday = target_datetime.date().weekday()
        expected_reschedule_time = now + delta + 24 * 60 * 60

        job_queue.run_daily(self.job_run_once, time=target_time, days=(target_weekday,))
        sleep(delta + 0.1)
        assert self.result == 1
        assert job_queue._queue.get(False)[0] == pytest.approx(expected_reschedule_time)

    def test_run_monthly(self, job_queue):
        delta, now = 0.1, time.time()
        date_time = dtm.datetime.utcfromtimestamp(now)
        time_of_day = (date_time + dtm.timedelta(seconds=delta)).time()
        expected_reschedule_time = now + delta

        day = date_time.day
        expected_reschedule_time += calendar.monthrange(date_time.year,
                                                        date_time.month)[1] * 24 * 60 * 60

        job_queue.run_monthly(self.job_run_once, time_of_day, day)
        sleep(0.2)
        assert self.result == 1
        assert job_queue._queue.get(False)[0] == pytest.approx(expected_reschedule_time)

    def test_run_monthly_and_not_strict(self, job_queue):
        # This only really tests something in months with < 31 days.
        # But the trouble of patching datetime is probably not worth it

        delta, now = 0.1, time.time()
        date_time = dtm.datetime.utcfromtimestamp(now)
        time_of_day = (date_time + dtm.timedelta(seconds=delta)).time()
        expected_reschedule_time = now + delta

        day = date_time.day
        date_time += dtm.timedelta(calendar.monthrange(date_time.year,
                                                       date_time.month)[1] - day)
        # next job should be scheduled on last day of month if day_is_strict is False
        expected_reschedule_time += (calendar.monthrange(date_time.year,
                                                         date_time.month)[1] - day) * 24 * 60 * 60

        job_queue.run_monthly(self.job_run_once, time_of_day, 31, day_is_strict=False)
        assert job_queue._queue.get(False)[0] == pytest.approx(expected_reschedule_time)

    def test_run_monthly_with_timezone(self, job_queue):
        """test that the day is retrieved based on the job's timezone
        We set a job to run at the current UTC time of day (plus a small delay buffer) with a
        timezone that is---approximately (see below)---UTC +24, and set it to run on the weekday
        after the current UTC weekday. The job should therefore be executed now (because in UTC+24,
        the time of day is the same as the current weekday is the one after the current UTC
        weekday).
        """
        now = time.time()
        utcnow = dtm.datetime.utcfromtimestamp(now)
        delta = 0.1

        # must subtract one minute because the UTC offset has to be strictly less than 24h
        # thus this test will xpass if run in the interval [00:00, 00:01) UTC time
        # (because target time will be 23:59 UTC, so local and target weekday will be the same)
        target_tzinfo = dtm.timezone(dtm.timedelta(days=1, minutes=-1))
        target_datetime = (utcnow + dtm.timedelta(days=1, minutes=-1, seconds=delta)).replace(
            tzinfo=target_tzinfo)
        target_time = target_datetime.timetz()
        target_day = target_datetime.day
        expected_reschedule_time = now + delta
        expected_reschedule_time += calendar.monthrange(target_datetime.year,
                                                        target_datetime.month)[1] * 24 * 60 * 60

        job_queue.run_monthly(self.job_run_once, target_time, target_day)
        sleep(delta + 0.1)
        assert self.result == 1
        assert job_queue._queue.get(False)[0] == pytest.approx(expected_reschedule_time)

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
        with pytest.raises(TypeError, match='must be of type'):
            j.interval = 'every 3 minutes'
        j.interval = 15
        assert j.interval_seconds == 15

        with pytest.raises(TypeError, match='argument should be of type'):
            j.days = 'every day'
        with pytest.raises(TypeError, match='The elements of the'):
            j.days = ('mon', 'wed')
        with pytest.raises(ValueError, match='from 0 up to and'):
            j.days = (0, 6, 12, 14)

        with pytest.raises(TypeError, match='argument should be one of the'):
            j._set_next_t('tomorrow')

    def test_get_jobs(self, job_queue):
        job1 = job_queue.run_once(self.job_run_once, 10, name='name1')
        job2 = job_queue.run_once(self.job_run_once, 10, name='name1')
        job3 = job_queue.run_once(self.job_run_once, 10, name='name2')

        assert job_queue.jobs() == (job1, job2, job3)
        assert job_queue.get_jobs_by_name('name1') == (job1, job2)
        assert job_queue.get_jobs_by_name('name2') == (job3,)

    def test_bot_in_init_deprecation(self, bot):
        with pytest.warns(TelegramDeprecationWarning):
            JobQueue(bot)

    def test_context_based_callback(self, job_queue):
        job_queue.run_once(self.job_context_based_callback, 0.01, context=2)

        sleep(0.03)

        assert self.result == 0

    def test_job_default_tzinfo(self, job_queue):
        """Test that default tzinfo is always set to UTC"""
        job_1 = job_queue.run_once(self.job_run_once, 0.01)
        job_2 = job_queue.run_repeating(self.job_run_once, 10)
        job_3 = job_queue.run_daily(self.job_run_once, time=dtm.time(hour=15))

        jobs = [job_1, job_2, job_3]

        for job in jobs:
            assert job.tzinfo == dtm.timezone.utc

    def test_job_next_t_property(self, job_queue):
        # Testing:
        # - next_t values match values from self._queue.queue (for run_once and run_repeating jobs)
        # - next_t equals None if job is removed or if it's already ran

        job1 = job_queue.run_once(self.job_run_once, 0.06, name='run_once job')
        job2 = job_queue.run_once(self.job_run_once, 0.06, name='canceled run_once job')
        job_queue.run_repeating(self.job_run_once, 0.04, name='repeatable job')

        sleep(0.05)
        job2.schedule_removal()

        with job_queue._queue.mutex:
            for t, job in job_queue._queue.queue:
                t = dtm.datetime.fromtimestamp(t, job.tzinfo)

                if job.removed:
                    assert job.next_t is None
                else:
                    assert job.next_t == t

        assert self.result == 1
        sleep(0.02)

        assert self.result == 2
        assert job1.next_t is None
        assert job2.next_t is None

    def test_job_set_next_t(self, job_queue):
        # Testing next_t setter for 'datetime.datetime' values

        job = job_queue.run_once(self.job_run_once, 0.05)

        t = dtm.datetime.now(tz=dtm.timezone(dtm.timedelta(hours=12)))
        job._set_next_t(t)
        job.tzinfo = dtm.timezone(dtm.timedelta(hours=5))
        assert job.next_t == t.astimezone(job.tzinfo)

    def test_passing_tzinfo_to_job(self, job_queue):
        """Test that tzinfo is correctly passed to job with run_once, run_daily, run_repeating
        and run_monthly methods"""

        when_dt_tz_specific = dtm.datetime.now(
            tz=dtm.timezone(dtm.timedelta(hours=12))
        ) + dtm.timedelta(seconds=2)
        when_dt_tz_utc = dtm.datetime.now() + dtm.timedelta(seconds=2)
        job_once1 = job_queue.run_once(self.job_run_once, when_dt_tz_specific)
        job_once2 = job_queue.run_once(self.job_run_once, when_dt_tz_utc)

        when_time_tz_specific = (dtm.datetime.now(
            tz=dtm.timezone(dtm.timedelta(hours=12))
        ) + dtm.timedelta(seconds=2)).timetz()
        when_time_tz_utc = (dtm.datetime.now() + dtm.timedelta(seconds=2)).timetz()
        job_once3 = job_queue.run_once(self.job_run_once, when_time_tz_specific)
        job_once4 = job_queue.run_once(self.job_run_once, when_time_tz_utc)

        first_dt_tz_specific = dtm.datetime.now(
            tz=dtm.timezone(dtm.timedelta(hours=12))
        ) + dtm.timedelta(seconds=2)
        first_dt_tz_utc = dtm.datetime.now() + dtm.timedelta(seconds=2)
        job_repeating1 = job_queue.run_repeating(
            self.job_run_once, 2, first=first_dt_tz_specific)
        job_repeating2 = job_queue.run_repeating(
            self.job_run_once, 2, first=first_dt_tz_utc)

        first_time_tz_specific = (dtm.datetime.now(
            tz=dtm.timezone(dtm.timedelta(hours=12))
        ) + dtm.timedelta(seconds=2)).timetz()
        first_time_tz_utc = (dtm.datetime.now() + dtm.timedelta(seconds=2)).timetz()
        job_repeating3 = job_queue.run_repeating(
            self.job_run_once, 2, first=first_time_tz_specific)
        job_repeating4 = job_queue.run_repeating(
            self.job_run_once, 2, first=first_time_tz_utc)

        time_tz_specific = (dtm.datetime.now(
            tz=dtm.timezone(dtm.timedelta(hours=12))
        ) + dtm.timedelta(seconds=2)).timetz()
        time_tz_utc = (dtm.datetime.now() + dtm.timedelta(seconds=2)).timetz()
        job_daily1 = job_queue.run_daily(self.job_run_once, time_tz_specific)
        job_daily2 = job_queue.run_daily(self.job_run_once, time_tz_utc)

        job_monthly1 = job_queue.run_monthly(self.job_run_once, time_tz_specific, 1)
        job_monthly2 = job_queue.run_monthly(self.job_run_once, time_tz_utc, 1)

        assert job_once1.tzinfo == when_dt_tz_specific.tzinfo
        assert job_once2.tzinfo == dtm.timezone.utc
        assert job_once3.tzinfo == when_time_tz_specific.tzinfo
        assert job_once4.tzinfo == dtm.timezone.utc
        assert job_repeating1.tzinfo == first_dt_tz_specific.tzinfo
        assert job_repeating2.tzinfo == dtm.timezone.utc
        assert job_repeating3.tzinfo == first_time_tz_specific.tzinfo
        assert job_repeating4.tzinfo == dtm.timezone.utc
        assert job_daily1.tzinfo == time_tz_specific.tzinfo
        assert job_daily2.tzinfo == dtm.timezone.utc
        assert job_monthly1.tzinfo == time_tz_specific.tzinfo
        assert job_monthly2.tzinfo == dtm.timezone.utc
