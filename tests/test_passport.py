#!/usr/bin/env python
#
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

from telegram import PassportData, PassportFile

RAW_PASSPORT_DATA = {'data': [{'type': 'personal_details',
                               'data': 'tj3pNwOpN+ZHsyb6F3aJcNmEyPxrOtGTbu3waBlCQDNaQ9oJlkbXpw+HI3y9faq/+TCeB/WsS/2TxRXTKZw4zXvGP2UsfdRkJ2SQq6x+Ffe/oTF9/q8sWp2BwU3hHUOz7ec1/QrdPBhPJjbwSykEBNggPweiBVDZ0x/DWJ0guCkGT9smYGqog1vqlqbIWG7AWcxVy2fpUy9w/zDXjxj5WQ3lRpHJmi46s9xIHobNGGBvWw6/bGBCInMoovgqRCEu1sgz2QXF3wNiUzGFycEzLz7o+1htLys5n8Pdi9MG4RY='},  # noqa: E501
                              {'type': 'driver_license',
                               'data': 'hOXQ/iHSGRDFXqql3yETA4AiP0mdlwmo9RtGS+Qg9E5okrN/yTcPNtBKb2fLA0posk35bvevN53cyJMHZnxErEFTSw/FQjPyRFdJUyjGNPeu4yOI73uk5eRVLTAlA2G0eN2azzfS/QOBGL19N3pHk9hMTZYPCBTDt89MHhRQS7Z3YWRSzFcFiEhktHv/ezgcg3EWtsUQ8K4J2445uoZzbB8wsQ6RM4ibn08RfjV6dNyVrj8jBGUpCBlA6iY60rFQM+LZ9ByI3OeS53bnIAMQC2rHHbV/wkzS6PbufOzjZgJq26aCLmC5YDomrpcrdvk0fvi6aEuBJEI3zcteh2fh/Q==',  # noqa: E501
                               'selfie': {'file_id': 'DgADBAADEQQAAkopgFNr6oi-wISRtAI',
                                          'file_date': 1534074942},
                               'reverse_side': {'file_id': 'DgADBAADNQQAAtoagFPf4wwmFZdmyQI',
                                                'file_date': 1534074942},
                               'front_side': {'file_id': 'DgADBAADxwMAApnQgVPK2-ckL2eXVAI',
                                              'file_date': 1534074942}},
                              {'type': 'address',
                               'data': 'j9SksVkSj128DBtZA+3aNjSFNirzv+R97guZaMgae4Gi0oDVNAF7twPR7j9VSmPedfJrEwL3O889Ei+a5F1xyLLyEI/qEBljvL70GFIhYGitS0JmNabHPHSZrjOl8b4s/0Z0Px2GpLO5siusTLQonimdUvu4UPjKquYISmlKEKhtmGATy+h+JDjNCYuOkhakeNw0Rk0BHgj0C3fCb7WZNQSyVb+2GTu6caR6eXf/AFwFp0TV3sRz3h0WIVPW8bna'},  # noqa: E501
                              {'type': 'utility_bill', 'files': [
                                  {'file_id': 'DgADBAADLAMAAhwfgVMyfGa5Nr0LvAI',
                                   'file_date': 1534074988},
                                  {'file_id': 'DgADBAADaQQAAsFxgVNVfLZuT-_3ZQI',
                                   'file_date': 1534074988}]},
                              {'type': 'email', 'email': 'fb3e3i47zt@dispostable.com'}],
                     'credentials': {
                         'data': 'uI/g4fJLVO6132t+yuBvKExTpTubinscH8KLVc8YPuo1SiXaBg4A6AaVdv60CPViMw8n+ShVWOTL6oN5Ye0+CC2/URZ0eeTMJcKkvJYRI0Q6YJ3aeeEzslwORKho0mGk5xSWpPV5LHXhRIlgUMA32NkbNuzzoij7OhqxvuDE50/0pAUKtxy69h+heAzxFj8+jYjgnOwgwNa6FGUG59oUozgpB98XrEeWGW+JIGE9fux8dSGkFhF2SjkmdW6b2Gexuq94TVGDgFigSvqMOgZj9slZI4UEdZBIGldPHrc8/+EuqWv+WKWU8hdj1dxfY/pNvonb8MwrQLrUyNafdLq5QD4Kmg3XPnZTI9bsYUf6xO9oKU42JezDcRbaCqKkUn6UceCkV2hHMJP4aVVI9Bad1k/rXlaDh8PUV19n6tct5UH8JfkBbGlj2uASI5lPasIvnWg9s1vsZ4ynE2YAuU4iotMkgmJkj1+JCl8Ul9uqzfiK0IbYfu57V82gUEjn6c4br49pY+Cvo9od9Lx8fSJCiXq+DdmDTfIZxpeFqEYeJi6/v0CjJni4CtS6LJGo9JUR2MlqOAiyOLomadlrZyzC2eLm8X6ouIXTxtbUqzxcTiH/r23NQ44YwJpMdDiulNuPg0tEyio8TokHj9APORiW+QIw4zLZFyBEorT1DSALm4AV3A1lIg0svOncDkOqa3ZydQ0tdysoXOq5Zsu+Qu/DQZQz5IGEHb7N9QW6KZDGfBOP5Ok04OxlXO8UaTZr6mysmu8jDOlqtitLKSCGDy0LPfITzehTqfEu0KrtmxI91zJtiNyE4g+oBzQsLwQ7vSp1xl7YNViDi8ea/upZdRavh3NthVD5TxyNJedt4Xp8q5/H5kSV/EFhumONPwBwOuN4KrsCQEaNtHZfYB8SH1v0rWbiFw3/owxCrCPqgEwMGnx+JTqsAplurIZfxsNz+57O4Hq10VVt7yhroq9UpIAR8C8hW58dcZBflWyQwG8HalYAaPJ/teSLP9o6MyiqrUkADbNBOFsUhIerq6Q0BnQ941sWg10BkG8oQSU6JdnZ1Ygml2gpFabBRXeeF5ijD0Y9Bq8D3vDnHKx/GziAK0aKlwSqfTmJ+C1hm7AxBekjtDavkBeq5bIOtxYaXqrtunQFAZRCrcnQEg0DPY6dYw+jmOR0NuHRMU5KeZ0994Jn0TRGiUoJtLp1MHJ2D1MCWG3Fp9Ps7vB46a9XiGYHJUdJjHsavvQRQjhB1FvA/kxXNubCjAOPLUz1j+BEkUUgwi65l8+pViHUCIhBdLJn7S0J9HbMsc3jXOFusfvXfyvf2SZMqyhEscs/2HzYgbCWVSxQ//6eimZqvW4an1JIEfH1xUH3zS0HvS7NWChtX1Cj+jJ2vw+lyom6a84wJ2mjSRVcaV6JZa2mIf2IuXfX8EMZwKMDJagkQ7effV3MrnCNrXUXJYn8wVm6l+uP+R9mCn9qbGlvWToCID0YM8MTxJ0LgzC0n93m46OxxCI1p1hPzVrmDCcKt3OASe0zVat415/sz9TTU7Rm8oNSAVUVNo7FRg2XwEb9VupGMjlscu4cJKLCtUpImSKDKlVLH2KYy6s4NdPjOjqtjQLRoaCxbYHmNXXE+vVwPiNBK/bBVT3XJgdmbkXa/PDnMjhAmn0huuxBu8GsTOs+bBdyDCbr6mY6EzN9lCPspEoOPs7nmREpjrvGmEqEddRteyAebpVqZQhqklyT3RVl8AmfoF7QgTi0NYqFb50Lgou3hFrMg7isG5EKU+IKI5WfzyWONlHNSpvO',  # noqa: E501
                         'hash': 'qyi5vQ2HCVjVMHb+l6HQ4krmvwwEkvm6Qmdf5GJcohM=',
                         'secret': 'kgJE0VLB9enOq5fhhX8gOv0xoaMIcskmRPOG1eMbiC/Q8slr7kur12H/YIoOfd7/DQ0ggE7TAAe34PypFvtmwt5fDVtqtPl9YoCeAOCFWxHxLgTCLbzoJ0lTJXoJkdHjlvR2lKaP+rMtaU1w8WOpYOGiNXyblQoWwFRrWNTHmHnmwBfGBFCj/vp89+C1viEYHeWPPUkBhf1vT31L70BEoe8hxORJEDg+jY+80W2nFdIWNBF+o9GSmbMWFtd7UFiuLPp2JUBCy8XuHozk8xFk/PN6m6DgSu32rC4YBJv/sWGUo/MmH0nxR3gaiEkj+9rWIybCNAwgfdQpk/KH2RCF8g=='}}  # noqa: E501


@pytest.fixture(scope='function')
def all_passport_data():
    raw_passport_data = deepcopy(RAW_PASSPORT_DATA)
    return [{'type': 'personal_details',
             'data': raw_passport_data['data'][0]['data']},
            {'type': 'passport',
             'data': raw_passport_data['data'][1]['data'],
             'front_side': raw_passport_data['data'][1]['front_side'],
             'selfie': raw_passport_data['data'][1]['selfie']},
            {'type': 'internal_passport',
             'data': raw_passport_data['data'][1]['data'],
             'front_side': raw_passport_data['data'][1]['front_side'],
             'selfie': raw_passport_data['data'][1]['selfie']},
            {'type': 'driver_license',
             'data': raw_passport_data['data'][1]['data'],
             'front_side': raw_passport_data['data'][1]['front_side'],
             'reverse_side': raw_passport_data['data'][1]['reverse_side'],
             'selfie': raw_passport_data['data'][1]['selfie']},
            {'type': 'identity_card',
             'data': raw_passport_data['data'][1]['data'],
             'front_side': raw_passport_data['data'][1]['front_side'],
             'reverse_side': raw_passport_data['data'][1]['reverse_side'],
             'selfie': raw_passport_data['data'][1]['selfie']},
            {'type': 'address',
             'data': raw_passport_data['data'][2]['data']},
            {'type': 'utility_bill',
             'files': raw_passport_data['data'][3]['files']},
            {'type': 'bank_statement',
             'files': raw_passport_data['data'][3]['files']},
            {'type': 'rental_agreement',
             'files': raw_passport_data['data'][3]['files']},
            {'type': 'passport_registration',
             'files': raw_passport_data['data'][3]['files']},
            {'type': 'temporary_registration',
             'files': raw_passport_data['data'][3]['files']},
            {'type': 'email',
             'email': 'fb3e3i47zt@dispostable.com'},
            {'type': 'phone_number',
             'phone_number': 'fb3e3i47zt@dispostable.com'}]


@pytest.fixture(scope='function')
def passport_data(bot):
    return PassportData.de_json(deepcopy(RAW_PASSPORT_DATA), bot=bot)


class TestPassport(object):
    driver_license_selfie_file_id = 'DgADBAADEQQAAkopgFNr6oi-wISRtAI'
    driver_license_front_side_file_id = 'DgADBAADxwMAApnQgVPK2-ckL2eXVAI'
    driver_license_reverse_side_file_id = 'DgADBAADNQQAAtoagFPf4wwmFZdmyQI'
    utility_bill_1_file_id = 'DgADBAADLAMAAhwfgVMyfGa5Nr0LvAI'
    utility_bill_2_file_id = 'DgADBAADaQQAAsFxgVNVfLZuT-_3ZQI'

    def test_creation(self, passport_data):
        assert isinstance(passport_data, PassportData)

    def test_expected_values(self, passport_data):
        personal_details, driver_license, address, utility_bill, email = passport_data.data

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
        credentials = passport_data.credentials.to_dict()

        # Copy credentials from other types to all types so we can decrypt everything
        sd = credentials['data']['secure_data']
        credentials['data']['secure_data'] = {
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

        assert isinstance(PassportData.de_json({
            'data': all_passport_data,
            'credentials': credentials
        }, bot=bot), PassportData)

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
