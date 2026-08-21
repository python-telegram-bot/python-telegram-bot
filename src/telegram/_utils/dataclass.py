#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""Helpers for Implementing Telegram Objects as dataclasses.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""

from collections.abc import Callable
from dataclasses import MISSING, dataclass, field
from typing import Any, TypeVar

from typing_extensions import dataclass_transform

_T = TypeVar("_T")
CONVERTER_KEY = object()


def tg_field(
    *,
    default: Any = MISSING,
    default_factory: Any = MISSING,
    init: bool = True,
    compare: bool = False,
    kw_only: Any = MISSING,
    converter: Callable[[Any], Any] | None = None,
) -> Any:
    field_metadata = None

    if converter is not None:
        field_metadata = {}
        field_metadata[CONVERTER_KEY] = converter

    return field(  # pylint: disable=invalid-field-call
        repr=False,
        compare=compare,
        init=init,
        default=default,
        default_factory=default_factory,
        metadata=field_metadata,
        kw_only=kw_only,
    )


@dataclass_transform(
    eq_default=True,
    order_default=False,
    kw_only_default=False,
    frozen_default=True,
    field_specifiers=(tg_field,),
)
def tg_dataclass(
    *,
    eq: bool = True,
) -> Callable[[type[_T]], type[_T]]:
    return dataclass(
        frozen=True,
        slots=True,
        repr=False,
        match_args=False,
        eq=eq,
    )
