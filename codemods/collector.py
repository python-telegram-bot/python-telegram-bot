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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

"""This file determines which methods/parameters need to be added to the API. It does so by
running test_official.py.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd().absolute()))

os.environ["TEST_OFFICIAL"] = "true"

from functools import cache

from helpers import to_camel_case

from tests.test_official.scraper import TelegramParameter
from tests.test_official.test_official import classes, methods


def run_test_official() -> list:
    """Run test_official.py and gather which errors occured."""

    try:
        output = subprocess.run(
            ["pytest", "tests/test_official/test_official.py", "-q", "--no-header", "--tb=line"],
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:  # if test_official.py fails (expected)
        output = e.output
    else:
        output = output.stdout

    # truncate part before ===failures===
    str_output = output[output.find("====") :]
    failures: list[str] = str_output.split("\n")[1:-2]
    return failures


def get_telegram_parameter(
    param_name: str, method_name: str | None = None, class_name: str | None = None
) -> TelegramParameter:
    """Get a TelegramParameter object from the scraper based on the method and parameter name.

    Args:
        method_name (str): The name of the method.
        param_name (str): The name of the parameter.

    Returns:
        TelegramParameter: The TelegramParameter object.
    """

    if method_name is not None:
        for method in methods:
            if method.method_name == to_camel_case(method_name):
                for param in method.method_parameters:
                    if param.param_name == param_name:
                        return param
    elif class_name is not None:
        for cls in classes:
            if cls.class_name == class_name:
                for param in cls.class_parameters:
                    if param.param_name == param_name:
                        return param
    else:
        raise ValueError("Either method_name or class_name must be provided.")

    raise ValueError(f"Param {param_name} not found in method {method_name} or class {class_name}")


@cache
def parse_failures() -> tuple[dict[str, TelegramParameter], dict[str, TelegramParameter]]:
    """Parse the output of run_test_official() to determine which methods/parameters need to be
    added to the API.

    Returns:
        list[TelegramParameter]: A list of parameters that need to be added to the API.
    """

    failures = run_test_official()

    # regex patterns
    param_missing_str = "AssertionError: Parameter ([a-z_]+) not found in ([a-z_]+)"
    attribute_missing_str = "AssertionError: Attribute ([a-z_]+) not found in ([a-zA-Z0-9]+)"

    missing_params_in_methods = {}  # {method_name: TelegramParameter}
    missing_attrs_in_classes = {}  # {class_name: TelegramParameter}

    for failure in failures:
        # We will only count missing parameters/attributes for now:

        # missing parameter
        if match := re.search(param_missing_str, failure):
            param_name = match.group(1)
            method_name = match.group(2)
            tg_param = get_telegram_parameter(param_name, method_name=method_name)
            missing_params_in_methods[method_name] = tg_param

        # missing attribute
        elif match := re.search(attribute_missing_str, failure):
            attr_name = match.group(1)
            class_name = match.group(2)
            tg_param = get_telegram_parameter(attr_name, class_name=class_name)
            missing_attrs_in_classes[class_name] = tg_param

        else:
            print(f"Unknown failure: {failure}")

    return missing_params_in_methods, missing_attrs_in_classes


# run_test_official()
