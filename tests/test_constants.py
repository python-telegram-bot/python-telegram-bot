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

from telegram import constants
from telegram.error import BadRequest


class TestConstants(object):
    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_max_message_length(self, bot, chat_id):
        bot.send_message(chat_id=chat_id, text='a' * constants.MAX_MESSAGE_LENGTH)

        with pytest.raises(BadRequest, match='Message is too long',
                           message='MAX_MESSAGE_LENGTH is no longer valid'):
            bot.send_message(chat_id=chat_id, text='a' * (constants.MAX_MESSAGE_LENGTH + 1))

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_max_caption_length(self, bot, chat_id):
        good_caption = 'a' * constants.MAX_CAPTION_LENGTH
        with open('tests/data/telegram.png', 'rb') as f:
            good_msg = bot.send_photo(photo=f, caption=good_caption, chat_id=chat_id)
        assert good_msg.caption == good_caption

        bad_caption = good_caption + 'Z'
        with pytest.raises(BadRequest, match="Media_caption_too_long",
                           message='MAX_CAPTION_LENGTH is no longer valid'):
            with open('tests/data/telegram.png', 'rb') as f:
                bot.send_photo(photo=f, caption=bad_caption, chat_id=chat_id)
