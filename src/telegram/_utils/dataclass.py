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
from collections.abc import Callable, Sequence
from dataclasses import MISSING, dataclass, field, is_dataclass
from typing import Any, TypeVar, get_args, get_origin

from typing_extensions import dataclass_transform

from telegram._utils.de_json import unwrap_optional

_T = TypeVar("_T")
CONVERTER_KEY = object()
"""Special marker indicating that an entry was deleted."""
ALIAS_KEY = object()
"""Special marker indicating that an entry was deleted."""


def to_sequence_annotation(annotation: object) -> object:
    item_type = get_args(annotation)[0]

    if get_origin(item_type) is tuple:
        item_type = to_sequence_annotation(item_type)

    return Sequence[item_type]


def process_init(cls: type[_T]) -> type[_T]:
    """Processes the ``__init__`` of a class transformed with :func:`dataclasses.dataclass`.

    Args:
        cls (:obj:`type`): A class transformed with :func:`dataclasses.dataclass`.

    The function updates the exposed signature of the provided class' ``__init__``:

    1) Replaces field names with their aliases.

    2) Replaces the annotations of fields with converters with the input annotations accepted by
       those converters.

           - Fields stored as tuples expose the corresponding :class:`collections.abc.Sequence`
             annotation.

           - Parameter required/optional status is calculated based on :param:`tg_field.default`

    It also provides runtime support for :param:`tg_field.alias`

    Note:
        The aliased name and converter function are assumed to exist under the field metadata with
        the sentinel keys `ALIAS_KEY`, `CONVERTER_KEY` repectively

    Returns:
        :obj:`type`:
            `cls` *Modified In Place*

    Raises:
        TypeError: If :paramref:`cls` is not a dataclass.
    """
    if not is_dataclass(cls):
        raise TypeError(f"{cls!r} is not a dataclass")

    fields = {dataclass_field.name: dataclass_field for dataclass_field in dataclasses.fields(cls)}
    has_aliases = any(
        dataclass_field.init and dataclass_field.metadata.get(ALIAS_KEY) is not None
        for dataclass_field in fields.values()
    )

    generated_init = cls.__init__
    generated_signature = inspect.signature(generated_init)

    @functools.wraps(generated_init)
    def aliased_init(self: object, *args: object, **kwargs: object) -> None:
        for field_name, dataclass_field in fields.items():
            alias = dataclass_field.metadata.get(ALIAS_KEY)

            if not dataclass_field.init or dataclass_field.metadata.get(ALIAS_KEY) is None:
                continue

            # Reject kwargs keys using the raw (unaliased) field name
            if field_name in kwargs:
                raise TypeError(
                    f"{cls.__name__}() got an unexpected keyword argument {field_name!r}"
                )

            # Swap the kwargs key from alias to field_name to satisfy runtime signature
            # of generated_init
            if alias in kwargs:
                kwargs[field_name] = kwargs.pop(alias)

        generated_init(self, *args, **kwargs)

    # Now we update parameter names (if aliased) and annotations (if a converter is present)
    # This is neccessary because TO._build_plan expects field names to match what
    # Telegram API returns
    parameters = []
    for param in generated_signature.parameters.values():
        dataclass_field = fields.get(param.name)

        if dataclass_field is None:
            parameters.append(param)
            continue

        alias = dataclass_field.metadata.get(ALIAS_KEY)
        converter = dataclass_field.metadata.get(CONVERTER_KEY)
        annotation = param.annotation

        if converter is not None:
            field_annotation = unwrap_optional(param.annotation)

            if get_origin(field_annotation) is tuple:
                annotation = to_sequence_annotation(field_annotation)

                if dataclass_field.default is not MISSING:
                    annotation |= None
            else:
                converter_param = next(iter(inspect.signature(converter).parameters.values()))
                annotation = converter_param.annotation

        parameters.append(
            param.replace(
                name=alias or param.name,
                annotation=annotation,
            )
        )

    signature = generated_signature.replace(parameters=parameters)

    if not has_aliases:
        generated_init.__signature__ = signature  # type: ignore[attr-defined]
        return cls

    aliased_init.__signature__ = signature  # type: ignore[attr-defined]
    cls.__init__ = aliased_init  # type: ignore[method-assign]
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
    field_metadata: dict[Any, Any] = {}

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
        metadata=field_metadata or None,
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
        transformed_cls = process_init(transformed_cls)

        if eq:
            compare_fields = tuple(
                dataclass_field.name
                for dataclass_field in dataclasses.fields(transformed_cls)
                if dataclass_field.compare
            )

            def __hash__(self: object) -> int:
                values = tuple(getattr(self, name) for name in compare_fields)
                return hash((self.__class__, values))

            transformed_cls.__hash__ = __hash__  # type: ignore[method-assign]

        return transformed_cls

    return decorate
