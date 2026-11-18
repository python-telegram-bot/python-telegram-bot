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
from enum import Enum
from types import GenericAlias
from typing import TYPE_CHECKING, Any, TypeVar, get_args, get_origin

from typing_extensions import dataclass_transform

from telegram._utils import enum as _enum
from telegram._utils.de_json import unwrap_optional

if TYPE_CHECKING:
    from telegram import TelegramObject

_T = TypeVar("_T")
TelegramObj = TypeVar("TelegramObj", bound="TelegramObject")

CONVERTER_KEY = object()
"""Special marker for storing the `converter` function."""
ALIAS_KEY = object()
"""Special marker for storing the field's alias (i.e. its desired `__init__` name)."""
ENUM_KEY = object()
"""Special marker indicating whether or not this field gets converted to an enum member."""


def to_sequence_annotation(annotation: object) -> GenericAlias:
    """Given a `tuple[T, ...]` returns a corresponding `Sequence[T]` recursively on `T`.
    Recursion is need to support cases such as (`InlineKeyboardMarkup.inline_keyboard`, ..etc)

    `Sequence[T]` is returened so that :meth:`TelegramObject._build_plan` can build the appropriate
    transformer, see its docstring.
    """
    item_type = get_args(annotation)[0]

    if get_origin(item_type) is tuple:
        item_type = to_sequence_annotation(item_type)

    return GenericAlias(Sequence, item_type)


def process_init(cls: type[_T]) -> type[_T]:
    """Processes the ``__init__`` of a class transformed with :func:`dataclasses.dataclass`.

    Args:
        cls (:obj:`type`): A class transformed with :func:`dataclasses.dataclass`.

    The function updates the exposed signature and annotation of the provided class' ``__init__``.
    It:

    1) Replaces field names with their aliases.

    2) Replaces type annotations of fields with converters with the annotation of the first
        converter parameter. With these special cases:

            - Fields stored as tuples expose the corresponding :class:`collections.abc.Sequence`
             annotation.
            - Parameter required/optional status is calculated based on :param:`tg_field.default`

    If aliases are present in the dataclass, a wrapper for __init__ is created to provide the
    necessary runtime support.

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
    alias_pairs = tuple(
        (dataclass_field.name, alias)
        for dataclass_field in fields.values()
        if dataclass_field.init and (alias := dataclass_field.metadata.get(ALIAS_KEY)) is not None
    )

    generated_init = cls.__init__
    generated_signature = inspect.signature(generated_init)

    @functools.wraps(generated_init)
    def aliased_init(self: object, *args: object, **kwargs: object) -> None:
        for field_name, alias in alias_pairs:
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
        is_enum_field = dataclass_field.metadata.get(ENUM_KEY, False)
        annotation = param.annotation

        if is_enum_field:
            # while enum fields still have a converter, we skip overwriting the annotation
            # because the existing field annotation already is the right input type
            pass
        elif converter is not None:
            if get_origin(param.annotation) is tuple:
                # Special case for tupel fields passing through parse_sequence_arg converter, we
                # *do not* rely on its first param for the correct annotation b/c (1) it uses a
                # TypeVar and (2) covers all possible argument types (required and optional)
                annotation = to_sequence_annotation(param.annotation)
                if dataclass_field.default is not MISSING:
                    annotation |= None
            else:
                converter_1st_param = next(iter(inspect.signature(converter).parameters.values()))
                annotation = converter_1st_param.annotation

                if dataclass_field.default is MISSING:
                    # Similar to (2) above, some converters (e.g int_to_timedelta) signatures cover
                    # *all* arg types (required and optional), so we judge requiredness
                    # from `field.default`
                    annotation = unwrap_optional(annotation)

        parameters.append(
            param.replace(
                name=alias or param.name,
                annotation=annotation,
            )
        )

    signature = generated_signature.replace(parameters=parameters)

    # Lastly, we overwrite __annotations__, which is important for test_official
    # to perfrom its types tests (it uses `typing.get_type_hints` which reads from __annotations)
    annotations = {param.name: param.annotation for param in parameters if param.name != "self"}
    annotations["return"] = None

    if len(alias_pairs) == 0:
        generated_init.__signature__ = signature  # type: ignore[attr-defined]
        generated_init.__annotations__ = annotations
        return cls

    aliased_init.__signature__ = signature  # type: ignore[attr-defined]
    aliased_init.__annotations__ = annotations

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
    enum: type[Enum] | None = None,
) -> Any:
    """Wrapper around :func:`dataclasses.field`. For defining fields for classes decorated with
    :func:`tg_dataclass`.

    See `Field specifier parameters
    <https://typing.python.org/en/latest/spec/dataclasses.html#field-specifier-parameters>`_
    for standard parameter descriptions.

    Args:
        compare (:obj:`bool`, optional): Passed to :func:`dataclasses.field`. Defaults to
            :obj:`False`.
        converter (:obj:`callable`, optional): A callable used to convert values when assigning to
            the field. Mutually exclusive with :paramref:`enum`.
        enum (:obj:`type[enum.Enum]`, optional): An enum class used to generate a default converter
            from. Mutually exclusive with :paramref:`converter`.

    Returns:
        :class:`dataclasses.Field`

    Raises:
        `ValueError` if both :paramref:`enum` and :paramref:`converter` are passed.
    """
    if enum is not None and converter is not None:
        raise ValueError("`enum` and `converter` are mutually exclusive!")

    field_metadata: dict[Any, Any] = {}

    if converter is not None:
        field_metadata[CONVERTER_KEY] = converter

    if enum is not None:
        field_metadata[ENUM_KEY] = True
        enum_converter = functools.partial(_enum.get_member, enum)

        # Defining and setting `enum_converter` here as opposed to coming from :param:`converter`
        # deliberately hides the converter from type checkers, see more in `process_init`
        field_metadata[CONVERTER_KEY] = enum_converter

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
    frozen_default=True,
    field_specifiers=(tg_field,),
)
def tg_dataclass(
    *,
    eq: bool = True,
) -> Callable[[type[TelegramObj]], type[TelegramObj]]:
    """Decorator for creating PTB-flavoured dataclasses. It [is]:

    - Sets suitable values for frozen, slots, repr, and match_args.
    - Used to decorate `TelegramObject`, all Bot API types, `Bot` and `ExtBot`.
    - Tweaks standard `dataclasses.dataclass` behaviours for PTB needs.

    Args:
        eq (:obj:`bool`): Value to pass to :func:`dataclasses.dataclass`. Defaults to ``True``
    """

    def decorate(cls: type[TelegramObj]) -> type[TelegramObj]:
        transformed_cls = dataclass(
            cls,
            frozen=True,
            slots=True,
            repr=False,
            match_args=False,
            eq=eq,
        )
        transformed_cls = process_init(transformed_cls)

        fields = dataclasses.fields(transformed_cls)

        # Set the cache of (filed, converter) pairs
        transformed_cls.__FIELD_CONVERTERS__ = tuple(
            (dataclass_field.name, dataclass_field.metadata[CONVERTER_KEY])
            for dataclass_field in fields
            if dataclass_field.metadata.get(CONVERTER_KEY) is not None
        )

        # `dataclass()` generates __[get/set]state__ functions that override our custom ones
        if cls.__name__ != "TelegramObject":
            delattr(transformed_cls, "__getstate__")
            delattr(transformed_cls, "__setstate__")

        if eq:
            compare_fields = tuple(
                dataclass_field.name for dataclass_field in fields if dataclass_field.compare
            )

            # Below we'll overwrite dc-generated __hash__ with this implemenattion that (i)
            # *includes* class name in the compare fields and (ii) uses object id as a fallback
            def __hash__(self: object) -> int:
                if compare_fields:
                    values = tuple(getattr(self, name) for name in compare_fields)
                    return hash((self.__class__, values))

                return object.__hash__(self)

            transformed_cls.__hash__ = __hash__  # type: ignore[method-assign]

        return transformed_cls

    return decorate
