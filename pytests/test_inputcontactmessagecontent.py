#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import json

import pytest

from telegram import InputContactMessageContent, InputMessageContent

@pytest.fixture(scope='class')
def json_dict():
    return {
            'first_name': TestInputContactMessageContent.first_name,
            'phone_number': TestInputContactMessageContent.phone_number,
            'last_name': TestInputContactMessageContent.last_name,
        }

@pytest.fixture(scope='class')
def input_contact_message_content():
   return InputContactMessageContent(first_name=TestInputContactMessageContent.first_name, phone_number=TestInputContactMessageContent.phone_number, last_name=TestInputContactMessageContent.last_name)

class TestInputContactMessageContent:
    """This object represents Tests for Telegram InputContactMessageContent."""

    phone_number = 'phone number'
    first_name = 'first name'
    last_name = 'last name'
    
    
    
    def test_de_json(self):
        icmc = InputContactMessageContent.de_json(json_dict, bot)

        assert icmc.first_name == self.first_name
        assert icmc.phone_number == self.phone_number
        assert icmc.last_name == self.last_name

    def test_icmc_de_json_factory(self):
        icmc = InputMessageContent.de_json(json_dict, bot)

        assert isinstance(icmc, InputContactMessageContent)

    def test_icmc_de_json_factory_without_required_args(self):
        json_dict = json_dict

        del (json_dict['phone_number'])
        del (json_dict['first_name'])

        icmc = InputMessageContent.de_json(json_dict, bot)

        assert icmc is False

    def test_to_json(self):
        icmc = InputContactMessageContent.de_json(json_dict, bot)

        json.loads(icmc.to_json())

    def test_to_dict(self):
        icmc = InputContactMessageContent.de_json(json_dict, bot).to_dict()

        assert isinstance(icmc, dict)
        assert json_dict == icmc


