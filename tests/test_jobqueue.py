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
import calendar
import datetime as dtm
import logging
import os
import platform
import time
from queue import Queue
from time import sleep

import pytest
import pytz
from apscheduler.schedulers import SchedulerNotRunningError
from flaky import flaky
from telegram.ext import JobQueue, Updater, Job, CallbackContext, Dispatcher, ContextTypes


class CustomContext(CallbackContext):
    pass


@pytest.fixture(scope='function')
def job_queue(bot, _dp):
    jq = JobQueue()
    jq.set_dispatcher(_dp)
    jq.start()
    yield jq
    jq.stop()


@pytest.mark.skipif(
    os.getenv('GITHUB_ACTIONS', False) and platform.system() in ['Windows', 'Darwin'],
    reason="On Windows & MacOS precise timings are not accurate.",
)
@flaky(10, 1)  # Timings aren't quite perfect
class TestJobQueue:
    result = 0
    job_time = 0
    received_error = None

    def test_slot_behaviour(self, job_queue, recwarn, mro_slots, _dp):
        for attr in job_queue.__slots__:
            assert getattr(job_queue, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not job_queue.__dict__, f"got missing slot(s): {job_queue.__dict__}"
        assert len(mro_slots(job_queue)) == len(set(mro_slots(job_queue))), "duplicate slot"
        job_queue.custom, job_queue._dispatcher = 'should give warning', _dp
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    @pytest.fixture(autouse=True)
    def reset(self):
        self.result = 0
        self.job_time = 0
        self.received_error = None

    def job_run_once(self, bot, job):
        self.result += 1

    def job_with_exception(self, bot, job=None):
        raise Exception('Test Error')

    def job_remove_self(self, bot, job):
        self.result += 1
        job.schedule_removal()

    def job_run_once_with_context(self, bot, job):
        self.result += job.context

    def job_datetime_tests(self, bot, job):
        self.job_time = time.time()

    def job_context_based_callback(self, context):
        if (
            isinstance(context, CallbackContext)
            and isinstance(context.job, Job)
            and isinstance(context.update_queue, Queue)
            and context.job.context == 2
            and context.chat_data is None
            and context.user_data is None
            and isinstance(context.bot_data, dict)
            and context.job_queue is not context.job.job_queue
        ):
            self.result += 1

    def error_handler(self, bot, update, error):
        self.received_error = str(error)

    def error_handler_context(self, update, context):
        self.received_error = str(context.error)

    def error_handler_raise_error(self, *args):
        raise Exception('Failing bigly')

    def test_run_once(self, job_queue):
        job_queue.run_once(self.job_run_once, 0.01)
        sleep(0.02)
        assert self.result == 1

    def test_run_once_timezone(self, job_queue, timezone):
        """Test the correct handling of aware datetimes"""
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

    def test_run_repeating_first_timezone(self, job_queue, timezone):
        """Test correct scheduling of job when passing a timezone-aware datetime as ``first``"""
        job_queue.run_repeating(
            self.job_run_once, 0.1, first=dtm.datetime.now(timezone) + dtm.timedelta(seconds=0.05)
        )
        sleep(0.1)
        assert self.result == 1

    def test_run_repeating_last(self, job_queue):
        job_queue.run_repeating(self.job_run_once, 0.05, last=0.06)
        sleep(0.1)
        assert self.result == 1
        sleep(0.1)
        assert self.result == 1

    def test_run_repeating_last_timezone(self, job_queue, timezone):
        """Test correct scheduling of job when passing a timezone-aware datetime as ``first``"""
        job_queue.run_repeating(
            self.job_run_once, 0.05, last=dtm.datetime.now(timezone) + dtm.timedelta(seconds=0.06)
        )
        sleep(0.1)
        assert self.result == 1
        sleep(0.1)
        assert self.result == 1

    def test_run_repeating_last_before_first(self, job_queue):
        with pytest.raises(ValueError, match="'last' must not be before 'first'!"):
            job_queue.run_repeating(self.job_run_once, 0.05, first=1, last=0.5)

    def test_run_repeating_timedelta(self, job_queue):
        job_queue.run_repeating(self.job_run_once, dtm.timedelta(minutes=3.3333e-4))
        sleep(0.05)
        assert self.result == 2

    def test_run_custom(self, job_queue):
        job_queue.run_custom(self.job_run_once, {'trigger': 'interval', 'seconds': 0.02})
        sleep(0.05)
        assert self.result == 2

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
        u = Updater(bot=bot, use_context=False)
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
        this_months_days = calendar.monthrange(now.year, now.month)[1]
        if now.month == 12:
            next_months_days = calendar.monthrange(now.year + 1, 1)[1]
        else:
            next_months_days = calendar.monthrange(now.year, now.month + 1)[1]

        expected_reschedule_time += dtm.timedelta(this_months_days)
        if day > next_months_days:
            expected_reschedule_time += dtm.timedelta(next_months_days)

        expected_reschedule_time = timezone.normalize(expected_reschedule_time)
        # Adjust the hour for the special case that between now and next month a DST switch happens
        expected_reschedule_time += dtm.timedelta(
            hours=time_of_day.hour - expected_reschedule_time.hour
        )
        expected_reschedule_time = expected_reschedule_time.timestamp()

        job_queue.run_monthly(self.job_run_once, time_of_day, day)
        sleep(delta + 0.1)
        assert self.result == 1
        scheduled_time = job_queue.jobs()[0].next_t.timestamp()
        assert scheduled_time == pytest.approx(expected_reschedule_time)

    def test_run_monthly_non_strict_day(self, job_queue, timezone):
        delta, now = 1, dtm.datetime.now(timezone)
        expected_reschedule_time = now + dtm.timedelta(seconds=delta)
        time_of_day = expected_reschedule_time.time().replace(tzinfo=timezone)

        expected_reschedule_time += dtm.timedelta(
            calendar.monthrange(now.year, now.month)[1]
        ) - dtm.timedelta(days=now.day)
        # Adjust the hour for the special case that between now & end of month a DST switch happens
        expected_reschedule_time = timezone.normalize(expected_reschedule_time)
        expected_reschedule_time += dtm.timedelta(
            hours=time_of_day.hour - expected_reschedule_time.hour
        )
        expected_reschedule_time = expected_reschedule_time.timestamp()

        job_queue.run_monthly(self.job_run_once, time_of_day, 31, day_is_strict=False)
        scheduled_time = job_queue.jobs()[0].next_t.timestamp()
        assert scheduled_time == pytest.approx(expected_reschedule_time)

    def test_default_tzinfo(self, _dp, tz_bot):
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        jq = JobQueue()
        original_bot = _dp.bot
        _dp.bot = tz_bot
        jq.set_dispatcher(_dp)
        try:
            jq.start()

            when = dtm.datetime.now(tz_bot.defaults.tzinfo) + dtm.timedelta(seconds=0.0005)
            jq.run_once(self.job_run_once, when.time())
            sleep(0.001)
            assert self.result == 1

            jq.stop()
        finally:
            _dp.bot = original_bot

    @pytest.mark.parametrize('use_context', [True, False])
    def test_get_jobs(self, job_queue, use_context):
        job_queue._dispatcher.use_context = use_context
        if use_context:
            callback = self.job_context_based_callback
        else:
            callback = self.job_run_once

        job1 = job_queue.run_once(callback, 10, name='name1')
        job2 = job_queue.run_once(callback, 10, name='name1')
        job3 = job_queue.run_once(callback, 10, name='name2')

        assert job_queue.jobs() == (job1, job2, job3)
        assert job_queue.get_jobs_by_name('name1') == (job1, job2)
        assert job_queue.get_jobs_by_name('name2') == (job3,)

    def test_context_based_callback(self, job_queue):
        job_queue._dispatcher.use_context = True

        job_queue.run_once(self.job_context_based_callback, 0.01, context=2)
        sleep(0.03)

        assert self.result == 1
        job_queue._dispatcher.use_context = False

    @pytest.mark.parametrize('use_context', [True, False])
    def test_job_run(self, _dp, use_context):
        _dp.use_context = use_context
        job_queue = JobQueue()
        job_queue.set_dispatcher(_dp)
        if use_context:
            job = job_queue.run_repeating(self.job_context_based_callback, 0.02, context=2)
        else:
            job = job_queue.run_repeating(self.job_run_once, 0.02, context=2)
        assert self.result == 0
        job.run(_dp)
        assert self.result == 1

    def test_enable_disable_job(self, job_queue):
        job = job_queue.run_repeating(self.job_run_once, 0.02)
        sleep(0.05)
        assert self.result == 2
        job.enabled = False
        assert not job.enabled
        sleep(0.05)
        assert self.result == 2
        job.enabled = True
        assert job.enabled
        sleep(0.05)
        assert self.result == 4

    def test_remove_job(self, job_queue):
        job = job_queue.run_repeating(self.job_run_once, 0.02)
        sleep(0.05)
        assert self.result == 2
        assert not job.removed
        job.schedule_removal()
        assert job.removed
        sleep(0.05)
        assert self.result == 2

    def test_job_lt_eq(self, job_queue):
        job = job_queue.run_repeating(self.job_run_once, 0.02)
        assert not job == job_queue
        assert not job < job

    def test_dispatch_error(self, job_queue, dp):
        dp.add_error_handler(self.error_handler)

        job = job_queue.run_once(self.job_with_exception, 0.05)
        sleep(0.1)
        assert self.received_error == 'Test Error'
        self.received_error = None
        job.run(dp)
        assert self.received_error == 'Test Error'

        # Remove handler
        dp.remove_error_handler(self.error_handler)
        self.received_error = None

        job = job_queue.run_once(self.job_with_exception, 0.05)
        sleep(0.1)
        assert self.received_error is None
        job.run(dp)
        assert self.received_error is None

    def test_dispatch_error_context(self, job_queue, cdp):
        cdp.add_error_handler(self.error_handler_context)

        job = job_queue.run_once(self.job_with_exception, 0.05)
        sleep(0.1)
        assert self.received_error == 'Test Error'
        self.received_error = None
        job.run(cdp)
        assert self.received_error == 'Test Error'

        # Remove handler
        cdp.remove_error_handler(self.error_handler_context)
        self.received_error = None

        job = job_queue.run_once(self.job_with_exception, 0.05)
        sleep(0.1)
        assert self.received_error is None
        job.run(cdp)
        assert self.received_error is None

    def test_dispatch_error_that_raises_errors(self, job_queue, dp, caplog):
        dp.add_error_handler(self.error_handler_raise_error)

        with caplog.at_level(logging.ERROR):
            job = job_queue.run_once(self.job_with_exception, 0.05)
        sleep(0.1)
        assert len(caplog.records) == 1
        rec = caplog.records[-1]
        assert 'processing the job' in rec.getMessage()
        assert 'uncaught error was raised while handling' in rec.getMessage()
        caplog.clear()

        with caplog.at_level(logging.ERROR):
            job.run(dp)
        assert len(caplog.records) == 1
        rec = caplog.records[-1]
        assert 'processing the job' in rec.getMessage()
        assert 'uncaught error was raised while handling' in rec.getMessage()
        caplog.clear()

        # Remove handler
        dp.remove_error_handler(self.error_handler_raise_error)
        self.received_error = None

        with caplog.at_level(logging.ERROR):
            job = job_queue.run_once(self.job_with_exception, 0.05)
        sleep(0.1)
        assert len(caplog.records) == 1
        rec = caplog.records[-1]
        assert 'No error handlers are registered' in rec.getMessage()
        caplog.clear()

        with caplog.at_level(logging.ERROR):
            job.run(dp)
        assert len(caplog.records) == 1
        rec = caplog.records[-1]
        assert 'No error handlers are registered' in rec.getMessage()

    def test_custom_context(self, bot, job_queue):
        dispatcher = Dispatcher(
            bot,
            Queue(),
            context_types=ContextTypes(
                context=CustomContext, bot_data=int, user_data=float, chat_data=complex
            ),
        )
        job_queue.set_dispatcher(dispatcher)

        def callback(context):
            self.result = (
                type(context),
                context.user_data,
                context.chat_data,
                type(context.bot_data),
            )

        job_queue.run_once(callback, 0.1)
        sleep(0.15)
        assert self.result == (CustomContext, None, None, int)
