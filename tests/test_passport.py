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

RAW_PASSPORT_DATA = {'data': [{'type': 'personal_details',
                               'data': 'tj3pNwOpN+ZHsyb6F3aJcNmEyPxrOtGTbu3waBlCQDNaQ9oJlkbXpw+HI3y9faq/+TCeB/WsS/2TxRXTKZw4zXvGP2UsfdRkJ2SQq6x+Ffe/oTF9/q8sWp2BwU3hHUOz7ec1/QrdPBhPJjbwSykEBNggPweiBVDZ0x/DWJ0guCkGT9smYGqog1vqlqbIWG7AWcxVy2fpUy9w/zDXjxj5WQ3lRpHJmi46s9xIHobNGGBvWw6/bGBCInMoovgqRCEu1sgz2QXF3wNiUzGFycEzLz7o+1htLys5n8Pdi9MG4RY='},
                              {'type': 'driver_license',
                               'data': 'hOXQ/iHSGRDFXqql3yETA4AiP0mdlwmo9RtGS+Qg9E5okrN/yTcPNtBKb2fLA0posk35bvevN53cyJMHZnxErEFTSw/FQjPyRFdJUyjGNPeu4yOI73uk5eRVLTAlA2G0eN2azzfS/QOBGL19N3pHk9hMTZYPCBTDt89MHhRQS7Z3YWRSzFcFiEhktHv/ezgcg3EWtsUQ8K4J2445uoZzbB8wsQ6RM4ibn08RfjV6dNyVrj8jBGUpCBlA6iY60rFQM+LZ9ByI3OeS53bnIAMQC2rHHbV/wkzS6PbufOzjZgJq26aCLmC5YDomrpcrdvk0fvi6aEuBJEI3zcteh2fh/Q==',
                               'selfie': {'file_id': 'DgADBAADEQQAAkopgFNr6oi-wISRtAI',
                                          'file_date': 1534074942},
                               'reverse_side': {'file_id': 'DgADBAADNQQAAtoagFPf4wwmFZdmyQI',
                                                'file_date': 1534074942},
                               'front_side': {'file_id': 'DgADBAADxwMAApnQgVPK2-ckL2eXVAI',
                                              'file_date': 1534074942}},
                              {'type': 'address',
                               'data': 'j9SksVkSj128DBtZA+3aNjSFNirzv+R97guZaMgae4Gi0oDVNAF7twPR7j9VSmPedfJrEwL3O889Ei+a5F1xyLLyEI/qEBljvL70GFIhYGitS0JmNabHPHSZrjOl8b4s/0Z0Px2GpLO5siusTLQonimdUvu4UPjKquYISmlKEKhtmGATy+h+JDjNCYuOkhakeNw0Rk0BHgj0C3fCb7WZNQSyVb+2GTu6caR6eXf/AFwFp0TV3sRz3h0WIVPW8bna'},
                              {'type': 'utility_bill', 'files': [
                                  {'file_id': 'DgADBAADLAMAAhwfgVMyfGa5Nr0LvAI',
                                   'file_date': 1534074988},
                                  {'file_id': 'DgADBAADaQQAAsFxgVNVfLZuT-_3ZQI',
                                   'file_date': 1534074988}]},
                              {'type': 'email', 'email': 'fb3e3i47zt@dispostable.com'}],
                     'credentials': {
                         'data': 'uI/g4fJLVO6132t+yuBvKExTpTubinscH8KLVc8YPuo1SiXaBg4A6AaVdv60CPViMw8n+ShVWOTL6oN5Ye0+CC2/URZ0eeTMJcKkvJYRI0Q6YJ3aeeEzslwORKho0mGk5xSWpPV5LHXhRIlgUMA32NkbNuzzoij7OhqxvuDE50/0pAUKtxy69h+heAzxFj8+jYjgnOwgwNa6FGUG59oUozgpB98XrEeWGW+JIGE9fux8dSGkFhF2SjkmdW6b2Gexuq94TVGDgFigSvqMOgZj9slZI4UEdZBIGldPHrc8/+EuqWv+WKWU8hdj1dxfY/pNvonb8MwrQLrUyNafdLq5QD4Kmg3XPnZTI9bsYUf6xO9oKU42JezDcRbaCqKkUn6UceCkV2hHMJP4aVVI9Bad1k/rXlaDh8PUV19n6tct5UH8JfkBbGlj2uASI5lPasIvnWg9s1vsZ4ynE2YAuU4iotMkgmJkj1+JCl8Ul9uqzfiK0IbYfu57V82gUEjn6c4br49pY+Cvo9od9Lx8fSJCiXq+DdmDTfIZxpeFqEYeJi6/v0CjJni4CtS6LJGo9JUR2MlqOAiyOLomadlrZyzC2eLm8X6ouIXTxtbUqzxcTiH/r23NQ44YwJpMdDiulNuPg0tEyio8TokHj9APORiW+QIw4zLZFyBEorT1DSALm4AV3A1lIg0svOncDkOqa3ZydQ0tdysoXOq5Zsu+Qu/DQZQz5IGEHb7N9QW6KZDGfBOP5Ok04OxlXO8UaTZr6mysmu8jDOlqtitLKSCGDy0LPfITzehTqfEu0KrtmxI91zJtiNyE4g+oBzQsLwQ7vSp1xl7YNViDi8ea/upZdRavh3NthVD5TxyNJedt4Xp8q5/H5kSV/EFhumONPwBwOuN4KrsCQEaNtHZfYB8SH1v0rWbiFw3/owxCrCPqgEwMGnx+JTqsAplurIZfxsNz+57O4Hq10VVt7yhroq9UpIAR8C8hW58dcZBflWyQwG8HalYAaPJ/teSLP9o6MyiqrUkADbNBOFsUhIerq6Q0BnQ941sWg10BkG8oQSU6JdnZ1Ygml2gpFabBRXeeF5ijD0Y9Bq8D3vDnHKx/GziAK0aKlwSqfTmJ+C1hm7AxBekjtDavkBeq5bIOtxYaXqrtunQFAZRCrcnQEg0DPY6dYw+jmOR0NuHRMU5KeZ0994Jn0TRGiUoJtLp1MHJ2D1MCWG3Fp9Ps7vB46a9XiGYHJUdJjHsavvQRQjhB1FvA/kxXNubCjAOPLUz1j+BEkUUgwi65l8+pViHUCIhBdLJn7S0J9HbMsc3jXOFusfvXfyvf2SZMqyhEscs/2HzYgbCWVSxQ//6eimZqvW4an1JIEfH1xUH3zS0HvS7NWChtX1Cj+jJ2vw+lyom6a84wJ2mjSRVcaV6JZa2mIf2IuXfX8EMZwKMDJagkQ7effV3MrnCNrXUXJYn8wVm6l+uP+R9mCn9qbGlvWToCID0YM8MTxJ0LgzC0n93m46OxxCI1p1hPzVrmDCcKt3OASe0zVat415/sz9TTU7Rm8oNSAVUVNo7FRg2XwEb9VupGMjlscu4cJKLCtUpImSKDKlVLH2KYy6s4NdPjOjqtjQLRoaCxbYHmNXXE+vVwPiNBK/bBVT3XJgdmbkXa/PDnMjhAmn0huuxBu8GsTOs+bBdyDCbr6mY6EzN9lCPspEoOPs7nmREpjrvGmEqEddRteyAebpVqZQhqklyT3RVl8AmfoF7QgTi0NYqFb50Lgou3hFrMg7isG5EKU+IKI5WfzyWONlHNSpvO',
                         'hash': 'qyi5vQ2HCVjVMHb+l6HQ4krmvwwEkvm6Qmdf5GJcohM=',
                         'secret': 'kgJE0VLB9enOq5fhhX8gOv0xoaMIcskmRPOG1eMbiC/Q8slr7kur12H/YIoOfd7/DQ0ggE7TAAe34PypFvtmwt5fDVtqtPl9YoCeAOCFWxHxLgTCLbzoJ0lTJXoJkdHjlvR2lKaP+rMtaU1w8WOpYOGiNXyblQoWwFRrWNTHmHnmwBfGBFCj/vp89+C1viEYHeWPPUkBhf1vT31L70BEoe8hxORJEDg+jY+80W2nFdIWNBF+o9GSmbMWFtd7UFiuLPp2JUBCy8XuHozk8xFk/PN6m6DgSu32rC4YBJv/sWGUo/MmH0nxR3gaiEkj+9rWIybCNAwgfdQpk/KH2RCF8g=='}}


@pytest.fixture(scope='function')
def all_passport_data():
    return [{'type': 'personal_details',
             'data': RAW_PASSPORT_DATA['data'][0]['data']},
            {'type': 'passport',
             'data': RAW_PASSPORT_DATA['data'][1]['data'],
             'front_side': RAW_PASSPORT_DATA['data'][1]['front_side'],
             'selfie': RAW_PASSPORT_DATA['data'][1]['selfie']},
            {'type': 'internal_passport',
             'data': RAW_PASSPORT_DATA['data'][1]['data'],
             'front_side': RAW_PASSPORT_DATA['data'][1]['front_side'],
             'selfie': RAW_PASSPORT_DATA['data'][1]['selfie']},
            {'type': 'driver_license',
             'data': RAW_PASSPORT_DATA['data'][1]['data'],
             'front_side': RAW_PASSPORT_DATA['data'][1]['front_side'],
             'reverse_side': RAW_PASSPORT_DATA['data'][1]['reverse_side'],
             'selfie': RAW_PASSPORT_DATA['data'][1]['selfie']},
            {'type': 'identity_card',
             'data': RAW_PASSPORT_DATA['data'][1]['data'],
             'front_side': RAW_PASSPORT_DATA['data'][1]['front_side'],
             'reverse_side': RAW_PASSPORT_DATA['data'][1]['reverse_side'],
             'selfie': RAW_PASSPORT_DATA['data'][1]['selfie']},
            {'type': 'address',
             'data': RAW_PASSPORT_DATA['data'][2]['data']},
            {'type': 'utility_bill',
             'files': RAW_PASSPORT_DATA['data'][3]['files']},
            {'type': 'bank_statement',
             'files': RAW_PASSPORT_DATA['data'][3]['files']},
            {'type': 'rental_agreement',
             'files': RAW_PASSPORT_DATA['data'][3]['files']},
            {'type': 'passport_registration',
             'files': RAW_PASSPORT_DATA['data'][3]['files']},
            {'type': 'temporary_registration',
             'files': RAW_PASSPORT_DATA['data'][3]['files']},
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
    utility_bill_1_file_id = 'DgADBAADLAMAAhwfgVMyfGa5Nr0LvAI'
    utility_bill_2_file_id = 'DgADBAADaQQAAsFxgVNVfLZuT-_3ZQI'
    driver_license_selfie_credentials_file_hash = 'Cila/qLXSBH7DpZFbb5bRZIRxeFW2uv/ulL0u0JNsYI='
    driver_license_selfie_credentials_secret = 'tivdId6RNYNsvXYPppdzrbxOBuBOr9wXRPDcCvnXU7E='

    def test_creation(self, passport_data):
        assert isinstance(passport_data, PassportData)

    def test_expected_encrypted_values(self, passport_data):
        personal_details, driver_license, address, utility_bill, email = passport_data.data

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

        assert address.type == 'address'
        assert address.data == RAW_PASSPORT_DATA['data'][2]['data']

        assert utility_bill.type == 'utility_bill'
        assert isinstance(utility_bill.files[0], PassportFile)
        assert utility_bill.files[0].file_id == self.utility_bill_1_file_id
        assert isinstance(utility_bill.files[1], PassportFile)
        assert utility_bill.files[1].file_id == self.utility_bill_2_file_id

        assert email.type == 'email'
        assert email.email == 'fb3e3i47zt@dispostable.com'

    def test_expected_decrypted_values(self, passport_data):
        (personal_details, driver_license, address,
         utility_bill, email) = passport_data.decrypted_data

        assert personal_details.type == 'personal_details'
        assert personal_details.data.to_dict() == {'gender': 'female',
                                                   'residence_country_code': 'DK',
                                                   'country_code': 'DK',
                                                   'birth_date': '01.01.2001',
                                                   'first_name': 'FIRSTNAME',
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
        data['credentials']['hash'] = b'notcorrecthash'
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
