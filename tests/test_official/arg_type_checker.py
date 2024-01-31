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
import re
from datetime import datetime
from types import FunctionType
from typing import Any, ForwardRef, Sequence, get_args, get_origin

import telegram
from telegram._utils.defaultvalue import DefaultValue
from telegram._utils.types import FileInput, ODVInput
from telegram.ext import Defaults
from tests.test_official.exceptions import ParamTypeCheckingExceptions as PTCE
from tests.test_official.exceptions import ignored_param_requirements
from tests.test_official.helpers import _extract_words, _get_params_base, _unionizer
from tests.test_official.scraper import TelegramParameter

# In order to evaluate the type annotation, we need to first have a mapping of the types
# specified in the official API to our types. The keys are types in the column of official API.
TYPE_MAPPING: dict[str, set[Any]] = {
    "Integer or String": {int | str},
    "Integer": {int},
    "String": {str},
    r"Boolean|True": {bool},
    r"Float(?: number)?": {float},
    # Distinguishing 1D and 2D Sequences and finding the inner type is done later.
    r"Array of (?:Array of )?[\w\,\s]*": {Sequence},
    r"InputFile(?: or String)?": {FileInput},
}


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
    ptb_param: inspect.Parameter, tg_parameter: TelegramParameter, obj: FunctionType | type
) -> bool:
    """This function checks whether the type annotation of the parameter is the same as the one
    specified in the official API. It also checks for some special cases where we accept more types

    Args:
        ptb_param (inspect.Parameter): The parameter object from our methods/classes
        tg_parameter (list[str]): The table row corresponding to the parameter from official API.
        obj (object): The object (method/class) that we are checking.

    Returns:
        :obj:`bool`: The boolean returned represents whether our parameter's type annotation is the
        same as Telegram's or not.
    """
    # PRE-PROCESSING:
    # In order to evaluate the type annotation, we need to first have a mapping of the types
    # (see TYPE_MAPPING comment defined above)
    tg_param_type: str = tg_parameter.param_type
    is_class = inspect.isclass(obj)
    # Let's check for a match:
    mapped: set[type] = _get_params_base(tg_param_type, TYPE_MAPPING)

    # We should have a maximum of one match.
    assert len(mapped) <= 1, f"More than one match found for {tg_param_type}"

    if not mapped:  # no match found, it's from telegram module
        # it could be a list of objects, so let's check that:
        objs = _extract_words(tg_param_type)
        # We want to store both string version of class and the class obj itself. e.g. "InputMedia"
        # and InputMedia because some annotations might be ForwardRefs.
        if len(objs) >= 2:  # We have to unionize the objects
            mapped_type: tuple[Any, ...] = (_unionizer(objs, False), _unionizer(objs, True))
        else:
            mapped_type = (
                getattr(telegram, tg_param_type),  # This will fail if it's not from telegram mod
                ForwardRef(tg_param_type),
                tg_param_type,  # for some reason, some annotations are just a string.
            )
    elif len(mapped) == 1:
        mapped_type = mapped.pop()

    # Resolve nested annotations to get inner types.
    if (ptb_annotation := list(get_args(ptb_param.annotation))) == []:
        ptb_annotation = ptb_param.annotation  # if it's not nested, just use the annotation

    if isinstance(ptb_annotation, list):
        # Some cleaning:
        # Remove 'Optional[...]' from the annotation if it's present. We do it this way since: 1)
        # we already check if argument should be optional or not + type checkers will complain.
        # 2) we want to check if our `obj` is same as API's `obj`, and since python evaluates
        # `Optional[obj] != obj` we have to remove the Optional, so that we can compare the two.
        if type(None) in ptb_annotation:
            ptb_annotation.remove(type(None))

        # Cleaning done... now let's put it back together.
        # Join all the annotations back (i.e. Union)
        ptb_annotation = _unionizer(ptb_annotation, False)

        # Last step, we need to use get_origin to get the original type, since using get_args
        # above will strip that out.
        wrapped = get_origin(ptb_param.annotation)
        if wrapped is not None:
            # collections.abc.Sequence -> typing.Sequence
            if "collections.abc.Sequence" in str(wrapped):
                wrapped = Sequence
            ptb_annotation = wrapped[ptb_annotation]
        # We have put back our annotation together after removing the NoneType!

    # CHECKING:
    # Each branch may have exits in the form of return statements. If the annotation is found to be
    # correct, the function will return True. If not, it will return False.

    # 1) HANDLING ARRAY TYPES:
    # Now let's do the checking, starting with "Array of ..." types.
    if "Array of " in tg_param_type:
        assert mapped_type is Sequence
        # For exceptions just check if they contain the annotation
        if ptb_param.name in PTCE.ARRAY_OF_EXCEPTIONS:
            return PTCE.ARRAY_OF_EXCEPTIONS[ptb_param.name] in str(ptb_annotation)

        pattern = r"Array of(?: Array of)? ([\w\,\s]*)"
        obj_match: re.Match | None = re.search(pattern, tg_param_type)  # extract obj from string
        if obj_match is None:
            raise AssertionError(f"Array of {tg_param_type} not found in {ptb_param.name}")
        obj_str: str = obj_match.group(1)
        # is obj a regular type like str?
        array_of_mapped: set[type] = _get_params_base(obj_str, TYPE_MAPPING)

        if len(array_of_mapped) == 0:  # no match found, it's from telegram module
            # it could be a list of objects, so let's check that:
            objs = _extract_words(obj_str)
            # let's unionize all the objects, with and without ForwardRefs.
            unionized_objs: list[type] = [_unionizer(objs, True), _unionizer(objs, False)]
        else:
            unionized_objs = [array_of_mapped.pop()]

        # This means it is Array of Array of [obj]
        if "Array of Array of" in tg_param_type:
            return any(Sequence[Sequence[o]] == ptb_annotation for o in unionized_objs)

        # This means it is Array of [obj]
        return any(mapped_type[o] == ptb_annotation for o in unionized_objs)

    # 2) HANDLING DEFAULTS PARAMETERS:
    # Classes whose parameters are all ODVInput should be converted and checked.
    if obj.__name__ in PTCE.IGNORED_DEFAULTS_CLASSES:
        parsed = ODVInput[mapped_type]
        return (ptb_annotation | None) == parsed  # We have to add back None in our annotation
    if not (
        # Defaults checking should not be done for:
        # 1. Parameters that have name conflict with `Defaults.name`
        is_class
        and obj.__name__ in ("ReplyParameters", "Message", "ExternalReplyInfo")
        and ptb_param.name in PTCE.IGNORED_DEFAULTS_PARAM_NAMES
    ):
        # Now let's check if the parameter is a Defaults parameter, it should be
        for name, _ in inspect.getmembers(Defaults, lambda x: isinstance(x, property)):
            if name == ptb_param.name or "parse_mode" in ptb_param.name:
                # mapped_type should not be a tuple since we need to check for equality:
                # This can happen when the Defaults parameter is a class, e.g. LinkPreviewOptions
                if isinstance(mapped_type, tuple):
                    mapped_type = mapped_type[1]  # We select the ForwardRef
                # Assert if it's ODVInput by checking equality:
                parsed = ODVInput[mapped_type]
                if (ptb_annotation | None) == parsed:  # We have to add back None in our annotation
                    return True
                return False

    # 3) HANDLING OTHER TYPES:
    # Special case for send_* methods where we accept more types than the official API:
    if (
        ptb_param.name in PTCE.ADDITIONAL_TYPES
        and not isinstance(mapped_type, tuple)
        and obj.__name__.startswith("send")
    ):
        mapped_type = mapped_type | PTCE.ADDITIONAL_TYPES[ptb_param.name]

    # 4) HANDLING DATETIMES:
    if (
        re.search(
            r"""([_]+|\b)  # check for word boundary or underscore
                date       # check for "date"
                [^\w]*\b   # optionally check for a word after 'date'
            """,
            ptb_param.name,
            re.VERBOSE,
        )
        or "Unix time" in tg_parameter.param_description
    ):
        if ptb_param.name in PTCE.DATETIME_EXCEPTIONS:
            return True
        # If it's a class, we only accept datetime as the parameter
        mapped_type = datetime if is_class else mapped_type | datetime

    # RESULTS: ALL OTHER BASIC TYPES-
    # Some types are too complicated, so we replace them with a simpler type:
    for (param_name, expected_class), exception_type in PTCE.COMPLEX_TYPES.items():
        if ptb_param.name == param_name and is_class is expected_class:
            ptb_annotation = exception_type

    # Final check, if the annotation is a tuple, we need to check if any of the types in the tuple
    # match the mapped type.
    if isinstance(mapped_type, tuple) and any(ptb_annotation == t for t in mapped_type):
        return True

    # If the annotation is not a tuple, we can just check if it's equal to the mapped type.
    return mapped_type == ptb_annotation
