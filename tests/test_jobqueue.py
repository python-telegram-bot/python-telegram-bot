#!/usr/bin/env python
# encoding: utf-8
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
"""
This module contains an object that represents Tests for JobQueue
"""
import logging
import sys
import unittest
import datetime
import time
from math import ceil
from time import sleep

from tests.test_updater import MockBot

sys.path.append('.')

from telegram.ext import JobQueue, Job, Updater
from tests.base import BaseTest

# Enable logging
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class JobQueueTest(BaseTest, unittest.TestCase):
    """
    This object represents Tests for Updater, Dispatcher, WebhookServer and
    WebhookHandler
    """

    def setUp(self):
        self.jq = JobQueue(MockBot('jobqueue_test'))
        self.jq.start()
        self.result = 0
        self.job_time = 0

    def tearDown(self):
        if self.jq is not None:
            self.jq.stop()

    def job1(self, bot, job):
        self.result += 1

    def job2(self, bot, job):
        raise Exception("Test Error")

    def job3(self, bot, job):
        self.result += 1
        job.schedule_removal()

    def job4(self, bot, job):
        self.result += job.context

    def job5(self, bot, job):
        self.job_time = time.time()

    def test_basic(self):
        self.jq.put(Job(self.job1, 0.1))
        sleep(1.5)
        self.assertGreaterEqual(self.result, 10)

    def test_job_with_context(self):
        self.jq.put(Job(self.job4, 0.1, context=5))
        sleep(1.5)
        self.assertGreaterEqual(self.result, 50)

    def test_noRepeat(self):
        self.jq.put(Job(self.job1, 0.1, repeat=False))
        sleep(0.5)
        self.assertEqual(1, self.result)

    def test_nextT(self):
        self.jq.put(Job(self.job1, 0.1), next_t=0.5)
        sleep(0.45)
        self.assertEqual(0, self.result)
        sleep(0.1)
        self.assertEqual(1, self.result)

    def test_multiple(self):
        self.jq.put(Job(self.job1, 0.1, repeat=False))
        self.jq.put(Job(self.job1, 0.2, repeat=False))
        self.jq.put(Job(self.job1, 0.4))
        sleep(1)
        self.assertEqual(4, self.result)

    def test_disabled(self):
        j0 = Job(self.job1, 0.1)
        j1 = Job(self.job1, 0.2)

        self.jq.put(j0)
        self.jq.put(Job(self.job1, 0.4))
        self.jq.put(j1)

        j0.enabled = False
        j1.enabled = False

        sleep(1)
        self.assertEqual(2, self.result)

    def test_schedule_removal(self):
        j0 = Job(self.job1, 0.1)
        j1 = Job(self.job1, 0.2)

        self.jq.put(j0)
        self.jq.put(Job(self.job1, 0.4))
        self.jq.put(j1)

        j0.schedule_removal()
        j1.schedule_removal()

        sleep(1)
        self.assertEqual(2, self.result)

    def test_schedule_removal_from_within(self):
        self.jq.put(Job(self.job1, 0.4))
        self.jq.put(Job(self.job3, 0.2))

        sleep(1)
        self.assertEqual(3, self.result)

    def test_longer_first(self):
        self.jq.put(Job(self.job1, 0.2, repeat=False))
        self.jq.put(Job(self.job1, 0.1, repeat=False))
        sleep(0.15)
        self.assertEqual(1, self.result)

    def test_error(self):
        self.jq.put(Job(self.job2, 0.1))
        self.jq.put(Job(self.job1, 0.2))
        sleep(0.5)
        self.assertEqual(2, self.result)

    def test_jobs_tuple(self):
        self.jq.stop()
        jobs = tuple(Job(self.job1, t) for t in range(5, 25))

        for job in jobs:
            self.jq.put(job)

        self.assertTupleEqual(jobs, self.jq.jobs())

    def test_inUpdater(self):
        u = Updater(bot="MockBot")
        u.job_queue.start()
        try:
            u.job_queue.put(Job(self.job1, 0.5))
            sleep(0.75)
            self.assertEqual(1, self.result)
            u.stop()
            sleep(2)
            self.assertEqual(1, self.result)
        finally:
            u.stop()

    def test_time_unit_int(self):
        # Testing seconds in int
        delta = 2
        expected_time = time.time() + delta

        self.jq.put(Job(self.job5, delta, repeat=False))
        sleep(2.5)
        self.assertAlmostEqual(self.job_time, expected_time, delta=0.1)

    def test_time_unit_dt_timedelta(self):
        # Testing seconds, minutes and hours as datetime.timedelta object
        # This is sufficient to test that it actually works.
        interval = datetime.timedelta(seconds=2)
        expected_time = time.time() + interval.total_seconds()

        self.jq.put(Job(self.job5, interval, repeat=False))
        sleep(2.5)
        self.assertAlmostEqual(self.job_time, expected_time, delta=0.1)

    def test_time_unit_dt_datetime(self):
        # Testing running at a specific datetime
        delta = datetime.timedelta(seconds=2)
        next_t = datetime.datetime.now() + delta
        expected_time = time.time() + delta.total_seconds()

        self.jq.put(Job(self.job5, repeat=False), next_t=next_t)
        sleep(2.5)
        self.assertAlmostEqual(self.job_time, expected_time, delta=0.1)

    def test_time_unit_dt_time_today(self):
        # Testing running at a specific time today
        delta = 2
        current_time = datetime.datetime.now().time()
        next_t = datetime.time(current_time.hour, current_time.minute, current_time.second + delta,
                               current_time.microsecond)
        expected_time = time.time() + delta

        self.jq.put(Job(self.job5, repeat=False), next_t=next_t)
        sleep(2.5)
        self.assertAlmostEqual(self.job_time, expected_time, delta=0.1)

    def test_time_unit_dt_time_tomorrow(self):
        # Testing running at a specific time that has passed today. Since we can't wait a day, we
        # test if the jobs next_t has been calculated correctly
        delta = -2
        current_time = datetime.datetime.now().time()
        next_t = datetime.time(current_time.hour, current_time.minute, current_time.second + delta,
                               current_time.microsecond)
        expected_time = time.time() + delta + 60 * 60 * 24

        self.jq.put(Job(self.job5, repeat=False), next_t=next_t)
        self.assertAlmostEqual(self.jq.queue.get(False)[0], expected_time, delta=0.1)

    def test_one_time_job(self):
        delta = 2
        expected_time = time.time() + delta

        self.jq.one_time_job(self.job5, delta)
        sleep(2.5)
        self.assertAlmostEqual(self.job_time, expected_time, delta=0.1)

    def test_repeating_job(self):
        interval = 0.1
        first = 1.5

        self.jq.repeating_job(self.job1, interval, first=first)
        sleep(2.505)
        self.assertAlmostEqual(self.result, 10, delta=1)

    def test_daily_job(self):
        delta = 1
        current_time = datetime.datetime.now().time()
        time_of_day = datetime.time(current_time.hour, current_time.minute,
                                    current_time.second + delta, current_time.microsecond)

        expected_time = time.time() + 60 * 60 * 24 + delta

        self.jq.daily_job(self.job1, time_of_day)
        sleep(2 * delta)
        self.assertEqual(self.result, 1)
        self.assertAlmostEqual(self.jq.queue.get(False)[0], expected_time, delta=0.1)

    def test_update_job_due_time(self):
        job = self.jq.one_time_job(self.job1, datetime.datetime(2030, 1, 1))

        sleep(0.5)
        self.assertEqual(self.result, 0)

        self.jq.update_job_due_time(job, time.time() + 1)

        sleep(0.5)
        self.assertEqual(self.result, 0)

        sleep(1.5)
        self.assertEqual(self.result, 1)

    def test_job_run_immediately_one_time(self):
        job = self.jq.one_time_job(self.job1, datetime.datetime(2030, 1, 1))

        sleep(0.5)
        self.assertEqual(self.result, 0)

        job.run_immediately()

        sleep(0.5)
        self.assertEqual(self.result, 1)

    def test_job_run_immediately_skip(self):
        job = self.jq.repeating_job(self.job1, 1, first=2)

        sleep(0.5)  # 0.5s | no runs
        self.assertEqual(self.result, 0)

        job.run_immediately(keep_schedule=False, skip_next=True)

        sleep(0.5)  # 1s | first run at 0.5s, rescheduled with interval=1 but skipping the next run
        self.assertEqual(self.result, 1)

        sleep(1)  # 2s | run at 1.5s was skipped
        self.assertEqual(self.result, 1)

        sleep(1)  # 3s | run at 2.5s was back to normal
        self.assertEqual(self.result, 2)

        sleep(1)  # 4s | just to confirm
        self.assertEqual(self.result, 3)

    def test_job_run_immediately_keep(self):
        job = self.jq.repeating_job(self.job1, 1)

        sleep(0.5)  # 0.5s | no runs
        self.assertEqual(self.result, 0)

        job.run_immediately(keep_schedule=True, skip_next=False)

        # 0.75s | first run at 0.5s, rescheduled with interval=0.5 to keep up with the schedule
        sleep(0.25)
        self.assertEqual(self.result, 1)

        sleep(0.5)  # 1.25s | run at 1s, rescheduled with interval=1
        self.assertEqual(self.result, 2)

        sleep(0.5)  # 1.75s | last run still at 1s
        self.assertEqual(self.result, 2)

        sleep(1)  # 2.25s | run at 2s was back to normal
        self.assertEqual(self.result, 3)

        sleep(1)  # 3.25s | just to confirm
        self.assertEqual(self.result, 4)

    def test_job_run_immediately_keep_skip(self):
        job = self.jq.repeating_job(self.job1, 1)

        sleep(0.5)  # 0.5s | no runs
        self.assertEqual(self.result, 0)

        job.run_immediately(keep_schedule=True, skip_next=True)

        # 0.75s | first run at 0.5s, rescheduled with interval=0.5 to keep up with the schedule...
        sleep(0.25)
        self.assertEqual(self.result, 1)

        sleep(0.5)  # 1.25s | ...but run at 1s was skipped, rescheduled with interval=1
        self.assertEqual(self.result, 1)

        sleep(0.5)  # 1.75s | last run still at 1s
        self.assertEqual(self.result, 1)

        sleep(1)  # 2.25s | the run at 2s was back to normal
        self.assertEqual(self.result, 2)

        sleep(1)  # 3.25s | just to confirm
        self.assertEqual(self.result, 3)


if __name__ == '__main__':
    unittest.main()
