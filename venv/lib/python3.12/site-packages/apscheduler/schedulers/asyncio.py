from __future__ import absolute_import
from functools import wraps, partial

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.util import maybe_ref

try:
    import asyncio
except ImportError:  # pragma: nocover
    try:
        import trollius as asyncio
    except ImportError:
        raise ImportError(
            'AsyncIOScheduler requires either Python 3.4 or the asyncio package installed')


def run_in_event_loop(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        wrapped = partial(func, self, *args, **kwargs)
        self._eventloop.call_soon_threadsafe(wrapped)
    return wrapper


class AsyncIOScheduler(BaseScheduler):
    """
    A scheduler that runs on an asyncio (:pep:`3156`) event loop.

    The default executor can run jobs based on native coroutines (``async def``).

    Extra options:

    ============== =============================================================
    ``event_loop`` AsyncIO event loop to use (defaults to the global event loop)
    ============== =============================================================
    """

    _eventloop = None
    _timeout = None

    @run_in_event_loop
    def shutdown(self, wait=True):
        super(AsyncIOScheduler, self).shutdown(wait)
        self._stop_timer()

    def _configure(self, config):
        self._eventloop = maybe_ref(config.pop('event_loop', None)) or asyncio.get_event_loop()
        super(AsyncIOScheduler, self)._configure(config)

    def _start_timer(self, wait_seconds):
        self._stop_timer()
        if wait_seconds is not None:
            self._timeout = self._eventloop.call_later(wait_seconds, self.wakeup)

    def _stop_timer(self):
        if self._timeout:
            self._timeout.cancel()
            del self._timeout

    @run_in_event_loop
    def wakeup(self):
        self._stop_timer()
        wait_seconds = self._process_jobs()
        self._start_timer(wait_seconds)

    def _create_default_executor(self):
        from apscheduler.executors.asyncio import AsyncIOExecutor
        return AsyncIOExecutor()
