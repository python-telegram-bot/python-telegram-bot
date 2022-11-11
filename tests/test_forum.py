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
from flaky import flaky

from telegram import Sticker


class TestForum:
    async def test_get_forum_topic_icon_stickers(self, bot):
        # we expect the first to stay as it is. This might change in the future.
        # If we have to fix this test too often maybe just checking it is set to "something"
        # is enough.
        emoji_sticker_list = await bot.get_forum_topic_icon_stickers()
        print(emoji_sticker_list[0].emoji)
        assert emoji_sticker_list[0].emoji == "📰"
        assert emoji_sticker_list[0].height == 512
        assert emoji_sticker_list[0].width == 512
        assert emoji_sticker_list[0].is_animated
        assert not emoji_sticker_list[0].is_video
        assert emoji_sticker_list[0].set_name == "Topics"
        assert emoji_sticker_list[0].type == Sticker.CUSTOM_EMOJI
        assert emoji_sticker_list[0].custom_emoji_id == "5420143492263320958"
        assert emoji_sticker_list[0].thumb.width == 128
        assert emoji_sticker_list[0].thumb.height == 128
        assert emoji_sticker_list[0].thumb.file_size == 4036
        assert emoji_sticker_list[0].thumb.file_unique_id == "AQADfh0AAso3OEty"
        assert emoji_sticker_list[0].file_size == 57126
        assert emoji_sticker_list[0].file_unique_id == "AgADfh0AAso3OEs"

    # we sadly do not have access to a test group right now so we only test params right now
    async def test_edit_forum_topic_all_params(self, monkeypatch, bot, chat_id):
        async def make_assertion(_, data, *args, **kwargs):
            assert data["chat_id"] == chat_id
            assert data["message_thread_id"] == 1234
            assert data["name"] == "name"
            assert data["icon_custom_emoji_id"] == "icon_custom_emoji_id"

        monkeypatch.setattr(bot, "_post", make_assertion)
        await bot.edit_forum_topic(
            chat_id,
            1234,
            "name",
            "icon_custom_emoji_id",
        )
        monkeypatch.delattr(bot, "_post")

    @flaky(3, 1)
    async def test_send_message_to_topic(self, bot, forum_group_id):
        test_string = "Topics are forever"

        result = await bot._post(
            "createForumTopic",
            {"chat_id": forum_group_id, "name": "Is just a yellow lemon tree"},
        )

        message_thread_id = result["message_thread_id"]

        message = await bot.send_message(
            chat_id=forum_group_id, text=test_string, message_thread_id=message_thread_id
        )

        assert message.text == test_string
        assert message.is_topic_message is True
        assert message.message_thread_id == message_thread_id

        result = await bot._post(
            "deleteForumTopic",
            {"chat_id": forum_group_id, "message_thread_id": message_thread_id},
        )
        assert result is True
