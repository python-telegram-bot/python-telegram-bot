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

from telegram import ForceReply


@pytest.fixture(scope='class')
def json_dict():
    return {
        'force_reply': TestForceReply.force_reply,
        'selective': TestForceReply.selective,
    }


@pytest.fixture(scope='class')
def force_reply():
    return ForceReply(TestForceReply.force_reply, TestForceReply.selective)


class TestForceReply:
    force_reply = True
    selective = True

    def test_send_message_with_force_reply(self, bot, chat_id, force_reply):
        message = bot.sendMessage(
            chat_id,
            'Моё судно на воздушной подушке полно угрей',
            reply_markup=force_reply)

        json.loads(message.to_json())
        assert message.text == 'Моё судно на воздушной подушке полно угрей'

    def test_force_reply_de_json(self, json_dict, bot):
        force_reply = ForceReply.de_json(json_dict, bot)

        assert force_reply.force_reply == self.force_reply
        assert force_reply.selective == self.selective

    def test_force_reply_to_json(self, force_reply):
        json.loads(force_reply.to_json())

    def test_force_reply_to_dict(self, force_reply):
        assert force_reply['force_reply'] == self.force_reply
        assert force_reply['selective'] == self.selective
