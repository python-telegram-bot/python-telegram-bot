#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2024
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
"""Functionality in this file is used for getting the [source] links on the classes, methods etc
to link to the correct files & lines on github. Can be simplified once
https://github.com/sphinx-doc/sphinx/issues/1556 is closed
"""
import subprocess
from pathlib import Path
from typing import Dict, Tuple

from sphinx.util import logging

# get the sphinx(!) logger
# Makes sure logs render in red and also plays nicely with e.g. the `nitpicky` option.
sphinx_logger = logging.getLogger(__name__)


# must be a module-level variable so that it can be written to by the `autodoc-process-docstring`
# event handler in `sphinx_hooks.py`
LINE_NUMBERS: Dict[str, Tuple[Path, int, int]] = {}


def _git_branch() -> str:
    """Get's the current git sha if available or fall back to `master`"""
    try:
        output = subprocess.check_output(
            ["git", "describe", "--tags", "--always"], stderr=subprocess.STDOUT
        )
        return output.decode().strip()
    except Exception as exc:
        sphinx_logger.exception(
            "Failed to get a description of the current commit. Falling back to `master`.",
            exc_info=exc,
        )
        return "master"


git_branch = _git_branch()
base_url = "https://github.com/python-telegram-bot/python-telegram-bot/blob/"


def linkcode_resolve(_, info) -> str:
    """See www.sphinx-doc.org/en/master/usage/extensions/linkcode.html"""
    combined = ".".join((info["module"], info["fullname"]))
    # special casing for ExtBot which is due to the special structure of extbot.rst
    combined = combined.replace("ExtBot.ExtBot", "ExtBot")

    line_info = LINE_NUMBERS.get(combined)

    if not line_info:
        # Try the __init__
        line_info = LINE_NUMBERS.get(f"{combined.rsplit('.', 1)[0]}.__init__")
    if not line_info:
        # Try the class
        line_info = LINE_NUMBERS.get(f"{combined.rsplit('.', 1)[0]}")
    if not line_info:
        # Try the module
        line_info = LINE_NUMBERS.get(info["module"])

    if not line_info:
        return None

    file, start_line, end_line = line_info
    return f"{base_url}{git_branch}/{file}#L{start_line}-L{end_line}"
