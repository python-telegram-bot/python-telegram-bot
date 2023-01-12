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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import pytest

from telegram import PassportElementErrorDataField, PassportElementErrorUnspecified


@pytest.fixture(scope="module")
def passport_element_error_unspecified():
    return PassportElementErrorUnspecified(Space.type_, Space.element_hash, Space.message)


class Space:
    source = "unspecified"
    type_ = "test_type"
    element_hash = "element_hash"
    message = "Error message"


class TestPassportElementErrorUnspecifiedWithoutRequest:
    def test_slot_behaviour(self, passport_element_error_unspecified, mro_slots):
        inst = passport_element_error_unspecified
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, passport_element_error_unspecified):
        assert passport_element_error_unspecified.source == Space.source
        assert passport_element_error_unspecified.type == Space.type_
        assert passport_element_error_unspecified.element_hash == Space.element_hash
        assert passport_element_error_unspecified.message == Space.message

    def test_to_dict(self, passport_element_error_unspecified):
        passport_element_error_unspecified_dict = passport_element_error_unspecified.to_dict()

        assert isinstance(passport_element_error_unspecified_dict, dict)
        assert (
            passport_element_error_unspecified_dict["source"]
            == passport_element_error_unspecified.source
        )
        assert (
            passport_element_error_unspecified_dict["type"]
            == passport_element_error_unspecified.type
        )
        assert (
            passport_element_error_unspecified_dict["element_hash"]
            == passport_element_error_unspecified.element_hash
        )
        assert (
            passport_element_error_unspecified_dict["message"]
            == passport_element_error_unspecified.message
        )

    def test_equality(self):
        a = PassportElementErrorUnspecified(Space.type_, Space.element_hash, Space.message)
        b = PassportElementErrorUnspecified(Space.type_, Space.element_hash, Space.message)
        c = PassportElementErrorUnspecified(Space.type_, "", "")
        d = PassportElementErrorUnspecified("", Space.element_hash, "")
        e = PassportElementErrorUnspecified("", "", Space.message)
        f = PassportElementErrorDataField(Space.type_, "", "", Space.message)

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
