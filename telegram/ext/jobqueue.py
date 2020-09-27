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

import datetime
import logging
import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, JobEvent

from telegram.ext.callbackcontext import CallbackContext

from typing import TYPE_CHECKING, Union, Callable, Tuple, Optional, List, Any, cast, overload
from telegram.utils.types import JSONDict
if TYPE_CHECKING:
    from telegram.ext import Dispatcher
    from telegram import Bot


class Days:
    MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
    EVERY_DAY = tuple(range(7))


class JobQueue:
    """This class allows you to periodically perform tasks with the bot. It is a convenience
    wrapper for the APScheduler library.

    Attributes:
        scheduler (:class:`apscheduler.schedulers.background.BackgroundScheduler`): The APScheduler
        bot (:class:`telegram.Bot`): The bot instance that should be passed to the jobs.
            DEPRECATED: Use :attr:`set_dispatcher` instead.

    """

    def __init__(self) -> None:
        self._dispatcher: 'Dispatcher' = None  # type: ignore[assignment]
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scheduler = BackgroundScheduler(timezone=pytz.utc)
        self.scheduler.add_listener(self._update_persistence,
                                    mask=EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

        # Dispatch errors and don't log them in the APS logger
        def aps_log_filter(record):  # type: ignore
            return 'raised an exception' not in record.msg

        logging.getLogger('apscheduler.executors.default').addFilter(aps_log_filter)
        self.scheduler.add_listener(self._dispatch_error, EVENT_JOB_ERROR)

    def _build_args(self, job: 'Job') -> List[Union[CallbackContext, 'Bot', 'Job']]:
        if self._dispatcher.use_context:
            return [CallbackContext.from_job(job, self._dispatcher)]
        return [self._dispatcher.bot, job]

    def _tz_now(self) -> datetime.datetime:
        return datetime.datetime.now(self.scheduler.timezone)

    def _update_persistence(self, event: JobEvent) -> None:
        self._dispatcher.update_persistence()

    def _dispatch_error(self, event: JobEvent) -> None:
        try:
            self._dispatcher.dispatch_error(None, event.exception)
        # Errors should not stop the thread.
        except Exception:
            self.logger.exception('An error was raised while processing the job and an '
                                  'uncaught error was raised while handling the error '
                                  'with an error_handler.')

    @overload
    def _parse_time_input(self, time: None, shift_day: bool = False) -> None:
        ...

    @overload
    def _parse_time_input(self,
                          time: Union[float, int, datetime.timedelta, datetime.datetime,
                                      datetime.time],
                          shift_day: bool = False) -> datetime.datetime:
        ...

    def _parse_time_input(self,
                          time: Union[float, int, datetime.timedelta, datetime.datetime,
                                      datetime.time, None],
                          shift_day: bool = False) -> Optional[datetime.datetime]:
        if time is None:
            return None
        if isinstance(time, (int, float)):
            return self._tz_now() + datetime.timedelta(seconds=time)
        if isinstance(time, datetime.timedelta):
            return self._tz_now() + time
        if isinstance(time, datetime.time):
            dt = datetime.datetime.combine(
                datetime.datetime.now(tz=time.tzinfo or self.scheduler.timezone).date(), time)
            if dt.tzinfo is None:
                dt = self.scheduler.timezone.localize(dt)
            if shift_day and dt <= datetime.datetime.now(pytz.utc):
                dt += datetime.timedelta(days=1)
            return dt
        # isinstance(time, datetime.datetime):
        return time

    def set_dispatcher(self, dispatcher: 'Dispatcher') -> None:
        """Set the dispatcher to be used by this JobQueue. Use this instead of passing a
        :class:`telegram.Bot` to the JobQueue, which is deprecated.

        Args:
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher.

        """
        self._dispatcher = dispatcher
        if dispatcher.bot.defaults:
            if dispatcher.bot.defaults:
                self.scheduler.configure(timezone=dispatcher.bot.defaults.tzinfo or pytz.utc)

    def run_once(self,
                 callback: Callable[['CallbackContext'], None],
                 when: Union[float, datetime.timedelta, datetime.datetime, datetime.time],
                 context: object = None,
                 name: str = None,
                 job_kwargs: JSONDict = None) -> 'Job':
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
                  which the job should run. If the timezone (``datetime.tzinfo``) is :obj:`None`,
                  the default timezone of the bot will be used.
                * :obj:`datetime.time` will be interpreted as a specific time of day at which the
                  job should run. This could be either today or, if the time has already passed,
                  tomorrow. If the timezone (``time.tzinfo``) is :obj:`None`, the
                  default timezone of the bot will be used.

            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to :obj:`None`.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.
            job_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to pass to the
                ``scheduler.add_job()``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        """
        if not job_kwargs:
            job_kwargs = {}

        name = name or callback.__name__
        job = Job(callback, context, name, self)
        dt = self._parse_time_input(when, shift_day=True)

        j = self.scheduler.add_job(callback,
                                   name=name,
                                   trigger='date',
                                   run_date=dt,
                                   args=self._build_args(job),
                                   timezone=dt.tzinfo or self.scheduler.timezone,
                                   **job_kwargs)

        job.job = j
        return job

    def run_repeating(self,
                      callback: Callable[['CallbackContext'], None],
                      interval: Union[float, datetime.timedelta],
                      first: Union[float, datetime.timedelta, datetime.datetime,
                                   datetime.time] = None,
                      last: Union[float, datetime.timedelta, datetime.datetime,
                                  datetime.time] = None,
                      context: object = None,
                      name: str = None,
                      job_kwargs: JSONDict = None) -> 'Job':
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
                  which the job should run. If the timezone (``datetime.tzinfo``) is :obj:`None`,
                  the default timezone of the bot will be used.
                * :obj:`datetime.time` will be interpreted as a specific time of day at which the
                  job should run. This could be either today or, if the time has already passed,
                  tomorrow. If the timezone (``time.tzinfo``) is :obj:`None`, the
                  default timezone of the bot will be used.

                Defaults to ``interval``
            last (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta` |                        \
                   :obj:`datetime.datetime` | :obj:`datetime.time`, optional):
                Latest possible time for the job to run. This parameter will be interpreted
                depending on its type. See ``first`` for details.

                If ``last`` is :obj:`datetime.datetime` or :obj:`datetime.time` type
                and ``last.tzinfo`` is :obj:`None`, the default timezone of the bot will be
                assumed.

                Defaults to :obj:`None`.
            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to :obj:`None`.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.
            job_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to pass to the
                ``scheduler.add_job()``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        Note:
             `interval` is always respected "as-is". That means that if DST changes during that
             interval, the job might not run at the time one would expect. It is always recommended
             to pin servers to UTC time, then time related behaviour can always be expected.

        """
        if not job_kwargs:
            job_kwargs = {}

        name = name or callback.__name__
        job = Job(callback, context, name, self)

        dt_first = self._parse_time_input(first)
        dt_last = self._parse_time_input(last)

        if dt_last and dt_first and dt_last < dt_first:
            raise ValueError("'last' must not be before 'first'!")

        if isinstance(interval, datetime.timedelta):
            interval = interval.total_seconds()

        j = self.scheduler.add_job(callback,
                                   trigger='interval',
                                   args=self._build_args(job),
                                   start_date=dt_first,
                                   end_date=dt_last,
                                   seconds=interval,
                                   name=name,
                                   **job_kwargs)

        job.job = j
        return job

    def run_monthly(self,
                    callback: Callable[['CallbackContext'], None],
                    when: datetime.time,
                    day: int,
                    context: object = None,
                    name: str = None,
                    day_is_strict: bool = True,
                    job_kwargs: JSONDict = None) -> 'Job':
        """Creates a new ``Job`` that runs on a monthly basis and adds it to the queue.

        Args:
            callback (:obj:`callable`):  The callback function that should be executed by the new
                job. Callback signature for context based API:

                    ``def callback(CallbackContext)``

                ``context.job`` is the :class:`telegram.ext.Job` instance. It can be used to access
                its ``job.context`` or change it to a repeating job.
            when (:obj:`datetime.time`): Time of day at which the job should run. If the timezone
                (``when.tzinfo``) is :obj:`None`, the default timezone of the bot will be used.
            day (:obj:`int`): Defines the day of the month whereby the job would run. It should
                be within the range of 1 and 31, inclusive.
            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to :obj:`None`.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.
            day_is_strict (:obj:`bool`, optional): If :obj:`False` and day > month.days, will pick
                the last day in the month. Defaults to :obj:`True`.
            job_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to pass to the
                ``scheduler.add_job()``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        """
        if not job_kwargs:
            job_kwargs = {}

        name = name or callback.__name__
        job = Job(callback, context, name, self)

        if day_is_strict:
            j = self.scheduler.add_job(callback,
                                       trigger='cron',
                                       args=self._build_args(job),
                                       name=name,
                                       day=day,
                                       hour=when.hour,
                                       minute=when.minute,
                                       second=when.second,
                                       timezone=when.tzinfo or self.scheduler.timezone,
                                       **job_kwargs)
        else:
            trigger = OrTrigger([CronTrigger(day=day,
                                             hour=when.hour,
                                             minute=when.minute,
                                             second=when.second,
                                             timezone=when.tzinfo,
                                             **job_kwargs),
                                 CronTrigger(day='last',
                                             hour=when.hour,
                                             minute=when.minute,
                                             second=when.second,
                                             timezone=when.tzinfo or self.scheduler.timezone,
                                             **job_kwargs)])
            j = self.scheduler.add_job(callback,
                                       trigger=trigger,
                                       args=self._build_args(job),
                                       name=name,
                                       **job_kwargs)

        job.job = j
        return job

    def run_daily(self,
                  callback: Callable[['CallbackContext'], None],
                  time: datetime.time,
                  days: Tuple[int, ...] = Days.EVERY_DAY,
                  context: object = None,
                  name: str = None,
                  job_kwargs: JSONDict = None) -> 'Job':
        """Creates a new ``Job`` that runs on a daily basis and adds it to the queue.

        Args:
            callback (:obj:`callable`): The callback function that should be executed by the new
                job. Callback signature for context based API:

                    ``def callback(CallbackContext)``

                ``context.job`` is the :class:`telegram.ext.Job` instance. It can be used to access
                its ``job.context`` or change it to a repeating job.
            time (:obj:`datetime.time`): Time of day at which the job should run. If the timezone
                (``time.tzinfo``) is :obj:`None`, the default timezone of the bot will be used.
            days (Tuple[:obj:`int`], optional): Defines on which days of the week the job should
                run. Defaults to ``EVERY_DAY``
            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to :obj:`None`.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.
            job_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to pass to the
                ``scheduler.add_job()``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        Note:
            For a note about DST, please see the documentation of `APScheduler`_.

        .. _`APScheduler`: https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
                           #daylight-saving-time-behavior

        """
        if not job_kwargs:
            job_kwargs = {}

        name = name or callback.__name__
        job = Job(callback, context, name, self)

        j = self.scheduler.add_job(callback,
                                   name=name,
                                   args=self._build_args(job),
                                   trigger='cron',
                                   day_of_week=','.join([str(d) for d in days]),
                                   hour=time.hour,
                                   minute=time.minute,
                                   second=time.second,
                                   timezone=time.tzinfo or self.scheduler.timezone,
                                   **job_kwargs)

        job.job = j
        return job

    def run_custom(self,
                   callback: Callable[['CallbackContext'], None],
                   job_kwargs: JSONDict,
                   context: object = None,
                   name: str = None) -> 'Job':
        """Creates a new customly defined ``Job``.

        Args:
            callback (:obj:`callable`): The callback function that should be executed by the new
                job. Callback signature for context based API:

                    ``def callback(CallbackContext)``

                ``context.job`` is the :class:`telegram.ext.Job` instance. It can be used to access
                its ``job.context`` or change it to a repeating job.
            job_kwargs (:obj:`dict`): Arbitrary keyword arguments. Used as arguments for
                ``scheduler.add_job``.
            context (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through ``job.context`` in the callback. Defaults to ``None``.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                ``callback.__name__``.

        Returns:
            :class:`telegram.ext.Job`: The new ``Job`` instance that has been added to the job
            queue.

        """
        name = name or callback.__name__
        job = Job(callback, context, name, self)

        j = self.scheduler.add_job(callback,
                                   args=self._build_args(job),
                                   name=name,
                                   **job_kwargs)

        job.job = j
        return job

    def start(self) -> None:
        """Starts the job_queue thread."""
        if not self.scheduler.running:
            self.scheduler.start()

    def stop(self) -> None:
        """Stops the thread."""
        if self.scheduler.running:
            self.scheduler.shutdown()

    def jobs(self) -> Tuple['Job', ...]:
        """Returns a tuple of all jobs that are currently in the ``JobQueue``."""
        return tuple(Job.from_aps_job(job, self) for job in self.scheduler.get_jobs())

    def get_jobs_by_name(self, name: str) -> Tuple['Job', ...]:
        """Returns a tuple of jobs with the given name that are currently in the ``JobQueue``"""
        return tuple(job for job in self.jobs() if job.name == name)


class Job:
    """This class is a convenience wrapper for the jobs held in a :class:`telegram.ext.JobQueue`.
    With the current backend APScheduler, :attr:`job` holds a :class:`apscheduler.job.Job`
    instance.

    Note:
        * All attributes and instance methods of :attr:`job` are also directly available as
          attributes/methods of the corresponding :class:`telegram.ext.Job` object.
        * Two instances of :class:`telegram.ext.Job` are considered equal, if their corresponding
          ``job`` attributes have the same ``id``.
        * If :attr:`job` isn't passed on initialization, it must be set manually afterwards for
          this :class:`telegram.ext.Job` to be useful.

    Attributes:
        callback (:obj:`callable`): The callback function that should be executed by the new job.
        context (:obj:`object`): Optional. Additional data needed for the callback function.
        name (:obj:`str`): Optional. The name of the new job.
        job_queue (:class:`telegram.ext.JobQueue`): Optional. The ``JobQueue`` this job belongs to.
        job (:class:`apscheduler.job.Job`): Optional. The APS Job this job is a wrapper for.

    Args:
        callback (:obj:`callable`): The callback function that should be executed by the new job.
            Callback signature for context based API:

                ``def callback(CallbackContext)``

            a ``context.job`` is the :class:`telegram.ext.Job` instance. It can be used to access
            its ``job.context`` or change it to a repeating job.
        context (:obj:`object`, optional): Additional data needed for the callback function. Can be
            accessed through ``job.context`` in the callback. Defaults to :obj:`None`.
        name (:obj:`str`, optional): The name of the new job. Defaults to ``callback.__name__``.
        job_queue (:class:`telegram.ext.JobQueue`, optional): The ``JobQueue`` this job belongs to.
            Only optional for backward compatibility with ``JobQueue.put()``.
        job (:class:`apscheduler.job.Job`, optional): The APS Job this job is a wrapper for.
    """

    def __init__(self,
                 callback: Callable[['CallbackContext'], None],
                 context: object = None,
                 name: str = None,
                 job_queue: JobQueue = None,
                 job: 'Job' = None):

        self.callback = callback
        self.context = context
        self.name = name or callback.__name__
        self.job_queue = job_queue

        self._removed = False
        self._enabled = False

        self.job = cast('Job', job)

    def run(self, dispatcher: 'Dispatcher') -> None:
        """Executes the callback function independently of the jobs schedule."""
        try:
            if dispatcher.use_context:
                self.callback(CallbackContext.from_job(self, dispatcher))
            else:
                self.callback(dispatcher.bot, self)  # type: ignore[arg-type,call-arg]
        except Exception as e:
            try:
                dispatcher.dispatch_error(None, e)
            # Errors should not stop the thread.
            except Exception:
                dispatcher.logger.exception('An error was raised while processing the job and an '
                                            'uncaught error was raised while handling the error '
                                            'with an error_handler.')

    def schedule_removal(self) -> None:
        """
        Schedules this job for removal from the ``JobQueue``. It will be removed without executing
        its callback function again.
        """
        self.job.remove()
        self._removed = True

    @property
    def removed(self) -> bool:
        """:obj:`bool`: Whether this job is due to be removed."""
        return self._removed

    @property
    def enabled(self) -> bool:
        """:obj:`bool`: Whether this job is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, status: bool) -> None:
        if status:
            self.job.resume()
        else:
            self.job.pause()
        self._enabled = status

    @property
    def next_t(self) -> Optional[datetime.datetime]:
        """
        :obj:`datetime.datetime`: Datetime for the next job execution.
            Datetime is localized according to :attr:`tzinfo`.
            If job is removed or already ran it equals to :obj:`None`.
        """
        return self.job.next_run_time

    @classmethod
    def from_aps_job(cls, job: 'Job', job_queue: JobQueue) -> 'Job':
        # context based callbacks
        if len(job.args) == 1:
            context = job.args[0].job.context
        else:
            context = job.args[1].context
        return cls(job.func, context=context, name=job.name, job_queue=job_queue, job=job)

    def __getattr__(self, item: str) -> Any:
        return getattr(self.job, item)

    def __lt__(self, other: object) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.id == other.id
        return False
