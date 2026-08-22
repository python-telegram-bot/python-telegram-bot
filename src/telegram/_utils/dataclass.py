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

import dataclasses
import functools
import inspect
from collections.abc import Callable
from dataclasses import MISSING, dataclass, field
from typing import Any, TypeVar

from typing_extensions import dataclass_transform

_T = TypeVar("_T")
CONVERTER_KEY = object()
ALIAS_KEY = object()


def _apply_aliases(cls: type[_T]) -> type[_T]:
    """Provides runtime support for the `alias` parameter of a field specifier (e.g tg_field).

    Args:
        cls (:obj:`type`): A class transformed with `dataclasses.dataclass`

    The function does two things to the provided class generated `__init__`:

    1) Wraps the generated __init__ with a generic one (*args: object, **kwargs: object) that
    rejects having the unalised field_name in kwargs.

    2) Updates the signature of the wrapper __init__ to replace parameter names from raw
    to aliased.

    Note:
        The aliased name is assumed to exist under the field metadata with
        the sentinel key `ALIAS_KEY`

    Returns:
        :obj:`type`:
            `cls` *Modified In Place*
    """
    aliases = {
        dataclass_field.name: alias
        for dataclass_field in dataclasses.fields(cls)
        if dataclass_field.init and (alias := dataclass_field.metadata.get(ALIAS_KEY)) is not None
    }

    if not aliases:
        return cls

    generated_init = cls.__init__
    generated_signature = inspect.signature(generated_init)

    @functools.wraps(generated_init)
    def aliased_init(self: object, *args: object, **kwargs: object) -> None:
        for field_name, alias in aliases.items():
            # 1.1) Reject kwargs keys using the raw (unaliased) field name
            if field_name in kwargs:
                raise TypeError(
                    f"{cls.__name__}() got an unexpected keyword argument {field_name!r}"
                )

            # 1.2) Swap the kwargs key from alias to field_name to satisfy runtime signature
            # of generated_init
            if alias in kwargs:
                kwargs[field_name] = kwargs.pop(alias)

        generated_init(self, *args, **kwargs)

    # 2) Now and since inspect.signature(generated_init/aliased_init) would still return parameters
    # with raw field_names instead of aliased ones, we update those parameters in the signature
    # This is neccessary because TO._build_plan expect field names to match what
    # Telegram API returns
    parameters = [
        parameter.replace(name=aliases.get(parameter.name) or parameter.name)
        for parameter in generated_signature.parameters.values()
    ]
    signature = generated_signature.replace(parameters=parameters)

    aliased_init.__signature__ = signature
    cls.__init__ = aliased_init
    return cls


def tg_field(
    *,
    default: Any = MISSING,
    default_factory: Any = MISSING,
    init: bool = True,
    compare: bool = False,
    kw_only: Any = MISSING,
    converter: Callable[[Any], Any] | None = None,
    alias: str | None = None,
) -> Any:
    field_metadata = None

    if any((converter, alias)):
        field_metadata = {}

    if converter is not None:
        field_metadata[CONVERTER_KEY] = converter

    if alias is not None:
        field_metadata[ALIAS_KEY] = alias

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
    def decorate(cls: type[_T]) -> type[_T]:
        transformed_cls = dataclass(
            cls,
            frozen=True,
            slots=True,
            repr=False,
            match_args=False,
            eq=eq,
        )
        return _apply_aliases(transformed_cls)

    return decorate
