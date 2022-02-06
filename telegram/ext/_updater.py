#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
import asyncio
import logging
import ssl
from pathlib import Path
from types import TracebackType
from typing import (
    Callable,
    List,
    Optional,
    Union,
    TypeVar,
    TYPE_CHECKING,
    Coroutine,
    Type,
)

from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import ODVInput
from telegram.error import InvalidToken, RetryAfter, TimedOut, Forbidden, TelegramError
from telegram.ext._utils.webhookhandler import WebhookAppClass, WebhookServer

if TYPE_CHECKING:
    from telegram import Bot


_UpdaterType = TypeVar('_UpdaterType', bound="Updater")


class Updater:
    """This class fetches updates for the bot either via long polling or by starting a webhook
    server. Received updates are enqueued into the :attr:`update_queue` and may be fetched from
    there to handle them appropriately.

    .. versionchanged:: 14.0

        * Removed argument and attribute ``user_sig_handler``
        * The only arguments and attributes are now :attr:`bot` and :attr:`update_queue` as now
          the sole purpose of this class is to fetch updates. The entry point to a PTB application
          is now :class:`telegram.ext.Application`.

    Attributes:
        bot (:class:`telegram.Bot`): The bot used with this Updater.
        update_queue (:class:`asyncio.Queue`): Queue for the updates.

    Args:
        bot (:class:`telegram.Bot`): The bot used with this Updater.
        update_queue (:class:`asyncio.Queue`): Queue for the updates.

    """

    __slots__ = (
        'bot',
        '_logger',
        'update_queue',
        'last_update_id',
        '_running',
        '_httpd',
        '__lock',
        '__asyncio_tasks',
    )

    def __init__(
        self,
        bot: 'Bot',
        update_queue: asyncio.Queue,
    ):
        self.bot = bot
        self.update_queue = update_queue

        self.last_update_id = 0
        self._running = False
        self._httpd: Optional[WebhookServer] = None
        self.__lock = asyncio.Lock()
        self.__asyncio_tasks: List[asyncio.Task] = []
        self._logger = logging.getLogger(__name__)

    @property
    def running(self) -> bool:
        return self._running

    async def initialize(self) -> None:
        await self.bot.initialize()

    async def shutdown(self) -> None:
        await self.bot.shutdown()
        self._logger.debug('Shut down of Updater complete')

    async def __aenter__(self: _UpdaterType) -> _UpdaterType:
        try:
            await self.initialize()
            return self
        except Exception as exc:
            await self.shutdown()
            raise exc

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # Make sure not to return `True` so that exceptions are not suppressed
        # https://docs.python.org/3/reference/datamodel.html?#object.__aexit__
        await self.shutdown()

    def _init_task(
        self, target: Callable[..., Coroutine], name: str, *args: object, **kwargs: object
    ) -> None:
        task = asyncio.create_task(
            coro=self._task_wrapper(target, name, *args, **kwargs),
            # TODO: Add this once we drop py3.7
            # name=f"Updater:{self.bot.id}:{name}",
        )
        self.__asyncio_tasks.append(task)

    async def _task_wrapper(
        self, target: Callable, name: str, *args: object, **kwargs: object
    ) -> None:
        self._logger.debug('%s - started', name)
        try:
            await target(*args, **kwargs)
        except Exception:
            self._logger.exception('Unhandled exception in %s.', name)
        self._logger.debug('%s - ended', name)

    # TODO: Probably drop `pool_connect` timeout again, because we probably want to just make
    #       sure that `getUpdates` always gets a connection without waiting
    async def start_polling(
        self,
        poll_interval: float = 0.0,
        timeout: int = 10,
        bootstrap_retries: int = -1,
        read_timeout: float = 2,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        allowed_updates: List[str] = None,
        drop_pending_updates: bool = None,
        error_callback: Callable[[TelegramError], None] = None,
    ) -> asyncio.Queue:
        """Starts polling updates from Telegram.

        .. versionchanged:: 14.0
            Removed the ``clean`` argument in favor of ``drop_pending_updates``.

        Args:
            poll_interval (:obj:`float`, optional): Time to wait between polling updates from
                Telegram in seconds. Default is ``0.0``.
            timeout (:obj:`float`, optional): Passed to :meth:`telegram.Bot.get_updates`.
            drop_pending_updates (:obj:`bool`, optional): Whether to clean any pending updates on
                Telegram servers before actually starting to poll. Default is :obj:`False`.

                .. versionadded :: 13.4
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                :class:`telegram.ext.Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely (default)
                *   0 - no retries
                * > 0 - retry up to X times

            allowed_updates (List[:obj:`str`], optional): Passed to
                :meth:`telegram.Bot.get_updates`.
            read_timeout (:obj:`float` | :obj:`int`, optional): Grace time in seconds for receiving
                the reply from server. Will be added to the ``timeout`` value and used as the read
                timeout from server (Default: ``2``).
            error_callback (Callable[[:exc:`telegram.error.TelegramError`], :obj:`None`], \
                optional): Callback to handle :exc:`telegram.error.TelegramError` s that occur
                while calling :meth:`telegram.Bot.get_updates` during polling. Defaults to
                :obj:`None`, in which case errors will be logged.

        Returns:
            :class:`asyncio.Queue`: The update queue that can be filled from the main thread.

        """
        async with self.__lock:
            if self.running:
                return self.update_queue

            self._running = True

            # Create & start tasks
            polling_ready = asyncio.Event()

            self._init_task(
                self._start_polling,
                "Polling Background task",
                poll_interval,
                timeout,
                read_timeout,
                write_timeout,
                connect_timeout,
                pool_timeout,
                bootstrap_retries,
                drop_pending_updates,
                allowed_updates,
                ready=polling_ready,
                error_callback=error_callback,
            )

            self._logger.debug('Waiting for polling to start')
            await polling_ready.wait()
            self._logger.debug('Polling to started')

            return self.update_queue

    async def _start_polling(
        self,
        poll_interval: float,
        timeout: int,
        read_timeout: Optional[float],
        write_timeout: Optional[float],
        connect_timeout: Optional[float],
        pool_timeout: Optional[float],
        bootstrap_retries: int,
        drop_pending_updates: bool,
        allowed_updates: Optional[List[str]],
        ready: asyncio.Event = None,
        error_callback: Callable[[TelegramError], None] = None,
    ) -> None:
        # Target of task 'updater.start_polling()'. Runs in background, pulls
        # updates from Telegram and inserts them in the update queue of the
        # Application.

        self._logger.debug('Updater started (polling)')

        await self._bootstrap(
            bootstrap_retries,
            drop_pending_updates=drop_pending_updates,
            webhook_url='',
            allowed_updates=None,
        )

        self._logger.debug('Bootstrap done')

        async def polling_action_cb() -> bool:
            updates = await self.bot.get_updates(
                self.last_update_id,
                timeout=timeout,
                read_timeout=read_timeout,
                connect_timeout=connect_timeout,
                write_timeout=write_timeout,
                pool_timeout=pool_timeout,
                allowed_updates=allowed_updates,
            )

            if updates:
                if not self.running:
                    self._logger.debug('Updates ignored and will be pulled again on restart')
                else:
                    for update in updates:
                        await self.update_queue.put(update)
                    self.last_update_id = updates[-1].update_id + 1

            return True

        def default_error_callback(exc: TelegramError) -> None:
            self._logger.exception('Exception happened while polling for updates.', exc_info=exc)

        if ready is not None:
            ready.set()

        await self._network_loop_retry(
            action_cb=polling_action_cb,
            onerr_cb=error_callback or default_error_callback,
            description='getting Updates',
            interval=poll_interval,
        )

    async def start_webhook(
        self,
        listen: str = '127.0.0.1',
        port: int = 80,
        url_path: str = '',
        cert: Union[str, Path] = None,
        key: Union[str, Path] = None,
        bootstrap_retries: int = 0,
        webhook_url: str = None,
        allowed_updates: List[str] = None,
        drop_pending_updates: bool = None,
        ip_address: str = None,
        max_connections: int = 40,
    ) -> asyncio.Queue:
        """
        Starts a small http server to listen for updates via webhook. If :attr:`cert`
        and :attr:`key` are not provided, the webhook will be started directly on
        http://listen:port/url_path, so SSL can be handled by another
        application. Else, the webhook will be started on
        https://listen:port/url_path. Also calls :meth:`telegram.Bot.set_webhook` as required.

        .. versionchanged:: 13.4
            :meth:`start_webhook` now *always* calls :meth:`telegram.Bot.set_webhook`, so pass
            ``webhook_url`` instead of calling ``updater.bot.set_webhook(webhook_url)`` manually.
        .. versionchanged:: 14.0
            Removed the ``clean`` argument in favor of ``drop_pending_updates`` and removed the
            deprecated argument ``force_event_loop``.

        Args:
            listen (:obj:`str`, optional): IP-Address to listen on. Default ``127.0.0.1``.
            port (:obj:`int`, optional): Port the bot should be listening on. Must be one of
                :attr:`telegram.constants.SUPPORTED_WEBHOOK_PORTS`. Defaults to ``80``.
            url_path (:obj:`str`, optional): Path inside url.
            cert (:class:`pathlib.Path` | :obj:`str`, optional): Path to the SSL certificate file.
            key (:class:`pathlib.Path` | :obj:`str`, optional): Path to the SSL key file.
            drop_pending_updates (:obj:`bool`, optional): Whether to clean any pending updates on
                Telegram servers before actually starting to poll. Default is :obj:`False`.
                .. versionadded :: 13.4
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
            max_connections (:obj:`int`, optional): Passed to
                :meth:`telegram.Bot.set_webhook`.
                .. versionadded:: 13.6
        Returns:
            :obj:`Queue`: The update queue that can be filled from the main thread.
        """
        async with self.__lock:
            if self.running:
                return self.update_queue

            self._running = True

            # Create & start tasks
            webhook_ready = asyncio.Event()

            await self._start_webhook(
                listen=listen,
                port=port,
                url_path=url_path,
                cert=cert,
                key=key,
                bootstrap_retries=bootstrap_retries,
                drop_pending_updates=drop_pending_updates,
                webhook_url=webhook_url,
                allowed_updates=allowed_updates,
                ready=webhook_ready,
                ip_address=ip_address,
                max_connections=max_connections,
            )

            self._logger.debug('Waiting for webhook server to start')
            await webhook_ready.wait()
            self._logger.debug('Webhook server started')

            # Return the update queue so the main thread can insert updates
            return self.update_queue

    async def _start_webhook(
        self,
        listen: str,
        port: int,
        url_path: str,
        bootstrap_retries: int,
        allowed_updates: Optional[List[str]],
        cert: Union[str, Path] = None,
        key: Union[str, Path] = None,
        drop_pending_updates: bool = None,
        webhook_url: str = None,
        ready: asyncio.Event = None,
        ip_address: str = None,
        max_connections: int = 40,
    ) -> None:
        self._logger.debug('Updater thread started (webhook)')

        if not url_path.startswith('/'):
            url_path = f'/{url_path}'

        # Create Tornado app instance
        app = WebhookAppClass(url_path, self.bot, self.update_queue)

        # Form SSL Context
        # An SSLError is raised if the private key does not match with the certificate
        # Note that we only use the SSL certificate for the WebhookServer, if the key is also
        # present. This is because the WebhookServer may not actually be in charge of performing
        # the SSL handshake, e.g. in case a reverse proxy is used
        if cert is not None and key is not None:
            try:
                ssl_ctx: Optional[ssl.SSLContext] = ssl.create_default_context(
                    ssl.Purpose.CLIENT_AUTH
                )
                ssl_ctx.load_cert_chain(cert, key)  # type: ignore[union-attr]
            except ssl.SSLError as exc:
                raise TelegramError('Invalid SSL Certificate') from exc
        else:
            ssl_ctx = None

        # Create and start server
        self._httpd = WebhookServer(listen, port, app, ssl_ctx)

        if not webhook_url:
            webhook_url = self._gen_webhook_url(listen, port, url_path)

        # We pass along the cert to the webhook if present.
        if cert is not None:
            await self._bootstrap(
                cert=cert,
                max_retries=bootstrap_retries,
                drop_pending_updates=drop_pending_updates,
                webhook_url=webhook_url,
                allowed_updates=allowed_updates,
                ip_address=ip_address,
                max_connections=max_connections,
            )
        else:
            await self._bootstrap(
                max_retries=bootstrap_retries,
                drop_pending_updates=drop_pending_updates,
                webhook_url=webhook_url,
                allowed_updates=allowed_updates,
                ip_address=ip_address,
                max_connections=max_connections,
            )

        await self._httpd.serve_forever(ready=ready)

    @staticmethod
    def _gen_webhook_url(listen: str, port: int, url_path: str) -> str:
        return f'https://{listen}:{port}{url_path}'

    async def _network_loop_retry(
        self,
        action_cb: Callable[..., Coroutine],
        onerr_cb: Callable[[TelegramError], None],
        description: str,
        interval: float,
    ) -> None:
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
        self._logger.debug('Start network loop retry %s', description)
        cur_interval = interval
        while self.running:
            try:
                try:
                    if not await action_cb():
                        break
                except RetryAfter as exc:
                    self._logger.info('%s', exc)
                    cur_interval = 0.5 + exc.retry_after
                except TimedOut as toe:
                    self._logger.debug('Timed out %s: %s', description, toe)
                    # If failure is due to timeout, we should retry asap.
                    cur_interval = 0
                except InvalidToken as pex:
                    self._logger.error('Invalid token; aborting')
                    raise pex
                except TelegramError as telegram_exc:
                    self._logger.error('Error while %s: %s', description, telegram_exc)
                    onerr_cb(telegram_exc)
                    cur_interval = self._increase_poll_interval(cur_interval)
                else:
                    cur_interval = interval

                if cur_interval:
                    await asyncio.sleep(cur_interval)

            except asyncio.CancelledError:
                self._logger.debug('Network loop retry %s was cancelled', description)
                break

    @staticmethod
    def _increase_poll_interval(current_interval: float) -> float:
        # increase waiting times on subsequent errors up to 30secs
        if current_interval == 0:
            current_interval = 1
        elif current_interval < 30:
            current_interval *= 1.5
        else:
            current_interval = min(30.0, current_interval)
        return current_interval

    async def _bootstrap(
        self,
        max_retries: int,
        webhook_url: Optional[str],
        allowed_updates: Optional[List[str]],
        drop_pending_updates: bool = None,
        cert: Union[str, Path] = None,
        bootstrap_interval: float = 5,
        ip_address: str = None,
        max_connections: int = 40,
    ) -> None:
        retries = [0]

        async def bootstrap_del_webhook() -> bool:
            self._logger.debug('Deleting webhook')
            if drop_pending_updates:
                self._logger.debug('Dropping pending updates from Telegram server')
            await self.bot.delete_webhook(drop_pending_updates=drop_pending_updates)
            return False

        async def bootstrap_set_webhook() -> bool:
            self._logger.debug('Setting webhook')
            if drop_pending_updates:
                self._logger.debug('Dropping pending updates from Telegram server')
            await self.bot.set_webhook(
                url=webhook_url,
                certificate=cert,
                allowed_updates=allowed_updates,
                ip_address=ip_address,
                drop_pending_updates=drop_pending_updates,
                max_connections=max_connections,
            )
            return False

        def bootstrap_onerr_cb(exc: Exception) -> None:
            if not isinstance(exc, Forbidden) and (max_retries < 0 or retries[0] < max_retries):
                retries[0] += 1
                self._logger.warning(
                    'Failed bootstrap phase; try=%s max_retries=%s', retries[0], max_retries
                )
            else:
                self._logger.error('Failed bootstrap phase after %s retries (%s)', retries[0], exc)
                raise exc

        # Dropping pending updates from TG can be efficiently done with the drop_pending_updates
        # parameter of delete/start_webhook, even in the case of polling. Also we want to make
        # sure that no webhook is configured in case of polling, so we just always call
        # delete_webhook for polling
        if drop_pending_updates or not webhook_url:
            await self._network_loop_retry(
                bootstrap_del_webhook,
                bootstrap_onerr_cb,
                'bootstrap del webhook',
                bootstrap_interval,
            )
            retries[0] = 0

        # Restore/set webhook settings, if needed. Again, we don't know ahead if a webhook is set,
        # so we set it anyhow.
        if webhook_url:
            await self._network_loop_retry(
                bootstrap_set_webhook,
                bootstrap_onerr_cb,
                'bootstrap set webhook',
                bootstrap_interval,
            )

    async def stop(self) -> None:
        """Stops the polling/webhook."""
        async with self.__lock:
            if self.running:
                self._logger.debug('Stopping Updater')

                self._running = False

                await self._stop_httpd()
                await self._join_tasks()

                self._logger.debug('Updater.stop() is complete')

    async def _stop_httpd(self) -> None:
        if self._httpd:
            self._logger.debug('Waiting for current webhook connection to be closed.')
            await self._httpd.shutdown()
            self._httpd = None

    async def _join_tasks(self) -> None:
        self._logger.debug('Stopping Background tasks')
        for task in self.__asyncio_tasks:
            task.cancel()
        await asyncio.gather(*self.__asyncio_tasks)
        self.__asyncio_tasks = []
