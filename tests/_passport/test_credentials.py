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

from telegram import Credentials, DataCredentials, FileCredentials, SecureData, SecureValue
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots

# Telegram doesn't send these classes directly: they are the decrypted content of
# EncryptedCredentials.data, see https://core.telegram.org/passport#credentials


class CredentialsTestBase:
    data_hash = "data_hash"
    file_hash = "file_hash"
    secret = "secret"
    nonce = "nonce"

    @property
    def data_credentials(self):
        return {"data_hash": self.data_hash, "secret": self.secret}

    @property
    def file_credentials(self):
        return {"file_hash": self.file_hash, "secret": self.secret}

    def check_data_credentials(self, credentials):
        assert isinstance(credentials, DataCredentials)
        assert credentials.data_hash == self.data_hash
        assert credentials.secret == self.secret

    def check_file_credentials(self, credentials):
        assert isinstance(credentials, FileCredentials)
        assert credentials.file_hash == self.file_hash
        assert credentials.secret == self.secret

    @staticmethod
    def check_slots(inst):
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"


class TestDataCredentialsWithoutRequest(CredentialsTestBase, DeserializationTestBase):
    de_json_class = DataCredentials

    @pytest.fixture
    def de_json_dict(self):
        return self.data_credentials

    def test_slot_behaviour(self, de_json_dict):
        self.check_slots(DataCredentials.de_json(de_json_dict))

    def test_de_json(self, offline_bot, de_json_dict):
        credentials = DataCredentials.de_json(de_json_dict, offline_bot)
        assert credentials.api_kwargs == {}

        self.check_data_credentials(credentials)
        assert credentials.hash == self.data_hash
        assert credentials.file_hash == self.data_hash


class TestFileCredentialsWithoutRequest(CredentialsTestBase, DeserializationTestBase):
    de_json_class = FileCredentials

    @pytest.fixture
    def de_json_dict(self):
        return self.file_credentials

    def test_slot_behaviour(self, de_json_dict):
        self.check_slots(FileCredentials.de_json(de_json_dict))

    def test_de_json(self, offline_bot, de_json_dict):
        credentials = FileCredentials.de_json(de_json_dict, offline_bot)
        assert credentials.api_kwargs == {}

        self.check_file_credentials(credentials)
        assert credentials.hash == self.file_hash
        assert credentials.data_hash == self.file_hash


class TestSecureValueWithoutRequest(CredentialsTestBase, DeserializationTestBase):
    de_json_class = SecureValue

    @pytest.fixture
    def de_json_dict(self):
        # Telegram only sends the fields that fit the type of the element. We set all of them
        # so that every argument is tested.
        return {
            "data": self.data_credentials,
            "front_side": self.file_credentials,
            "reverse_side": self.file_credentials,
            "selfie": self.file_credentials,
            "files": [self.file_credentials],
            "translation": [self.file_credentials],
        }

    def test_slot_behaviour(self, de_json_dict):
        self.check_slots(SecureValue.de_json(de_json_dict))

    def test_de_json(self, offline_bot, de_json_dict):
        secure_value = SecureValue.de_json(de_json_dict, offline_bot)
        assert secure_value.api_kwargs == {}

        self.check_data_credentials(secure_value.data)
        self.check_file_credentials(secure_value.front_side)
        self.check_file_credentials(secure_value.reverse_side)
        self.check_file_credentials(secure_value.selfie)
        assert len(secure_value.files) == 1
        self.check_file_credentials(secure_value.files[0])
        assert len(secure_value.translation) == 1
        self.check_file_credentials(secure_value.translation[0])


class TestSecureDataWithoutRequest(CredentialsTestBase, DeserializationTestBase):
    de_json_class = SecureData

    @property
    def id_document(self):
        return {
            "data": self.data_credentials,
            "front_side": self.file_credentials,
            "selfie": self.file_credentials,
            "translation": [self.file_credentials],
        }

    @property
    def id_document_with_reverse_side(self):
        return self.id_document | {"reverse_side": self.file_credentials}

    @property
    def proof_of_address(self):
        return {"files": [self.file_credentials], "translation": [self.file_credentials]}

    @pytest.fixture
    def de_json_dict(self):
        return {
            "personal_details": {"data": self.data_credentials},
            "passport": self.id_document,
            "internal_passport": self.id_document,
            "driver_license": self.id_document_with_reverse_side,
            "identity_card": self.id_document_with_reverse_side,
            "address": {"data": self.data_credentials},
            "utility_bill": self.proof_of_address,
            "bank_statement": self.proof_of_address,
            "rental_agreement": self.proof_of_address,
            "passport_registration": self.proof_of_address,
            "temporary_registration": self.proof_of_address,
        }

    def test_slot_behaviour(self, de_json_dict):
        self.check_slots(SecureData.de_json(de_json_dict))

    def test_de_json(self, offline_bot, de_json_dict):
        secure_data = SecureData.de_json(de_json_dict, offline_bot)
        assert secure_data.api_kwargs == {}

        for name in ("personal_details", "address"):
            secure_value = getattr(secure_data, name)
            assert isinstance(secure_value, SecureValue), name
            self.check_data_credentials(secure_value.data)
            assert secure_value.front_side is None
            assert secure_value.files == ()

        for name in ("passport", "internal_passport", "driver_license", "identity_card"):
            secure_value = getattr(secure_data, name)
            assert isinstance(secure_value, SecureValue), name
            self.check_data_credentials(secure_value.data)
            self.check_file_credentials(secure_value.front_side)
            self.check_file_credentials(secure_value.selfie)
            self.check_file_credentials(secure_value.translation[0])
            if name in ("driver_license", "identity_card"):
                self.check_file_credentials(secure_value.reverse_side)
            else:
                assert secure_value.reverse_side is None

        for name in (
            "utility_bill",
            "bank_statement",
            "rental_agreement",
            "passport_registration",
            "temporary_registration",
        ):
            secure_value = getattr(secure_data, name)
            assert isinstance(secure_value, SecureValue), name
            assert secure_value.data is None
            self.check_file_credentials(secure_value.files[0])
            self.check_file_credentials(secure_value.translation[0])


class TestCredentialsWithoutRequest(CredentialsTestBase, DeserializationTestBase):
    de_json_class = Credentials

    @pytest.fixture
    def de_json_dict(self):
        return {
            "secure_data": {"personal_details": {"data": self.data_credentials}},
            "nonce": self.nonce,
        }

    def test_slot_behaviour(self, de_json_dict):
        self.check_slots(Credentials.de_json(de_json_dict))

    def test_de_json(self, offline_bot, de_json_dict):
        credentials = Credentials.de_json(de_json_dict, offline_bot)
        assert credentials.api_kwargs == {}

        assert credentials.nonce == self.nonce
        assert isinstance(credentials.secure_data, SecureData)
        self.check_data_credentials(credentials.secure_data.personal_details.data)
        assert credentials.secure_data.passport is None
