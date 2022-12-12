#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2022
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
"""Below classes are used in the tests to allow monkeypatching attributes since parent classes
don't have __dict__.
"""
from telegram import Bot
from telegram.ext import Application, ExtBot


class DictExtBot(ExtBot):
    pass


class DictBot(Bot):
    pass


class DictApplication(Application):
    pass


def mro_slots(cls, only_parents: bool = False):
    """Returns a list of all slots of a class and its parents.

    Args:
        cls (:obj:`type`): The class to get the slots from.
        only_parents (:obj:`bool`, optional): If ``True``, only the slots of the parents are
            returned. Defaults to ``False``.
    """
    if only_parents:
        classes = cls.__class__.__mro__[1:-1]
    else:
        classes = cls.__class__.__mro__[:-1]

    return [
        attr
        for cls in classes
        if hasattr(cls, "__slots__")  # The Exception class doesn't have slots
        for attr in cls.__slots__
        if attr != "__dict__"  # left here for classes which still has __dict__
    ]
