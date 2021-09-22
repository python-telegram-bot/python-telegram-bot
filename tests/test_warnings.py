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
import pathlib
from collections import defaultdict

import pytest

from telegram.utils.warnings import warn
from telegram.warnings import PTBUserWarning, PTBRuntimeWarning, PTBDeprecationWarning


class TestWarnings:
    @pytest.mark.parametrize(
        "inst",
        [
            (PTBUserWarning("test message")),
            (PTBRuntimeWarning("test message")),
            (PTBDeprecationWarning()),
        ],
    )
    def test_slots_behavior(self, inst, mro_slots):
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_test_coverage(self):
        """This test is only here to make sure that new warning classes will set __slots__
        properly.
        Add the new warning class to the below covered_subclasses dict, if it's covered in the
        above test_slots_behavior tests.
        """

        def make_assertion(cls):
            assert set(cls.__subclasses__()) == covered_subclasses[cls]
            for subcls in cls.__subclasses__():
                make_assertion(subcls)

        covered_subclasses = defaultdict(set)
        covered_subclasses.update(
            {
                PTBUserWarning: {
                    PTBRuntimeWarning,
                    PTBDeprecationWarning,
                },
            }
        )

        make_assertion(PTBUserWarning)

    def test_warn(self, recwarn):
        expected_file = (
            pathlib.Path(__file__).parent.parent.resolve() / 'telegram' / 'utils' / 'warnings.py'
        )

        warn('test message')
        assert len(recwarn) == 1
        assert recwarn[0].category is PTBUserWarning
        assert str(recwarn[0].message) == 'test message'
        assert pathlib.Path(recwarn[0].filename) == expected_file, "incorrect stacklevel!"

        warn('test message 2', category=PTBRuntimeWarning)
        assert len(recwarn) == 2
        assert recwarn[1].category is PTBRuntimeWarning
        assert str(recwarn[1].message) == 'test message 2'
        assert pathlib.Path(recwarn[1].filename) == expected_file, "incorrect stacklevel!"

        warn('test message 3', stacklevel=1, category=PTBDeprecationWarning)
        expected_file = pathlib.Path(__file__)
        assert len(recwarn) == 3
        assert recwarn[2].category is PTBDeprecationWarning
        assert str(recwarn[2].message) == 'test message 3'
        assert pathlib.Path(recwarn[2].filename) == expected_file, "incorrect stacklevel!"
