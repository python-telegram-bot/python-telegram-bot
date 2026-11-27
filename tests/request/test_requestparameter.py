#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
import datetime as dtm
import json
from collections.abc import Sequence

import pytest

from telegram import (
    InputFile,
    InputMediaLivePhoto,
    InputMediaPhoto,
    InputMediaSticker,
    InputMediaVideo,
    InputPaidMediaLivePhoto,
    InputPaidMediaVideo,
    InputPollOption,
    InputProfilePhotoAnimated,
    InputProfilePhotoStatic,
    InputSticker,
    InputStoryContentPhoto,
    InputStoryContentVideo,
    MessageEntity,
)
from telegram.constants import ChatType
from telegram.request._requestparameter import RequestParameter
from tests.auxil.build_messages import make_message
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


class TestRequestParameterWithoutRequest:
    def test_slot_behaviour(self):
        inst = RequestParameter("name", "value", [1, 2])
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_init(self):
        request_parameter = RequestParameter("name", "value", [1, 2])
        assert request_parameter.name == "name"
        assert request_parameter.value == "value"
        assert request_parameter.input_files == [1, 2]

        request_parameter = RequestParameter("name", "value", None)
        assert request_parameter.name == "name"
        assert request_parameter.value == "value"
        assert request_parameter.input_files is None

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (1, "1"),
            ("one", "one"),
            (True, "true"),
            (None, None),
            ([1, "1"], '[1, "1"]'),
            ({True: None}, '{"true": null}'),
            ((1,), "[1]"),
        ],
    )
    def test_json_value(self, value, expected):
        request_parameter = RequestParameter("name", value, None)
        assert request_parameter.json_value == expected

    def test_multiple_multipart_data(self):
        assert RequestParameter("name", "value", []).multipart_data is None

        input_file_1 = InputFile("data1", attach=True)
        input_file_2 = InputFile("data2", filename="custom")
        request_parameter = RequestParameter(
            value="value", name="name", input_files=[input_file_1, input_file_2]
        )
        files = request_parameter.multipart_data
        assert files[input_file_1.attach_name] == input_file_1.field_tuple
        assert files["name"] == input_file_2.field_tuple

    @pytest.mark.parametrize(
        ("value", "expected_value"),
        [
            (True, True),
            ("str", "str"),
            ({1: 1.0}, {1: 1.0}),
            (ChatType.PRIVATE, "private"),
            (MessageEntity("type", 1, 1), {"type": "type", "offset": 1, "length": 1}),
            (dtm.datetime(2019, 11, 11, 0, 26, 16, 10**5), 1573431976),
            (dtm.timedelta(days=42), 42 * 24 * 60 * 60),
            (
                [
                    True,
                    "str",
                    MessageEntity("type", 1, 1),
                    ChatType.PRIVATE,
                    dtm.datetime(2019, 11, 11, 0, 26, 16, 10**5),
                ],
                [True, "str", {"type": "type", "offset": 1, "length": 1}, "private", 1573431976],
            ),
        ],
    )
    def test_from_input_no_media(self, value, expected_value):
        request_parameter = RequestParameter.from_input("key", value)
        assert request_parameter.value == expected_value
        assert request_parameter.input_files is None

    @pytest.mark.parametrize(
        ("value", "expected_type", "expected_value"),
        [
            (dtm.timedelta(seconds=1), int, 1),
            (dtm.timedelta(milliseconds=1), float, 0.001),
        ],
    )
    def test_from_input_timedelta(self, value, expected_type, expected_value):
        request_parameter = RequestParameter.from_input("key", value)
        assert request_parameter.value == expected_value
        assert request_parameter.input_files is None
        assert isinstance(request_parameter.value, expected_type)

    def test_from_input_inputfile(self):
        inputfile_1 = InputFile("data1", filename="inputfile_1", attach=True)
        inputfile_2 = InputFile("data2", filename="inputfile_2")

        request_parameter = RequestParameter.from_input("key", inputfile_1)
        assert request_parameter.value == inputfile_1.attach_uri
        assert request_parameter.input_files == [inputfile_1]

        request_parameter = RequestParameter.from_input("key", inputfile_2)
        assert request_parameter.value is None
        assert request_parameter.input_files == [inputfile_2]

        request_parameter = RequestParameter.from_input("key", [inputfile_1, inputfile_2])
        assert request_parameter.value == [inputfile_1.attach_uri]
        assert request_parameter.input_files == [inputfile_1, inputfile_2]

    @pytest.mark.parametrize(
        "input_media",
        [
            InputMediaPhoto(b"photo"),
            InputMediaVideo(b"video", thumbnail=b"thumbnail", cover=b"cover"),
            InputMediaVideo("file_id", thumbnail=b"thumbnail", cover=b"cover"),
            InputPaidMediaVideo(b"video", thumbnail=b"thumbnail", cover=b"cover"),
            InputMediaLivePhoto(b"video", b"photo"),
            InputMediaLivePhoto("file_id", InputFile(b"photo")),
            InputPaidMediaLivePhoto(b"video", b"photo"),
        ],
        ids=lambda media: type(media).__name__,
    )
    def test_from_input_media_files(self, input_media):
        expected = input_media.to_dict()
        request_parameter = RequestParameter.from_input("key", input_media)
        payload = json.loads(request_parameter.json_value)
        files = request_parameter.multipart_data
        assert len(files) == sum(isinstance(field, InputFile) for field in expected.values())
        for key, field in expected.items():
            if isinstance(field, InputFile):
                uri = payload[key]
                assert uri.startswith("attach://")
                if field.attach_uri:
                    assert uri == field.attach_uri
                assert files[uri.removeprefix("attach://")] == field.field_tuple
                expected[key] = uri
        assert payload == expected

    @pytest.mark.parametrize("media_type", [InputMediaVideo, InputPaidMediaVideo])
    @pytest.mark.parametrize("media", ["typed_id", InputFile(b"video", attach=True)])
    def test_from_input_media_api_kwargs(self, media_type, media):
        api_kwargs = {
            "media": "override_id",
            "cover": "cover_id",
            "future_field": {"enabled": True},
        }
        video = media_type(media, cover=b"unused", api_kwargs=api_kwargs)
        parameter = RequestParameter.from_input("media", video)
        expected = {"type": "video", **api_kwargs}
        if isinstance(media, InputFile):
            expected["media"] = media.attach_uri
            assert parameter.multipart_data == {media.attach_name: media.field_tuple}
        else:
            assert parameter.multipart_data is None
        assert json.loads(parameter.json_value) == expected

    async def test_send_poll_with_uploaded_options(self, offline_bot, monkeypatch):
        photo = InputFile(b"photo", filename="photo.jpg")
        sticker = InputFile(b"sticker", filename="sticker.webp")
        raw_media = {"type": "photo", "media": "file_id"}
        extra = {"future_field": True}

        async def check_request(url, request_data, **kwargs):
            photo_option, sticker_option, overridden, raw_only, plain = json.loads(
                request_data.json_parameters["options"]
            )
            assert overridden["media"] == raw_media
            assert raw_only["media"] == raw_media
            assert photo_option["media"]["future_field"] is True
            assert sticker_option["future_field"] is True
            assert "media" not in plain
            files = request_data.multipart_data
            assert len(files) == 2
            for option, source in ((photo_option, photo), (sticker_option, sticker)):
                uri = option["media"]["media"]
                assert uri.startswith("attach://")
                assert files[uri.removeprefix("attach://")] == source.field_tuple
            return make_message("poll").to_dict()

        monkeypatch.setattr(offline_bot.request, "post", check_request)
        await offline_bot.send_poll(
            1,
            "question",
            [
                InputPollOption("photo", media=InputMediaPhoto(photo, api_kwargs=extra)),
                InputPollOption("sticker", media=InputMediaSticker(sticker), api_kwargs=extra),
                InputPollOption(
                    "override", media=InputMediaPhoto(b"unused"), api_kwargs={"media": raw_media}
                ),
                InputPollOption("raw", api_kwargs={"media": raw_media}),
                "plain",
            ],
        )
        assert photo.attach_name is None
        assert sticker.attach_name is None

    def test_from_input_profile_photo_static(self):
        input_profile_photo = InputProfilePhotoStatic(data_file("telegram.jpg").read_bytes())
        expected = input_profile_photo.to_dict()
        expected.update({"photo": input_profile_photo.photo.attach_uri})
        request_parameter = RequestParameter.from_input("key", input_profile_photo)
        assert request_parameter.value == expected
        assert request_parameter.input_files == [input_profile_photo.photo]

    def test_from_input_profile_photo_animated(self):
        input_profile_photo = InputProfilePhotoAnimated(
            data_file("telegram2.mp4").read_bytes(),
            main_frame_timestamp=dtm.timedelta(seconds=42, milliseconds=43),
        )
        expected = input_profile_photo.to_dict()
        expected.update({"animation": input_profile_photo.animation.attach_uri})
        request_parameter = RequestParameter.from_input("key", input_profile_photo)
        assert request_parameter.value == expected
        assert request_parameter.input_files == [input_profile_photo.animation]

    @pytest.mark.parametrize(
        ("cls", "args"),
        [
            (InputProfilePhotoStatic, (data_file("telegram.jpg"),)),
            (
                InputProfilePhotoAnimated,
                (data_file("telegram2.mp4"), dtm.timedelta(seconds=42, milliseconds=43)),
            ),
        ],
    )
    def test_from_input_profile_photo_local_files(self, cls, args):
        input_profile_photo = cls(*args)
        expected = input_profile_photo.to_dict()
        requested = RequestParameter.from_input("key", input_profile_photo)
        assert requested.value == expected
        assert requested.input_files is None

    def test_from_input_inputsticker(self):
        input_sticker = InputSticker(data_file("telegram.png").read_bytes(), ["emoji"], "static")
        expected = input_sticker.to_dict()
        expected.update({"sticker": input_sticker.sticker.attach_uri})
        request_parameter = RequestParameter.from_input("key", input_sticker)
        assert request_parameter.value == expected
        assert request_parameter.input_files == [input_sticker.sticker]

    def test_from_input_story_content_photo(self):
        input_story_content_photo = InputStoryContentPhoto(data_file("telegram.jpg").read_bytes())
        expected = input_story_content_photo.to_dict()
        expected.update({"photo": input_story_content_photo.photo.attach_uri})
        request_parameter = RequestParameter.from_input("key", input_story_content_photo)
        assert request_parameter.value == expected
        assert request_parameter.input_files == [input_story_content_photo.photo]

    def test_from_input_story_content_video(self):
        input_story_content_video = InputStoryContentVideo(data_file("telegram2.mp4").read_bytes())
        expected = input_story_content_video.to_dict()
        expected.update({"video": input_story_content_video.video.attach_uri})
        request_parameter = RequestParameter.from_input("key", input_story_content_video)
        assert request_parameter.value == expected
        assert request_parameter.input_files == [input_story_content_video.video]

    @pytest.mark.parametrize(
        ("cls", "arg"),
        [
            (InputStoryContentPhoto, data_file("telegram.jpg")),
            (InputStoryContentVideo, data_file("telegram2.mp4")),
        ],
    )
    def test_from_input_story_content_local_files(self, cls, arg):
        input_story_content = cls(arg)
        expected = input_story_content.to_dict()
        requested = RequestParameter.from_input("key", input_story_content)
        assert requested.value == expected
        assert requested.input_files is None

    def test_from_input_str_and_bytes(self):
        input_str = "test_input"
        request_parameter = RequestParameter.from_input("input", input_str)
        assert request_parameter.value == input_str
        assert request_parameter.name == "input"
        assert request_parameter.input_files is None

        input_bytes = b"test_input"
        request_parameter = RequestParameter.from_input("input", input_bytes)
        assert request_parameter.value == input_bytes
        assert request_parameter.name == "input"
        assert request_parameter.input_files is None

    def test_from_input_different_sequences(self):
        input_list = ["item1", "item2"]
        request_parameter = RequestParameter.from_input("input", input_list)
        assert request_parameter.value == input_list
        assert request_parameter.name == "input"
        assert request_parameter.input_files is None

        input_tuple = tuple(input_list)
        request_parameter = RequestParameter.from_input("input", input_tuple)
        assert request_parameter.value == input_list
        assert request_parameter.name == "input"
        assert request_parameter.input_files is None

        class CustomSequence(Sequence):
            def __init__(self, items):
                self.items = items

            def __getitem__(self, index):
                return self.items[index]

            def __len__(self):
                return len(self.items)

        input_custom_sequence = CustomSequence(input_list)
        request_parameter = RequestParameter.from_input("input", input_custom_sequence)
        assert request_parameter.value == input_list
        assert request_parameter.name == "input"
        assert request_parameter.input_files is None
