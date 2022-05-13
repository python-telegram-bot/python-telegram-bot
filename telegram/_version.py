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
# pylint: disable=missing-module-docstring
from typing import NamedTuple, Dict
from telegram import constants

_RELEASE_LEVEL_SHORTHANDS: Dict[str, str] = {
    "alpha": "a",
    "beta": "b",
    "candidate": "rc",
    "final": "final",
}


class Version(NamedTuple):
    """Copies the behavior of sys.version_info.
    serial is always 0 for stable releases.
    """

    major: int
    minor: int
    micro: int
    releaselevel: str  # Literal['alpha', 'beta', 'candidate', 'final']
    serial: int

    def _rl_shorthand(self) -> str:
        return _RELEASE_LEVEL_SHORTHANDS[self.releaselevel]

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}"
        if self.micro != 0:
            version = f"{version}.{self.micro}"
        if self.releaselevel != "final":
            version = f"{version}{self._rl_shorthand()}{self.serial}"

        return version


__version_info__ = Version(major=20, minor=0, micro=0, releaselevel="alpha", serial=0)
__version__ = str(__version_info__)

__bot_api_version__ = constants.BOT_API_VERSION
__bot_api_version_info__ = constants.BOT_API_VERSION_INFO
