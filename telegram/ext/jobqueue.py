#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
from threading import Thread, Lock, Event
from queue import PriorityQueue, Empty


class JobQueue(object):
    """This class allows you to periodically perform tasks with the bot.

    Attributes:
        queue (PriorityQueue):
        bot (Bot):

    Args:
        bot (Bot): The bot instance that should be passed to the jobs

    Deprecated: 5.2
        prevent_autostart (Optional[bool]): Thread does not start during initialisation.
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
        """:type: Thread"""
        self._next_peek = None
        """:type: float"""
        self._running = False

    def put(self, job, next_t=None):
        """Queue a new job.

        Args:
            job (Job): The ``Job`` instance representing the new job
            next_t (Optional[float]): Time in seconds in which the job should be executed first.
                Defaults to ``job.interval``

        """
        job.job_queue = self

        if next_t is None:
            next_t = job.interval

        now = time.time()
        next_t += now

        self.logger.debug('Putting job %s with t=%f', job.name, next_t)
        self.queue.put((next_t, job))

        # Wake up the loop if this job should be executed next
        self._set_next_peek(next_t)

    def _set_next_peek(self, t):
        """
        Set next peek if not defined or `t` is before next peek.
        In case the next peek was set, also trigger the `self.__tick` event.

        """
        with self.__next_peek_lock:
            if not self._next_peek or self._next_peek > t:
                self._next_peek = t
                self.__tick.set()

    def tick(self):
        """
        Run all jobs that are due and re-enqueue them with their interval.

        """
        now = time.time()

        self.logger.debug('Ticking jobs with t=%f', now)

        while True:
            try:
                t, job = self.queue.get(False)
            except Empty:
                break

            self.logger.debug('Peeked at %s with t=%f', job.name, t)

            if t > now:
                # we can get here in two conditions:
                # 1. At the second or later pass of the while loop, after we've already processed
                #    the job(s) we were supposed to at this time.
                # 2. At the first iteration of the loop only if `self.put()` had triggered
                #    `self.__tick` because `self._next_peek` wasn't set
                self.logger.debug("Next task isn't due yet. Finished!")
                self.queue.put((t, job))
                self._set_next_peek(t)
                break

            if job._remove.is_set():
                self.logger.debug('Removing job %s', job.name)
                continue

            if job.enabled:
                self.logger.debug('Running job %s', job.name)

                try:
                    job.run(self.bot)

                except:
                    self.logger.exception('An uncaught error was raised while executing job %s',
                                          job.name)

            else:
                self.logger.debug('Skipping disabled job %s', job.name)

            if job.repeat:
                self.put(job)

    def start(self):
        """
        Starts the job_queue thread.

        """
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
                tmout = self._next_peek and self._next_peek - time.time()
                self._next_peek = None
                self.__tick.clear()

            self.__tick.wait(tmout)

            # If we were woken up by self.stop(), just bail out
            if not self._running:
                break

            self.tick()

        self.logger.debug('%s thread stopped', self.__class__.__name__)

    def stop(self):
        """
        Stops the thread
        """
        with self.__start_lock:
            self._running = False

        self.__tick.set()
        if self.__thread is not None:
            self.__thread.join()

    def jobs(self):
        """Returns a tuple of all jobs that are currently in the ``JobQueue``"""
        return tuple(job[1] for job in self.queue.queue if job)


class Job(object):
    """This class encapsulates a Job

    Attributes:
        callback (function):
        interval (float):
        repeat (bool):
        name (str):
        enabled (bool): Boolean property that decides if this job is currently active

    Args:
        callback (function): The callback function that should be executed by the Job. It should
            take two parameters ``bot`` and ``job``, where ``job`` is the ``Job`` instance. It
            can be used to terminate the job or modify its interval.
        interval (float): The interval in which this job should execute its callback function in
            seconds.
        repeat (Optional[bool]): If this job should be periodically execute its callback function
            (``True``) or only once (``False``). Defaults to ``True``
        context (Optional[object]): Additional data needed for the callback function. Can be
            accessed through ``job.context`` in the callback. Defaults to ``None``

    """
    job_queue = None

    def __init__(self, callback, interval, repeat=True, context=None):
        self.callback = callback
        self.interval = interval
        self.repeat = repeat
        self.context = context

        self.name = callback.__name__
        self._remove = Event()
        self._enabled = Event()
        self._enabled.set()

    def run(self, bot):
        """Executes the callback function"""
        self.callback(bot, self)

    def schedule_removal(self):
        """
        Schedules this job for removal from the ``JobQueue``. It will be removed without executing
        its callback function again.

        """
        self._remove.set()

    def is_enabled(self):
        return self._enabled.is_set()

    def set_enabled(self, status):
        if status:
            self._enabled.set()
        else:
            self._enabled.clear()

    enabled = property(is_enabled, set_enabled)

    def __lt__(self, other):
        return False
