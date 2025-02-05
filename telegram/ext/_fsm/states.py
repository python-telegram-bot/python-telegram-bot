"""This Module contains implementations of State classes for Finite State Machines"""

import abc
import contextlib
from typing import ClassVar, Optional
from uuid import uuid4


class State(abc.ABC):
    __knows_uids: ClassVar[set[str]] = set()
    __not_cache: ClassVar[dict[str, "_NOTState"]] = {}
    __or_cache: ClassVar[dict[tuple[str, str], "_ORState"]] = {}
    __and_cache: ClassVar[dict[tuple[str, str], "_ANDState"]] = {}
    __xor_cache: ClassVar[dict[tuple[str, str], "_XORState"]] = {}

    IDLE: "State"
    """Default State for all Finite State Machines"""
    ANY: "State"
    """Special State that matches any other State. Useful to define fallback behavior.
    *Not* supported in ``set_state`` method of FSMs.
    """

    def __init__(self, uid: Optional[str] = None):
        effective_uid = uid or uuid4().hex
        if effective_uid in self.__knows_uids:
            raise ValueError(f"Duplicate UID: {effective_uid} already registered")
        self._uid = effective_uid
        self.__knows_uids.add(effective_uid)

    def __invert__(self) -> "_NOTState":
        with contextlib.suppress(KeyError):
            return self.__not_cache[self.uid]
        return self.__not_cache.setdefault(self.uid, _NOTState(self))

    def __or__(self, other: "State") -> "_ORState":
        key = (self.uid, other.uid)
        with contextlib.suppress(KeyError):
            return self.__or_cache[key]
        return self.__or_cache.setdefault(key, _ORState(self, other))

    def __and__(self, other: "State") -> "_ANDState":
        key = (self.uid, other.uid)
        with contextlib.suppress(KeyError):
            return self.__and_cache[key]
        return self.__and_cache.setdefault(key, _ANDState(self, other))

    def __xor__(self, other: "State") -> "_XORState":
        key = (self.uid, other.uid)
        with contextlib.suppress(KeyError):
            return self.__xor_cache[key]
        return self.__xor_cache.setdefault(key, _XORState(self, other))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.uid}>"

    def __str__(self) -> str:
        return self.uid

    @property
    def uid(self) -> str:
        return self._uid

    def matches(self, state: "State") -> bool:
        if isinstance(state, (_NOTState, _ANDState, _ORState, _XORState)):
            return state.matches(self)
        return self.uid == state.uid


class _AnyState(State):
    def matches(self, state: "State") -> bool:  # noqa: ARG002
        return True


State.IDLE = State("IDLE")
State.ANY = _AnyState("ANY")


class _XORState(State):
    def __init__(self, state_one: State, state_two: State):
        super().__init__(uid=f"({state_one.uid})^({state_two.uid})")
        self._state_one = state_one
        self._state_two = state_two

    def matches(self, state: "State") -> bool:
        return self._state_one.matches(state) ^ self._state_two.matches(state)


class _ORState(State):
    def __init__(self, state_one: State, state_two: State):
        super().__init__(uid=f"({state_one.uid})|({state_two.uid})")
        self._state_one = state_one
        self._state_two = state_two

    def matches(self, state: "State") -> bool:
        return self._state_one.matches(state) or self._state_two.matches(state)


class _ANDState(State):
    def __init__(self, state_one: State, state_two: State):
        super().__init__(uid=f"({state_one.uid})&({state_two.uid})")
        self._state_one = state_one
        self._state_two = state_two

    def matches(self, state: "State") -> bool:
        return self._state_one.matches(state) and self._state_two.matches(state)


class _NOTState(State):
    def __init__(self, state: State):
        super().__init__(uid=f"!({state.uid})")
        self._state = state

    def matches(self, state: "State") -> bool:
        return not self._state.matches(state)
