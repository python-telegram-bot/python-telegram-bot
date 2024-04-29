#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
import importlib
import inspect
import os
from pathlib import Path

included = {  # These modules/classes intentionally have __dict__.
    "CallbackContext",
}


def test_class_has_slots_and_no_dict():
    tg_paths = Path("telegram").rglob("*.py")

    for path in tg_paths:
        if "__" in str(path):  # Exclude __init__, __main__, etc
            continue
        mod_name = str(path)[:-3].replace(os.sep, ".")
        module = importlib.import_module(mod_name)  # import module to get classes in it.

        for name, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__ or any(  # exclude 'imported' modules
                x in name for x in ("__class__", "__init__", "Queue", "Webhook")
            ):
                continue

            assert "__slots__" in cls.__dict__, f"class '{name}' in {path} doesn't have __slots__"
            # if the class slots is a string, then mro_slots() iterates through that string (bad).
            assert not isinstance(cls.__slots__, str), f"{name!r}s slots shouldn't be strings"

            # specify if a certain module/class/base class should have dict-
            if any(i in included for i in (cls.__module__, name, cls.__base__.__name__)):
                assert "__dict__" in get_slots(cls), f"class {name!r} ({path}) has no __dict__"
                continue

            assert "__dict__" not in get_slots(cls), f"class '{name}' in {path} has __dict__"


def get_slots(_class):
    return [attr for cls in _class.__mro__ if hasattr(cls, "__slots__") for attr in cls.__slots__]
