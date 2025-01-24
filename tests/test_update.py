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
import time
from copy import deepcopy

import pytest

from telegram import (
    BusinessConnection,
    BusinessMessagesDeleted,
    CallbackQuery,
    Chat,
    ChatBoost,
    ChatBoostRemoved,
    ChatBoostSourcePremium,
    ChatBoostUpdated,
    ChatJoinRequest,
    ChatMemberOwner,
    ChatMemberUpdated,
    ChosenInlineResult,
    InaccessibleMessage,
    InlineQuery,
    Message,
    MessageReactionCountUpdated,
    MessageReactionUpdated,
    PaidMediaPurchased,
    Poll,
    PollAnswer,
    PollOption,
    PreCheckoutQuery,
    ReactionCount,
    ReactionTypeEmoji,
    ShippingAddress,
    ShippingQuery,
    Update,
    User,
)
from telegram._utils.datetime import from_timestamp
from telegram.warnings import PTBUserWarning
from tests.auxil.slots import mro_slots

message = Message(
    1,
    dtm.datetime.utcnow(),
    Chat(1, ""),
    from_user=User(1, "", False),
    text="Text",
    sender_chat=Chat(1, ""),
)
channel_post = Message(
    1,
    dtm.datetime.utcnow(),
    Chat(1, ""),
    text="Text",
    sender_chat=Chat(1, ""),
)
chat_member_updated = ChatMemberUpdated(
    Chat(1, "chat"),
    User(1, "", False),
    from_timestamp(int(time.time())),
    ChatMemberOwner(User(1, "", False), True),
    ChatMemberOwner(User(1, "", False), True),
)


chat_join_request = ChatJoinRequest(
    chat=Chat(1, Chat.SUPERGROUP),
    from_user=User(1, "first_name", False),
    date=from_timestamp(int(time.time())),
    user_chat_id=1,
    bio="bio",
)

chat_boost = ChatBoostUpdated(
    chat=Chat(1, "priv"),
    boost=ChatBoost(
        "1",
        from_timestamp(int(time.time())),
        from_timestamp(int(time.time())),
        ChatBoostSourcePremium(User(1, "", False)),
    ),
)

removed_chat_boost = ChatBoostRemoved(
    Chat(1, "private"),
    "2",
    from_timestamp(int(time.time())),
    ChatBoostSourcePremium(User(1, "name", False)),
)

message_reaction = MessageReactionUpdated(
    chat=Chat(1, "chat"),
    message_id=1,
    date=from_timestamp(int(time.time())),
    old_reaction=(ReactionTypeEmoji("👍"),),
    new_reaction=(ReactionTypeEmoji("👍"),),
    user=User(1, "name", False),
    actor_chat=Chat(1, ""),
)


message_reaction_count = MessageReactionCountUpdated(
    chat=Chat(1, "chat"),
    message_id=1,
    date=from_timestamp(int(time.time())),
    reactions=(ReactionCount(ReactionTypeEmoji("👍"), 1),),
)

business_connection = BusinessConnection(
    "1",
    User(1, "name", False),
    1,
    from_timestamp(int(time.time())),
    True,
    True,
)

deleted_business_messages = BusinessMessagesDeleted(
    "1",
    Chat(1, ""),
    (1, 2),
)

business_message = Message(
    1,
    dtm.datetime.utcnow(),
    Chat(1, ""),
    User(1, "", False),
)

purchased_paid_media = PaidMediaPurchased(
    from_user=User(1, "", False),
    paid_media_payload="payload",
)


params = [
    {"message": message},
    {"edited_message": message},
    {"callback_query": CallbackQuery(1, User(1, "", False), "chat", message=message)},
    {"channel_post": channel_post},
    {"edited_channel_post": channel_post},
    {"inline_query": InlineQuery(1, User(1, "", False), "", "")},
    {"chosen_inline_result": ChosenInlineResult("id", User(1, "", False), "")},
    {
        "shipping_query": ShippingQuery(
            "id", User(1, "", False), "", ShippingAddress("", "", "", "", "", "")
        )
    },
    {"pre_checkout_query": PreCheckoutQuery("id", User(1, "", False), "", 0, "")},
    {"poll": Poll("id", "?", [PollOption(".", 1)], False, False, False, Poll.REGULAR, True)},
    {
        "poll_answer": PollAnswer(
            "id",
            [1],
            User(
                1,
                "",
                False,
            ),
            Chat(1, ""),
        )
    },
    {"my_chat_member": chat_member_updated},
    {"chat_member": chat_member_updated},
    {"chat_join_request": chat_join_request},
    {"chat_boost": chat_boost},
    {"removed_chat_boost": removed_chat_boost},
    {"message_reaction": message_reaction},
    {"message_reaction_count": message_reaction_count},
    {"business_connection": business_connection},
    {"deleted_business_messages": deleted_business_messages},
    {"business_message": business_message},
    {"edited_business_message": business_message},
    {"purchased_paid_media": purchased_paid_media},
    # Must be last to conform with `ids` below!
    {"callback_query": CallbackQuery(1, User(1, "", False), "chat")},
]

all_types = (
    "message",
    "edited_message",
    "callback_query",
    "channel_post",
    "edited_channel_post",
    "inline_query",
    "chosen_inline_result",
    "shipping_query",
    "pre_checkout_query",
    "poll",
    "poll_answer",
    "my_chat_member",
    "chat_member",
    "chat_join_request",
    "chat_boost",
    "removed_chat_boost",
    "message_reaction",
    "message_reaction_count",
    "business_connection",
    "deleted_business_messages",
    "business_message",
    "edited_business_message",
    "purchased_paid_media",
)

ids = (*all_types, "callback_query_without_message")


@pytest.fixture(scope="module", params=params, ids=ids)
def update(request):
    return Update(update_id=UpdateTestBase.update_id, **request.param)


class UpdateTestBase:
    update_id = 868573637


class TestUpdateWithoutRequest(UpdateTestBase):
    def test_slot_behaviour(self):
        update = Update(self.update_id)
        for attr in update.__slots__:
            assert getattr(update, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(update)) == len(set(mro_slots(update))), "duplicate slot"

    @pytest.mark.parametrize("paramdict", argvalues=params, ids=ids)
    def test_de_json(self, offline_bot, paramdict):
        json_dict = {"update_id": self.update_id}
        # Convert the single update 'item' to a dict of that item and apply it to the json_dict
        json_dict.update({k: v.to_dict() for k, v in paramdict.items()})
        update = Update.de_json(json_dict, offline_bot)
        assert update.api_kwargs == {}

        assert update.update_id == self.update_id

        # Make sure only one thing in the update (other than update_id) is not None
        i = 0
        for _type in all_types:
            if getattr(update, _type) is not None:
                i += 1
                assert getattr(update, _type) == paramdict[_type]
        assert i == 1

    def test_to_dict(self, update):
        update_dict = update.to_dict()

        assert isinstance(update_dict, dict)
        assert update_dict["update_id"] == update.update_id
        for _type in all_types:
            if getattr(update, _type) is not None:
                assert update_dict[_type] == getattr(update, _type).to_dict()

    def test_equality(self):
        a = Update(self.update_id, message=message)
        b = Update(self.update_id, message=message)
        c = Update(self.update_id)
        d = Update(0, message=message)
        e = User(self.update_id, "", False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    def test_effective_chat(self, update):
        # Test that it's sometimes None per docstring
        chat = update.effective_chat
        if not (
            update.inline_query is not None
            or update.chosen_inline_result is not None
            or (update.callback_query is not None and update.callback_query.message is None)
            or update.shipping_query is not None
            or update.pre_checkout_query is not None
            or update.poll is not None
            or update.poll_answer is not None
            or update.business_connection is not None
            or update.purchased_paid_media is not None
        ):
            assert chat.id == 1
        else:
            assert chat is None

    def test_effective_user(self, update):
        # Test that it's sometimes None per docstring
        user = update.effective_user
        if not (
            update.channel_post is not None
            or update.edited_channel_post is not None
            or update.poll is not None
            or update.chat_boost is not None
            or update.removed_chat_boost is not None
            or update.message_reaction_count is not None
            or update.deleted_business_messages is not None
        ):
            assert user.id == 1
        else:
            assert user is None

    def test_effective_sender_non_anonymous(self, update):
        update = deepcopy(update)
        # Simulate 'Remain anonymous' being turned off
        if message := (update.message or update.edited_message):
            message._unfreeze()
            message.sender_chat = None
        elif reaction := (update.message_reaction):
            reaction._unfreeze()
            reaction.actor_chat = None
        elif answer := (update.poll_answer):
            answer._unfreeze()
            answer.voter_chat = None

        # Test that it's sometimes None per docstring
        sender = update.effective_sender
        if not (
            update.poll is not None
            or update.chat_boost is not None
            or update.removed_chat_boost is not None
            or update.message_reaction_count is not None
            or update.deleted_business_messages is not None
        ):
            if update.channel_post or update.edited_channel_post:
                assert isinstance(sender, Chat)
            else:
                assert isinstance(sender, User)

        else:
            assert sender is None

        cached = update.effective_sender
        assert cached is sender

    def test_effective_sender_anonymous(self, update):
        update = deepcopy(update)
        # Simulate 'Remain anonymous' being turned on
        if message := (update.message or update.edited_message):
            message._unfreeze()
            message.from_user = None
        elif reaction := (update.message_reaction):
            reaction._unfreeze()
            reaction.user = None
        elif answer := (update.poll_answer):
            answer._unfreeze()
            answer.user = None

        # Test that it's sometimes None per docstring
        sender = update.effective_sender
        if not (
            update.poll is not None
            or update.chat_boost is not None
            or update.removed_chat_boost is not None
            or update.message_reaction_count is not None
            or update.deleted_business_messages is not None
        ):
            if (
                update.message
                or update.edited_message
                or update.channel_post
                or update.edited_channel_post
                or update.message_reaction
                or update.poll_answer
            ):
                assert isinstance(sender, Chat)
            else:
                assert isinstance(sender, User)
        else:
            assert sender is None

        cached = update.effective_sender
        assert cached is sender

    def test_effective_message(self, update):
        # Test that it's sometimes None per docstring
        eff_message = update.effective_message
        if not (
            update.inline_query is not None
            or update.chosen_inline_result is not None
            or (update.callback_query is not None and update.callback_query.message is None)
            or update.shipping_query is not None
            or update.pre_checkout_query is not None
            or update.poll is not None
            or update.poll_answer is not None
            or update.my_chat_member is not None
            or update.chat_member is not None
            or update.chat_join_request is not None
            or update.chat_boost is not None
            or update.removed_chat_boost is not None
            or update.message_reaction is not None
            or update.message_reaction_count is not None
            or update.deleted_business_messages is not None
            or update.business_connection is not None
            or update.purchased_paid_media is not None
        ):
            assert eff_message.message_id == message.message_id
        else:
            assert eff_message is None

    def test_effective_message_inaccessible(self):
        update = Update(
            update_id=1,
            callback_query=CallbackQuery(
                "id",
                User(1, "", False),
                "chat",
                message=InaccessibleMessage(message_id=1, chat=Chat(1, "")),
            ),
        )
        with pytest.warns(
            PTBUserWarning,
            match="update.callback_query` is not `None`, but of type `InaccessibleMessage`",
        ) as record:
            assert update.effective_message is None

        assert record[0].filename == __file__
