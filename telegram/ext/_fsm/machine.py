"""This Module contains the FiniteStateMachine class and the built-in subclass SingleStateMachine.
"""

import abc
import asyncio
import contextlib
import datetime as dtm
import logging
import time
import weakref
from collections import defaultdict, deque
from collections.abc import AsyncIterator, Hashable, Mapping, MutableSequence, Sequence
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Generic, Literal, Optional, TypeVar, Union, overload

from telegram.ext._fsm.states import State
from telegram.ext._utils.types import JobCallback

if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from telegram.ext import JobQueue

_KT = TypeVar("_KT", bound=Hashable)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class StateInfo(Generic[_KT]):
    def __init__(self: "StateInfo[_KT]", key: _KT, state: State, version: int) -> None:
        self.key: _KT = key
        self.state: State = state
        self.version: int = version


class FiniteStateMachine(abc.ABC, Generic[_KT]):
    def __init__(self) -> None:
        self._locks: MutableMapping[_KT, asyncio.Lock] = weakref.WeakValueDictionary()

        # There is likely litte benefit for a user to customize how exactly the states are stored
        # and accessed. So we make this private and only provide a read-only view.
        self.__states: dict[_KT, tuple[State, int]] = defaultdict(
            lambda: (State.IDLE, time.perf_counter_ns())
        )
        self._states = MappingProxyType(self.__states)

        self.__job_queue: Optional[weakref.ReferenceType[JobQueue]] = None
        self.__history: Mapping[_KT, MutableSequence[State]] = defaultdict(
            lambda: deque(maxlen=10)
        )

    @property
    def states(self) -> Mapping[_KT, tuple[State, int]]:
        return self._states

    def store_state_history(self, key: _KT, state: State) -> None:
        # Making this public so that users can override if they want to customize the history
        # E.g., they could want to store more/fewer states, also depending on the key
        self.__history[key].append(state)

    def get_state_history(self, key: _KT) -> Sequence[State]:
        return list(self.__history[key])

    def get_lock(self, key: _KT) -> asyncio.Lock:
        """Returns a lock that is unique for this key at runtime.
        It can be used to prevent concurrent access to resources associated to this key.
        """
        return self._locks.setdefault(key, asyncio.Lock())

    @abc.abstractmethod
    def get_state_info(self, update: object) -> StateInfo[_KT]:
        """Returns exactly one active state for the update.
        If more than one stored key applies to the update, one must be chosen.
        It's recommended to select the most specific one.

        Example:
            The state of a chat, a user or a user in a specific chat could be tracked.
            For a message in that chat, the state of the user in that chat should be returned if
            available. Otherwise, the state of the chat should be returned.

        Important:
            This must be an atomic operation and not e.g. wait for a lock.
            Instead, if necessary, return a special state indicating that the key is currently
            busy.
        """

    def _do_set_state(
        self, key: _KT, state: State, version: Optional[int] = None
    ) -> StateInfo[_KT]:
        """Protected method to set the state for the specified key.

        The version can be optionally used for optimistic locking. If the version does not match
        the current version, the state should not be updated.

        Important:
            This should be used exclusively by methods of this class and subclasses.
            It should *not* be called directly by users of this class!
        """
        _LOGGER.debug("Setting %s state to %s", key, state)
        if state is State.ANY:
            raise ValueError("State.ANY is not supported in set_state")

        if version and version != self._states.get(key, (None, None))[1]:
            raise ValueError("Optimistic locking failed. Not updating state.")

        if jq := self._get_job_queue(raise_exception=False):
            # This is a rather tight coupling between FSM and JobQueue
            # Not sure if we like that. Makes it even harder to replace JobQueue
            # (or the JQ implementation) with something else.
            # The upside is that we don't need to maintain any additional internal state
            # for the jobs and persistence is handled by the JobQueue.
            cancel_jobs = jq.jobs(pattern=str(hash(key)))
            for job in cancel_jobs:
                _LOGGER.debug("Cancelling timeout job %s", job)
                job.schedule_removal()

        # important to use time.perf_counter_ns() here, as time_ns() is not monotonic
        self.__states[key] = (state, time.perf_counter_ns())
        # Doing this *after* do_set_state so that any exceptions are raised before the history
        # is updated
        self.store_state_history(key, state)
        return StateInfo(key, state, self._states[key][1])

    async def set_state(self, key: _KT, state: State, version: Optional[int] = None) -> None:
        """Store the state for the specified key."""
        async with self.get_lock(key):
            self._do_set_state(key, state, version)

    def set_state_nowait(self, key: _KT, state: State, version: Optional[int] = None) -> None:
        """Store the state for the specified key without waiting for a lock."""
        if self.get_lock(key).locked():
            raise asyncio.InvalidStateError("Lock is locked")
        self._do_set_state(key, state, version)

    @contextlib.asynccontextmanager
    async def as_state(self, key: _KT, state: State) -> AsyncIterator[None]:
        """Context manager to set the state for the specified key and reset it afterwards."""
        async with self.get_lock(key):
            current_state, current_version = self.states[key]
            new_version = self._do_set_state(key, state, current_version).version
            try:
                yield
            finally:
                self._do_set_state(key, current_state, new_version)

    @staticmethod
    def _build_job_name(keys: Sequence[_KT]) -> str:
        return f"FSM_Job_{'_'.join(str(hash(k)) for k in keys)}"

    def set_job_queue(self, job_queue: "JobQueue") -> None:
        self.__job_queue = weakref.ref(job_queue)

    @overload
    def _get_job_queue(self, raise_exception: Literal[False]) -> Optional["JobQueue"]: ...

    @overload
    def _get_job_queue(self) -> "JobQueue": ...

    def _get_job_queue(self, raise_exception: bool = True) -> Optional["JobQueue"]:
        if self.__job_queue is None:
            if raise_exception:
                raise RuntimeError("JobQueue not set")
            return None
        job_queue = self.__job_queue()
        if job_queue is None:
            if raise_exception:
                raise RuntimeError("JobQueue was garbage collected")
            return None
        return job_queue

    def schedule_timeout(
        self,
        callback: JobCallback,
        when: Union[float, dtm.timedelta, dtm.datetime, dtm.time],
        cancel_keys: Optional[Sequence[_KT]] = None,
        job_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        """Schedule a timeout job. This is a thin wrapper around JobQueue.run_once.
        The callback will have to take care of resetting any state if necessary.
        Pass cancel_keys to automatically cancel the job when a new state is set for any of the
        keys.
        """
        job_kwargs = job_kwargs or {}
        if cancel_keys:
            if "name" in job_kwargs:
                raise ValueError("job_kwargs must not contain a 'name' key")
            job_kwargs["name"] = self._build_job_name(cancel_keys)
        self._get_job_queue().run_once(callback, when, **job_kwargs)
        _LOGGER.debug(
            "Scheduled timeout. Will be cancelled when a new set state is for either of: %s",
            cancel_keys or [],
        )


class SingleStateMachine(FiniteStateMachine[None]):
    def get_state_info(self, update: object) -> StateInfo[None]:  # noqa: ARG002
        return StateInfo(None, State.IDLE, 0)

    def do_set_state(self, key: None, state: State) -> None:
        pass
