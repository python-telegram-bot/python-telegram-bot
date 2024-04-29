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

from telegram.ext import BaseHandler
from tests.auxil.slots import mro_slots


class TestHandler:
    def test_slot_behaviour(self):
        class SubclassHandler(BaseHandler):
            __slots__ = ()

            def __init__(self):
                super().__init__(lambda x: None)

            def check_update(self, update: object):
                pass

        inst = SubclassHandler()
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_repr(self):
        async def some_func():
            return None

        class SubclassHandler(BaseHandler):
            __slots__ = ()

            def __init__(self):
                super().__init__(callback=some_func)

            def check_update(self, update: object):
                pass

        sh = SubclassHandler()
        assert repr(sh) == "SubclassHandler[callback=TestHandler.test_repr.<locals>.some_func]"

    def test_repr_no_qualname(self):
        class ClassBasedCallback:
            async def __call__(self, *args, **kwargs):
                pass

            def __repr__(self):
                return "Repr of ClassBasedCallback"

        class SubclassHandler(BaseHandler):
            __slots__ = ()

            def __init__(self):
                super().__init__(callback=ClassBasedCallback())

            def check_update(self, update: object):
                pass

        sh = SubclassHandler()
        assert repr(sh) == "SubclassHandler[callback=Repr of ClassBasedCallback]"
