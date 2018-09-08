#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
import pytest
from flaky import flaky

from telegram import (InputMediaVideo, InputMediaPhoto, InputMediaAnimation, Message, InputFile,
                      InputMediaAudio, InputMediaDocument)
# noinspection PyUnresolvedReferences
from .test_animation import animation, animation_file  # noqa: F401
# noinspection PyUnresolvedReferences
from .test_audio import audio, audio_file  # noqa: F401
# noinspection PyUnresolvedReferences
from .test_document import document, document_file  # noqa: F401
# noinspection PyUnresolvedReferences
from .test_photo import _photo, photo_file, photo, thumb  # noqa: F401
# noinspection PyUnresolvedReferences
from .test_video import video, video_file  # noqa: F401


@pytest.fixture(scope='class')
def input_media_video(class_thumb_file):
    return InputMediaVideo(media=TestInputMediaVideo.media,
                           caption=TestInputMediaVideo.caption,
                           width=TestInputMediaVideo.width,
                           height=TestInputMediaVideo.height,
                           duration=TestInputMediaVideo.duration,
                           parse_mode=TestInputMediaVideo.parse_mode,
                           thumb=class_thumb_file,
                           supports_streaming=TestInputMediaVideo.supports_streaming)


@pytest.fixture(scope='class')
def input_media_photo(class_thumb_file):
    return InputMediaPhoto(media=TestInputMediaPhoto.media,
                           caption=TestInputMediaPhoto.caption,
                           parse_mode=TestInputMediaPhoto.parse_mode)


@pytest.fixture(scope='class')
def input_media_animation(class_thumb_file):
    return InputMediaAnimation(media=TestInputMediaAnimation.media,
                               caption=TestInputMediaAnimation.caption,
                               parse_mode=TestInputMediaAnimation.parse_mode,
                               width=TestInputMediaAnimation.width,
                               height=TestInputMediaAnimation.height,
                               thumb=class_thumb_file,
                               duration=TestInputMediaAnimation.duration)


@pytest.fixture(scope='class')
def input_media_audio(class_thumb_file):
    return InputMediaAudio(media=TestInputMediaAudio.media,
                           caption=TestInputMediaAudio.caption,
                           duration=TestInputMediaAudio.duration,
                           performer=TestInputMediaAudio.performer,
                           title=TestInputMediaAudio.title,
                           thumb=class_thumb_file,
                           parse_mode=TestInputMediaAudio.parse_mode)


@pytest.fixture(scope='class')
def input_media_document(class_thumb_file):
    return InputMediaDocument(media=TestInputMediaDocument.media,
                              caption=TestInputMediaDocument.caption,
                              thumb=class_thumb_file,
                              parse_mode=TestInputMediaDocument.parse_mode)


class TestInputMediaVideo(object):
    type = "video"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    width = 3
    height = 4
    duration = 5
    parse_mode = 'HTML'
    supports_streaming = True

    def test_expected_values(self, input_media_video):
        assert input_media_video.type == self.type
        assert input_media_video.media == self.media
        assert input_media_video.caption == self.caption
        assert input_media_video.width == self.width
        assert input_media_video.height == self.height
        assert input_media_video.duration == self.duration
        assert input_media_video.parse_mode == self.parse_mode
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
        assert input_media_video_dict['supports_streaming'] == input_media_video.supports_streaming

    def test_with_video(self, video):  # noqa: F811
        # fixture found in test_video
        input_media_video = InputMediaVideo(video, caption="test 3")
        assert input_media_video.type == self.type
        assert input_media_video.media == video.file_id
        assert input_media_video.width == video.width
        assert input_media_video.height == video.height
        assert input_media_video.duration == video.duration
        assert input_media_video.caption == "test 3"

    def test_with_video_file(self, video_file):  # noqa: F811
        # fixture found in test_video
        input_media_video = InputMediaVideo(video_file, caption="test 3")
        assert input_media_video.type == self.type
        assert isinstance(input_media_video.media, InputFile)
        assert input_media_video.caption == "test 3"


class TestInputMediaPhoto(object):
    type = "photo"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = 'Markdown'

    def test_expected_values(self, input_media_photo):
        assert input_media_photo.type == self.type
        assert input_media_photo.media == self.media
        assert input_media_photo.caption == self.caption
        assert input_media_photo.parse_mode == self.parse_mode

    def test_to_dict(self, input_media_photo):
        input_media_photo_dict = input_media_photo.to_dict()
        assert input_media_photo_dict['type'] == input_media_photo.type
        assert input_media_photo_dict['media'] == input_media_photo.media
        assert input_media_photo_dict['caption'] == input_media_photo.caption
        assert input_media_photo_dict['parse_mode'] == input_media_photo.parse_mode

    def test_with_photo(self, photo):  # noqa: F811
        # fixture found in test_photo
        input_media_photo = InputMediaPhoto(photo, caption="test 2")
        assert input_media_photo.type == self.type
        assert input_media_photo.media == photo.file_id
        assert input_media_photo.caption == "test 2"

    def test_with_photo_file(self, photo_file):  # noqa: F811
        # fixture found in test_photo
        input_media_photo = InputMediaPhoto(photo_file, caption="test 2")
        assert input_media_photo.type == self.type
        assert isinstance(input_media_photo.media, InputFile)
        assert input_media_photo.caption == "test 2"


class TestInputMediaAnimation(object):
    type = "animation"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = 'Markdown'
    width = 30
    height = 30
    duration = 1

    def test_expected_values(self, input_media_animation):
        assert input_media_animation.type == self.type
        assert input_media_animation.media == self.media
        assert input_media_animation.caption == self.caption
        assert input_media_animation.parse_mode == self.parse_mode
        assert isinstance(input_media_animation.thumb, InputFile)

    def test_to_dict(self, input_media_animation):
        input_media_animation_dict = input_media_animation.to_dict()
        assert input_media_animation_dict['type'] == input_media_animation.type
        assert input_media_animation_dict['media'] == input_media_animation.media
        assert input_media_animation_dict['caption'] == input_media_animation.caption
        assert input_media_animation_dict['parse_mode'] == input_media_animation.parse_mode
        assert input_media_animation_dict['width'] == input_media_animation.width
        assert input_media_animation_dict['height'] == input_media_animation.height
        assert input_media_animation_dict['duration'] == input_media_animation.duration

    def test_with_animation(self, animation):  # noqa: F811
        # fixture found in test_animation
        input_media_animation = InputMediaAnimation(animation, caption="test 2")
        assert input_media_animation.type == self.type
        assert input_media_animation.media == animation.file_id
        assert input_media_animation.caption == "test 2"

    def test_with_animation_file(self, animation_file):  # noqa: F811
        # fixture found in test_animation
        input_media_animation = InputMediaAnimation(animation_file, caption="test 2")
        assert input_media_animation.type == self.type
        assert isinstance(input_media_animation.media, InputFile)
        assert input_media_animation.caption == "test 2"


class TestInputMediaAudio(object):
    type = "audio"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    duration = 3
    performer = 'performer'
    title = 'title'
    parse_mode = 'HTML'

    def test_expected_values(self, input_media_audio):
        assert input_media_audio.type == self.type
        assert input_media_audio.media == self.media
        assert input_media_audio.caption == self.caption
        assert input_media_audio.duration == self.duration
        assert input_media_audio.performer == self.performer
        assert input_media_audio.title == self.title
        assert input_media_audio.parse_mode == self.parse_mode
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

    def test_with_audio(self, audio):  # noqa: F811
        # fixture found in test_audio
        input_media_audio = InputMediaAudio(audio, caption="test 3")
        assert input_media_audio.type == self.type
        assert input_media_audio.media == audio.file_id
        assert input_media_audio.duration == audio.duration
        assert input_media_audio.performer == audio.performer
        assert input_media_audio.title == audio.title
        assert input_media_audio.caption == "test 3"

    def test_with_audio_file(self, audio_file):  # noqa: F811
        # fixture found in test_audio
        input_media_audio = InputMediaAudio(audio_file, caption="test 3")
        assert input_media_audio.type == self.type
        assert isinstance(input_media_audio.media, InputFile)
        assert input_media_audio.caption == "test 3"


class TestInputMediaDocument(object):
    type = "document"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = 'HTML'

    def test_expected_values(self, input_media_document):
        assert input_media_document.type == self.type
        assert input_media_document.media == self.media
        assert input_media_document.caption == self.caption
        assert input_media_document.parse_mode == self.parse_mode
        assert isinstance(input_media_document.thumb, InputFile)

    def test_to_dict(self, input_media_document):
        input_media_document_dict = input_media_document.to_dict()
        assert input_media_document_dict['type'] == input_media_document.type
        assert input_media_document_dict['media'] == input_media_document.media
        assert input_media_document_dict['caption'] == input_media_document.caption
        assert input_media_document_dict['parse_mode'] == input_media_document.parse_mode

    def test_with_document(self, document):  # noqa: F811
        # fixture found in test_document
        input_media_document = InputMediaDocument(document, caption="test 3")
        assert input_media_document.type == self.type
        assert input_media_document.media == document.file_id
        assert input_media_document.caption == "test 3"

    def test_with_document_file(self, document_file):  # noqa: F811
        # fixture found in test_document
        input_media_document = InputMediaDocument(document_file, caption="test 3")
        assert input_media_document.type == self.type
        assert isinstance(input_media_document.media, InputFile)
        assert input_media_document.caption == "test 3"


@pytest.fixture(scope='function')  # noqa: F811
def media_group(photo, thumb):
    return [InputMediaPhoto(photo, caption='photo `1`', parse_mode='Markdown'),
            InputMediaPhoto(thumb, caption='<b>photo</b> 2', parse_mode='HTML')]


class TestSendMediaGroup(object):
    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_media_group_photo(self, bot, chat_id, media_group):
        messages = bot.send_media_group(chat_id, media_group)
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert all([isinstance(mes, Message) for mes in messages])
        assert all([mes.media_group_id == messages[0].media_group_id for mes in messages])

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_media_group_all_args(self, bot, chat_id, media_group):
        m1 = bot.send_message(chat_id, text="test")
        messages = bot.send_media_group(chat_id, media_group, disable_notification=True,
                                        reply_to_message_id=m1.message_id)
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert all([isinstance(mes, Message) for mes in messages])
        assert all([mes.media_group_id == messages[0].media_group_id for mes in messages])

    @flaky(3, 1)  # noqa: F811
    @pytest.mark.timeout(10)  # noqa: F811
    def test_send_media_group_new_files(self, bot, chat_id, video_file, photo_file,  # noqa: F811
                                        animation_file):  # noqa: F811
        messages = bot.send_media_group(chat_id, [
            InputMediaVideo(video_file),
            InputMediaPhoto(photo_file)
        ])
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert all([isinstance(mes, Message) for mes in messages])
        assert all([mes.media_group_id == messages[0].media_group_id for mes in messages])

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_edit_message_media(self, bot, chat_id, media_group):
        messages = bot.send_media_group(chat_id, media_group)
        cid = messages[-1].chat.id
        mid = messages[-1].message_id
        new_message = bot.edit_message_media(chat_id=cid, message_id=mid, media=media_group[0])
        assert isinstance(new_message, Message)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_edit_message_media_new_file(self, bot, chat_id, media_group, thumb_file):
        messages = bot.send_media_group(chat_id, media_group)
        cid = messages[-1].chat.id
        mid = messages[-1].message_id
        new_message = bot.edit_message_media(chat_id=cid, message_id=mid,
                                             media=InputMediaPhoto(thumb_file))
        assert isinstance(new_message, Message)
