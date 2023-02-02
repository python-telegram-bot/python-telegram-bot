#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2023
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
from enum import Enum

from docutils.nodes import Element
from sphinx.domains.python import PyXRefRole
from sphinx.environment import BuildEnvironment
from sphinx.util import logging

import telegram

# get the sphinx(!) logger
# Makes sure logs render in red and also plays nicely with e.g. the `nitpicky` option.
sphinx_logger = logging.getLogger(__name__)

CONSTANTS_ROLE = "tg-const"


class TGConstXRefRole(PyXRefRole):
    """This is a bit of Sphinx magic. We add a new role type called tg-const that allows us to
    reference values from the `telegram.constants.module` while using the actual value as title
    of the link.

    Example:

        :tg-const:`telegram.constants.MessageLimit.MAX_TEXT_LENGTH` renders as `4096` but links to
        the constant.
    """

    def process_link(
        self,
        env: BuildEnvironment,
        refnode: Element,
        has_explicit_title: bool,
        title: str,
        target: str,
    ) -> tuple[str, str]:
        title, target = super().process_link(env, refnode, has_explicit_title, title, target)
        try:
            # We use `eval` to get the value of the expression. Maybe there are better ways to
            # do this via importlib or so, but it does the job for now
            value = eval(target)
            # Maybe we need a better check if the target is actually from tg.constants
            # for now checking if it's an Enum suffices since those are used nowhere else in PTB
            if isinstance(value, Enum):
                # Special casing for file size limits
                if isinstance(value, telegram.constants.FileSizeLimit):
                    return f"{int(value.value / 1e6)} MB", target
                return repr(value.value), target
            # Just for (Bot API) versions number auto add in constants:
            if isinstance(value, str) and target in (
                "telegram.constants.BOT_API_VERSION",
                "telegram.__version__",
            ):
                return value, target
            if isinstance(value, tuple) and target in (
                "telegram.constants.BOT_API_VERSION_INFO",
                "telegram.__version_info__",
            ):
                return repr(value), target
            sphinx_logger.warning(
                f"%s:%d: WARNING: Did not convert reference %s. :{CONSTANTS_ROLE}: is not supposed"
                " to be used with this type of target.",
                refnode.source,
                refnode.line,
                refnode.rawsource,
            )
            return title, target
        except Exception as exc:
            sphinx_logger.exception(
                "%s:%d: WARNING: Did not convert reference %s due to an exception.",
                refnode.source,
                refnode.line,
                refnode.rawsource,
                exc_info=exc,
            )
            return title, target
