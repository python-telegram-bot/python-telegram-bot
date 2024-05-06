#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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

import asyncio

import pytest

from telegram import Contact, ReplyParameters, Voice
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.request import RequestData
from tests.auxil.build_messages import make_message
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def contact():
    return Contact(
        TestContactBase.phone_number,
        TestContactBase.first_name,
        TestContactBase.last_name,
        TestContactBase.user_id,
    )


class TestContactBase:
    phone_number = "+11234567890"
    first_name = "Leandro"
    last_name = "Toledo"
    user_id = 23


class TestContactWithoutRequest(TestContactBase):
    def test_slot_behaviour(self, contact):
        for attr in contact.__slots__:
            assert getattr(contact, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(contact)) == len(set(mro_slots(contact))), "duplicate slot"

    def test_de_json_required(self, bot):
        json_dict = {"phone_number": self.phone_number, "first_name": self.first_name}
        contact = Contact.de_json(json_dict, bot)
        assert contact.api_kwargs == {}

        assert contact.phone_number == self.phone_number
        assert contact.first_name == self.first_name

    def test_de_json_all(self, bot):
        json_dict = {
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_id": self.user_id,
        }
        contact = Contact.de_json(json_dict, bot)
        assert contact.api_kwargs == {}

        assert contact.phone_number == self.phone_number
        assert contact.first_name == self.first_name
        assert contact.last_name == self.last_name
        assert contact.user_id == self.user_id

    def test_to_dict(self, contact):
        contact_dict = contact.to_dict()

        assert isinstance(contact_dict, dict)
        assert contact_dict["phone_number"] == contact.phone_number
        assert contact_dict["first_name"] == contact.first_name
        assert contact_dict["last_name"] == contact.last_name
        assert contact_dict["user_id"] == contact.user_id

    def test_equality(self):
        a = Contact(self.phone_number, self.first_name)
        b = Contact(self.phone_number, self.first_name)
        c = Contact(self.phone_number, "")
        d = Contact("", self.first_name)
        e = Voice("", "unique_id", 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    async def test_send_contact_without_required(self, bot, chat_id):
        with pytest.raises(ValueError, match="Either contact or phone_number and first_name"):
            await bot.send_contact(chat_id=chat_id)

    async def test_send_mutually_exclusive(self, bot, chat_id, contact):
        with pytest.raises(ValueError, match="Not both"):
            await bot.send_contact(
                chat_id=chat_id,
                contact=contact,
                phone_number=contact.phone_number,
                first_name=contact.first_name,
            )

    async def test_send_with_contact(self, monkeypatch, bot, chat_id, contact):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            phone = data["phone_number"] == contact.phone_number
            first = data["first_name"] == contact.first_name
            last = data["last_name"] == contact.last_name
            return phone and first and last

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.send_contact(contact=contact, chat_id=chat_id)

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_contact_default_quote_parse_mode(
        self, default_bot, chat_id, contact, custom, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            assert request_data.parameters["reply_parameters"].get("quote_parse_mode") == (
                custom or default_bot.defaults.quote_parse_mode
            )
            return make_message("dummy reply").to_dict()

        kwargs = {"message_id": 1}
        if custom is not None:
            kwargs["quote_parse_mode"] = custom

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        await default_bot.send_contact(
            chat_id, contact=contact, reply_parameters=ReplyParameters(**kwargs)
        )


class TestContactWithRequest(TestContactBase):
    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_contact_default_allow_sending_without_reply(
        self, default_bot, chat_id, contact, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_contact(
                chat_id,
                contact=contact,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_contact(
                chat_id, contact=contact, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to be replied not found"):
                await default_bot.send_contact(
                    chat_id, contact=contact, reply_to_message_id=reply_to_message.message_id
                )

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_contact_default_protect_content(self, chat_id, default_bot, contact):
        tasks = asyncio.gather(
            default_bot.send_contact(chat_id, contact=contact),
            default_bot.send_contact(chat_id, contact=contact, protect_content=False),
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content
