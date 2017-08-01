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

from telegram import InputTextMessageContent, InputMessageContent, ParseMode

@pytest.fixture(scope='class')
def json_dict():
    return {
            'parse_mode': TestInputTextMessageContent.parse_mode,
            'message_text': TestInputTextMessageContent.message_text,
            'disable_web_page_preview': TestInputTextMessageContent.disable_web_page_preview,
        }

@pytest.fixture(scope='class')
def input_text_message_content():
   return InputTextMessageContent(parse_mode=TestInputTextMessageContent.parse_mode, message_text=TestInputTextMessageContent.message_text, disable_web_page_preview=TestInputTextMessageContent.disable_web_page_preview)

class TestInputTextMessageContent:
    """This object represents Tests for Telegram InputTextMessageContent."""

    message_text = '*message text*'
    parse_mode = ParseMode.MARKDOWN
    disable_web_page_preview = True
    
    
    
    def test_de_json(self):
        itmc = InputTextMessageContent.de_json(json_dict, bot)

        assert itmc.parse_mode == self.parse_mode
        assert itmc.message_text == self.message_text
        assert itmc.disable_web_page_preview == self.disable_web_page_preview

    def test_itmc_de_json_factory(self):
        itmc = InputMessageContent.de_json(json_dict, bot)

        assert isinstance(itmc, InputTextMessageContent)

    def test_itmc_de_json_factory_without_required_args(self):
        json_dict = json_dict

        del (json_dict['message_text'])

        itmc = InputMessageContent.de_json(json_dict, bot)

        assert itmc is False

    def test_to_json(self):
        itmc = InputTextMessageContent.de_json(json_dict, bot)

        json.loads(itmc.to_json())

    def test_to_dict(self):
        itmc = InputTextMessageContent.de_json(json_dict, bot).to_dict()

        assert isinstance(itmc, dict)
        assert json_dict == itmc


