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
from threading import Thread, Lock, Event
from queue import PriorityQueue


class JobQueue(object):
    """This class allows you to periodically perform tasks with the bot.

    Attributes:
        queue (PriorityQueue):
        bot (Bot):

    Args:
        bot (Bot): The bot instance that should be passed to the jobs

    """

    def __init__(self, bot):
        self.queue = PriorityQueue()
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__lock = Lock()
        self.__tick = Event()
        self._next_peek = None
        self._running = False

    def put(self, job, next_t=None, prevent_autostart=False):
        """Queue a new job. If the JobQueue is not running, it will be started.

        Args:
            job (Job): The ``Job`` instance representing the new job
            next_t (Optional[float]): Time in seconds in which the job should be executed first.
                Defaults to ``job.interval``
            prevent_autostart (Optional[bool]): If ``True``, the job queue will not be started
                automatically if it is not running. Defaults to ``False``

        """
        job.job_queue = self

        if next_t is None:
            next_t = job.interval

        now = time.time()
        next_t += now

        self.logger.debug('Putting job %s with t=%f', job.name, next_t)
        self.queue.put((next_t, job))

        # Wake up the loop if this job should be executed next
        if not self._next_peek or self._next_peek > next_t:
            self._next_peek = next_t
            self.__tick.set()

        if not self._running and not prevent_autostart:
            self.logger.debug('Auto-starting JobQueue')
            self.start()

    def tick(self):
        """
        Run all jobs that are due and re-enqueue them with their interval.

        """
        now = time.time()

        self.logger.debug('Ticking jobs with t=%f', now)

        while not self.queue.empty():
            t, job = self.queue.queue[0]
            self.logger.debug('Peeked at %s with t=%f', job.name, t)

            if t <= now:
                self.queue.get()

                if job._remove.is_set():
                    self.logger.debug('Removing job %s', job.name)
                    continue

                elif job.enabled:
                    self.logger.debug('Running job %s', job.name)

                    try:
                        job.run(self.bot)

                    except:
                        self.logger.exception(
                            'An uncaught error was raised while executing job %s', job.name)

                else:
                    self.logger.debug('Skipping disabled job %s', job.name)

                if job.repeat:
                    self.put(job)

                continue

            self.logger.debug('Next task isn\'t due yet. Finished!')
            self._next_peek = t
            break

        else:
            self._next_peek = None

        self.__tick.clear()

    def start(self):
        """
        Starts the job_queue thread.

        """
        self.__lock.acquire()

        if not self._running:
            self._running = True
            self.__lock.release()
            job_queue_thread = Thread(target=self._start, name="job_queue")
            job_queue_thread.start()
            self.logger.debug('%s thread started', self.__class__.__name__)

        else:
            self.__lock.release()

    def _start(self):
        """
        Thread target of thread ``job_queue``. Runs in background and performs ticks on the job
        queue.

        """
        while self._running:
            self.__tick.wait(self._next_peek and self._next_peek - time.time())

            # If we were woken up by set(), wait with the new timeout
            if self.__tick.is_set():
                self.__tick.clear()
                continue

            self.tick()

        self.logger.debug('%s thread stopped', self.__class__.__name__)

    def stop(self):
        """
        Stops the thread
        """
        with self.__lock:
            self._running = False

        self.__tick.set()

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
