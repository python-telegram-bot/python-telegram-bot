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

import pytest

from telegram.ext._utils.trackingdict import TrackingDict
from tests.auxil.slots import mro_slots


@pytest.fixture()
def td() -> TrackingDict:
    td = TrackingDict()
    td.update_no_track({1: 1})
    return td


@pytest.fixture()
def data() -> dict:
    return {1: 1}


class TestTrackingDict:
    def test_slot_behaviour(self, td):
        for attr in td.__slots__:
            assert getattr(td, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(td)) == len(set(mro_slots(td))), "duplicate slot"

    def test_representations(self, td, data):
        assert repr(td) == repr(data)
        assert str(td) == str(data)

    def test_len(self, td, data):
        assert len(td) == len(data)

    def test_boolean(self, td, data):
        assert bool(td) == bool(data)
        assert bool(TrackingDict()) == bool({})

    def test_equality(self, td, data):
        assert td == data
        assert data == td
        assert td != TrackingDict()
        assert TrackingDict() != td
        td_2 = TrackingDict()
        td_2["foo"] = 7
        assert td != td_2
        assert td_2 != td
        assert td != 1
        assert td != 1
        assert td != 5
        assert td != 5

    def test_getitem(self, td):
        assert td[1] == 1
        assert not td.pop_accessed_write_items()
        assert not td.pop_accessed_keys()

    def test_setitem(self, td):
        td[5] = 5
        assert td[5] == 5
        assert td.pop_accessed_write_items() == [(5, 5)]
        td[5] = 7
        assert td[5] == 7
        assert td.pop_accessed_keys() == {5}

    def test_delitem(self, td):
        assert not td.pop_accessed_keys()
        td[5] = 7
        del td[1]
        assert 1 not in td
        assert td.pop_accessed_keys() == {1, 5}
        td[1] = 7
        td[5] = 7
        assert td.pop_accessed_keys() == {1, 5}
        del td[5]
        assert 5 not in td
        assert td.pop_accessed_write_items() == [(5, TrackingDict.DELETED)]

    def test_update_no_track(self, td):
        assert not td.pop_accessed_keys()
        td.update_no_track({2: 2, 3: 3})
        assert td == {1: 1, 2: 2, 3: 3}
        assert not td.pop_accessed_keys()

    def test_pop(self, td):
        td.pop(1)
        assert 1 not in td
        assert td.pop_accessed_keys() == {1}
        td[1] = 7
        td[5] = 8
        assert 1 in td
        assert 5 in td
        assert td.pop_accessed_keys() == {1, 5}
        td.pop(5)
        assert 5 not in td
        assert td.pop_accessed_write_items() == [(5, TrackingDict.DELETED)]

        with pytest.raises(KeyError):
            td.pop(5)

        assert td.pop(5, 8) == 8
        assert 5 not in td
        assert not td.pop_accessed_keys()

        assert td.pop(5, 8) == 8
        assert 5 not in td
        assert not td.pop_accessed_write_items()

    def test_popitem(self, td):
        td.update_no_track({2: 2})
        assert td.popitem() == (1, 1)
        assert 1 not in td
        assert td.pop_accessed_keys() == {1}

        assert td.popitem() == (2, 2)
        assert 2 not in td
        assert not td
        assert td.pop_accessed_write_items() == [(2, TrackingDict.DELETED)]

        with pytest.raises(KeyError):
            td.popitem()

    def test_clear(self, td):
        td.clear()
        assert td == {}
        assert td.pop_accessed_keys() == {1}
        td[5] = 7
        assert 5 in td
        assert td.pop_accessed_keys() == {5}
        td.clear()
        assert td == {}
        assert td.pop_accessed_write_items() == [(5, TrackingDict.DELETED)]

    def test_set_default(self, td):
        assert td.setdefault(1, 2) == 1
        assert td[1] == 1
        assert not td.pop_accessed_keys()
        assert not td.pop_accessed_write_items()

        assert td.setdefault(2, 3) == 3
        assert td[2] == 3
        assert td.pop_accessed_keys() == {2}
        assert td.setdefault(3, 4) == 4
        assert td[3] == 4
        assert td.pop_accessed_write_items() == [(3, 4)]

    def test_iter(self, td, data):
        data.update({2: 2, 3: 3, 4: 4})
        td.update_no_track({2: 2, 3: 3, 4: 4})
        assert not td.pop_accessed_keys()
        assert list(iter(td)) == list(iter(data))

    def test_mark_as_accessed(self, td):
        td[1] = 2
        assert td.pop_accessed_keys() == {1}
        assert td.pop_accessed_keys() == set()
        td.mark_as_accessed(1)
        assert td.pop_accessed_keys() == {1}
