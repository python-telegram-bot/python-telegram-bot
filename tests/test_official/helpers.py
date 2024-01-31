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

import re
from typing import Any, ForwardRef, Sequence

from bs4 import PageElement, Tag

import telegram


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


def _unionizer(annotation: Sequence[Any] | set[Any], forward_ref: bool) -> Any:
    """Returns a union of all the types in the annotation. If forward_ref is True, it wraps the
    annotation in a ForwardRef and then unionizes."""
    union = None
    for t in annotation:
        if forward_ref:
            t = ForwardRef(t)  # noqa: PLW2901
        elif not forward_ref and isinstance(t, str):  # we have to import objects from lib
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
    # Check if the string starts with a capital letter and contains only alphanumeric characters
    return bool(re.match(r"^[A-Z][a-zA-Z\d]*$", s))


def is_parameter_required_by_tg(field: str) -> bool:
    if field in {"Required", "Yes"}:
        return True
    return field.split(".", 1)[0] != "Optional"  # splits the sentence and extracts first word
