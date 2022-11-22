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
import pytest

from telegram import ForumTopic, ForumTopicClosed, ForumTopicCreated, ForumTopicReopened, Sticker

TEST_MSG_TEXT = "Topics are forever"
TEST_TOPIC_ICON_COLOR = 0x6FB9F0
TEST_TOPIC_NAME = "Sad bot true: real stories"


@pytest.fixture(scope="module")
async def emoji_id(bot):
    emoji_sticker_list = await bot.get_forum_topic_icon_stickers()
    first_sticker = emoji_sticker_list[0]
    return first_sticker.custom_emoji_id


@pytest.fixture
async def forum_topic_object(forum_group_id, emoji_id):
    return ForumTopic(
        message_thread_id=forum_group_id,
        name=TEST_TOPIC_NAME,
        icon_color=TEST_TOPIC_ICON_COLOR,
        icon_custom_emoji_id=emoji_id,
    )


@pytest.fixture
async def real_topic(bot, emoji_id, forum_group_id):
    result = await bot.create_forum_topic(
        chat_id=forum_group_id,
        name=TEST_TOPIC_NAME,
        icon_color=TEST_TOPIC_ICON_COLOR,
        icon_custom_emoji_id=emoji_id,
    )

    yield result

    result = await bot.delete_forum_topic(
        chat_id=forum_group_id, message_thread_id=result.message_thread_id
    )
    assert result is True, "Topic was not deleted"


class TestForumTopic:
    def test_slot_behaviour(self, mro_slots, forum_topic_object):
        for attr in forum_topic_object.__slots__:
            assert getattr(forum_topic_object, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(forum_topic_object)) == len(
            set(mro_slots(forum_topic_object))
        ), "duplicate slot"

    async def test_expected_values(self, emoji_id, forum_group_id, forum_topic_object):
        assert forum_topic_object.message_thread_id == forum_group_id
        assert forum_topic_object.icon_color == TEST_TOPIC_ICON_COLOR
        assert forum_topic_object.name == TEST_TOPIC_NAME
        assert forum_topic_object.icon_custom_emoji_id == emoji_id

    def test_de_json(self, bot, emoji_id, forum_group_id):
        assert ForumTopic.de_json(None, bot=bot) is None

        json_dict = {
            "message_thread_id": forum_group_id,
            "name": TEST_TOPIC_NAME,
            "icon_color": TEST_TOPIC_ICON_COLOR,
            "icon_custom_emoji_id": emoji_id,
        }
        topic = ForumTopic.de_json(json_dict, bot)
        assert topic.api_kwargs == {}

        assert topic.message_thread_id == forum_group_id
        assert topic.icon_color == TEST_TOPIC_ICON_COLOR
        assert topic.name == TEST_TOPIC_NAME
        assert topic.icon_custom_emoji_id == emoji_id

    def test_to_dict(self, emoji_id, forum_group_id, forum_topic_object):
        topic_dict = forum_topic_object.to_dict()

        assert isinstance(topic_dict, dict)
        assert topic_dict["message_thread_id"] == forum_group_id
        assert topic_dict["name"] == TEST_TOPIC_NAME
        assert topic_dict["icon_color"] == TEST_TOPIC_ICON_COLOR
        assert topic_dict["icon_custom_emoji_id"] == emoji_id

    def test_equality(self, emoji_id, forum_group_id):
        a = ForumTopic(
            message_thread_id=forum_group_id,
            name=TEST_TOPIC_NAME,
            icon_color=TEST_TOPIC_ICON_COLOR,
        )
        b = ForumTopic(
            message_thread_id=forum_group_id,
            name=TEST_TOPIC_NAME,
            icon_color=TEST_TOPIC_ICON_COLOR,
            icon_custom_emoji_id=emoji_id,
        )
        c = ForumTopic(
            message_thread_id=forum_group_id,
            name=f"{TEST_TOPIC_NAME}!",
            icon_color=TEST_TOPIC_ICON_COLOR,
        )
        d = ForumTopic(
            message_thread_id=forum_group_id + 1,
            name=TEST_TOPIC_NAME,
            icon_color=TEST_TOPIC_ICON_COLOR,
        )
        e = ForumTopic(
            message_thread_id=forum_group_id,
            name=TEST_TOPIC_NAME,
            icon_color=0xFFD67E,
        )

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    @pytest.mark.flaky(3, 1)
    async def test_create_forum_topic(self, real_topic):
        result = real_topic
        assert isinstance(result, ForumTopic)
        assert result.name == TEST_TOPIC_NAME
        assert result.message_thread_id
        assert isinstance(result.icon_color, int)
        assert isinstance(result.icon_custom_emoji_id, str)

    async def test_create_forum_topic_with_only_required_args(self, bot, forum_group_id):
        result = await bot.create_forum_topic(chat_id=forum_group_id, name=TEST_TOPIC_NAME)
        assert isinstance(result, ForumTopic)
        assert result.name == TEST_TOPIC_NAME
        assert result.message_thread_id
        assert isinstance(result.icon_color, int)  # color is still there though it was not passed
        assert result.icon_custom_emoji_id is None

        result = await bot.delete_forum_topic(
            chat_id=forum_group_id, message_thread_id=result.message_thread_id
        )
        assert result is True, "Failed to delete forum topic"

    @pytest.mark.flaky(3, 1)
    async def test_get_forum_topic_icon_stickers(self, bot):
        emoji_sticker_list = await bot.get_forum_topic_icon_stickers()
        first_sticker = emoji_sticker_list[0]

        assert first_sticker.emoji == "📰"
        assert first_sticker.height == 512
        assert first_sticker.width == 512
        assert first_sticker.is_animated
        assert not first_sticker.is_video
        assert first_sticker.set_name == "Topics"
        assert first_sticker.type == Sticker.CUSTOM_EMOJI
        assert first_sticker.thumb.width == 128
        assert first_sticker.thumb.height == 128

        # The following data of first item returned has changed in the past already,
        # so check sizes loosely and ID's only by length of string
        assert first_sticker.thumb.file_size in range(2000, 7000)
        assert first_sticker.file_size in range(20000, 70000)
        assert len(first_sticker.custom_emoji_id) == 19
        assert len(first_sticker.thumb.file_unique_id) == 16
        assert len(first_sticker.file_unique_id) == 15

    async def test_edit_forum_topic(self, emoji_id, forum_group_id, bot, real_topic):
        result = await bot.edit_forum_topic(
            chat_id=forum_group_id,
            message_thread_id=real_topic.message_thread_id,
            name=f"{TEST_TOPIC_NAME}_EDITED",
            icon_custom_emoji_id=emoji_id,
        )
        assert result is True, "Failed to edit forum topic"
        # no way of checking the edited name, just the boolean result

    @pytest.mark.flaky(3, 1)
    async def test_send_message_to_topic(self, bot, forum_group_id, real_topic):
        message_thread_id = real_topic.message_thread_id

        message = await bot.send_message(
            chat_id=forum_group_id, text=TEST_MSG_TEXT, message_thread_id=message_thread_id
        )

        assert message.text == TEST_MSG_TEXT
        assert message.is_topic_message is True
        assert message.message_thread_id == message_thread_id

    async def test_close_and_reopen_forum_topic(self, bot, forum_group_id, real_topic):
        message_thread_id = real_topic.message_thread_id

        result = await bot.close_forum_topic(
            chat_id=forum_group_id,
            message_thread_id=message_thread_id,
        )
        assert result is True, "Failed to close forum topic"
        # bot will still be able to send a message to a closed topic, so can't test anything like
        # the inability to post to the topic

        result = await bot.reopen_forum_topic(
            chat_id=forum_group_id,
            message_thread_id=message_thread_id,
        )
        assert result is True, "Failed to reopen forum topic"

    @pytest.mark.xfail(reason="Can fail due to race conditions in GH actions CI")
    async def test_unpin_all_forum_topic_messages(self, bot, forum_group_id, real_topic):
        message_thread_id = real_topic.message_thread_id

        msgs = [
            await (
                await bot.send_message(
                    chat_id=forum_group_id, text=TEST_MSG_TEXT, message_thread_id=message_thread_id
                )
            ).pin()
            for _ in range(2)
        ]

        assert all(msgs) is True, "Message(s) were not pinned"

        # We need 2 or more pinned msgs for this to work, else we get Chat_not_modified error
        result = await bot.unpin_all_forum_topic_messages(
            chat_id=forum_group_id, message_thread_id=message_thread_id
        )
        assert result is True, "Failed to unpin all the messages in forum topic"


@pytest.fixture
def topic_created():
    return ForumTopicCreated(name=TEST_TOPIC_NAME, icon_color=TEST_TOPIC_ICON_COLOR)


class TestForumTopicCreated:
    def test_slot_behaviour(self, topic_created, mro_slots):
        for attr in topic_created.__slots__:
            assert getattr(topic_created, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(topic_created)) == len(
            set(mro_slots(topic_created))
        ), "duplicate slot"

    def test_expected_values(self, topic_created):
        assert topic_created.icon_color == TEST_TOPIC_ICON_COLOR
        assert topic_created.name == TEST_TOPIC_NAME

    def test_de_json(self, bot):
        assert ForumTopicCreated.de_json(None, bot=bot) is None

        json_dict = {"icon_color": TEST_TOPIC_ICON_COLOR, "name": TEST_TOPIC_NAME}
        action = ForumTopicCreated.de_json(json_dict, bot)
        assert action.api_kwargs == {}

        assert action.icon_color == TEST_TOPIC_ICON_COLOR
        assert action.name == TEST_TOPIC_NAME

    def test_to_dict(self, topic_created):
        action_dict = topic_created.to_dict()

        assert isinstance(action_dict, dict)
        assert action_dict["name"] == TEST_TOPIC_NAME
        assert action_dict["icon_color"] == TEST_TOPIC_ICON_COLOR

    def test_equality(self, emoji_id):
        a = ForumTopicCreated(name=TEST_TOPIC_NAME, icon_color=TEST_TOPIC_ICON_COLOR)
        b = ForumTopicCreated(
            name=TEST_TOPIC_NAME,
            icon_color=TEST_TOPIC_ICON_COLOR,
            icon_custom_emoji_id=emoji_id,
        )
        c = ForumTopicCreated(name=f"{TEST_TOPIC_NAME}!", icon_color=TEST_TOPIC_ICON_COLOR)
        d = ForumTopicCreated(name=TEST_TOPIC_NAME, icon_color=0xFFD67E)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


class TestForumTopicClosed:
    def test_slot_behaviour(self, mro_slots):
        action = ForumTopicClosed()
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self):
        action = ForumTopicClosed.de_json({}, None)
        assert action.api_kwargs == {}
        assert isinstance(action, ForumTopicClosed)

    def test_to_dict(self):
        action = ForumTopicClosed()
        action_dict = action.to_dict()
        assert action_dict == {}


class TestForumTopicReopened:
    def test_slot_behaviour(self, mro_slots):
        action = ForumTopicReopened()
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self):
        action = ForumTopicReopened.de_json({}, None)
        assert action.api_kwargs == {}
        assert isinstance(action, ForumTopicReopened)

    def test_to_dict(self):
        action = ForumTopicReopened()
        action_dict = action.to_dict()
        assert action_dict == {}
