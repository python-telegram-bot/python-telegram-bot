#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
"""This module contains helper functions related to json en-/decoding.

.. versionadded:: 20.0

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
from typing import Any

try:
    import orjson

    def json_loads(json_str: str) -> Any:
        """Implementation independent interface for loading an object from a JSON string.

        Uses the std-lib `json` module if the optional 3rd party dependency is not available
        """
        return orjson.loads(json_str)

    def json_dumps(obj: object) -> str:
        """Implementation independent interface for dumping an object to a JSON string.

        Uses the std-lib `json` module if the optional 3rd party dependency is not available
        """
        return orjson.dumps(obj).decode("utf-8")

except ImportError:
    import json

    def json_loads(json_str: str) -> Any:
        """Implementation independent interface for loading an object from a JSON string.

        Uses the std-lib `json` module if the optional 3rd party dependency is not available
        """
        return json.loads(json_str)

    def json_dumps(obj: object) -> str:
        """Implementation independent interface for dumping an object to a JSON string.

        Uses the std-lib `json` module if the optional 3rd party dependency is not available
        """
        return json.dumps(obj)
