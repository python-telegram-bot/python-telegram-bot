#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
    InlineQueryResultMpeg4Gif,
    InlineKeyboardButton,
    InlineQueryResultVoice,
    InlineKeyboardMarkup,
    InputTextMessageContent,
    MessageEntity,
)


@pytest.fixture(scope='class')
def inline_query_result_mpeg4_gif():
    return InlineQueryResultMpeg4Gif(
        TestInlineQueryResultMpeg4Gif.id_,
        TestInlineQueryResultMpeg4Gif.mpeg4_url,
        TestInlineQueryResultMpeg4Gif.thumb_url,
        mpeg4_width=TestInlineQueryResultMpeg4Gif.mpeg4_width,
        mpeg4_height=TestInlineQueryResultMpeg4Gif.mpeg4_height,
        mpeg4_duration=TestInlineQueryResultMpeg4Gif.mpeg4_duration,
        title=TestInlineQueryResultMpeg4Gif.title,
        caption=TestInlineQueryResultMpeg4Gif.caption,
        parse_mode=TestInlineQueryResultMpeg4Gif.parse_mode,
        caption_entities=TestInlineQueryResultMpeg4Gif.caption_entities,
        input_message_content=TestInlineQueryResultMpeg4Gif.input_message_content,
        reply_markup=TestInlineQueryResultMpeg4Gif.reply_markup,
        thumb_mime_type=TestInlineQueryResultMpeg4Gif.thumb_mime_type,
    )


class TestInlineQueryResultMpeg4Gif:
    id_ = 'id'
    type_ = 'mpeg4_gif'
    mpeg4_url = 'mpeg4 url'
    mpeg4_width = 10
    mpeg4_height = 15
    mpeg4_duration = 1
    thumb_url = 'thumb url'
    thumb_mime_type = 'image/jpeg'
    title = 'title'
    caption = 'caption'
    parse_mode = 'Markdown'
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('reply_markup')]])

    def test_slot_behaviour(self, inline_query_result_mpeg4_gif, recwarn, mro_slots):
        inst = inline_query_result_mpeg4_gif
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.id = 'should give warning', self.id_
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_expected_values(self, inline_query_result_mpeg4_gif):
        assert inline_query_result_mpeg4_gif.type == self.type_
        assert inline_query_result_mpeg4_gif.id == self.id_
        assert inline_query_result_mpeg4_gif.mpeg4_url == self.mpeg4_url
        assert inline_query_result_mpeg4_gif.mpeg4_width == self.mpeg4_width
        assert inline_query_result_mpeg4_gif.mpeg4_height == self.mpeg4_height
        assert inline_query_result_mpeg4_gif.mpeg4_duration == self.mpeg4_duration
        assert inline_query_result_mpeg4_gif.thumb_url == self.thumb_url
        assert inline_query_result_mpeg4_gif.thumb_mime_type == self.thumb_mime_type
        assert inline_query_result_mpeg4_gif.title == self.title
        assert inline_query_result_mpeg4_gif.caption == self.caption
        assert inline_query_result_mpeg4_gif.parse_mode == self.parse_mode
        assert inline_query_result_mpeg4_gif.caption_entities == self.caption_entities
        assert (
            inline_query_result_mpeg4_gif.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_mpeg4_gif.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_mpeg4_gif):
        inline_query_result_mpeg4_gif_dict = inline_query_result_mpeg4_gif.to_dict()

        assert isinstance(inline_query_result_mpeg4_gif_dict, dict)
        assert inline_query_result_mpeg4_gif_dict['type'] == inline_query_result_mpeg4_gif.type
        assert inline_query_result_mpeg4_gif_dict['id'] == inline_query_result_mpeg4_gif.id
        assert (
            inline_query_result_mpeg4_gif_dict['mpeg4_url']
            == inline_query_result_mpeg4_gif.mpeg4_url
        )
        assert (
            inline_query_result_mpeg4_gif_dict['mpeg4_width']
            == inline_query_result_mpeg4_gif.mpeg4_width
        )
        assert (
            inline_query_result_mpeg4_gif_dict['mpeg4_height']
            == inline_query_result_mpeg4_gif.mpeg4_height
        )
        assert (
            inline_query_result_mpeg4_gif_dict['mpeg4_duration']
            == inline_query_result_mpeg4_gif.mpeg4_duration
        )
        assert (
            inline_query_result_mpeg4_gif_dict['thumb_url']
            == inline_query_result_mpeg4_gif.thumb_url
        )
        assert (
            inline_query_result_mpeg4_gif_dict['thumb_mime_type']
            == inline_query_result_mpeg4_gif.thumb_mime_type
        )
        assert inline_query_result_mpeg4_gif_dict['title'] == inline_query_result_mpeg4_gif.title
        assert (
            inline_query_result_mpeg4_gif_dict['caption'] == inline_query_result_mpeg4_gif.caption
        )
        assert (
            inline_query_result_mpeg4_gif_dict['parse_mode']
            == inline_query_result_mpeg4_gif.parse_mode
        )
        assert inline_query_result_mpeg4_gif_dict['caption_entities'] == [
            ce.to_dict() for ce in inline_query_result_mpeg4_gif.caption_entities
        ]
        assert (
            inline_query_result_mpeg4_gif_dict['input_message_content']
            == inline_query_result_mpeg4_gif.input_message_content.to_dict()
        )
        assert (
            inline_query_result_mpeg4_gif_dict['reply_markup']
            == inline_query_result_mpeg4_gif.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultMpeg4Gif(self.id_, self.mpeg4_url, self.thumb_url)
        b = InlineQueryResultMpeg4Gif(self.id_, self.mpeg4_url, self.thumb_url)
        c = InlineQueryResultMpeg4Gif(self.id_, '', self.thumb_url)
        d = InlineQueryResultMpeg4Gif('', self.mpeg4_url, self.thumb_url)
        e = InlineQueryResultVoice(self.id_, '', '')

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
