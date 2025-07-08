#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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

import pytest

from telegram import (
    BusinessBotRights,
    BusinessConnection,
    Chat,
    InputProfilePhotoStatic,
    InputStoryContentPhoto,
    MessageEntity,
    StarAmount,
    Story,
    StoryAreaTypeLink,
    StoryAreaTypeUniqueGift,
    User,
)
from telegram._files._inputstorycontent import InputStoryContentVideo
from telegram._files.sticker import Sticker
from telegram._gifts import AcceptedGiftTypes, Gift
from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inputchecklist import InputChecklist, InputChecklistTask
from telegram._message import Message
from telegram._ownedgift import OwnedGiftRegular, OwnedGifts
from telegram._reply import ReplyParameters
from telegram._utils.datetime import UTC
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.constants import InputProfilePhotoType, InputStoryContentType
from tests.auxil.files import data_file


class BusinessMethodsTestBase:
    bci = "42"


class TestBusinessMethodsWithoutRequest(BusinessMethodsTestBase):
    async def test_get_business_connection(self, offline_bot, monkeypatch):
        user = User(1, "first", False)
        user_chat_id = 1
        date = dtm.datetime.utcnow()
        rights = BusinessBotRights(can_reply=True)
        is_enabled = True
        bc = BusinessConnection(
            self.bci,
            user,
            user_chat_id,
            date,
            is_enabled,
            rights=rights,
        ).to_json()

        async def do_request(*args, **kwargs):
            data = kwargs.get("request_data")
            obj = data.parameters.get("business_connection_id")
            if obj == self.bci:
                return 200, f'{{"ok": true, "result": {bc}}}'.encode()
            return 400, b'{"ok": false, "result": []}'

        monkeypatch.setattr(offline_bot.request, "do_request", do_request)
        obj = await offline_bot.get_business_connection(business_connection_id=self.bci)
        assert isinstance(obj, BusinessConnection)

    @pytest.mark.parametrize("bool_param", [True, False, None])
    async def test_get_business_account_gifts(self, offline_bot, monkeypatch, bool_param):
        offset = 50
        limit = 50
        owned_gifts = OwnedGifts(
            total_count=1,
            gifts=[
                OwnedGiftRegular(
                    gift=Gift(
                        id="id1",
                        sticker=Sticker(
                            "file_id", "file_unique_id", 512, 512, False, False, "regular"
                        ),
                        star_count=5,
                    ),
                    send_date=dtm.datetime.now(tz=UTC).replace(microsecond=0),
                    owned_gift_id="some_id_1",
                )
            ],
        ).to_json()

        async def do_request_and_make_assertions(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("exclude_unsaved") is bool_param
            assert data.get("exclude_saved") is bool_param
            assert data.get("exclude_unlimited") is bool_param
            assert data.get("exclude_limited") is bool_param
            assert data.get("exclude_unique") is bool_param
            assert data.get("sort_by_price") is bool_param
            assert data.get("offset") == offset
            assert data.get("limit") == limit

            return 200, f'{{"ok": true, "result": {owned_gifts}}}'.encode()

        monkeypatch.setattr(offline_bot.request, "do_request", do_request_and_make_assertions)
        obj = await offline_bot.get_business_account_gifts(
            business_connection_id=self.bci,
            exclude_unsaved=bool_param,
            exclude_saved=bool_param,
            exclude_unlimited=bool_param,
            exclude_limited=bool_param,
            exclude_unique=bool_param,
            sort_by_price=bool_param,
            offset=offset,
            limit=limit,
        )
        assert isinstance(obj, OwnedGifts)

    async def test_get_business_account_star_balance(self, offline_bot, monkeypatch):
        star_amount_json = StarAmount(amount=100, nanostar_amount=356).to_json()

        async def do_request(*args, **kwargs):
            data = kwargs.get("request_data")
            obj = data.parameters.get("business_connection_id")
            if obj == self.bci:
                return 200, f'{{"ok": true, "result": {star_amount_json}}}'.encode()
            return 400, b'{"ok": false, "result": []}'

        monkeypatch.setattr(offline_bot.request, "do_request", do_request)
        obj = await offline_bot.get_business_account_star_balance(business_connection_id=self.bci)
        assert isinstance(obj, StarAmount)

    async def test_read_business_message(self, offline_bot, monkeypatch):
        chat_id = 43
        message_id = 44

        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("chat_id") == chat_id
            assert data.get("message_id") == message_id
            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.read_business_message(
            business_connection_id=self.bci, chat_id=chat_id, message_id=message_id
        )

    async def test_delete_business_messages(self, offline_bot, monkeypatch):
        message_ids = [1, 2, 3]

        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("message_ids") == message_ids
            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.delete_business_messages(
            business_connection_id=self.bci, message_ids=message_ids
        )

    @pytest.mark.parametrize("last_name", [None, "last_name"])
    async def test_set_business_account_name(self, offline_bot, monkeypatch, last_name):
        first_name = "Test Business Account"

        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("first_name") == first_name
            assert data.get("last_name") == last_name
            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.set_business_account_name(
            business_connection_id=self.bci, first_name=first_name, last_name=last_name
        )

    @pytest.mark.parametrize("username", ["username", None])
    async def test_set_business_account_username(self, offline_bot, monkeypatch, username):
        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("username") == username
            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.set_business_account_username(
            business_connection_id=self.bci, username=username
        )

    @pytest.mark.parametrize("bio", ["bio", None])
    async def test_set_business_account_bio(self, offline_bot, monkeypatch, bio):
        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("bio") == bio
            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.set_business_account_bio(business_connection_id=self.bci, bio=bio)

    async def test_set_business_account_gift_settings(self, offline_bot, monkeypatch):
        show_gift_button = True
        accepted_gift_types = AcceptedGiftTypes(True, True, True, True)

        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").json_parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("show_gift_button") == "true"
            assert data.get("accepted_gift_types") == accepted_gift_types.to_json()
            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.set_business_account_gift_settings(
            business_connection_id=self.bci,
            show_gift_button=show_gift_button,
            accepted_gift_types=accepted_gift_types,
        )

    async def test_convert_gift_to_stars(self, offline_bot, monkeypatch):
        owned_gift_id = "some_id"

        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("owned_gift_id") == owned_gift_id
            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.convert_gift_to_stars(
            business_connection_id=self.bci,
            owned_gift_id=owned_gift_id,
        )

    @pytest.mark.parametrize("keep_original_details", [True, None])
    @pytest.mark.parametrize("star_count", [100, None])
    async def test_upgrade_gift(self, offline_bot, monkeypatch, keep_original_details, star_count):
        owned_gift_id = "some_id"

        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("owned_gift_id") == owned_gift_id
            assert data.get("keep_original_details") is keep_original_details
            assert data.get("star_count") == star_count

            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.upgrade_gift(
            business_connection_id=self.bci,
            owned_gift_id=owned_gift_id,
            keep_original_details=keep_original_details,
            star_count=star_count,
        )

    @pytest.mark.parametrize("star_count", [100, None])
    async def test_transfer_gift(self, offline_bot, monkeypatch, star_count):
        owned_gift_id = "some_id"
        new_owner_chat_id = 123

        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("owned_gift_id") == owned_gift_id
            assert data.get("new_owner_chat_id") == new_owner_chat_id
            assert data.get("star_count") == star_count

            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.transfer_gift(
            business_connection_id=self.bci,
            owned_gift_id=owned_gift_id,
            new_owner_chat_id=new_owner_chat_id,
            star_count=star_count,
        )

    async def test_transfer_business_account_stars(self, offline_bot, monkeypatch):
        star_count = 100

        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("star_count") == star_count

            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.transfer_business_account_stars(
            business_connection_id=self.bci,
            star_count=star_count,
        )

    @pytest.mark.parametrize("is_public", [True, False, None, DEFAULT_NONE])
    async def test_set_business_account_profile_photo(self, offline_bot, monkeypatch, is_public):
        async def make_assertion(*args, **kwargs):
            request_data = kwargs.get("request_data")
            params = request_data.parameters
            assert params.get("business_connection_id") == self.bci
            if is_public is DEFAULT_NONE:
                assert "is_public" not in params
            else:
                assert params.get("is_public") == is_public

            assert (photo_dict := params.get("photo")).get("type") == InputProfilePhotoType.STATIC
            assert (photo_attach := photo_dict["photo"]).startswith("attach://")
            assert isinstance(
                request_data.multipart_data.get(photo_attach.removeprefix("attach://")), tuple
            )

            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "photo": InputProfilePhotoStatic(
                photo=data_file("telegram.jpg").read_bytes(),
            ),
        }
        if is_public is not DEFAULT_NONE:
            kwargs["is_public"] = is_public

        assert await offline_bot.set_business_account_profile_photo(**kwargs)

    async def test_set_business_account_profile_photo_local_file(self, offline_bot, monkeypatch):
        async def make_assertion(*args, **kwargs):
            request_data = kwargs.get("request_data")
            params = request_data.parameters
            assert params.get("business_connection_id") == self.bci

            assert (photo_dict := params.get("photo")).get("type") == InputProfilePhotoType.STATIC
            assert photo_dict["photo"] == data_file("telegram.jpg").as_uri()
            assert not request_data.multipart_data

            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "photo": InputProfilePhotoStatic(
                photo=data_file("telegram.jpg"),
            ),
        }

        assert await offline_bot.set_business_account_profile_photo(**kwargs)

    @pytest.mark.parametrize("is_public", [True, False, None, DEFAULT_NONE])
    async def test_remove_business_account_profile_photo(
        self, offline_bot, monkeypatch, is_public
    ):
        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            if is_public is DEFAULT_NONE:
                assert "is_public" not in data
            else:
                assert data.get("is_public") == is_public

            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        kwargs = {"business_connection_id": self.bci}
        if is_public is not DEFAULT_NONE:
            kwargs["is_public"] = is_public

        assert await offline_bot.remove_business_account_profile_photo(**kwargs)

    @pytest.mark.parametrize("active_period", [dtm.timedelta(seconds=30), 30])
    async def test_post_story_all_args(self, offline_bot, monkeypatch, active_period):
        content = InputStoryContentPhoto(photo=data_file("telegram.jpg").read_bytes())
        caption = "test caption"
        caption_entities = [
            MessageEntity(MessageEntity.BOLD, 0, 3),
            MessageEntity(MessageEntity.ITALIC, 5, 11),
        ]
        parse_mode = "Markdown"
        areas = [StoryAreaTypeLink("http_url"), StoryAreaTypeUniqueGift("unique_gift_name")]
        post_to_chat_page = True
        protect_content = True
        json_story = Story(chat=Chat(123, "private"), id=123).to_json()

        async def do_request_and_make_assertions(*args, **kwargs):
            request_data = kwargs.get("request_data")
            params = kwargs.get("request_data").parameters
            assert params.get("business_connection_id") == self.bci
            assert params.get("active_period") == 30
            assert params.get("caption") == caption
            assert params.get("caption_entities") == [e.to_dict() for e in caption_entities]
            assert params.get("parse_mode") == parse_mode
            assert params.get("areas") == [area.to_dict() for area in areas]
            assert params.get("post_to_chat_page") is post_to_chat_page
            assert params.get("protect_content") is protect_content

            assert (content_dict := params.get("content")).get(
                "type"
            ) == InputStoryContentType.PHOTO
            assert (photo_attach := content_dict["photo"]).startswith("attach://")
            assert isinstance(
                request_data.multipart_data.get(photo_attach.removeprefix("attach://")), tuple
            )

            return 200, f'{{"ok": true, "result": {json_story}}}'.encode()

        monkeypatch.setattr(offline_bot.request, "do_request", do_request_and_make_assertions)
        obj = await offline_bot.post_story(
            business_connection_id=self.bci,
            content=content,
            active_period=active_period,
            caption=caption,
            caption_entities=caption_entities,
            parse_mode=parse_mode,
            areas=areas,
            post_to_chat_page=post_to_chat_page,
            protect_content=protect_content,
        )
        assert isinstance(obj, Story)

    @pytest.mark.parametrize("active_period", [dtm.timedelta(seconds=30), 30])
    async def test_post_story_local_file(self, offline_bot, monkeypatch, active_period):
        json_story = Story(chat=Chat(123, "private"), id=123).to_json()

        async def make_assertion(*args, **kwargs):
            request_data = kwargs.get("request_data")
            params = request_data.parameters
            assert params.get("business_connection_id") == self.bci

            assert (content_dict := params.get("content")).get(
                "type"
            ) == InputStoryContentType.PHOTO
            assert content_dict["photo"] == data_file("telegram.jpg").as_uri()
            assert not request_data.multipart_data

            return 200, f'{{"ok": true, "result": {json_story}}}'.encode()

        monkeypatch.setattr(offline_bot.request, "do_request", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "content": InputStoryContentPhoto(
                photo=data_file("telegram.jpg"),
            ),
            "active_period": active_period,
        }

        assert await offline_bot.post_story(**kwargs)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    @pytest.mark.parametrize(
        ("passed_value", "expected_value"),
        [(DEFAULT_NONE, "Markdown"), ("HTML", "HTML"), (None, None)],
    )
    async def test_post_story_default_parse_mode(
        self, default_bot, monkeypatch, passed_value, expected_value
    ):
        async def make_assertion(url, request_data, *args, **kwargs):
            assert request_data.parameters.get("parse_mode") == expected_value
            return Story(chat=Chat(123, "private"), id=123).to_dict()

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "content": InputStoryContentPhoto(photo=data_file("telegram.jpg").read_bytes()),
            "active_period": dtm.timedelta(seconds=20),
            "caption": "caption",
        }
        if passed_value is not DEFAULT_NONE:
            kwargs["parse_mode"] = passed_value

        await default_bot.post_story(**kwargs)

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    @pytest.mark.parametrize(
        ("passed_value", "expected_value"),
        [(DEFAULT_NONE, True), (False, False), (None, None)],
    )
    async def test_post_story_default_protect_content(
        self, default_bot, monkeypatch, passed_value, expected_value
    ):
        async def make_assertion(url, request_data, *args, **kwargs):
            assert request_data.parameters.get("protect_content") == expected_value
            return Story(chat=Chat(123, "private"), id=123).to_dict()

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "content": InputStoryContentPhoto(bytes("photo", encoding="utf-8")),
            "active_period": dtm.timedelta(seconds=20),
        }
        if passed_value is not DEFAULT_NONE:
            kwargs["protect_content"] = passed_value

        await default_bot.post_story(**kwargs)

    @pytest.mark.parametrize(
        ("argument", "expected"),
        [(4, 4), (4.0, 4), (dtm.timedelta(seconds=4), 4), (4.5, 4.5)],
    )
    async def test_post_story_float_time_period(
        self, offline_bot, monkeypatch, argument, expected
    ):
        # We test that whole number conversion works properly. Only tested here but
        # relevant for some other methods too (e.g bot.set_business_account_profile_photo)
        async def make_assertion(url, request_data, *args, **kwargs):
            data = request_data.parameters
            content = data["content"]

            assert content["duration"] == expected
            assert type(content["duration"]) is type(expected)
            assert content["cover_frame_timestamp"] == expected
            assert type(content["cover_frame_timestamp"]) is type(expected)

            return Story(chat=Chat(123, "private"), id=123).to_dict()

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "content": InputStoryContentVideo(
                video=data_file("telegram.mp4"),
                duration=argument,
                cover_frame_timestamp=argument,
            ),
            "active_period": dtm.timedelta(seconds=20),
        }

        assert await offline_bot.post_story(**kwargs)

    async def test_edit_story_all_args(self, offline_bot, monkeypatch):
        story_id = 1234
        content = InputStoryContentPhoto(photo=data_file("telegram.jpg").read_bytes())
        caption = "test caption"
        caption_entities = [
            MessageEntity(MessageEntity.BOLD, 0, 3),
            MessageEntity(MessageEntity.ITALIC, 5, 11),
        ]
        parse_mode = "Markdown"
        areas = [StoryAreaTypeLink("http_url"), StoryAreaTypeUniqueGift("unique_gift_name")]
        json_story = Story(chat=Chat(123, "private"), id=123).to_json()

        async def do_request_and_make_assertions(*args, **kwargs):
            request_data = kwargs.get("request_data")
            params = kwargs.get("request_data").parameters
            assert params.get("business_connection_id") == self.bci
            assert params.get("story_id") == story_id
            assert params.get("caption") == caption
            assert params.get("caption_entities") == [e.to_dict() for e in caption_entities]
            assert params.get("parse_mode") == parse_mode
            assert params.get("areas") == [area.to_dict() for area in areas]

            assert (content_dict := params.get("content")).get(
                "type"
            ) == InputStoryContentType.PHOTO
            assert (photo_attach := content_dict["photo"]).startswith("attach://")
            assert isinstance(
                request_data.multipart_data.get(photo_attach.removeprefix("attach://")), tuple
            )

            return 200, f'{{"ok": true, "result": {json_story}}}'.encode()

        monkeypatch.setattr(offline_bot.request, "do_request", do_request_and_make_assertions)
        obj = await offline_bot.edit_story(
            business_connection_id=self.bci,
            story_id=story_id,
            content=content,
            caption=caption,
            caption_entities=caption_entities,
            parse_mode=parse_mode,
            areas=areas,
        )
        assert isinstance(obj, Story)

    async def test_edit_story_local_file(self, offline_bot, monkeypatch):
        json_story = Story(chat=Chat(123, "private"), id=123).to_json()

        async def make_assertion(*args, **kwargs):
            request_data = kwargs.get("request_data")
            params = request_data.parameters
            assert params.get("business_connection_id") == self.bci

            assert (content_dict := params.get("content")).get(
                "type"
            ) == InputStoryContentType.PHOTO
            assert content_dict["photo"] == data_file("telegram.jpg").as_uri()
            assert not request_data.multipart_data

            return 200, f'{{"ok": true, "result": {json_story}}}'.encode()

        monkeypatch.setattr(offline_bot.request, "do_request", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "story_id": 1234,
            "content": InputStoryContentPhoto(
                photo=data_file("telegram.jpg"),
            ),
        }

        assert await offline_bot.edit_story(**kwargs)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    @pytest.mark.parametrize(
        ("passed_value", "expected_value"),
        [(DEFAULT_NONE, "Markdown"), ("HTML", "HTML"), (None, None)],
    )
    async def test_edit_story_default_parse_mode(
        self, default_bot, monkeypatch, passed_value, expected_value
    ):
        async def make_assertion(url, request_data, *args, **kwargs):
            assert request_data.parameters.get("parse_mode") == expected_value
            return Story(chat=Chat(123, "private"), id=123).to_dict()

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "story_id": 1234,
            "content": InputStoryContentPhoto(photo=data_file("telegram.jpg").read_bytes()),
            "caption": "caption",
        }
        if passed_value is not DEFAULT_NONE:
            kwargs["parse_mode"] = passed_value

        await default_bot.edit_story(**kwargs)

    async def test_delete_story(self, offline_bot, monkeypatch):
        story_id = 123

        async def make_assertion(*args, **kwargs):
            data = kwargs.get("request_data").parameters
            assert data.get("business_connection_id") == self.bci
            assert data.get("story_id") == story_id
            return True

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)
        assert await offline_bot.delete_story(business_connection_id=self.bci, story_id=story_id)

    async def test_send_checklist_all_args(self, offline_bot, monkeypatch):
        chat_id = 123
        checklist = InputChecklist(
            title="My Checklist",
            tasks=[InputChecklistTask(1, "Task 1"), InputChecklistTask(2, "Task 2")],
        )
        disable_notification = True
        protect_content = False
        message_effect_id = 42
        reply_parameters = ReplyParameters(23, chat_id, allow_sending_without_reply=True)
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="test", callback_data="test2")]]
        )
        json_message = Message(1, dtm.datetime.now(), Chat(1, ""), text="test").to_json()

        async def make_assertions(*args, **kwargs):
            params = kwargs.get("request_data").parameters
            assert params.get("business_connection_id") == self.bci
            assert params.get("chat_id") == chat_id
            assert params.get("checklist") == checklist.to_dict()
            assert params.get("disable_notification") is disable_notification
            assert params.get("protect_content") is protect_content
            assert params.get("message_effect_id") == message_effect_id
            assert params.get("reply_parameters") == reply_parameters.to_dict()
            assert params.get("reply_markup") == reply_markup.to_dict()

            return 200, f'{{"ok": true, "result": {json_message}}}'.encode()

        monkeypatch.setattr(offline_bot.request, "do_request", make_assertions)
        obj = await offline_bot.send_checklist(
            business_connection_id=self.bci,
            chat_id=chat_id,
            checklist=checklist,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_effect_id=message_effect_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
        )
        assert isinstance(obj, Message)

    @pytest.mark.parametrize("default_bot", [{"disable_notification": True}], indirect=True)
    @pytest.mark.parametrize(
        ("passed_value", "expected_value"),
        [(DEFAULT_NONE, True), (False, False), (None, None)],
    )
    async def test_send_checklist_default_disable_notification(
        self, default_bot, monkeypatch, passed_value, expected_value
    ):
        async def make_assertion(url, request_data, *args, **kwargs):
            assert request_data.parameters.get("disable_notification") is expected_value
            return Message(1, dtm.datetime.now(), Chat(1, ""), text="test").to_dict()

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "chat_id": 123,
            "checklist": InputChecklist(
                title="My Checklist",
                tasks=[InputChecklistTask(1, "Task 1")],
            ),
        }
        if passed_value is not DEFAULT_NONE:
            kwargs["disable_notification"] = passed_value

        await default_bot.send_checklist(**kwargs)

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    @pytest.mark.parametrize(
        ("passed_value", "expected_value"),
        [(DEFAULT_NONE, True), (False, False), (None, None)],
    )
    async def test_send_checklist_default_protect_content(
        self, default_bot, monkeypatch, passed_value, expected_value
    ):
        async def make_assertion(url, request_data, *args, **kwargs):
            assert request_data.parameters.get("protect_content") is expected_value
            return Message(1, dtm.datetime.now(), Chat(1, ""), text="test").to_dict()

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        kwargs = {
            "business_connection_id": self.bci,
            "chat_id": 123,
            "checklist": InputChecklist(
                title="My Checklist",
                tasks=[InputChecklistTask(1, "Task 1")],
            ),
        }
        if passed_value is not DEFAULT_NONE:
            kwargs["protect_content"] = passed_value

        await default_bot.send_checklist(**kwargs)

    async def test_send_checklist_mutually_exclusive_reply_parameters(self, offline_bot):
        """Test that reply_to_message_id and allow_sending_without_reply are mutually exclusive
        with reply_parameters."""
        with pytest.raises(ValueError, match="`reply_to_message_id` and"):
            await offline_bot.send_checklist(
                self.bci,
                123,
                InputChecklist(title="My Checklist", tasks=[InputChecklistTask(1, "Task 1")]),
                reply_to_message_id=1,
                reply_parameters=True,
            )

        with pytest.raises(ValueError, match="`allow_sending_without_reply` and"):
            await offline_bot.send_checklist(
                self.bci,
                123,
                InputChecklist(title="My Checklist", tasks=[InputChecklistTask(1, "Task 1")]),
                allow_sending_without_reply=True,
                reply_parameters=True,
            )

    async def test_edit_message_checklist_all_args(self, offline_bot, monkeypatch):
        chat_id = 123
        message_id = 45
        checklist = InputChecklist(
            title="My Checklist",
            tasks=[InputChecklistTask(1, "Task 1"), InputChecklistTask(2, "Task 2")],
        )
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="test", callback_data="test2")]]
        )
        json_message = Message(1, dtm.datetime.now(), Chat(1, ""), text="test").to_json()

        async def make_assertions(*args, **kwargs):
            params = kwargs.get("request_data").parameters
            assert params.get("business_connection_id") == self.bci
            assert params.get("chat_id") == chat_id
            assert params.get("message_id") == message_id
            assert params.get("checklist") == checklist.to_dict()
            assert params.get("reply_markup") == reply_markup.to_dict()

            return 200, f'{{"ok": true, "result": {json_message}}}'.encode()

        monkeypatch.setattr(offline_bot.request, "do_request", make_assertions)
        obj = await offline_bot.edit_message_checklist(
            business_connection_id=self.bci,
            chat_id=chat_id,
            message_id=message_id,
            checklist=checklist,
            reply_markup=reply_markup,
        )
        assert isinstance(obj, Message)
