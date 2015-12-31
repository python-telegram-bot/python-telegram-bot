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
from threading import Lock

try:
    from queue import Queue, PriorityQueue
except ImportError:
    from Queue import Queue, PriorityQueue


class JobQueue(object):
    """This class allows you to periodically perform tasks with the bot.

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

    def put(self, run, interval, next_t=None):
        """
        Queue a new job.

        Args:
            run (function): A function that takes the parameter `bot`
            interval (float): The interval in seconds in which `run` should be
                executed
            next_t (Optional[float]): Time in seconds in which run should be
                executed first. Defaults to `interval`
        """
        name = run.__name__

        job = JobQueue.Job()
        job.run = run
        job.interval = interval
        job.name = name

        if next_t is None:
            next_t = interval

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
                self.logger.debug("About time! running")
                j.run()
                self.put(j, now + j.interval)
                continue

            self.logger.debug("Next task isn't due yet. Finished!")
            break

    def start(self):
        """
        Thread target of thread 'job_queue'. Runs in background and performs
        ticks on the job queue.
        """
        self.__lock.acquire()
        if not self.running:
            self.running = True
            self.__lock.release()
            while self.running:
                self.tick()
                time.sleep(self.tick_interval)
        else:
            self.__lock.release()

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

        def run(self):
            pass

        def __lt__(self, other):
            return False
