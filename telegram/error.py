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
"""This module contains a object that represents a Telegram Error."""


def _lstrip_str(in_s, lstr):
    """
    Args:
        in_s (str): in string
        lstr (str): substr to strip from left side

    Returns:
        str:

    """
    if in_s.startswith(lstr):
        res = in_s[len(lstr):]
    else:
        res = in_s
    return res


class TelegramError(Exception):
    """This object represents a Telegram Error."""

    def __init__(self, message):
        """
        Args:
            message (str):

        Returns:

        """
        super(TelegramError, self).__init__()

        msg = _lstrip_str(message, 'Error: ')
        msg = _lstrip_str(msg, '[Error]: ')
        if msg != message:
            # api_error - capitalize the msg...
            msg = msg.capitalize()
        self.message = msg

    def __str__(self):
        return '%s' % (self.message)


class Unauthorized(TelegramError):

    def __init__(self):
        super(Unauthorized, self).__init__('Unauthorized')


class InvalidToken(TelegramError):

    def __init__(self):
        super(InvalidToken, self).__init__('Invalid token')


class NetworkError(TelegramError):
    pass


class TimedOut(NetworkError):

    def __init__(self):
        super(TimedOut, self).__init__('Timed out')
