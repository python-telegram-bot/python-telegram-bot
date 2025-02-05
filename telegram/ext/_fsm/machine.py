"""This Module contains the FiniteStateMachine class and the built-in subclass SingleStateMachine.
"""

import abc
import asyncio
import collections
import weakref
from typing import TYPE_CHECKING, Generic, TypeVar

from telegram.ext._fsm.states import State

if TYPE_CHECKING:
    from collections.abc import MutableMapping

_KT = TypeVar("_KT", bound=collections.abc.Hashable)


class FiniteStateMachine(abc.ABC, Generic[_KT]):
    def __init__(self) -> None:
        self._semaphores: MutableMapping[_KT, asyncio.BoundedSemaphore] = (
            weakref.WeakValueDictionary()
        )

    def get_semaphore(self, key: _KT) -> asyncio.BoundedSemaphore:
        """Returns a semaphore that is unique for this key at runtime.
        It can be used to prevent concurrent access to resources associated to this key.
        """
        return self._semaphores.setdefault(key, asyncio.BoundedSemaphore(1))

    @abc.abstractmethod
    def get_active_key_state(self, update: object) -> tuple[collections.abc.Hashable, State]:
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


class SingleStateMachine(FiniteStateMachine[None]):
    def get_active_key_state(self, update: object) -> tuple[None, State]:  # noqa: ARG002
        return None, State.IDLE

    def do_set_state(self, key: None, state: State) -> None:
        pass
