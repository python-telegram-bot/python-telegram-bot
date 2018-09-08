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

import pytest
from flaky import flaky

from telegram import ForceReply


@pytest.fixture(scope='class')
def force_reply():
    return ForceReply(TestForceReply.force_reply, TestForceReply.selective)


class TestForceReply(object):
    force_reply = True
    selective = True

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_message_with_force_reply(self, bot, chat_id, force_reply):
        message = bot.send_message(chat_id, 'text', reply_markup=force_reply)

        assert message.text == 'text'

    def test_expected(self, force_reply):
        assert force_reply.force_reply == self.force_reply
        assert force_reply.selective == self.selective

    def test_to_dict(self, force_reply):
        force_reply_dict = force_reply.to_dict()

        assert isinstance(force_reply_dict, dict)
        assert force_reply_dict['force_reply'] == force_reply.force_reply
        assert force_reply_dict['selective'] == force_reply.selective
