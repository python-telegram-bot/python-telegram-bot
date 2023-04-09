#!/usr/bin/env python
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
import inspect


def mro_slots(obj, only_parents: bool = False):
    """Returns a list of all slots of a class and its parents.
    Args:
        obj (:obj:`type`): The class or class-instance to get the slots from.
        only_parents (:obj:`bool`, optional): If ``True``, only the slots of the parents are
            returned. Defaults to ``False``.
    """
    cls = obj if inspect.isclass(obj) else obj.__class__

    classes = cls.__mro__[1:] if only_parents else cls.__mro__

    return [
        attr
        for cls in classes
        if hasattr(cls, "__slots__")  # The Exception class doesn't have slots
        for attr in cls.__slots__
    ]
