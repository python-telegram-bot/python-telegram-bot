#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
"""This module facilitates the deprecation of functions"""

import warnings


def deprecate(func, old, new):
    """Warn users invoking old to switch to the new function."""

    def f(*args, **kwargs):
        warnings.warn("{0} is being deprecated, please use {1} from now on".format(old, new))
        return func(*args, **kwargs)

    return f


def deprecate_network_delay(timeout, total_timeout, **kwargs):
    if 'network_delay' in kwargs:
        warnings.warn('start_polling(): network_delay is being deprecated, please use '
                      'total_timeout from now on')
        if timeout is not None:
            network_delay = kwargs['network_delay']
            if network_delay is not None:
                total_timeout = timeout + network_delay
            else:
                warnings.warn('start_polling(): network_delay is ignored becuase it is None')
        else:
            warnings.warn('start_polling(): network_delay is ignored because timeout is None')

    return total_timeout
