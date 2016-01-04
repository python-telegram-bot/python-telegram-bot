#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <devs@python-telegram-bot.org>
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

"""
This module contains the class JobQueue
"""

import logging
import time
from threading import Thread, Lock

try:
    from queue import Queue, PriorityQueue
except ImportError:
    from Queue import Queue, PriorityQueue


class JobQueue(object):
    """
    This class allows you to periodically perform tasks with the bot.

    Attributes:
        tick_interval (float):
        queue (PriorityQueue):
        bot (Bot):
        running (bool):

    Args:
        bot (Bot): The bot instance that should be passed to the jobs

    Keyword Args:
        tick_interval (Optional[float]): The interval this queue should check
            the newest task in seconds. Defaults to 1.0
    """

    def __init__(self, bot, tick_interval=1.0):
        self.tick_interval = tick_interval
        self.queue = PriorityQueue()
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.__lock = Lock()
        self.running = False

    def put(self, run, interval, repeat=True, next_t=None):
        """
        Queue a new job.

        Args:
            run (function): A function that takes the parameter `bot`
            interval (float): The interval in seconds in which `run` should be
                executed
            repeat (Optional[bool]): If false, job will only be executed once
            next_t (Optional[float]): Time in seconds in which run should be
                executed first. Defaults to `interval`
        """
        name = run.__name__

        job = JobQueue.Job()
        job.run = run
        job.interval = interval
        job.name = name
        job.repeat = repeat

        if next_t is None:
            next_t = interval

        next_t += time.time()

        self.logger.debug("Putting a {} with t={}".format(
                job.name, next_t))
        self.queue.put((next_t, job))

    def tick(self):
        """
        Run all jobs that are due and re-enqueue them with their interval
        """
        now = time.time()

        self.logger.debug("Ticking jobs with t={}".format(now))
        while not self.queue.empty():
            t, j = self.queue.queue[0]
            self.logger.debug("Peeked at {} with t={}".format(
                    j.name, t))

            if t < now:
                self.queue.get()
                self.logger.info("Running job {}".format(j.name))
                try:
                    j.run(self.bot)
                except:
                    self.logger.exception("An uncaught error was raised while "
                                          "executing job {}".format(j.name))
                if j.repeat:
                    self.put(j.run, j.interval)
                continue

            self.logger.debug("Next task isn't due yet. Finished!")
            break

    def start(self):
        """
        Starts the job_queue thread.
        """
        self.__lock.acquire()
        if not self.running:
            self.running = True
            self.__lock.release()
            job_queue_thread = Thread(target=self._start,
                                      name="job_queue")
            job_queue_thread.start()
            self.logger.info('Job Queue thread started')
        else:
            self.__lock.release()

    def _start(self):
        """
        Thread target of thread 'job_queue'. Runs in background and performs
        ticks on the job queue.
        """
        while self.running:
            self.tick()
            time.sleep(self.tick_interval)

        self.logger.info('Job Queue thread stopped')

    def stop(self):
        """
        Stops the thread
        """
        with self.__lock:
            self.running = False

    class Job(object):
        """ Inner class that represents a job """
        interval = None
        name = None
        repeat = None

        def run(self):
            pass

        def __lt__(self, other):
            return False
