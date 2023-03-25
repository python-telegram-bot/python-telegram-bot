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
import pytest

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultVideo,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)
from tests.auxil.deprecations import check_thumb_deprecation_warnings_for_args_and_attrs
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_video():
    return InlineQueryResultVideo(
        TestInlineQueryResultVideoBase.id_,
        TestInlineQueryResultVideoBase.video_url,
        TestInlineQueryResultVideoBase.mime_type,
        TestInlineQueryResultVideoBase.thumbnail_url,
        TestInlineQueryResultVideoBase.title,
        video_width=TestInlineQueryResultVideoBase.video_width,
        video_height=TestInlineQueryResultVideoBase.video_height,
        video_duration=TestInlineQueryResultVideoBase.video_duration,
        caption=TestInlineQueryResultVideoBase.caption,
        parse_mode=TestInlineQueryResultVideoBase.parse_mode,
        caption_entities=TestInlineQueryResultVideoBase.caption_entities,
        description=TestInlineQueryResultVideoBase.description,
        input_message_content=TestInlineQueryResultVideoBase.input_message_content,
        reply_markup=TestInlineQueryResultVideoBase.reply_markup,
    )


class TestInlineQueryResultVideoBase:
    id_ = "id"
    type_ = "video"
    video_url = "video url"
    mime_type = "mime type"
    video_width = 10
    video_height = 15
    video_duration = 15
    thumbnail_url = "thumbnail url"
    title = "title"
    caption = "caption"
    parse_mode = "Markdown"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    description = "description"
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultVideoWithoutRequest(TestInlineQueryResultVideoBase):
    def test_slot_behaviour(self, inline_query_result_video):
        inst = inline_query_result_video
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_video):
        assert inline_query_result_video.type == self.type_
        assert inline_query_result_video.id == self.id_
        assert inline_query_result_video.video_url == self.video_url
        assert inline_query_result_video.mime_type == self.mime_type
        assert inline_query_result_video.video_width == self.video_width
        assert inline_query_result_video.video_height == self.video_height
        assert inline_query_result_video.video_duration == self.video_duration
        assert inline_query_result_video.thumbnail_url == self.thumbnail_url
        assert inline_query_result_video.title == self.title
        assert inline_query_result_video.description == self.description
        assert inline_query_result_video.caption == self.caption
        assert inline_query_result_video.parse_mode == self.parse_mode
        assert inline_query_result_video.caption_entities == tuple(self.caption_entities)
        assert (
            inline_query_result_video.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_video.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_caption_entities_always_tuple(self):
        video = InlineQueryResultVideo(
            self.id_, self.video_url, self.mime_type, self.thumbnail_url, self.title
        )
        assert video.caption_entities == ()

    def test_thumb_url_property_deprecation_warning(self, recwarn):
        inline_query_result_video = InlineQueryResultVideo(
            TestInlineQueryResultVideoBase.id_,
            TestInlineQueryResultVideoBase.video_url,
            TestInlineQueryResultVideoBase.mime_type,
            TestInlineQueryResultVideoBase.thumbnail_url,
            TestInlineQueryResultVideoBase.title,
            video_width=TestInlineQueryResultVideoBase.video_width,
            video_height=TestInlineQueryResultVideoBase.video_height,
            video_duration=TestInlineQueryResultVideoBase.video_duration,
            caption=TestInlineQueryResultVideoBase.caption,
            parse_mode=TestInlineQueryResultVideoBase.parse_mode,
            caption_entities=TestInlineQueryResultVideoBase.caption_entities,
            description=TestInlineQueryResultVideoBase.description,
            input_message_content=TestInlineQueryResultVideoBase.input_message_content,
            reply_markup=TestInlineQueryResultVideoBase.reply_markup,
            thumb_url=TestInlineQueryResultVideoBase.thumbnail_url,  # deprecated arg
        )
        assert inline_query_result_video.thumb_url == inline_query_result_video.thumbnail_url
        check_thumb_deprecation_warnings_for_args_and_attrs(
            recwarn,
            __file__,
            deprecated_name="thumb_url",
            new_name="thumbnail_url",
        )

    def test_thumb_url_issues_warning_and_works_without_positional_arg(self, recwarn):
        inline_query_result_video = InlineQueryResultVideo(
            TestInlineQueryResultVideoBase.id_,
            TestInlineQueryResultVideoBase.video_url,
            TestInlineQueryResultVideoBase.mime_type,
            # Positional argument thumbnail_url should be here, but it's not. Code works fine.
            # If user deletes thumb_url from positional arguments and replaces it with a keyword
            # argument while keeping `title` as a positional argument, the code will break.
            # But it should break, given the fact that the user now passes fewer positional
            # arguments than they are expected to.
            title=TestInlineQueryResultVideoBase.title,
            video_width=TestInlineQueryResultVideoBase.video_width,
            video_height=TestInlineQueryResultVideoBase.video_height,
            video_duration=TestInlineQueryResultVideoBase.video_duration,
            caption=TestInlineQueryResultVideoBase.caption,
            parse_mode=TestInlineQueryResultVideoBase.parse_mode,
            caption_entities=TestInlineQueryResultVideoBase.caption_entities,
            description=TestInlineQueryResultVideoBase.description,
            input_message_content=TestInlineQueryResultVideoBase.input_message_content,
            reply_markup=TestInlineQueryResultVideoBase.reply_markup,
            thumb_url=TestInlineQueryResultVideoBase.thumbnail_url,  # deprecated arg
        )
        assert inline_query_result_video.thumb_url == inline_query_result_video.thumbnail_url
        check_thumb_deprecation_warnings_for_args_and_attrs(
            recwarn,
            __file__,
            deprecated_name="thumb_url",
            new_name="thumbnail_url",
        )

    def test_init_throws_error_without_thumbnail_url_and_thumb_url(self, recwarn):
        with pytest.raises(ValueError, match="You must pass either"):
            InlineQueryResultVideo(
                TestInlineQueryResultVideoBase.id_,
                TestInlineQueryResultVideoBase.video_url,
                TestInlineQueryResultVideoBase.mime_type,
                # no thumbnail_url, no thumb_url
                # see note in previous test on `title` being keyword argument here
                title=TestInlineQueryResultVideoBase.title,
                video_width=TestInlineQueryResultVideoBase.video_width,
                video_height=TestInlineQueryResultVideoBase.video_height,
                video_duration=TestInlineQueryResultVideoBase.video_duration,
                caption=TestInlineQueryResultVideoBase.caption,
                parse_mode=TestInlineQueryResultVideoBase.parse_mode,
                caption_entities=TestInlineQueryResultVideoBase.caption_entities,
                description=TestInlineQueryResultVideoBase.description,
                input_message_content=TestInlineQueryResultVideoBase.input_message_content,
                reply_markup=TestInlineQueryResultVideoBase.reply_markup,
            )

    def test_throws_type_error_with_title_not_passed_or_is_none(self):
        # this test is needed because we had to make argument title optional in declaration of
        # __init__() while it is not optional. This had to be done to deal with renaming of
        # thumb_url.  Hence, we have to enforce `title` being required by checking it.
        with pytest.raises(TypeError, match="missing a required argument"):
            InlineQueryResultVideo(
                TestInlineQueryResultVideoBase.id_,
                TestInlineQueryResultVideoBase.video_url,
                TestInlineQueryResultVideoBase.mime_type,
                TestInlineQueryResultVideoBase.thumbnail_url,
                # title is missing
                video_width=TestInlineQueryResultVideoBase.video_width,
                video_height=TestInlineQueryResultVideoBase.video_height,
                video_duration=TestInlineQueryResultVideoBase.video_duration,
                caption=TestInlineQueryResultVideoBase.caption,
                parse_mode=TestInlineQueryResultVideoBase.parse_mode,
                caption_entities=TestInlineQueryResultVideoBase.caption_entities,
                description=TestInlineQueryResultVideoBase.description,
                input_message_content=TestInlineQueryResultVideoBase.input_message_content,
                reply_markup=TestInlineQueryResultVideoBase.reply_markup,
            )

        with pytest.raises(TypeError, match="missing a required argument"):
            InlineQueryResultVideo(
                TestInlineQueryResultVideoBase.id_,
                TestInlineQueryResultVideoBase.video_url,
                TestInlineQueryResultVideoBase.mime_type,
                TestInlineQueryResultVideoBase.thumbnail_url,
                title=None,  # the declaration of __init__ allows it, but we don't.
                video_width=TestInlineQueryResultVideoBase.video_width,
                video_height=TestInlineQueryResultVideoBase.video_height,
                video_duration=TestInlineQueryResultVideoBase.video_duration,
                caption=TestInlineQueryResultVideoBase.caption,
                parse_mode=TestInlineQueryResultVideoBase.parse_mode,
                caption_entities=TestInlineQueryResultVideoBase.caption_entities,
                description=TestInlineQueryResultVideoBase.description,
                input_message_content=TestInlineQueryResultVideoBase.input_message_content,
                reply_markup=TestInlineQueryResultVideoBase.reply_markup,
            )

    def test_throws_value_error_with_different_deprecated_and_new_arg_thumb_url(self):
        with pytest.raises(
            ValueError,
            match="different entities as 'thumb_url' and 'thumbnail_url'",
        ):
            InlineQueryResultVideo(
                TestInlineQueryResultVideoBase.id_,
                TestInlineQueryResultVideoBase.video_url,
                TestInlineQueryResultVideoBase.mime_type,
                TestInlineQueryResultVideoBase.thumbnail_url,
                TestInlineQueryResultVideoBase.title,
                video_width=TestInlineQueryResultVideoBase.video_width,
                video_height=TestInlineQueryResultVideoBase.video_height,
                video_duration=TestInlineQueryResultVideoBase.video_duration,
                caption=TestInlineQueryResultVideoBase.caption,
                parse_mode=TestInlineQueryResultVideoBase.parse_mode,
                caption_entities=TestInlineQueryResultVideoBase.caption_entities,
                description=TestInlineQueryResultVideoBase.description,
                input_message_content=TestInlineQueryResultVideoBase.input_message_content,
                reply_markup=TestInlineQueryResultVideoBase.reply_markup,
                thumb_url="some other url",
            )

    def test_to_dict(self, inline_query_result_video):
        inline_query_result_video_dict = inline_query_result_video.to_dict()

        assert isinstance(inline_query_result_video_dict, dict)
        assert inline_query_result_video_dict["type"] == inline_query_result_video.type
        assert inline_query_result_video_dict["id"] == inline_query_result_video.id
        assert inline_query_result_video_dict["video_url"] == inline_query_result_video.video_url
        assert inline_query_result_video_dict["mime_type"] == inline_query_result_video.mime_type
        assert (
            inline_query_result_video_dict["video_width"] == inline_query_result_video.video_width
        )
        assert (
            inline_query_result_video_dict["video_height"]
            == inline_query_result_video.video_height
        )
        assert (
            inline_query_result_video_dict["video_duration"]
            == inline_query_result_video.video_duration
        )
        assert (
            inline_query_result_video_dict["thumbnail_url"]
            == inline_query_result_video.thumbnail_url
        )
        assert inline_query_result_video_dict["title"] == inline_query_result_video.title
        assert (
            inline_query_result_video_dict["description"] == inline_query_result_video.description
        )
        assert inline_query_result_video_dict["caption"] == inline_query_result_video.caption
        assert inline_query_result_video_dict["parse_mode"] == inline_query_result_video.parse_mode
        assert inline_query_result_video_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_video.caption_entities
        ]
        assert (
            inline_query_result_video_dict["input_message_content"]
            == inline_query_result_video.input_message_content.to_dict()
        )
        assert (
            inline_query_result_video_dict["reply_markup"]
            == inline_query_result_video.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultVideo(
            self.id_, self.video_url, self.mime_type, self.thumbnail_url, self.title
        )
        b = InlineQueryResultVideo(
            self.id_, self.video_url, self.mime_type, self.thumbnail_url, self.title
        )
        c = InlineQueryResultVideo(self.id_, "", self.mime_type, self.thumbnail_url, self.title)
        d = InlineQueryResultVideo(
            "", self.video_url, self.mime_type, self.thumbnail_url, self.title
        )
        e = InlineQueryResultVoice(self.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
