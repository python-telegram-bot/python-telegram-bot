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
import abc
import threading

import pytest
import inspect

import telegram
import telegram.ext
from telegram.ext.utils import promise, webhookhandler
from telegram.utils.helpers import DefaultValue
from telegram.utils.request import Request


@pytest.fixture(scope='function')
def tg_classes():
    tg_classes = inspect.getmembers(telegram, inspect.isclass)
    tg_ext_classes = inspect.getmembers(telegram.ext, inspect.isclass)
    utils_classes = [
        ('Promise', promise.Promise),
        ('WebhookServer', webhookhandler.WebhookServer),
        ('DefaultValue', DefaultValue),
        ('Request', Request),
    ]

    tg_classes.extend(tg_ext_classes)
    tg_classes.extend(utils_classes)
    return tg_classes


def test_class_has_slots(tg_classes):
    for name, cls in tg_classes:
        assert getattr(cls, '__slots__', 'err') != 'err', f"class {name} doesn't have __slots__"


def test_class_slots_has_dict(tg_classes):
    for name, cls in tg_classes:
        # Following classes' parents have '__dict__' in them so they're skipped
        if issubclass(cls, (telegram.TelegramError, Exception, BaseException)):
            continue
        attrs = set()
        for child in cls.__mro__[:-1]:  # Get MRO to get all slots
            # These classes don't have __slots__, so add dict manually.
            if issubclass(child, (threading.Thread, abc.ABC)):
                attrs.add('__dict__')
            else:
                for attr in child.__slots__:
                    attrs.add(attr)

        assert '__dict__' in attrs, f"class {name} doesn't have __dict__"
