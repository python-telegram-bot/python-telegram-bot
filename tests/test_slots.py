#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
import importlib.util
import os
from glob import iglob

import inspect


excluded = {
    'telegram.error',
    '_ConversationTimeoutContext',
    'DispatcherHandlerStop',
    'Days',
    'telegram.deprecate',
    'TelegramDecryptionError',
    'ContextTypes',
    'CallbackDataCache',
    'InvalidCallbackData',
    '_KeyboardData',
}  # These modules/classes intentionally don't have __dict__.


def test_class_has_slots_and_dict(mro_slots):
    tg_paths = [p for p in iglob("telegram/**/*.py", recursive=True) if 'vendor' not in p]

    for path in tg_paths:
        # windows uses backslashes:
        if os.name == 'nt':
            split_path = path.split('\\')
        else:
            split_path = path.split('/')
        mod_name = f"telegram{'.ext.' if split_path[1] == 'ext' else '.'}{split_path[-1][:-3]}"
        spec = importlib.util.spec_from_file_location(mod_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # Exec module to get classes in it.

        for name, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__ or any(  # exclude 'imported' modules
                x in name for x in {'__class__', '__init__', 'Queue', 'Webhook'}
            ):
                continue
            assert '__slots__' in cls.__dict__, f"class '{name}' in {path} doesn't have __slots__"
            if cls.__module__ in excluded or name in excluded:
                continue
            assert '__dict__' in get_slots(cls), f"class '{name}' in {path} doesn't have __dict__"


def get_slots(_class):
    slots = [attr for cls in _class.__mro__ if hasattr(cls, '__slots__') for attr in cls.__slots__]

    # We're a bit hacky here to handle cases correctly, where we can't read the parents slots from
    # the mro
    if '__dict__' not in slots:
        try:

            class Subclass(_class):
                __slots__ = ('__dict__',)

        except TypeError as exc:
            if '__dict__ slot disallowed: we already got one' in str(exc):
                slots.append('__dict__')
            else:
                raise exc

    return slots
