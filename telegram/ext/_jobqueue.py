#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
import asyncio
import datetime
import weakref
from typing import TYPE_CHECKING, Optional, Tuple, Union, cast, overload

import pytz
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.job import Job as APSJob
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from telegram._utils.types import JSONDict
from telegram._utils.warnings import warn
from telegram.ext._extbot import ExtBot
from telegram.ext._utils.types import JobCallback

if TYPE_CHECKING:
    from telegram.ext import Application


class JobQueue:
    """This class allows you to periodically perform tasks with the bot. It is a convenience
    wrapper for the APScheduler library.

    .. seealso:: :attr:`telegram.ext.Application.job_queue`,
        :attr:`telegram.ext.CallbackContext.job_queue`,
        `Timerbot Example <examples.timerbot.html>`_,
        `Job Queue <https://github.com/python-telegram-bot/
        python-telegram-bot/wiki/Extensions-%E2%80%93-JobQueue>`_

    Attributes:
        scheduler (:class:`apscheduler.schedulers.asyncio.AsyncIOScheduler`): The scheduler.

            .. versionchanged:: 20.0
                Uses :class:`~apscheduler.schedulers.asyncio.AsyncIOScheduler` instead of
                :class:`~apscheduler.schedulers.background.BackgroundScheduler`

    """

    __slots__ = ("_application", "scheduler", "_executor")
    _CRON_MAPPING = ("sun", "mon", "tue", "wed", "thu", "fri", "sat")

    def __init__(self) -> None:
        self._application: "Optional[weakref.ReferenceType[Application]]" = None
        self._executor = AsyncIOExecutor()
        self.scheduler = AsyncIOScheduler(timezone=pytz.utc, executors={"default": self._executor})

    def _tz_now(self) -> datetime.datetime:
        return datetime.datetime.now(self.scheduler.timezone)

    @overload
    def _parse_time_input(self, time: None, shift_day: bool = False) -> None:
        ...

    @overload
    def _parse_time_input(
        self,
        time: Union[float, int, datetime.timedelta, datetime.datetime, datetime.time],
        shift_day: bool = False,
    ) -> datetime.datetime:
        ...

    def _parse_time_input(
        self,
        time: Union[float, int, datetime.timedelta, datetime.datetime, datetime.time, None],
        shift_day: bool = False,
    ) -> Optional[datetime.datetime]:
        if time is None:
            return None
        if isinstance(time, (int, float)):
            return self._tz_now() + datetime.timedelta(seconds=time)
        if isinstance(time, datetime.timedelta):
            return self._tz_now() + time
        if isinstance(time, datetime.time):
            date_time = datetime.datetime.combine(
                datetime.datetime.now(tz=time.tzinfo or self.scheduler.timezone).date(), time
            )
            if date_time.tzinfo is None:
                date_time = self.scheduler.timezone.localize(date_time)
            if shift_day and date_time <= datetime.datetime.now(pytz.utc):
                date_time += datetime.timedelta(days=1)
            return date_time
        return time

    def set_application(self, application: "Application") -> None:
        """Set the application to be used by this JobQueue.

        Args:
            application (:class:`telegram.ext.Application`): The application.

        """
        self._application = weakref.ref(application)
        if isinstance(application.bot, ExtBot) and application.bot.defaults:
            self.scheduler.configure(
                timezone=application.bot.defaults.tzinfo or pytz.utc,
                executors={"default": self._executor},
            )

    @property
    def application(self) -> "Application":
        """The application this JobQueue is associated with."""
        if self._application is None:
            raise RuntimeError("No application was set for this JobQueue.")
        application = self._application()
        if application is not None:
            return application
        raise RuntimeError("The application instance is no longer alive.")

    def run_once(
        self,
        callback: JobCallback,
        when: Union[float, datetime.timedelta, datetime.datetime, datetime.time],
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
    ) -> "Job":
        """Creates a new :class:`Job` instance that runs once and adds it to the queue.

        Args:
            callback (:term:`coroutine function`): The callback function that should be executed by
                the new job. Callback signature::

                    async def callback(context: CallbackContext)

            when (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta` |                         \
                  :obj:`datetime.datetime` | :obj:`datetime.time`):
                Time in or at which the job should run. This parameter will be interpreted
                depending on its type.

                * :obj:`int` or :obj:`float` will be interpreted as "seconds from now" in which the
                  job should run.
                * :obj:`datetime.timedelta` will be interpreted as "time from now" in which the
                  job should run.
                * :obj:`datetime.datetime` will be interpreted as a specific date and time at
                  which the job should run. If the timezone (:attr:`datetime.datetime.tzinfo`) is
                  :obj:`None`, the default timezone of the bot will be used, which is UTC unless
                  :attr:`telegram.ext.Defaults.tzinfo` is used.
                * :obj:`datetime.time` will be interpreted as a specific time of day at which the
                  job should run. This could be either today or, if the time has already passed,
                  tomorrow. If the timezone (:attr:`datetime.time.tzinfo`) is :obj:`None`, the
                  default timezone of the bot will be used, which is UTC unless
                  :attr:`telegram.ext.Defaults.tzinfo` is used.

            chat_id (:obj:`int`, optional): Chat id of the chat associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.chat_data` will
                be available in the callback.

                .. versionadded:: 20.0

            user_id (:obj:`int`, optional): User id of the user associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.user_data` will
                be available in the callback.

                .. versionadded:: 20.0
            data (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through :attr:`Job.data` in the callback. Defaults to
                :obj:`None`.

                .. versionchanged:: 20.0
                    Renamed the parameter ``context`` to :paramref:`data`.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                :external:attr:`callback.__name__ <definition.__name__>`.
            job_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to pass to the
                :meth:`apscheduler.schedulers.base.BaseScheduler.add_job()`.

        Returns:
            :class:`telegram.ext.Job`: The new :class:`Job` instance that has been added to the job
            queue.

        """
        if not job_kwargs:
            job_kwargs = {}

        name = name or callback.__name__
        job = Job(callback=callback, data=data, name=name, chat_id=chat_id, user_id=user_id)
        date_time = self._parse_time_input(when, shift_day=True)

        j = self.scheduler.add_job(
            job.run,
            name=name,
            trigger="date",
            run_date=date_time,
            args=(self.application,),
            timezone=date_time.tzinfo or self.scheduler.timezone,
            **job_kwargs,
        )

        job._job = j  # pylint: disable=protected-access
        return job

    def run_repeating(
        self,
        callback: JobCallback,
        interval: Union[float, datetime.timedelta],
        first: Union[float, datetime.timedelta, datetime.datetime, datetime.time] = None,
        last: Union[float, datetime.timedelta, datetime.datetime, datetime.time] = None,
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
    ) -> "Job":
        """Creates a new :class:`Job` instance that runs at specified intervals and adds it to the
        queue.

        Note:
            For a note about DST, please see the documentation of `APScheduler`_.

        .. _`APScheduler`: https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
                           #daylight-saving-time-behavior

        Args:
            callback (:term:`coroutine function`): The callback function that should be executed by
                the new job. Callback signature::

                    async def callback(context: CallbackContext)

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
                  which the job should run. If the timezone (:attr:`datetime.datetime.tzinfo`) is
                  :obj:`None`, the default timezone of the bot will be used.
                * :obj:`datetime.time` will be interpreted as a specific time of day at which the
                  job should run. This could be either today or, if the time has already passed,
                  tomorrow. If the timezone (:attr:`datetime.time.tzinfo`) is :obj:`None`, the
                  default timezone of the bot will be used, which is UTC unless
                  :attr:`telegram.ext.Defaults.tzinfo` is used.

                Defaults to :paramref:`interval`
            last (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta` |                        \
                   :obj:`datetime.datetime` | :obj:`datetime.time`, optional):
                Latest possible time for the job to run. This parameter will be interpreted
                depending on its type. See :paramref:`first` for details.

                If :paramref:`last` is :obj:`datetime.datetime` or :obj:`datetime.time` type
                and ``last.tzinfo`` is :obj:`None`, the default timezone of the bot will be
                assumed, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is used.

                Defaults to :obj:`None`.
            data (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through :attr:`Job.data` in the callback. Defaults to
                :obj:`None`.

                .. versionchanged:: 20.0
                    Renamed the parameter ``context`` to :paramref:`data`.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                :external:attr:`callback.__name__ <definition.__name__>`.
            chat_id (:obj:`int`, optional): Chat id of the chat associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.chat_data` will
                be available in the callback.

                .. versionadded:: 20.0

            user_id (:obj:`int`, optional): User id of the user associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.user_data` will
                be available in the callback.

                .. versionadded:: 20.0
            job_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to pass to the
                :meth:`apscheduler.schedulers.base.BaseScheduler.add_job()`.

        Returns:
            :class:`telegram.ext.Job`: The new :class:`Job` instance that has been added to the job
            queue.

        """
        if not job_kwargs:
            job_kwargs = {}

        name = name or callback.__name__
        job = Job(callback=callback, data=data, name=name, chat_id=chat_id, user_id=user_id)

        dt_first = self._parse_time_input(first)
        dt_last = self._parse_time_input(last)

        if dt_last and dt_first and dt_last < dt_first:
            raise ValueError("'last' must not be before 'first'!")

        if isinstance(interval, datetime.timedelta):
            interval = interval.total_seconds()

        j = self.scheduler.add_job(
            job.run,
            trigger="interval",
            args=(self.application,),
            start_date=dt_first,
            end_date=dt_last,
            seconds=interval,
            name=name,
            **job_kwargs,
        )

        job._job = j  # pylint: disable=protected-access
        return job

    def run_monthly(
        self,
        callback: JobCallback,
        when: datetime.time,
        day: int,
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
    ) -> "Job":
        """Creates a new :class:`Job` that runs on a monthly basis and adds it to the queue.

        .. versionchanged:: 20.0
            The ``day_is_strict`` argument was removed. Instead one can now pass ``-1`` to the
            :paramref:`day` parameter to have the job run on the last day of the month.

        Args:
            callback (:term:`coroutine function`): The callback function that should be executed by
                the new job. Callback signature::

                    async def callback(context: CallbackContext)

            when (:obj:`datetime.time`): Time of day at which the job should run. If the timezone
                (``when.tzinfo``) is :obj:`None`, the default timezone of the bot will be used,
                which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is used.
            day (:obj:`int`): Defines the day of the month whereby the job would run. It should
                be within the range of ``1`` and ``31``, inclusive. If a month has fewer days than
                this number, the job will not run in this month. Passing ``-1`` leads to the job
                running on the last day of the month.
            data (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through :attr:`Job.data` in the callback. Defaults to
                :obj:`None`.

                .. versionchanged:: 20.0
                    Renamed the parameter ``context`` to :paramref:`data`.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                :external:attr:`callback.__name__ <definition.__name__>`.
            chat_id (:obj:`int`, optional): Chat id of the chat associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.chat_data` will
                be available in the callback.

                .. versionadded:: 20.0

            user_id (:obj:`int`, optional): User id of the user associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.user_data` will
                be available in the callback.

                .. versionadded:: 20.0
            job_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to pass to the
                :meth:`apscheduler.schedulers.base.BaseScheduler.add_job()`.

        Returns:
            :class:`telegram.ext.Job`: The new :class:`Job` instance that has been added to the job
            queue.

        """
        if not job_kwargs:
            job_kwargs = {}

        name = name or callback.__name__
        job = Job(callback=callback, data=data, name=name, chat_id=chat_id, user_id=user_id)

        j = self.scheduler.add_job(
            job.run,
            trigger="cron",
            args=(self.application,),
            name=name,
            day="last" if day == -1 else day,
            hour=when.hour,
            minute=when.minute,
            second=when.second,
            timezone=when.tzinfo or self.scheduler.timezone,
            **job_kwargs,
        )
        job._job = j  # pylint: disable=protected-access
        return job

    def run_daily(
        self,
        callback: JobCallback,
        time: datetime.time,
        days: Tuple[int, ...] = tuple(range(7)),
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
    ) -> "Job":
        """Creates a new :class:`Job` that runs on a daily basis and adds it to the queue.

        Note:
            For a note about DST, please see the documentation of `APScheduler`_.

        .. _`APScheduler`: https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
                           #daylight-saving-time-behavior

        Args:
            callback (:term:`coroutine function`): The callback function that should be executed by
                the new job. Callback signature::

                    async def callback(context: CallbackContext)

            time (:obj:`datetime.time`): Time of day at which the job should run. If the timezone
                (:obj:`datetime.time.tzinfo`) is :obj:`None`, the default timezone of the bot will
                be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is used.
            days (Tuple[:obj:`int`], optional): Defines on which days of the week the job should
                run (where ``0-6`` correspond to sunday - saturday). By default, the job will run
                every day.

                .. versionchanged:: 20.0
                    Changed day of the week mapping of 0-6 from monday-sunday to sunday-saturday.
            data (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through :attr:`Job.data` in the callback. Defaults to
                :obj:`None`.

                .. versionchanged:: 20.0
                    Renamed the parameter ``context`` to :paramref:`data`.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                :external:attr:`callback.__name__ <definition.__name__>`.
            chat_id (:obj:`int`, optional): Chat id of the chat associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.chat_data` will
                be available in the callback.

                .. versionadded:: 20.0

            user_id (:obj:`int`, optional): User id of the user associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.user_data` will
                be available in the callback.

                .. versionadded:: 20.0
            job_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to pass to the
                :meth:`apscheduler.schedulers.base.BaseScheduler.add_job()`.

        Returns:
            :class:`telegram.ext.Job`: The new :class:`Job` instance that has been added to the job
            queue.

        """
        # TODO: After v20.0, we should remove the this warning.
        warn(
            "Prior to v20.0 the `days` parameter was not aligned to that of cron's weekday scheme."
            "We recommend double checking if the passed value is correct.",
            stacklevel=2,
        )
        if not job_kwargs:
            job_kwargs = {}

        name = name or callback.__name__
        job = Job(callback=callback, data=data, name=name, chat_id=chat_id, user_id=user_id)

        j = self.scheduler.add_job(
            job.run,
            name=name,
            args=(self.application,),
            trigger="cron",
            day_of_week=",".join([self._CRON_MAPPING[d] for d in days]),
            hour=time.hour,
            minute=time.minute,
            second=time.second,
            timezone=time.tzinfo or self.scheduler.timezone,
            **job_kwargs,
        )

        job._job = j  # pylint: disable=protected-access
        return job

    def run_custom(
        self,
        callback: JobCallback,
        job_kwargs: JSONDict,
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
    ) -> "Job":
        """Creates a new custom defined :class:`Job`.

        Args:
            callback (:term:`coroutine function`): The callback function that should be executed by
                the new job. Callback signature::

                    async def callback(context: CallbackContext)

            job_kwargs (:obj:`dict`): Arbitrary keyword arguments. Used as arguments for
                :meth:`apscheduler.schedulers.base.BaseScheduler.add_job`.
            data (:obj:`object`, optional): Additional data needed for the callback function.
                Can be accessed through :attr:`Job.data` in the callback. Defaults to
                :obj:`None`.

                .. versionchanged:: 20.0
                    Renamed the parameter ``context`` to :paramref:`data`.
            name (:obj:`str`, optional): The name of the new job. Defaults to
                :external:attr:`callback.__name__ <definition.__name__>`.
            chat_id (:obj:`int`, optional): Chat id of the chat associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.chat_data` will
                be available in the callback.

                .. versionadded:: 20.0

            user_id (:obj:`int`, optional): User id of the user associated with this job. If
                passed, the corresponding :attr:`~telegram.ext.CallbackContext.user_data` will
                be available in the callback.

                .. versionadded:: 20.0

        Returns:
            :class:`telegram.ext.Job`: The new :class:`Job` instance that has been added to the job
            queue.

        """
        name = name or callback.__name__
        job = Job(callback=callback, data=data, name=name, chat_id=chat_id, user_id=user_id)

        j = self.scheduler.add_job(job.run, args=(self.application,), name=name, **job_kwargs)

        job._job = j  # pylint: disable=protected-access
        return job

    async def start(self) -> None:
        # this method async just in case future versions need that
        """Starts the :class:`~telegram.ext.JobQueue`."""
        if not self.scheduler.running:
            self.scheduler.start()

    async def stop(self, wait: bool = True) -> None:
        """Shuts down the :class:`~telegram.ext.JobQueue`.

        Args:
            wait (:obj:`bool`, optional): Whether to wait until all currently running jobs
                have finished. Defaults to :obj:`True`.

        """
        # the interface methods of AsyncIOExecutor are currently not really asyncio-compatible
        # so we apply some small tweaks here to try and smoothen the integration into PTB
        # TODO: When APS 4.0 hits, we should be able to remove the tweaks
        if wait:
            # Unfortunately AsyncIOExecutor just cancels them all ...
            await asyncio.gather(
                *self._executor._pending_futures,  # pylint: disable=protected-access
                return_exceptions=True,
            )
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            # scheduler.shutdown schedules a task in the event loop but immediately returns
            # so give it a tiny bit of time to actually shut down.
            await asyncio.sleep(0.01)

    def jobs(self) -> Tuple["Job", ...]:
        """Returns a tuple of all *scheduled* jobs that are currently in the :class:`JobQueue`.

        Returns:
            Tuple[:class:`Job`]: Tuple of all *scheduled* jobs.
        """
        return tuple(
            Job._from_aps_job(job)  # pylint: disable=protected-access
            for job in self.scheduler.get_jobs()
        )

    def get_jobs_by_name(self, name: str) -> Tuple["Job", ...]:
        """Returns a tuple of all *pending/scheduled* jobs with the given name that are currently
        in the :class:`JobQueue`.

        Returns:
            Tuple[:class:`Job`]: Tuple of all *pending* or *scheduled* jobs matching the name.
        """
        return tuple(job for job in self.jobs() if job.name == name)


class Job:
    """This class is a convenience wrapper for the jobs held in a :class:`telegram.ext.JobQueue`.
    With the current backend APScheduler, :attr:`job` holds a :class:`apscheduler.job.Job`
    instance.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :class:`id <apscheduler.job.Job>` is equal.

    Note:
        All attributes and instance methods of :attr:`job` are also directly available as
        attributes/methods of the corresponding :class:`telegram.ext.Job` object.

    Warning:
        This class should not be instantiated manually.
        Use the methods of :class:`telegram.ext.JobQueue` to schedule jobs.

    .. versionchanged:: 20.0

       * Removed argument and attribute ``job_queue``.
       * Renamed ``Job.context`` to :attr:`Job.data`.
       * Removed argument ``job``

    Args:
        callback (:term:`coroutine function`): The callback function that should be executed by the
            new job. Callback signature::

                async def callback(context: CallbackContext)

        data (:obj:`object`, optional): Additional data needed for the callback function. Can be
            accessed through :attr:`Job.data` in the callback. Defaults to :obj:`None`.
        name (:obj:`str`, optional): The name of the new job. Defaults to
            :external:obj:`callback.__name__ <definition.__name__>`.
        chat_id (:obj:`int`, optional): Chat id of the chat that this job is associated with.

            .. versionadded:: 20.0
        user_id (:obj:`int`, optional): User id of the user that this job is associated with.

            .. versionadded:: 20.0

    Attributes:
        callback (:term:`coroutine function`): The callback function that should be executed by the
            new job.
        data (:obj:`object`): Optional. Additional data needed for the callback function.
        name (:obj:`str`): Optional. The name of the new job.
        chat_id (:obj:`int`): Optional. Chat id of the chat that this job is associated with.

            .. versionadded:: 20.0
        user_id (:obj:`int`): Optional. User id of the user that this job is associated with.

            .. versionadded:: 20.0
    """

    __slots__ = (
        "callback",
        "data",
        "name",
        "_removed",
        "_enabled",
        "_job",
        "chat_id",
        "user_id",
    )

    def __init__(
        self,
        callback: JobCallback,
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
    ):

        self.callback = callback
        self.data = data
        self.name = name or callback.__name__
        self.chat_id = chat_id
        self.user_id = user_id

        self._removed = False
        self._enabled = False

        self._job = cast(APSJob, None)  # skipcq: PTC-W0052

    @property
    def job(self) -> APSJob:
        """:class:`apscheduler.job.Job`: The APS Job this job is a wrapper for.

        .. versionchanged:: 20.0
            This property is now read-only.
        """
        return self._job

    async def run(self, application: "Application") -> None:
        """Executes the callback function independently of the jobs schedule. Also calls
        :meth:`telegram.ext.Application.update_persistence`.

        .. versionchanged:: 20.0
            Calls :meth:`telegram.ext.Application.update_persistence`.

        Args:
            application (:class:`telegram.ext.Application`): The application this job is associated
                with.
        """
        # We shield the task such that the job isn't cancelled mid-run
        await asyncio.shield(self._run(application))

    async def _run(self, application: "Application") -> None:
        try:
            context = application.context_types.context.from_job(self, application)
            await context.refresh_data()
            await self.callback(context)
        except Exception as exc:
            await application.create_task(application.process_error(None, exc, job=self))
        finally:
            # This is internal logic of application - let's keep it private for now
            application._mark_for_persistence_update(job=self)  # pylint: disable=protected-access

    def schedule_removal(self) -> None:
        """
        Schedules this job for removal from the :class:`JobQueue`. It will be removed without
        executing its callback function again.
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
        :class:`datetime.datetime`: Datetime for the next job execution.
        Datetime is localized according to :attr:`datetime.datetime.tzinfo`.
        If job is removed or already ran it equals to :obj:`None`.

        Warning:
            This attribute is only available, if the :class:`telegram.ext.JobQueue` this job
            belongs to is already started. Otherwise APScheduler raises an :exc:`AttributeError`.
        """
        return self.job.next_run_time

    @classmethod
    def _from_aps_job(cls, job: APSJob) -> "Job":
        return job.func.__self__

    def __getattr__(self, item: str) -> object:
        try:
            return getattr(self.job, item)
        except AttributeError as exc:
            raise AttributeError(
                f"Neither 'telegram.ext.Job' nor 'apscheduler.job.Job' has attribute '{item}'"
            ) from exc

    def __lt__(self, other: object) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
