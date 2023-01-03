#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This tests whether our submodules have __all__ or not.
Additionally also tests if all public submodules are included in __all__ for __init__'s.
"""
import importlib
import os
from pathlib import Path


def test_public_submodules_dunder_all():
    modules_to_search = list(Path("telegram").rglob("*.py"))

    if not modules_to_search:
        raise AssertionError("No modules found to search through, please modify this test.")

    for mod_path in modules_to_search:
        path = str(mod_path)
        folder = mod_path.parent

        if mod_path.name == "__init__.py" and "_" not in path[:-11]:  # init of public submodules
            mod = load_module(mod_path)
            assert hasattr(mod, "__all__"), f"{folder}'s __init__ does not have an __all__!"

            pub_mods = get_public_submodules_in_folder(folder)
            cond = all(pub_mod in mod.__all__ for pub_mod in pub_mods)

            assert cond, f"{path}'s __all__ should contain all public submodules ({pub_mods})!"
            continue

        if "_" in path:  # skip private modules
            continue

        mod = load_module(mod_path)
        assert hasattr(mod, "__all__"), f"{mod_path.name} does not have an __all__!"


def load_module(path: Path):
    if path.name == "__init__.py":
        mod_name = str(path.parent).replace(os.sep, ".")  # telegram(.ext) format
    else:
        mod_name = f"{path.parent}.{path.stem}".replace(os.sep, ".")  # telegram(.ext).(...) format
    return importlib.import_module(mod_name)


def get_public_submodules_in_folder(path: Path):
    return [i.stem for i in path.glob("[!_]*.py")]
