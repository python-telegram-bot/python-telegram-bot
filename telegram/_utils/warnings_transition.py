#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
"""This module contains classes used for transition warnings issued by this library.

It was created to prevent circular imports that would be caused by creating the warnings
inside warnings.py.

.. versionadded:: NEXT.VERSION
"""
from typing import Any

from telegram._utils.warnings import warn
from telegram.warnings import PTBDeprecationWarning


# Narrower type hints will cause linting errors and/or circular imports.
# We'll use `Any` here and put type hints in the calling code.
def warn_about_thumb_return_thumbnail(thumb: Any, thumbnail: Any) -> Any:
    """A helper function for the transition introduced by API 6.6.

    Checks the `thumb` and `thumbnail` objects; warns if non-None `thumb` object was passed.
    Returns `thumbnail` object (either the one originally passed by the user or the one that
    user passed as `thumb`).

    Raises ValueError if both `thumb` and `thumbnail` objects were passed, and they are different.
    """
    if thumb and thumbnail and thumb != thumbnail:
        raise ValueError(
            "You passed different entities as 'thumb' and 'thumbnail'. The parameter 'thumb' "
            "was renamed to 'thumbnail' in Bot API 6.6. We recommend using 'thumbnail' "
            "instead of 'thumb'."
        )

    if thumb:
        warn(
            "Bot API 6.6 renamed the argument 'thumb' to 'thumbnail'.",
            PTBDeprecationWarning,
            stacklevel=2,
        )
        return thumb

    return thumbnail
