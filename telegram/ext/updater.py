#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
"""This module contains the class Updater, which tries to make creating Telegram bots intuitive."""

import logging
import os
import ssl
from threading import Thread, Lock, current_thread, Event
from time import sleep
import subprocess
from signal import signal, SIGINT, SIGTERM, SIGABRT
from queue import Queue

from telegram import Bot, TelegramError
from telegram.ext import Dispatcher, JobQueue
from telegram.error import Unauthorized, InvalidToken, RetryAfter, TimedOut
from telegram.utils.helpers import get_signal_name
from telegram.utils.request import Request
from telegram.utils.webhookhandler import (WebhookServer, WebhookHandler)

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Updater(object):
    """
    This class, which employs the :class:`telegram.ext.Dispatcher`, provides a frontend to
    :class:`telegram.Bot` to the programmer, so they can focus on coding the bot. Its purpose is to
    receive the updates from Telegram and to deliver them to said dispatcher. It also runs in a
    separate thread, so the user can interact with the bot, for example on the command line. The
    dispatcher supports handlers for different kinds of data: Updates from Telegram, basic text
    commands and even arbitrary types. The updater can be started as a polling service or, for
    production, use a webhook to receive updates. This is achieved using the WebhookServer and
    WebhookHandler classes.


    Attributes:
        bot (:class:`telegram.Bot`): The bot used with this Updater.
        user_sig_handler (:obj:`signal`): signals the updater will respond to.
        update_queue (:obj:`Queue`): Queue for the updates.
        job_queue (:class:`telegram.ext.JobQueue`): Jobqueue for the updater.
        dispatcher (:class:`telegram.ext.Dispatcher`): Dispatcher that handles the updates and
            dispatches them to the handlers.
        running (:obj:`bool`): Indicates if the updater is running.

    Args:
        token (:obj:`str`, optional): The bot's token given by the @BotFather.
        base_url (:obj:`str`, optional): Base_url for the bot.
        workers (:obj:`int`, optional): Amount of threads in the thread pool for functions
            decorated with ``@run_async``.
        bot (:class:`telegram.Bot`, optional): A pre-initialized bot instance. If a pre-initialized
            bot is used, it is the user's responsibility to create it using a `Request`
            instance with a large enough connection pool.
        private_key (:obj:`bytes`, optional): Private key for decryption of telegram passport data.
        private_key_password (:obj:`bytes`, optional): Password for above private key.
        user_sig_handler (:obj:`function`, optional): Takes ``signum, frame`` as positional
            arguments. This will be called when a signal is received, defaults are (SIGINT,
            SIGTERM, SIGABRT) setable with :attr:`idle`.
        request_kwargs (:obj:`dict`, optional): Keyword args to control the creation of a
            `telegram.utils.request.Request` object (ignored if `bot` argument is used). The
            request_kwargs are very useful for the advanced users who would like to control the
            default timeouts and/or control the proxy used for http communication.

    Note:
        You must supply either a :attr:`bot` or a :attr:`token` argument.

    Raises:
        ValueError: If both :attr:`token` and :attr:`bot` are passed or none of them.

    """

    _request = None

    def __init__(self,
                 token=None,
                 base_url=None,
                 workers=4,
                 bot=None,
                 private_key=None,
                 private_key_password=None,
                 user_sig_handler=None,
                 request_kwargs=None):

        if (token is None) and (bot is None):
            raise ValueError('`token` or `bot` must be passed')
        if (token is not None) and (bot is not None):
            raise ValueError('`token` and `bot` are mutually exclusive')
        if (private_key is not None) and (bot is not None):
            raise ValueError('`bot` and `private_key` are mutually exclusive')

        self.logger = logging.getLogger(__name__)

        con_pool_size = workers + 4

        if bot is not None:
            self.bot = bot
            if bot.request.con_pool_size < con_pool_size:
                self.logger.warning(
                    'Connection pool of Request object is smaller than optimal value (%s)',
                    con_pool_size)
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
                request_kwargs['con_pool_size'] = con_pool_size
            self._request = Request(**request_kwargs)
            self.bot = Bot(token, base_url, request=self._request, private_key=private_key,
                           private_key_password=private_key_password)
        self.user_sig_handler = user_sig_handler
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
        self.running = False
        self.is_idle = False
        self.httpd = None
        self.__lock = Lock()
        self.__threads = []

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
            self.logger.exception('unhandled exception in %s', thr_name)
            raise
        self.logger.debug('{0} - ended'.format(thr_name))

    def start_polling(self,
                      poll_interval=0.0,
                      timeout=10,
                      clean=False,
                      bootstrap_retries=-1,
                      read_latency=2.,
                      allowed_updates=None):
        """Starts polling updates from Telegram.

        Args:
            poll_interval (:obj:`float`, optional): Time to wait between polling updates from
                Telegram in seconds. Default is 0.0.
            timeout (:obj:`float`, optional): Passed to :attr:`telegram.Bot.get_updates`.
            clean (:obj:`bool`, optional): Whether to clean any pending updates on Telegram servers
                before actually starting to poll. Default is False.
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                `Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely (default)
                *   0 - no retries
                * > 0 - retry up to X times

            allowed_updates (List[:obj:`str`], optional): Passed to
                :attr:`telegram.Bot.get_updates`.
            read_latency (:obj:`float` | :obj:`int`, optional): Grace time in seconds for receiving
                the reply from server. Will be added to the `timeout` value and used as the read
                timeout from server (Default: 2).

        Returns:
            :obj:`Queue`: The update queue that can be filled from the main thread.

        """
        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                self.job_queue.start()
                dispatcher_ready = Event()
                self._init_thread(self.dispatcher.start, "dispatcher", ready=dispatcher_ready)
                self._init_thread(self._start_polling, "updater", poll_interval, timeout,
                                  read_latency, bootstrap_retries, clean, allowed_updates)

                dispatcher_ready.wait()

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
                      webhook_url=None,
                      allowed_updates=None):
        """
        Starts a small http server to listen for updates via webhook. If cert
        and key are not provided, the webhook will be started directly on
        http://listen:port/url_path, so SSL can be handled by another
        application. Else, the webhook will be started on
        https://listen:port/url_path

        Args:
            listen (:obj:`str`, optional): IP-Address to listen on. Default ``127.0.0.1``.
            port (:obj:`int`, optional): Port the bot should be listening on. Default ``80``.
            url_path (:obj:`str`, optional): Path inside url.
            cert (:obj:`str`, optional): Path to the SSL certificate file.
            key (:obj:`str`, optional): Path to the SSL key file.
            clean (:obj:`bool`, optional): Whether to clean any pending updates on Telegram servers
                before actually starting the webhook. Default is ``False``.
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                `Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely (default)
                *   0 - no retries
                * > 0 - retry up to X times

            webhook_url (:obj:`str`, optional): Explicitly specify the webhook url. Useful behind
                NAT, reverse proxy, etc. Default is derived from `listen`, `port` & `url_path`.
            allowed_updates (List[:obj:`str`], optional): Passed to
                :attr:`telegram.Bot.set_webhook`.

        Returns:
            :obj:`Queue`: The update queue that can be filled from the main thread.

        """
        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                self.job_queue.start()
                self._init_thread(self.dispatcher.start, "dispatcher"),
                self._init_thread(self._start_webhook, "updater", listen, port, url_path, cert,
                                  key, bootstrap_retries, clean, webhook_url, allowed_updates)

                # Return the update queue so the main thread can insert updates
                return self.update_queue

    def _start_polling(self, poll_interval, timeout, read_latency, bootstrap_retries, clean,
                       allowed_updates):  # pragma: no cover
        # Thread target of thread 'updater'. Runs in background, pulls
        # updates from Telegram and inserts them in the update queue of the
        # Dispatcher.

        self.logger.debug('Updater thread started (polling)')

        self._bootstrap(bootstrap_retries, clean=clean, webhook_url='', allowed_updates=None)

        self.logger.debug('Bootstrap done')

        def polling_action_cb():
            updates = self.bot.get_updates(
                self.last_update_id, timeout=timeout, read_latency=read_latency,
                allowed_updates=allowed_updates)

            if updates:
                if not self.running:
                    self.logger.debug('Updates ignored and will be pulled again on restart')
                else:
                    for update in updates:
                        self.update_queue.put(update)
                    self.last_update_id = updates[-1].update_id + 1

            return True

        def polling_onerr_cb(exc):
            # Put the error into the update queue and let the Dispatcher
            # broadcast it
            self.update_queue.put(exc)

        self._network_loop_retry(polling_action_cb, polling_onerr_cb, 'getting Updates',
                                 poll_interval)

    def _network_loop_retry(self, action_cb, onerr_cb, description, interval):
        """Perform a loop calling `action_cb`, retrying after network errors.

        Stop condition for loop: `self.running` evaluates False or return value of `action_cb`
        evaluates False.

        Args:
            action_cb (:obj:`callable`): Network oriented callback function to call.
            onerr_cb (:obj:`callable`): Callback to call when TelegramError is caught. Receives the
                exception object as a parameter.
            description (:obj:`str`): Description text to use for logs and exception raised.
            interval (:obj:`float` | :obj:`int`): Interval to sleep between each call to
                `action_cb`.

        """
        self.logger.debug('Start network loop retry %s', description)
        cur_interval = interval
        while self.running:
            try:
                if not action_cb():
                    break
            except RetryAfter as e:
                self.logger.info('%s', e)
                cur_interval = 0.5 + e.retry_after
            except TimedOut as toe:
                self.logger.debug('Timed out %s: %s', description, toe)
                # If failure is due to timeout, we should retry asap.
                cur_interval = 0
            except InvalidToken as pex:
                self.logger.error('Invalid token; aborting')
                raise pex
            except TelegramError as te:
                self.logger.error('Error while %s: %s', description, te)
                onerr_cb(te)
                cur_interval = self._increase_poll_interval(cur_interval)
            else:
                cur_interval = interval

            if cur_interval:
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
                       webhook_url, allowed_updates):
        self.logger.debug('Updater thread started (webhook)')
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
                cert=open(cert, 'rb'),
                allowed_updates=allowed_updates)
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
        if exit_code == 0:
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

    def _bootstrap(self, max_retries, clean, webhook_url, allowed_updates, cert=None,
                   bootstrap_interval=5):
        retries = [0]

        def bootstrap_del_webhook():
            self.bot.delete_webhook()
            return False

        def bootstrap_clean_updates():
            self.logger.debug('Cleaning updates from Telegram server')
            updates = self.bot.get_updates()
            while updates:
                updates = self.bot.get_updates(updates[-1].update_id + 1)
            return False

        def bootstrap_set_webhook():
            self.bot.set_webhook(
                url=webhook_url, certificate=cert, allowed_updates=allowed_updates)
            return False

        def bootstrap_onerr_cb(exc):
            if not isinstance(exc, Unauthorized) and (max_retries < 0 or retries[0] < max_retries):
                retries[0] += 1
                self.logger.warning('Failed bootstrap phase; try=%s max_retries=%s',
                                    retries[0], max_retries)
            else:
                self.logger.error('Failed bootstrap phase after %s retries (%s)', retries[0], exc)
                raise exc

        # Cleaning pending messages is done by polling for them - so we need to delete webhook if
        # one is configured.
        # We also take this chance to delete pre-configured webhook if this is a polling Updater.
        # NOTE: We don't know ahead if a webhook is configured, so we just delete.
        if clean or not webhook_url:
            self._network_loop_retry(bootstrap_del_webhook, bootstrap_onerr_cb,
                                     'bootstrap del webhook', bootstrap_interval)
            retries[0] = 0

        # Clean pending messages, if requested.
        if clean:
            self._network_loop_retry(bootstrap_clean_updates, bootstrap_onerr_cb,
                                     'bootstrap clean updates', bootstrap_interval)
            retries[0] = 0
            sleep(1)

        # Restore/set webhook settings, if needed. Again, we don't know ahead if a webhook is set,
        # so we set it anyhow.
        if webhook_url:
            self._network_loop_retry(bootstrap_set_webhook, bootstrap_onerr_cb,
                                     'bootstrap set webhook', bootstrap_interval)

    def stop(self):
        """Stops the polling/webhook thread, the dispatcher and the job queue."""

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
            self.logger.info('Received signal {} ({}), stopping...'.format(
                signum, get_signal_name(signum)))
            self.stop()
            if self.user_sig_handler:
                self.user_sig_handler(signum, frame)
        else:
            self.logger.warning('Exiting immediately!')
            import os
            os._exit(1)

    def idle(self, stop_signals=(SIGINT, SIGTERM, SIGABRT)):
        """Blocks until one of the signals are received and stops the updater.

        Args:
            stop_signals (:obj:`iterable`): Iterable containing signals from the signal module that
                should be subscribed to. Updater.stop() will be called on receiving one of those
                signals. Defaults to (``SIGINT``, ``SIGTERM``, ``SIGABRT``).

        """
        for sig in stop_signals:
            signal(sig, self.signal_handler)

        self.is_idle = True

        while self.is_idle:
            sleep(1)
