#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
"""This module contains helper functions related to parsing arguments for classes and methods.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
from collections.abc import Sequence
from typing import Optional, TypeVar

from telegram._linkpreviewoptions import LinkPreviewOptions
from telegram._utils.types import ODVInput

T = TypeVar("T")


def parse_sequence_arg(arg: Optional[Sequence[T]]) -> tuple[T, ...]:
    """Parses an optional sequence into a tuple

    Args:
        arg (:obj:`Sequence`): The sequence to parse.

    Returns:
        :obj:`Tuple`: The sequence converted to a tuple or an empty tuple.
    """
    return tuple(arg) if arg else ()


def parse_lpo_and_dwpp(
    disable_web_page_preview: Optional[bool], link_preview_options: ODVInput[LinkPreviewOptions]
) -> ODVInput[LinkPreviewOptions]:
    """Wrapper around warn_about_deprecated_arg_return_new_arg. Takes care of converting
    disable_web_page_preview to LinkPreviewOptions.
    """
    if disable_web_page_preview and link_preview_options:
        raise ValueError(
            "Parameters `disable_web_page_preview` and `link_preview_options` are mutually "
            "exclusive."
        )

    if disable_web_page_preview is not None:
        link_preview_options = LinkPreviewOptions(is_disabled=disable_web_page_preview)

    return link_preview_options
