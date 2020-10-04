# !/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
import sys
import subprocess

import certifi

from typing import Optional

from . import __version__ as telegram_ver


def _git_revision() -> Optional[str]:
    try:
        output = subprocess.check_output(["git", "describe", "--long", "--tags"],
                                         stderr=subprocess.STDOUT)
    except (subprocess.SubprocessError, OSError):
        return None
    return output.decode().strip()


def print_ver_info() -> None:
    git_revision = _git_revision()
    print('python-telegram-bot {}'.format(telegram_ver) + (' ({})'.format(git_revision)
                                                           if git_revision else ''))
    print('certifi {}'.format(certifi.__version__))  # type: ignore[attr-defined]
    print('Python {}'.format(sys.version.replace('\n', ' ')))


def main() -> None:
    print_ver_info()


if __name__ == '__main__':
    main()
