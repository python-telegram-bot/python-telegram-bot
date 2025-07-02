from __future__ import absolute_import

from apscheduler.schedulers.base import BaseScheduler

try:
    from PyQt5.QtCore import QObject, QTimer
except (ImportError, RuntimeError):  # pragma: nocover
    try:
        from PyQt4.QtCore import QObject, QTimer
    except ImportError:
        try:
            from PySide.QtCore import QObject, QTimer  # noqa
        except ImportError:
            raise ImportError('QtScheduler requires either PyQt5, PyQt4 or PySide installed')


class QtScheduler(BaseScheduler):
    """A scheduler that runs in a Qt event loop."""

    _timer = None

    def shutdown(self, *args, **kwargs):
        super(QtScheduler, self).shutdown(*args, **kwargs)
        self._stop_timer()

    def _start_timer(self, wait_seconds):
        self._stop_timer()
        if wait_seconds is not None:
            wait_time = min(wait_seconds * 1000, 2147483647)
            self._timer = QTimer.singleShot(wait_time, self._process_jobs)

    def _stop_timer(self):
        if self._timer:
            if self._timer.isActive():
                self._timer.stop()
            del self._timer

    def wakeup(self):
        self._start_timer(0)

    def _process_jobs(self):
        wait_seconds = super(QtScheduler, self)._process_jobs()
        self._start_timer(wait_seconds)
