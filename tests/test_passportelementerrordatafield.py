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

from telegram import PassportElementErrorDataField, PassportElementErrorSelfie


@pytest.fixture(scope="module")
def passport_element_error_data_field():
    return PassportElementErrorDataField(
        Space.type_,
        Space.field_name,
        Space.data_hash,
        Space.message,
    )


class Space:
    source = "data"
    type_ = "test_type"
    field_name = "test_field"
    data_hash = "data_hash"
    message = "Error message"


class TestPassportElementErrorDataFieldNoReq:
    def test_slot_behaviour(self, passport_element_error_data_field, mro_slots):
        inst = passport_element_error_data_field
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, passport_element_error_data_field):
        assert passport_element_error_data_field.source == Space.source
        assert passport_element_error_data_field.type == Space.type_
        assert passport_element_error_data_field.field_name == Space.field_name
        assert passport_element_error_data_field.data_hash == Space.data_hash
        assert passport_element_error_data_field.message == Space.message

    def test_to_dict(self, passport_element_error_data_field):
        passport_element_error_data_field_dict = passport_element_error_data_field.to_dict()

        assert isinstance(passport_element_error_data_field_dict, dict)
        assert (
            passport_element_error_data_field_dict["source"]
            == passport_element_error_data_field.source
        )
        assert (
            passport_element_error_data_field_dict["type"]
            == passport_element_error_data_field.type
        )
        assert (
            passport_element_error_data_field_dict["field_name"]
            == passport_element_error_data_field.field_name
        )
        assert (
            passport_element_error_data_field_dict["data_hash"]
            == passport_element_error_data_field.data_hash
        )
        assert (
            passport_element_error_data_field_dict["message"]
            == passport_element_error_data_field.message
        )

    def test_equality(self):
        a = PassportElementErrorDataField(
            Space.type_, Space.field_name, Space.data_hash, Space.message
        )
        b = PassportElementErrorDataField(
            Space.type_, Space.field_name, Space.data_hash, Space.message
        )
        c = PassportElementErrorDataField(Space.type_, "", "", "")
        d = PassportElementErrorDataField("", Space.field_name, "", "")
        e = PassportElementErrorDataField("", "", Space.data_hash, "")
        f = PassportElementErrorDataField("", "", "", Space.message)
        g = PassportElementErrorSelfie(Space.type_, "", Space.message)

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

        assert a != g
        assert hash(a) != hash(g)
