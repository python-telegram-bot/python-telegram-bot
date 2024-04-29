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

from telegram import EncryptedPassportElement, PassportElementError, PassportFile
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def encrypted_passport_element():
    return EncryptedPassportElement(
        TestEncryptedPassportElementBase.type_,
        "this is a hash",
        data=TestEncryptedPassportElementBase.data,
        phone_number=TestEncryptedPassportElementBase.phone_number,
        email=TestEncryptedPassportElementBase.email,
        files=TestEncryptedPassportElementBase.files,
        front_side=TestEncryptedPassportElementBase.front_side,
        reverse_side=TestEncryptedPassportElementBase.reverse_side,
        selfie=TestEncryptedPassportElementBase.selfie,
    )


class TestEncryptedPassportElementBase:
    type_ = "type"
    hash = "this is a hash"
    data = "data"
    phone_number = "phone_number"
    email = "email"
    files = [PassportFile("file_id", 50, 0, 25)]
    front_side = PassportFile("file_id", 50, 0, 25)
    reverse_side = PassportFile("file_id", 50, 0, 25)
    selfie = PassportFile("file_id", 50, 0, 25)


class TestEncryptedPassportElementWithoutRequest(TestEncryptedPassportElementBase):
    def test_slot_behaviour(self, encrypted_passport_element):
        inst = encrypted_passport_element
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, encrypted_passport_element):
        assert encrypted_passport_element.type == self.type_
        assert encrypted_passport_element.hash == self.hash
        assert encrypted_passport_element.data == self.data
        assert encrypted_passport_element.phone_number == self.phone_number
        assert encrypted_passport_element.email == self.email
        assert encrypted_passport_element.files == tuple(self.files)
        assert encrypted_passport_element.front_side == self.front_side
        assert encrypted_passport_element.reverse_side == self.reverse_side
        assert encrypted_passport_element.selfie == self.selfie

    def test_to_dict(self, encrypted_passport_element):
        encrypted_passport_element_dict = encrypted_passport_element.to_dict()

        assert isinstance(encrypted_passport_element_dict, dict)
        assert encrypted_passport_element_dict["type"] == encrypted_passport_element.type
        assert encrypted_passport_element_dict["data"] == encrypted_passport_element.data
        assert (
            encrypted_passport_element_dict["phone_number"]
            == encrypted_passport_element.phone_number
        )
        assert encrypted_passport_element_dict["email"] == encrypted_passport_element.email
        assert isinstance(encrypted_passport_element_dict["files"], list)
        assert (
            encrypted_passport_element_dict["front_side"]
            == encrypted_passport_element.front_side.to_dict()
        )
        assert (
            encrypted_passport_element_dict["reverse_side"]
            == encrypted_passport_element.reverse_side.to_dict()
        )
        assert (
            encrypted_passport_element_dict["selfie"]
            == encrypted_passport_element.selfie.to_dict()
        )

    def test_attributes_always_tuple(self):
        element = EncryptedPassportElement(self.type_, self.hash)
        assert element.files == ()
        assert element.translation == ()

    def test_equality(self):
        a = EncryptedPassportElement(self.type_, self.hash, data=self.data)
        b = EncryptedPassportElement(self.type_, self.hash, data=self.data)
        c = EncryptedPassportElement(self.data, "")
        d = PassportElementError("source", "type", "message")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
