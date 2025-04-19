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

from telegram import BusinessConnection, User
from telegram._files.sticker import Sticker
from telegram._gifts import AcceptedGiftTypes, Gift
from telegram._ownedgift import OwnedGiftRegular, OwnedGifts
from telegram._utils.datetime import UTC


class BusinessMethodsTestBase:
    bci = "42"


class TestBusinessMethodsWithoutRequest(BusinessMethodsTestBase):
    async def test_get_business_connection(self, offline_bot, monkeypatch):
        user = User(1, "first", False)
        user_chat_id = 1
        date = dtm.datetime.utcnow()
        can_reply = True
        is_enabled = True
        bc = BusinessConnection(
            self.bci, user, user_chat_id, date, can_reply, is_enabled
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
