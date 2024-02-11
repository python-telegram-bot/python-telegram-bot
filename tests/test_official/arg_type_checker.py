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
"""This module contains functions which confirm that the parameters of our methods and classes
match the official API. It also checks if the type annotations are correct and if the parameters
are required or not."""

import inspect
import logging
import re
from datetime import datetime
from types import FunctionType
from typing import Any, Sequence

from telegram._utils.defaultvalue import DefaultValue
from telegram._utils.types import FileInput, ODVInput
from telegram.ext import Defaults
from tests.test_official.exceptions import ParamTypeCheckingExceptions as PTCE
from tests.test_official.exceptions import ignored_param_requirements
from tests.test_official.helpers import (
    _extract_words,
    _get_params_base,
    _unionizer,
    cached_type_hints,
    resolve_forward_refs_in_type,
    wrap_with_none,
)
from tests.test_official.scraper import TelegramParameter

ARRAY_OF_PATTERN = r"Array of(?: Array of)? ([\w\,\s]*)"

# In order to evaluate the type annotation, we need to first have a mapping of the types
# specified in the official API to our types. The keys are types in the column of official API.
TYPE_MAPPING: dict[str, set[Any]] = {
    "Integer or String": {int | str},
    "Integer": {int},
    "String": {str},
    r"Boolean|True": {bool},
    r"Float(?: number)?": {float},
    # Distinguishing 1D and 2D Sequences and finding the inner type is done later.
    ARRAY_OF_PATTERN: {Sequence},
    r"InputFile(?: or String)?": {resolve_forward_refs_in_type(FileInput)},
}

ALL_DEFAULTS = inspect.getmembers(Defaults, lambda x: isinstance(x, property))

DATETIME_REGEX = re.compile(
    r"""([_]+|\b)  # check for word boundary or underscore
    date       # check for "date"
    [^\w]*\b   # optionally check for a word after 'date'
    """,
    re.VERBOSE,
)

log = logging.debug


def check_required_param(
    tg_param: TelegramParameter, param: inspect.Parameter, method_or_obj_name: str
) -> bool:
    """Checks if the method/class parameter is a required/optional param as per Telegram docs.

    Returns:
        :obj:`bool`: The boolean returned represents whether our parameter's requirement (optional
            or required) is the same as Telegram's or not.
    """
    is_ours_required = param.default is inspect.Parameter.empty
    # Handle cases where we provide convenience intentionally-
    if param.name in ignored_param_requirements(method_or_obj_name):
        return True
    return tg_param.param_required is is_ours_required


def check_defaults_type(ptb_param: inspect.Parameter) -> bool:
    return DefaultValue.get_value(ptb_param.default) is None


def check_param_type(
    ptb_param: inspect.Parameter,
    tg_parameter: TelegramParameter,
    obj: FunctionType | type,
) -> tuple[bool, type]:
    """This function checks whether the type annotation of the parameter is the same as the one
    specified in the official API. It also checks for some special cases where we accept more types

    Args:
        ptb_param: The parameter object from our methods/classes
        tg_parameter: The table row corresponding to the parameter from official API.
        obj: The object (method/class) that we are checking.

    Returns:
        :obj:`tuple`: A tuple containing:
            * :obj:`bool`: The boolean returned represents whether our parameter's type annotation
              is the same as Telegram's or not.
            * :obj:`type`: The expected type annotation of the parameter.
    """
    # PRE-PROCESSING:
    tg_param_type: str = tg_parameter.param_type
    is_class = inspect.isclass(obj)
    ptb_annotation = cached_type_hints(obj, is_class).get(ptb_param.name)

    # Let's check for a match:
    # In order to evaluate the type annotation, we need to first have a mapping of the types
    # (see TYPE_MAPPING comment defined at the top level of this module)
    mapped: set[type] = _get_params_base(tg_param_type, TYPE_MAPPING)

    # We should have a maximum of one match.
    assert len(mapped) <= 1, f"More than one match found for {tg_param_type}"

    # it may be a list of objects, so let's extract them using _extract_words:
    mapped_type = _unionizer(_extract_words(tg_param_type)) if not mapped else mapped.pop()
    # If the parameter is not required by TG, `None` should be added to `mapped_type`
    mapped_type = wrap_with_none(tg_parameter, mapped_type, obj)

    log(
        "At the end of PRE-PROCESSING, the values of variables are:\n"
        "Parameter name: %s\n"
        "ptb_annotation= %s\n"
        "mapped_type= %s\n"
        "tg_param_type= %s\n"
        "tg_parameter.param_required= %s\n",
        ptb_param.name,
        ptb_annotation,
        mapped_type,
        tg_param_type,
        tg_parameter.param_required,
    )

    # CHECKING:
    # Each branch manipulates the `mapped_type` (except for 4) ) to match the `ptb_annotation`.

    # 1) HANDLING ARRAY TYPES:
    # Now let's do the checking, starting with "Array of ..." types.
    if "Array of " in tg_param_type:
        # For exceptions just check if they contain the annotation
        if ptb_param.name in PTCE.ARRAY_OF_EXCEPTIONS:
            return PTCE.ARRAY_OF_EXCEPTIONS[ptb_param.name] in str(ptb_annotation), Sequence

        obj_match: re.Match | None = re.search(ARRAY_OF_PATTERN, tg_param_type)
        if obj_match is None:
            raise AssertionError(f"Array of {tg_param_type} not found in {ptb_param.name}")
        obj_str: str = obj_match.group(1)
        # is obj a regular type like str?
        array_map: set[type] = _get_params_base(obj_str, TYPE_MAPPING)

        mapped_type = _unionizer(_extract_words(obj_str)) if not array_map else array_map.pop()

        if "Array of Array of" in tg_param_type:
            log("Array of Array of type found in `%s`\n", tg_param_type)
            mapped_type = Sequence[Sequence[mapped_type]]
        else:
            log("Array of type found in `%s`\n", tg_param_type)
            mapped_type = Sequence[mapped_type]

    # 2) HANDLING OTHER TYPES:
    # Special case for send_* methods where we accept more types than the official API:
    elif ptb_param.name in PTCE.ADDITIONAL_TYPES and obj.__name__.startswith("send"):
        log("Checking that `%s` has an additional argument!\n", ptb_param.name)
        mapped_type = mapped_type | PTCE.ADDITIONAL_TYPES[ptb_param.name]

    # 3) HANDLING DATETIMES:
    elif (
        re.search(
            DATETIME_REGEX,
            ptb_param.name,
        )
        or "Unix time" in tg_parameter.param_description
    ):
        log("Checking that `%s` is a datetime!\n", ptb_param.name)
        if ptb_param.name in PTCE.DATETIME_EXCEPTIONS:
            return True, mapped_type
        # If it's a class, we only accept datetime as the parameter
        mapped_type = datetime if is_class else mapped_type | datetime

    # 4) COMPLEX TYPES:
    # Some types are too complicated, so we replace our annotation with a simpler type:
    elif any(ptb_param.name in key for key in PTCE.COMPLEX_TYPES):
        log("Converting `%s` to a simpler type!\n", ptb_param.name)
        for (param_name, is_expected_class), exception_type in PTCE.COMPLEX_TYPES.items():
            if ptb_param.name == param_name and is_class is is_expected_class:
                ptb_annotation = wrap_with_none(tg_parameter, exception_type, obj)

    # 5) HANDLING DEFAULTS PARAMETERS:
    # Classes whose parameters are all ODVInput should be converted and checked.
    elif obj.__name__ in PTCE.IGNORED_DEFAULTS_CLASSES:
        log("Checking that `%s`'s param is ODVInput:\n", obj.__name__)
        mapped_type = ODVInput[mapped_type]
    elif not (
        # Defaults checking should not be done for:
        # 1. Parameters that have name conflict with `Defaults.name`
        is_class
        and obj.__name__ in ("ReplyParameters", "Message", "ExternalReplyInfo")
        and ptb_param.name in PTCE.IGNORED_DEFAULTS_PARAM_NAMES
    ):
        # Now let's check if the parameter is a Defaults parameter, it should be
        for name, _ in ALL_DEFAULTS:
            if name == ptb_param.name or "parse_mode" in ptb_param.name:
                log("Checking that `%s` is a Defaults parameter!\n", ptb_param.name)
                mapped_type = ODVInput[mapped_type]
                break

    # RESULTS:-
    mapped_type = wrap_with_none(tg_parameter, mapped_type, obj)
    mapped_type = resolve_forward_refs_in_type(mapped_type)
    log(
        "At RESULTS, we are comparing:\nptb_annotation= %s\nmapped_type= %s\n",
        ptb_annotation,
        mapped_type,
    )
    return mapped_type == ptb_annotation, mapped_type
