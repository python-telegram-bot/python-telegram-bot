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

from telegram import PassportElementErrorFrontSide, PassportElementErrorSelfie
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def passport_element_error_front_side():
    return PassportElementErrorFrontSide(
        TestPassportElementErrorFrontSideBase.type_,
        TestPassportElementErrorFrontSideBase.file_hash,
        TestPassportElementErrorFrontSideBase.message,
    )


class TestPassportElementErrorFrontSideBase:
    source = "front_side"
    type_ = "test_type"
    file_hash = "file_hash"
    message = "Error message"


class TestPassportElementErrorFrontSideWithoutRequest(TestPassportElementErrorFrontSideBase):
    def test_slot_behaviour(self, passport_element_error_front_side):
        inst = passport_element_error_front_side
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, passport_element_error_front_side):
        assert passport_element_error_front_side.source == self.source
        assert passport_element_error_front_side.type == self.type_
        assert passport_element_error_front_side.file_hash == self.file_hash
        assert passport_element_error_front_side.message == self.message

    def test_to_dict(self, passport_element_error_front_side):
        passport_element_error_front_side_dict = passport_element_error_front_side.to_dict()

        assert isinstance(passport_element_error_front_side_dict, dict)
        assert (
            passport_element_error_front_side_dict["source"]
            == passport_element_error_front_side.source
        )
        assert (
            passport_element_error_front_side_dict["type"]
            == passport_element_error_front_side.type
        )
        assert (
            passport_element_error_front_side_dict["file_hash"]
            == passport_element_error_front_side.file_hash
        )
        assert (
            passport_element_error_front_side_dict["message"]
            == passport_element_error_front_side.message
        )

    def test_equality(self):
        a = PassportElementErrorFrontSide(self.type_, self.file_hash, self.message)
        b = PassportElementErrorFrontSide(self.type_, self.file_hash, self.message)
        c = PassportElementErrorFrontSide(self.type_, "", "")
        d = PassportElementErrorFrontSide("", self.file_hash, "")
        e = PassportElementErrorFrontSide("", "", self.message)
        f = PassportElementErrorSelfie(self.type_, self.file_hash, self.message)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)
