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
"""Helpers for building ``TelegramObject.de_json`` transformation plans.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""

import importlib
from collections.abc import Callable, Sequence
from functools import lru_cache
from types import UnionType
from typing import TYPE_CHECKING, TypeAlias, Union, cast, get_args, get_origin

if TYPE_CHECKING:
    from telegram import Bot
    from telegram._telegramobject import TelegramObject

DeJsonValueTransformer: TypeAlias = Callable[[object, "Bot | None"], object]


@lru_cache(maxsize=1)
def get_telegram_namespace() -> dict[str, object]:
    """Return the live package namespace used to resolve forward references."""
    return vars(importlib.import_module("telegram"))


def resolve_annotation(
    annotation: object,
    constructor_globals: dict[str, object],
    telegram_namespace: dict[str, object],
) -> object:
    """Resolve a string annotation when all of its names exist at runtime."""
    if not isinstance(annotation, str):
        return annotation

    try:
        return eval(  # pylint: disable=eval-used  # noqa: S307
            annotation,
            constructor_globals,
            telegram_namespace,
        )
    except NameError:
        # Some outgoing-only types are imported under TYPE_CHECKING. They do not describe fields
        # that de_json transforms, so an unresolved annotation can safely stay unchanged.
        return annotation


def unwrap_optional(annotation: object) -> object:
    """Return the sole non-None member of an optional union, if it has one."""
    if get_origin(annotation) not in (Union, UnionType):
        return annotation

    non_none_annotations = tuple(
        member
        for member in get_args(annotation)
        if member is not type(None)  # pylint: disable=unidiomatic-typecheck
    )
    return non_none_annotations[0] if len(non_none_annotations) == 1 else annotation


def build_sequence_transformer(
    item_annotation: object,
    constructor_globals: dict[str, object],
    telegram_namespace: dict[str, object],
    telegram_object_base_class: type["TelegramObject"],
) -> DeJsonValueTransformer | None:
    """Build the value transformer for one level of a JSON array annotation."""
    resolved_item_annotation = resolve_annotation(
        item_annotation,
        constructor_globals,
        telegram_namespace,
    )
    item_origin = get_origin(resolved_item_annotation)

    if item_origin is Sequence:
        nested_item_annotations = get_args(resolved_item_annotation)
        if not nested_item_annotations:
            return None

        nested_item_transformer = build_sequence_transformer(
            nested_item_annotations[0],
            constructor_globals,
            telegram_namespace,
            telegram_object_base_class,
        )
        if nested_item_transformer is None:
            return None
        item_transformer = cast("DeJsonValueTransformer", nested_item_transformer)

        def transform_nested_sequence(
            raw_value: object,
            bot: "Bot | None",
            item_transformer: DeJsonValueTransformer = item_transformer,
        ) -> object:
            if not isinstance(raw_value, list):
                return raw_value
            return [item_transformer(item, bot) for item in raw_value]

        return transform_nested_sequence

    if isinstance(resolved_item_annotation, type) and issubclass(
        resolved_item_annotation, telegram_object_base_class
    ):
        telegram_object_class = cast("type[TelegramObject]", resolved_item_annotation)

        def transform_object_sequence(
            raw_value: object,
            bot: "Bot | None",
            target_class: "type[TelegramObject]" = telegram_object_class,
        ) -> object:
            if not isinstance(raw_value, list):
                return raw_value
            return target_class.de_list(raw_value, bot)

        return transform_object_sequence

    return None
