#!/usr/bin/env python

"""
This module contains the class BotEventHandler, which tries to make creating

Telegram Bots intuitive!
"""
import logging
import ssl
from threading import Thread
from time import sleep

import subprocess

from telegram import (Bot, TelegramError, dispatcher, Dispatcher,
                      NullHandler)
from telegram.utils.webhookhandler import (WebhookServer, WebhookHandler)

# Adjust for differences in Python versions
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

H = NullHandler()
logging.getLogger(__name__).addHandler(H)


class BotEventHandler:
    """
    This class provides a frontend to telegram.Bot to the programmer, so they
    can focus on coding the bot. It also runs in a separate thread, so the user
    can interact with the bot, for example on the command line. It supports
    Handlers for different kinds of data: Updates from Telegram, basic text
    commands and even arbitrary types.
    Polling as well as webhook are supported.


    Attributes:

    Args:
        token (str): The bots token given by the @BotFather
        base_url (Optional[str]):
        workers (Optional[int]): Amount of threads in the thread pool for
            functions decorated with @run_async
    """

    def __init__(self, token, base_url=None, workers=4):

        self.bot = Bot(token, base_url)
        self.update_queue = Queue()
        self.dispatcher = Dispatcher(self.bot, self.update_queue,
                                     workers=workers)
        self.last_update_id = 0
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.httpd = None

    def start_polling(self, poll_interval=1.0, timeout=10, network_delay=2):
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
        dispatcher_thread = Thread(target=self.dispatcher.start,
                                   name="dispatcher")
        event_handler_thread = Thread(target=self._start_polling,
                                      name="eventhandler",
                                      args=(poll_interval, timeout,
                                            network_delay))

        self.running = True

        # Start threads
        dispatcher_thread.start()
        event_handler_thread.start()

        # Return the update queue so the main thread can insert updates
        return self.update_queue

    def start_webhook(self, host, port, cert, key, listen='0.0.0.0'):
        """
        Starts a small http server to listen for updates via webhook

        Args:
            host (str): Hostname or IP of the bot
            port (int): Port the bot should be listening on
            cert (str): Path to the SSL certificate file
            key (str): Path to the SSL key file
            listen (Optional[str]): IP-Address to listen on

        Returns:
            Queue: The update queue that can be filled from the main thread
        """

        # Create Thread objects
        dispatcher_thread = Thread(target=self.dispatcher.start,
                                   name="dispatcher")
        event_handler_thread = Thread(target=self._start_webhook,
                                      name="eventhandler",
                                      args=(host, port, cert, key, listen))

        self.running = True

        # Start threads
        dispatcher_thread.start()
        event_handler_thread.start()

        # Return the update queue so the main thread can insert updates
        return self.update_queue

    def _start_polling(self, poll_interval, timeout, network_delay):
        """
        Thread target of thread 'eventhandler'. Runs in background, pulls
        updates from Telegram and inserts them in the update queue of the
        Dispatcher.
        """

        current_interval = poll_interval
        self.logger.info('Event Handler thread started')

        # Remove webhook
        self.bot.setWebhook(webhook_url=None)

        while self.running:
            try:
                updates = self.bot.getUpdates(self.last_update_id,
                                              timeout=timeout,
                                              network_delay=network_delay)
                if not self.running:
                    if len(updates) > 0:
                        self.logger.info('Updates ignored and will be pulled '
                                         'again on restart.')
                    break

                for update in updates:
                    self.update_queue.put(update)
                    self.last_update_id = update.update_id + 1
                    current_interval = poll_interval

                sleep(current_interval)
            except TelegramError as te:
                # Put the error into the update queue and let the Dispatcher
                # broadcast it
                self.update_queue.put(te)
                sleep(current_interval)

                # increase waiting times on subsequent errors up to 30secs
                if current_interval < 30:
                    current_interval += current_interval / 2
                if current_interval > 30:
                    current_interval = 30

        self.logger.info('Event Handler thread stopped')

    def _start_webhook(self, host, port, cert, key, listen):
        self.logger.info('Event Handler thread started')
        url_base = "https://%s:%d" % (host, port)
        url_path = "/%s" % self.bot.token

        # Remove webhook
        self.bot.setWebhook(webhook_url=None)

        # Set webhook
        self.bot.setWebhook(webhook_url=url_base + url_path,
                            certificate=open(cert, 'rb'))

        # Start server
        self.httpd = WebhookServer((listen, port), WebhookHandler,
                                   self.update_queue, url_path)

        # Check SSL-Certificate with openssl, if possible
        try:
            exit_code = subprocess.call(["openssl", "x509", "-text", "-noout",
                                         "-in", cert])
        except OSError:
            exit_code = 0

        if exit_code is 0:
            try:
                self.httpd.socket = ssl.wrap_socket(self.httpd.socket,
                                                    certfile=cert,
                                                    keyfile=key,
                                                    server_side=True)
            except ssl.SSLError as error:
                self.logger.error(str(error))
                return

            self.httpd.serve_forever(poll_interval=1)
            self.logger.info('Event Handler thread stopped')

    def stop(self):
        """
        Stops the polling thread and the dispatcher
        """
        self.logger.info('Stopping Event Handler and Dispatcher...')
        self.running = False

        if self.httpd:
            self.logger.info(
                'Waiting for current webhook connection to be closed... '
                'Send a Telegram message to the bot to exit immediately.')
            self.httpd.shutdown()
            self.httpd = None

        self.logger.debug("Requesting Dispatcher to stop...")
        self.dispatcher.stop()
        while dispatcher.running_async > 0:
            sleep(1)

        self.logger.debug("Dispatcher stopped.")
