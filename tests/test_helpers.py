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
import re

import pytest

from telegram import Message, MessageEntity, Update, helpers
from telegram.constants import MessageType


class TestHelpers:
    def test_escape_markdown(self):
        test_str = "*bold*, _italic_, `code`, [text_link](http://github.com/)"
        expected_str = r"\*bold\*, \_italic\_, \`code\`, \[text\_link](http://github.com/)"

        assert expected_str == helpers.escape_markdown(test_str)

    def test_escape_markdown_v2(self):
        test_str = r"a_b*c[d]e (fg) h~I`>JK#L+MN -O=|p{qr}s.t!\ \u"
        expected_str = r"a\_b\*c\[d\]e \(fg\) h\~I\`\>JK\#L\+MN \-O\=\|p\{qr\}s\.t\!\\ \\u"

        assert expected_str == helpers.escape_markdown(test_str, version=2)

    def test_escape_markdown_v2_monospaced(self):

        test_str = r"mono/pre: `abc` \int (`\some \`stuff)"
        expected_str = "mono/pre: \\`abc\\` \\\\int (\\`\\\\some \\\\\\`stuff)"

        assert expected_str == helpers.escape_markdown(
            test_str, version=2, entity_type=MessageEntity.PRE
        )
        assert expected_str == helpers.escape_markdown(
            test_str, version=2, entity_type=MessageEntity.CODE
        )

    def test_escape_markdown_v2_text_link(self):

        test_str = "https://url.containing/funny)cha)\\ra\\)cter\\s"
        expected_str = "https://url.containing/funny\\)cha\\)\\\\ra\\\\\\)cter\\\\s"

        assert expected_str == helpers.escape_markdown(
            test_str, version=2, entity_type=MessageEntity.TEXT_LINK
        )

    def test_markdown_invalid_version(self):
        with pytest.raises(ValueError):
            helpers.escape_markdown("abc", version=-1)

    def test_create_deep_linked_url(self):
        username = "JamesTheMock"

        payload = "hello"
        expected = f"https://t.me/{username}?start={payload}"
        actual = helpers.create_deep_linked_url(username, payload)
        assert expected == actual

        expected = f"https://t.me/{username}?startgroup={payload}"
        actual = helpers.create_deep_linked_url(username, payload, group=True)
        assert expected == actual

        payload = ""
        expected = f"https://t.me/{username}"
        assert expected == helpers.create_deep_linked_url(username)
        assert expected == helpers.create_deep_linked_url(username, payload)
        payload = None
        assert expected == helpers.create_deep_linked_url(username, payload)

        with pytest.raises(ValueError):
            helpers.create_deep_linked_url(username, "text with spaces")

        with pytest.raises(ValueError):
            helpers.create_deep_linked_url(username, "0" * 65)

        with pytest.raises(ValueError):
            helpers.create_deep_linked_url(None, None)
        with pytest.raises(ValueError):  # too short username (4 is minimum)
            helpers.create_deep_linked_url("abc", None)

    @pytest.mark.parametrize("message_type", list(MessageType))
    @pytest.mark.parametrize("entity_type", [Update, Message])
    def test_effective_message_type(self, message_type, entity_type):
        def build_test_message(kwargs):
            config = dict(
                message_id=1,
                from_user=None,
                date=None,
                chat=None,
            )
            config.update(**kwargs)
            return Message(**config)

        message = build_test_message({message_type: True})
        entity = message if entity_type is Message else Update(1, message=message)
        assert helpers.effective_message_type(entity) == message_type

        empty_update = Update(2)
        assert helpers.effective_message_type(empty_update) is None

    def test_effective_message_type_wrong_type(self):
        entity = dict()
        with pytest.raises(
            TypeError, match=re.escape(f"neither Message nor Update (got: {type(entity)})")
        ):
            helpers.effective_message_type(entity)

    def test_mention_html(self):
        expected = '<a href="tg://user?id=1">the name</a>'

        assert expected == helpers.mention_html(1, "the name")

    def test_mention_markdown(self):
        expected = "[the name](tg://user?id=1)"

        assert expected == helpers.mention_markdown(1, "the name")

    def test_mention_markdown_2(self):
        expected = r"[the\_name](tg://user?id=1)"

        assert expected == helpers.mention_markdown(1, "the_name")
