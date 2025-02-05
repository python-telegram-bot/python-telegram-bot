"""This Module contains the FiniteStateMachine class and the built-in subclass SingleStateMachine.
"""

import abc
import asyncio
import datetime as dtm
import logging
import weakref
from collections.abc import Hashable, Sequence
from typing import TYPE_CHECKING, Any, Generic, Literal, Optional, TypeVar, Union, overload

from telegram.ext._fsm.states import State
from telegram.ext._utils.types import JobCallback

if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from telegram.ext import JobQueue

_KT = TypeVar("_KT", bound=Hashable)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class FiniteStateMachine(abc.ABC, Generic[_KT]):
    def __init__(self) -> None:
        self._semaphores: MutableMapping[_KT, asyncio.BoundedSemaphore] = (
            weakref.WeakValueDictionary()
        )
        self.__job_queue: Optional[weakref.ReferenceType[JobQueue]] = None

    def get_semaphore(self, key: _KT) -> asyncio.BoundedSemaphore:
        """Returns a semaphore that is unique for this key at runtime.
        It can be used to prevent concurrent access to resources associated to this key.
        """
        return self._semaphores.setdefault(key, asyncio.BoundedSemaphore(1))

    @abc.abstractmethod
    def get_active_key_state(self, update: object) -> tuple[Hashable, State]:
        """Returns exactly one active state for the update.
        If more than one stored key applies to the update, one must chosen.
        It's recommended to select the most specific one.

        Example:
            The state of a chat, a user or a user in a specific chat could be tracked.
            For a message in that chat, the state of the user in that chat should be returned if
            available. Otherwise, the state of the chat should be returned.

        Important:
            This must be an atomic operation and not e.g. wait for a semaphore.
            Instead, if necessary, return a special state indicating that the key is currently
            busy.
        """

    @abc.abstractmethod
    def do_set_state(self, key: _KT, state: State) -> None:
        """Store the state for the specified key.
        If the state is ``FSMState.IDLE``, it's recommended to drop the key from the in-memory
        data.

        Warning:
            This method should not be directly accessed by user code.
            It is intended for internal use in this class only.
            Instead, use :meth:`set_state`
        """

    def _do_set_state(self, key: _KT, state: State) -> None:
        if state is State.ANY:
            raise ValueError("State.ANY is not supported in set_state")

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

        return self.do_set_state(key, state)

    async def set_state(self, key: _KT, state: State) -> None:
        """Store the state for the specified key."""
        async with self.get_semaphore(key):
            self._do_set_state(key, state)

    def set_state_nowait(self, key: _KT, state: State) -> None:
        """Store the state for the specified key without waiting for a semaphore."""
        if self.get_semaphore(key).locked():
            raise asyncio.InvalidStateError("Semaphore is locked")
        self._do_set_state(key, state)

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
    def get_active_key_state(self, update: object) -> tuple[None, State]:  # noqa: ARG002
        return None, State.IDLE

    def do_set_state(self, key: None, state: State) -> None:
        pass
