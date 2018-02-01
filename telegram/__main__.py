# !/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

import certifi
import future

from . import __version__ as telegram_ver


def print_ver_info():
    print('python-telegram-bot {0}'.format(telegram_ver))
    print('certifi {0}'.format(certifi.__version__))
    print('future {0}'.format(future.__version__))
    print('Python {0}'.format(sys.version.replace('\n', ' ')))


def main():
    print_ver_info()


if __name__ == '__main__':
    main()
