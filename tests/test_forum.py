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

TEST_TOPIC_ICON_COLOR = 0x6FB9F0
TEST_TOPIC_NAME = "Sad bot true: real stories"
# TODO replace with something meaningful when getForumTopicIconStickers is implemented?
TEST_TOPIC_EMOJI_ID = "some_id"


@pytest.fixture(scope="module")
async def emoji_id(bot):
    emoji_sticker_list = await bot.get_forum_topic_icon_stickers()
    first_sticker = emoji_sticker_list[0]
    return first_sticker.custom_emoji_id


@pytest.fixture
async def create_and_delete_topic(bot, forum_group_id, emoji_id):
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


@pytest.fixture
def topic(forum_group_id, emoji_id):
    return ForumTopic(
        message_thread_id=forum_group_id,
        name=TEST_TOPIC_NAME,
        icon_color=TEST_TOPIC_ICON_COLOR,
        icon_custom_emoji_id=TEST_TOPIC_EMOJI_ID,
    )


class TestForumTopic:
    def test_slot_behaviour(self, mro_slots, topic):
        for attr in topic.__slots__:
            assert getattr(topic, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(topic)) == len(set(mro_slots(topic))), "duplicate slot"

    def test_expected_values(self, forum_group_id, topic):
        assert topic.message_thread_id == forum_group_id
        assert topic.icon_color == TEST_TOPIC_ICON_COLOR
        assert topic.name == TEST_TOPIC_NAME
        assert topic.icon_custom_emoji_id == TEST_TOPIC_EMOJI_ID

    def test_de_json(self, bot, forum_group_id):
        assert ForumTopic.de_json(None, bot=bot) is None

        json_dict = {
            "message_thread_id": forum_group_id,
            "name": TEST_TOPIC_NAME,
            "icon_color": TEST_TOPIC_ICON_COLOR,
            "icon_custom_emoji_id": TEST_TOPIC_EMOJI_ID,
        }
        topic = ForumTopic.de_json(json_dict, bot)
        assert topic.api_kwargs == {}

        assert topic.message_thread_id == forum_group_id
        assert topic.icon_color == TEST_TOPIC_ICON_COLOR
        assert topic.name == TEST_TOPIC_NAME
        assert topic.icon_custom_emoji_id == TEST_TOPIC_EMOJI_ID

    def test_to_dict(self, forum_group_id, topic):
        topic_dict = topic.to_dict()

        assert isinstance(topic_dict, dict)
        assert topic_dict["message_thread_id"] == forum_group_id
        assert topic_dict["name"] == TEST_TOPIC_NAME
        assert topic_dict["icon_color"] == TEST_TOPIC_ICON_COLOR
        assert topic_dict["icon_custom_emoji_id"] == TEST_TOPIC_EMOJI_ID

    def test_equality(self, forum_group_id):
        a = ForumTopic(
            message_thread_id=forum_group_id,
            name=TEST_TOPIC_NAME,
            icon_color=TEST_TOPIC_ICON_COLOR,
        )
        b = ForumTopic(
            message_thread_id=forum_group_id,
            name=TEST_TOPIC_NAME,
            icon_color=TEST_TOPIC_ICON_COLOR,
            icon_custom_emoji_id=TEST_TOPIC_EMOJI_ID,
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
    async def test_create_forum_topic(self, create_and_delete_topic):
        result = create_and_delete_topic
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
        assert result is True, "Topic was not deleted"

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

    # we sadly do not have access to a test group right now so we only test params right now
    async def test_edit_forum_topic_all_params(self, monkeypatch, bot, chat_id):
        # TODO this no longer fails but still needs reworking?
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

    @pytest.mark.flaky(3, 1)
    async def test_send_message_to_topic(self, bot, forum_group_id, create_and_delete_topic):
        test_string = "Topics are forever"

        # TODO attribute instead of dict key when the method is implemented
        message_thread_id = create_and_delete_topic["message_thread_id"]

        message = await bot.send_message(
            chat_id=forum_group_id, text=test_string, message_thread_id=message_thread_id
        )

        assert message.text == test_string
        assert message.is_topic_message is True
        assert message.message_thread_id == message_thread_id


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

    def test_equality(self):
        a = ForumTopicCreated(name=TEST_TOPIC_NAME, icon_color=TEST_TOPIC_ICON_COLOR)
        b = ForumTopicCreated(
            name=TEST_TOPIC_NAME,
            icon_color=TEST_TOPIC_ICON_COLOR,
            icon_custom_emoji_id=TEST_TOPIC_EMOJI_ID,
        )
        c = ForumTopicCreated(name=f"{TEST_TOPIC_NAME}!", icon_color=TEST_TOPIC_ICON_COLOR)
        d = ForumTopicCreated(name=TEST_TOPIC_NAME, icon_color=0xFFD67E)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

    @pytest.mark.flaky(3, 1)
    async def test_create_forum_topic_returns_good_object(
        self, bot, forum_group_id, create_and_delete_topic
    ):
        data = await bot.get_updates()

        last_message = data[-1].message
        assert last_message.forum_topic_created.name == TEST_TOPIC_NAME


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
