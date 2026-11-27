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

import pytest

from telegram import (
    Animation,
    Audio,
    BotCommand,
    Chat,
    Checklist,
    ChecklistTask,
    Contact,
    Dice,
    Document,
    ExternalReplyInfo,
    Game,
    Giveaway,
    GiveawayWinners,
    Invoice,
    LinkPreviewOptions,
    LivePhoto,
    Location,
    MessageEntity,
    MessageOriginUser,
    PaidMediaInfo,
    PaidMediaPreview,
    PhotoSize,
    Poll,
    PollOption,
    ReplyParameters,
    Sticker,
    Story,
    TextQuote,
    User,
    Venue,
    Video,
    VideoNote,
    Voice,
)
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def external_reply_info():
    return ExternalReplyInfo(
        origin=ExternalReplyInfoTestBase.origin,
        chat=ExternalReplyInfoTestBase.chat,
        message_id=ExternalReplyInfoTestBase.message_id,
        link_preview_options=ExternalReplyInfoTestBase.link_preview_options,
        giveaway=ExternalReplyInfoTestBase.giveaway,
        paid_media=ExternalReplyInfoTestBase.paid_media,
        checklist=ExternalReplyInfoTestBase.checklist,
        live_photo=ExternalReplyInfoTestBase.live_photo,
        animation=ExternalReplyInfoTestBase.animation,
        audio=ExternalReplyInfoTestBase.audio,
        document=ExternalReplyInfoTestBase.document,
        photo=ExternalReplyInfoTestBase.photo,
        sticker=ExternalReplyInfoTestBase.sticker,
        story=ExternalReplyInfoTestBase.story,
        video=ExternalReplyInfoTestBase.video,
        video_note=ExternalReplyInfoTestBase.video_note,
        voice=ExternalReplyInfoTestBase.voice,
        has_media_spoiler=ExternalReplyInfoTestBase.has_media_spoiler,
        contact=ExternalReplyInfoTestBase.contact,
        dice=ExternalReplyInfoTestBase.dice,
        game=ExternalReplyInfoTestBase.game,
        giveaway_winners=ExternalReplyInfoTestBase.giveaway_winners,
        invoice=ExternalReplyInfoTestBase.invoice,
        location=ExternalReplyInfoTestBase.location,
        poll=ExternalReplyInfoTestBase.poll,
        venue=ExternalReplyInfoTestBase.venue,
    )


class ExternalReplyInfoTestBase:
    origin = MessageOriginUser(
        dtm.datetime.now(dtm.UTC).replace(microsecond=0), User(1, "user", False)
    )
    chat = Chat(1, Chat.SUPERGROUP)
    message_id = 123
    link_preview_options = LinkPreviewOptions(True)
    giveaway = Giveaway(
        (Chat(1, Chat.CHANNEL), Chat(2, Chat.SUPERGROUP)),
        dtm.datetime.now(dtm.UTC).replace(microsecond=0),
        1,
    )
    paid_media = PaidMediaInfo(5, [PaidMediaPreview(10, 10, 10)])
    checklist = Checklist(
        title="Checklist Title",
        tasks=[
            ChecklistTask(text="Item 1", id=1),
            ChecklistTask(text="Item 2", id=2),
        ],
    )
    live_photo = LivePhoto(
        file_id="file_id",
        file_unique_id="file_unique_id",
        width=100,
        height=100,
        duration=dtm.timedelta(seconds=10),
        photo=[],
        mime_type="image/jpeg",
        file_size=1024,
    )
    animation = Animation("animation_id", "animation_unique_id", 320, 180, 1)
    audio = Audio("audio_id", "audio_unique_id", 42)
    document = Document("document_id", "document_unique_id")
    photo = [PhotoSize("photo_id", "photo_unique_id", 640, 360)]
    sticker = Sticker("sticker_id", "sticker_unique_id", 512, 512, False, False, Sticker.REGULAR)
    story = Story(Chat(3, Chat.CHANNEL), 4)
    video = Video("video_id", "video_unique_id", 640, 360, 5)
    video_note = VideoNote("video_note_id", "video_note_unique_id", 240, 3)
    voice = Voice("voice_id", "voice_unique_id", 2)
    has_media_spoiler = True
    contact = Contact("+11234567890", "first name")
    dice = Dice(5, Dice.DICE)
    game = Game("game title", "game description", [PhotoSize("game_id", "game_unique_id", 1, 1)])
    giveaway_winners = GiveawayWinners(
        Chat(5, Chat.CHANNEL),
        6,
        dtm.datetime.now(dtm.UTC).replace(microsecond=0),
        1,
        [User(7, "winner", False)],
    )
    invoice = Invoice("invoice title", "invoice description", "start_parameter", "EUR", 100)
    location = Location(13.4, 52.5)
    poll = Poll(
        id="poll_id",
        question="poll question",
        options=[
            PollOption(text="option 1", voter_count=1, persistent_id="0"),
            PollOption(text="option 2", voter_count=0, persistent_id="1"),
        ],
        total_voter_count=1,
        is_closed=False,
        is_anonymous=True,
        type=Poll.REGULAR,
        allows_multiple_answers=False,
        allows_revoting=True,
        members_only=False,
    )
    venue = Venue(Location(13.4, 52.5), "venue title", "venue address")


class TestExternalReplyInfoWithoutRequest(ExternalReplyInfoTestBase, DeserializationTestBase):
    de_json_class = ExternalReplyInfo

    @pytest.fixture
    def de_json_dict(self):
        return {
            "origin": self.origin.to_dict(),
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "link_preview_options": self.link_preview_options.to_dict(),
            "giveaway": self.giveaway.to_dict(),
            "paid_media": self.paid_media.to_dict(),
            "checklist": self.checklist.to_dict(),
            "live_photo": self.live_photo.to_dict(),
            "animation": self.animation.to_dict(),
            "audio": self.audio.to_dict(),
            "document": self.document.to_dict(),
            "photo": [photo.to_dict() for photo in self.photo],
            "sticker": self.sticker.to_dict(),
            "story": self.story.to_dict(),
            "video": self.video.to_dict(),
            "video_note": self.video_note.to_dict(),
            "voice": self.voice.to_dict(),
            "has_media_spoiler": self.has_media_spoiler,
            "contact": self.contact.to_dict(),
            "dice": self.dice.to_dict(),
            "game": self.game.to_dict(),
            "giveaway_winners": self.giveaway_winners.to_dict(),
            "invoice": self.invoice.to_dict(),
            "location": self.location.to_dict(),
            "poll": self.poll.to_dict(),
            "venue": self.venue.to_dict(),
        }

    def test_slot_behaviour(self, external_reply_info):
        for attr in external_reply_info.__slots__:
            assert getattr(external_reply_info, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(external_reply_info)) == len(set(mro_slots(external_reply_info))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot, de_json_dict):
        external_reply_info = ExternalReplyInfo.de_json(de_json_dict, offline_bot)
        assert external_reply_info.api_kwargs == {}

        assert external_reply_info.origin == self.origin
        assert external_reply_info.chat == self.chat
        assert external_reply_info.message_id == self.message_id
        assert external_reply_info.link_preview_options == self.link_preview_options
        assert external_reply_info.giveaway == self.giveaway
        assert external_reply_info.paid_media == self.paid_media
        assert external_reply_info.checklist == self.checklist
        assert external_reply_info.live_photo == self.live_photo
        assert external_reply_info.animation == self.animation
        assert external_reply_info.audio == self.audio
        assert external_reply_info.document == self.document
        assert external_reply_info.photo == tuple(self.photo)
        assert external_reply_info.sticker == self.sticker
        assert external_reply_info.story == self.story
        assert external_reply_info.video == self.video
        assert external_reply_info.video_note == self.video_note
        assert external_reply_info.voice == self.voice
        assert external_reply_info.has_media_spoiler == self.has_media_spoiler
        assert external_reply_info.contact == self.contact
        assert external_reply_info.dice == self.dice
        assert external_reply_info.game == self.game
        assert external_reply_info.giveaway_winners == self.giveaway_winners
        assert external_reply_info.invoice == self.invoice
        assert external_reply_info.location == self.location
        assert external_reply_info.poll == self.poll
        assert external_reply_info.venue == self.venue

    def test_to_dict(self, external_reply_info):
        ext_reply_info_dict = external_reply_info.to_dict()

        assert isinstance(ext_reply_info_dict, dict)
        assert ext_reply_info_dict["origin"] == self.origin.to_dict()
        assert ext_reply_info_dict["chat"] == self.chat.to_dict()
        assert ext_reply_info_dict["message_id"] == self.message_id
        assert ext_reply_info_dict["link_preview_options"] == self.link_preview_options.to_dict()
        assert ext_reply_info_dict["giveaway"] == self.giveaway.to_dict()
        assert ext_reply_info_dict["paid_media"] == self.paid_media.to_dict()
        assert ext_reply_info_dict["checklist"] == self.checklist.to_dict()
        assert ext_reply_info_dict["live_photo"] == self.live_photo.to_dict()
        assert ext_reply_info_dict["animation"] == self.animation.to_dict()
        assert ext_reply_info_dict["audio"] == self.audio.to_dict()
        assert ext_reply_info_dict["document"] == self.document.to_dict()
        assert ext_reply_info_dict["photo"] == [photo.to_dict() for photo in self.photo]
        assert ext_reply_info_dict["sticker"] == self.sticker.to_dict()
        assert ext_reply_info_dict["story"] == self.story.to_dict()
        assert ext_reply_info_dict["video"] == self.video.to_dict()
        assert ext_reply_info_dict["video_note"] == self.video_note.to_dict()
        assert ext_reply_info_dict["voice"] == self.voice.to_dict()
        assert ext_reply_info_dict["has_media_spoiler"] == self.has_media_spoiler
        assert ext_reply_info_dict["contact"] == self.contact.to_dict()
        assert ext_reply_info_dict["dice"] == self.dice.to_dict()
        assert ext_reply_info_dict["game"] == self.game.to_dict()
        assert ext_reply_info_dict["giveaway_winners"] == self.giveaway_winners.to_dict()
        assert ext_reply_info_dict["invoice"] == self.invoice.to_dict()
        assert ext_reply_info_dict["location"] == self.location.to_dict()
        assert ext_reply_info_dict["poll"] == self.poll.to_dict()
        assert ext_reply_info_dict["venue"] == self.venue.to_dict()

    def test_equality(self, external_reply_info):
        a = external_reply_info
        b = ExternalReplyInfo(origin=self.origin)
        c = ExternalReplyInfo(
            origin=MessageOriginUser(
                dtm.datetime.now(dtm.UTC).replace(tzinfo=None), User(2, "user", False)
            )
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
        text=TextQuoteTestBase.text,
        position=TextQuoteTestBase.position,
        entities=TextQuoteTestBase.entities,
        is_manual=TextQuoteTestBase.is_manual,
    )


class TextQuoteTestBase:
    text = "text"
    position = 1
    entities = [
        MessageEntity(MessageEntity.MENTION, 1, 2),
        MessageEntity(MessageEntity.EMAIL, 3, 4),
    ]
    is_manual = True


class TestTextQuoteWithoutRequest(TextQuoteTestBase, DeserializationTestBase):
    de_json_class = TextQuote

    @pytest.fixture
    def de_json_dict(self):
        return {
            "text": self.text,
            "position": self.position,
            "entities": [entity.to_dict() for entity in self.entities],
            "is_manual": self.is_manual,
        }

    def test_slot_behaviour(self, text_quote):
        for attr in text_quote.__slots__:
            assert getattr(text_quote, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(text_quote)) == len(set(mro_slots(text_quote))), "duplicate slot"

    def test_de_json(self, offline_bot, de_json_dict):
        text_quote = TextQuote.de_json(de_json_dict, offline_bot)
        assert text_quote.api_kwargs == {}

        assert text_quote.text == self.text
        assert text_quote.position == self.position
        assert text_quote.entities == tuple(self.entities)
        assert text_quote.is_manual == self.is_manual

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
        message_id=ReplyParametersTestBase.message_id,
        chat_id=ReplyParametersTestBase.chat_id,
        allow_sending_without_reply=ReplyParametersTestBase.allow_sending_without_reply,
        quote=ReplyParametersTestBase.quote,
        quote_parse_mode=ReplyParametersTestBase.quote_parse_mode,
        quote_entities=ReplyParametersTestBase.quote_entities,
        quote_position=ReplyParametersTestBase.quote_position,
        checklist_task_id=ReplyParametersTestBase.checklist_task_id,
        poll_option_id=ReplyParametersTestBase.poll_option_id,
    )


class ReplyParametersTestBase:
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
    checklist_task_id = 9
    poll_option_id = "213"


class TestReplyParametersWithoutRequest(ReplyParametersTestBase):
    def test_slot_behaviour(self, reply_parameters):
        for attr in reply_parameters.__slots__:
            assert getattr(reply_parameters, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(reply_parameters)) == len(set(mro_slots(reply_parameters))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot):
        json_dict = {
            "message_id": self.message_id,
            "chat_id": self.chat_id,
            "allow_sending_without_reply": self.allow_sending_without_reply,
            "quote": self.quote,
            "quote_parse_mode": self.quote_parse_mode,
            "quote_entities": [entity.to_dict() for entity in self.quote_entities],
            "quote_position": self.quote_position,
            "checklist_task_id": self.checklist_task_id,
            "poll_option_id": self.poll_option_id,
        }

        reply_parameters = ReplyParameters.de_json(json_dict, offline_bot)
        assert reply_parameters.api_kwargs == {}

        assert reply_parameters.message_id == self.message_id
        assert reply_parameters.chat_id == self.chat_id
        assert reply_parameters.allow_sending_without_reply == self.allow_sending_without_reply
        assert reply_parameters.quote == self.quote
        assert reply_parameters.quote_parse_mode == self.quote_parse_mode
        assert reply_parameters.quote_entities == tuple(self.quote_entities)
        assert reply_parameters.quote_position == self.quote_position
        assert reply_parameters.checklist_task_id == self.checklist_task_id
        assert reply_parameters.poll_option_id == self.poll_option_id

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
        assert reply_parameters_dict["checklist_task_id"] == self.checklist_task_id
        assert reply_parameters_dict["poll_option_id"] == self.poll_option_id

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
