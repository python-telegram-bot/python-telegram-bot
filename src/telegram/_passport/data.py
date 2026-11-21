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
# pylint: disable=missing-module-docstring

from telegram._telegramobject import TelegramObject
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class PersonalDetails(TelegramObject):
    """
    This object represents personal details.

    Args:
        first_name (:obj:`str`): First Name.
        middle_name (:obj:`str`): Optional. First Name.
        last_name (:obj:`str`): Last Name.
        birth_date (:obj:`str`): Date of birth in DD.MM.YYYY format.
        gender (:obj:`str`): Gender, male or female.
        country_code (:obj:`str`): Citizenship (ISO 3166-1 alpha-2 country code).
        residence_country_code (:obj:`str`): Country of residence (ISO 3166-1 alpha-2 country
            code).
        first_name_native (:obj:`str`): First Name in the language of the user's country of
            residence.
        middle_name_native (:obj:`str`): Optional. Middle Name in the language of the user's
            country of residence.
        last_name_native (:obj:`str`): Last Name in the language of the user's country of
            residence.

    Attributes:
        first_name (:obj:`str`): First Name.
        middle_name (:obj:`str`): Optional. First Name.
        last_name (:obj:`str`): Last Name.
        birth_date (:obj:`str`): Date of birth in DD.MM.YYYY format.
        gender (:obj:`str`): Gender, male or female.
        country_code (:obj:`str`): Citizenship (ISO 3166-1 alpha-2 country code).
        residence_country_code (:obj:`str`): Country of residence (ISO 3166-1 alpha-2 country
            code).
        first_name_native (:obj:`str`): First Name in the language of the user's country of
            residence.
        middle_name_native (:obj:`str`): Optional. Middle Name in the language of the user's
            country of residence.
        last_name_native (:obj:`str`): Last Name in the language of the user's country of
            residence.
    """

    # Required
    first_name: str = tg_field()
    last_name: str = tg_field()
    birth_date: str = tg_field()
    gender: str = tg_field()
    country_code: str = tg_field()
    residence_country_code: str = tg_field()
    # Optional
    first_name_native: str | None = tg_field(default=None)
    last_name_native: str | None = tg_field(default=None)
    middle_name: str | None = tg_field(default=None)
    middle_name_native: str | None = tg_field(default=None)


@tg_dataclass()
class ResidentialAddress(TelegramObject):
    """
    This object represents a residential address.

    Args:
        street_line1 (:obj:`str`): First line for the address.
        street_line2 (:obj:`str`): Optional. Second line for the address.
        city (:obj:`str`): City.
        state (:obj:`str`): Optional. State.
        country_code (:obj:`str`): ISO 3166-1 alpha-2 country code.
        post_code (:obj:`str`): Address post code.

    Attributes:
        street_line1 (:obj:`str`): First line for the address.
        street_line2 (:obj:`str`): Optional. Second line for the address.
        city (:obj:`str`): City.
        state (:obj:`str`): Optional. State.
        country_code (:obj:`str`): ISO 3166-1 alpha-2 country code.
        post_code (:obj:`str`): Address post code.
    """

    # Required
    street_line1: str = tg_field()
    street_line2: str = tg_field()
    city: str = tg_field()
    state: str = tg_field()
    country_code: str = tg_field()
    post_code: str = tg_field()


@tg_dataclass()
class IdDocumentData(TelegramObject):
    """
    This object represents the data of an identity document.

    Args:
        document_no (:obj:`str`): Document number.
        expiry_date (:obj:`str`): Optional. Date of expiry, in DD.MM.YYYY format.

    Attributes:
        document_no (:obj:`str`): Document number.
        expiry_date (:obj:`str`): Optional. Date of expiry, in DD.MM.YYYY format.
    """

    document_no: str = tg_field()
    expiry_date: str = tg_field()
