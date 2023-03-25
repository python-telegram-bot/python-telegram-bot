#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
import asyncio
import copy
from collections.abc import Sequence

import pytest

from telegram import (
    InputFile,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    MessageEntity,
)
from telegram.constants import ParseMode

# noinspection PyUnresolvedReferences
from telegram.error import BadRequest
from telegram.request import RequestData
from tests._files.test_animation import animation, animation_file  # noqa: F401
from tests.auxil.files import data_file
from tests.auxil.networking import expect_bad_request
from tests.auxil.slots import mro_slots

# noinspection PyUnresolvedReferences
from tests.test_forum import emoji_id, real_topic  # noqa: F401

from ..auxil.deprecations import check_thumb_deprecation_warnings_for_args_and_attrs

# noinspection PyUnresolvedReferences
from .test_audio import audio, audio_file  # noqa: F401

# noinspection PyUnresolvedReferences
from .test_document import document, document_file  # noqa: F401

# noinspection PyUnresolvedReferences
from .test_photo import photo, photo_file, photolist, thumb  # noqa: F401

# noinspection PyUnresolvedReferences
from .test_video import video, video_file  # noqa: F401


@pytest.fixture(scope="module")
def input_media_video(class_thumb_file):
    return InputMediaVideo(
        media=TestInputMediaVideoBase.media,
        caption=TestInputMediaVideoBase.caption,
        width=TestInputMediaVideoBase.width,
        height=TestInputMediaVideoBase.height,
        duration=TestInputMediaVideoBase.duration,
        parse_mode=TestInputMediaVideoBase.parse_mode,
        caption_entities=TestInputMediaVideoBase.caption_entities,
        thumbnail=class_thumb_file,
        supports_streaming=TestInputMediaVideoBase.supports_streaming,
        has_spoiler=TestInputMediaVideoBase.has_spoiler,
    )


@pytest.fixture(scope="module")
def input_media_photo():
    return InputMediaPhoto(
        media=TestInputMediaPhotoBase.media,
        caption=TestInputMediaPhotoBase.caption,
        parse_mode=TestInputMediaPhotoBase.parse_mode,
        caption_entities=TestInputMediaPhotoBase.caption_entities,
        has_spoiler=TestInputMediaPhotoBase.has_spoiler,
    )


@pytest.fixture(scope="module")
def input_media_animation(class_thumb_file):
    return InputMediaAnimation(
        media=TestInputMediaAnimationBase.media,
        caption=TestInputMediaAnimationBase.caption,
        parse_mode=TestInputMediaAnimationBase.parse_mode,
        caption_entities=TestInputMediaAnimationBase.caption_entities,
        width=TestInputMediaAnimationBase.width,
        height=TestInputMediaAnimationBase.height,
        thumbnail=class_thumb_file,
        duration=TestInputMediaAnimationBase.duration,
        has_spoiler=TestInputMediaAnimationBase.has_spoiler,
    )


@pytest.fixture(scope="module")
def input_media_audio(class_thumb_file):
    return InputMediaAudio(
        media=TestInputMediaAudioBase.media,
        caption=TestInputMediaAudioBase.caption,
        duration=TestInputMediaAudioBase.duration,
        performer=TestInputMediaAudioBase.performer,
        title=TestInputMediaAudioBase.title,
        thumbnail=class_thumb_file,
        parse_mode=TestInputMediaAudioBase.parse_mode,
        caption_entities=TestInputMediaAudioBase.caption_entities,
    )


@pytest.fixture(scope="module")
def input_media_document(class_thumb_file):
    return InputMediaDocument(
        media=TestInputMediaDocumentBase.media,
        caption=TestInputMediaDocumentBase.caption,
        thumbnail=class_thumb_file,
        parse_mode=TestInputMediaDocumentBase.parse_mode,
        caption_entities=TestInputMediaDocumentBase.caption_entities,
        disable_content_type_detection=TestInputMediaDocumentBase.disable_content_type_detection,
    )


class TestInputMediaVideoBase:
    type_ = "video"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    width = 3
    height = 4
    duration = 5
    parse_mode = "HTML"
    supports_streaming = True
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]
    has_spoiler = True


class TestInputMediaVideoWithoutRequest(TestInputMediaVideoBase):
    def test_slot_behaviour(self, input_media_video):
        inst = input_media_video
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_media_video):
        assert input_media_video.type == self.type_
        assert input_media_video.media == self.media
        assert input_media_video.caption == self.caption
        assert input_media_video.width == self.width
        assert input_media_video.height == self.height
        assert input_media_video.duration == self.duration
        assert input_media_video.parse_mode == self.parse_mode
        assert input_media_video.caption_entities == tuple(self.caption_entities)
        assert input_media_video.supports_streaming == self.supports_streaming
        assert isinstance(input_media_video.thumbnail, InputFile)
        assert input_media_video.thumb is input_media_video.thumbnail
        assert input_media_video.has_spoiler == self.has_spoiler

    def test_thumb_property_deprecation_warning(self, recwarn):
        input_media_video = InputMediaVideo(self.media, thumb=object())
        assert input_media_video.thumb is input_media_video.thumbnail
        check_thumb_deprecation_warnings_for_args_and_attrs(recwarn, __file__)

    def test_caption_entities_always_tuple(self):
        input_media_video = InputMediaVideo(self.media)
        assert input_media_video.caption_entities == ()

    def test_to_dict(self, input_media_video):
        input_media_video_dict = input_media_video.to_dict()
        assert input_media_video_dict["type"] == input_media_video.type
        assert input_media_video_dict["media"] == input_media_video.media
        assert input_media_video_dict["caption"] == input_media_video.caption
        assert input_media_video_dict["width"] == input_media_video.width
        assert input_media_video_dict["height"] == input_media_video.height
        assert input_media_video_dict["duration"] == input_media_video.duration
        assert input_media_video_dict["parse_mode"] == input_media_video.parse_mode
        assert input_media_video_dict["caption_entities"] == [
            ce.to_dict() for ce in input_media_video.caption_entities
        ]
        assert input_media_video_dict["supports_streaming"] == input_media_video.supports_streaming
        assert input_media_video_dict["has_spoiler"] == input_media_video.has_spoiler

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
            data_file("telegram.mp4"), thumbnail=data_file("telegram.jpg")
        )
        assert input_media_video.media == data_file("telegram.mp4").as_uri()
        assert input_media_video.thumbnail == data_file("telegram.jpg").as_uri()

    def test_with_local_files_throws_exception_with_different_thumb_and_thumbnail(self):
        with pytest.raises(ValueError, match="You passed different entities as 'thumb' and "):
            InputMediaVideo(
                data_file("telegram.mp4"),
                thumbnail=data_file("telegram.jpg"),
                thumb=data_file("telegram_no_standard_header.jpg"),
            )


class TestInputMediaPhotoBase:
    type_ = "photo"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = "Markdown"
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]
    has_spoiler = True


class TestInputMediaPhotoWithoutRequest(TestInputMediaPhotoBase):
    def test_slot_behaviour(self, input_media_photo):
        inst = input_media_photo
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_media_photo):
        assert input_media_photo.type == self.type_
        assert input_media_photo.media == self.media
        assert input_media_photo.caption == self.caption
        assert input_media_photo.parse_mode == self.parse_mode
        assert input_media_photo.caption_entities == tuple(self.caption_entities)
        assert input_media_photo.has_spoiler == self.has_spoiler

    def test_caption_entities_always_tuple(self):
        input_media_photo = InputMediaPhoto(self.media)
        assert input_media_photo.caption_entities == ()

    def test_to_dict(self, input_media_photo):
        input_media_photo_dict = input_media_photo.to_dict()
        assert input_media_photo_dict["type"] == input_media_photo.type
        assert input_media_photo_dict["media"] == input_media_photo.media
        assert input_media_photo_dict["caption"] == input_media_photo.caption
        assert input_media_photo_dict["parse_mode"] == input_media_photo.parse_mode
        assert input_media_photo_dict["caption_entities"] == [
            ce.to_dict() for ce in input_media_photo.caption_entities
        ]
        assert input_media_photo_dict["has_spoiler"] == input_media_photo.has_spoiler

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
        input_media_photo = InputMediaPhoto(data_file("telegram.mp4"))
        assert input_media_photo.media == data_file("telegram.mp4").as_uri()


class TestInputMediaAnimationBase:
    type_ = "animation"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = "Markdown"
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]
    width = 30
    height = 30
    duration = 1
    has_spoiler = True


class TestInputMediaAnimationWithoutRequest(TestInputMediaAnimationBase):
    def test_slot_behaviour(self, input_media_animation):
        inst = input_media_animation
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_media_animation):
        assert input_media_animation.type == self.type_
        assert input_media_animation.media == self.media
        assert input_media_animation.caption == self.caption
        assert input_media_animation.parse_mode == self.parse_mode
        assert input_media_animation.caption_entities == tuple(self.caption_entities)
        assert isinstance(input_media_animation.thumbnail, InputFile)
        assert input_media_animation.thumb is input_media_animation.thumbnail
        assert input_media_animation.has_spoiler == self.has_spoiler

    def test_thumb_property_deprecation_warning(self, recwarn):
        input_media_animation = InputMediaAnimation(self.media, thumb=object())
        assert input_media_animation.thumb is input_media_animation.thumbnail
        check_thumb_deprecation_warnings_for_args_and_attrs(recwarn, __file__)

    def test_caption_entities_always_tuple(self):
        input_media_animation = InputMediaAnimation(self.media)
        assert input_media_animation.caption_entities == ()

    def test_to_dict(self, input_media_animation):
        input_media_animation_dict = input_media_animation.to_dict()
        assert input_media_animation_dict["type"] == input_media_animation.type
        assert input_media_animation_dict["media"] == input_media_animation.media
        assert input_media_animation_dict["caption"] == input_media_animation.caption
        assert input_media_animation_dict["parse_mode"] == input_media_animation.parse_mode
        assert input_media_animation_dict["caption_entities"] == [
            ce.to_dict() for ce in input_media_animation.caption_entities
        ]
        assert input_media_animation_dict["width"] == input_media_animation.width
        assert input_media_animation_dict["height"] == input_media_animation.height
        assert input_media_animation_dict["duration"] == input_media_animation.duration
        assert input_media_animation_dict["has_spoiler"] == input_media_animation.has_spoiler

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
            data_file("telegram.mp4"), thumbnail=data_file("telegram.jpg")
        )
        assert input_media_animation.media == data_file("telegram.mp4").as_uri()
        assert input_media_animation.thumbnail == data_file("telegram.jpg").as_uri()

    def test_with_local_files_throws_exception_with_different_thumb_and_thumbnail(self):
        with pytest.raises(ValueError, match="You passed different entities as 'thumb' and "):
            InputMediaAnimation(
                data_file("telegram.mp4"),
                thumbnail=data_file("telegram.jpg"),
                thumb=data_file("telegram_no_standard_header.jpg"),
            )


class TestInputMediaAudioBase:
    type_ = "audio"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    duration = 3
    performer = "performer"
    title = "title"
    parse_mode = "HTML"
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]


class TestInputMediaAudioWithoutRequest(TestInputMediaAudioBase):
    def test_slot_behaviour(self, input_media_audio):
        inst = input_media_audio
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_media_audio):
        assert input_media_audio.type == self.type_
        assert input_media_audio.media == self.media
        assert input_media_audio.caption == self.caption
        assert input_media_audio.duration == self.duration
        assert input_media_audio.performer == self.performer
        assert input_media_audio.title == self.title
        assert input_media_audio.parse_mode == self.parse_mode
        assert input_media_audio.caption_entities == tuple(self.caption_entities)
        assert isinstance(input_media_audio.thumbnail, InputFile)
        assert input_media_audio.thumb is input_media_audio.thumbnail

    def test_thumb_property_deprecation_warning(self, recwarn):
        input_media_audio = InputMediaAudio(self.media, thumb=object())
        assert input_media_audio.thumb is input_media_audio.thumbnail
        check_thumb_deprecation_warnings_for_args_and_attrs(recwarn, __file__)

    def test_caption_entities_always_tuple(self):
        input_media_audio = InputMediaAudio(self.media)
        assert input_media_audio.caption_entities == ()

    def test_to_dict(self, input_media_audio):
        input_media_audio_dict = input_media_audio.to_dict()
        assert input_media_audio_dict["type"] == input_media_audio.type
        assert input_media_audio_dict["media"] == input_media_audio.media
        assert input_media_audio_dict["caption"] == input_media_audio.caption
        assert input_media_audio_dict["duration"] == input_media_audio.duration
        assert input_media_audio_dict["performer"] == input_media_audio.performer
        assert input_media_audio_dict["title"] == input_media_audio.title
        assert input_media_audio_dict["parse_mode"] == input_media_audio.parse_mode
        assert input_media_audio_dict["caption_entities"] == [
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
            data_file("telegram.mp4"), thumbnail=data_file("telegram.jpg")
        )
        assert input_media_audio.media == data_file("telegram.mp4").as_uri()
        assert input_media_audio.thumbnail == data_file("telegram.jpg").as_uri()

    def test_with_local_files_throws_exception_with_different_thumb_and_thumbnail(self):
        with pytest.raises(ValueError, match="You passed different entities as 'thumb' and "):
            InputMediaAudio(
                data_file("telegram.mp4"),
                thumbnail=data_file("telegram.jpg"),
                thumb=data_file("telegram_no_standard_header.jpg"),
            )


class TestInputMediaDocumentBase:
    type_ = "document"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = "HTML"
    caption_entities = [MessageEntity(MessageEntity.BOLD, 0, 2)]
    disable_content_type_detection = True


class TestInputMediaDocumentWithoutRequest(TestInputMediaDocumentBase):
    def test_slot_behaviour(self, input_media_document):
        inst = input_media_document
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_media_document):
        assert input_media_document.type == self.type_
        assert input_media_document.media == self.media
        assert input_media_document.caption == self.caption
        assert input_media_document.parse_mode == self.parse_mode
        assert input_media_document.caption_entities == tuple(self.caption_entities)
        assert (
            input_media_document.disable_content_type_detection
            == self.disable_content_type_detection
        )
        assert isinstance(input_media_document.thumbnail, InputFile)
        assert input_media_document.thumb is input_media_document.thumbnail

    def test_thumb_property_deprecation_warning(self, recwarn):
        input_media_document = InputMediaDocument(self.media, thumb=object())
        assert input_media_document.thumb is input_media_document.thumbnail
        check_thumb_deprecation_warnings_for_args_and_attrs(recwarn, __file__)

    def test_caption_entities_always_tuple(self):
        input_media_document = InputMediaDocument(self.media)
        assert input_media_document.caption_entities == ()

    def test_to_dict(self, input_media_document):
        input_media_document_dict = input_media_document.to_dict()
        assert input_media_document_dict["type"] == input_media_document.type
        assert input_media_document_dict["media"] == input_media_document.media
        assert input_media_document_dict["caption"] == input_media_document.caption
        assert input_media_document_dict["parse_mode"] == input_media_document.parse_mode
        assert input_media_document_dict["caption_entities"] == [
            ce.to_dict() for ce in input_media_document.caption_entities
        ]
        assert (
            input_media_document["disable_content_type_detection"]
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
            data_file("telegram.mp4"), thumbnail=data_file("telegram.jpg")
        )
        assert input_media_document.media == data_file("telegram.mp4").as_uri()
        assert input_media_document.thumbnail == data_file("telegram.jpg").as_uri()

    def test_with_local_files_throws_exception_with_different_thumb_and_thumbnail(self):
        with pytest.raises(ValueError, match="You passed different entities as 'thumb' and "):
            InputMediaDocument(
                data_file("telegram.mp4"),
                thumbnail=data_file("telegram.jpg"),
                thumb=data_file("telegram_no_standard_header.jpg"),
            )


@pytest.fixture(scope="module")
def media_group(photo, thumb):  # noqa: F811
    return [
        InputMediaPhoto(photo, caption="*photo* 1", parse_mode="Markdown"),
        InputMediaPhoto(thumb, caption="<b>photo</b> 2", parse_mode="HTML"),
        InputMediaPhoto(
            photo, caption="photo 3", caption_entities=[MessageEntity(MessageEntity.BOLD, 0, 5)]
        ),
    ]


@pytest.fixture(scope="module")
def media_group_no_caption_args(photo, thumb):  # noqa: F811
    return [InputMediaPhoto(photo), InputMediaPhoto(thumb), InputMediaPhoto(photo)]


@pytest.fixture(scope="module")
def media_group_no_caption_only_caption_entities(photo, thumb):  # noqa: F811
    return [
        InputMediaPhoto(photo, caption_entities=[MessageEntity(MessageEntity.BOLD, 0, 5)]),
        InputMediaPhoto(photo, caption_entities=[MessageEntity(MessageEntity.BOLD, 0, 5)]),
    ]


@pytest.fixture(scope="module")
def media_group_no_caption_only_parse_mode(photo, thumb):  # noqa: F811
    return [
        InputMediaPhoto(photo, parse_mode="Markdown"),
        InputMediaPhoto(thumb, parse_mode="HTML"),
    ]


class TestSendMediaGroupWithoutRequest:
    async def test_send_media_group_throws_error_with_group_caption_and_individual_captions(
        self,
        bot,
        chat_id,
        media_group,
        media_group_no_caption_only_caption_entities,
        media_group_no_caption_only_parse_mode,
    ):
        for group in (
            media_group,
            media_group_no_caption_only_caption_entities,
            media_group_no_caption_only_parse_mode,
        ):
            with pytest.raises(
                ValueError,
                match="You can only supply either group caption or media with captions.",
            ):
                await bot.send_media_group(chat_id, group, caption="foo")

    async def test_send_media_group_custom_filename(
        self,
        bot,
        chat_id,
        photo_file,  # noqa: F811
        animation_file,  # noqa: F811
        audio_file,  # noqa: F811
        video_file,  # noqa: F811
        monkeypatch,
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            result = all(
                field_tuple[0] == "custom_filename"
                for field_tuple in request_data.multipart_data.values()
            )
            if result is True:
                raise Exception("Test was successful")

        monkeypatch.setattr(bot.request, "post", make_assertion)

        media = [
            InputMediaAnimation(animation_file, filename="custom_filename"),
            InputMediaAudio(audio_file, filename="custom_filename"),
            InputMediaPhoto(photo_file, filename="custom_filename"),
            InputMediaVideo(video_file, filename="custom_filename"),
        ]

        with pytest.raises(Exception, match="Test was successful"):
            await bot.send_media_group(chat_id, media)

    async def test_send_media_group_with_thumbs(
        self, bot, chat_id, video_file, photo_file, monkeypatch  # noqa: F811
    ):
        async def make_assertion(method, url, request_data: RequestData, *args, **kwargs):
            nonlocal input_video
            files = request_data.multipart_data
            video_check = files[input_video.media.attach_name] == input_video.media.field_tuple
            thumb_check = (
                files[input_video.thumbnail.attach_name] == input_video.thumbnail.field_tuple
            )
            result = video_check and thumb_check
            raise Exception(f"Test was {'successful' if result else 'failing'}")

        monkeypatch.setattr(bot.request, "_request_wrapper", make_assertion)
        input_video = InputMediaVideo(video_file, thumbnail=photo_file)
        with pytest.raises(Exception, match="Test was successful"):
            await bot.send_media_group(chat_id, [input_video, input_video])

    async def test_edit_message_media_with_thumb(
        self, bot, chat_id, video_file, photo_file, monkeypatch  # noqa: F811
    ):
        async def make_assertion(
            method: str, url: str, request_data: RequestData = None, *args, **kwargs
        ):
            files = request_data.multipart_data
            video_check = files[input_video.media.attach_name] == input_video.media.field_tuple
            thumb_check = (
                files[input_video.thumbnail.attach_name] == input_video.thumbnail.field_tuple
            )
            result = video_check and thumb_check
            raise Exception(f"Test was {'successful' if result else 'failing'}")

        monkeypatch.setattr(bot.request, "_request_wrapper", make_assertion)
        input_video = InputMediaVideo(video_file, thumbnail=photo_file)
        with pytest.raises(Exception, match="Test was successful"):
            await bot.edit_message_media(chat_id=chat_id, message_id=123, media=input_video)


class CustomSequence(Sequence):
    def __init__(self, items):
        self.items = items

    def __getitem__(self, index):
        return self.items[index]

    def __len__(self):
        return len(self.items)


class TestSendMediaGroupWithRequest:
    async def test_send_media_group_photo(self, bot, chat_id, media_group):
        messages = await bot.send_media_group(chat_id, media_group)
        assert isinstance(messages, tuple)
        assert len(messages) == 3
        assert all(isinstance(mes, Message) for mes in messages)
        assert all(mes.media_group_id == messages[0].media_group_id for mes in messages)
        assert all(mes.caption == f"photo {idx+1}" for idx, mes in enumerate(messages))
        assert all(
            mes.caption_entities == (MessageEntity(MessageEntity.BOLD, 0, 5),) for mes in messages
        )

    async def test_send_media_group_new_files(
        self, bot, chat_id, video_file, photo_file  # noqa: F811
    ):
        async def func():
            return await bot.send_media_group(
                chat_id,
                [
                    InputMediaVideo(video_file),
                    InputMediaPhoto(photo_file),
                    InputMediaPhoto(data_file("telegram.jpg").read_bytes()),
                ],
            )

        messages = await expect_bad_request(
            func, "Type of file mismatch", "Telegram did not accept the file."
        )

        assert isinstance(messages, tuple)
        assert len(messages) == 3
        assert all(isinstance(mes, Message) for mes in messages)
        assert all(mes.media_group_id == messages[0].media_group_id for mes in messages)

    @pytest.mark.parametrize("sequence_type", [list, tuple, CustomSequence])
    @pytest.mark.parametrize("bot_class", ["raw_bot", "ext_bot"])
    async def test_send_media_group_different_sequences(
        self, bot, chat_id, media_group, sequence_type, bot_class, raw_bot
    ):
        """Test that send_media_group accepts different sequence types. This test ensures that
        Bot._insert_defaults works for arbitrary sequence types."""
        bot = bot if bot_class == "ext_bot" else raw_bot

        messages = await bot.send_media_group(chat_id, sequence_type(media_group))
        assert isinstance(messages, tuple)
        assert len(messages) == 3
        assert all(isinstance(mes, Message) for mes in messages)
        assert all(mes.media_group_id == messages[0].media_group_id for mes in messages)

    async def test_send_media_group_with_message_thread_id(
        self, bot, real_topic, forum_group_id, media_group  # noqa: F811
    ):
        messages = await bot.send_media_group(
            forum_group_id,
            media_group,
            message_thread_id=real_topic.message_thread_id,
        )
        assert isinstance(messages, tuple)
        assert len(messages) == 3
        assert all(isinstance(mes, Message) for mes in messages)
        assert all(i.message_thread_id == real_topic.message_thread_id for i in messages)

    @pytest.mark.parametrize(
        ("caption", "parse_mode", "caption_entities"),
        [
            # same combinations of caption options as in media_group fixture
            ("*photo* 1", "Markdown", None),
            ("<b>photo</b> 1", "HTML", None),
            ("photo 1", None, [MessageEntity(MessageEntity.BOLD, 0, 5)]),
        ],
    )
    async def test_send_media_group_with_group_caption(
        self,
        bot,
        chat_id,
        media_group_no_caption_args,
        caption,
        parse_mode,
        caption_entities,
    ):
        # prepare a copy to check later on if calling the method has caused side effects
        copied_media_group = media_group_no_caption_args.copy()

        messages = await bot.send_media_group(
            chat_id,
            media_group_no_caption_args,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )

        # Check that the method had no side effects:
        # original group was not changed and 1st item still points to the same object
        # (1st item must be copied within the method before adding the caption)
        assert media_group_no_caption_args == copied_media_group
        assert media_group_no_caption_args[0] is copied_media_group[0]

        assert not any(item.parse_mode for item in media_group_no_caption_args)

        assert isinstance(messages, tuple)
        assert len(messages) == 3
        assert all(isinstance(mes, Message) for mes in messages)

        first_message, other_messages = messages[0], messages[1:]
        assert all(mes.media_group_id == first_message.media_group_id for mes in messages)

        # Make sure first message got the caption, which will lead
        # to Telegram displaying its caption as group caption
        assert first_message.caption
        assert first_message.caption_entities == (MessageEntity(MessageEntity.BOLD, 0, 5),)

        # Check that other messages have no captions
        assert all(mes.caption is None for mes in other_messages)
        assert not any(mes.caption_entities for mes in other_messages)

    async def test_send_media_group_all_args(self, bot, raw_bot, chat_id, media_group):
        ext_bot = bot
        # We need to test 1) below both the bot and raw_bot and setting this up with
        # pytest.parametrize appears to be difficult ...
        aws = {b.send_message(chat_id, text="test") for b in (ext_bot, raw_bot)}
        for msg_task in asyncio.as_completed(aws):
            m1 = await msg_task
            copied_media_group = copy.copy(media_group)
            messages = await m1.get_bot().send_media_group(
                chat_id,
                media_group,
                disable_notification=True,
                reply_to_message_id=m1.message_id,
                protect_content=True,
            )

            # 1)
            # make sure that the media_group was not modified
            assert media_group == copied_media_group
            assert all(
                a.parse_mode == b.parse_mode for a, b in zip(media_group, copied_media_group)
            )

            assert isinstance(messages, tuple)
            assert len(messages) == 3
            assert all(isinstance(mes, Message) for mes in messages)
            assert all(mes.media_group_id == messages[0].media_group_id for mes in messages)
            assert all(mes.caption == f"photo {idx+1}" for idx, mes in enumerate(messages))
            assert all(
                mes.caption_entities == (MessageEntity(MessageEntity.BOLD, 0, 5),)
                for mes in messages
            )
            assert all(mes.has_protected_content for mes in messages)

    async def test_send_media_group_with_spoiler(
        self, bot, chat_id, photo_file, video_file  # noqa: F811
    ):
        # Media groups can't contain Animations, so that is tested in test_animation.py
        media = [
            InputMediaPhoto(photo_file, has_spoiler=True),
            InputMediaVideo(video_file, has_spoiler=True),
        ]
        messages = await bot.send_media_group(chat_id, media)
        assert isinstance(messages, tuple)
        assert len(messages) == 2
        assert all(isinstance(mes, Message) for mes in messages)
        assert all(mes.media_group_id == messages[0].media_group_id for mes in messages)
        assert all(mes.has_media_spoiler for mes in messages)

    async def test_edit_message_media(self, bot, raw_bot, chat_id, media_group):
        ext_bot = bot
        # We need to test 1) below both the bot and raw_bot and setting this up with
        # pytest.parametrize appears to be difficult ...
        aws = {b.send_media_group(chat_id, media_group) for b in (ext_bot, raw_bot)}
        for msg_task in asyncio.as_completed(aws):
            messages = await msg_task
            cid = messages[-1].chat.id
            mid = messages[-1].message_id
            copied_media = copy.copy(media_group[0])
            new_message = (
                await messages[-1]
                .get_bot()
                .edit_message_media(chat_id=cid, message_id=mid, media=media_group[0])
            )
            assert isinstance(new_message, Message)

            # 1)
            # make sure that the media was not modified
            assert media_group[0].parse_mode == copied_media.parse_mode

    async def test_edit_message_media_new_file(self, bot, chat_id, media_group, thumb_file):
        messages = await bot.send_media_group(chat_id, media_group)
        cid = messages[-1].chat.id
        mid = messages[-1].message_id
        new_message = await bot.edit_message_media(
            chat_id=cid, message_id=mid, media=InputMediaPhoto(thumb_file)
        )
        assert isinstance(new_message, Message)

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_media_group_default_allow_sending_without_reply(
        self, default_bot, chat_id, media_group, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            messages = await default_bot.send_media_group(
                chat_id,
                media_group,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert [m.reply_to_message is None for m in messages]
        elif default_bot.defaults.allow_sending_without_reply:
            messages = await default_bot.send_media_group(
                chat_id, media_group, reply_to_message_id=reply_to_message.message_id
            )
            assert [m.reply_to_message is None for m in messages]
        else:
            with pytest.raises(BadRequest, match="message not found"):
                await default_bot.send_media_group(
                    chat_id, media_group, reply_to_message_id=reply_to_message.message_id
                )

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_media_group_default_protect_content(
        self, chat_id, media_group, default_bot
    ):
        tasks = asyncio.gather(
            default_bot.send_media_group(chat_id, media_group),
            default_bot.send_media_group(chat_id, media_group, protect_content=False),
        )
        protected, unprotected = await tasks
        assert all(msg.has_protected_content for msg in protected)
        assert not all(msg.has_protected_content for msg in unprotected)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": ParseMode.HTML}], indirect=True)
    async def test_send_media_group_default_parse_mode(
        self, chat_id, media_group_no_caption_args, default_bot
    ):
        default = await default_bot.send_media_group(
            chat_id, media_group_no_caption_args, caption="<b>photo</b> 1"
        )

        # make sure no parse_mode was set as a side effect
        assert not any(item.parse_mode for item in media_group_no_caption_args)

        tasks = asyncio.gather(
            default_bot.send_media_group(
                chat_id,
                media_group_no_caption_args.copy(),
                caption="*photo* 1",
                parse_mode=ParseMode.MARKDOWN_V2,
            ),
            default_bot.send_media_group(
                chat_id,
                media_group_no_caption_args.copy(),
                caption="<b>photo</b> 1",
                parse_mode=None,
            ),
        )
        overridden_markdown_v2, overridden_none = await tasks

        # Make sure first message got the caption, which will lead to Telegram
        # displaying its caption as group caption
        assert overridden_none[0].caption == "<b>photo</b> 1"
        assert not overridden_none[0].caption_entities
        # First messages in these two groups have to have caption "photo 1"
        # because of parse mode (default or explicit)
        for mes_group in (default, overridden_markdown_v2):
            first_message = mes_group[0]
            assert first_message.caption == "photo 1"
            assert first_message.caption_entities == (MessageEntity(MessageEntity.BOLD, 0, 5),)

        # This check is valid for all 3 groups of messages
        for mes_group in (default, overridden_markdown_v2, overridden_none):
            first_message, other_messages = mes_group[0], mes_group[1:]
            assert all(mes.media_group_id == first_message.media_group_id for mes in mes_group)
            # Check that messages from 2nd message onwards have no captions
            assert all(mes.caption is None for mes in other_messages)
            assert not any(mes.caption_entities for mes in other_messages)

    @pytest.mark.parametrize(
        "default_bot", [{"parse_mode": ParseMode.HTML}], indirect=True, ids=["HTML-Bot"]
    )
    @pytest.mark.parametrize("media_type", ["animation", "document", "audio", "photo", "video"])
    async def test_edit_message_media_default_parse_mode(
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
        html_caption = "<b>bold</b> <i>italic</i> <code>code</code>"
        markdown_caption = "*bold* _italic_ `code`"
        test_caption = "bold italic code"
        test_entities = [
            MessageEntity(MessageEntity.BOLD, 0, 4),
            MessageEntity(MessageEntity.ITALIC, 5, 6),
            MessageEntity(MessageEntity.CODE, 12, 4),
        ]

        def build_media(parse_mode, med_type):
            kwargs = {}
            if parse_mode != ParseMode.HTML:
                kwargs["parse_mode"] = parse_mode
                kwargs["caption"] = markdown_caption
            else:
                kwargs["caption"] = html_caption

            if med_type == "animation":
                return InputMediaAnimation(animation, **kwargs)
            if med_type == "document":
                return InputMediaDocument(document, **kwargs)
            if med_type == "audio":
                return InputMediaAudio(audio, **kwargs)
            if med_type == "photo":
                return InputMediaPhoto(photo, **kwargs)
            if med_type == "video":
                return InputMediaVideo(video, **kwargs)
            return None

        message = await default_bot.send_photo(chat_id, photo)

        media = build_media(parse_mode=ParseMode.HTML, med_type=media_type)
        copied_media = copy.copy(media)
        message = await default_bot.edit_message_media(
            media,
            message.chat_id,
            message.message_id,
        )
        assert message.caption == test_caption
        assert message.caption_entities == tuple(test_entities)
        # make sure that the media was not modified
        assert media.parse_mode == copied_media.parse_mode

        # Remove caption to avoid "Message not changed"
        await message.edit_caption()

        media = build_media(parse_mode=ParseMode.MARKDOWN_V2, med_type=media_type)
        copied_media = copy.copy(media)
        message = await default_bot.edit_message_media(
            media,
            message.chat_id,
            message.message_id,
        )
        assert message.caption == test_caption
        assert message.caption_entities == tuple(test_entities)
        # make sure that the media was not modified
        assert media.parse_mode == copied_media.parse_mode

        # Remove caption to avoid "Message not changed"
        await message.edit_caption()

        media = build_media(parse_mode=None, med_type=media_type)
        copied_media = copy.copy(media)
        message = await default_bot.edit_message_media(
            media,
            message.chat_id,
            message.message_id,
        )
        assert message.caption == markdown_caption
        assert message.caption_entities == ()
        # make sure that the media was not modified
        assert media.parse_mode == copied_media.parse_mode
