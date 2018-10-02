#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
from telegram import TelegramObject


class PersonalDetails(TelegramObject):
    """
    This object represents personal details.

    Attributes:
        first_name (:obj:`str`): First Name.
        middle_name (:obj:`str`): Optional. First Name.
        last_name (:obj:`str`): Last Name.
        birth_date (:obj:`str`): Date of birth in DD.MM.YYYY format.
        gender (:obj:`str`): Gender, male or female.
        country_code (:obj:`str`): Citizenship (ISO 3166-1 alpha-2 country code).
        residence_country_code (:obj:`str`): Country of residence (ISO 3166-1 alpha-2 country
            code).
        first_name (:obj:`str`): First Name in the language of the user's country of residence.
        middle_name (:obj:`str`): Optional. Middle Name in the language of the user's country of
            residence.
        last_name (:obj:`str`): Last Name in the language of the user's country of residence.
    """

    def __init__(self, first_name, last_name, birth_date, gender, country_code,
                 residence_country_code, first_name_native=None,
                 last_name_native=None, middle_name=None,
                 middle_name_native=None, bot=None, **kwargs):
        # Required
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.birth_date = birth_date
        self.gender = gender
        self.country_code = country_code
        self.residence_country_code = residence_country_code
        self.first_name_native = first_name_native
        self.last_name_native = last_name_native
        self.middle_name_native = middle_name_native

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(bot=bot, **data)


class ResidentialAddress(TelegramObject):
    """
    This object represents a residential address.

    Attributes:
        street_line1 (:obj:`str`): First line for the address.
        street_line2 (:obj:`str`): Optional. Second line for the address.
        city (:obj:`str`): City.
        state (:obj:`str`): Optional. State.
        country_code (:obj:`str`): ISO 3166-1 alpha-2 country code.
        post_code (:obj:`str`): Address post code.
    """

    def __init__(self, street_line1, street_line2, city, state, country_code,
                 post_code, bot=None, **kwargs):
        # Required
        self.street_line1 = street_line1
        self.street_line2 = street_line2
        self.city = city
        self.state = state
        self.country_code = country_code
        self.post_code = post_code

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(bot=bot, **data)


class IdDocumentData(TelegramObject):
    """
    This object represents the data of an identity document.

    Attributes:
        document_no (:obj:`str`): Document number.
        expiry_date (:obj:`str`): Optional. Date of expiry, in DD.MM.YYYY format.
    """

    def __init__(self, document_no, expiry_date, bot=None, **kwargs):
        self.document_no = document_no
        self.expiry_date = expiry_date

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(bot=bot, **data)
