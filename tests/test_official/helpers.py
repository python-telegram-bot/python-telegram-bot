#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains helper functions for the official API tests used in the other modules."""

import functools
import re
from typing import TYPE_CHECKING, Any, Sequence, _eval_type, get_type_hints

from bs4 import PageElement, Tag

import telegram
import telegram._utils.defaultvalue
import telegram._utils.types

if TYPE_CHECKING:
    from tests.test_official.scraper import TelegramParameter


tg_objects = vars(telegram)
tg_objects.update(vars(telegram._utils.types))
tg_objects.update(vars(telegram._utils.defaultvalue))


def _get_params_base(object_name: str, search_dict: dict[str, set[Any]]) -> set[Any]:
    """Helper function for the *_params functions below.
    Given an object name and a search dict, goes through the keys of the search dict and checks if
    the object name matches any of the regexes (keys). The union of all the sets (values) of the
    matching regexes is returned. `object_name` may be a CamelCase or snake_case name.
    """
    out = set()
    for regex, params in search_dict.items():
        if re.fullmatch(regex, object_name):
            out.update(params)
        # also check the snake_case version
        snake_case_name = re.sub(r"(?<!^)(?=[A-Z])", "_", object_name).lower()
        if re.fullmatch(regex, snake_case_name):
            out.update(params)
    return out


def _extract_words(text: str) -> set[str]:
    """Extracts all words from a string, removing all punctuation and words like 'and' & 'or'."""
    return set(re.sub(r"[^\w\s]", "", text).split()) - {"and", "or"}


def _unionizer(annotation: Sequence[Any] | set[Any]) -> Any:
    """Returns a union of all the types in the annotation. Also imports objects from lib."""
    union = None
    for t in annotation:
        if isinstance(t, str):  # we have to import objects from lib
            t = getattr(telegram, t)  # noqa: PLW2901
        union = t if union is None else union | t
    return union


def find_next_sibling_until(tag: Tag, name: str, until: Tag) -> PageElement | None:
    for sibling in tag.next_siblings:
        if sibling is until:
            return None
        if sibling.name == name:
            return sibling
    return None


def is_pascal_case(s):
    "PascalCase. Starts with a capital letter and has no spaces. Useful for identifying classes."
    return bool(re.match(r"^[A-Z][a-zA-Z\d]*$", s))


def is_parameter_required_by_tg(field: str) -> bool:
    if field in {"Required", "Yes"}:
        return True
    return field.split(".", 1)[0] != "Optional"  # splits the sentence and extracts first word


def wrap_with_none(tg_parameter: "TelegramParameter", mapped_type: Any, obj: object) -> type:
    """Adds `None` to type annotation if the parameter isn't required. Respects ignored params."""
    # have to import here to avoid circular imports
    from tests.test_official.exceptions import ignored_param_requirements

    if tg_parameter.param_name in ignored_param_requirements(obj.__name__):
        return mapped_type | type(None)
    return mapped_type | type(None) if not tg_parameter.param_required else mapped_type


@functools.cache
def cached_type_hints(obj: Any, is_class: bool) -> dict[str, Any]:
    """Returns type hints of a class, method, or function, with forward refs evaluated."""
    return get_type_hints(obj.__init__ if is_class else obj, localns=tg_objects)


@functools.cache
def resolve_forward_refs_in_type(obj: type) -> type:
    """Resolves forward references in a type hint."""
    return _eval_type(obj, localns=tg_objects, globalns=None)
