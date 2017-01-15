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
"""This module contains the class Updater, which tries to make creating
Telegram bots intuitive."""

import logging
import os
import ssl
import warnings
from threading import Thread, Lock, current_thread, Event
from time import sleep
import subprocess
from signal import signal, SIGINT, SIGTERM, SIGABRT
from queue import Queue

from telegram import Bot, TelegramError
from telegram.ext import Dispatcher, JobQueue
from telegram.error import Unauthorized, InvalidToken, RetryAfter
from telegram.utils.request import Request
from telegram.utils.webhookhandler import (WebhookServer, WebhookHandler)

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Updater(object):
    """
    This class, which employs the Dispatcher class, provides a frontend to
    telegram.Bot to the programmer, so they can focus on coding the bot. Its
    purpose is to receive the updates from Telegram and to deliver them to said
    dispatcher. It also runs in a separate thread, so the user can interact
    with the bot, for example on the command line. The dispatcher supports
    handlers for different kinds of data: Updates from Telegram, basic text
    commands and even arbitrary types.
    The updater can be started as a polling service or, for production, use a
    webhook to receive updates. This is achieved using the WebhookServer and
    WebhookHandler classes.


    Attributes:

    Args:
        token (Optional[str]): The bot's token given by the @BotFather
        base_url (Optional[str]):
        workers (Optional[int]): Amount of threads in the thread pool for
            functions decorated with @run_async
        bot (Optional[Bot]): A pre-initialized bot instance. If a pre-initizlied bot is used, it is
            the user's responsibility to create it using a `Request` instance with a large enough
            connection pool.
        request_kwargs (Optional[dict]): Keyword args to control the creation of a request object
            (ignored if `bot` argument is used).

    Raises:
        ValueError: If both `token` and `bot` are passed or none of them.

    """
    _request = None

    def __init__(self, token=None, base_url=None, workers=4, bot=None, request_kwargs=None):
        if (token is None) and (bot is None):
            raise ValueError('`token` or `bot` must be passed')
        if (token is not None) and (bot is not None):
            raise ValueError('`token` and `bot` are mutually exclusive')

        if bot is not None:
            self.bot = bot
        else:
            # we need a connection pool the size of:
            # * for each of the workers
            # * 1 for Dispatcher
            # * 1 for polling Updater (even if webhook is used, we can spare a connection)
            # * 1 for JobQueue
            # * 1 for main thread
            if request_kwargs is None:
                request_kwargs = {}
            if 'con_pool_size' not in request_kwargs:
                request_kwargs['con_pool_size'] = workers + 4
            self._request = Request(**request_kwargs)
            self.bot = Bot(token, base_url, request=self._request)
        self.update_queue = Queue()
        self.job_queue = JobQueue(self.bot)
        self.__exception_event = Event()
        self.dispatcher = Dispatcher(
            self.bot,
            self.update_queue,
            job_queue=self.job_queue,
            workers=workers,
            exception_event=self.__exception_event)
        self.last_update_id = 0
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.is_idle = False
        self.httpd = None
        self.__lock = Lock()
        self.__threads = []
        """:type: list[Thread]"""

    def _init_thread(self, target, name, *args, **kwargs):
        thr = Thread(target=self._thread_wrapper, name=name, args=(target,) + args, kwargs=kwargs)
        thr.start()
        self.__threads.append(thr)

    def _thread_wrapper(self, target, *args, **kwargs):
        thr_name = current_thread().name
        self.logger.debug('{0} - started'.format(thr_name))
        try:
            target(*args, **kwargs)
        except Exception:
            self.__exception_event.set()
            self.logger.exception('unhandled exception')
            raise
        self.logger.debug('{0} - ended'.format(thr_name))

    def start_polling(self,
                      poll_interval=0.0,
                      timeout=10,
                      network_delay=None,
                      clean=False,
                      bootstrap_retries=0,
                      read_latency=2.,
                      allowed_updates=None):
        """
        Starts polling updates from Telegram.

        Args:
            poll_interval (Optional[float]): Time to wait between polling updates from Telegram in
            seconds. Default is 0.0

            timeout (Optional[float]): Passed to Bot.getUpdates

            network_delay: Deprecated. Will be honoured as `read_latency` for a while but will be
                removed in the future.

            clean (Optional[bool]): Whether to clean any pending updates on Telegram servers before
              actually starting to poll. Default is False.

            bootstrap_retries (Optional[int]): Whether the bootstrapping phase of the `Updater`
              will retry on failures on the Telegram server.

                |   < 0 - retry indefinitely
                |     0 - no retries (default)
                |   > 0 - retry up to X times

            allowed_updates (Optional[list[str]]): Passed to Bot.getUpdates

            read_latency (Optional[float|int]): Grace time in seconds for receiving the reply from
                server. Will be added to the `timeout` value and used as the read timeout from
                server (Default: 2).


        Returns:
            Queue: The update queue that can be filled from the main thread

        """
        if network_delay is not None:
            warnings.warn('network_delay is deprecated, use read_latency instead')
            read_latency = network_delay

        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                self.job_queue.start()
                self._init_thread(self.dispatcher.start, "dispatcher")
                self._init_thread(self._start_polling, "updater", poll_interval, timeout,
                                  read_latency, bootstrap_retries, clean, allowed_updates)

                # Return the update queue so the main thread can insert updates
                return self.update_queue

    def start_webhook(self,
                      listen='127.0.0.1',
                      port=80,
                      url_path='',
                      cert=None,
                      key=None,
                      clean=False,
                      bootstrap_retries=0,
                      webhook_url=None):
        """
        Starts a small http server to listen for updates via webhook. If cert
        and key are not provided, the webhook will be started directly on
        http://listen:port/url_path, so SSL can be handled by another
        application. Else, the webhook will be started on
        https://listen:port/url_path

        Args:
            listen (Optional[str]): IP-Address to listen on
            port (Optional[int]): Port the bot should be listening on
            url_path (Optional[str]): Path inside url
            cert (Optional[str]): Path to the SSL certificate file
            key (Optional[str]): Path to the SSL key file
            clean (Optional[bool]): Whether to clean any pending updates on
                Telegram servers before actually starting the webhook. Default
                is False.
            bootstrap_retries (Optional[int[): Whether the bootstrapping phase
                of the `Updater` will retry on failures on the Telegram server.

                |   < 0 - retry indefinitely
                |   0 - no retries (default)
                |   > 0 - retry up to X times
            webhook_url (Optional[str]): Explicitly specifiy the webhook url.
                Useful behind NAT, reverse proxy, etc. Default is derived from
                `listen`, `port` & `url_path`.

        Returns:
            Queue: The update queue that can be filled from the main thread

        """
        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                self.job_queue.start()
                self._init_thread(self.dispatcher.start, "dispatcher"),
                self._init_thread(self._start_webhook, "updater", listen, port, url_path, cert,
                                  key, bootstrap_retries, clean, webhook_url)

                # Return the update queue so the main thread can insert updates
                return self.update_queue

    def _start_polling(self, poll_interval, timeout, read_latency, bootstrap_retries, clean,
                       allowed_updates):
        """
        Thread target of thread 'updater'. Runs in background, pulls
        updates from Telegram and inserts them in the update queue of the
        Dispatcher.

        """
        cur_interval = poll_interval
        self.logger.debug('Updater thread started')

        self._bootstrap(bootstrap_retries, clean=clean, webhook_url='')

        while self.running:
            try:
                updates = self.bot.getUpdates(
                    self.last_update_id,
                    timeout=timeout,
                    read_latency=read_latency,
                    allowed_updates=allowed_updates)
            except RetryAfter as e:
                self.logger.info(str(e))
                cur_interval = 0.5 + e.retry_after
            except TelegramError as te:
                self.logger.error("Error while getting Updates: {0}".format(te))

                # Put the error into the update queue and let the Dispatcher
                # broadcast it
                self.update_queue.put(te)

                cur_interval = self._increase_poll_interval(cur_interval)
            else:
                if not self.running:
                    if len(updates) > 0:
                        self.logger.debug('Updates ignored and will be pulled '
                                          'again on restart.')
                    break

                if updates:
                    for update in updates:
                        self.update_queue.put(update)
                    self.last_update_id = updates[-1].update_id + 1

                cur_interval = poll_interval

            sleep(cur_interval)

    @staticmethod
    def _increase_poll_interval(current_interval):
        # increase waiting times on subsequent errors up to 30secs
        if current_interval == 0:
            current_interval = 1
        elif current_interval < 30:
            current_interval += current_interval / 2
        elif current_interval > 30:
            current_interval = 30
        return current_interval

    def _start_webhook(self, listen, port, url_path, cert, key, bootstrap_retries, clean,
                       webhook_url):
        self.logger.debug('Updater thread started')
        use_ssl = cert is not None and key is not None
        if not url_path.startswith('/'):
            url_path = '/{0}'.format(url_path)

        # Create and start server
        self.httpd = WebhookServer((listen, port), WebhookHandler, self.update_queue, url_path,
                                   self.bot)

        if use_ssl:
            self._check_ssl_cert(cert, key)

            # DO NOT CHANGE: Only set webhook if SSL is handled by library
            if not webhook_url:
                webhook_url = self._gen_webhook_url(listen, port, url_path)

            self._bootstrap(
                max_retries=bootstrap_retries,
                clean=clean,
                webhook_url=webhook_url,
                cert=open(cert, 'rb'))
        elif clean:
            self.logger.warning("cleaning updates is not supported if "
                                "SSL-termination happens elsewhere; skipping")

        self.httpd.serve_forever(poll_interval=1)

    def _check_ssl_cert(self, cert, key):
        # Check SSL-Certificate with openssl, if possible
        try:
            exit_code = subprocess.call(
                ["openssl", "x509", "-text", "-noout", "-in", cert],
                stdout=open(os.devnull, 'wb'),
                stderr=subprocess.STDOUT)
        except OSError:
            exit_code = 0
        if exit_code is 0:
            try:
                self.httpd.socket = ssl.wrap_socket(
                    self.httpd.socket, certfile=cert, keyfile=key, server_side=True)
            except ssl.SSLError as error:
                self.logger.exception('Failed to init SSL socket')
                raise TelegramError(str(error))
        else:
            raise TelegramError('SSL Certificate invalid')

    @staticmethod
    def _gen_webhook_url(listen, port, url_path):
        return 'https://{listen}:{port}{path}'.format(listen=listen, port=port, path=url_path)

    def _bootstrap(self, max_retries, clean, webhook_url, cert=None):
        retries = 0
        while 1:

            try:
                if clean:
                    # Disable webhook for cleaning
                    self.bot.deleteWebhook()
                    self._clean_updates()
                    sleep(1)

                self.bot.setWebhook(url=webhook_url, certificate=cert)
            except (Unauthorized, InvalidToken):
                raise
            except TelegramError:
                msg = 'error in bootstrap phase; try={0} max_retries={1}'.format(retries,
                                                                                 max_retries)
                if max_retries < 0 or retries < max_retries:
                    self.logger.warning(msg)
                    retries += 1
                else:
                    self.logger.exception(msg)
                    raise
            else:
                break
            sleep(1)

    def _clean_updates(self):
        self.logger.debug('Cleaning updates from Telegram server')
        updates = self.bot.getUpdates()
        while updates:
            updates = self.bot.getUpdates(updates[-1].update_id + 1)

    def stop(self):
        """
        Stops the polling/webhook thread, the dispatcher and the job queue
        """

        self.job_queue.stop()
        with self.__lock:
            if self.running or self.dispatcher.has_running_threads:
                self.logger.debug('Stopping Updater and Dispatcher...')

                self.running = False

                self._stop_httpd()
                self._stop_dispatcher()
                self._join_threads()

                # Stop the Request instance only if it was created by the Updater
                if self._request:
                    self._request.stop()

    def _stop_httpd(self):
        if self.httpd:
            self.logger.debug('Waiting for current webhook connection to be '
                              'closed... Send a Telegram message to the bot to exit '
                              'immediately.')
            self.httpd.shutdown()
            self.httpd = None

    def _stop_dispatcher(self):
        self.logger.debug('Requesting Dispatcher to stop...')
        self.dispatcher.stop()

    def _join_threads(self):
        for thr in self.__threads:
            self.logger.debug('Waiting for {0} thread to end'.format(thr.name))
            thr.join()
            self.logger.debug('{0} thread has ended'.format(thr.name))
        self.__threads = []

    def signal_handler(self, signum, frame):
        self.is_idle = False
        if self.running:
            self.stop()
        else:
            self.logger.warning('Exiting immediately!')
            import os
            os._exit(1)

    def idle(self, stop_signals=(SIGINT, SIGTERM, SIGABRT)):
        """
        Blocks until one of the signals are received and stops the updater

        Args:
            stop_signals: Iterable containing signals from the signal module
                that should be subscribed to. Updater.stop() will be called on
                receiving one of those signals. Defaults to (SIGINT, SIGTERM,
                SIGABRT)
        """
        for sig in stop_signals:
            signal(sig, self.signal_handler)

        self.is_idle = True

        while self.is_idle:
            sleep(1)
