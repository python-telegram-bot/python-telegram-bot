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


def build_union_transformer(
    union_annotation: object,
    constructor_globals: dict[str, object],
    telegram_namespace: dict[str, object],
    telegram_object_base_class: type["TelegramObject"],
) -> DeJsonValueTransformer | None:
    """Build a value transformer for a Union annotation containing TelegramObject types."""
    if get_origin(union_annotation) not in (Union, UnionType):
        return None

    args = get_args(union_annotation)
    tg_classes: list[type[TelegramObject]] = []
    has_sequence = False
    sequence_item_class: type[TelegramObject] | None = None

    for arg in args:
        resolved_arg = resolve_annotation(arg, constructor_globals, telegram_namespace)
        if isinstance(resolved_arg, type) and issubclass(resolved_arg, telegram_object_base_class):
            tg_classes.append(cast("type[TelegramObject]", resolved_arg))
        elif get_origin(resolved_arg) is Sequence:
            has_sequence = True
            seq_args = get_args(resolved_arg)
            if seq_args:
                resolved_item = resolve_annotation(
                    seq_args[0], constructor_globals, telegram_namespace
                )
                if isinstance(resolved_item, type) and issubclass(
                    resolved_item, telegram_object_base_class
                ):
                    sequence_item_class = cast("type[TelegramObject]", resolved_item)

    if not tg_classes and not has_sequence:
        return None

    def transform_union(
        raw_value: object,
        bot: "Bot | None",
        tg_classes: tuple[type[TelegramObject], ...] = tuple(tg_classes),
        sequence_item_class: type[TelegramObject] | None = sequence_item_class,
    ) -> object:
        if isinstance(raw_value, dict):
            for cls in tg_classes:
                if cls.__DE_JSON_DISPATCH__:
                    dispatch_key, dispatch_mapping = cls.__DE_JSON_DISPATCH__
                    if raw_value.get(dispatch_key) in dispatch_mapping:
                        return cls.de_json(raw_value, bot)
                else:
                    return cls.de_json(raw_value, bot)
            if tg_classes:
                return tg_classes[0].de_json(raw_value, bot)
        elif isinstance(raw_value, list) and sequence_item_class is not None:
            return tuple(
                sequence_item_class.de_json(item, bot) if isinstance(item, dict) else item
                for item in raw_value
            )
        return raw_value

    return transform_union

