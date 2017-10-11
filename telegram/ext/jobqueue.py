#!/usr/bin/env python
# flake8: noqa E501
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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

import logging
import time
import warnings
import datetime
import weakref
from numbers import Number
from threading import Thread, Lock, Event
from queue import PriorityQueue, Empty


class Days(object):
    MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
    EVERY_DAY = tuple(range(7))


class JobQueue(object):
    """This class allows you to periodically perform tasks with the bot.

    Attributes:
        queue (:obj:`PriorityQueue`): The queue that holds the Jobs.
        bot (:class:`telegram.Bot`): Bot that's send to the handlers.

    Args:
        bot (:class:`telegram.Bot`): The bot instance that should be passed to the jobs.

    Deprecated:
        prevent_autostart (:obj:`bool`, optional): Thread does not start during initialisation.
        Use `start` method instead.

    """

    def __init__(self, bot, prevent_autostart=None):
        if prevent_autostart is not None:
            warnings.warn("prevent_autostart is being deprecated, use `start` method instead.")

        self.queue = PriorityQueue()
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__start_lock = Lock()
        self.__next_peek_lock = Lock()  # to protect self._next_peek & self.__tick
        self.__tick = Event()
        self.__thread = None
        self._next_peek = None
        self._running = False

    def put(self, job, next_t=None):
        """Queue a new job.

        Note:
            This method is deprecated. Please use: :attr:`run_once`, :attr:`run_daily`
            or :attr:`run_repeating` instead.

        Args:
            job (:class:`telegram.ext.Job`): The ``Job`` instance representing the new job.
            next_t (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta` | :obj:`datetime.datetime` | :obj:`datetime.time`, optional):
                Time in or at which the job should run for the first time. This parameter will
                be interpreted depending on its type.

                * :obj:`int` or :obj:`float` will be interpreted as "seconds from now" in which the
                  job should run.
                * :obj:`datetime.timedelta` will be interpreted as "time from now" in which the
                  job should run.
                * :obj:`datetime.datetime` will be interpreted as a specific date and time at
                  which the job should run.
                * :obj:`datetime.time` will be interpreted as a specific time at which the job
                  should run. This could be either today or, if the time has already passed,
                  tomorrow.

        """

        warnings.warn("'JobQueue.put' is being deprecated, use 'JobQueue.run_once', "
                      "'JobQueue.run_daily' or 'JobQueue.run_repeating' instead")
        if job.job_queue is None:
            job.job_queue = self
        self._put(job, next_t=next_t)

    def _put(self, job, next_t=None, last_t=None):
        if next_t is None:
            next_t = job.interval
            if next_t is None:
                raise ValueError('next_t is None')

        if isinstance(next_t, datetime.datetime):
            next_t = (next_t - datetime.datetime.now()).total_seconds()

        elif isinstance(next_t, datetime.time):
            next_datetime = datetime.datetime.combine(datetime.date.today(), next_t)

            if datetime.datetime.now().time() > next_t:
                next_datetime += datetime.timedelta(days=1)

            next_t = (next_datetime - datetime.datetime.now()).total_seconds()

        elif isinstance(next_t, datetime.timedelta):
            next_t = next_t.total_seconds()

        next_t += last_t or time.time()

        self.logger.debug('Putting job %s with t=%f', job.name, next_t)

        self.queue.put((next_t, job))

        # Wake up the loop if this job should be executed next
        self._set_next_peek(next_t)

    def run_once(self, callback, when, context=None, name=None):
        """Creates a new ``Job`` that runs once and adds it to the queue.

        Args:
            callback (:obj:`callable`): The callback function that should be executed by the new
                job. It should take ``bot, job`` as parameters, where ``job`` is the
                :class:`telegram.ext.Job` instance. It can be used to access it's
                ``job.context`` or change it to a repeating job.
            when (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta` | :obj:`datetime.datetime` | :obj:`datetime.time`):
                Time in or at which the job should run. This parameter will be interpreted
                depending on its type.

                * :obj:`int` or :obj:`float` will be interpreted as "seconds from now" in which the
                  job should run.
                * :obj:`datetime.timedelta` will be interpreted as "time from now" in which the
                  job should run.
                * :obj:`datetime.datetime` will be interpreted as a specific date and time at
                  which the job should run.
                * :obj:`datetime.time` will be interpreted as a specific time of day at which the
                  job should run. This could be either today or, if the time has already passed,
                  tomorrow.

            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to ``None``.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        """
        job = Job(callback, repeat=False, context=context, name=name, job_queue=self)
        self._put(job, next_t=when)
        return job

    def run_repeating(self, callback, interval, first=None, context=None, name=None):
        """Creates a new ``Job`` that runs once and adds it to the queue.

        Args:
            callback (:obj:`callable`): The callback function that should be executed by the new
                job. It should take ``bot, job`` as parameters, where ``job`` is the
                :class:`telegram.ext.Job` instance. It can be used to access it's
                ``Job.context`` or change it to a repeating job.
            interval (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta`): The interval in which
                the job will run. If it is an :obj:`int` or a :obj:`float`, it will be interpreted
                as seconds.
            first (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta` | :obj:`datetime.datetime` | :obj:`datetime.time`, optional):
                Time in or at which the job should run. This parameter will be interpreted
                depending on its type.

                * :obj:`int` or :obj:`float` will be interpreted as "seconds from now" in which the
                  job should run.
                * :obj:`datetime.timedelta` will be interpreted as "time from now" in which the
                  job should run.
                * :obj:`datetime.datetime` will be interpreted as a specific date and time at
                  which the job should run.
                * :obj:`datetime.time` will be interpreted as a specific time of day at which the
                  job should run. This could be either today or, if the time has already passed,
                  tomorrow.

                Defaults to ``interval``
            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to ``None``.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        """

        job = Job(callback,
                  interval=interval,
                  repeat=True,
                  context=context,
                  name=name,
                  job_queue=self)
        self._put(job, next_t=first)
        return job

    def run_daily(self, callback, time, days=Days.EVERY_DAY, context=None, name=None):
        """Creates a new ``Job`` that runs once and adds it to the queue.

        Args:
            callback (:obj:`callable`): The callback function that should be executed by the new
                job. It should take ``bot, job`` as parameters, where ``job`` is the
                :class:`telegram.ext.Job` instance. It can be used to access it's ``Job.context``
                or change it to a repeating job.
            time (:obj:`datetime.time`): Time of day at which the job should run.
            days (Tuple[:obj:`int`], optional): Defines on which days of the week the job should
                run. Defaults to ``EVERY_DAY``
            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to ``None``.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        """

        job = Job(callback,
                  interval=datetime.timedelta(days=1),
                  repeat=True,
                  days=days,
                  context=context,
                  name=name,
                  job_queue=self)
        self._put(job, next_t=time)
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
                t, job = self.queue.get(False)
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
                self.queue.put((t, job))
                self._set_next_peek(t)
                break

            if job.removed:
                self.logger.debug('Removing job %s', job.name)
                continue

            if job.enabled:
                try:
                    current_week_day = datetime.datetime.now().weekday()
                    if any(day == current_week_day for day in job.days):
                        self.logger.debug('Running job %s', job.name)
                        job.run(self.bot)

                except:
                    self.logger.exception('An uncaught error was raised while executing job %s',
                                          job.name)
            else:
                self.logger.debug('Skipping disabled job %s', job.name)

            if job.repeat and not job.removed:
                self._put(job, last_t=t)
            else:
                self.logger.debug('Dropping non-repeating or removed job %s', job.name)

    def start(self):
        """Starts the job_queue thread."""

        self.__start_lock.acquire()

        if not self._running:
            self._running = True
            self.__start_lock.release()
            self.__thread = Thread(target=self._main_loop, name="job_queue")
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

        return tuple(job[1] for job in self.queue.queue if job)


class Job(object):
    """This class encapsulates a Job.

    Attributes:
        callback (:obj:`callable`): The callback function that should be executed by the new job.
        context (:obj:`object`): Optional. Additional data needed for the callback function.
        name (:obj:`str`): Optional. The name of the new job.

    Args:
        callback (:obj:`callable`): The callback function that should be executed by the new job.
            It should take ``bot, job`` as parameters, where ``job`` is the
            :class:`telegram.ext.Job` instance. It can be used to access it's :attr:`context`
            or change it to a repeating job.
        interval (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta`, optional): The interval in
            which the job will run. If it is an :obj:`int` or a :obj:`float`, it will be
            interpreted as seconds. If you don't set this value, you must set :attr:`repeat` to
            ``False`` and specify :attr:`next_t` when you put the job into the job queue.
        repeat (:obj:`bool`, optional): If this job should be periodically execute its callback
            function (``True``) or only once (``False``). Defaults to ``True``.
        context (:obj:`object`, optional): Additional data needed for the callback function. Can be
            accessed through ``job.context`` in the callback. Defaults to ``None``.
        name (:obj:`str`, optional): The name of the new job. Defaults to ``callback.__name__``.
        days (Tuple[:obj:`int`], optional): Defines on which days of the week the job should run.
            Defaults to ``Days.EVERY_DAY``
        job_queue (:class:`telegram.ext.JobQueue`, optional): The ``JobQueue`` this job belongs to.
            Only optional for backward compatibility with ``JobQueue.put()``.

    """

    def __init__(self,
                 callback,
                 interval=None,
                 repeat=True,
                 context=None,
                 days=Days.EVERY_DAY,
                 name=None,
                 job_queue=None):

        self.callback = callback
        self.context = context
        self.name = name or callback.__name__

        self._repeat = repeat
        self._interval = None
        self.interval = interval
        self.repeat = repeat

        self._days = None
        self.days = days

        self._job_queue = weakref.proxy(job_queue) if job_queue is not None else None

        self._remove = Event()
        self._enabled = Event()
        self._enabled.set()

    def run(self, bot):
        """Executes the callback function."""

        self.callback(bot, self)

    def schedule_removal(self):
        """
        Schedules this job for removal from the ``JobQueue``. It will be removed without executing
        its callback function again.

        """

        self._remove.set()

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
            raise ValueError("The 'interval' must be of type 'datetime.timedelta',"
                             " 'int' or 'float'")

        self._interval = interval

    @property
    def interval_seconds(self):
        """:obj:`int`: The interval for this job in seconds."""
        if isinstance(self.interval, datetime.timedelta):
            return self.interval.total_seconds()
        else:
            return self.interval

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
            raise ValueError("The 'days' argument should be of type 'tuple'")

        if not all(isinstance(day, int) for day in days):
            raise ValueError("The elements of the 'days' argument should be of type 'int'")

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
