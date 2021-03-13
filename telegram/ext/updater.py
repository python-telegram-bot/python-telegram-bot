#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
import ssl
import warnings
from queue import Queue
from signal import SIGABRT, SIGINT, SIGTERM, signal
from threading import Event, Lock, Thread, current_thread
from time import sleep
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union, no_type_check

from telegram import Bot, TelegramError
from telegram.error import InvalidToken, RetryAfter, TimedOut, Unauthorized
from telegram.ext import Dispatcher, JobQueue
from telegram.utils.deprecate import TelegramDeprecationWarning
from telegram.utils.helpers import get_signal_name
from telegram.utils.request import Request
from telegram.ext.utils.webhookhandler import WebhookAppClass, WebhookServer

if TYPE_CHECKING:
    from telegram.ext import BasePersistence, Defaults


class Updater:
    """
    This class, which employs the :class:`telegram.ext.Dispatcher`, provides a frontend to
    :class:`telegram.Bot` to the programmer, so they can focus on coding the bot. Its purpose is to
    receive the updates from Telegram and to deliver them to said dispatcher. It also runs in a
    separate thread, so the user can interact with the bot, for example on the command line. The
    dispatcher supports handlers for different kinds of data: Updates from Telegram, basic text
    commands and even arbitrary types. The updater can be started as a polling service or, for
    production, use a webhook to receive updates. This is achieved using the WebhookServer and
    WebhookHandler classes.

    Note:
        * You must supply either a :attr:`bot` or a :attr:`token` argument.
        * If you supply a :attr:`bot`, you will need to pass :attr:`defaults` to *both* the bot and
          the :class:`telegram.ext.Updater`.

    Args:
        token (:obj:`str`, optional): The bot's token given by the @BotFather.
        base_url (:obj:`str`, optional): Base_url for the bot.
        base_file_url (:obj:`str`, optional): Base_file_url for the bot.
        workers (:obj:`int`, optional): Amount of threads in the thread pool for functions
            decorated with ``@run_async`` (ignored if `dispatcher` argument is used).
        bot (:class:`telegram.Bot`, optional): A pre-initialized bot instance (ignored if
            `dispatcher` argument is used). If a pre-initialized bot is used, it is the user's
            responsibility to create it using a `Request` instance with a large enough connection
            pool.
        dispatcher (:class:`telegram.ext.Dispatcher`, optional): A pre-initialized dispatcher
            instance. If a pre-initialized dispatcher is used, it is the user's responsibility to
            create it with proper arguments.
        private_key (:obj:`bytes`, optional): Private key for decryption of telegram passport data.
        private_key_password (:obj:`bytes`, optional): Password for above private key.
        user_sig_handler (:obj:`function`, optional): Takes ``signum, frame`` as positional
            arguments. This will be called when a signal is received, defaults are (SIGINT,
            SIGTERM, SIGABRT) settable with :attr:`idle`.
        request_kwargs (:obj:`dict`, optional): Keyword args to control the creation of a
            `telegram.utils.request.Request` object (ignored if `bot` or `dispatcher` argument is
            used). The request_kwargs are very useful for the advanced users who would like to
            control the default timeouts and/or control the proxy used for http communication.
        use_context (:obj:`bool`, optional): If set to :obj:`True` uses the context based callback
            API (ignored if `dispatcher` argument is used). Defaults to :obj:`True`.
            **New users**: set this to :obj:`True`.
        persistence (:class:`telegram.ext.BasePersistence`, optional): The persistence class to
            store data that should be persistent over restarts (ignored if `dispatcher` argument is
            used).
        defaults (:class:`telegram.ext.Defaults`, optional): An object containing default values to
            be used if not set explicitly in the bot methods.

    Raises:
        ValueError: If both :attr:`token` and :attr:`bot` are passed or none of them.


    Attributes:
        bot (:class:`telegram.Bot`): The bot used with this Updater.
        user_sig_handler (:obj:`function`): Optional. Function to be called when a signal is
            received.
        update_queue (:obj:`Queue`): Queue for the updates.
        job_queue (:class:`telegram.ext.JobQueue`): Jobqueue for the updater.
        dispatcher (:class:`telegram.ext.Dispatcher`): Dispatcher that handles the updates and
            dispatches them to the handlers.
        running (:obj:`bool`): Indicates if the updater is running.
        persistence (:class:`telegram.ext.BasePersistence`): Optional. The persistence class to
            store data that should be persistent over restarts.
        use_context (:obj:`bool`): Optional. :obj:`True` if using context based callbacks.

    """

    _request = None

    def __init__(
        self,
        token: str = None,
        base_url: str = None,
        workers: int = 4,
        bot: Bot = None,
        private_key: bytes = None,
        private_key_password: bytes = None,
        user_sig_handler: Callable = None,
        request_kwargs: Dict[str, Any] = None,
        persistence: 'BasePersistence' = None,
        defaults: 'Defaults' = None,
        use_context: bool = True,
        dispatcher: Dispatcher = None,
        base_file_url: str = None,
    ):

        if defaults and bot:
            warnings.warn(
                'Passing defaults to an Updater has no effect when a Bot is passed '
                'as well. Pass them to the Bot instead.',
                TelegramDeprecationWarning,
                stacklevel=2,
            )

        if dispatcher is None:
            if (token is None) and (bot is None):
                raise ValueError('`token` or `bot` must be passed')
            if (token is not None) and (bot is not None):
                raise ValueError('`token` and `bot` are mutually exclusive')
            if (private_key is not None) and (bot is not None):
                raise ValueError('`bot` and `private_key` are mutually exclusive')
        else:
            if bot is not None:
                raise ValueError('`dispatcher` and `bot` are mutually exclusive')
            if persistence is not None:
                raise ValueError('`dispatcher` and `persistence` are mutually exclusive')
            if workers is not None:
                raise ValueError('`dispatcher` and `workers` are mutually exclusive')
            if use_context != dispatcher.use_context:
                raise ValueError('`dispatcher` and `use_context` are mutually exclusive')

        self.logger = logging.getLogger(__name__)

        if dispatcher is None:
            con_pool_size = workers + 4

            if bot is not None:
                self.bot = bot
                if bot.request.con_pool_size < con_pool_size:
                    self.logger.warning(
                        'Connection pool of Request object is smaller than optimal value (%s)',
                        con_pool_size,
                    )
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
                self.bot = Bot(
                    token,  # type: ignore[arg-type]
                    base_url,
                    base_file_url=base_file_url,
                    request=self._request,
                    private_key=private_key,
                    private_key_password=private_key_password,
                    defaults=defaults,
                )
            self.update_queue: Queue = Queue()
            self.job_queue = JobQueue()
            self.__exception_event = Event()
            self.persistence = persistence
            self.dispatcher = Dispatcher(
                self.bot,
                self.update_queue,
                job_queue=self.job_queue,
                workers=workers,
                exception_event=self.__exception_event,
                persistence=persistence,
                use_context=use_context,
            )
            self.job_queue.set_dispatcher(self.dispatcher)
        else:
            con_pool_size = dispatcher.workers + 4

            self.bot = dispatcher.bot
            if self.bot.request.con_pool_size < con_pool_size:
                self.logger.warning(
                    'Connection pool of Request object is smaller than optimal value (%s)',
                    con_pool_size,
                )
            self.update_queue = dispatcher.update_queue
            self.__exception_event = dispatcher.exception_event
            self.persistence = dispatcher.persistence
            self.job_queue = dispatcher.job_queue
            self.dispatcher = dispatcher

        self.user_sig_handler = user_sig_handler
        self.last_update_id = 0
        self.running = False
        self.is_idle = False
        self.httpd = None
        self.__lock = Lock()
        self.__threads: List[Thread] = []

    def _init_thread(self, target: Callable, name: str, *args: object, **kwargs: object) -> None:
        thr = Thread(
            target=self._thread_wrapper,
            name=f"Bot:{self.bot.id}:{name}",
            args=(target,) + args,
            kwargs=kwargs,
        )
        thr.start()
        self.__threads.append(thr)

    def _thread_wrapper(self, target: Callable, *args: object, **kwargs: object) -> None:
        thr_name = current_thread().name
        self.logger.debug('%s - started', thr_name)
        try:
            target(*args, **kwargs)
        except Exception:
            self.__exception_event.set()
            self.logger.exception('unhandled exception in %s', thr_name)
            raise
        self.logger.debug('%s - ended', thr_name)

    def start_polling(
        self,
        poll_interval: float = 0.0,
        timeout: float = 10,
        clean: bool = None,
        bootstrap_retries: int = -1,
        read_latency: float = 2.0,
        allowed_updates: List[str] = None,
        drop_pending_updates: bool = None,
    ) -> Optional[Queue]:
        """Starts polling updates from Telegram.

        Args:
            poll_interval (:obj:`float`, optional): Time to wait between polling updates from
                Telegram in seconds. Default is 0.0.
            timeout (:obj:`float`, optional): Passed to :meth:`telegram.Bot.get_updates`.
            drop_pending_updates (:obj:`bool`, optional): Whether to clean any pending updates on
                Telegram servers before actually starting to poll. Default is :obj:`False`.

                .. versionadded :: 13.4
            clean (:obj:`bool`, optional): Alias for ``drop_pending_updates``.

                .. deprecated:: 13.4
                    Use ``drop_pending_updates`` instead.
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                :class:`telegram.ext.Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely (default)
                *   0 - no retries
                * > 0 - retry up to X times

            allowed_updates (List[:obj:`str`], optional): Passed to
                :meth:`telegram.Bot.get_updates`.
            read_latency (:obj:`float` | :obj:`int`, optional): Grace time in seconds for receiving
                the reply from server. Will be added to the ``timeout`` value and used as the read
                timeout from server (Default: 2).

        Returns:
            :obj:`Queue`: The update queue that can be filled from the main thread.

        """
        if (clean is not None) and (drop_pending_updates is not None):
            raise TypeError('`clean` and `drop_pending_updates` are mutually exclusive.')

        if clean is not None:
            warnings.warn(
                'The argument `clean` of `start_polling` is deprecated. Please use '
                '`drop_pending_updates` instead.',
                category=TelegramDeprecationWarning,
                stacklevel=2,
            )

        drop_pending_updates = drop_pending_updates if drop_pending_updates is not None else clean

        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                self.job_queue.start()
                dispatcher_ready = Event()
                polling_ready = Event()
                self._init_thread(self.dispatcher.start, "dispatcher", ready=dispatcher_ready)
                self._init_thread(
                    self._start_polling,
                    "updater",
                    poll_interval,
                    timeout,
                    read_latency,
                    bootstrap_retries,
                    drop_pending_updates,
                    allowed_updates,
                    ready=polling_ready,
                )

                self.logger.debug('Waiting for Dispatcher and polling to start')
                dispatcher_ready.wait()
                polling_ready.wait()

                # Return the update queue so the main thread can insert updates
                return self.update_queue
            return None

    def start_webhook(
        self,
        listen: str = '127.0.0.1',
        port: int = 80,
        url_path: str = '',
        cert: str = None,
        key: str = None,
        clean: bool = None,
        bootstrap_retries: int = 0,
        webhook_url: str = None,
        allowed_updates: List[str] = None,
        force_event_loop: bool = False,
        drop_pending_updates: bool = None,
        ip_address: str = None,
    ) -> Optional[Queue]:
        """
        Starts a small http server to listen for updates via webhook. If cert
        and key are not provided, the webhook will be started directly on
        http://listen:port/url_path, so SSL can be handled by another
        application. Else, the webhook will be started on
        https://listen:port/url_path. Also calls :meth:`telegram.Bot.set_webhook` as required.

        Note:
            Due to an incompatibility of the Tornado library PTB uses for the webhook with Python
            3.8+ on Windows machines, PTB will attempt to set the event loop to
            :attr:`asyncio.SelectorEventLoop` and raise an exception, if an incompatible event loop
            has already been specified. See this `thread`_ for more details. To suppress the
            exception, set :attr:`force_event_loop` to :obj:`True`.

            .. _thread: https://github.com/tornadoweb/tornado/issues/2608

        Args:
            listen (:obj:`str`, optional): IP-Address to listen on. Default ``127.0.0.1``.
            port (:obj:`int`, optional): Port the bot should be listening on. Default ``80``.
            url_path (:obj:`str`, optional): Path inside url.
            cert (:obj:`str`, optional): Path to the SSL certificate file.
            key (:obj:`str`, optional): Path to the SSL key file.
            drop_pending_updates (:obj:`bool`, optional): Whether to clean any pending updates on
                Telegram servers before actually starting to poll. Default is :obj:`False`.

                .. versionadded :: 13.4
            clean (:obj:`bool`, optional): Alias for ``drop_pending_updates``.

                .. deprecated:: 13.4
                    Use ``drop_pending_updates`` instead.
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                :class:`telegram.ext.Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely (default)
                *   0 - no retries
                * > 0 - retry up to X times

            webhook_url (:obj:`str`, optional): Explicitly specify the webhook url. Useful behind
                NAT, reverse proxy, etc. Default is derived from ``listen``, ``port`` &
                ``url_path``.
            ip_address (:obj:`str`, optional): Passed to :meth:`telegram.Bot.set_webhook`.

                .. versionadded :: 13.4
            allowed_updates (List[:obj:`str`], optional): Passed to
                :meth:`telegram.Bot.set_webhook`.
            force_event_loop (:obj:`bool`, optional): Force using the current event loop. See above
                note for details. Defaults to :obj:`False`

        Returns:
            :obj:`Queue`: The update queue that can be filled from the main thread.

        """
        if (clean is not None) and (drop_pending_updates is not None):
            raise TypeError('`clean` and `drop_pending_updates` are mutually exclusive.')

        if clean is not None:
            warnings.warn(
                'The argument `clean` of `start_webhook` is deprecated. Please use '
                '`drop_pending_updates` instead.',
                category=TelegramDeprecationWarning,
                stacklevel=2,
            )

        drop_pending_updates = drop_pending_updates if drop_pending_updates is not None else clean

        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                webhook_ready = Event()
                dispatcher_ready = Event()
                self.job_queue.start()
                self._init_thread(self.dispatcher.start, "dispatcher", dispatcher_ready)
                self._init_thread(
                    self._start_webhook,
                    "updater",
                    listen,
                    port,
                    url_path,
                    cert,
                    key,
                    bootstrap_retries,
                    drop_pending_updates,
                    webhook_url,
                    allowed_updates,
                    ready=webhook_ready,
                    force_event_loop=force_event_loop,
                    ip_address=ip_address,
                )

                self.logger.debug('Waiting for Dispatcher and Webhook to start')
                webhook_ready.wait()
                dispatcher_ready.wait()

                # Return the update queue so the main thread can insert updates
                return self.update_queue
            return None

    @no_type_check
    def _start_polling(
        self,
        poll_interval,
        timeout,
        read_latency,
        bootstrap_retries,
        drop_pending_updates,
        allowed_updates,
        ready=None,
    ):  # pragma: no cover
        # Thread target of thread 'updater'. Runs in background, pulls
        # updates from Telegram and inserts them in the update queue of the
        # Dispatcher.

        self.logger.debug('Updater thread started (polling)')

        self._bootstrap(
            bootstrap_retries,
            drop_pending_updates=drop_pending_updates,
            webhook_url='',
            allowed_updates=None,
        )

        self.logger.debug('Bootstrap done')

        def polling_action_cb():
            updates = self.bot.get_updates(
                self.last_update_id,
                timeout=timeout,
                read_latency=read_latency,
                allowed_updates=allowed_updates,
            )

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

        if ready is not None:
            ready.set()

        self._network_loop_retry(
            polling_action_cb, polling_onerr_cb, 'getting Updates', poll_interval
        )

    @no_type_check
    def _network_loop_retry(self, action_cb, onerr_cb, description, interval):
        """Perform a loop calling `action_cb`, retrying after network errors.

        Stop condition for loop: `self.running` evaluates :obj:`False` or return value of
        `action_cb` evaluates :obj:`False`.

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
            except RetryAfter as exc:
                self.logger.info('%s', exc)
                cur_interval = 0.5 + exc.retry_after
            except TimedOut as toe:
                self.logger.debug('Timed out %s: %s', description, toe)
                # If failure is due to timeout, we should retry asap.
                cur_interval = 0
            except InvalidToken as pex:
                self.logger.error('Invalid token; aborting')
                raise pex
            except TelegramError as telegram_exc:
                self.logger.error('Error while %s: %s', description, telegram_exc)
                onerr_cb(telegram_exc)
                cur_interval = self._increase_poll_interval(cur_interval)
            else:
                cur_interval = interval

            if cur_interval:
                sleep(cur_interval)

    @staticmethod
    def _increase_poll_interval(current_interval: float) -> float:
        # increase waiting times on subsequent errors up to 30secs
        if current_interval == 0:
            current_interval = 1
        elif current_interval < 30:
            current_interval += current_interval / 2
        elif current_interval > 30:
            current_interval = 30
        return current_interval

    @no_type_check
    def _start_webhook(
        self,
        listen,
        port,
        url_path,
        cert,
        key,
        bootstrap_retries,
        drop_pending_updates,
        webhook_url,
        allowed_updates,
        ready=None,
        force_event_loop=False,
        ip_address=None,
    ):
        self.logger.debug('Updater thread started (webhook)')

        # Note that we only use the SSL certificate for the WebhookServer, if the key is also
        # present. This is because the WebhookServer may not actually be in charge of performing
        # the SSL handshake, e.g. in case a reverse proxy is used
        use_ssl = cert is not None and key is not None

        if not url_path.startswith('/'):
            url_path = f'/{url_path}'

        # Create Tornado app instance
        app = WebhookAppClass(url_path, self.bot, self.update_queue)

        # Form SSL Context
        # An SSLError is raised if the private key does not match with the certificate
        if use_ssl:
            try:
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(cert, key)
            except ssl.SSLError as exc:
                raise TelegramError('Invalid SSL Certificate') from exc
        else:
            ssl_ctx = None

        # Create and start server
        self.httpd = WebhookServer(listen, port, app, ssl_ctx)

        if not webhook_url:
            webhook_url = self._gen_webhook_url(listen, port, url_path)

        # We pass along the cert to the webhook if present.
        self._bootstrap(
            max_retries=bootstrap_retries,
            drop_pending_updates=drop_pending_updates,
            webhook_url=webhook_url,
            allowed_updates=allowed_updates,
            cert=open(cert, 'rb') if cert is not None else None,
            ip_address=ip_address,
        )

        self.httpd.serve_forever(force_event_loop=force_event_loop, ready=ready)

    @staticmethod
    def _gen_webhook_url(listen: str, port: int, url_path: str) -> str:
        return f'https://{listen}:{port}{url_path}'

    @no_type_check
    def _bootstrap(
        self,
        max_retries,
        drop_pending_updates,
        webhook_url,
        allowed_updates,
        cert=None,
        bootstrap_interval=5,
        ip_address=None,
    ):
        retries = [0]

        def bootstrap_del_webhook():
            self.logger.debug('Deleting webhook')
            if drop_pending_updates:
                self.logger.debug('Dropping pending updates from Telegram server')
            self.bot.delete_webhook(drop_pending_updates=drop_pending_updates)
            return False

        def bootstrap_set_webhook():
            self.logger.debug('Setting webhook')
            if drop_pending_updates:
                self.logger.debug('Dropping pending updates from Telegram server')
            self.bot.set_webhook(
                url=webhook_url,
                certificate=cert,
                allowed_updates=allowed_updates,
                ip_address=ip_address,
                drop_pending_updates=drop_pending_updates,
            )
            return False

        def bootstrap_onerr_cb(exc):
            if not isinstance(exc, Unauthorized) and (max_retries < 0 or retries[0] < max_retries):
                retries[0] += 1
                self.logger.warning(
                    'Failed bootstrap phase; try=%s max_retries=%s', retries[0], max_retries
                )
            else:
                self.logger.error('Failed bootstrap phase after %s retries (%s)', retries[0], exc)
                raise exc

        # Dropping pending updates from TG can be efficiently done with the drop_pending_updates
        # parameter of delete/start_webhook, even in the case of polling. Also we want to make
        # sure that no webhook is configured in case of polling, so we just always call
        # delete_webhook for polling
        if drop_pending_updates or not webhook_url:
            self._network_loop_retry(
                bootstrap_del_webhook,
                bootstrap_onerr_cb,
                'bootstrap del webhook',
                bootstrap_interval,
            )
            retries[0] = 0

        # Restore/set webhook settings, if needed. Again, we don't know ahead if a webhook is set,
        # so we set it anyhow.
        if webhook_url:
            self._network_loop_retry(
                bootstrap_set_webhook,
                bootstrap_onerr_cb,
                'bootstrap set webhook',
                bootstrap_interval,
            )

    def stop(self) -> None:
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

    @no_type_check
    def _stop_httpd(self) -> None:
        if self.httpd:
            self.logger.debug(
                'Waiting for current webhook connection to be '
                'closed... Send a Telegram message to the bot to exit '
                'immediately.'
            )
            self.httpd.shutdown()
            self.httpd = None

    @no_type_check
    def _stop_dispatcher(self) -> None:
        self.logger.debug('Requesting Dispatcher to stop...')
        self.dispatcher.stop()

    @no_type_check
    def _join_threads(self) -> None:
        for thr in self.__threads:
            self.logger.debug('Waiting for %s thread to end', thr.name)
            thr.join()
            self.logger.debug('%s thread has ended', thr.name)
        self.__threads = []

    @no_type_check
    def signal_handler(self, signum, frame) -> None:
        self.is_idle = False
        if self.running:
            self.logger.info(
                'Received signal %s (%s), stopping...', signum, get_signal_name(signum)
            )
            if self.persistence:
                # Update user_data, chat_data and bot_data before flushing
                self.dispatcher.update_persistence()
                self.persistence.flush()
            self.stop()
            if self.user_sig_handler:
                self.user_sig_handler(signum, frame)
        else:
            self.logger.warning('Exiting immediately!')
            # pylint: disable=C0415,W0212
            import os

            os._exit(1)

    def idle(self, stop_signals: Union[List, Tuple] = (SIGINT, SIGTERM, SIGABRT)) -> None:
        """Blocks until one of the signals are received and stops the updater.

        Args:
            stop_signals (:obj:`list` | :obj:`tuple`): List containing signals from the signal
                module that should be subscribed to. Updater.stop() will be called on receiving one
                of those signals. Defaults to (``SIGINT``, ``SIGTERM``, ``SIGABRT``).

        """
        for sig in stop_signals:
            signal(sig, self.signal_handler)

        self.is_idle = True

        while self.is_idle:
            sleep(1)
