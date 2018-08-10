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
    def __init__(self, first_name, last_name, birth_date, gender, country_code,
                 residence_country_code, bot=None, **kwargs):
        # Required
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.gender = gender
        self.country_code = country_code
        self.residence_country_code = residence_country_code

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(bot=bot, **data)


class ResidentialAddress(TelegramObject):
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
    def __init__(self, document_no, expiry_date, bot=None, **kwargs):
        self.document_no = document_no
        self.expiry_date = expiry_date

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(bot=bot, **data)
