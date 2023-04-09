#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
    @pytest.mark.parametrize(
        ("test_str", "expected"),
        [
            ("*bold*", r"\*bold\*"),
            ("_italic_", r"\_italic\_"),
            ("`code`", r"\`code\`"),
            ("[text_link](https://github.com/)", r"\[text\_link](https://github.com/)"),
        ],
        ids=["bold", "italic", "code", "text_link"],
    )
    def test_escape_markdown(self, test_str, expected):
        assert expected == helpers.escape_markdown(test_str)

    @pytest.mark.parametrize(
        ("test_str", "expected"),
        [
            (r"a_b*c[d]e", r"a\_b\*c\[d\]e"),
            (r"(fg) ", r"\(fg\) "),
            (r"h~I`>JK#L+MN", r"h\~I\`\>JK\#L\+MN"),
            (r"-O=|p{qr}s.t!\ ", r"\-O\=\|p\{qr\}s\.t\!\\ "),
            (r"\u", r"\\u"),
        ],
    )
    def test_escape_markdown_v2(self, test_str, expected):
        assert expected == helpers.escape_markdown(test_str, version=2)

    @pytest.mark.parametrize(
        ("test_str", "expected"),
        [
            (r"mono/pre:", r"mono/pre:"),
            ("`abc`", r"\`abc\`"),
            (r"\int", r"\\int"),
            (r"(`\some \` stuff)", r"(\`\\some \\\` stuff)"),
        ],
    )
    def test_escape_markdown_v2_monospaced(self, test_str, expected):
        assert expected == helpers.escape_markdown(
            test_str, version=2, entity_type=MessageEntity.PRE
        )
        assert expected == helpers.escape_markdown(
            test_str, version=2, entity_type=MessageEntity.CODE
        )

    def test_escape_markdown_v2_text_link(self):
        test_str = "https://url.containing/funny)cha)\\ra\\)cter\\s"
        expected_str = "https://url.containing/funny\\)cha\\)\\\\ra\\\\\\)cter\\\\s"

        assert expected_str == helpers.escape_markdown(
            test_str, version=2, entity_type=MessageEntity.TEXT_LINK
        )

    def test_markdown_invalid_version(self):
        with pytest.raises(ValueError, match="Markdown version must be either"):
            helpers.escape_markdown("abc", version=-1)
        with pytest.raises(ValueError, match="Markdown version must be either"):
            helpers.mention_markdown(1, "abc", version=-1)

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

        with pytest.raises(ValueError, match="Only the following characters"):
            helpers.create_deep_linked_url(username, "text with spaces")

        with pytest.raises(ValueError, match="must not exceed 64"):
            helpers.create_deep_linked_url(username, "0" * 65)

        with pytest.raises(ValueError, match="valid bot_username"):
            helpers.create_deep_linked_url(None, None)
        with pytest.raises(ValueError, match="valid bot_username"):  # too short username, 4 is min
            helpers.create_deep_linked_url("abc", None)

    @pytest.mark.parametrize("message_type", list(MessageType))
    @pytest.mark.parametrize("entity_type", [Update, Message])
    def test_effective_message_type(self, message_type, entity_type):
        def build_test_message(kwargs):
            config = {
                "message_id": 1,
                "from_user": None,
                "date": None,
                "chat": None,
            }
            config.update(**kwargs)
            return Message(**config)

        message = build_test_message({message_type: (True,)})  # tuple for array-type args
        entity = message if entity_type is Message else Update(1, message=message)
        assert helpers.effective_message_type(entity) == message_type

        empty_update = Update(2)
        assert helpers.effective_message_type(empty_update) is None

    def test_effective_message_type_wrong_type(self):
        entity = {}
        with pytest.raises(
            TypeError, match=re.escape(f"neither Message nor Update (got: {type(entity)})")
        ):
            helpers.effective_message_type(entity)

    def test_mention_html(self):
        expected = '<a href="tg://user?id=1">the name</a>'

        assert expected == helpers.mention_html(1, "the name")

    @pytest.mark.parametrize(
        ("test_str", "expected"),
        [
            ("the name", "[the name](tg://user?id=1)"),
            ("under_score", "[under_score](tg://user?id=1)"),
            ("starred*text", "[starred*text](tg://user?id=1)"),
            ("`backtick`", "[`backtick`](tg://user?id=1)"),
            ("[square brackets", "[[square brackets](tg://user?id=1)"),
        ],
    )
    def test_mention_markdown(self, test_str, expected):
        assert expected == helpers.mention_markdown(1, test_str)

    def test_mention_markdown_2(self):
        expected = r"[the\_name](tg://user?id=1)"

        assert expected == helpers.mention_markdown(1, "the_name", 2)
