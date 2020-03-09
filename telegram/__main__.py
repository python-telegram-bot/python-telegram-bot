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
import future


from . import __version__ as telegram_ver


def _git_revision():
    try:
        output = subprocess.check_output(["git", "describe", "--long", "--tags"],
                                         stderr=subprocess.STDOUT)
    except (subprocess.SubprocessError, OSError):
        return None
    return output.decode().strip()


def print_ver_info():
    git_revision = _git_revision()
    print('python-telegram-bot {0}'.format(telegram_ver) + (' ({0})'.format(git_revision)
                                                            if git_revision else ''))
    print('certifi {0}'.format(certifi.__version__))
    print('future {0}'.format(future.__version__))
    print('Python {0}'.format(sys.version.replace('\n', ' ')))


def main():
    print_ver_info()


if __name__ == '__main__':
    main()
