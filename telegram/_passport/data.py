#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
from typing import TYPE_CHECKING, Any

from telegram._telegramobject import TelegramObject

if TYPE_CHECKING:
    from telegram import Bot


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
        first_name_native (:obj:`str`): First Name in the language of the user's country of
            residence.
        middle_name_native (:obj:`str`): Optional. Middle Name in the language of the user's
            country of residence.
        last_name_native (:obj:`str`): Last Name in the language of the user's country of
            residence.
    """

    __slots__ = (
        "middle_name",
        "first_name_native",
        "last_name_native",
        "residence_country_code",
        "first_name",
        "last_name",
        "country_code",
        "gender",
        "middle_name_native",
        "birth_date",
    )

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: str,
        gender: str,
        country_code: str,
        residence_country_code: str,
        first_name_native: str = None,
        last_name_native: str = None,
        middle_name: str = None,
        middle_name_native: str = None,
        bot: "Bot" = None,
        **_kwargs: Any,
    ):
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

        self.set_bot(bot)


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

    __slots__ = (
        "post_code",
        "city",
        "country_code",
        "street_line2",
        "street_line1",
        "state",
    )

    def __init__(
        self,
        street_line1: str,
        street_line2: str,
        city: str,
        state: str,
        country_code: str,
        post_code: str,
        bot: "Bot" = None,
        **_kwargs: Any,
    ):
        # Required
        self.street_line1 = street_line1
        self.street_line2 = street_line2
        self.city = city
        self.state = state
        self.country_code = country_code
        self.post_code = post_code

        self.set_bot(bot)


class IdDocumentData(TelegramObject):
    """
    This object represents the data of an identity document.

    Attributes:
        document_no (:obj:`str`): Document number.
        expiry_date (:obj:`str`): Optional. Date of expiry, in DD.MM.YYYY format.
    """

    __slots__ = ("document_no", "expiry_date")

    def __init__(self, document_no: str, expiry_date: str, bot: "Bot" = None, **_kwargs: Any):
        self.document_no = document_no
        self.expiry_date = expiry_date

        self.set_bot(bot)
