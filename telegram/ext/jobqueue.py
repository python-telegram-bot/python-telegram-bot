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
"""This module contains the classes JobQueue and Job."""

import calendar
import datetime
import logging
import time
import warnings
import weakref
from numbers import Number
from queue import PriorityQueue, Empty
from threading import Thread, Lock, Event

from telegram.ext.callbackcontext import CallbackContext
from telegram.utils.deprecate import TelegramDeprecationWarning
from telegram.utils.helpers import to_float_timestamp


class Days:
    MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
    EVERY_DAY = tuple(range(7))


class JobQueue:
    """This class allows you to periodically perform tasks with the bot.

    Attributes:
        _queue (:obj:`PriorityQueue`): The queue that holds the Jobs.
        bot (:class:`telegram.Bot`): The bot instance that should be passed to the jobs.
            DEPRECATED: Use :attr:`set_dispatcher` instead.

    """

    def __init__(self, bot=None):
        self._queue = PriorityQueue()
        if bot:
            warnings.warn("Passing bot to jobqueue is deprecated. Please use set_dispatcher "
                          "instead!", TelegramDeprecationWarning, stacklevel=2)

            class MockDispatcher:
                def __init__(self):
                    self.bot = bot
                    self.use_context = False

            self._dispatcher = MockDispatcher()
        else:
            self._dispatcher = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__start_lock = Lock()
        self.__next_peek_lock = Lock()  # to protect self._next_peek & self.__tick
        self.__tick = Event()
        self.__thread = None
        self._next_peek = None
        self._running = False

    def set_dispatcher(self, dispatcher):
        """Set the dispatcher to be used by this JobQueue. Use this instead of passing a
        :class:`telegram.Bot` to the JobQueue, which is deprecated.

        Args:
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher.

        """
        self._dispatcher = dispatcher

    def _put(self, job, time_spec=None, previous_t=None):
        """
        Enqueues the job, scheduling its next run at the correct time.

        Args:
            job (telegram.ext.Job): job to enqueue
            time_spec (optional):
                Specification of the time for which the job should be scheduled. The precise
                semantics of this parameter depend on its type (see
                :func:`telegram.ext.JobQueue.run_repeating` for details).
                Defaults to now + ``job.interval``.
            previous_t (optional):
                Time at which the job last ran (``None`` if it hasn't run yet).

        """
        # get time at which to run:
        if time_spec is None:
            time_spec = job.interval
        if time_spec is None:
            raise ValueError("no time specification given for scheduling non-repeating job")
        next_t = to_float_timestamp(time_spec, reference_timestamp=previous_t)

        # enqueue:
        self.logger.debug('Putting job %s with t=%s', job.name, time_spec)
        self._queue.put((next_t, job))
        job._set_next_t(next_t)

        # Wake up the loop if this job should be executed next
        self._set_next_peek(next_t)

    def run_once(self, callback, when, context=None, name=None):
        """Creates a new ``Job`` that runs once and adds it to the queue.

        Args:
            callback (:obj:`callable`): The callback function that should be executed by the new
                job. Callback signature for context based API:

                    ``def callback(CallbackContext)``

                ``context.job`` is the :class:`telegram.ext.Job` instance. It can be used to access
                its ``job.context`` or change it to a repeating job.
            when (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta` |                         \
                  :obj:`datetime.datetime` | :obj:`datetime.time`):
                Time in or at which the job should run. This parameter will be interpreted
                depending on its type.

                * :obj:`int` or :obj:`float` will be interpreted as "seconds from now" in which the
                  job should run.
                * :obj:`datetime.timedelta` will be interpreted as "time from now" in which the
                  job should run.
                * :obj:`datetime.datetime` will be interpreted as a specific date and time at
                  which the job should run. If the timezone (``datetime.tzinfo``) is ``None``, UTC
                  will be assumed.
                * :obj:`datetime.time` will be interpreted as a specific time of day at which the
                  job should run. This could be either today or, if the time has already passed,
                  tomorrow. If the timezone (``time.tzinfo``) is ``None``, UTC will be assumed.

                If ``when`` is :obj:`datetime.datetime` or :obj:`datetime.time` type
                then ``when.tzinfo`` will define ``Job.tzinfo``. Otherwise UTC will be assumed.

            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to ``None``.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        """
        tzinfo = when.tzinfo if isinstance(when, (datetime.datetime, datetime.time)) else None

        job = Job(callback,
                  repeat=False,
                  context=context,
                  name=name,
                  job_queue=self,
                  tzinfo=tzinfo)
        self._put(job, time_spec=when)
        return job

    def run_repeating(self, callback, interval, first=None, context=None, name=None):
        """Creates a new ``Job`` that runs at specified intervals and adds it to the queue.

        Args:
            callback (:obj:`callable`): The callback function that should be executed by the new
                job. Callback signature for context based API:

                    ``def callback(CallbackContext)``

                ``context.job`` is the :class:`telegram.ext.Job` instance. It can be used to access
                its ``job.context`` or change it to a repeating job.
            interval (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta`): The interval in which
                the job will run. If it is an :obj:`int` or a :obj:`float`, it will be interpreted
                as seconds.
            first (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta` |                        \
                   :obj:`datetime.datetime` | :obj:`datetime.time`, optional):
                Time in or at which the job should run. This parameter will be interpreted
                depending on its type.

                * :obj:`int` or :obj:`float` will be interpreted as "seconds from now" in which the
                  job should run.
                * :obj:`datetime.timedelta` will be interpreted as "time from now" in which the
                  job should run.
                * :obj:`datetime.datetime` will be interpreted as a specific date and time at
                  which the job should run. If the timezone (``datetime.tzinfo``) is ``None``, UTC
                  will be assumed.
                * :obj:`datetime.time` will be interpreted as a specific time of day at which the
                  job should run. This could be either today or, if the time has already passed,
                  tomorrow. If the timezone (``time.tzinfo``) is ``None``, UTC will be assumed.

                If ``first`` is :obj:`datetime.datetime` or :obj:`datetime.time` type
                then ``first.tzinfo`` will define ``Job.tzinfo``. Otherwise UTC will be assumed.

                Defaults to ``interval``
            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to ``None``.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        Note:
             `interval` is always respected "as-is". That means that if DST changes during that
             interval, the job might not run at the time one would expect. It is always recommended
             to pin servers to UTC time, then time related behaviour can always be expected.

        """
        tzinfo = first.tzinfo if isinstance(first, (datetime.datetime, datetime.time)) else None

        job = Job(callback,
                  interval=interval,
                  repeat=True,
                  context=context,
                  name=name,
                  job_queue=self,
                  tzinfo=tzinfo)
        self._put(job, time_spec=first)
        return job

    def run_monthly(self, callback, when, day, context=None, name=None, day_is_strict=True):
        """Creates a new ``Job`` that runs on a monthly basis and adds it to the queue.

        Args:
            callback (:obj:`callable`):  The callback function that should be executed by the new
                job. Callback signature for context based API:

                    ``def callback(CallbackContext)``

                ``context.job`` is the :class:`telegram.ext.Job` instance. It can be used to access
                its ``job.context`` or change it to a repeating job.
            when (:obj:`datetime.time`): Time of day at which the job should run. If the timezone
                (``when.tzinfo``) is ``None``, UTC will be assumed. This will also implicitly
                define ``Job.tzinfo``.
            day (:obj:`int`): Defines the day of the month whereby the job would run. It should
                be within the range of 1 and 31, inclusive.
            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to ``None``.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.
            day_is_strict (:obj:`bool`, optional): If ``False`` and day > month.days, will pick
                the last day in the month. Defaults to ``True``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        """
        tzinfo = when.tzinfo if isinstance(when, (datetime.datetime, datetime.time)) else None
        if 1 <= day <= 31:
            next_dt = self._get_next_month_date(day, day_is_strict, when, allow_now=True)
            job = Job(callback, repeat=False, context=context, name=name, job_queue=self,
                      is_monthly=True, day_is_strict=day_is_strict, tzinfo=tzinfo)
            self._put(job, time_spec=next_dt)
            return job
        else:
            raise ValueError("The elements of the 'day' argument should be from 1 up to"
                             " and including 31")

    def _get_next_month_date(self, day, day_is_strict, when, allow_now=False):
        """This method returns the date that the next monthly job should be scheduled.

        Args:
           day (:obj:`int`): The day of the month the job should run.
           day_is_strict (:obj:`bool`):
               Specification as to whether the specified day of job should be strictly
               respected. If day_is_strict is ``True`` it ignores months whereby the
               specified date does not exist (e.g February 31st). If it set to ``False``,
               it returns the last valid date of the month instead. For example,
               if the user runs a job on the 31st of every month, and sets
               the day_is_strict variable to ``False``, April, for example,
               the job would run on April 30th.
           when (:obj:`datetime.time`): Time of day at which the job should run. If the
               timezone (``time.tzinfo``) is ``None``, UTC will be assumed.
           allow_now (:obj:`bool`): Whether executing the job right now is a feasible options.
               For stability reasons, this defaults to :obj:`False`, but it needs to be :obj:`True`
               on initializing a job.

        """
        dt = datetime.datetime.now(tz=when.tzinfo or datetime.timezone.utc)
        dt_time = dt.time().replace(tzinfo=when.tzinfo)
        days_in_current_month = calendar.monthrange(dt.year, dt.month)[1]
        days_till_months_end = days_in_current_month - dt.day
        if days_in_current_month < day:
            # if the day does not exist in the current month (e.g Feb 31st)
            if day_is_strict is False:
                # set day as last day of month instead
                next_dt = dt + datetime.timedelta(days=days_till_months_end)
            else:
                # else set as day in subsequent month. Subsequent month is
                # guaranteed to have the date, if current month does not have the date.
                next_dt = dt + datetime.timedelta(days=days_till_months_end + day)
        else:
            # if the day exists in the current month
            if dt.day < day:
                # day is upcoming
                next_dt = dt + datetime.timedelta(day - dt.day)
            elif dt.day > day or (dt.day == day and ((not allow_now and dt_time >= when)
                                                     or (allow_now and dt_time > when))):
                # run next month if day has already passed
                next_year = dt.year + 1 if dt.month == 12 else dt.year
                next_month = 1 if dt.month == 12 else dt.month + 1
                days_in_next_month = calendar.monthrange(next_year, next_month)[1]
                next_month_has_date = days_in_next_month >= day
                if next_month_has_date:
                    next_dt = dt + datetime.timedelta(days=days_till_months_end + day)
                elif day_is_strict:
                    # schedule the subsequent month if day is strict
                    next_dt = dt + datetime.timedelta(
                        days=days_till_months_end + days_in_next_month + day)
                else:
                    # schedule in the next month last date if day is not strict
                    next_dt = dt + datetime.timedelta(days=days_till_months_end
                                                      + days_in_next_month)

            else:
                # day is today but time has not yet come
                next_dt = dt

        # Set the correct time
        next_dt = next_dt.replace(hour=when.hour, minute=when.minute, second=when.second,
                                  microsecond=when.microsecond)
        # fold is new in Py3.6
        if hasattr(next_dt, 'fold'):
            next_dt = next_dt.replace(fold=when.fold)
        return next_dt

    def run_daily(self, callback, time, days=Days.EVERY_DAY, context=None, name=None):
        """Creates a new ``Job`` that runs on a daily basis and adds it to the queue.

        Args:
            callback (:obj:`callable`): The callback function that should be executed by the new
                job. Callback signature for context based API:

                    ``def callback(CallbackContext)``

                ``context.job`` is the :class:`telegram.ext.Job` instance. It can be used to access
                its ``job.context`` or change it to a repeating job.
            time (:obj:`datetime.time`): Time of day at which the job should run. If the timezone
                (``time.tzinfo``) is ``None``, UTC will be assumed.
                ``time.tzinfo`` will implicitly define ``Job.tzinfo``.
            days (Tuple[:obj:`int`], optional): Defines on which days of the week the job should
                run. Defaults to ``EVERY_DAY``
            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to ``None``.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        Note:
             Daily is just an alias for "24 Hours". That means that if DST changes during that
             interval, the job might not run at the time one would expect. It is always recommended
             to pin servers to UTC time, then time related behaviour can always be expected.

        """
        job = Job(callback,
                  interval=datetime.timedelta(days=1),
                  repeat=True,
                  days=days,
                  tzinfo=time.tzinfo,
                  context=context,
                  name=name,
                  job_queue=self)
        self._put(job, time_spec=time)
        return job

    def _set_next_peek(self, t):
        # """
        # Set next peek if not defined or `t` is before next peek.
        # In case the next peek was set, also trigger the `self.__tick` event.
        # """
        with self.__next_peek_lock:
            if not self._next_peek or self._next_peek > t:
                self._next_peek = t
                self.__tick.set()

    def tick(self):
        """Run all jobs that are due and re-enqueue them with their interval."""
        now = time.time()

        self.logger.debug('Ticking jobs with t=%f', now)

        while True:
            try:
                t, job = self._queue.get(False)
            except Empty:
                break

            self.logger.debug('Peeked at %s with t=%f', job.name, t)

            if t > now:
                # We can get here in two conditions:
                # 1. At the second or later pass of the while loop, after we've already
                #    processed the job(s) we were supposed to at this time.
                # 2. At the first iteration of the loop only if `self.put()` had triggered
                #    `self.__tick` because `self._next_peek` wasn't set
                self.logger.debug("Next task isn't due yet. Finished!")
                self._queue.put((t, job))
                self._set_next_peek(t)
                break

            if job.removed:
                self.logger.debug('Removing job %s', job.name)
                continue

            if job.enabled:
                try:
                    current_week_day = datetime.datetime.now(job.tzinfo).date().weekday()
                    if current_week_day in job.days:
                        self.logger.debug('Running job %s', job.name)
                        job.run(self._dispatcher)
                        self._dispatcher.update_persistence()

                except Exception:
                    self.logger.exception('An uncaught error was raised while executing job %s',
                                          job.name)
            else:
                self.logger.debug('Skipping disabled job %s', job.name)

            if job.repeat and not job.removed:
                self._put(job, previous_t=t)
            elif job.is_monthly and not job.removed:
                dt = datetime.datetime.now(tz=job.tzinfo)
                dt_time = dt.time().replace(tzinfo=job.tzinfo)
                self._put(job, time_spec=self._get_next_month_date(dt.day, job.day_is_strict,
                                                                   dt_time))
            else:
                job._set_next_t(None)
                self.logger.debug('Dropping non-repeating or removed job %s', job.name)

    def start(self):
        """Starts the job_queue thread."""
        self.__start_lock.acquire()

        if not self._running:
            self._running = True
            self.__start_lock.release()
            self.__thread = Thread(target=self._main_loop,
                                   name="Bot:{}:job_queue".format(self._dispatcher.bot.id))
            self.__thread.start()
            self.logger.debug('%s thread started', self.__class__.__name__)
        else:
            self.__start_lock.release()

    def _main_loop(self):
        """
        Thread target of thread ``job_queue``. Runs in background and performs ticks on the job
        queue.

        """
        while self._running:
            # self._next_peek may be (re)scheduled during self.tick() or self.put()
            with self.__next_peek_lock:
                tmout = self._next_peek - time.time() if self._next_peek else None
                self._next_peek = None
                self.__tick.clear()

            self.__tick.wait(tmout)

            # If we were woken up by self.stop(), just bail out
            if not self._running:
                break

            self.tick()

        self.logger.debug('%s thread stopped', self.__class__.__name__)

    def stop(self):
        """Stops the thread."""
        with self.__start_lock:
            self._running = False

        self.__tick.set()
        if self.__thread is not None:
            self.__thread.join()

    def jobs(self):
        """Returns a tuple of all jobs that are currently in the ``JobQueue``."""
        with self._queue.mutex:
            return tuple(job[1] for job in self._queue.queue if job)

    def get_jobs_by_name(self, name):
        """Returns a tuple of jobs with the given name that are currently in the ``JobQueue``"""
        with self._queue.mutex:
            return tuple(job[1] for job in self._queue.queue if job and job[1].name == name)


class Job:
    """This class encapsulates a Job.

    Attributes:
        callback (:obj:`callable`): The callback function that should be executed by the new job.
        context (:obj:`object`): Optional. Additional data needed for the callback function.
        name (:obj:`str`): Optional. The name of the new job.
        is_monthly (:obj: `bool`): Optional. Indicates whether it is a monthly job.
        day_is_strict (:obj: `bool`): Optional. Indicates whether the monthly jobs day is strict.

    Args:
        callback (:obj:`callable`): The callback function that should be executed by the new job.
            Callback signature for context based API:

                ``def callback(CallbackContext)``

            a ``context.job`` is the :class:`telegram.ext.Job` instance. It can be used to access
            its ``job.context`` or change it to a repeating job.
        interval (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta`, optional): The time
            interval between executions of the job. If it is an :obj:`int` or a :obj:`float`,
            it will be interpreted as seconds. If you don't set this value, you must set
            :attr:`repeat` to ``False`` and specify :attr:`time_spec` when you put the job into
            the job queue.
        repeat (:obj:`bool`, optional): If this job should be periodically execute its callback
            function (``True``) or only once (``False``). Defaults to ``True``.
        context (:obj:`object`, optional): Additional data needed for the callback function. Can be
            accessed through ``job.context`` in the callback. Defaults to ``None``.
        name (:obj:`str`, optional): The name of the new job. Defaults to ``callback.__name__``.
        days (Tuple[:obj:`int`], optional): Defines on which days of the week the job should run.
            Defaults to ``Days.EVERY_DAY``
        job_queue (:class:`telegram.ext.JobQueue`, optional): The ``JobQueue`` this job belongs to.
            Only optional for backward compatibility with ``JobQueue.put()``.
        tzinfo (:obj:`datetime.tzinfo`, optional): timezone associated to this job. Used when
            checking the day of the week to determine whether a job should run (only relevant when
            ``days is not Days.EVERY_DAY``). Defaults to UTC.
        is_monthly (:obj:`bool`, optional): If this job is supposed to be a monthly scheduled job.
            Defaults to ``False``.
        day_is_strict (:obj:`bool`, optional): If ``False`` and day > month.days, will pick the
            last day in the month. Defaults to ``True``. Only relevant when ``is_monthly`` is
            ``True``.
    """

    def __init__(self,
                 callback,
                 interval=None,
                 repeat=True,
                 context=None,
                 days=Days.EVERY_DAY,
                 name=None,
                 job_queue=None,
                 tzinfo=None,
                 is_monthly=False,
                 day_is_strict=True):

        self.callback = callback
        self.context = context
        self.name = name or callback.__name__

        self._repeat = None
        self._interval = None
        self.interval = interval
        self._next_t = None
        self.repeat = repeat
        self.is_monthly = is_monthly
        self.day_is_strict = day_is_strict

        self._days = None
        self.days = days
        self.tzinfo = tzinfo or datetime.timezone.utc

        self._job_queue = weakref.proxy(job_queue) if job_queue is not None else None

        self._remove = Event()
        self._enabled = Event()
        self._enabled.set()

    def run(self, dispatcher):
        """Executes the callback function."""
        if dispatcher.use_context:
            self.callback(CallbackContext.from_job(self, dispatcher))
        else:
            self.callback(dispatcher.bot, self)

    def schedule_removal(self):
        """
        Schedules this job for removal from the ``JobQueue``. It will be removed without executing
        its callback function again.

        """
        self._remove.set()
        self._next_t = None

    @property
    def removed(self):
        """:obj:`bool`: Whether this job is due to be removed."""
        return self._remove.is_set()

    @property
    def enabled(self):
        """:obj:`bool`: Whether this job is enabled."""
        return self._enabled.is_set()

    @enabled.setter
    def enabled(self, status):
        if status:
            self._enabled.set()
        else:
            self._enabled.clear()

    @property
    def interval(self):
        """
        :obj:`int` | :obj:`float` | :obj:`datetime.timedelta`: Optional. The interval in which the
            job will run.

        """
        return self._interval

    @interval.setter
    def interval(self, interval):
        if interval is None and self.repeat:
            raise ValueError("The 'interval' can not be 'None' when 'repeat' is set to 'True'")

        if not (interval is None or isinstance(interval, (Number, datetime.timedelta))):
            raise TypeError("The 'interval' must be of type 'datetime.timedelta',"
                            " 'int' or 'float'")

        self._interval = interval

    @property
    def interval_seconds(self):
        """:obj:`int`: The interval for this job in seconds."""
        interval = self.interval
        if isinstance(interval, datetime.timedelta):
            return interval.total_seconds()
        else:
            return interval

    @property
    def next_t(self):
        """
        :obj:`datetime.datetime`: Datetime for the next job execution.
            Datetime is localized according to :attr:`tzinfo`.
            If job is removed or already ran it equals to ``None``.

        """
        return datetime.datetime.fromtimestamp(self._next_t, self.tzinfo) if self._next_t else None

    def _set_next_t(self, next_t):
        if isinstance(next_t, datetime.datetime):
            # Set timezone to UTC in case datetime is in local timezone.
            next_t = next_t.astimezone(datetime.timezone.utc)
            next_t = to_float_timestamp(next_t)
        elif not (isinstance(next_t, Number) or next_t is None):
            raise TypeError("The 'next_t' argument should be one of the following types: "
                            "'float', 'int', 'datetime.datetime' or 'NoneType'")

        self._next_t = next_t

    @property
    def repeat(self):
        """:obj:`bool`: Optional. If this job should periodically execute its callback function."""
        return self._repeat

    @repeat.setter
    def repeat(self, repeat):
        if self.interval is None and repeat:
            raise ValueError("'repeat' can not be set to 'True' when no 'interval' is set")
        self._repeat = repeat

    @property
    def days(self):
        """Tuple[:obj:`int`]: Optional. Defines on which days of the week the job should run."""
        return self._days

    @days.setter
    def days(self, days):
        if not isinstance(days, tuple):
            raise TypeError("The 'days' argument should be of type 'tuple'")

        if not all(isinstance(day, int) for day in days):
            raise TypeError("The elements of the 'days' argument should be of type 'int'")

        if not all(0 <= day <= 6 for day in days):
            raise ValueError("The elements of the 'days' argument should be from 0 up to and "
                             "including 6")

        self._days = days

    @property
    def job_queue(self):
        """:class:`telegram.ext.JobQueue`: Optional. The ``JobQueue`` this job belongs to."""
        return self._job_queue

    @job_queue.setter
    def job_queue(self, job_queue):
        # Property setter for backward compatibility with JobQueue.put()
        if not self._job_queue:
            self._job_queue = weakref.proxy(job_queue)
        else:
            raise RuntimeError("The 'job_queue' attribute can only be set once.")

    def __lt__(self, other):
        return False
