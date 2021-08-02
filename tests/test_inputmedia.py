#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
from pathlib import Path

import pytest
from flaky import flaky

from telegram import (
    InputMediaVideo,
    InputMediaPhoto,
    InputMediaAnimation,
    Message,
    InputFile,
    InputMediaAudio,
    InputMediaDocument,
    MessageEntity,
    ParseMode,
)

# noinspection PyUnresolvedReferences
from telegram.error import BadRequest
from .test_animation import animation, animation_file  # noqa: F401

# noinspection PyUnresolvedReferences
from .test_audio import audio, audio_file  # noqa: F401

# noinspection PyUnresolvedReferences
from .test_document import document, document_file  # noqa: F401

# noinspection PyUnresolvedReferences
from .test_photo import _photo, photo_file, photo, thumb  # noqa: F401

# noinspection PyUnresolvedReferences
from .test_video import video, video_file  # noqa: F401
from tests.conftest import expect_bad_request


@pytest.fixture(scope='class')
def input_media_video(class_thumb_file):
    return InputMediaVideo(
        media=TestInputMediaVideo.media,
        caption=TestInputMediaVideo.caption,
        width=TestInputMediaVideo.width,
        height=TestInputMediaVideo.height,
        duration=TestInputMediaVideo.duration,
        parse_mode=TestInputMediaVideo.parse_mode,
        caption_entities=TestInputMediaVideo.caption_entities,
        thumb=class_thumb_file,
        supports_streaming=TestInputMediaVideo.supports_streaming,
    )


@pytest.fixture(scope='class')
def input_media_photo(class_thumb_file):
    return InputMediaPhoto(
        media=TestInputMediaPhoto.media,
        caption=TestInputMediaPhoto.caption,
        parse_mode=TestInputMediaPhoto.parse_mode,
        caption_entities=TestInputMediaPhoto.caption_entities,
    )


@pytest.fixture(scope='class')
def input_media_animation(class_thumb_file):
    return InputMediaAnimation(
        media=TestInputMediaAnimation.media,
        caption=TestInputMediaAnimation.caption,
        parse_mode=TestInputMediaAnimation.parse_mode,
        caption_entities=TestInputMediaAnimation.caption_entities,
        width=TestInputMediaAnimation.width,
        height=TestInputMediaAnimation.height,
        thumb=class_thumb_file,
        duration=TestInputMediaAnimation.duration,
    )


@pytest.fixture(scope='class')
def input_media_audio(class_thumb_file):
    return InputMediaAudio(
        media=TestInputMediaAudio.media,
        caption=TestInputMediaAudio.caption,
        duration=TestInputMediaAudio.duration,
        performer=TestInputMediaAudio.performer,
        title=TestInputMediaAudio.title,
        thumb=class_thumb_file,
        parse_mode=TestInputMediaAudio.parse_mode,
        caption_entities=TestInputMediaAudio.caption_entities,
    )


@pytest.fixture(scope='class')
def input_media_document(class_thumb_file):
    return InputMediaDocument(
        media=TestInputMediaDocument.media,
        caption=TestInputMediaDocument.caption,
        thumb=class_thumb_file,
        parse_mode=TestInputMediaDocument.parse_mode,
        caption_entities=TestInputMediaDocument.caption_entities,
        disable_content_type_detection=TestInputMediaDocument.disable_content_type_detection,
    )


class TestInputMediaVideo:
    type_ = "video"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    width = 3
    height = 4
    duration = 5
    parse_mode = 'HTML'
    supports_streaming = True
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]

    def test_slot_behaviour(self, input_media_video, recwarn, mro_slots):
        inst = input_media_video
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.type = 'should give warning', self.type_
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_expected_values(self, input_media_video):
        assert input_media_video.type == self.type_
        assert input_media_video.media == self.media
        assert input_media_video.caption == self.caption
        assert input_media_video.width == self.width
        assert input_media_video.height == self.height
        assert input_media_video.duration == self.duration
        assert input_media_video.parse_mode == self.parse_mode
        assert input_media_video.caption_entities == self.caption_entities
        assert input_media_video.supports_streaming == self.supports_streaming
        assert isinstance(input_media_video.thumb, InputFile)

    def test_to_dict(self, input_media_video):
        input_media_video_dict = input_media_video.to_dict()
        assert input_media_video_dict['type'] == input_media_video.type
        assert input_media_video_dict['media'] == input_media_video.media
        assert input_media_video_dict['caption'] == input_media_video.caption
        assert input_media_video_dict['width'] == input_media_video.width
        assert input_media_video_dict['height'] == input_media_video.height
        assert input_media_video_dict['duration'] == input_media_video.duration
        assert input_media_video_dict['parse_mode'] == input_media_video.parse_mode
        assert input_media_video_dict['caption_entities'] == [
            ce.to_dict() for ce in input_media_video.caption_entities
        ]
        assert input_media_video_dict['supports_streaming'] == input_media_video.supports_streaming

    def test_with_video(self, video):  # noqa: F811
        # fixture found in test_video
        input_media_video = InputMediaVideo(video, caption="test 3")
        assert input_media_video.type == self.type_
        assert input_media_video.media == video.file_id
        assert input_media_video.width == video.width
        assert input_media_video.height == video.height
        assert input_media_video.duration == video.duration
        assert input_media_video.caption == "test 3"

    def test_with_video_file(self, video_file):  # noqa: F811
        # fixture found in test_video
        input_media_video = InputMediaVideo(video_file, caption="test 3")
        assert input_media_video.type == self.type_
        assert isinstance(input_media_video.media, InputFile)
        assert input_media_video.caption == "test 3"

    def test_with_local_files(self):
        input_media_video = InputMediaVideo(
            'tests/data/telegram.mp4', thumb='tests/data/telegram.jpg'
        )
        assert input_media_video.media == (Path.cwd() / 'tests/data/telegram.mp4/').as_uri()
        assert input_media_video.thumb == (Path.cwd() / 'tests/data/telegram.jpg/').as_uri()


class TestInputMediaPhoto:
    type_ = "photo"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = 'Markdown'
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]

    def test_slot_behaviour(self, input_media_photo, recwarn, mro_slots):
        inst = input_media_photo
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.type = 'should give warning', self.type_
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_expected_values(self, input_media_photo):
        assert input_media_photo.type == self.type_
        assert input_media_photo.media == self.media
        assert input_media_photo.caption == self.caption
        assert input_media_photo.parse_mode == self.parse_mode
        assert input_media_photo.caption_entities == self.caption_entities

    def test_to_dict(self, input_media_photo):
        input_media_photo_dict = input_media_photo.to_dict()
        assert input_media_photo_dict['type'] == input_media_photo.type
        assert input_media_photo_dict['media'] == input_media_photo.media
        assert input_media_photo_dict['caption'] == input_media_photo.caption
        assert input_media_photo_dict['parse_mode'] == input_media_photo.parse_mode
        assert input_media_photo_dict['caption_entities'] == [
            ce.to_dict() for ce in input_media_photo.caption_entities
        ]

    def test_with_photo(self, photo):  # noqa: F811
        # fixture found in test_photo
        input_media_photo = InputMediaPhoto(photo, caption="test 2")
        assert input_media_photo.type == self.type_
        assert input_media_photo.media == photo.file_id
        assert input_media_photo.caption == "test 2"

    def test_with_photo_file(self, photo_file):  # noqa: F811
        # fixture found in test_photo
        input_media_photo = InputMediaPhoto(photo_file, caption="test 2")
        assert input_media_photo.type == self.type_
        assert isinstance(input_media_photo.media, InputFile)
        assert input_media_photo.caption == "test 2"

    def test_with_local_files(self):
        input_media_photo = InputMediaPhoto('tests/data/telegram.mp4')
        assert input_media_photo.media == (Path.cwd() / 'tests/data/telegram.mp4/').as_uri()


class TestInputMediaAnimation:
    type_ = "animation"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = 'Markdown'
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]
    width = 30
    height = 30
    duration = 1

    def test_slot_behaviour(self, input_media_animation, recwarn, mro_slots):
        inst = input_media_animation
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.type = 'should give warning', self.type_
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_expected_values(self, input_media_animation):
        assert input_media_animation.type == self.type_
        assert input_media_animation.media == self.media
        assert input_media_animation.caption == self.caption
        assert input_media_animation.parse_mode == self.parse_mode
        assert input_media_animation.caption_entities == self.caption_entities
        assert isinstance(input_media_animation.thumb, InputFile)

    def test_to_dict(self, input_media_animation):
        input_media_animation_dict = input_media_animation.to_dict()
        assert input_media_animation_dict['type'] == input_media_animation.type
        assert input_media_animation_dict['media'] == input_media_animation.media
        assert input_media_animation_dict['caption'] == input_media_animation.caption
        assert input_media_animation_dict['parse_mode'] == input_media_animation.parse_mode
        assert input_media_animation_dict['caption_entities'] == [
            ce.to_dict() for ce in input_media_animation.caption_entities
        ]
        assert input_media_animation_dict['width'] == input_media_animation.width
        assert input_media_animation_dict['height'] == input_media_animation.height
        assert input_media_animation_dict['duration'] == input_media_animation.duration

    def test_with_animation(self, animation):  # noqa: F811
        # fixture found in test_animation
        input_media_animation = InputMediaAnimation(animation, caption="test 2")
        assert input_media_animation.type == self.type_
        assert input_media_animation.media == animation.file_id
        assert input_media_animation.caption == "test 2"

    def test_with_animation_file(self, animation_file):  # noqa: F811
        # fixture found in test_animation
        input_media_animation = InputMediaAnimation(animation_file, caption="test 2")
        assert input_media_animation.type == self.type_
        assert isinstance(input_media_animation.media, InputFile)
        assert input_media_animation.caption == "test 2"

    def test_with_local_files(self):
        input_media_animation = InputMediaAnimation(
            'tests/data/telegram.mp4', thumb='tests/data/telegram.jpg'
        )
        assert input_media_animation.media == (Path.cwd() / 'tests/data/telegram.mp4').as_uri()
        assert input_media_animation.thumb == (Path.cwd() / 'tests/data/telegram.jpg').as_uri()


class TestInputMediaAudio:
    type_ = "audio"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    duration = 3
    performer = 'performer'
    title = 'title'
    parse_mode = 'HTML'
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]

    def test_slot_behaviour(self, input_media_audio, recwarn, mro_slots):
        inst = input_media_audio
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.type = 'should give warning', self.type_
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_expected_values(self, input_media_audio):
        assert input_media_audio.type == self.type_
        assert input_media_audio.media == self.media
        assert input_media_audio.caption == self.caption
        assert input_media_audio.duration == self.duration
        assert input_media_audio.performer == self.performer
        assert input_media_audio.title == self.title
        assert input_media_audio.parse_mode == self.parse_mode
        assert input_media_audio.caption_entities == self.caption_entities
        assert isinstance(input_media_audio.thumb, InputFile)

    def test_to_dict(self, input_media_audio):
        input_media_audio_dict = input_media_audio.to_dict()
        assert input_media_audio_dict['type'] == input_media_audio.type
        assert input_media_audio_dict['media'] == input_media_audio.media
        assert input_media_audio_dict['caption'] == input_media_audio.caption
        assert input_media_audio_dict['duration'] == input_media_audio.duration
        assert input_media_audio_dict['performer'] == input_media_audio.performer
        assert input_media_audio_dict['title'] == input_media_audio.title
        assert input_media_audio_dict['parse_mode'] == input_media_audio.parse_mode
        assert input_media_audio_dict['caption_entities'] == [
            ce.to_dict() for ce in input_media_audio.caption_entities
        ]

    def test_with_audio(self, audio):  # noqa: F811
        # fixture found in test_audio
        input_media_audio = InputMediaAudio(audio, caption="test 3")
        assert input_media_audio.type == self.type_
        assert input_media_audio.media == audio.file_id
        assert input_media_audio.duration == audio.duration
        assert input_media_audio.performer == audio.performer
        assert input_media_audio.title == audio.title
        assert input_media_audio.caption == "test 3"

    def test_with_audio_file(self, audio_file):  # noqa: F811
        # fixture found in test_audio
        input_media_audio = InputMediaAudio(audio_file, caption="test 3")
        assert input_media_audio.type == self.type_
        assert isinstance(input_media_audio.media, InputFile)
        assert input_media_audio.caption == "test 3"

    def test_with_local_files(self):
        input_media_audio = InputMediaAudio(
            'tests/data/telegram.mp4', thumb='tests/data/telegram.jpg'
        )
        assert input_media_audio.media == (Path.cwd() / 'tests/data/telegram.mp4/').as_uri()
        assert input_media_audio.thumb == (Path.cwd() / 'tests/data/telegram.jpg/').as_uri()


class TestInputMediaDocument:
    type_ = "document"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = 'HTML'
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]
    disable_content_type_detection = True

    def test_slot_behaviour(self, input_media_document, recwarn, mro_slots):
        inst = input_media_document
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.type = 'should give warning', self.type_
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_expected_values(self, input_media_document):
        assert input_media_document.type == self.type_
        assert input_media_document.media == self.media
        assert input_media_document.caption == self.caption
        assert input_media_document.parse_mode == self.parse_mode
        assert input_media_document.caption_entities == self.caption_entities
        assert (
            input_media_document.disable_content_type_detection
            == self.disable_content_type_detection
        )
        assert isinstance(input_media_document.thumb, InputFile)

    def test_to_dict(self, input_media_document):
        input_media_document_dict = input_media_document.to_dict()
        assert input_media_document_dict['type'] == input_media_document.type
        assert input_media_document_dict['media'] == input_media_document.media
        assert input_media_document_dict['caption'] == input_media_document.caption
        assert input_media_document_dict['parse_mode'] == input_media_document.parse_mode
        assert input_media_document_dict['caption_entities'] == [
            ce.to_dict() for ce in input_media_document.caption_entities
        ]
        assert (
            input_media_document['disable_content_type_detection']
            == input_media_document.disable_content_type_detection
        )

    def test_with_document(self, document):  # noqa: F811
        # fixture found in test_document
        input_media_document = InputMediaDocument(document, caption="test 3")
        assert input_media_document.type == self.type_
        assert input_media_document.media == document.file_id
        assert input_media_document.caption == "test 3"

    def test_with_document_file(self, document_file):  # noqa: F811
        # fixture found in test_document
        input_media_document = InputMediaDocument(document_file, caption="test 3")
        assert input_media_document.type == self.type_
        assert isinstance(input_media_document.media, InputFile)
        assert input_media_document.caption == "test 3"

    def test_with_local_files(self):
        input_media_document = InputMediaDocument(
            'tests/data/telegram.mp4', thumb='tests/data/telegram.jpg'
        )
        assert input_media_document.media == (Path.cwd() / 'tests/data/telegram.mp4').as_uri()
        assert input_media_document.thumb == (Path.cwd() / 'tests/data/telegram.jpg').as_uri()


@pytest.fixture(scope='function')  # noqa: F811
def media_group(photo, thumb):  # noqa: F811
    return [
        InputMediaPhoto(photo, caption='*photo* 1', parse_mode='Markdown'),
        InputMediaPhoto(thumb, caption='<b>photo</b> 2', parse_mode='HTML'),
        InputMediaPhoto(
            photo, caption='photo 3', caption_entities=[MessageEntity(MessageEntity.BOLD, 0, 5)]
        ),
    ]


class TestSendMediaGroup:
    @flaky(3, 1)
    def test_send_media_group_photo(self, bot, chat_id, media_group):
        messages = bot.send_media_group(chat_id, media_group)
        assert isinstance(messages, list)
        assert len(messages) == 3
        assert all(isinstance(mes, Message) for mes in messages)
        assert all(mes.media_group_id == messages[0].media_group_id for mes in messages)
        assert all(mes.caption == f'photo {idx+1}' for idx, mes in enumerate(messages))
        assert all(
            mes.caption_entities == [MessageEntity(MessageEntity.BOLD, 0, 5)] for mes in messages
        )

    @flaky(3, 1)
    def test_send_media_group_all_args(self, bot, chat_id, media_group):
        m1 = bot.send_message(chat_id, text="test")
        messages = bot.send_media_group(
            chat_id, media_group, disable_notification=True, reply_to_message_id=m1.message_id
        )
        assert isinstance(messages, list)
        assert len(messages) == 3
        assert all(isinstance(mes, Message) for mes in messages)
        assert all(mes.media_group_id == messages[0].media_group_id for mes in messages)
        assert all(mes.caption == f'photo {idx+1}' for idx, mes in enumerate(messages))
        assert all(
            mes.caption_entities == [MessageEntity(MessageEntity.BOLD, 0, 5)] for mes in messages
        )

    @flaky(3, 1)
    def test_send_media_group_custom_filename(
        self,
        bot,
        chat_id,
        photo_file,  # noqa: F811
        animation_file,  # noqa: F811
        audio_file,  # noqa: F811
        video_file,  # noqa: F811
        monkeypatch,
    ):
        def make_assertion(url, data, **kwargs):
            result = all(im.media.filename == 'custom_filename' for im in data['media'])
            # We are a bit hacky here b/c Bot.send_media_group expects a list of Message-dicts
            return [Message(0, None, None, text=result).to_dict()]

        monkeypatch.setattr(bot.request, 'post', make_assertion)

        media = [
            InputMediaAnimation(animation_file, filename='custom_filename'),
            InputMediaAudio(audio_file, filename='custom_filename'),
            InputMediaPhoto(photo_file, filename='custom_filename'),
            InputMediaVideo(video_file, filename='custom_filename'),
        ]

        assert bot.send_media_group(chat_id, media)[0].text is True

    def test_send_media_group_with_thumbs(
        self, bot, chat_id, video_file, photo_file, monkeypatch  # noqa: F811
    ):
        def test(*args, **kwargs):
            data = kwargs['fields']
            video_check = data[input_video.media.attach] == input_video.media.field_tuple
            thumb_check = data[input_video.thumb.attach] == input_video.thumb.field_tuple
            result = video_check and thumb_check
            raise Exception(f"Test was {'successful' if result else 'failing'}")

        monkeypatch.setattr('telegram.utils.request.Request._request_wrapper', test)
        input_video = InputMediaVideo(video_file, thumb=photo_file)
        with pytest.raises(Exception, match='Test was successful'):
            bot.send_media_group(chat_id, [input_video, input_video])

    @flaky(3, 1)  # noqa: F811
    def test_send_media_group_new_files(
        self, bot, chat_id, video_file, photo_file, animation_file  # noqa: F811
    ):  # noqa: F811
        def func():
            with open('tests/data/telegram.jpg', 'rb') as file:
                return bot.send_media_group(
                    chat_id,
                    [
                        InputMediaVideo(video_file),
                        InputMediaPhoto(photo_file),
                        InputMediaPhoto(file.read()),
                    ],
                )

        messages = expect_bad_request(
            func, 'Type of file mismatch', 'Telegram did not accept the file.'
        )

        assert isinstance(messages, list)
        assert len(messages) == 3
        assert all(isinstance(mes, Message) for mes in messages)
        assert all(mes.media_group_id == messages[0].media_group_id for mes in messages)

    @flaky(3, 1)
    @pytest.mark.parametrize(
        'default_bot,custom',
        [
            ({'allow_sending_without_reply': True}, None),
            ({'allow_sending_without_reply': False}, None),
            ({'allow_sending_without_reply': False}, True),
        ],
        indirect=['default_bot'],
    )
    def test_send_media_group_default_allow_sending_without_reply(
        self, default_bot, chat_id, media_group, custom
    ):
        reply_to_message = default_bot.send_message(chat_id, 'test')
        reply_to_message.delete()
        if custom is not None:
            messages = default_bot.send_media_group(
                chat_id,
                media_group,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert [m.reply_to_message is None for m in messages]
        elif default_bot.defaults.allow_sending_without_reply:
            messages = default_bot.send_media_group(
                chat_id, media_group, reply_to_message_id=reply_to_message.message_id
            )
            assert [m.reply_to_message is None for m in messages]
        else:
            with pytest.raises(BadRequest, match='message not found'):
                default_bot.send_media_group(
                    chat_id, media_group, reply_to_message_id=reply_to_message.message_id
                )

    @flaky(3, 1)
    def test_edit_message_media(self, bot, chat_id, media_group):
        messages = bot.send_media_group(chat_id, media_group)
        cid = messages[-1].chat.id
        mid = messages[-1].message_id
        new_message = bot.edit_message_media(chat_id=cid, message_id=mid, media=media_group[0])
        assert isinstance(new_message, Message)

    @flaky(3, 1)
    def test_edit_message_media_new_file(self, bot, chat_id, media_group, thumb_file):
        messages = bot.send_media_group(chat_id, media_group)
        cid = messages[-1].chat.id
        mid = messages[-1].message_id
        new_message = bot.edit_message_media(
            chat_id=cid, message_id=mid, media=InputMediaPhoto(thumb_file)
        )
        assert isinstance(new_message, Message)

    def test_edit_message_media_with_thumb(
        self, bot, chat_id, video_file, photo_file, monkeypatch  # noqa: F811
    ):
        def test(*args, **kwargs):
            data = kwargs['fields']
            video_check = data[input_video.media.attach] == input_video.media.field_tuple
            thumb_check = data[input_video.thumb.attach] == input_video.thumb.field_tuple
            result = video_check and thumb_check
            raise Exception(f"Test was {'successful' if result else 'failing'}")

        monkeypatch.setattr('telegram.utils.request.Request._request_wrapper', test)
        input_video = InputMediaVideo(video_file, thumb=photo_file)
        with pytest.raises(Exception, match='Test was successful'):
            bot.edit_message_media(chat_id=chat_id, message_id=123, media=input_video)

    @flaky(3, 1)
    @pytest.mark.parametrize(
        'default_bot', [{'parse_mode': ParseMode.HTML}], indirect=True, ids=['HTML-Bot']
    )
    @pytest.mark.parametrize('media_type', ['animation', 'document', 'audio', 'photo', 'video'])
    def test_edit_message_media_default_parse_mode(
        self,
        chat_id,
        default_bot,
        media_type,
        animation,  # noqa: F811
        document,  # noqa: F811
        audio,  # noqa: F811
        photo,  # noqa: F811
        video,  # noqa: F811
    ):
        html_caption = '<b>bold</b> <i>italic</i> <code>code</code>'
        markdown_caption = '*bold* _italic_ `code`'
        test_caption = 'bold italic code'
        test_entities = [
            MessageEntity(MessageEntity.BOLD, 0, 4),
            MessageEntity(MessageEntity.ITALIC, 5, 6),
            MessageEntity(MessageEntity.CODE, 12, 4),
        ]

        def build_media(parse_mode, med_type):
            kwargs = {}
            if parse_mode != ParseMode.HTML:
                kwargs['parse_mode'] = parse_mode
                kwargs['caption'] = markdown_caption
            else:
                kwargs['caption'] = html_caption

            if med_type == 'animation':
                return InputMediaAnimation(animation, **kwargs)
            if med_type == 'document':
                return InputMediaDocument(document, **kwargs)
            if med_type == 'audio':
                return InputMediaAudio(audio, **kwargs)
            if med_type == 'photo':
                return InputMediaPhoto(photo, **kwargs)
            if med_type == 'video':
                return InputMediaVideo(video, **kwargs)

        message = default_bot.send_photo(chat_id, photo)

        message = default_bot.edit_message_media(
            message.chat_id,
            message.message_id,
            media=build_media(parse_mode=ParseMode.HTML, med_type=media_type),
        )
        assert message.caption == test_caption
        assert message.caption_entities == test_entities

        # Remove caption to avoid "Message not changed"
        message.edit_caption()

        message = default_bot.edit_message_media(
            message.chat_id,
            message.message_id,
            media=build_media(parse_mode=ParseMode.MARKDOWN_V2, med_type=media_type),
        )
        assert message.caption == test_caption
        assert message.caption_entities == test_entities

        # Remove caption to avoid "Message not changed"
        message.edit_caption()

        message = default_bot.edit_message_media(
            message.chat_id,
            message.message_id,
            media=build_media(parse_mode=None, med_type=media_type),
        )
        assert message.caption == markdown_caption
        assert message.caption_entities == []
