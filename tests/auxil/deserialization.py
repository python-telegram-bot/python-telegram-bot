#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2026
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module provides a common base class for the deserialization tests of all subclasses of
:class:`telegram.TelegramObject`.

Every test class that subclasses :class:`DeserializationTestBase` gets the following tests
for free:

* ``test_de_json_dict_is_complete``: the ``de_json_dict`` fixture sets every argument of the
  class, so that the other tests really cover all of them.
* ``test_de_json_missing_optional_args``: ``de_json`` works when only the required arguments
  are passed and all optional arguments end up as ``None``/empty.
* ``test_de_json_api_kwargs``: unknown arguments (e.g. fields added to the Bot API in a newer
  version) are passed into ``api_kwargs`` (backward compatibility).
* ``test_de_json_missing_required_args``: ``de_json`` works when a required argument is
  missing (e.g. because Telegram stopped sending it), see
  ``TelegramObject.__DE_JSON_COMPAT__`` (forward compatibility).
* ``test_de_json_localization``: datetime fields are localized according to
  ``Defaults.tzinfo``.

The class-specific checks of the deserialized values have to be implemented in
``test_de_json``, which is an abstract method.

Note:
    pytest silently skips abstract classes. If a subclass forgets to implement
    ``test_de_json``, *none* of its tests are collected. ``tests/test_deserialization.py``
    contains a meta-test that catches this.
"""

import abc
import datetime as dtm
import inspect
from collections.abc import Iterator
from typing import Any, ClassVar

import pytest

from telegram import TelegramObject
from telegram._telegramobject import _DATETIME_FIELD
from telegram._utils.datetime import UTC
from telegram._utils.types import JSONDict

# A field name that is (hopefully) never going to be added to the Bot API
_UNKNOWN_FIELD = "ptb_unknown_test_field"


def _json_key(parameter_name: str) -> str:
    """Translate an ``__init__`` parameter name to the key used in the Bot API JSON."""
    return "from" if parameter_name == "from_user" else parameter_name


def _is_empty(value: object) -> bool:
    return value is None or value == ()


class DeserializationTestBase(abc.ABC):
    """Base class for the test classes of :class:`telegram.TelegramObject` subclasses.

    Subclasses must

    * set :attr:`de_json_class` to the class under test,
    * provide a fixture named ``de_json_dict`` that returns the JSON data for the class
      with *all* arguments (required and optional) set to non-``None`` values,
    * implement :meth:`test_de_json`, which checks the class specific values.

    The generic tests can be overridden in a subclass if a class really needs special
    treatment. Please add a comment explaining why if you do so.
    """

    de_json_class: ClassVar[type[TelegramObject]]

    @pytest.fixture
    def de_json_dict(self) -> JSONDict:
        raise NotImplementedError(
            f"{type(self).__name__} must define a `de_json_dict` fixture returning the JSON "
            f"data of {self.de_json_class.__name__} with all arguments set."
        )

    @abc.abstractmethod
    def test_de_json(self, *args: Any, **kwargs: Any) -> None:
        """Deserialize ``de_json_dict`` and check every attribute of the resulting object."""

    # ----------------------------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------------------------
    @classmethod
    def _parameters(cls) -> Iterator[inspect.Parameter]:
        for name, param in inspect.signature(cls.de_json_class).parameters.items():
            if name == "api_kwargs" or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            yield param

    @classmethod
    def _required_parameters(cls) -> list[str]:
        return [p.name for p in cls._parameters() if p.default is inspect.Parameter.empty]

    @classmethod
    def _optional_parameters(cls) -> list[inspect.Parameter]:
        return [p for p in cls._parameters() if p.default is not inspect.Parameter.empty]

    @classmethod
    def _datetime_parameters(cls) -> list[str]:
        if "__DE_JSON_PLAN__" not in cls.de_json_class.__dict__:
            cls.de_json_class._build_plan()
        plan = cls.de_json_class.__DE_JSON_PLAN__
        return [name for name, target in plan.items() if target is _DATETIME_FIELD]

    # ----------------------------------------------------------------------------------------
    # Generic tests
    # ----------------------------------------------------------------------------------------
    def test_de_json_dict_is_complete(self, de_json_dict):
        """Make sure that the other tests actually test all arguments."""
        expected = {_json_key(p.name) for p in self._parameters()}
        missing = expected - de_json_dict.keys()
        assert not missing, f"`de_json_dict` is missing the arguments {sorted(missing)}"
        none_values = sorted(key for key in expected if de_json_dict[key] is None)
        assert not none_values, f"`de_json_dict` has `None` values for {none_values}"

    def test_de_json_missing_optional_args(self, offline_bot, de_json_dict):
        json_dict = {
            key: de_json_dict[key]
            for key in map(_json_key, self._required_parameters())
            if key in de_json_dict
        }
        obj = self.de_json_class.de_json(json_dict, offline_bot)

        assert isinstance(obj, self.de_json_class)
        assert obj.api_kwargs == {}
        assert obj.get_bot() is offline_bot
        for param in self._optional_parameters():
            if not hasattr(obj, param.name):
                continue
            value = getattr(obj, param.name)
            if param.default is None:
                assert _is_empty(value), f"{param.name!r} should be empty but is {value!r}"
            else:
                assert value == param.default, f"{param.name!r} should be {param.default!r}"

    def test_de_json_api_kwargs(self, offline_bot, de_json_dict):
        """Telegram may add new fields at any time, before PTB supports them."""
        extra = {_UNKNOWN_FIELD: {"some": ["value"]}}
        obj = self.de_json_class.de_json(de_json_dict | extra, offline_bot)
        reference = self.de_json_class.de_json(de_json_dict, offline_bot)

        assert isinstance(obj, self.de_json_class)
        assert obj.api_kwargs == extra
        assert obj.to_dict() == reference.to_dict() | extra

    def test_de_json_missing_required_args(self, offline_bot, de_json_dict):
        """Telegram may stop sending fields that are required in PTB. Deserialization must not
        fail in that case. See ``TelegramObject.__DE_JSON_COMPAT__``."""
        for name in self._required_parameters():
            json_dict = de_json_dict.copy()
            json_dict.pop(_json_key(name), None)

            obj = self.de_json_class.de_json(json_dict, offline_bot)

            assert isinstance(obj, self.de_json_class), f"failed without {name!r}"
            assert obj.api_kwargs == {}, f"unexpected api_kwargs without {name!r}"
            if hasattr(obj, name):
                value = getattr(obj, name)
                assert _is_empty(value), f"{name!r} should be empty but is {value!r}"

    def test_de_json_localization(self, tz_bot, offline_bot, raw_bot, de_json_dict):
        datetime_parameters = self._datetime_parameters()
        if not datetime_parameters:
            # Nothing to localize. We don't skip here to avoid hundreds of skipped tests in the
            # test report.
            return

        obj_raw = self.de_json_class.de_json(de_json_dict, raw_bot)
        obj_bot = self.de_json_class.de_json(de_json_dict, offline_bot)
        obj_tz = self.de_json_class.de_json(de_json_dict, tz_bot)

        for name in datetime_parameters:
            raw_value = getattr(obj_raw, name)
            bot_value = getattr(obj_bot, name)
            tz_value = getattr(obj_tz, name)
            assert isinstance(tz_value, dtm.datetime), f"{name!r} is not a datetime"

            assert raw_value.tzinfo == UTC, name
            assert bot_value.tzinfo == UTC, name
            # comparing utcoffsets because comparing tzinfo objects is unpredictable
            expected_offset = tz_bot.defaults.tzinfo.utcoffset(tz_value.replace(tzinfo=None))
            assert tz_value.utcoffset() == expected_offset, name
