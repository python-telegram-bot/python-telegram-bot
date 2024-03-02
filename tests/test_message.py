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
from copy import copy
from datetime import datetime

import pytest

from telegram import (
    Animation,
    Audio,
    Bot,
    Chat,
    ChatBoostAdded,
    ChatShared,
    Contact,
    Dice,
    Document,
    ExternalReplyInfo,
    Game,
    Giveaway,
    GiveawayCompleted,
    GiveawayCreated,
    GiveawayWinners,
    Invoice,
    LinkPreviewOptions,
    Location,
    Message,
    MessageAutoDeleteTimerChanged,
    MessageEntity,
    MessageOriginChat,
    PassportData,
    PhotoSize,
    Poll,
    PollOption,
    ProximityAlertTriggered,
    ReplyParameters,
    Sticker,
    Story,
    SuccessfulPayment,
    TextQuote,
    Update,
    User,
    UsersShared,
    Venue,
    Video,
    VideoChatEnded,
    VideoChatParticipantsInvited,
    VideoChatScheduled,
    VideoChatStarted,
    VideoNote,
    Voice,
    WebAppData,
)
from telegram._utils.datetime import UTC
from telegram.constants import ChatAction, ParseMode
from telegram.ext import Defaults
from telegram.warnings import PTBDeprecationWarning
from tests._passport.test_passport import RAW_PASSPORT_DATA
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.auxil.build_messages import make_message
from tests.auxil.pytest_classes import PytestExtBot, PytestMessage
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def message(bot):
    message = PytestMessage(
        message_id=TestMessageBase.id_,
        date=TestMessageBase.date,
        chat=copy(TestMessageBase.chat),
        from_user=copy(TestMessageBase.from_user),
    )
    message.set_bot(bot)
    message._unfreeze()
    message.chat._unfreeze()
    message.from_user._unfreeze()
    return message


@pytest.fixture(
    params=[
        {
            "reply_to_message": Message(
                50, datetime.utcnow(), Chat(13, "channel"), User(9, "i", False)
            )
        },
        {"edit_date": datetime.utcnow()},
        {
            "text": "a text message",
            "entities": [MessageEntity("bold", 10, 4), MessageEntity("italic", 16, 7)],
        },
        {
            "caption": "A message caption",
            "caption_entities": [MessageEntity("bold", 1, 1), MessageEntity("text_link", 4, 3)],
        },
        {"audio": Audio("audio_id", "unique_id", 12), "caption": "audio_file"},
        {"document": Document("document_id", "unique_id"), "caption": "document_file"},
        {
            "animation": Animation("animation_id", "unique_id", 30, 30, 1),
            "caption": "animation_file",
        },
        {
            "game": Game(
                "my_game",
                "just my game",
                [
                    PhotoSize("game_photo_id", "unique_id", 30, 30),
                ],
            )
        },
        {"photo": [PhotoSize("photo_id", "unique_id", 50, 50)], "caption": "photo_file"},
        {"sticker": Sticker("sticker_id", "unique_id", 50, 50, True, False, Sticker.REGULAR)},
        {"story": Story(Chat(1, Chat.PRIVATE), 0)},
        {"video": Video("video_id", "unique_id", 12, 12, 12), "caption": "video_file"},
        {"voice": Voice("voice_id", "unique_id", 5)},
        {"video_note": VideoNote("video_note_id", "unique_id", 20, 12)},
        {"new_chat_members": [User(55, "new_user", False)]},
        {"contact": Contact("phone_numner", "contact_name")},
        {"location": Location(-23.691288, 46.788279)},
        {"venue": Venue(Location(-23.691288, 46.788279), "some place", "right here")},
        {"left_chat_member": User(33, "kicked", False)},
        {"new_chat_title": "new title"},
        {"new_chat_photo": [PhotoSize("photo_id", "unique_id", 50, 50)]},
        {"delete_chat_photo": True},
        {"group_chat_created": True},
        {"supergroup_chat_created": True},
        {"channel_chat_created": True},
        {"message_auto_delete_timer_changed": MessageAutoDeleteTimerChanged(42)},
        {"migrate_to_chat_id": -12345},
        {"migrate_from_chat_id": -54321},
        {
            "pinned_message": Message(
                7, datetime.utcnow(), Chat(13, "channel"), User(9, "i", False)
            )
        },
        {"invoice": Invoice("my invoice", "invoice", "start", "EUR", 243)},
        {
            "successful_payment": SuccessfulPayment(
                "EUR", 243, "payload", "charge_id", "provider_id", order_info={}
            )
        },
        {"connected_website": "http://example.com/"},
        {"author_signature": "some_author_sign"},
        {
            "photo": [PhotoSize("photo_id", "unique_id", 50, 50)],
            "caption": "photo_file",
            "media_group_id": 1234443322222,
        },
        {"passport_data": PassportData.de_json(RAW_PASSPORT_DATA, None)},
        {
            "poll": Poll(
                id="abc",
                question="What is this?",
                options=[PollOption(text="a", voter_count=1), PollOption(text="b", voter_count=2)],
                is_closed=False,
                total_voter_count=0,
                is_anonymous=False,
                type=Poll.REGULAR,
                allows_multiple_answers=True,
                explanation_entities=[],
            )
        },
        {
            "text": "a text message",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "start", "url": "http://google.com"},
                        {"text": "next", "callback_data": "abcd"},
                    ],
                    [{"text": "Cancel", "callback_data": "Cancel"}],
                ]
            },
        },
        {"dice": Dice(4, "🎲")},
        {"via_bot": User(9, "A_Bot", True)},
        {
            "proximity_alert_triggered": ProximityAlertTriggered(
                User(1, "John", False), User(2, "Doe", False), 42
            )
        },
        {"video_chat_scheduled": VideoChatScheduled(datetime.utcnow())},
        {"video_chat_started": VideoChatStarted()},
        {"video_chat_ended": VideoChatEnded(100)},
        {
            "video_chat_participants_invited": VideoChatParticipantsInvited(
                [User(1, "Rem", False), User(2, "Emilia", False)]
            )
        },
        {"sender_chat": Chat(-123, "discussion_channel")},
        {"is_automatic_forward": True},
        {"has_protected_content": True},
        {
            "entities": [
                MessageEntity(MessageEntity.BOLD, 0, 1),
                MessageEntity(MessageEntity.TEXT_LINK, 2, 3, url="https://ptb.org"),
            ]
        },
        {"web_app_data": WebAppData("some_data", "some_button_text")},
        {"message_thread_id": 123},
        {"users_shared": UsersShared(1, [2, 3])},
        {"chat_shared": ChatShared(3, 4)},
        {
            "giveaway": Giveaway(
                chats=[Chat(1, Chat.SUPERGROUP)],
                winners_selection_date=datetime.utcnow().replace(microsecond=0),
                winner_count=5,
            )
        },
        {"giveaway_created": GiveawayCreated()},
        {
            "giveaway_winners": GiveawayWinners(
                chat=Chat(1, Chat.CHANNEL),
                giveaway_message_id=123456789,
                winners_selection_date=datetime.utcnow().replace(microsecond=0),
                winner_count=42,
                winners=[User(1, "user1", False), User(2, "user2", False)],
            )
        },
        {
            "giveaway_completed": GiveawayCompleted(
                winner_count=42,
                unclaimed_prize_count=4,
                giveaway_message=make_message(text="giveaway_message"),
            )
        },
        {
            "link_preview_options": LinkPreviewOptions(
                is_disabled=True,
                url="https://python-telegram-bot.org",
                prefer_small_media=True,
                prefer_large_media=True,
                show_above_text=True,
            )
        },
        {
            "external_reply": ExternalReplyInfo(
                MessageOriginChat(datetime.utcnow(), Chat(1, Chat.PRIVATE))
            )
        },
        {"quote": TextQuote("a text quote", 1)},
        {"forward_origin": MessageOriginChat(datetime.utcnow(), Chat(1, Chat.PRIVATE))},
        {"reply_to_story": Story(Chat(1, Chat.PRIVATE), 0)},
        {"boost_added": ChatBoostAdded(100)},
        {"sender_boost_count": 1},
    ],
    ids=[
        "reply",
        "edited",
        "text",
        "caption_entities",
        "audio",
        "document",
        "animation",
        "game",
        "photo",
        "sticker",
        "story",
        "video",
        "voice",
        "video_note",
        "new_members",
        "contact",
        "location",
        "venue",
        "left_member",
        "new_title",
        "new_photo",
        "delete_photo",
        "group_created",
        "supergroup_created",
        "channel_created",
        "message_auto_delete_timer_changed",
        "migrated_to",
        "migrated_from",
        "pinned",
        "invoice",
        "successful_payment",
        "connected_website",
        "author_signature",
        "photo_from_media_group",
        "passport_data",
        "poll",
        "reply_markup",
        "dice",
        "via_bot",
        "proximity_alert_triggered",
        "video_chat_scheduled",
        "video_chat_started",
        "video_chat_ended",
        "video_chat_participants_invited",
        "sender_chat",
        "is_automatic_forward",
        "has_protected_content",
        "entities",
        "web_app_data",
        "message_thread_id",
        "users_shared",
        "chat_shared",
        "giveaway",
        "giveaway_created",
        "giveaway_winners",
        "giveaway_completed",
        "link_preview_options",
        "external_reply",
        "quote",
        "forward_origin",
        "reply_to_story",
        "boost_added",
        "sender_boost_count",
    ],
)
def message_params(bot, request):
    message = Message(
        message_id=TestMessageBase.id_,
        from_user=TestMessageBase.from_user,
        date=TestMessageBase.date,
        chat=TestMessageBase.chat,
        **request.param,
    )
    message.set_bot(bot)
    return message


class TestMessageBase:
    id_ = 1
    from_user = User(2, "testuser", False)
    date = datetime.utcnow()
    chat = Chat(3, "private")
    test_entities = [
        {"length": 4, "offset": 10, "type": "bold"},
        {"length": 3, "offset": 16, "type": "italic"},
        {"length": 3, "offset": 20, "type": "italic"},
        {"length": 4, "offset": 25, "type": "code"},
        {"length": 5, "offset": 31, "type": "text_link", "url": "http://github.com/ab_"},
        {
            "length": 12,
            "offset": 38,
            "type": "text_mention",
            "user": User(123456789, "mentioned user", False),
        },
        {"length": 3, "offset": 55, "type": "pre", "language": "python"},
        {"length": 21, "offset": 60, "type": "url"},
    ]
    test_text = "Test for <bold, ita_lic, code, links, text-mention and pre. http://google.com/ab_"
    test_entities_v2 = [
        {"length": 4, "offset": 0, "type": "underline"},
        {"length": 4, "offset": 10, "type": "bold"},
        {"length": 7, "offset": 16, "type": "italic"},
        {"length": 6, "offset": 25, "type": "code"},
        {"length": 5, "offset": 33, "type": "text_link", "url": r"http://github.com/abc\)def"},
        {
            "length": 12,
            "offset": 40,
            "type": "text_mention",
            "user": User(123456789, "mentioned user", False),
        },
        {"length": 5, "offset": 57, "type": "pre"},
        {"length": 17, "offset": 64, "type": "url"},
        {"length": 41, "offset": 86, "type": "italic"},
        {"length": 29, "offset": 91, "type": "bold"},
        {"length": 9, "offset": 101, "type": "strikethrough"},
        {"length": 10, "offset": 129, "type": "pre", "language": "python"},
        {"length": 7, "offset": 141, "type": "spoiler"},
        {"length": 2, "offset": 150, "type": "custom_emoji", "custom_emoji_id": "1"},
        {"length": 34, "offset": 154, "type": "blockquote"},
        {"length": 6, "offset": 181, "type": "bold"},
    ]
    test_text_v2 = (
        r"Test for <bold, ita_lic, \`code, links, text-mention and `\pre. "
        "http://google.com and bold nested in strk>trgh nested in italic. Python pre. Spoiled. "
        "👍.\nMultiline\nblock quote\nwith nested."
    )
    test_message = Message(
        message_id=1,
        from_user=None,
        date=None,
        chat=None,
        text=test_text,
        entities=[MessageEntity(**e) for e in test_entities],
        caption=test_text,
        caption_entities=[MessageEntity(**e) for e in test_entities],
    )
    test_message_v2 = Message(
        message_id=1,
        from_user=None,
        date=None,
        chat=None,
        text=test_text_v2,
        entities=[MessageEntity(**e) for e in test_entities_v2],
        caption=test_text_v2,
        caption_entities=[MessageEntity(**e) for e in test_entities_v2],
    )


class TestMessageWithoutRequest(TestMessageBase):
    @staticmethod
    async def check_quote_parsing(
        message: Message, method, bot_method_name: str, args, monkeypatch
    ):
        """Used in testing reply_* below. Makes sure that quote and do_quote are handled
        correctly
        """
        with pytest.raises(ValueError, match="`quote` and `do_quote` are mutually exclusive"):
            await method(*args, quote=True, do_quote=True)

        with pytest.warns(PTBDeprecationWarning, match="`quote` parameter is deprecated"):
            await method(*args, quote=True)

        with pytest.raises(
            ValueError,
            match="`reply_to_message_id` and `reply_parameters` are mutually exclusive.",
        ):
            await method(*args, reply_to_message_id=42, reply_parameters=42)

        async def make_assertion(*args, **kwargs):
            return kwargs.get("chat_id"), kwargs.get("reply_parameters")

        monkeypatch.setattr(message.get_bot(), bot_method_name, make_assertion)

        for param in ("quote", "do_quote"):
            chat_id, reply_parameters = await method(*args, **{param: True})
            if chat_id != message.chat.id:
                pytest.fail(f"chat_id is {chat_id} but should be {message.chat.id}")
            if reply_parameters is None or reply_parameters.message_id != message.message_id:
                pytest.fail(
                    f"reply_parameters is {reply_parameters} but should be {message.message_id}"
                )

        input_chat_id = object()
        input_reply_parameters = ReplyParameters(message_id=1, chat_id=42)
        chat_id, reply_parameters = await method(
            *args, do_quote={"chat_id": input_chat_id, "reply_parameters": input_reply_parameters}
        )
        if chat_id is not input_chat_id:
            pytest.fail(f"chat_id is {chat_id} but should be {chat_id}")
        if reply_parameters is not input_reply_parameters:
            pytest.fail(f"reply_parameters is {reply_parameters} but should be {reply_parameters}")

        input_parameters_2 = ReplyParameters(message_id=2, chat_id=43)
        chat_id, reply_parameters = await method(
            *args,
            reply_parameters=input_parameters_2,
            # passing these here to make sure that `reply_parameters` has higher priority
            do_quote={"chat_id": input_chat_id, "reply_parameters": input_reply_parameters},
        )
        if chat_id is not message.chat.id:
            pytest.fail(f"chat_id is {chat_id} but should be {message.chat.id}")
        if reply_parameters is not input_parameters_2:
            pytest.fail(
                f"reply_parameters is {reply_parameters} but should be {input_parameters_2}"
            )

        chat_id, reply_parameters = await method(
            *args,
            reply_to_message_id=42,
            # passing these here to make sure that `reply_to_message_id` has higher priority
            do_quote={"chat_id": input_chat_id, "reply_parameters": input_reply_parameters},
        )
        if chat_id != message.chat.id:
            pytest.fail(f"chat_id is {chat_id} but should be {message.chat.id}")
        if reply_parameters is None or reply_parameters.message_id != 42:
            pytest.fail(f"reply_parameters is {reply_parameters} but should be 42")

    def test_slot_behaviour(self):
        message = Message(
            message_id=TestMessageBase.id_,
            date=TestMessageBase.date,
            chat=copy(TestMessageBase.chat),
            from_user=copy(TestMessageBase.from_user),
        )
        for attr in message.__slots__:
            assert getattr(message, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(message)) == len(set(mro_slots(message))), "duplicate slot"

    def test_all_possibilities_de_json_and_to_dict(self, bot, message_params):
        new = Message.de_json(message_params.to_dict(), bot)
        assert new.api_kwargs == {}
        assert new.to_dict() == message_params.to_dict()

        # Checking that none of the attributes are dicts is a best effort approach to ensure that
        # de_json converts everything to proper classes without having to write special tests for
        # every single case
        for slot in new.__slots__:
            assert not isinstance(new[slot], dict)

    def test_de_json_localization(self, bot, raw_bot, tz_bot):
        json_dict = {
            "message_id": 12,
            "from_user": None,
            "date": int(datetime.now().timestamp()),
            "chat": None,
            "edit_date": int(datetime.now().timestamp()),
        }

        message_raw = Message.de_json(json_dict, raw_bot)
        message_bot = Message.de_json(json_dict, bot)
        message_tz = Message.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        date_offset = message_tz.date.utcoffset()
        date_tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(message_tz.date.replace(tzinfo=None))

        edit_date_offset = message_tz.edit_date.utcoffset()
        edit_date_tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            message_tz.edit_date.replace(tzinfo=None)
        )

        assert message_raw.date.tzinfo == UTC
        assert message_bot.date.tzinfo == UTC
        assert date_offset == date_tz_bot_offset

        assert message_raw.edit_date.tzinfo == UTC
        assert message_bot.edit_date.tzinfo == UTC
        assert edit_date_offset == edit_date_tz_bot_offset

    def test_de_json_api_kwargs_backward_compatibility(self, bot, message_params):
        message_dict = message_params.to_dict()
        keys = (
            "user_shared",
            "forward_from",
            "forward_from_chat",
            "forward_from_message_id",
            "forward_signature",
            "forward_sender_name",
            "forward_date",
        )
        for key in keys:
            message_dict[key] = key
        message = Message.de_json(message_dict, bot)
        assert message.api_kwargs == {key: key for key in keys}

    def test_equality(self):
        id_ = 1
        a = Message(id_, self.date, self.chat, from_user=self.from_user)
        b = Message(id_, self.date, self.chat, from_user=self.from_user)
        c = Message(id_, self.date, Chat(123, Chat.GROUP), from_user=User(0, "", False))
        d = Message(0, self.date, self.chat, from_user=self.from_user)
        e = Update(id_)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    def test_bool(self, message, recwarn):
        # Relevant as long as we override MaybeInaccessibleMessage.__bool__
        # Can be removed once that's removed
        assert bool(message) is True
        assert len(recwarn) == 0

    async def test_parse_entity(self):
        text = (
            b"\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467"
            b"\\u200d\\U0001f467\\U0001f431http://google.com"
        ).decode("unicode-escape")
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            text=text,
            entities=[entity],
        )
        assert message.parse_entity(entity) == "http://google.com"

        with pytest.raises(RuntimeError, match="Message has no"):
            Message(message_id=1, date=self.date, chat=self.chat).parse_entity(entity)

    async def test_parse_caption_entity(self):
        caption = (
            b"\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467"
            b"\\u200d\\U0001f467\\U0001f431http://google.com"
        ).decode("unicode-escape")
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            caption=caption,
            caption_entities=[entity],
        )
        assert message.parse_caption_entity(entity) == "http://google.com"

        with pytest.raises(RuntimeError, match="Message has no"):
            Message(message_id=1, date=self.date, chat=self.chat).parse_entity(entity)

    async def test_parse_entities(self):
        text = (
            b"\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467"
            b"\\u200d\\U0001f467\\U0001f431http://google.com"
        ).decode("unicode-escape")
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            text=text,
            entities=[entity_2, entity],
        )
        assert message.parse_entities(MessageEntity.URL) == {entity: "http://google.com"}
        assert message.parse_entities() == {entity: "http://google.com", entity_2: "h"}

    async def test_parse_caption_entities(self):
        text = (
            b"\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467"
            b"\\u200d\\U0001f467\\U0001f431http://google.com"
        ).decode("unicode-escape")
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            caption=text,
            caption_entities=[entity_2, entity],
        )
        assert message.parse_caption_entities(MessageEntity.URL) == {entity: "http://google.com"}
        assert message.parse_caption_entities() == {
            entity: "http://google.com",
            entity_2: "h",
        }

    def test_text_html_simple(self):
        test_html_string = (
            "<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, "
            r"<code>\`code</code>, "
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r"<pre>`\pre</pre>. http://google.com "
            "and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. "
            '<pre><code class="python">Python pre</code></pre>. '
            '<span class="tg-spoiler">Spoiled</span>. '
            '<tg-emoji emoji-id="1">👍</tg-emoji>.\n'
            "<blockquote>Multiline\nblock quote\nwith <b>nested</b>.</blockquote>"
        )
        text_html = self.test_message_v2.text_html
        assert text_html == test_html_string

    def test_text_html_empty(self, message):
        message.text = None
        message.caption = "test"
        assert message.text_html is None

    def test_text_html_urled(self):
        test_html_string = (
            "<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, "
            r"<code>\`code</code>, "
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r'<pre>`\pre</pre>. <a href="http://google.com">http://google.com</a> '
            "and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. "
            '<pre><code class="python">Python pre</code></pre>. '
            '<span class="tg-spoiler">Spoiled</span>. '
            '<tg-emoji emoji-id="1">👍</tg-emoji>.\n'
            "<blockquote>Multiline\nblock quote\nwith <b>nested</b>.</blockquote>"
        )
        text_html = self.test_message_v2.text_html_urled
        assert text_html == test_html_string

    def test_text_markdown_simple(self):
        test_md_string = (
            r"Test for <*bold*, _ita_\__lic_, `code`, "
            "[links](http://github.com/ab_), "
            "[text-mention](tg://user?id=123456789) and ```python\npre```. "
            r"http://google.com/ab\_"
        )
        text_markdown = self.test_message.text_markdown
        assert text_markdown == test_md_string

    def test_text_markdown_v2_simple(self):
        test_md_string = (
            r"__Test__ for <*bold*, _ita\_lic_, `\\\`code`, "
            "[links](http://github.com/abc\\\\\\)def), "
            "[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. "
            r"http://google\.com and _bold *nested in ~strk\>trgh~ nested in* italic_\. "
            "```python\nPython pre```\\. ||Spoiled||\\. ![👍](tg://emoji?id=1)\\.\n"
            ">Multiline\n"
            ">block quote\n"
            r">with *nested*\."
        )
        text_markdown = self.test_message_v2.text_markdown_v2
        assert text_markdown == test_md_string

    @pytest.mark.parametrize(
        "entity_type",
        [
            MessageEntity.UNDERLINE,
            MessageEntity.STRIKETHROUGH,
            MessageEntity.SPOILER,
            MessageEntity.BLOCKQUOTE,
            MessageEntity.CUSTOM_EMOJI,
        ],
    )
    def test_text_markdown_new_in_v2(self, message, entity_type):
        message.text = "test"
        message.entities = [
            MessageEntity(MessageEntity.BOLD, offset=0, length=4),
            MessageEntity(MessageEntity.ITALIC, offset=0, length=4),
        ]
        with pytest.raises(ValueError, match="Nested entities are not supported for"):
            assert message.text_markdown

        message.entities = [MessageEntity(entity_type, offset=0, length=4)]
        with pytest.raises(ValueError, match="entities are not supported for"):
            message.text_markdown

        message.entities = []

    def test_text_markdown_empty(self, message):
        message.text = None
        message.caption = "test"
        assert message.text_markdown is None
        assert message.text_markdown_v2 is None

    def test_text_markdown_urled(self):
        test_md_string = (
            r"Test for <*bold*, _ita_\__lic_, `code`, "
            "[links](http://github.com/ab_), "
            "[text-mention](tg://user?id=123456789) and ```python\npre```. "
            "[http://google.com/ab_](http://google.com/ab_)"
        )
        text_markdown = self.test_message.text_markdown_urled
        assert text_markdown == test_md_string

    def test_text_markdown_v2_urled(self):
        test_md_string = (
            r"__Test__ for <*bold*, _ita\_lic_, `\\\`code`, "
            "[links](http://github.com/abc\\\\\\)def), "
            "[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. "
            r"[http://google\.com](http://google.com) and _bold *nested in ~strk\>trgh~ "
            "nested in* italic_\\. ```python\nPython pre```\\. ||Spoiled||\\. "
            "![👍](tg://emoji?id=1)\\.\n"
            ">Multiline\n"
            ">block quote\n"
            r">with *nested*\."
        )
        text_markdown = self.test_message_v2.text_markdown_v2_urled
        assert text_markdown == test_md_string

    def test_text_html_emoji(self):
        text = b"\\U0001f469\\u200d\\U0001f469\\u200d ABC".decode("unicode-escape")
        expected = b"\\U0001f469\\u200d\\U0001f469\\u200d <b>ABC</b>".decode("unicode-escape")
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            text=text,
            entities=[bold_entity],
        )
        assert expected == message.text_html

    def test_text_markdown_emoji(self):
        text = b"\\U0001f469\\u200d\\U0001f469\\u200d ABC".decode("unicode-escape")
        expected = b"\\U0001f469\\u200d\\U0001f469\\u200d *ABC*".decode("unicode-escape")
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            1, self.date, self.chat, self.from_user, text=text, entities=[bold_entity]
        )
        assert expected == message.text_markdown

    @pytest.mark.parametrize(
        "type_",
        argvalues=[
            "text_markdown",
            "text_markdown_urled",
        ],
    )
    def test_text_custom_emoji_md_v1(self, type_, recwarn):
        text = "Look a custom emoji: 😎"
        emoji_entity = MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=21,
            length=2,
            custom_emoji_id="5472409228461217725",
        )
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            text=text,
            entities=[emoji_entity],
        )
        with pytest.raises(ValueError, match="Custom Emoji entities are not supported for"):
            getattr(message, type_)

    @pytest.mark.parametrize(
        "type_",
        argvalues=[
            "text_markdown_v2",
            "text_markdown_v2_urled",
        ],
    )
    def test_text_custom_emoji_md_v2(self, type_):
        text = "Look a custom emoji: 😎"
        expected = "Look a custom emoji: ![😎](tg://emoji?id=5472409228461217725)"
        emoji_entity = MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=21,
            length=2,
            custom_emoji_id="5472409228461217725",
        )
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            text=text,
            entities=[emoji_entity],
        )
        assert expected == message[type_]

    @pytest.mark.parametrize(
        "type_",
        argvalues=[
            "text_html",
            "text_html_urled",
        ],
    )
    def test_text_custom_emoji_html(self, type_):
        text = "Look a custom emoji: 😎"
        expected = 'Look a custom emoji: <tg-emoji emoji-id="5472409228461217725">😎</tg-emoji>'
        emoji_entity = MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=21,
            length=2,
            custom_emoji_id="5472409228461217725",
        )
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            text=text,
            entities=[emoji_entity],
        )
        assert expected == message[type_]

    def test_caption_html_simple(self):
        test_html_string = (
            "<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, "
            r"<code>\`code</code>, "
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r"<pre>`\pre</pre>. http://google.com "
            "and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. "
            '<pre><code class="python">Python pre</code></pre>. '
            '<span class="tg-spoiler">Spoiled</span>. '
            '<tg-emoji emoji-id="1">👍</tg-emoji>.\n'
            "<blockquote>Multiline\nblock quote\nwith <b>nested</b>.</blockquote>"
        )
        caption_html = self.test_message_v2.caption_html
        assert caption_html == test_html_string

    def test_caption_html_empty(self, message):
        message.text = "test"
        message.caption = None
        assert message.caption_html is None

    def test_caption_html_urled(self):
        test_html_string = (
            "<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, "
            r"<code>\`code</code>, "
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r'<pre>`\pre</pre>. <a href="http://google.com">http://google.com</a> '
            "and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. "
            '<pre><code class="python">Python pre</code></pre>. '
            '<span class="tg-spoiler">Spoiled</span>. '
            '<tg-emoji emoji-id="1">👍</tg-emoji>.\n'
            "<blockquote>Multiline\nblock quote\nwith <b>nested</b>.</blockquote>"
        )
        caption_html = self.test_message_v2.caption_html_urled
        assert caption_html == test_html_string

    def test_caption_markdown_simple(self):
        test_md_string = (
            r"Test for <*bold*, _ita_\__lic_, `code`, "
            "[links](http://github.com/ab_), "
            "[text-mention](tg://user?id=123456789) and ```python\npre```. "
            r"http://google.com/ab\_"
        )
        caption_markdown = self.test_message.caption_markdown
        assert caption_markdown == test_md_string

    def test_caption_markdown_v2_simple(self):
        test_md_string = (
            r"__Test__ for <*bold*, _ita\_lic_, `\\\`code`, "
            "[links](http://github.com/abc\\\\\\)def), "
            "[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. "
            r"http://google\.com and _bold *nested in ~strk\>trgh~ nested in* italic_\. "
            "```python\nPython pre```\\. ||Spoiled||\\. ![👍](tg://emoji?id=1)\\.\n"
            ">Multiline\n"
            ">block quote\n"
            r">with *nested*\."
        )
        caption_markdown = self.test_message_v2.caption_markdown_v2
        assert caption_markdown == test_md_string

    def test_caption_markdown_empty(self, message):
        message.text = "test"
        message.caption = None
        assert message.caption_markdown is None
        assert message.caption_markdown_v2 is None

    def test_caption_markdown_urled(self):
        test_md_string = (
            r"Test for <*bold*, _ita_\__lic_, `code`, "
            "[links](http://github.com/ab_), "
            "[text-mention](tg://user?id=123456789) and ```python\npre```. "
            "[http://google.com/ab_](http://google.com/ab_)"
        )
        caption_markdown = self.test_message.caption_markdown_urled
        assert caption_markdown == test_md_string

    def test_caption_markdown_v2_urled(self):
        test_md_string = (
            r"__Test__ for <*bold*, _ita\_lic_, `\\\`code`, "
            "[links](http://github.com/abc\\\\\\)def), "
            "[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. "
            r"[http://google\.com](http://google.com) and _bold *nested in ~strk\>trgh~ "
            "nested in* italic_\\. ```python\nPython pre```\\. ||Spoiled||\\. "
            "![👍](tg://emoji?id=1)\\.\n"
            ">Multiline\n"
            ">block quote\n"
            r">with *nested*\."
        )
        caption_markdown = self.test_message_v2.caption_markdown_v2_urled
        assert caption_markdown == test_md_string

    def test_caption_html_emoji(self):
        caption = b"\\U0001f469\\u200d\\U0001f469\\u200d ABC".decode("unicode-escape")
        expected = b"\\U0001f469\\u200d\\U0001f469\\u200d <b>ABC</b>".decode("unicode-escape")
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            caption=caption,
            caption_entities=[bold_entity],
        )
        assert expected == message.caption_html

    def test_caption_markdown_emoji(self):
        caption = b"\\U0001f469\\u200d\\U0001f469\\u200d ABC".decode("unicode-escape")
        expected = b"\\U0001f469\\u200d\\U0001f469\\u200d *ABC*".decode("unicode-escape")
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            caption=caption,
            caption_entities=[bold_entity],
        )
        assert expected == message.caption_markdown

    @pytest.mark.parametrize(
        "type_",
        argvalues=[
            "caption_markdown",
            "caption_markdown_urled",
        ],
    )
    def test_caption_custom_emoji_md_v1(self, type_, recwarn):
        caption = "Look a custom emoji: 😎"
        emoji_entity = MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=21,
            length=2,
            custom_emoji_id="5472409228461217725",
        )
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            caption=caption,
            caption_entities=[emoji_entity],
        )
        with pytest.raises(ValueError, match="Custom Emoji entities are not supported for"):
            getattr(message, type_)

    @pytest.mark.parametrize(
        "type_",
        argvalues=[
            "caption_markdown_v2",
            "caption_markdown_v2_urled",
        ],
    )
    def test_caption_custom_emoji_md_v2(self, type_):
        caption = "Look a custom emoji: 😎"
        expected = "Look a custom emoji: ![😎](tg://emoji?id=5472409228461217725)"
        emoji_entity = MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=21,
            length=2,
            custom_emoji_id="5472409228461217725",
        )
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            caption=caption,
            caption_entities=[emoji_entity],
        )
        assert expected == message[type_]

    @pytest.mark.parametrize(
        "type_",
        argvalues=[
            "caption_html",
            "caption_html_urled",
        ],
    )
    def test_caption_custom_emoji_html(self, type_):
        caption = "Look a custom emoji: 😎"
        expected = 'Look a custom emoji: <tg-emoji emoji-id="5472409228461217725">😎</tg-emoji>'
        emoji_entity = MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=21,
            length=2,
            custom_emoji_id="5472409228461217725",
        )
        message = Message(
            1,
            from_user=self.from_user,
            date=self.date,
            chat=self.chat,
            caption=caption,
            caption_entities=[emoji_entity],
        )
        assert expected == message[type_]

    async def test_parse_entities_url_emoji(self):
        url = b"http://github.com/?unicode=\\u2713\\U0001f469".decode("unicode-escape")
        text = "some url"
        link_entity = MessageEntity(type=MessageEntity.URL, offset=0, length=8, url=url)
        message = Message(
            1, self.from_user, self.date, self.chat, text=text, entities=[link_entity]
        )
        assert message.parse_entities() == {link_entity: text}
        assert next(iter(message.parse_entities())).url == url

    def test_chat_id(self, message):
        assert message.chat_id == message.chat.id

    def test_id(self, message):
        assert message.message_id == message.id

    @pytest.mark.parametrize("type_", argvalues=[Chat.SUPERGROUP, Chat.CHANNEL])
    def test_link_with_username(self, message, type_):
        message.chat.username = "username"
        message.chat.type = type_
        assert message.link == f"https://t.me/{message.chat.username}/{message.message_id}"

    @pytest.mark.parametrize(
        ("type_", "id_"), argvalues=[(Chat.CHANNEL, -1003), (Chat.SUPERGROUP, -1003)]
    )
    def test_link_with_id(self, message, type_, id_):
        message.chat.username = None
        message.chat.id = id_
        message.chat.type = type_
        # The leading - for group ids/ -100 for supergroup ids isn't supposed to be in the link
        assert message.link == f"https://t.me/c/{3}/{message.message_id}"

    def test_link_with_topics(self, message):
        message.chat.username = None
        message.chat.id = -1003
        message.is_topic_message = True
        message.message_thread_id = 123
        assert message.link == f"https://t.me/c/3/{message.message_id}?thread=123"

    def test_link_with_reply(self, message):
        message.chat.username = None
        message.chat.id = -1003
        message.reply_to_message = Message(7, self.from_user, self.date, self.chat, text="Reply")
        message.message_thread_id = 123
        assert message.link == f"https://t.me/c/3/{message.message_id}?thread=123"

    @pytest.mark.parametrize(("id_", "username"), argvalues=[(None, "username"), (-3, None)])
    def test_link_private_chats(self, message, id_, username):
        message.chat.type = Chat.PRIVATE
        message.chat.id = id_
        message.chat.username = username
        assert message.link is None
        message.chat.type = Chat.GROUP
        assert message.link is None

    def test_effective_attachment(self, message_params):
        # This list is hard coded on purpose because just using constants.MessageAttachmentType
        # (which is used in Message.effective_message) wouldn't find any mistakes
        expected_attachment_types = [
            "animation",
            "audio",
            "contact",
            "dice",
            "document",
            "game",
            "invoice",
            "location",
            "passport_data",
            "photo",
            "poll",
            "sticker",
            "story",
            "successful_payment",
            "video",
            "video_note",
            "voice",
            "venue",
        ]

        for _ in range(3):
            # We run the same test multiple times to make sure that the caching is tested

            attachment = message_params.effective_attachment
            if attachment:
                condition = any(
                    message_params[message_type] is attachment
                    for message_type in expected_attachment_types
                )
                assert condition, "Got effective_attachment for unexpected type"
            else:
                condition = any(
                    message_params[message_type] for message_type in expected_attachment_types
                )
                assert not condition, "effective_attachment was None even though it should not be"

    def test_compute_quote_position_and_entities_false_index(self, message):
        message.text = "AA"
        with pytest.raises(
            ValueError,
            match="You requested the 5-th occurrence of 'A', "
            "but this text appears only 2 times.",
        ):
            message.compute_quote_position_and_entities("A", 5)

    def test_compute_quote_position_and_entities_no_text_or_caption(self, message):
        message.text = None
        message.caption = None
        with pytest.raises(
            RuntimeError,
            match="This message has neither text nor caption.",
        ):
            message.compute_quote_position_and_entities("A", 5)

    @pytest.mark.parametrize(
        ("text", "quote", "index", "expected"),
        argvalues=[
            ("AA", "A", None, 0),
            ("AA", "A", 0, 0),
            ("AA", "A", 1, 1),
            ("ABC ABC ABC ABC", "ABC", None, 0),
            ("ABC ABC ABC ABC", "ABC", 0, 0),
            ("ABC ABC ABC ABC", "ABC", 3, 12),
            ("👨‍👨‍👧👨‍👨‍👧👨‍👨‍👧👨‍👨‍👧", "👨‍👨‍👧", 0, 0),
            ("👨‍👨‍👧👨‍👨‍👧👨‍👨‍👧👨‍👨‍👧", "👨‍👨‍👧", 3, 24),
            ("👨‍👨‍👧👨‍👨‍👧👨‍👨‍👧👨‍👨‍👧", "👨", 1, 3),
            ("👨‍👨‍👧👨‍👨‍👧👨‍👨‍👧👨‍👨‍👧", "👧", 2, 22),
        ],
    )
    @pytest.mark.parametrize("caption", [True, False])
    def test_compute_quote_position_and_entities_position(
        self, message, text, quote, index, expected, caption
    ):
        if caption:
            message.caption = text
            message.text = None
        else:
            message.text = text
            message.caption = None

        assert message.compute_quote_position_and_entities(quote, index)[0] == expected

    def test_compute_quote_position_and_entities_entities(self, message):
        message.text = "A A A"
        message.entities = ()
        assert message.compute_quote_position_and_entities("A", 0)[1] is None

        message.entities = (
            # covers complete string
            MessageEntity(type=MessageEntity.BOLD, offset=0, length=6),
            # covers first 2 As only
            MessageEntity(type=MessageEntity.ITALIC, offset=0, length=3),
            # covers second 2 As only
            MessageEntity(type=MessageEntity.UNDERLINE, offset=2, length=3),
            # covers middle A only
            MessageEntity(type=MessageEntity.STRIKETHROUGH, offset=2, length=1),
            # covers only whitespace, should be ignored
            MessageEntity(type=MessageEntity.CODE, offset=1, length=1),
        )

        assert message.compute_quote_position_and_entities("A", 0)[1] == (
            MessageEntity(type=MessageEntity.BOLD, offset=0, length=1),
            MessageEntity(type=MessageEntity.ITALIC, offset=0, length=1),
        )

        assert message.compute_quote_position_and_entities("A", 1)[1] == (
            MessageEntity(type=MessageEntity.BOLD, offset=0, length=1),
            MessageEntity(type=MessageEntity.ITALIC, offset=0, length=1),
            MessageEntity(type=MessageEntity.UNDERLINE, offset=0, length=1),
            MessageEntity(type=MessageEntity.STRIKETHROUGH, offset=0, length=1),
        )

        assert message.compute_quote_position_and_entities("A", 2)[1] == (
            MessageEntity(type=MessageEntity.BOLD, offset=0, length=1),
            MessageEntity(type=MessageEntity.UNDERLINE, offset=0, length=1),
        )

    @pytest.mark.parametrize(
        ("target_chat_id", "expected"),
        argvalues=[
            (None, 3),
            (3, 3),
            (-1003, -1003),
            ("@username", "@username"),
        ],
    )
    def test_build_reply_arguments_chat_id_and_message_id(self, message, target_chat_id, expected):
        message.chat.id = 3
        reply_kwargs = message.build_reply_arguments(target_chat_id=target_chat_id)
        assert reply_kwargs["chat_id"] == expected
        assert reply_kwargs["reply_parameters"].chat_id == (None if expected == 3 else 3)
        assert reply_kwargs["reply_parameters"].message_id == message.message_id

    @pytest.mark.parametrize(
        ("target_chat_id", "message_thread_id", "expected"),
        argvalues=[
            (None, None, True),
            (None, 123, True),
            (None, 0, False),
            (None, -1, False),
            (3, None, True),
            (3, 123, True),
            (3, 0, False),
            (3, -1, False),
            (-1003, None, False),
            (-1003, 123, False),
            (-1003, 0, False),
            (-1003, -1, False),
            ("@username", None, True),
            ("@username", 123, True),
            ("@username", 0, False),
            ("@username", -1, False),
            ("@other_username", None, False),
            ("@other_username", 123, False),
            ("@other_username", 0, False),
            ("@other_username", -1, False),
        ],
    )
    def test_build_reply_arguments_aswr(
        self, message, target_chat_id, message_thread_id, expected
    ):
        message.chat.id = 3
        message.chat.username = "username"
        message.message_thread_id = 123
        assert (
            message.build_reply_arguments(
                target_chat_id=target_chat_id, message_thread_id=message_thread_id
            )["reply_parameters"].allow_sending_without_reply
            is not None
        ) == expected

        assert (
            message.build_reply_arguments(
                target_chat_id=target_chat_id,
                message_thread_id=message_thread_id,
                allow_sending_without_reply="custom",
            )["reply_parameters"].allow_sending_without_reply
        ) == ("custom" if expected else None)

    def test_build_reply_arguments_quote(self, message, monkeypatch):
        reply_parameters = message.build_reply_arguments()["reply_parameters"]
        assert reply_parameters.quote is None
        assert reply_parameters.quote_entities == ()
        assert reply_parameters.quote_position is None
        assert not reply_parameters.quote_parse_mode

        quote_obj = object()
        quote_index = object()
        quote_entities = (object(), object())
        quote_position = object()

        def mock_compute(quote, index):
            if quote is quote_obj and index is quote_index:
                return quote_position, quote_entities
            return False, False

        monkeypatch.setattr(message, "compute_quote_position_and_entities", mock_compute)
        reply_parameters = message.build_reply_arguments(quote=quote_obj, quote_index=quote_index)[
            "reply_parameters"
        ]

        assert reply_parameters.quote is quote_obj
        assert reply_parameters.quote_entities is quote_entities
        assert reply_parameters.quote_position is quote_position
        assert not reply_parameters.quote_parse_mode

    async def test_reply_text(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            text = kwargs["text"] == "test"
            return id_ and text

        assert check_shortcut_signature(
            Message.reply_text,
            Bot.send_message,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_text,
            message.get_bot(),
            "send_message",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_text, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_message", make_assertion)
        assert await message.reply_text("test")
        await self.check_quote_parsing(
            message, message.reply_text, "send_message", ["test"], monkeypatch
        )

    async def test_reply_markdown(self, monkeypatch, message):
        test_md_string = (
            r"Test for <*bold*, _ita_\__lic_, `code`, "
            "[links](http://github.com/ab_), "
            "[text-mention](tg://user?id=123456789) and ```python\npre```. "
            r"http://google.com/ab\_"
        )

        async def make_assertion(*_, **kwargs):
            cid = kwargs["chat_id"] == message.chat_id
            markdown_text = kwargs["text"] == test_md_string
            markdown_enabled = kwargs["parse_mode"] == ParseMode.MARKDOWN
            return all([cid, markdown_text, markdown_enabled])

        assert check_shortcut_signature(
            Message.reply_markdown,
            Bot.send_message,
            ["chat_id", "parse_mode", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_text,
            message.get_bot(),
            "send_message",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_text, message.get_bot())

        text_markdown = self.test_message.text_markdown
        assert text_markdown == test_md_string

        monkeypatch.setattr(message.get_bot(), "send_message", make_assertion)
        assert await message.reply_markdown(self.test_message.text_markdown)

    async def test_reply_markdown_v2(self, monkeypatch, message):
        test_md_string = (
            r"__Test__ for <*bold*, _ita\_lic_, `\\\`code`, "
            "[links](http://github.com/abc\\\\\\)def), "
            "[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. "
            r"http://google\.com and _bold *nested in ~strk\>trgh~ nested in* italic_\. "
            "```python\nPython pre```\\. ||Spoiled||\\. ![👍](tg://emoji?id=1)\\.\n"
            ">Multiline\n"
            ">block quote\n"
            r">with *nested*\."
        )

        async def make_assertion(*_, **kwargs):
            cid = kwargs["chat_id"] == message.chat_id
            markdown_text = kwargs["text"] == test_md_string
            markdown_enabled = kwargs["parse_mode"] == ParseMode.MARKDOWN_V2
            return all([cid, markdown_text, markdown_enabled])

        assert check_shortcut_signature(
            Message.reply_markdown_v2,
            Bot.send_message,
            ["chat_id", "parse_mode", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_text,
            message.get_bot(),
            "send_message",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_text, message.get_bot())

        text_markdown = self.test_message_v2.text_markdown_v2
        assert text_markdown == test_md_string

        monkeypatch.setattr(message.get_bot(), "send_message", make_assertion)
        assert await message.reply_markdown_v2(self.test_message_v2.text_markdown_v2)
        await self.check_quote_parsing(
            message, message.reply_markdown_v2, "send_message", [test_md_string], monkeypatch
        )

    async def test_reply_html(self, monkeypatch, message):
        test_html_string = (
            "<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, "
            r"<code>\`code</code>, "
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r"<pre>`\pre</pre>. http://google.com "
            "and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. "
            '<pre><code class="python">Python pre</code></pre>. '
            '<span class="tg-spoiler">Spoiled</span>. '
            '<tg-emoji emoji-id="1">👍</tg-emoji>.\n'
            "<blockquote>Multiline\nblock quote\nwith <b>nested</b>.</blockquote>"
        )

        async def make_assertion(*_, **kwargs):
            cid = kwargs["chat_id"] == message.chat_id
            html_text = kwargs["text"] == test_html_string
            html_enabled = kwargs["parse_mode"] == ParseMode.HTML
            return all([cid, html_text, html_enabled])

        assert check_shortcut_signature(
            Message.reply_html,
            Bot.send_message,
            ["chat_id", "parse_mode", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_text,
            message.get_bot(),
            "send_message",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_text, message.get_bot())

        text_html = self.test_message_v2.text_html
        assert text_html == test_html_string

        monkeypatch.setattr(message.get_bot(), "send_message", make_assertion)
        assert await message.reply_html(self.test_message_v2.text_html)
        await self.check_quote_parsing(
            message, message.reply_html, "send_message", [test_html_string], monkeypatch
        )

    async def test_reply_media_group(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            media = kwargs["media"] == "reply_media_group"
            return id_ and media

        assert check_shortcut_signature(
            Message.reply_media_group,
            Bot.send_media_group,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_media_group,
            message.get_bot(),
            "send_media_group",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_media_group, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_media_group", make_assertion)
        assert await message.reply_media_group(media="reply_media_group")
        await self.check_quote_parsing(
            message,
            message.reply_media_group,
            "send_media_group",
            ["reply_media_group"],
            monkeypatch,
        )

    async def test_reply_photo(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            photo = kwargs["photo"] == "test_photo"
            return id_ and photo

        assert check_shortcut_signature(
            Message.reply_photo,
            Bot.send_photo,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_photo,
            message.get_bot(),
            "send_photo",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_photo, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_photo", make_assertion)
        assert await message.reply_photo(photo="test_photo")
        await self.check_quote_parsing(
            message, message.reply_photo, "send_photo", ["test_photo"], monkeypatch
        )

    async def test_reply_audio(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            audio = kwargs["audio"] == "test_audio"
            return id_ and audio

        assert check_shortcut_signature(
            Message.reply_audio,
            Bot.send_audio,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_audio,
            message.get_bot(),
            "send_audio",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_audio, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_audio", make_assertion)
        assert await message.reply_audio(audio="test_audio")
        await self.check_quote_parsing(
            message, message.reply_audio, "send_audio", ["test_audio"], monkeypatch
        )

    async def test_reply_document(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            document = kwargs["document"] == "test_document"
            return id_ and document

        assert check_shortcut_signature(
            Message.reply_document,
            Bot.send_document,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_document,
            message.get_bot(),
            "send_document",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_document, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_document", make_assertion)
        assert await message.reply_document(document="test_document")
        await self.check_quote_parsing(
            message, message.reply_document, "send_document", ["test_document"], monkeypatch
        )

    async def test_reply_animation(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            animation = kwargs["animation"] == "test_animation"
            return id_ and animation

        assert check_shortcut_signature(
            Message.reply_animation,
            Bot.send_animation,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_animation,
            message.get_bot(),
            "send_animation",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_animation, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_animation", make_assertion)
        assert await message.reply_animation(animation="test_animation")
        await self.check_quote_parsing(
            message, message.reply_animation, "send_animation", ["test_animation"], monkeypatch
        )

    async def test_reply_sticker(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            sticker = kwargs["sticker"] == "test_sticker"
            return id_ and sticker

        assert check_shortcut_signature(
            Message.reply_sticker,
            Bot.send_sticker,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_sticker,
            message.get_bot(),
            "send_sticker",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_sticker, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_sticker", make_assertion)
        assert await message.reply_sticker(sticker="test_sticker")
        await self.check_quote_parsing(
            message, message.reply_sticker, "send_sticker", ["test_sticker"], monkeypatch
        )

    async def test_reply_video(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            video = kwargs["video"] == "test_video"
            return id_ and video

        assert check_shortcut_signature(
            Message.reply_video,
            Bot.send_video,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_video,
            message.get_bot(),
            "send_video",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_video, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_video", make_assertion)
        assert await message.reply_video(video="test_video")
        await self.check_quote_parsing(
            message, message.reply_video, "send_video", ["test_video"], monkeypatch
        )

    async def test_reply_video_note(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            video_note = kwargs["video_note"] == "test_video_note"
            return id_ and video_note

        assert check_shortcut_signature(
            Message.reply_video_note,
            Bot.send_video_note,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_video_note,
            message.get_bot(),
            "send_video_note",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_video_note, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_video_note", make_assertion)
        assert await message.reply_video_note(video_note="test_video_note")
        await self.check_quote_parsing(
            message, message.reply_video_note, "send_video_note", ["test_video_note"], monkeypatch
        )

    async def test_reply_voice(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            voice = kwargs["voice"] == "test_voice"
            return id_ and voice

        assert check_shortcut_signature(
            Message.reply_voice,
            Bot.send_voice,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_voice,
            message.get_bot(),
            "send_voice",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_voice, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_voice", make_assertion)
        assert await message.reply_voice(voice="test_voice")
        await self.check_quote_parsing(
            message, message.reply_voice, "send_voice", ["test_voice"], monkeypatch
        )

    async def test_reply_location(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            location = kwargs["location"] == "test_location"
            return id_ and location

        assert check_shortcut_signature(
            Message.reply_location,
            Bot.send_location,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_location,
            message.get_bot(),
            "send_location",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_location, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_location", make_assertion)
        assert await message.reply_location(location="test_location")
        await self.check_quote_parsing(
            message, message.reply_location, "send_location", ["test_location"], monkeypatch
        )

    async def test_reply_venue(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            venue = kwargs["venue"] == "test_venue"
            return id_ and venue

        assert check_shortcut_signature(
            Message.reply_venue,
            Bot.send_venue,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_venue,
            message.get_bot(),
            "send_venue",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_venue, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_venue", make_assertion)
        assert await message.reply_venue(venue="test_venue")
        await self.check_quote_parsing(
            message, message.reply_venue, "send_venue", ["test_venue"], monkeypatch
        )

    async def test_reply_contact(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            contact = kwargs["contact"] == "test_contact"
            return id_ and contact

        assert check_shortcut_signature(
            Message.reply_contact,
            Bot.send_contact,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_contact,
            message.get_bot(),
            "send_contact",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_contact, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_contact", make_assertion)
        assert await message.reply_contact(contact="test_contact")
        await self.check_quote_parsing(
            message, message.reply_contact, "send_contact", ["test_contact"], monkeypatch
        )

    async def test_reply_poll(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            question = kwargs["question"] == "test_poll"
            options = kwargs["options"] == ["1", "2", "3"]
            return id_ and question and options

        assert check_shortcut_signature(
            Message.reply_poll,
            Bot.send_poll,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_poll, message.get_bot(), "send_poll", skip_params=["reply_to_message_id"]
        )
        assert await check_defaults_handling(message.reply_poll, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_poll", make_assertion)
        assert await message.reply_poll(question="test_poll", options=["1", "2", "3"])
        await self.check_quote_parsing(
            message, message.reply_poll, "send_poll", ["test_poll", ["1", "2", "3"]], monkeypatch
        )

    async def test_reply_dice(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            contact = kwargs["disable_notification"] is True
            return id_ and contact

        assert check_shortcut_signature(
            Message.reply_dice,
            Bot.send_dice,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_dice, message.get_bot(), "send_dice", skip_params=["reply_to_message_id"]
        )
        assert await check_defaults_handling(message.reply_dice, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_dice", make_assertion)
        assert await message.reply_dice(disable_notification=True)
        await self.check_quote_parsing(
            message,
            message.reply_dice,
            "send_dice",
            [],
            monkeypatch,
        )

    async def test_reply_action(self, monkeypatch, message: Message):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == message.chat_id
            action = kwargs["action"] == ChatAction.TYPING
            return id_ and action

        assert check_shortcut_signature(
            Message.reply_chat_action, Bot.send_chat_action, ["chat_id", "reply_to_message_id"], []
        )
        assert await check_shortcut_call(
            message.reply_chat_action, message.get_bot(), "send_chat_action"
        )
        assert await check_defaults_handling(message.reply_chat_action, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_chat_action", make_assertion)
        assert await message.reply_chat_action(action=ChatAction.TYPING)

    async def test_reply_game(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            return (
                kwargs["chat_id"] == message.chat_id and kwargs["game_short_name"] == "test_game"
            )

        assert check_shortcut_signature(
            Message.reply_game,
            Bot.send_game,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_game, message.get_bot(), "send_game", skip_params=["reply_to_message_id"]
        )
        assert await check_defaults_handling(message.reply_game, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_game", make_assertion)
        assert await message.reply_game(game_short_name="test_game")
        await self.check_quote_parsing(
            message, message.reply_game, "send_game", ["test_game"], monkeypatch
        )

    async def test_reply_invoice(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            title = kwargs["title"] == "title"
            description = kwargs["description"] == "description"
            payload = kwargs["payload"] == "payload"
            provider_token = kwargs["provider_token"] == "provider_token"
            currency = kwargs["currency"] == "currency"
            prices = kwargs["prices"] == "prices"
            args = title and description and payload and provider_token and currency and prices
            return kwargs["chat_id"] == message.chat_id and args

        assert check_shortcut_signature(
            Message.reply_invoice,
            Bot.send_invoice,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(
            message.reply_invoice,
            message.get_bot(),
            "send_invoice",
            skip_params=["reply_to_message_id"],
        )
        assert await check_defaults_handling(message.reply_invoice, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "send_invoice", make_assertion)
        assert await message.reply_invoice(
            "title",
            "description",
            "payload",
            "provider_token",
            "currency",
            "prices",
        )
        await self.check_quote_parsing(
            message,
            message.reply_invoice,
            "send_invoice",
            ["title", "description", "payload", "provider_token", "currency", "prices"],
            monkeypatch,
        )

    @pytest.mark.parametrize(("disable_notification", "protected"), [(False, True), (True, False)])
    async def test_forward(self, monkeypatch, message, disable_notification, protected):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == 123456
            from_chat = kwargs["from_chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            notification = kwargs["disable_notification"] == disable_notification
            protected_cont = kwargs["protect_content"] == protected
            return chat_id and from_chat and message_id and notification and protected_cont

        assert check_shortcut_signature(
            Message.forward, Bot.forward_message, ["from_chat_id", "message_id"], []
        )
        assert await check_shortcut_call(message.forward, message.get_bot(), "forward_message")
        assert await check_defaults_handling(message.forward, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "forward_message", make_assertion)
        assert await message.forward(
            123456, disable_notification=disable_notification, protect_content=protected
        )
        assert not await message.forward(635241)

    @pytest.mark.parametrize(("disable_notification", "protected"), [(True, False), (False, True)])
    async def test_copy(self, monkeypatch, message, disable_notification, protected):
        keyboard = [[1, 2]]

        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == 123456
            from_chat = kwargs["from_chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            notification = kwargs["disable_notification"] == disable_notification
            protected_cont = kwargs["protect_content"] == protected
            if kwargs.get("reply_markup") is not None:
                reply_markup = kwargs["reply_markup"] is keyboard
            else:
                reply_markup = True
            return (
                chat_id
                and from_chat
                and message_id
                and notification
                and reply_markup
                and protected_cont
            )

        assert check_shortcut_signature(
            Message.copy, Bot.copy_message, ["from_chat_id", "message_id"], []
        )
        assert await check_shortcut_call(message.copy, message.get_bot(), "copy_message")
        assert await check_defaults_handling(message.copy, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "copy_message", make_assertion)
        assert await message.copy(
            123456, disable_notification=disable_notification, protect_content=protected
        )
        assert await message.copy(
            123456,
            reply_markup=keyboard,
            disable_notification=disable_notification,
            protect_content=protected,
        )
        assert not await message.copy(635241)

    @pytest.mark.parametrize(("disable_notification", "protected"), [(True, False), (False, True)])
    async def test_reply_copy(self, monkeypatch, message, disable_notification, protected):
        keyboard = [[1, 2]]

        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["from_chat_id"] == 123456
            from_chat = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == 456789
            notification = kwargs["disable_notification"] == disable_notification
            is_protected = kwargs["protect_content"] == protected
            if kwargs.get("reply_markup") is not None:
                reply_markup = kwargs["reply_markup"] is keyboard
            else:
                reply_markup = True
            return (
                chat_id
                and from_chat
                and message_id
                and notification
                and reply_markup
                and is_protected
            )

        assert check_shortcut_signature(
            Message.reply_copy,
            Bot.copy_message,
            ["chat_id", "reply_to_message_id"],
            ["quote", "do_quote", "reply_to_message_id"],
        )
        assert await check_shortcut_call(message.copy, message.get_bot(), "copy_message")
        assert await check_defaults_handling(message.copy, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "copy_message", make_assertion)
        assert await message.reply_copy(
            123456, 456789, disable_notification=disable_notification, protect_content=protected
        )
        assert await message.reply_copy(
            123456,
            456789,
            reply_markup=keyboard,
            disable_notification=disable_notification,
            protect_content=protected,
        )
        await self.check_quote_parsing(
            message,
            message.reply_copy,
            "copy_message",
            [123456, 456789],
            monkeypatch,
        )

    async def test_edit_text(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            text = kwargs["text"] == "test"
            return chat_id and message_id and text

        assert check_shortcut_signature(
            Message.edit_text,
            Bot.edit_message_text,
            ["chat_id", "message_id", "inline_message_id"],
            [],
        )
        assert await check_shortcut_call(
            message.edit_text,
            message.get_bot(),
            "edit_message_text",
            skip_params=["inline_message_id"],
            shortcut_kwargs=["message_id", "chat_id"],
        )
        assert await check_defaults_handling(message.edit_text, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "edit_message_text", make_assertion)
        assert await message.edit_text(text="test")

    async def test_edit_caption(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            caption = kwargs["caption"] == "new caption"
            return chat_id and message_id and caption

        assert check_shortcut_signature(
            Message.edit_caption,
            Bot.edit_message_caption,
            ["chat_id", "message_id", "inline_message_id"],
            [],
        )
        assert await check_shortcut_call(
            message.edit_caption,
            message.get_bot(),
            "edit_message_caption",
            skip_params=["inline_message_id"],
            shortcut_kwargs=["message_id", "chat_id"],
        )
        assert await check_defaults_handling(message.edit_caption, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "edit_message_caption", make_assertion)
        assert await message.edit_caption(caption="new caption")

    async def test_edit_media(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            media = kwargs["media"] == "my_media"
            return chat_id and message_id and media

        assert check_shortcut_signature(
            Message.edit_media,
            Bot.edit_message_media,
            ["chat_id", "message_id", "inline_message_id"],
            [],
        )
        assert await check_shortcut_call(
            message.edit_media,
            message.get_bot(),
            "edit_message_media",
            skip_params=["inline_message_id"],
            shortcut_kwargs=["message_id", "chat_id"],
        )
        assert await check_defaults_handling(message.edit_media, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "edit_message_media", make_assertion)
        assert await message.edit_media("my_media")

    async def test_edit_reply_markup(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            reply_markup = kwargs["reply_markup"] == [["1", "2"]]
            return chat_id and message_id and reply_markup

        assert check_shortcut_signature(
            Message.edit_reply_markup,
            Bot.edit_message_reply_markup,
            ["chat_id", "message_id", "inline_message_id"],
            [],
        )
        assert await check_shortcut_call(
            message.edit_reply_markup,
            message.get_bot(),
            "edit_message_reply_markup",
            skip_params=["inline_message_id"],
            shortcut_kwargs=["message_id", "chat_id"],
        )
        assert await check_defaults_handling(message.edit_reply_markup, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "edit_message_reply_markup", make_assertion)
        assert await message.edit_reply_markup(reply_markup=[["1", "2"]])

    async def test_edit_live_location(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            latitude = kwargs["latitude"] == 1
            longitude = kwargs["longitude"] == 2
            return chat_id and message_id and longitude and latitude

        assert check_shortcut_signature(
            Message.edit_live_location,
            Bot.edit_message_live_location,
            ["chat_id", "message_id", "inline_message_id"],
            [],
        )
        assert await check_shortcut_call(
            message.edit_live_location,
            message.get_bot(),
            "edit_message_live_location",
            skip_params=["inline_message_id"],
            shortcut_kwargs=["message_id", "chat_id"],
        )
        assert await check_defaults_handling(message.edit_live_location, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "edit_message_live_location", make_assertion)
        assert await message.edit_live_location(latitude=1, longitude=2)

    async def test_stop_live_location(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.stop_live_location,
            Bot.stop_message_live_location,
            ["chat_id", "message_id", "inline_message_id"],
            [],
        )
        assert await check_shortcut_call(
            message.stop_live_location,
            message.get_bot(),
            "stop_message_live_location",
            skip_params=["inline_message_id"],
            shortcut_kwargs=["message_id", "chat_id"],
        )
        assert await check_defaults_handling(message.stop_live_location, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "stop_message_live_location", make_assertion)
        assert await message.stop_live_location()

    async def test_set_game_score(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            user_id = kwargs["user_id"] == 1
            score = kwargs["score"] == 2
            return chat_id and message_id and user_id and score

        assert check_shortcut_signature(
            Message.set_game_score,
            Bot.set_game_score,
            ["chat_id", "message_id", "inline_message_id"],
            [],
        )
        assert await check_shortcut_call(
            message.set_game_score,
            message.get_bot(),
            "set_game_score",
            skip_params=["inline_message_id"],
            shortcut_kwargs=["message_id", "chat_id"],
        )
        assert await check_defaults_handling(message.set_game_score, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "set_game_score", make_assertion)
        assert await message.set_game_score(user_id=1, score=2)

    async def test_get_game_high_scores(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            user_id = kwargs["user_id"] == 1
            return chat_id and message_id and user_id

        assert check_shortcut_signature(
            Message.get_game_high_scores,
            Bot.get_game_high_scores,
            ["chat_id", "message_id", "inline_message_id"],
            [],
        )
        assert await check_shortcut_call(
            message.get_game_high_scores,
            message.get_bot(),
            "get_game_high_scores",
            skip_params=["inline_message_id"],
            shortcut_kwargs=["message_id", "chat_id"],
        )
        assert await check_defaults_handling(message.get_game_high_scores, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "get_game_high_scores", make_assertion)
        assert await message.get_game_high_scores(user_id=1)

    async def test_delete(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.delete, Bot.delete_message, ["chat_id", "message_id"], []
        )
        assert await check_shortcut_call(message.delete, message.get_bot(), "delete_message")
        assert await check_defaults_handling(message.delete, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "delete_message", make_assertion)
        assert await message.delete()

    async def test_stop_poll(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.stop_poll, Bot.stop_poll, ["chat_id", "message_id"], []
        )
        assert await check_shortcut_call(message.stop_poll, message.get_bot(), "stop_poll")
        assert await check_defaults_handling(message.stop_poll, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "stop_poll", make_assertion)
        assert await message.stop_poll()

    async def test_pin(self, monkeypatch, message):
        async def make_assertion(*args, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.pin, Bot.pin_chat_message, ["chat_id", "message_id"], []
        )
        assert await check_shortcut_call(message.pin, message.get_bot(), "pin_chat_message")
        assert await check_defaults_handling(message.pin, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "pin_chat_message", make_assertion)
        assert await message.pin()

    async def test_unpin(self, monkeypatch, message):
        async def make_assertion(*args, **kwargs):
            chat_id = kwargs["chat_id"] == message.chat_id
            message_id = kwargs["message_id"] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.unpin, Bot.unpin_chat_message, ["chat_id", "message_id"], []
        )
        assert await check_shortcut_call(
            message.unpin,
            message.get_bot(),
            "unpin_chat_message",
            shortcut_kwargs=["chat_id", "message_id"],
        )
        assert await check_defaults_handling(message.unpin, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "unpin_chat_message", make_assertion)
        assert await message.unpin()

    @pytest.mark.parametrize(
        ("default_quote", "chat_type", "expected"),
        [
            (False, Chat.PRIVATE, False),
            (None, Chat.PRIVATE, False),
            (True, Chat.PRIVATE, True),
            (False, Chat.GROUP, False),
            (None, Chat.GROUP, True),
            (True, Chat.GROUP, True),
            (False, Chat.SUPERGROUP, False),
            (None, Chat.SUPERGROUP, True),
            (True, Chat.SUPERGROUP, True),
            (False, Chat.CHANNEL, False),
            (None, Chat.CHANNEL, True),
            (True, Chat.CHANNEL, True),
        ],
    )
    async def test_default_do_quote(
        self, bot, message, default_quote, chat_type, expected, monkeypatch
    ):
        message.set_bot(PytestExtBot(token=bot.token, defaults=Defaults(do_quote=default_quote)))

        async def make_assertion(*_, **kwargs):
            reply_parameters = kwargs.get("reply_parameters") or ReplyParameters(message_id=False)
            condition = reply_parameters.message_id == message.message_id
            return condition == expected

        monkeypatch.setattr(message.get_bot(), "send_message", make_assertion)

        try:
            message.chat.type = chat_type
            assert await message.reply_text("test")
        finally:
            message.get_bot()._defaults = None

    async def test_edit_forum_topic(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            return (
                kwargs["chat_id"] == message.chat_id
                and kwargs["message_thread_id"] == message.message_thread_id
                and kwargs["name"] == "New Name"
                and kwargs["icon_custom_emoji_id"] == "12345"
            )

        assert check_shortcut_signature(
            Message.edit_forum_topic, Bot.edit_forum_topic, ["chat_id", "message_thread_id"], []
        )
        assert await check_shortcut_call(
            message.edit_forum_topic,
            message.get_bot(),
            "edit_forum_topic",
            shortcut_kwargs=["chat_id", "message_thread_id"],
        )
        assert await check_defaults_handling(message.edit_forum_topic, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "edit_forum_topic", make_assertion)
        assert await message.edit_forum_topic(name="New Name", icon_custom_emoji_id="12345")

    async def test_close_forum_topic(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            return (
                kwargs["chat_id"] == message.chat_id
                and kwargs["message_thread_id"] == message.message_thread_id
            )

        assert check_shortcut_signature(
            Message.close_forum_topic, Bot.close_forum_topic, ["chat_id", "message_thread_id"], []
        )
        assert await check_shortcut_call(
            message.close_forum_topic,
            message.get_bot(),
            "close_forum_topic",
            shortcut_kwargs=["chat_id", "message_thread_id"],
        )
        assert await check_defaults_handling(message.close_forum_topic, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "close_forum_topic", make_assertion)
        assert await message.close_forum_topic()

    async def test_reopen_forum_topic(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            return (
                kwargs["chat_id"] == message.chat_id
                and kwargs["message_thread_id"] == message.message_thread_id
            )

        assert check_shortcut_signature(
            Message.reopen_forum_topic,
            Bot.reopen_forum_topic,
            ["chat_id", "message_thread_id"],
            [],
        )
        assert await check_shortcut_call(
            message.reopen_forum_topic,
            message.get_bot(),
            "reopen_forum_topic",
            shortcut_kwargs=["chat_id", "message_thread_id"],
        )
        assert await check_defaults_handling(message.reopen_forum_topic, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "reopen_forum_topic", make_assertion)
        assert await message.reopen_forum_topic()

    async def test_delete_forum_topic(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            return (
                kwargs["chat_id"] == message.chat_id
                and kwargs["message_thread_id"] == message.message_thread_id
            )

        assert check_shortcut_signature(
            Message.delete_forum_topic,
            Bot.delete_forum_topic,
            ["chat_id", "message_thread_id"],
            [],
        )
        assert await check_shortcut_call(
            message.delete_forum_topic,
            message.get_bot(),
            "delete_forum_topic",
            shortcut_kwargs=["chat_id", "message_thread_id"],
        )
        assert await check_defaults_handling(message.delete_forum_topic, message.get_bot())

        monkeypatch.setattr(message.get_bot(), "delete_forum_topic", make_assertion)
        assert await message.delete_forum_topic()

    async def test_unpin_all_forum_topic_messages(self, monkeypatch, message):
        async def make_assertion(*_, **kwargs):
            return (
                kwargs["chat_id"] == message.chat_id
                and kwargs["message_thread_id"] == message.message_thread_id
            )

        assert check_shortcut_signature(
            Message.unpin_all_forum_topic_messages,
            Bot.unpin_all_forum_topic_messages,
            ["chat_id", "message_thread_id"],
            [],
        )
        assert await check_shortcut_call(
            message.unpin_all_forum_topic_messages,
            message.get_bot(),
            "unpin_all_forum_topic_messages",
            shortcut_kwargs=["chat_id", "message_thread_id"],
        )
        assert await check_defaults_handling(
            message.unpin_all_forum_topic_messages, message.get_bot()
        )

        monkeypatch.setattr(message.get_bot(), "unpin_all_forum_topic_messages", make_assertion)
        assert await message.unpin_all_forum_topic_messages()
