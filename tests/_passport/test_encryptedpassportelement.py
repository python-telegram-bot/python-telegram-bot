#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

import datetime as dtm

import pytest

from telegram import EncryptedPassportElement, PassportElementError, PassportFile
from telegram._utils.datetime import UTC
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def encrypted_passport_element():
    return EncryptedPassportElement(
        EncryptedPassportElementTestBase.type_,
        "this is a hash",
        data=EncryptedPassportElementTestBase.data,
        phone_number=EncryptedPassportElementTestBase.phone_number,
        email=EncryptedPassportElementTestBase.email,
        files=EncryptedPassportElementTestBase.files,
        front_side=EncryptedPassportElementTestBase.front_side,
        reverse_side=EncryptedPassportElementTestBase.reverse_side,
        selfie=EncryptedPassportElementTestBase.selfie,
        translation=EncryptedPassportElementTestBase.translation,
    )


class EncryptedPassportElementTestBase:
    type_ = "driver_license"
    hash = "this is a hash"
    data = "data"
    phone_number = "phone_number"
    email = "email"
    passport_file = PassportFile(
        file_id="file_id",
        file_unique_id="file_unique_id",
        file_date=dtm.datetime(2026, 1, 1, tzinfo=UTC),
        file_size=25,
    )
    files = [passport_file]
    front_side = passport_file
    reverse_side = passport_file
    selfie = passport_file
    translation = [passport_file]


class TestEncryptedPassportElementWithoutRequest(
    EncryptedPassportElementTestBase, DeserializationTestBase
):
    de_json_class = EncryptedPassportElement

    @pytest.fixture
    def de_json_dict(self):
        # Telegram only sends the fields that fit the type of the element. We set all of them
        # so that every argument is tested.
        return {
            "type": self.type_,
            "hash": self.hash,
            "data": self.data,
            "phone_number": self.phone_number,
            "email": self.email,
            "files": [passport_file.to_dict() for passport_file in self.files],
            "front_side": self.front_side.to_dict(),
            "reverse_side": self.reverse_side.to_dict(),
            "selfie": self.selfie.to_dict(),
            "translation": [passport_file.to_dict() for passport_file in self.translation],
        }

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
        assert encrypted_passport_element.translation == tuple(self.translation)

    def test_de_json(self, offline_bot, de_json_dict):
        element = EncryptedPassportElement.de_json(de_json_dict, offline_bot)
        assert element.api_kwargs == {}

        assert element.type == self.type_
        assert element.hash == self.hash
        assert element.data == self.data
        assert element.phone_number == self.phone_number
        assert element.email == self.email
        assert element.files == tuple(self.files)
        assert element.front_side == self.front_side
        assert element.reverse_side == self.reverse_side
        assert element.selfie == self.selfie
        assert element.translation == tuple(self.translation)

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
