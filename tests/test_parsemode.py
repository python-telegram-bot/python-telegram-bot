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

from telegram import ParseMode


class TestParseMode(object):
    markdown_text = '*bold* _italic_ [link](http://google.com) [name](tg://user?id=123456789).'
    html_text = ('<b>bold</b> <i>italic</i> <a href="http://google.com">link</a> '
                 '<a href="tg://user?id=123456789">name</a>.')
    formatted_text_formatted = u'bold italic link name.'

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_message_with_parse_mode_markdown(self, bot, chat_id):
        message = bot.send_message(chat_id=chat_id, text=self.markdown_text,
                                   parse_mode=ParseMode.MARKDOWN)

        assert message.text == self.formatted_text_formatted

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_message_with_parse_mode_html(self, bot, chat_id):
        message = bot.send_message(chat_id=chat_id, text=self.html_text,
                                   parse_mode=ParseMode.HTML)

        assert message.text == self.formatted_text_formatted
