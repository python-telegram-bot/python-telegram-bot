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

import pytest

from telegram import IdDocumentData, PersonalDetails, ResidentialAddress
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots

# Telegram doesn't send these classes directly: they are the decrypted content of
# EncryptedPassportElement.data, see https://core.telegram.org/passport#fields


def check_slots(inst):
    for attr in inst.__slots__:
        assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
    assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"


class TestPersonalDetailsWithoutRequest(DeserializationTestBase):
    de_json_class = PersonalDetails

    @pytest.fixture
    def de_json_dict(self):
        return {
            "first_name": "FIRSTNAME",
            "last_name": "LASTNAME",
            "middle_name": "MIDDLENAME",
            "birth_date": "01.01.2001",
            "gender": "female",
            "country_code": "DK",
            "residence_country_code": "DK",
            "first_name_native": "FIRSTNAMENATIVE",
            "last_name_native": "LASTNAMENATIVE",
            "middle_name_native": "MIDDLENAMENATIVE",
        }

    def test_slot_behaviour(self, de_json_dict):
        check_slots(PersonalDetails.de_json(de_json_dict))

    def test_de_json(self, offline_bot, de_json_dict):
        personal_details = PersonalDetails.de_json(de_json_dict, offline_bot)
        assert personal_details.api_kwargs == {}

        assert personal_details.first_name == "FIRSTNAME"
        assert personal_details.last_name == "LASTNAME"
        assert personal_details.middle_name == "MIDDLENAME"
        assert personal_details.birth_date == "01.01.2001"
        assert personal_details.gender == "female"
        assert personal_details.country_code == "DK"
        assert personal_details.residence_country_code == "DK"
        assert personal_details.first_name_native == "FIRSTNAMENATIVE"
        assert personal_details.last_name_native == "LASTNAMENATIVE"
        assert personal_details.middle_name_native == "MIDDLENAMENATIVE"


class TestResidentialAddressWithoutRequest(DeserializationTestBase):
    de_json_class = ResidentialAddress

    @pytest.fixture
    def de_json_dict(self):
        return {
            "street_line1": "STREET_LINE1",
            "street_line2": "STREET_LINE2",
            "city": "CITY",
            "state": "STATE",
            "country_code": "DK",
            "post_code": "POSTCODE",
        }

    def test_slot_behaviour(self, de_json_dict):
        check_slots(ResidentialAddress.de_json(de_json_dict))

    def test_de_json(self, offline_bot, de_json_dict):
        residential_address = ResidentialAddress.de_json(de_json_dict, offline_bot)
        assert residential_address.api_kwargs == {}

        assert residential_address.street_line1 == "STREET_LINE1"
        assert residential_address.street_line2 == "STREET_LINE2"
        assert residential_address.city == "CITY"
        assert residential_address.state == "STATE"
        assert residential_address.country_code == "DK"
        assert residential_address.post_code == "POSTCODE"


class TestIdDocumentDataWithoutRequest(DeserializationTestBase):
    de_json_class = IdDocumentData

    @pytest.fixture
    def de_json_dict(self):
        return {"document_no": "DOCUMENT_NO", "expiry_date": "01.01.2001"}

    def test_slot_behaviour(self, de_json_dict):
        check_slots(IdDocumentData.de_json(de_json_dict))

    def test_de_json(self, offline_bot, de_json_dict):
        id_document_data = IdDocumentData.de_json(de_json_dict, offline_bot)
        assert id_document_data.api_kwargs == {}

        assert id_document_data.document_no == "DOCUMENT_NO"
        assert id_document_data.expiry_date == "01.01.2001"
