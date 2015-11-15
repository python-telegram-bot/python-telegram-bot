#!/usr/bin/env python

"""
This module contains the class BotEventHandler, which tries to make creating 
Telegram Bots intuitive!
"""
import logging
import sys
from threading import Thread
from telegram import (Bot, TelegramError, broadcaster, Broadcaster,
                      NullHandler)
from time import sleep

# Adjust for differences in Python versions
if sys.version_info.major is 2:
    from Queue import Queue
elif sys.version_info.major is 3:
    from queue import Queue

H = NullHandler()
logging.getLogger(__name__).addHandler(H)


class BotEventHandler:
    """
    This class provides a frontend to telegram.Bot to the programmer, so they
    can focus on coding the bot. I also runs in a separate thread, so the user
    can interact with the bot, for example on the command line. It supports
    Handlers for different kinds of data: Updates from Telegram, basic text
    commands and even arbitrary types.
    
    Attributes:
    
    Args:
        token (str): The bots token given by the @BotFather
        base_url (Optional[str]):
        broadcaster (Optional[Broadcaster]): Use present Broadcaster object. If
            None, a new one will be created.
        workers (Optional[int]): Amount of threads in the thread pool for
            functions decorated with @run_async
    """
    
    def __init__(self, token, base_url=None, broadcaster=None, workers=4):
        self.bot = Bot(token, base_url)
        self.last_update_id = 0

        if broadcaster:
            self.update_queue = broadcaster.update_queue
            self.broadcaster = broadcaster
        else:
            self.update_queue = Queue()
            self.broadcaster = Broadcaster(self.bot, self.update_queue,
                                           workers=workers)
        self.logger = logging.getLogger(__name__)
        self.running = False

    def start(self, poll_interval=1.0, timeout=10, network_delay=2):
        """
        Starts polling updates from Telegram. 
        
        Args:
            poll_interval (Optional[float]): Time to wait between polling 
                updates from Telegram in seconds. Default is 1.0
            timeout (Optional[float]): Passed to Bot.getUpdates
            network_delay (Optional[float]): Passed to Bot.getUpdates

        Returns:
            Queue: The update queue that can be filled from the main thread
        """

        # Create Thread objects
        broadcaster_thread = Thread(target=self.broadcaster.start,
                                    name="broadcaster")
        event_handler_thread = Thread(target=self.__start, name="eventhandler",
                                      args=(poll_interval, timeout,
                                            network_delay))

        self.running = True
        
        # Start threads
        broadcaster_thread.start()
        event_handler_thread.start()
        
        # Return the update queue so the main thread can insert updates
        return self.update_queue

    def __start(self, poll_interval, timeout, network_delay):
        """
        Thread target of thread 'eventhandler'. Runs in background, pulls
        updates from Telegram and inserts them in the update queue of the
        Broadcaster.
        """

        current_interval = poll_interval
        self.logger.info('Event Handler thread started')

        while self.running:
            try:
                updates = self.bot.getUpdates(self.last_update_id,
                                              timeout=timeout,
                                              network_delay=network_delay)
                if not self.running:
                    if len(updates) > 0:
                        self.logger.info('Updates ignored and will be pulled ' +
                                         'again on restart.')
                    break

                for update in updates:
                    self.update_queue.put(update)
                    self.last_update_id = update.update_id + 1
                    current_interval = poll_interval
                
                sleep(current_interval)
            except TelegramError as te:
                # Put the error into the update queue and let the Broadcaster
                # broadcast it
                self.update_queue.put(te)
                sleep(current_interval)

                # increase waiting times on subsequent errors up to 30secs
                if current_interval < 30:
                    current_interval += current_interval / 2
                if current_interval > 30:
                    current_interval = 30

        self.logger.info('Event Handler thread stopped')

    def stop(self):
        """
        Stops the polling thread and the broadcaster
        """
        self.logger.info('Stopping Event Handler and Broadcaster...')
        self.running = False
        self.broadcaster.stop()
        while broadcaster.running_async > 0:
            sleep(1)

