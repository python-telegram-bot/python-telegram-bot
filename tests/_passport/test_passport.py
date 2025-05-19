#!/usr/bin/env python
# flake8: noqa: E501
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
from copy import deepcopy

import pytest

from telegram import (
    Bot,
    Credentials,
    File,
    PassportData,
    PassportElementErrorDataField,
    PassportElementErrorSelfie,
    PassportFile,
)
from telegram.error import PassportDecryptionError

# Note: All classes in telegram.credentials (except EncryptedCredentials) aren't directly tested
# here, although they are implicitly tested. Testing for those classes was too much work and not
# worth it.
from telegram.request import RequestData
from tests.auxil.pytest_classes import make_bot
from tests.auxil.slots import mro_slots

RAW_PASSPORT_DATA = {
    "credentials": {
        "hash": "qB4hz2LMcXYhglwz6EvXMMyI3PURisWLXl/iCmCXcSk=",
        "secret": "O6x3X2JrLO1lUIhw48os1gaenDuZLhesoZMKXehZwtM3vsxOdtxHKWQyLNwtbyy4snYpARXDwf8f1QHNmQ/M1PwBQvk1ozrZBXb4a6k/iYj+P4v8Xw2M++CRHqZv0LaxFtyHOXnNYZ6dXpNeF0ZvYYTmm0FsYvK+/3/F6VDB3Oe6xWlXFLwaCCP/jA9i2+dKp6iq8NLOo4VnxenPKWWYz20RZ50MdAbS3UR+NCx4AHM2P5DEGrHNW0tMXJ+FG3jpVrit5BuCbB/eRgKxNGRWNxEGV5hun5MChdxKCEHCimnUA97h7MZdoTgYxkrfvDSZ/V89BnFXLdr87t/NLvVE0Q==",
        "data": "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",
    },
    "data": [
        {
            "data": "QRfzWcCN4WncvRO3lASG+d+c5gzqXtoCinQ1PgtYiZMKXCksx9eB9Ic1bOt8C/un9/XaX220PjJSO7Kuba+nXXC51qTsjqP9rnLKygnEIWjKrfiDdklzgcukpRzFSjiOAvhy86xFJZ1PfPSrFATy/Gp1RydLzbrBd2ZWxZqXrxcMoA0Q2UTTFXDoCYerEAiZoD69i79tB/6nkLBcUUvN5d52gKd/GowvxWqAAmdO6l1N7jlo6aWjdYQNBAK1KHbJdbRZMJLxC1MqMuZXAYrPoYBRKr5xAnxDTmPn/LEZKLc3gwwZyEgR5x7e9jp5heM6IEMmsv3O/6SUeEQs7P0iVuRSPLMJLfDdwns8Tl3fF2M4IxKVovjCaOVW+yHKsADDAYQPzzH2RcrWVD0TP5I64mzpK64BbTOq3qm3Hn51SV9uA/+LvdGbCp7VnzHx4EdUizHsVyilJULOBwvklsrDRvXMiWmh34ZSR6zilh051tMEcRf0I+Oe7pIxVJd/KKfYA2Z/eWVQTCn5gMuAInQNXFSqDIeIqBX+wca6kvOCUOXB7J2uRjTpLaC4DM9s/sNjSBvFixcGAngt+9oap6Y45rQc8ZJaNN/ALqEJAmkphW8=",
            "type": "personal_details",
            "hash": "What to put here?",
        },
        {
            "reverse_side": {
                "file_size": 32424112,
                "file_date": 1534074942,
                "file_id": "DgADBAADNQQAAtoagFPf4wwmFZdmyQI",
                "file_unique_id": "adc3145fd2e84d95b64d68eaa22aa33e",
            },
            "translation": [
                {
                    "file_size": 28640,
                    "file_date": 1535630933,
                    "file_id": "DgADBAADswMAAisqQVAmooP-kVgLgAI",
                    "file_unique_id": "52a90d53d6064bb58feb582acdc3a324",
                },
                {
                    "file_size": 28672,
                    "file_date": 1535630933,
                    "file_id": "DgADBAAD1QMAAnrpQFBMZsT3HysjwwI",
                    "file_unique_id": "7285f864d168441ba1f7d02146250432",
                },
            ],
            "front_side": {
                "file_size": 28624,
                "file_date": 1534074942,
                "file_id": "DgADBAADxwMAApnQgVPK2-ckL2eXVAI",
                "file_unique_id": "d9d52a700cbb4a189a80104aa5978133",
            },
            "type": "driver_license",
            "selfie": {
                "file_size": 28592,
                "file_date": 1534074942,
                "file_id": "DgADBAADEQQAAkopgFNr6oi-wISRtAI",
                "file_unique_id": "d4e390cca57b4da5a65322b304762a12",
            },
            "data": "eJUOFuY53QKmGqmBgVWlLBAQCUQJ79n405SX6M5aGFIIodOPQqnLYvMNqTwTrXGDlW+mVLZcbu+y8luLVO8WsJB/0SB7q5WaXn/IMt1G9lz5G/KMLIZG/x9zlnimsaQLg7u8srG6L4KZzv+xkbbHjZdETrxU8j0N/DoS4HvLMRSJAgeFUrY6v2YW9vSRg+fSxIqQy1jR2VKpzAT8OhOz7A==",
            "hash": "We seriously need to improve this mess! took so long to debug!",
        },
        {
            "translation": [
                {
                    "file_size": 28480,
                    "file_date": 1535630939,
                    "file_id": "DgADBAADyQUAAqyqQVC_eoX_KwNjJwI",
                    "file_unique_id": "38b2877b443542cbaf520c6e36a33ac4",
                },
                {
                    "file_size": 28528,
                    "file_date": 1535630939,
                    "file_id": "DgADBAADsQQAAubTQVDRO_FN3lOwWwI",
                    "file_unique_id": "f008ca48c44b4a47895ddbcd2f76741e",
                },
            ],
            "files": [
                {
                    "file_size": 28640,
                    "file_date": 1534074988,
                    "file_id": "DgADBAADLAMAAhwfgVMyfGa5Nr0LvAI",
                    "file_unique_id": "b170748794834644baaa3ec57ee4ce7a",
                },
                {
                    "file_size": 28480,
                    "file_date": 1534074988,
                    "file_id": "DgADBAADaQQAAsFxgVNVfLZuT-_3ZQI",
                    "file_unique_id": "19a12ae34dca424b85e0308f706cee75",
                },
            ],
            "type": "utility_bill",
            "hash": "Wow over 30 minutes spent debugging passport stuff.",
        },
        {
            "data": "j9SksVkSj128DBtZA+3aNjSFNirzv+R97guZaMgae4Gi0oDVNAF7twPR7j9VSmPedfJrEwL3O889Ei+a5F1xyLLyEI/qEBljvL70GFIhYGitS0JmNabHPHSZrjOl8b4s/0Z0Px2GpLO5siusTLQonimdUvu4UPjKquYISmlKEKhtmGATy+h+JDjNCYuOkhakeNw0Rk0BHgj0C3fCb7WZNQSyVb+2GTu6caR6eXf/AFwFp0TV3sRz3h0WIVPW8bna",
            "type": "address",
            "hash": "at least I get the pattern now",
        },
        {"email": "fb3e3i47zt@dispostable.com", "type": "email", "hash": "this should be it."},
    ],
}


@pytest.fixture(scope="module")
def all_passport_data():
    return [
        {
            "type": "personal_details",
            "data": RAW_PASSPORT_DATA["data"][0]["data"],
            "hash": "what to put here?",
        },
        {
            "type": "passport",
            "data": RAW_PASSPORT_DATA["data"][1]["data"],
            "front_side": RAW_PASSPORT_DATA["data"][1]["front_side"],
            "selfie": RAW_PASSPORT_DATA["data"][1]["selfie"],
            "translation": RAW_PASSPORT_DATA["data"][1]["translation"],
            "hash": "more data arghh",
        },
        {
            "type": "internal_passport",
            "data": RAW_PASSPORT_DATA["data"][1]["data"],
            "front_side": RAW_PASSPORT_DATA["data"][1]["front_side"],
            "selfie": RAW_PASSPORT_DATA["data"][1]["selfie"],
            "translation": RAW_PASSPORT_DATA["data"][1]["translation"],
            "hash": "more data arghh",
        },
        {
            "type": "driver_license",
            "data": RAW_PASSPORT_DATA["data"][1]["data"],
            "front_side": RAW_PASSPORT_DATA["data"][1]["front_side"],
            "reverse_side": RAW_PASSPORT_DATA["data"][1]["reverse_side"],
            "selfie": RAW_PASSPORT_DATA["data"][1]["selfie"],
            "translation": RAW_PASSPORT_DATA["data"][1]["translation"],
            "hash": "more data arghh",
        },
        {
            "type": "identity_card",
            "data": RAW_PASSPORT_DATA["data"][1]["data"],
            "front_side": RAW_PASSPORT_DATA["data"][1]["front_side"],
            "reverse_side": RAW_PASSPORT_DATA["data"][1]["reverse_side"],
            "selfie": RAW_PASSPORT_DATA["data"][1]["selfie"],
            "translation": RAW_PASSPORT_DATA["data"][1]["translation"],
            "hash": "more data arghh",
        },
        {
            "type": "utility_bill",
            "files": RAW_PASSPORT_DATA["data"][2]["files"],
            "translation": RAW_PASSPORT_DATA["data"][2]["translation"],
            "hash": "more data arghh",
        },
        {
            "type": "bank_statement",
            "files": RAW_PASSPORT_DATA["data"][2]["files"],
            "translation": RAW_PASSPORT_DATA["data"][2]["translation"],
            "hash": "more data arghh",
        },
        {
            "type": "rental_agreement",
            "files": RAW_PASSPORT_DATA["data"][2]["files"],
            "translation": RAW_PASSPORT_DATA["data"][2]["translation"],
            "hash": "more data arghh",
        },
        {
            "type": "passport_registration",
            "files": RAW_PASSPORT_DATA["data"][2]["files"],
            "translation": RAW_PASSPORT_DATA["data"][2]["translation"],
            "hash": "more data arghh",
        },
        {
            "type": "temporary_registration",
            "files": RAW_PASSPORT_DATA["data"][2]["files"],
            "translation": RAW_PASSPORT_DATA["data"][2]["translation"],
            "hash": "more data arghh",
        },
        {
            "type": "address",
            "data": RAW_PASSPORT_DATA["data"][3]["data"],
            "hash": "more data arghh",
        },
        {"type": "email", "email": "fb3e3i47zt@dispostable.com", "hash": "more data arghh"},
        {
            "type": "phone_number",
            "phone_number": "fb3e3i47zt@dispostable.com",
            "hash": "more data arghh",
        },
    ]


@pytest.fixture(scope="module")
def passport_data(bot):
    return PassportData.de_json(RAW_PASSPORT_DATA, bot=bot)


class PassportTestBase:
    driver_license_selfie_file_id = "DgADBAADEQQAAkopgFNr6oi-wISRtAI"
    driver_license_selfie_file_unique_id = "d4e390cca57b4da5a65322b304762a12"
    driver_license_front_side_file_id = "DgADBAADxwMAApnQgVPK2-ckL2eXVAI"
    driver_license_front_side_file_unique_id = "d9d52a700cbb4a189a80104aa5978133"
    driver_license_reverse_side_file_id = "DgADBAADNQQAAtoagFPf4wwmFZdmyQI"
    driver_license_reverse_side_file_unique_id = "adc3145fd2e84d95b64d68eaa22aa33e"
    driver_license_translation_1_file_id = "DgADBAADswMAAisqQVAmooP-kVgLgAI"
    driver_license_translation_1_file_unique_id = "52a90d53d6064bb58feb582acdc3a324"
    driver_license_translation_2_file_id = "DgADBAAD1QMAAnrpQFBMZsT3HysjwwI"
    driver_license_translation_2_file_unique_id = "7285f864d168441ba1f7d02146250432"
    utility_bill_1_file_id = "DgADBAADLAMAAhwfgVMyfGa5Nr0LvAI"
    utility_bill_1_file_unique_id = "b170748794834644baaa3ec57ee4ce7a"
    utility_bill_2_file_id = "DgADBAADaQQAAsFxgVNVfLZuT-_3ZQI"
    utility_bill_2_file_unique_id = "19a12ae34dca424b85e0308f706cee75"
    utility_bill_translation_1_file_id = "DgADBAADyQUAAqyqQVC_eoX_KwNjJwI"
    utility_bill_translation_1_file_unique_id = "38b2877b443542cbaf520c6e36a33ac4"
    utility_bill_translation_2_file_id = "DgADBAADsQQAAubTQVDRO_FN3lOwWwI"
    utility_bill_translation_2_file_unique_id = "f008ca48c44b4a47895ddbcd2f76741e"
    driver_license_selfie_credentials_file_hash = "Cila/qLXSBH7DpZFbb5bRZIRxeFW2uv/ulL0u0JNsYI="
    driver_license_selfie_credentials_secret = "tivdId6RNYNsvXYPppdzrbxOBuBOr9wXRPDcCvnXU7E="


class TestPassportWithoutRequest(PassportTestBase):
    def test_slot_behaviour(self, passport_data):
        inst = passport_data
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_creation(self, passport_data):
        assert isinstance(passport_data, PassportData)

    def test_expected_encrypted_values(self, passport_data):
        personal_details, driver_license, utility_bill, address, email = passport_data.data

        assert personal_details.type == "personal_details"
        assert personal_details.data == RAW_PASSPORT_DATA["data"][0]["data"]

        assert driver_license.type == "driver_license"
        assert driver_license.data == RAW_PASSPORT_DATA["data"][1]["data"]
        assert isinstance(driver_license.selfie, PassportFile)
        assert driver_license.selfie.file_id == self.driver_license_selfie_file_id
        assert driver_license.selfie.file_unique_id == self.driver_license_selfie_file_unique_id

        assert isinstance(driver_license.front_side, PassportFile)
        assert driver_license.front_side.file_id == self.driver_license_front_side_file_id
        assert (
            driver_license.front_side.file_unique_id
            == self.driver_license_front_side_file_unique_id
        )

        assert isinstance(driver_license.reverse_side, PassportFile)
        assert driver_license.reverse_side.file_id == self.driver_license_reverse_side_file_id
        assert (
            driver_license.reverse_side.file_unique_id
            == self.driver_license_reverse_side_file_unique_id
        )

        assert isinstance(driver_license.translation[0], PassportFile)
        assert driver_license.translation[0].file_id == self.driver_license_translation_1_file_id
        assert (
            driver_license.translation[0].file_unique_id
            == self.driver_license_translation_1_file_unique_id
        )

        assert isinstance(driver_license.translation[1], PassportFile)
        assert driver_license.translation[1].file_id == self.driver_license_translation_2_file_id
        assert (
            driver_license.translation[1].file_unique_id
            == self.driver_license_translation_2_file_unique_id
        )

        assert utility_bill.type == "utility_bill"
        assert isinstance(utility_bill.files[0], PassportFile)
        assert utility_bill.files[0].file_id == self.utility_bill_1_file_id
        assert utility_bill.files[0].file_unique_id == self.utility_bill_1_file_unique_id

        assert isinstance(utility_bill.files[1], PassportFile)
        assert utility_bill.files[1].file_id == self.utility_bill_2_file_id
        assert utility_bill.files[1].file_unique_id == self.utility_bill_2_file_unique_id

        assert isinstance(utility_bill.translation[0], PassportFile)
        assert utility_bill.translation[0].file_id == self.utility_bill_translation_1_file_id
        assert (
            utility_bill.translation[0].file_unique_id
            == self.utility_bill_translation_1_file_unique_id
        )

        assert isinstance(utility_bill.translation[1], PassportFile)
        assert utility_bill.translation[1].file_id == self.utility_bill_translation_2_file_id
        assert (
            utility_bill.translation[1].file_unique_id
            == self.utility_bill_translation_2_file_unique_id
        )

        assert address.type == "address"
        assert address.data == RAW_PASSPORT_DATA["data"][3]["data"]

        assert email.type == "email"
        assert email.email == "fb3e3i47zt@dispostable.com"

    def test_expected_decrypted_values(self, passport_data):
        (
            personal_details,
            driver_license,
            utility_bill,
            address,
            email,
        ) = passport_data.decrypted_data

        assert personal_details.type == "personal_details"
        assert personal_details.data.to_dict() == {
            "first_name": "FIRSTNAME",
            "middle_name": "MIDDLENAME",
            "first_name_native": "FIRSTNAMENATIVE",
            "residence_country_code": "DK",
            "birth_date": "01.01.2001",
            "last_name_native": "LASTNAMENATIVE",
            "gender": "female",
            "middle_name_native": "MIDDLENAMENATIVE",
            "country_code": "DK",
            "last_name": "LASTNAME",
        }

        assert driver_license.type == "driver_license"
        assert driver_license.data.to_dict() == {
            "expiry_date": "01.01.2001",
            "document_no": "DOCUMENT_NO",
        }
        assert isinstance(driver_license.selfie, PassportFile)
        assert driver_license.selfie.file_id == self.driver_license_selfie_file_id
        assert driver_license.selfie.file_unique_id == self.driver_license_selfie_file_unique_id

        assert isinstance(driver_license.front_side, PassportFile)
        assert driver_license.front_side.file_id == self.driver_license_front_side_file_id
        assert (
            driver_license.front_side.file_unique_id
            == self.driver_license_front_side_file_unique_id
        )

        assert isinstance(driver_license.reverse_side, PassportFile)
        assert driver_license.reverse_side.file_id == self.driver_license_reverse_side_file_id
        assert (
            driver_license.reverse_side.file_unique_id
            == self.driver_license_reverse_side_file_unique_id
        )

        assert address.type == "address"
        assert address.data.to_dict() == {
            "city": "CITY",
            "street_line2": "STREET_LINE2",
            "state": "STATE",
            "post_code": "POSTCODE",
            "country_code": "DK",
            "street_line1": "STREET_LINE1",
        }

        assert utility_bill.type == "utility_bill"
        assert isinstance(utility_bill.files[0], PassportFile)
        assert utility_bill.files[0].file_id == self.utility_bill_1_file_id
        assert utility_bill.files[0].file_unique_id == self.utility_bill_1_file_unique_id

        assert isinstance(utility_bill.files[1], PassportFile)
        assert utility_bill.files[1].file_id == self.utility_bill_2_file_id
        assert utility_bill.files[1].file_unique_id == self.utility_bill_2_file_unique_id

        assert email.type == "email"
        assert email.email == "fb3e3i47zt@dispostable.com"

    def test_de_json_and_to_dict(self, offline_bot):
        passport_data = PassportData.de_json(RAW_PASSPORT_DATA, offline_bot)
        assert passport_data.api_kwargs == {}
        assert passport_data.to_dict() == RAW_PASSPORT_DATA

        assert passport_data.decrypted_data
        assert passport_data.to_dict() == RAW_PASSPORT_DATA

    def test_equality(self, passport_data):
        a = PassportData(passport_data.data, passport_data.credentials)
        b = PassportData(passport_data.data, passport_data.credentials)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        new_pp_data = deepcopy(passport_data)
        new_pp_data.credentials._unfreeze()
        new_pp_data.credentials.hash = "NOTAPROPERHASH"
        c = PassportData(new_pp_data.data, new_pp_data.credentials)

        assert a != c
        assert hash(a) != hash(c)

    def test_bot_init_invalid_key(self, offline_bot):
        with pytest.raises(TypeError):
            Bot(offline_bot.token, private_key="Invalid key!")

        # Different error messages for different cryptography versions
        with pytest.raises(
            ValueError, match="(Could not deserialize key data)|(Unable to load PEM file)"
        ):
            Bot(offline_bot.token, private_key=b"Invalid key!")

    def test_all_types(self, passport_data, offline_bot, all_passport_data):
        credentials = passport_data.decrypted_credentials.to_dict()

        # Copy credentials from other types to all types so we can decrypt everything
        sd = credentials["secure_data"]
        credentials["secure_data"] = {
            "personal_details": sd["personal_details"].copy(),
            "passport": sd["driver_license"].copy(),
            "internal_passport": sd["driver_license"].copy(),
            "driver_license": sd["driver_license"].copy(),
            "identity_card": sd["driver_license"].copy(),
            "address": sd["address"].copy(),
            "utility_bill": sd["utility_bill"].copy(),
            "bank_statement": sd["utility_bill"].copy(),
            "rental_agreement": sd["utility_bill"].copy(),
            "passport_registration": sd["utility_bill"].copy(),
            "temporary_registration": sd["utility_bill"].copy(),
        }

        new = PassportData.de_json(
            {
                "data": all_passport_data,
                # Replaced below
                "credentials": {"data": "data", "hash": "hash", "secret": "secret"},
            },
            bot=offline_bot,
        )
        assert new.api_kwargs == {}

        new.credentials._decrypted_data = Credentials.de_json(credentials, offline_bot)
        assert new.credentials.api_kwargs == {}

        assert isinstance(new, PassportData)
        assert new.decrypted_data

    async def test_passport_data_okay_with_non_crypto_bot(self, offline_bot):
        async with make_bot(token=offline_bot.token) as b:
            assert PassportData.de_json(RAW_PASSPORT_DATA, bot=b)

    def test_wrong_hash(self, offline_bot):
        data = deepcopy(RAW_PASSPORT_DATA)
        data["credentials"]["hash"] = "bm90Y29ycmVjdGhhc2g="  # Not correct hash
        passport_data = PassportData.de_json(data, bot=offline_bot)
        with pytest.raises(PassportDecryptionError):
            assert passport_data.decrypted_data

    async def test_wrong_key(self, offline_bot):
        short_key = (
            b"-----BEGIN RSA PRIVATE"
            b" KEY-----\r\nMIIBOQIBAAJBAKU+OZ2jJm7sCA/ec4gngNZhXYPu+DZ/TAwSMl0W7vAPXAsLplBk\r\nO8l6IBHx8N0ZC4Bc65mO3b2G8YAzqndyqH8CAwEAAQJAWOx3jQFzeVXDsOaBPdAk\r\nYTncXVeIc6tlfUl9mOLyinSbRNCy1XicOiOZFgH1rRKOGIC1235QmqxFvdecySoY\r\nwQIhAOFeGgeX9CrEPuSsd9+kqUcA2avCwqdQgSdy2qggRFyJAiEAu7QHT8JQSkHU\r\nDELfzrzc24AhjyG0z1DpGZArM8COascCIDK42SboXj3Z2UXiQ0CEcMzYNiVgOisq\r\nBUd5pBi+2mPxAiAM5Z7G/Sv1HjbKrOGh29o0/sXPhtpckEuj5QMC6E0gywIgFY6S\r\nNjwrAA+cMmsgY0O2fAzEKkDc5YiFsiXaGaSS4eA=\r\n-----END"
            b" RSA PRIVATE KEY-----"
        )
        async with make_bot(token=offline_bot.token, private_key=short_key) as b:
            passport_data = PassportData.de_json(RAW_PASSPORT_DATA, bot=b)
            with pytest.raises(PassportDecryptionError):
                assert passport_data.decrypted_data

        async with make_bot(token=offline_bot.token, private_key=short_key) as b:
            passport_data = PassportData.de_json(RAW_PASSPORT_DATA, bot=b)
            with pytest.raises(PassportDecryptionError):
                assert passport_data.decrypted_data

    async def test_mocked_download_passport_file(self, passport_data, monkeypatch):
        # The files are not coming from our test offline_bot, therefore the file id is invalid/wrong
        # when coming from this offline_bot, so we monkeypatch the call, to make sure that Bot.get_file
        # at least gets called
        # TODO: Actually download a passport file in a test
        selfie = passport_data.decrypted_data[1].selfie

        # NOTE: file_unique_id is not used in the get_file method, so it is passed directly
        async def get_file(*_, **kwargs):
            return File(kwargs["file_id"], selfie.file_unique_id)

        monkeypatch.setattr(passport_data.get_bot(), "get_file", get_file)
        file = await selfie.get_file()
        assert file.file_id == selfie.file_id
        assert file.file_unique_id == selfie.file_unique_id
        assert file._credentials.file_hash == self.driver_license_selfie_credentials_file_hash
        assert file._credentials.secret == self.driver_license_selfie_credentials_secret

    async def test_mocked_set_passport_data_errors(
        self, monkeypatch, offline_bot, chat_id, passport_data
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            return (
                data["user_id"] == str(chat_id)
                and data["errors"][0]["file_hash"]
                == (
                    passport_data.decrypted_credentials.secure_data.driver_license.selfie.file_hash
                )
                and data["errors"][1]["data_hash"]
                == passport_data.decrypted_credentials.secure_data.driver_license.data.data_hash
            )

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        message = await offline_bot.set_passport_data_errors(
            chat_id,
            [
                PassportElementErrorSelfie(
                    "driver_license",
                    (
                        passport_data.decrypted_credentials.secure_data.driver_license.selfie.file_hash
                    ),
                    "You're not handsome enough to use this app!",
                ),
                PassportElementErrorDataField(
                    "driver_license",
                    "expiry_date",
                    (
                        passport_data.decrypted_credentials.secure_data.driver_license.data.data_hash
                    ),
                    "Your driver license is expired!",
                ),
            ],
        )
        assert message
