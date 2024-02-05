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
# along with this program. If not, see [http://www.gnu.org/licenses/].
import inspect
from typing import TYPE_CHECKING

import pytest

import telegram
from tests.auxil.envvars import RUN_TEST_OFFICIAL
from tests.test_official.arg_type_checker import (
    check_defaults_type,
    check_param_type,
    check_required_param,
)
from tests.test_official.exceptions import (
    GLOBALLY_IGNORED_PARAMETERS,
    backwards_compat_kwargs,
    ptb_extra_params,
    ptb_ignored_params,
)
from tests.test_official.scraper import Scraper, TelegramClass, TelegramMethod

if TYPE_CHECKING:
    from types import FunctionType

# Will skip all tests in this file if the env var is False
pytestmark = pytest.mark.skipif(not RUN_TEST_OFFICIAL, reason="test_official is not enabled")

methods, method_ids, classes, class_ids = [], [], [], []  # not needed (just for completeness)

if RUN_TEST_OFFICIAL:
    scraper = Scraper()
    methods, method_ids = scraper.collect_methods()
    classes, class_ids = scraper.collect_classes()


@pytest.mark.parametrize("tg_method", argvalues=methods, ids=method_ids)
def test_check_method(tg_method: TelegramMethod) -> None:
    """This function checks for the following things compared to the official API docs:

    - Method existence
    - Parameter existence
    - Parameter requirement correctness
    - Parameter type annotation existence
    - Parameter type annotation correctness
    - Parameter default value correctness
    - No unexpected parameters
    - Extra parameters should be keyword only
    """
    ptb_method: FunctionType | None = getattr(telegram.Bot, tg_method.method_name, None)
    assert ptb_method, f"Method {tg_method.method_name} not found in telegram.Bot"

    # Check arguments based on source
    sig = inspect.signature(ptb_method, follow_wrapped=True)
    checked = []

    for tg_parameter in tg_method.method_parameters:
        # Check if parameter is present in our method
        ptb_param = sig.parameters.get(tg_parameter.param_name)
        assert (
            ptb_param is not None
        ), f"Parameter {tg_parameter.param_name} not found in {ptb_method.__name__}"

        # Now check if the parameter is required or not
        assert check_required_param(
            tg_parameter, ptb_param, ptb_method.__name__
        ), f"Param {ptb_param.name!r} of {ptb_method.__name__!r} requirement mismatch"

        # Check if type annotation is present
        assert (
            ptb_param.annotation is not inspect.Parameter.empty
        ), f"Param {ptb_param.name!r} of {ptb_method.__name__!r} should have a type annotation!"
        # Check if type annotation is correct
        correct_type_hint, expected_type_hint = check_param_type(
            ptb_param,
            tg_parameter,
            ptb_method,
        )
        assert correct_type_hint, (
            f"Type hint of param {ptb_param.name!r} of {ptb_method.__name__!r} should be "
            f"{expected_type_hint!r} or something else!"
        )

        # Now we will check that we don't pass default values if the parameter is not required.
        if ptb_param.default is not inspect.Parameter.empty:  # If there is a default argument...
            default_arg_none = check_defaults_type(ptb_param)  # check if it's None
            assert (
                default_arg_none
            ), f"Param {ptb_param.name!r} of {ptb_method.__name__!r} should be `None`"
        checked.append(tg_parameter.param_name)

    expected_additional_args = GLOBALLY_IGNORED_PARAMETERS.copy()
    expected_additional_args |= ptb_extra_params(tg_method.method_name)
    expected_additional_args |= backwards_compat_kwargs(tg_method.method_name)

    unexpected_args = (sig.parameters.keys() ^ checked) - expected_additional_args
    assert (
        unexpected_args == set()
    ), f"In {ptb_method.__qualname__}, unexpected args were found: {unexpected_args}."

    kw_or_positional_args = [
        p.name for p in sig.parameters.values() if p.kind != inspect.Parameter.KEYWORD_ONLY
    ]
    non_kw_only_args = set(kw_or_positional_args).difference(checked).difference(["self"])
    non_kw_only_args -= backwards_compat_kwargs(tg_method.method_name)
    assert non_kw_only_args == set(), (
        f"In {ptb_method.__qualname__}, extra args should be keyword only (compared to "
        f"{tg_method.method_name} in API)"
    )


@pytest.mark.parametrize("tg_class", argvalues=classes, ids=class_ids)
def test_check_object(tg_class: TelegramClass) -> None:
    """This function checks for the following things compared to the official API docs:

    - Class existence
    - Parameter existence
    - Parameter requirement correctness
    - Parameter type annotation existence
    - Parameter type annotation correctness
    - Parameter default value correctness
    - No unexpected parameters
    """
    obj = getattr(telegram, tg_class.class_name)

    # Check arguments based on source. Makes sure to only check __init__'s signature & nothing else
    sig = inspect.signature(obj.__init__, follow_wrapped=True)

    checked = set()
    fields_removed_by_ptb = ptb_ignored_params(tg_class.class_name)

    for tg_parameter in tg_class.class_parameters:
        field: str = tg_parameter.param_name

        if field in fields_removed_by_ptb:
            continue

        if field == "from":
            field = "from_user"

        ptb_param = sig.parameters.get(field)
        assert ptb_param is not None, f"Attribute {field} not found in {obj.__name__}"

        # Now check if the parameter is required or not
        assert check_required_param(
            tg_parameter, ptb_param, obj.__name__
        ), f"Param {ptb_param.name!r} of {obj.__name__!r} requirement mismatch"

        # Check if type annotation is present
        assert (
            ptb_param.annotation is not inspect.Parameter.empty
        ), f"Param {ptb_param.name!r} of {obj.__name__!r} should have a type annotation"

        # Check if type annotation is correct
        correct_type_hint, expected_type_hint = check_param_type(ptb_param, tg_parameter, obj)
        assert correct_type_hint, (
            f"Type hint of param {ptb_param.name!r} of {obj.__name__!r} should be "
            f"{expected_type_hint!r} or something else!"
        )

        # Now we will check that we don't pass default values if the parameter is not required.
        if ptb_param.default is not inspect.Parameter.empty:  # If there is a default argument...
            default_arg_none = check_defaults_type(ptb_param)  # check if its None
            assert (
                default_arg_none
            ), f"Param {ptb_param.name!r} of {obj.__name__!r} should be `None`"

        checked.add(field)

    expected_additional_args = GLOBALLY_IGNORED_PARAMETERS.copy()
    expected_additional_args |= ptb_extra_params(tg_class.class_name)
    expected_additional_args |= backwards_compat_kwargs(tg_class.class_name)

    unexpected_args = (sig.parameters.keys() ^ checked) - expected_additional_args
    assert (
        unexpected_args == set()
    ), f"In {tg_class.class_name}, unexpected args were found: {unexpected_args}."
