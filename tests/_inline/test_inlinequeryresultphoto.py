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
    InlineQueryResultPhoto,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)
from tests.auxil.deprecations import check_thumb_deprecation_warnings_for_args_and_attrs
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_photo():
    return InlineQueryResultPhoto(
        TestInlineQueryResultPhotoBase.id_,
        TestInlineQueryResultPhotoBase.photo_url,
        TestInlineQueryResultPhotoBase.thumbnail_url,
        photo_width=TestInlineQueryResultPhotoBase.photo_width,
        photo_height=TestInlineQueryResultPhotoBase.photo_height,
        title=TestInlineQueryResultPhotoBase.title,
        description=TestInlineQueryResultPhotoBase.description,
        caption=TestInlineQueryResultPhotoBase.caption,
        parse_mode=TestInlineQueryResultPhotoBase.parse_mode,
        caption_entities=TestInlineQueryResultPhotoBase.caption_entities,
        input_message_content=TestInlineQueryResultPhotoBase.input_message_content,
        reply_markup=TestInlineQueryResultPhotoBase.reply_markup,
    )


class TestInlineQueryResultPhotoBase:
    id_ = "id"
    type_ = "photo"
    photo_url = "photo url"
    photo_width = 10
    photo_height = 15
    thumbnail_url = "thumb url"
    title = "title"
    description = "description"
    caption = "caption"
    parse_mode = "HTML"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]

    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultPhotoWithoutRequest(TestInlineQueryResultPhotoBase):
    def test_slot_behaviour(self, inline_query_result_photo):
        inst = inline_query_result_photo
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_photo):
        assert inline_query_result_photo.type == self.type_
        assert inline_query_result_photo.id == self.id_
        assert inline_query_result_photo.photo_url == self.photo_url
        assert inline_query_result_photo.photo_width == self.photo_width
        assert inline_query_result_photo.photo_height == self.photo_height
        assert inline_query_result_photo.thumbnail_url == self.thumbnail_url
        assert inline_query_result_photo.title == self.title
        assert inline_query_result_photo.description == self.description
        assert inline_query_result_photo.caption == self.caption
        assert inline_query_result_photo.parse_mode == self.parse_mode
        assert inline_query_result_photo.caption_entities == tuple(self.caption_entities)
        assert (
            inline_query_result_photo.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_photo.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_caption_entities_always_tuple(self):
        result = InlineQueryResultPhoto(self.id_, self.photo_url, self.thumbnail_url)
        assert result.caption_entities == ()

    def test_thumb_url_property_deprecation_warning(self, recwarn):
        inline_query_result_photo = InlineQueryResultPhoto(
            TestInlineQueryResultPhotoBase.id_,
            TestInlineQueryResultPhotoBase.photo_url,
            TestInlineQueryResultPhotoBase.thumbnail_url,
            photo_width=TestInlineQueryResultPhotoBase.photo_width,
            photo_height=TestInlineQueryResultPhotoBase.photo_height,
            title=TestInlineQueryResultPhotoBase.title,
            description=TestInlineQueryResultPhotoBase.description,
            caption=TestInlineQueryResultPhotoBase.caption,
            parse_mode=TestInlineQueryResultPhotoBase.parse_mode,
            caption_entities=TestInlineQueryResultPhotoBase.caption_entities,
            input_message_content=TestInlineQueryResultPhotoBase.input_message_content,
            reply_markup=TestInlineQueryResultPhotoBase.reply_markup,
            thumb_url=TestInlineQueryResultPhotoBase.thumbnail_url,  # deprecated arg
        )
        assert inline_query_result_photo.thumb_url == inline_query_result_photo.thumbnail_url
        check_thumb_deprecation_warnings_for_args_and_attrs(
            recwarn,
            __file__,
            deprecated_name="thumb_url",
            new_name="thumbnail_url",
        )

    def test_thumb_url_issues_warning_and_works_without_positional_arg(self, recwarn):
        inline_query_result_photo = InlineQueryResultPhoto(
            TestInlineQueryResultPhotoBase.id_,
            TestInlineQueryResultPhotoBase.photo_url,
            # positional argument thumbnail_url should be here, but it's not
            photo_width=TestInlineQueryResultPhotoBase.photo_width,
            photo_height=TestInlineQueryResultPhotoBase.photo_height,
            title=TestInlineQueryResultPhotoBase.title,
            description=TestInlineQueryResultPhotoBase.description,
            caption=TestInlineQueryResultPhotoBase.caption,
            parse_mode=TestInlineQueryResultPhotoBase.parse_mode,
            caption_entities=TestInlineQueryResultPhotoBase.caption_entities,
            input_message_content=TestInlineQueryResultPhotoBase.input_message_content,
            reply_markup=TestInlineQueryResultPhotoBase.reply_markup,
            thumb_url=TestInlineQueryResultPhotoBase.thumbnail_url,  # deprecated arg
        )
        assert inline_query_result_photo.thumb_url == inline_query_result_photo.thumbnail_url
        check_thumb_deprecation_warnings_for_args_and_attrs(
            recwarn,
            __file__,
            deprecated_name="thumb_url",
            new_name="thumbnail_url",
        )

    def test_init_throws_error_without_thumbnail_url_and_thumb_url(self, recwarn):
        with pytest.raises(ValueError, match="You must pass either"):
            InlineQueryResultPhoto(
                TestInlineQueryResultPhotoBase.id_,
                TestInlineQueryResultPhotoBase.photo_url,
                # no thumbnail_url or thumb_url
                photo_width=TestInlineQueryResultPhotoBase.photo_width,
                photo_height=TestInlineQueryResultPhotoBase.photo_height,
                title=TestInlineQueryResultPhotoBase.title,
                description=TestInlineQueryResultPhotoBase.description,
                caption=TestInlineQueryResultPhotoBase.caption,
                parse_mode=TestInlineQueryResultPhotoBase.parse_mode,
                caption_entities=TestInlineQueryResultPhotoBase.caption_entities,
                input_message_content=TestInlineQueryResultPhotoBase.input_message_content,
                reply_markup=TestInlineQueryResultPhotoBase.reply_markup,
            )

    def test_throws_value_error_with_different_deprecated_and_new_arg_thumb_url(self):
        with pytest.raises(
            ValueError,
            match="different entities as 'thumb_url' and 'thumbnail_url'",
        ):
            InlineQueryResultPhoto(
                TestInlineQueryResultPhotoBase.id_,
                TestInlineQueryResultPhotoBase.photo_url,
                TestInlineQueryResultPhotoBase.thumbnail_url,
                photo_width=TestInlineQueryResultPhotoBase.photo_width,
                photo_height=TestInlineQueryResultPhotoBase.photo_height,
                title=TestInlineQueryResultPhotoBase.title,
                description=TestInlineQueryResultPhotoBase.description,
                caption=TestInlineQueryResultPhotoBase.caption,
                parse_mode=TestInlineQueryResultPhotoBase.parse_mode,
                caption_entities=TestInlineQueryResultPhotoBase.caption_entities,
                input_message_content=TestInlineQueryResultPhotoBase.input_message_content,
                reply_markup=TestInlineQueryResultPhotoBase.reply_markup,
                thumb_url="some other url",
            )

    def test_to_dict(self, inline_query_result_photo):
        inline_query_result_photo_dict = inline_query_result_photo.to_dict()

        assert isinstance(inline_query_result_photo_dict, dict)
        assert inline_query_result_photo_dict["type"] == inline_query_result_photo.type
        assert inline_query_result_photo_dict["id"] == inline_query_result_photo.id
        assert inline_query_result_photo_dict["photo_url"] == inline_query_result_photo.photo_url
        assert (
            inline_query_result_photo_dict["photo_width"] == inline_query_result_photo.photo_width
        )
        assert (
            inline_query_result_photo_dict["photo_height"]
            == inline_query_result_photo.photo_height
        )
        assert (
            inline_query_result_photo_dict["thumbnail_url"]
            == inline_query_result_photo.thumbnail_url
        )
        assert inline_query_result_photo_dict["title"] == inline_query_result_photo.title
        assert (
            inline_query_result_photo_dict["description"] == inline_query_result_photo.description
        )
        assert inline_query_result_photo_dict["caption"] == inline_query_result_photo.caption
        assert inline_query_result_photo_dict["parse_mode"] == inline_query_result_photo.parse_mode
        assert inline_query_result_photo_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_photo.caption_entities
        ]
        assert (
            inline_query_result_photo_dict["input_message_content"]
            == inline_query_result_photo.input_message_content.to_dict()
        )
        assert (
            inline_query_result_photo_dict["reply_markup"]
            == inline_query_result_photo.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultPhoto(self.id_, self.photo_url, self.thumbnail_url)
        b = InlineQueryResultPhoto(self.id_, self.photo_url, self.thumbnail_url)
        c = InlineQueryResultPhoto(self.id_, "", self.thumbnail_url)
        d = InlineQueryResultPhoto("", self.photo_url, self.thumbnail_url)
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
