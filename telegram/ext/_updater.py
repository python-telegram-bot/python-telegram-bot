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
from contextlib import AbstractAsyncContextManager
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Callable, Coroutine, List, Optional, Type, TypeVar, Union

from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import ODVInput
from telegram.error import InvalidToken, RetryAfter, TelegramError, TimedOut

try:
    from telegram.ext._utils.webhookhandler import WebhookAppClass, WebhookServer

    WEBHOOKS_AVAILABLE = True
except ImportError:
    WEBHOOKS_AVAILABLE = False

if TYPE_CHECKING:
    from telegram import Bot


_UpdaterType = TypeVar("_UpdaterType", bound="Updater")  # pylint: disable=invalid-name


class Updater(AbstractAsyncContextManager):
    """This class fetches updates for the bot either via long polling or by starting a webhook
    server. Received updates are enqueued into the :attr:`update_queue` and may be fetched from
    there to handle them appropriately.

    Instances of this class can be used as asyncio context managers, where

    .. code:: python

        async with updater:
            # code

    is roughly equivalent to

    .. code:: python

        try:
            await updater.initialize()
            # code
        finally:
            await updater.shutdown()

    .. seealso:: :wiki:`Architecture Overview <Architecture>`,
        :wiki:`Builder Pattern <Builder-Pattern>`

    .. versionchanged:: 20.0

        * Removed argument and attribute ``user_sig_handler``
        * The only arguments and attributes are now :attr:`bot` and :attr:`update_queue` as now
          the sole purpose of this class is to fetch updates. The entry point to a PTB application
          is now :class:`telegram.ext.Application`.

    Args:
        bot (:class:`telegram.Bot`): The bot used with this Updater.
        update_queue (:class:`asyncio.Queue`): Queue for the updates.

    Attributes:
        bot (:class:`telegram.Bot`): The bot used with this Updater.
        update_queue (:class:`asyncio.Queue`): Queue for the updates.

    """

    __slots__ = (
        "bot",
        "_logger",
        "update_queue",
        "_last_update_id",
        "_running",
        "_initialized",
        "_httpd",
        "__lock",
        "__polling_task",
    )

    def __init__(
        self,
        bot: "Bot",
        update_queue: asyncio.Queue,
    ):
        self.bot = bot
        self.update_queue = update_queue

        self._last_update_id = 0
        self._running = False
        self._initialized = False
        self._httpd: Optional[WebhookServer] = None
        self.__lock = asyncio.Lock()
        self.__polling_task: Optional[asyncio.Task] = None
        self._logger = logging.getLogger(__name__)

    @property
    def running(self) -> bool:
        return self._running

    async def initialize(self) -> None:
        """Initializes the Updater & the associated :attr:`bot` by calling
        :meth:`telegram.Bot.initialize`.

        .. seealso::
            :meth:`shutdown`
        """
        if self._initialized:
            self._logger.debug("This Updater is already initialized.")
            return

        await self.bot.initialize()
        self._initialized = True

    async def shutdown(self) -> None:
        """
        Shutdown the Updater & the associated :attr:`bot` by calling :meth:`telegram.Bot.shutdown`.

        .. seealso::
            :meth:`initialize`

        Raises:
            :exc:`RuntimeError`: If the updater is still running.
        """
        if self.running:
            raise RuntimeError("This Updater is still running!")

        if not self._initialized:
            self._logger.debug("This Updater is already shut down. Returning.")
            return

        await self.bot.shutdown()
        self._initialized = False
        self._logger.debug("Shut down of Updater complete")

    async def __aenter__(self: _UpdaterType) -> _UpdaterType:
        """Simple context manager which initializes the Updater."""
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
        """Shutdown the Updater from the context manager."""
        # Make sure not to return `True` so that exceptions are not suppressed
        # https://docs.python.org/3/reference/datamodel.html?#object.__aexit__
        await self.shutdown()

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

        .. versionchanged:: 20.0
            Removed the ``clean`` argument in favor of :paramref:`drop_pending_updates`.

        Args:
            poll_interval (:obj:`float`, optional): Time to wait between polling updates from
                Telegram in seconds. Default is ``0.0``.
            timeout (:obj:`float`, optional): Passed to
                :paramref:`telegram.Bot.get_updates.timeout`. Defaults to ``10`` seconds.
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                :class:`telegram.ext.Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely (default)
                *   0 - no retries
                * > 0 - retry up to X times
            read_timeout (:obj:`float`, optional): Value to pass to
                :paramref:`telegram.Bot.get_updates.read_timeout`. Defaults to ``2``.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.Bot.get_updates.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.Bot.get_updates.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.Bot.get_updates.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            allowed_updates (List[:obj:`str`], optional): Passed to
                :meth:`telegram.Bot.get_updates`.
            drop_pending_updates (:obj:`bool`, optional): Whether to clean any pending updates on
                Telegram servers before actually starting to poll. Default is :obj:`False`.

                .. versionadded :: 13.4
            error_callback (Callable[[:exc:`telegram.error.TelegramError`], :obj:`None`], \
                optional): Callback to handle :exc:`telegram.error.TelegramError` s that occur
                while calling :meth:`telegram.Bot.get_updates` during polling. Defaults to
                :obj:`None`, in which case errors will be logged. Callback signature::

                    def callback(error: telegram.error.TelegramError)

                Note:
                    The :paramref:`error_callback` must *not* be a :term:`coroutine function`! If
                    asynchronous behavior of the callback is wanted, please schedule a task from
                    within the callback.

        Returns:
            :class:`asyncio.Queue`: The update queue that can be filled from the main thread.

        Raises:
            :exc:`RuntimeError`: If the updater is already running or was not initialized.

        """
        if error_callback and asyncio.iscoroutinefunction(error_callback):
            raise TypeError(
                "The `error_callback` must not be a coroutine function! Use an ordinary function "
                "instead. "
            )

        async with self.__lock:
            if self.running:
                raise RuntimeError("This Updater is already running!")
            if not self._initialized:
                raise RuntimeError("This Updater was not initialized via `Updater.initialize`!")

            self._running = True

            try:
                # Create & start tasks
                polling_ready = asyncio.Event()

                await self._start_polling(
                    poll_interval=poll_interval,
                    timeout=timeout,
                    read_timeout=read_timeout,
                    write_timeout=write_timeout,
                    connect_timeout=connect_timeout,
                    pool_timeout=pool_timeout,
                    bootstrap_retries=bootstrap_retries,
                    drop_pending_updates=drop_pending_updates,
                    allowed_updates=allowed_updates,
                    ready=polling_ready,
                    error_callback=error_callback,
                )

                self._logger.debug("Waiting for polling to start")
                await polling_ready.wait()
                self._logger.debug("Polling updates from Telegram started")

                return self.update_queue
            except Exception as exc:
                self._running = False
                raise exc

    async def _start_polling(
        self,
        poll_interval: float,
        timeout: int,
        read_timeout: float,
        write_timeout: ODVInput[float],
        connect_timeout: ODVInput[float],
        pool_timeout: ODVInput[float],
        bootstrap_retries: int,
        drop_pending_updates: Optional[bool],
        allowed_updates: Optional[List[str]],
        ready: asyncio.Event,
        error_callback: Optional[Callable[[TelegramError], None]],
    ) -> None:

        self._logger.debug("Updater started (polling)")

        # the bootstrapping phase does two things:
        # 1) make sure there is no webhook set
        # 2) apply drop_pending_updates
        await self._bootstrap(
            bootstrap_retries,
            drop_pending_updates=drop_pending_updates,
            webhook_url="",
            allowed_updates=None,
        )

        self._logger.debug("Bootstrap done")

        async def polling_action_cb() -> bool:
            try:
                updates = await self.bot.get_updates(
                    offset=self._last_update_id,
                    timeout=timeout,
                    read_timeout=read_timeout,
                    connect_timeout=connect_timeout,
                    write_timeout=write_timeout,
                    pool_timeout=pool_timeout,
                    allowed_updates=allowed_updates,
                )
            except asyncio.CancelledError as exc:
                # TODO: in py3.8+, CancelledError is a subclass of BaseException, so we can drop
                #  this clause when we drop py3.7
                raise exc
            except TelegramError as exc:
                # TelegramErrors should be processed by the network retry loop
                raise exc
            except Exception as exc:
                # Other exceptions should not. Let's log them for now.
                self._logger.critical(
                    "Something went wrong processing the data received from Telegram. "
                    "Received data was *not* processed!",
                    exc_info=exc,
                )
                return True

            if updates:
                if not self.running:
                    self._logger.critical(
                        "Updater stopped unexpectedly. Pulled updates will be ignored and again "
                        "on restart."
                    )
                else:
                    for update in updates:
                        await self.update_queue.put(update)
                    self._last_update_id = updates[-1].update_id + 1  # Add one to 'confirm' it

            return True  # Keep fetching updates & don't quit. Polls with poll_interval.

        def default_error_callback(exc: TelegramError) -> None:
            self._logger.exception("Exception happened while polling for updates.", exc_info=exc)

        # Start task that runs in background, pulls
        # updates from Telegram and inserts them in the update queue of the
        # Application.
        self.__polling_task = asyncio.create_task(
            self._network_loop_retry(
                action_cb=polling_action_cb,
                on_err_cb=error_callback or default_error_callback,
                description="getting Updates",
                interval=poll_interval,
            )
        )

        if ready is not None:
            ready.set()

    async def start_webhook(
        self,
        listen: str = "127.0.0.1",
        port: int = 80,
        url_path: str = "",
        cert: Union[str, Path] = None,
        key: Union[str, Path] = None,
        bootstrap_retries: int = 0,
        webhook_url: str = None,
        allowed_updates: List[str] = None,
        drop_pending_updates: bool = None,
        ip_address: str = None,
        max_connections: int = 40,
        secret_token: str = None,
    ) -> asyncio.Queue:
        """
        Starts a small http server to listen for updates via webhook. If :paramref:`cert`
        and :paramref:`key` are not provided, the webhook will be started directly on
        ``http://listen:port/url_path``, so SSL can be handled by another
        application. Else, the webhook will be started on
        ``https://listen:port/url_path``. Also calls :meth:`telegram.Bot.set_webhook` as required.

        Important:
            If you want to use this method, you must install PTB with the optional requirement
            ``webhooks``, i.e.

            .. code-block:: bash

               pip install python-telegram-bot[webhooks]

        .. seealso:: :wiki:`Webhooks`

        .. versionchanged:: 13.4
            :meth:`start_webhook` now *always* calls :meth:`telegram.Bot.set_webhook`, so pass
            ``webhook_url`` instead of calling ``updater.bot.set_webhook(webhook_url)`` manually.
        .. versionchanged:: 20.0
            * Removed the ``clean`` argument in favor of :paramref:`drop_pending_updates` and
              removed the deprecated argument ``force_event_loop``.
            * To use this method, PTB must be installed via
              ``pip install python-telegram-bot[webhooks]``.

        Args:
            listen (:obj:`str`, optional): IP-Address to listen on. Defaults to
                `127.0.0.1 <https://en.wikipedia.org/wiki/Localhost>`_.
            port (:obj:`int`, optional): Port the bot should be listening on. Must be one of
                :attr:`telegram.constants.SUPPORTED_WEBHOOK_PORTS` unless the bot is running
                behind a proxy. Defaults to ``80``.
            url_path (:obj:`str`, optional): Path inside url (http(s)://listen:port/<url_path>).
                Defaults to ``''``.
            cert (:class:`pathlib.Path` | :obj:`str`, optional): Path to the SSL certificate file.
            key (:class:`pathlib.Path` | :obj:`str`, optional): Path to the SSL key file.
            drop_pending_updates (:obj:`bool`, optional): Whether to clean any pending updates on
                Telegram servers before actually starting to poll. Default is :obj:`False`.

                .. versionadded :: 13.4
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                :class:`telegram.ext.Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely
                *   0 - no retries (default)
                * > 0 - retry up to X times
            webhook_url (:obj:`str`, optional): Explicitly specify the webhook url. Useful behind
                NAT, reverse proxy, etc. Default is derived from :paramref:`listen`,
                :paramref:`port`, :paramref:`url_path`, :paramref:`cert`, and :paramref:`key`.
            ip_address (:obj:`str`, optional): Passed to :meth:`telegram.Bot.set_webhook`.
                Defaults to :obj:`None`.

                .. versionadded :: 13.4
            allowed_updates (List[:obj:`str`], optional): Passed to
                :meth:`telegram.Bot.set_webhook`. Defaults to :obj:`None`.
            max_connections (:obj:`int`, optional): Passed to
                :meth:`telegram.Bot.set_webhook`. Defaults to ``40``.

                .. versionadded:: 13.6
            secret_token (:obj:`str`, optional): Passed to :meth:`telegram.Bot.set_webhook`.
                Defaults to :obj:`None`.

                When added, the web server started by this call will expect the token to be set in
                the ``X-Telegram-Bot-Api-Secret-Token`` header of an incoming request and will
                raise a :class:`http.HTTPStatus.FORBIDDEN <http.HTTPStatus>` error if either the
                header isn't set or it is set to a wrong token.

                .. versionadded:: 20.0
        Returns:
            :class:`queue.Queue`: The update queue that can be filled from the main thread.

        Raises:
            :exc:`RuntimeError`: If the updater is already running or was not initialized.
        """
        if not WEBHOOKS_AVAILABLE:
            raise RuntimeError(
                "To use `start_webhook`, PTB must be installed via `pip install "
                "python-telegram-bot[webhooks]`."
            )

        async with self.__lock:
            if self.running:
                raise RuntimeError("This Updater is already running!")
            if not self._initialized:
                raise RuntimeError("This Updater was not initialized via `Updater.initialize`!")

            self._running = True

            try:
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
                    secret_token=secret_token,
                )

                self._logger.debug("Waiting for webhook server to start")
                await webhook_ready.wait()
                self._logger.debug("Webhook server started")
            except Exception as exc:
                self._running = False
                raise exc

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
        secret_token: str = None,
    ) -> None:
        self._logger.debug("Updater thread started (webhook)")

        if not url_path.startswith("/"):
            url_path = f"/{url_path}"

        # Create Tornado app instance
        app = WebhookAppClass(url_path, self.bot, self.update_queue, secret_token)

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
                raise TelegramError("Invalid SSL Certificate") from exc
        else:
            ssl_ctx = None

        # Create and start server
        self._httpd = WebhookServer(listen, port, app, ssl_ctx)

        if not webhook_url:
            webhook_url = self._gen_webhook_url(
                protocol="https" if ssl_ctx else "http",
                listen=listen,
                port=port,
                url_path=url_path,
            )

        # We pass along the cert to the webhook if present.
        await self._bootstrap(
            # Passing a Path or string only works if the bot is running against a local bot API
            # server, so let's read the contents
            cert=Path(cert).read_bytes() if cert else None,
            max_retries=bootstrap_retries,
            drop_pending_updates=drop_pending_updates,
            webhook_url=webhook_url,
            allowed_updates=allowed_updates,
            ip_address=ip_address,
            max_connections=max_connections,
            secret_token=secret_token,
        )

        await self._httpd.serve_forever(ready=ready)

    @staticmethod
    def _gen_webhook_url(protocol: str, listen: str, port: int, url_path: str) -> str:
        # TODO: double check if this should be https in any case - the docs of start_webhook
        # say differently!
        return f"{protocol}://{listen}:{port}{url_path}"

    async def _network_loop_retry(
        self,
        action_cb: Callable[..., Coroutine],
        on_err_cb: Callable[[TelegramError], None],
        description: str,
        interval: float,
    ) -> None:
        """Perform a loop calling `action_cb`, retrying after network errors.

        Stop condition for loop: `self.running` evaluates :obj:`False` or return value of
        `action_cb` evaluates :obj:`False`.

        Args:
            action_cb (:term:`coroutine function`): Network oriented callback function to call.
            on_err_cb (:obj:`callable`): Callback to call when TelegramError is caught. Receives
                the exception object as a parameter.
            description (:obj:`str`): Description text to use for logs and exception raised.
            interval (:obj:`float` | :obj:`int`): Interval to sleep between each call to
                `action_cb`.

        """
        self._logger.debug("Start network loop retry %s", description)
        cur_interval = interval
        while self.running:
            try:
                try:
                    if not await action_cb():
                        break
                except RetryAfter as exc:
                    self._logger.info("%s", exc)
                    cur_interval = 0.5 + exc.retry_after
                except TimedOut as toe:
                    self._logger.debug("Timed out %s: %s", description, toe)
                    # If failure is due to timeout, we should retry asap.
                    cur_interval = 0
                except InvalidToken as pex:
                    self._logger.error("Invalid token; aborting")
                    raise pex
                except TelegramError as telegram_exc:
                    self._logger.error("Error while %s: %s", description, telegram_exc)
                    on_err_cb(telegram_exc)

                    # increase waiting times on subsequent errors up to 30secs
                    cur_interval = 1 if cur_interval == 0 else min(30, 1.5 * cur_interval)
                else:
                    cur_interval = interval

                if cur_interval:
                    await asyncio.sleep(cur_interval)

            except asyncio.CancelledError:
                self._logger.debug("Network loop retry %s was cancelled", description)
                break

    async def _bootstrap(
        self,
        max_retries: int,
        webhook_url: Optional[str],
        allowed_updates: Optional[List[str]],
        drop_pending_updates: bool = None,
        cert: Optional[bytes] = None,
        bootstrap_interval: float = 1,
        ip_address: str = None,
        max_connections: int = 40,
        secret_token: str = None,
    ) -> None:
        """Prepares the setup for fetching updates: delete or set the webhook and drop pending
        updates if appropriate. If there are unsuccessful attempts, this will retry as specified by
        :paramref:`max_retries`.
        """
        retries = 0

        async def bootstrap_del_webhook() -> bool:
            self._logger.debug("Deleting webhook")
            if drop_pending_updates:
                self._logger.debug("Dropping pending updates from Telegram server")
            await self.bot.delete_webhook(drop_pending_updates=drop_pending_updates)
            return False

        async def bootstrap_set_webhook() -> bool:
            self._logger.debug("Setting webhook")
            if drop_pending_updates:
                self._logger.debug("Dropping pending updates from Telegram server")
            await self.bot.set_webhook(
                url=webhook_url,
                certificate=cert,
                allowed_updates=allowed_updates,
                ip_address=ip_address,
                drop_pending_updates=drop_pending_updates,
                max_connections=max_connections,
                secret_token=secret_token,
            )
            return False

        def bootstrap_on_err_cb(exc: Exception) -> None:
            # We need this since retries is an immutable object otherwise and the changes
            # wouldn't propagate outside of thi function
            nonlocal retries

            if not isinstance(exc, InvalidToken) and (max_retries < 0 or retries < max_retries):
                retries += 1
                self._logger.warning(
                    "Failed bootstrap phase; try=%s max_retries=%s", retries, max_retries
                )
            else:
                self._logger.error("Failed bootstrap phase after %s retries (%s)", retries, exc)
                raise exc

        # Dropping pending updates from TG can be efficiently done with the drop_pending_updates
        # parameter of delete/start_webhook, even in the case of polling. Also, we want to make
        # sure that no webhook is configured in case of polling, so we just always call
        # delete_webhook for polling
        if drop_pending_updates or not webhook_url:
            await self._network_loop_retry(
                bootstrap_del_webhook,
                bootstrap_on_err_cb,
                "bootstrap del webhook",
                bootstrap_interval,
            )

            # Reset the retries counter for the next _network_loop_retry call
            retries = 0

        # Restore/set webhook settings, if needed. Again, we don't know ahead if a webhook is set,
        # so we set it anyhow.
        if webhook_url:
            await self._network_loop_retry(
                bootstrap_set_webhook,
                bootstrap_on_err_cb,
                "bootstrap set webhook",
                bootstrap_interval,
            )

    async def stop(self) -> None:
        """Stops the polling/webhook.

        .. seealso::
            :meth:`start_polling`, :meth:`start_webhook`

        Raises:
            :exc:`RuntimeError`: If the updater is not running.
        """
        async with self.__lock:
            if not self.running:
                raise RuntimeError("This Updater is not running!")

            self._logger.debug("Stopping Updater")

            self._running = False

            await self._stop_httpd()
            await self._stop_polling()

            self._logger.debug("Updater.stop() is complete")

    async def _stop_httpd(self) -> None:
        """Stops the Webhook server by calling ``WebhookServer.shutdown()``"""
        if self._httpd:
            self._logger.debug("Waiting for current webhook connection to be closed.")
            await self._httpd.shutdown()
            self._httpd = None

    async def _stop_polling(self) -> None:
        """Stops the polling task by awaiting it."""
        if self.__polling_task:
            self._logger.debug("Waiting background polling task to finish up.")
            self.__polling_task.cancel()

            try:
                await self.__polling_task
            except asyncio.CancelledError:
                # This only happens in rare edge-cases, e.g. when `stop()` is called directly
                # after start_polling(), but lets better be safe than sorry ...
                pass

            self.__polling_task = None
