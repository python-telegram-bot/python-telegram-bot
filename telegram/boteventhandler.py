#!/usr/bin/env python

"""
This module contains the class BotEventHandler, which tries to make creating 
Telegram Bots intuitive!
"""

import sys
from threading import Thread
from telegram import (Bot, TelegramError, TelegramObject, Broadcaster)
from time import sleep
from functools import wraps

# Adjust for differences in Python versions
if sys.version_info.major is 2:
    from Queue import Queue
elif sys.version_info.major is 3:
    from queue import Queue


def run_async(func):
    """
    Function decorator that will run the function in a new thread.

    Args:
        func (function): The function to run in the thread.

    Returns:
        function:
    """

    @wraps(func)
    def async_func(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return async_func


class BotEventHandler(TelegramObject):
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
    """
    
    def __init__(self, token, base_url=None):
        self.bot = Bot(token, base_url)
        self.update_queue = Queue()
        self.last_update_id = 0
        self.broadcaster = Broadcaster(self.bot, self.update_queue)

    def start(self, poll_interval=1.0):
        """
        Starts polling updates from Telegram. 
        
        Args:
            poll_interval (Optional[float]): Time to wait between polling 
                updates from Telegram in seconds. Default is 1.0

        Returns:
            Queue: The update queue that can be filled from the main thread
        """

        # Create Thread objects
        broadcaster_thread = Thread(target=self.broadcaster.start,
                                    name="broadcaster")
        event_handler_thread = Thread(target=self.__start, name="eventhandler",
                                      args=(poll_interval,))

        # Set threads as daemons so they'll stop if the main thread stops
        broadcaster_thread.daemon = True
        event_handler_thread.daemon = True
        
        # Start threads
        broadcaster_thread.start()
        event_handler_thread.start()
        
        # Return the update queue so the main thread can insert updates
        return self.update_queue

    def __start(self, poll_interval):
        """
        Thread target of thread 'eventhandler'. Runs in background, pulls
        updates from Telegram and inserts them in the update queue of the
        Broadcaster.
        """

        current_interval = poll_interval

        while True:
            try:
                updates = self.bot.getUpdates(self.last_update_id)
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
