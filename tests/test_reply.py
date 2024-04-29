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

import datetime as dtm

import pytest

from telegram import (
    BotCommand,
    Chat,
    ExternalReplyInfo,
    Giveaway,
    LinkPreviewOptions,
    MessageEntity,
    MessageOriginUser,
    ReplyParameters,
    TextQuote,
    User,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def external_reply_info():
    return ExternalReplyInfo(
        origin=TestExternalReplyInfoBase.origin,
        chat=TestExternalReplyInfoBase.chat,
        message_id=TestExternalReplyInfoBase.message_id,
        link_preview_options=TestExternalReplyInfoBase.link_preview_options,
        giveaway=TestExternalReplyInfoBase.giveaway,
    )


class TestExternalReplyInfoBase:
    origin = MessageOriginUser(
        dtm.datetime.now(dtm.timezone.utc).replace(microsecond=0), User(1, "user", False)
    )
    chat = Chat(1, Chat.SUPERGROUP)
    message_id = 123
    link_preview_options = LinkPreviewOptions(True)
    giveaway = Giveaway(
        (Chat(1, Chat.CHANNEL), Chat(2, Chat.SUPERGROUP)),
        dtm.datetime.now(dtm.timezone.utc).replace(microsecond=0),
        1,
    )


class TestExternalReplyInfoWithoutRequest(TestExternalReplyInfoBase):
    def test_slot_behaviour(self, external_reply_info):
        for attr in external_reply_info.__slots__:
            assert getattr(external_reply_info, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(external_reply_info)) == len(
            set(mro_slots(external_reply_info))
        ), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "origin": self.origin.to_dict(),
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "link_preview_options": self.link_preview_options.to_dict(),
            "giveaway": self.giveaway.to_dict(),
        }

        external_reply_info = ExternalReplyInfo.de_json(json_dict, bot)
        assert external_reply_info.api_kwargs == {}

        assert external_reply_info.origin == self.origin
        assert external_reply_info.chat == self.chat
        assert external_reply_info.message_id == self.message_id
        assert external_reply_info.link_preview_options == self.link_preview_options
        assert external_reply_info.giveaway == self.giveaway

        assert ExternalReplyInfo.de_json(None, bot) is None

    def test_to_dict(self, external_reply_info):
        ext_reply_info_dict = external_reply_info.to_dict()

        assert isinstance(ext_reply_info_dict, dict)
        assert ext_reply_info_dict["origin"] == self.origin.to_dict()
        assert ext_reply_info_dict["chat"] == self.chat.to_dict()
        assert ext_reply_info_dict["message_id"] == self.message_id
        assert ext_reply_info_dict["link_preview_options"] == self.link_preview_options.to_dict()
        assert ext_reply_info_dict["giveaway"] == self.giveaway.to_dict()

    def test_equality(self, external_reply_info):
        a = external_reply_info
        b = ExternalReplyInfo(origin=self.origin)
        c = ExternalReplyInfo(
            origin=MessageOriginUser(dtm.datetime.utcnow(), User(2, "user", False))
        )

        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture(scope="module")
def text_quote():
    return TextQuote(
        text=TestTextQuoteBase.text,
        position=TestTextQuoteBase.position,
        entities=TestTextQuoteBase.entities,
        is_manual=TestTextQuoteBase.is_manual,
    )


class TestTextQuoteBase:
    text = "text"
    position = 1
    entities = [
        MessageEntity(MessageEntity.MENTION, 1, 2),
        MessageEntity(MessageEntity.EMAIL, 3, 4),
    ]
    is_manual = True


class TestTextQuoteWithoutRequest(TestTextQuoteBase):
    def test_slot_behaviour(self, text_quote):
        for attr in text_quote.__slots__:
            assert getattr(text_quote, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(text_quote)) == len(set(mro_slots(text_quote))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "text": self.text,
            "position": self.position,
            "entities": [entity.to_dict() for entity in self.entities],
            "is_manual": self.is_manual,
        }

        text_quote = TextQuote.de_json(json_dict, bot)
        assert text_quote.api_kwargs == {}

        assert text_quote.text == self.text
        assert text_quote.position == self.position
        assert text_quote.entities == tuple(self.entities)
        assert text_quote.is_manual == self.is_manual

        assert TextQuote.de_json(None, bot) is None

    def test_to_dict(self, text_quote):
        text_quote_dict = text_quote.to_dict()

        assert isinstance(text_quote_dict, dict)
        assert text_quote_dict["text"] == self.text
        assert text_quote_dict["position"] == self.position
        assert text_quote_dict["entities"] == [entity.to_dict() for entity in self.entities]
        assert text_quote_dict["is_manual"] == self.is_manual

    def test_equality(self, text_quote):
        a = text_quote
        b = TextQuote(text=self.text, position=self.position)
        c = TextQuote(text="foo", position=self.position)
        d = TextQuote(text=self.text, position=7)

        e = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def reply_parameters():
    return ReplyParameters(
        message_id=TestReplyParametersBase.message_id,
        chat_id=TestReplyParametersBase.chat_id,
        allow_sending_without_reply=TestReplyParametersBase.allow_sending_without_reply,
        quote=TestReplyParametersBase.quote,
        quote_parse_mode=TestReplyParametersBase.quote_parse_mode,
        quote_entities=TestReplyParametersBase.quote_entities,
        quote_position=TestReplyParametersBase.quote_position,
    )


class TestReplyParametersBase:
    message_id = 123
    chat_id = 456
    allow_sending_without_reply = True
    quote = "foo"
    quote_parse_mode = "html"
    quote_entities = [
        MessageEntity(MessageEntity.MENTION, 1, 2),
        MessageEntity(MessageEntity.EMAIL, 3, 4),
    ]
    quote_position = 5


class TestReplyParametersWithoutRequest(TestReplyParametersBase):
    def test_slot_behaviour(self, reply_parameters):
        for attr in reply_parameters.__slots__:
            assert getattr(reply_parameters, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(reply_parameters)) == len(
            set(mro_slots(reply_parameters))
        ), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "message_id": self.message_id,
            "chat_id": self.chat_id,
            "allow_sending_without_reply": self.allow_sending_without_reply,
            "quote": self.quote,
            "quote_parse_mode": self.quote_parse_mode,
            "quote_entities": [entity.to_dict() for entity in self.quote_entities],
            "quote_position": self.quote_position,
        }

        reply_parameters = ReplyParameters.de_json(json_dict, bot)
        assert reply_parameters.api_kwargs == {}

        assert reply_parameters.message_id == self.message_id
        assert reply_parameters.chat_id == self.chat_id
        assert reply_parameters.allow_sending_without_reply == self.allow_sending_without_reply
        assert reply_parameters.quote == self.quote
        assert reply_parameters.quote_parse_mode == self.quote_parse_mode
        assert reply_parameters.quote_entities == tuple(self.quote_entities)
        assert reply_parameters.quote_position == self.quote_position

        assert ReplyParameters.de_json(None, bot) is None

    def test_to_dict(self, reply_parameters):
        reply_parameters_dict = reply_parameters.to_dict()

        assert isinstance(reply_parameters_dict, dict)
        assert reply_parameters_dict["message_id"] == self.message_id
        assert reply_parameters_dict["chat_id"] == self.chat_id
        assert (
            reply_parameters_dict["allow_sending_without_reply"]
            == self.allow_sending_without_reply
        )
        assert reply_parameters_dict["quote"] == self.quote
        assert reply_parameters_dict["quote_parse_mode"] == self.quote_parse_mode
        assert reply_parameters_dict["quote_entities"] == [
            entity.to_dict() for entity in self.quote_entities
        ]
        assert reply_parameters_dict["quote_position"] == self.quote_position

    def test_equality(self, reply_parameters):
        a = reply_parameters
        b = ReplyParameters(message_id=self.message_id)
        c = ReplyParameters(message_id=7)

        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
