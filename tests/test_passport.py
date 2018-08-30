#!/usr/bin/env python
# flake8: noqa: E501
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from telegram import (PassportData, PassportFile, Bot, File, PassportElementErrorSelfie,
                      PassportElementErrorDataField, Credentials, TelegramDecryptionError)
# Generated using the scope:
# {
#   data: [
#     {
#       type: 'personal_details',
#       native_names: true
#     },
#     {
#       type: 'id_document',
#       selfie: true,
#       translation: true
#     },
#     {
#       type: 'address_document',
#       translation: true
#     },
#     'address',
#     'email'
#   ],
#   v: 1
# }
RAW_PASSPORT_DATA = {'credentials': {'hash': 'qB4hz2LMcXYhglwz6EvXMMyI3PURisWLXl/iCmCXcSk=',
                                     'secret': 'O6x3X2JrLO1lUIhw48os1gaenDuZLhesoZMKXehZwtM3vsxOdtxHKWQyLNwtbyy4snYpARXDwf8f1QHNmQ/M1PwBQvk1ozrZBXb4a6k/iYj+P4v8Xw2M++CRHqZv0LaxFtyHOXnNYZ6dXpNeF0ZvYYTmm0FsYvK+/3/F6VDB3Oe6xWlXFLwaCCP/jA9i2+dKp6iq8NLOo4VnxenPKWWYz20RZ50MdAbS3UR+NCx4AHM2P5DEGrHNW0tMXJ+FG3jpVrit5BuCbB/eRgKxNGRWNxEGV5hun5MChdxKCEHCimnUA97h7MZdoTgYxkrfvDSZ/V89BnFXLdr87t/NLvVE0Q==',
                                     'data': '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'},
                     'data': [
                         {
                             'data': 'QRfzWcCN4WncvRO3lASG+d+c5gzqXtoCinQ1PgtYiZMKXCksx9eB9Ic1bOt8C/un9/XaX220PjJSO7Kuba+nXXC51qTsjqP9rnLKygnEIWjKrfiDdklzgcukpRzFSjiOAvhy86xFJZ1PfPSrFATy/Gp1RydLzbrBd2ZWxZqXrxcMoA0Q2UTTFXDoCYerEAiZoD69i79tB/6nkLBcUUvN5d52gKd/GowvxWqAAmdO6l1N7jlo6aWjdYQNBAK1KHbJdbRZMJLxC1MqMuZXAYrPoYBRKr5xAnxDTmPn/LEZKLc3gwwZyEgR5x7e9jp5heM6IEMmsv3O/6SUeEQs7P0iVuRSPLMJLfDdwns8Tl3fF2M4IxKVovjCaOVW+yHKsADDAYQPzzH2RcrWVD0TP5I64mzpK64BbTOq3qm3Hn51SV9uA/+LvdGbCp7VnzHx4EdUizHsVyilJULOBwvklsrDRvXMiWmh34ZSR6zilh051tMEcRf0I+Oe7pIxVJd/KKfYA2Z/eWVQTCn5gMuAInQNXFSqDIeIqBX+wca6kvOCUOXB7J2uRjTpLaC4DM9s/sNjSBvFixcGAngt+9oap6Y45rQc8ZJaNN/ALqEJAmkphW8=',
                             'type': 'personal_details'
                         }, {
                             'reverse_side': {'file_date': 1534074942,
                                              'file_id': 'DgADBAADNQQAAtoagFPf4wwmFZdmyQI'},
                             'translation': [{'file_size': 28640, 'file_date': 1535630933,
                                              'file_id': 'DgADBAADswMAAisqQVAmooP-kVgLgAI'},
                                             {'file_size': 28672, 'file_date': 1535630933,
                                              'file_id': 'DgADBAAD1QMAAnrpQFBMZsT3HysjwwI'}],
                             'front_side': {'file_size': 28624, 'file_date': 1534074942,
                                            'file_id': 'DgADBAADxwMAApnQgVPK2-ckL2eXVAI'},
                             'type': 'driver_license',
                             'selfie': {'file_size': 28592, 'file_date': 1534074942,
                                        'file_id': 'DgADBAADEQQAAkopgFNr6oi-wISRtAI'},
                             'data': 'eJUOFuY53QKmGqmBgVWlLBAQCUQJ79n405SX6M5aGFIIodOPQqnLYvMNqTwTrXGDlW+mVLZcbu+y8luLVO8WsJB/0SB7q5WaXn/IMt1G9lz5G/KMLIZG/x9zlnimsaQLg7u8srG6L4KZzv+xkbbHjZdETrxU8j0N/DoS4HvLMRSJAgeFUrY6v2YW9vSRg+fSxIqQy1jR2VKpzAT8OhOz7A=='
                         }, {
                             'translation': [{'file_size': 28480, 'file_date': 1535630939,
                                              'file_id': 'DgADBAADyQUAAqyqQVC_eoX_KwNjJwI'},
                                             {'file_size': 28528, 'file_date': 1535630939,
                                              'file_id': 'DgADBAADsQQAAubTQVDRO_FN3lOwWwI'}],
                             'files': [{'file_size': 28640, 'file_date': 1534074988,
                                        'file_id': 'DgADBAADLAMAAhwfgVMyfGa5Nr0LvAI'},
                                       {'file_size': 28480, 'file_date': 1534074988,
                                        'file_id': 'DgADBAADaQQAAsFxgVNVfLZuT-_3ZQI'}],
                             'type': 'utility_bill'
                         }, {
                             'data': 'j9SksVkSj128DBtZA+3aNjSFNirzv+R97guZaMgae4Gi0oDVNAF7twPR7j9VSmPedfJrEwL3O889Ei+a5F1xyLLyEI/qEBljvL70GFIhYGitS0JmNabHPHSZrjOl8b4s/0Z0Px2GpLO5siusTLQonimdUvu4UPjKquYISmlKEKhtmGATy+h+JDjNCYuOkhakeNw0Rk0BHgj0C3fCb7WZNQSyVb+2GTu6caR6eXf/AFwFp0TV3sRz3h0WIVPW8bna',
                             'type': 'address'
                         }, {
                             'email': 'fb3e3i47zt@dispostable.com', 'type': 'email'
                         }]}


@pytest.fixture(scope='function')
def all_passport_data():
    return [{'type': 'personal_details',
             'data': RAW_PASSPORT_DATA['data'][0]['data']},
            {'type': 'passport',
             'data': RAW_PASSPORT_DATA['data'][1]['data'],
             'front_side': RAW_PASSPORT_DATA['data'][1]['front_side'],
             'selfie': RAW_PASSPORT_DATA['data'][1]['selfie'],
             'translation': RAW_PASSPORT_DATA['data'][1]['translation']},
            {'type': 'internal_passport',
             'data': RAW_PASSPORT_DATA['data'][1]['data'],
             'front_side': RAW_PASSPORT_DATA['data'][1]['front_side'],
             'selfie': RAW_PASSPORT_DATA['data'][1]['selfie'],
             'translation': RAW_PASSPORT_DATA['data'][1]['translation']},
            {'type': 'driver_license',
             'data': RAW_PASSPORT_DATA['data'][1]['data'],
             'front_side': RAW_PASSPORT_DATA['data'][1]['front_side'],
             'reverse_side': RAW_PASSPORT_DATA['data'][1]['reverse_side'],
             'selfie': RAW_PASSPORT_DATA['data'][1]['selfie'],
             'translation': RAW_PASSPORT_DATA['data'][1]['translation']},
            {'type': 'identity_card',
             'data': RAW_PASSPORT_DATA['data'][1]['data'],
             'front_side': RAW_PASSPORT_DATA['data'][1]['front_side'],
             'reverse_side': RAW_PASSPORT_DATA['data'][1]['reverse_side'],
             'selfie': RAW_PASSPORT_DATA['data'][1]['selfie'],
             'translation': RAW_PASSPORT_DATA['data'][1]['translation']},
            {'type': 'utility_bill',
             'files': RAW_PASSPORT_DATA['data'][2]['files'],
             'translation': RAW_PASSPORT_DATA['data'][2]['translation']},
            {'type': 'bank_statement',
             'files': RAW_PASSPORT_DATA['data'][2]['files'],
             'translation': RAW_PASSPORT_DATA['data'][2]['translation']},
            {'type': 'rental_agreement',
             'files': RAW_PASSPORT_DATA['data'][2]['files'],
             'translation': RAW_PASSPORT_DATA['data'][2]['translation']},
            {'type': 'passport_registration',
             'files': RAW_PASSPORT_DATA['data'][2]['files'],
             'translation': RAW_PASSPORT_DATA['data'][2]['translation']},
            {'type': 'temporary_registration',
             'files': RAW_PASSPORT_DATA['data'][2]['files'],
             'translation': RAW_PASSPORT_DATA['data'][2]['translation']},
            {'type': 'address',
             'data': RAW_PASSPORT_DATA['data'][3]['data']},
            {'type': 'email',
             'email': 'fb3e3i47zt@dispostable.com'},
            {'type': 'phone_number',
             'phone_number': 'fb3e3i47zt@dispostable.com'}]


@pytest.fixture(scope='function')
def passport_data(bot):
    return PassportData.de_json(RAW_PASSPORT_DATA, bot=bot)


class TestPassport(object):
    driver_license_selfie_file_id = 'DgADBAADEQQAAkopgFNr6oi-wISRtAI'
    driver_license_front_side_file_id = 'DgADBAADxwMAApnQgVPK2-ckL2eXVAI'
    driver_license_reverse_side_file_id = 'DgADBAADNQQAAtoagFPf4wwmFZdmyQI'
    driver_license_translation_1_file_id = 'DgADBAADswMAAisqQVAmooP-kVgLgAI'
    driver_license_translation_2_file_id = 'DgADBAAD1QMAAnrpQFBMZsT3HysjwwI'
    utility_bill_1_file_id = 'DgADBAADLAMAAhwfgVMyfGa5Nr0LvAI'
    utility_bill_2_file_id = 'DgADBAADaQQAAsFxgVNVfLZuT-_3ZQI'
    utility_bill_translation_1_file_id = 'DgADBAADyQUAAqyqQVC_eoX_KwNjJwI'
    utility_bill_translation_2_file_id = 'DgADBAADsQQAAubTQVDRO_FN3lOwWwI'
    driver_license_selfie_credentials_file_hash = 'Cila/qLXSBH7DpZFbb5bRZIRxeFW2uv/ulL0u0JNsYI='
    driver_license_selfie_credentials_secret = 'tivdId6RNYNsvXYPppdzrbxOBuBOr9wXRPDcCvnXU7E='

    def test_creation(self, passport_data):
        assert isinstance(passport_data, PassportData)

    def test_expected_encrypted_values(self, passport_data):
        personal_details, driver_license, utility_bill, address, email = passport_data.data

        assert personal_details.type == 'personal_details'
        assert personal_details.data == RAW_PASSPORT_DATA['data'][0]['data']

        assert driver_license.type == 'driver_license'
        assert driver_license.data == RAW_PASSPORT_DATA['data'][1]['data']
        assert isinstance(driver_license.selfie, PassportFile)
        assert driver_license.selfie.file_id == self.driver_license_selfie_file_id
        assert isinstance(driver_license.front_side, PassportFile)
        assert driver_license.front_side.file_id == self.driver_license_front_side_file_id
        assert isinstance(driver_license.reverse_side, PassportFile)
        assert driver_license.reverse_side.file_id == self.driver_license_reverse_side_file_id
        assert isinstance(driver_license.translation[0], PassportFile)
        assert driver_license.translation[0].file_id == self.driver_license_translation_1_file_id
        assert isinstance(driver_license.translation[1], PassportFile)
        assert driver_license.translation[1].file_id == self.driver_license_translation_2_file_id

        assert utility_bill.type == 'utility_bill'
        assert isinstance(utility_bill.files[0], PassportFile)
        assert utility_bill.files[0].file_id == self.utility_bill_1_file_id
        assert isinstance(utility_bill.files[1], PassportFile)
        assert utility_bill.files[1].file_id == self.utility_bill_2_file_id
        assert isinstance(utility_bill.translation[0], PassportFile)
        assert utility_bill.translation[0].file_id == self.utility_bill_translation_1_file_id
        assert isinstance(utility_bill.translation[1], PassportFile)
        assert utility_bill.translation[1].file_id == self.utility_bill_translation_2_file_id

        assert address.type == 'address'
        assert address.data == RAW_PASSPORT_DATA['data'][3]['data']

        assert email.type == 'email'
        assert email.email == 'fb3e3i47zt@dispostable.com'

    def test_expected_decrypted_values(self, passport_data):
        (personal_details, driver_license, utility_bill, address,
         email) = passport_data.decrypted_data

        assert personal_details.type == 'personal_details'
        assert personal_details.data.to_dict() == {'first_name': 'FIRSTNAME',
                                                   'middle_name': 'MIDDLENAME',
                                                   'first_name_native': 'FIRSTNAMENATIVE',
                                                   'residence_country_code': 'DK',
                                                   'birth_date': '01.01.2001',
                                                   'last_name_native': 'LASTNAMENATIVE',
                                                   'gender': 'female',
                                                   'middle_name_native': 'MIDDLENAMENATIVE',
                                                   'country_code': 'DK',
                                                   'last_name': 'LASTNAME'}

        assert driver_license.type == 'driver_license'
        assert driver_license.data.to_dict() == {'expiry_date': '01.01.2001',
                                                 'document_no': 'DOCUMENT_NO'}
        assert isinstance(driver_license.selfie, PassportFile)
        assert driver_license.selfie.file_id == self.driver_license_selfie_file_id
        assert isinstance(driver_license.front_side, PassportFile)
        assert driver_license.front_side.file_id == self.driver_license_front_side_file_id
        assert isinstance(driver_license.reverse_side, PassportFile)
        assert driver_license.reverse_side.file_id == self.driver_license_reverse_side_file_id

        assert address.type == 'address'
        assert address.data.to_dict() == {'city': 'CITY', 'street_line2': 'STREET_LINE2',
                                          'state': 'STATE', 'post_code': 'POSTCODE',
                                          'country_code': 'DK', 'street_line1': 'STREET_LINE1'}

        assert utility_bill.type == 'utility_bill'
        assert isinstance(utility_bill.files[0], PassportFile)
        assert utility_bill.files[0].file_id == self.utility_bill_1_file_id
        assert isinstance(utility_bill.files[1], PassportFile)
        assert utility_bill.files[1].file_id == self.utility_bill_2_file_id

        assert email.type == 'email'
        assert email.email == 'fb3e3i47zt@dispostable.com'

    def test_all_types(self, passport_data, bot, all_passport_data):
        credentials = passport_data.decrypted_credentials.to_dict()

        # Copy credentials from other types to all types so we can decrypt everything
        sd = credentials['secure_data']
        credentials['secure_data'] = {
            'personal_details': sd['personal_details'].copy(),
            'passport': sd['driver_license'].copy(),
            'internal_passport': sd['driver_license'].copy(),
            'driver_license': sd['driver_license'].copy(),
            'identity_card': sd['driver_license'].copy(),
            'address': sd['address'].copy(),
            'utility_bill': sd['utility_bill'].copy(),
            'bank_statement': sd['utility_bill'].copy(),
            'rental_agreement': sd['utility_bill'].copy(),
            'passport_registration': sd['utility_bill'].copy(),
            'temporary_registration': sd['utility_bill'].copy(),
        }

        new = PassportData.de_json({
            'data': all_passport_data,
            # Replaced below
            'credentials': {'data': 'data', 'hash': 'hash', 'secret': 'secret'}
        }, bot=bot)

        new.credentials._decrypted_data = Credentials.de_json(credentials, bot)

        assert isinstance(new, PassportData)
        assert new.decrypted_data

    def test_bot_init_invalid_key(self, bot):
        with pytest.raises(TypeError):
            Bot(bot.token, private_key=u'Invalid key!')

        with pytest.raises(ValueError):
            Bot(bot.token, private_key=b'Invalid key!')

    def test_passport_data_okay_with_non_crypto_bot(self, bot):
        b = Bot(bot.token)
        assert PassportData.de_json(RAW_PASSPORT_DATA, bot=b)

    def test_wrong_hash(self, bot):
        data = deepcopy(RAW_PASSPORT_DATA)
        data['credentials']['hash'] = 'bm90Y29ycmVjdGhhc2g='  # Not correct hash
        passport_data = PassportData.de_json(data, bot=bot)
        with pytest.raises(TelegramDecryptionError):
            assert passport_data.decrypted_data

    def test_wrong_key(self, bot):
        short_key = b"-----BEGIN RSA PRIVATE KEY-----\r\nMIIBOQIBAAJBAKU+OZ2jJm7sCA/ec4gngNZhXYPu+DZ/TAwSMl0W7vAPXAsLplBk\r\nO8l6IBHx8N0ZC4Bc65mO3b2G8YAzqndyqH8CAwEAAQJAWOx3jQFzeVXDsOaBPdAk\r\nYTncXVeIc6tlfUl9mOLyinSbRNCy1XicOiOZFgH1rRKOGIC1235QmqxFvdecySoY\r\nwQIhAOFeGgeX9CrEPuSsd9+kqUcA2avCwqdQgSdy2qggRFyJAiEAu7QHT8JQSkHU\r\nDELfzrzc24AhjyG0z1DpGZArM8COascCIDK42SboXj3Z2UXiQ0CEcMzYNiVgOisq\r\nBUd5pBi+2mPxAiAM5Z7G/Sv1HjbKrOGh29o0/sXPhtpckEuj5QMC6E0gywIgFY6S\r\nNjwrAA+cMmsgY0O2fAzEKkDc5YiFsiXaGaSS4eA=\r\n-----END RSA PRIVATE KEY-----"
        b = Bot(bot.token, private_key=short_key)
        passport_data = PassportData.de_json(RAW_PASSPORT_DATA, bot=b)
        with pytest.raises(TelegramDecryptionError):
            assert passport_data.decrypted_data

        wrong_key = b"-----BEGIN RSA PRIVATE KEY-----\r\nMIIEogIBAAKCAQB4qCFltuvHakZze86TUweU7E/SB3VLGEHAe7GJlBmrou9SSWsL\r\nH7E++157X6UqWFl54LOE9MeHZnoW7rZ+DxLKhk6NwAHTxXPnvw4CZlvUPC3OFxg3\r\nhEmNen6ojSM4sl4kYUIa7F+Q5uMEYaboxoBen9mbj4zzMGsG4aY/xBOb2ewrXQyL\r\nRh//tk1Px4ago+lUPisAvQVecz7/6KU4Xj4Lpv2z20f3cHlZX6bb7HlE1vixCMOf\r\nxvfC5SkWEGZMR/ZoWQUsoDkrDSITF/S3GtLfg083TgtCKaOF3mCT27sJ1og77npP\r\n0cH/qdlbdoFtdrRj3PvBpaj/TtXRhmdGcJBxAgMBAAECggEAYSq1Sp6XHo8dkV8B\r\nK2/QSURNu8y5zvIH8aUrgqo8Shb7OH9bryekrB3vJtgNwR5JYHdu2wHttcL3S4SO\r\nftJQxbyHgmxAjHUVNGqOM6yPA0o7cR70J7FnMoKVgdO3q68pVY7ll50IET9/T0X9\r\nDrTdKFb+/eILFsXFS1NpeSzExdsKq3zM0sP/vlJHHYVTmZDGaGEvny/eLAS+KAfG\r\nrKP96DeO4C/peXEJzALZ/mG1ReBB05Qp9Dx1xEC20yreRk5MnnBA5oiHVG5ZLOl9\r\nEEHINidqN+TMNSkxv67xMfQ6utNu5IpbklKv/4wqQOJOO50HZ+qBtSurTN573dky\r\nzslbCQKBgQDHDUBYyKN/v69VLmvNVcxTgrOcrdbqAfefJXb9C3dVXhS8/oRkCRU/\r\ndzxYWNT7hmQyWUKor/izh68rZ/M+bsTnlaa7IdAgyChzTfcZL/2pxG9pq05GF1Q4\r\nBSJ896ZEe3jEhbpJXRlWYvz7455svlxR0H8FooCTddTmkU3nsQSx0wKBgQCbLSa4\r\nyZs2QVstQQerNjxAtLi0IvV8cJkuvFoNC2Q21oqQc7BYU7NJL7uwriprZr5nwkCQ\r\nOFQXi4N3uqimNxuSng31ETfjFZPp+pjb8jf7Sce7cqU66xxR+anUzVZqBG1CJShx\r\nVxN7cWN33UZvIH34gA2Ax6AXNnJG42B5Gn1GKwKBgQCZ/oh/p4nGNXfiAK3qB6yy\r\nFvX6CwuvsqHt/8AUeKBz7PtCU+38roI/vXF0MBVmGky+HwxREQLpcdl1TVCERpIT\r\nUFXThI9OLUwOGI1IcTZf9tby+1LtKvM++8n4wGdjp9qAv6ylQV9u09pAzZItMwCd\r\nUx5SL6wlaQ2y60tIKk0lfQKBgBJS+56YmA6JGzY11qz+I5FUhfcnpauDNGOTdGLT\r\n9IqRPR2fu7RCdgpva4+KkZHLOTLReoRNUojRPb4WubGfEk93AJju5pWXR7c6k3Bt\r\novS2mrJk8GQLvXVksQxjDxBH44sLDkKMEM3j7uYJqDaZNKbyoCWT7TCwikAau5qx\r\naRevAoGAAKZV705dvrpJuyoHFZ66luANlrAwG/vNf6Q4mBEXB7guqMkokCsSkjqR\r\nhsD79E6q06zA0QzkLCavbCn5kMmDS/AbA80+B7El92iIN6d3jRdiNZiewkhlWhEG\r\nm4N0gQRfIu+rUjsS/4xk8UuQUT/Ossjn/hExi7ejpKdCc7N++bc=\r\n-----END RSA PRIVATE KEY-----"
        b = Bot(bot.token, private_key=wrong_key)
        passport_data = PassportData.de_json(RAW_PASSPORT_DATA, bot=b)
        with pytest.raises(TelegramDecryptionError):
            assert passport_data.decrypted_data

    def test_mocked_download_passport_file(self, passport_data, monkeypatch):
        # The files are not coming from our test bot, therefore the file id is invalid/wrong
        # when coming from this bot, so we monkeypatch the call, to make sure that Bot.get_file
        # at least gets called
        # TODO: Actually download a passport file in a test
        selfie = passport_data.decrypted_data[1].selfie

        def get_file(*args, **kwargs):
            return File(args[1])

        monkeypatch.setattr('telegram.Bot.get_file', get_file)
        file = selfie.get_file()
        assert file.file_id == selfie.file_id
        assert file._credentials.file_hash == self.driver_license_selfie_credentials_file_hash
        assert file._credentials.secret == self.driver_license_selfie_credentials_secret

    def test_mocked_set_passport_data_errors(self, monkeypatch, bot, chat_id, passport_data):
        def test(_, url, data, **kwargs):
            return (data['user_id'] == chat_id and
                    data['errors'][0]['file_hash'] == (passport_data.decrypted_credentials
                                                       .secure_data.driver_license
                                                       .selfie.file_hash) and
                    data['errors'][1]['data_hash'] == (passport_data.decrypted_credentials
                                                       .secure_data.driver_license
                                                       .data.data_hash))

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        message = bot.set_passport_data_errors(chat_id, [
            PassportElementErrorSelfie('driver_license',
                                       (passport_data.decrypted_credentials
                                        .secure_data.driver_license.selfie.file_hash),
                                       'You\'re not handsome enough to use this app!'),
            PassportElementErrorDataField('driver_license',
                                          'expiry_date',
                                          (passport_data.decrypted_credentials
                                           .secure_data.driver_license.data.data_hash),
                                          'Your driver license is expired!')
        ])
        assert message

    def test_de_json_and_to_dict(self, bot):
        passport_data = PassportData.de_json(RAW_PASSPORT_DATA, bot)
        assert passport_data.to_dict() == RAW_PASSPORT_DATA

        assert passport_data.decrypted_data
        assert passport_data.to_dict() == RAW_PASSPORT_DATA

    def test_equality(self, passport_data):
        a = PassportData(passport_data.data, passport_data.credentials)
        b = PassportData(passport_data.data, passport_data.credentials)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        passport_data.credentials.hash = 'NOTAPROPERHASH'
        c = PassportData(passport_data.data, passport_data.credentials)

        assert a != c
        assert hash(a) != hash(c)
