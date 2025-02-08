# python-telegram-bot - a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
# by the python-telegram-bot contributors <devs@python-telegram-bot.org>
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
    Chat,
    ChatBoost,
    ChatBoostAdded,
    ChatBoostRemoved,
    ChatBoostSource,
    ChatBoostSourceGiftCode,
    ChatBoostSourceGiveaway,
    ChatBoostSourcePremium,
    ChatBoostUpdated,
    Dice,
    User,
    UserChatBoosts,
)
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import ChatBoostSources
from telegram.request import RequestData
from tests.auxil.dummy_objects import get_dummy_object_json_dict
from tests.auxil.slots import mro_slots


class ChatBoostDefaults:
    source = ChatBoostSource.PREMIUM
    chat_id = 1
    boost_id = "2"
    giveaway_message_id = 3
    is_unclaimed = False
    chat = Chat(1, "group")
    user = User(1, "user", False)
    date = dtm.datetime.now(dtm.timezone.utc).replace(microsecond=0)
    default_source = ChatBoostSourcePremium(user)
    prize_star_count = 99
    boost = ChatBoost(
        boost_id=boost_id,
        add_date=date,
        expiration_date=date,
        source=default_source,
    )


@pytest.fixture(scope="module")
def chat_boost_source():
    return ChatBoostSource(
        source=ChatBoostDefaults.source,
    )


class TestChatBoostSourceWithoutRequest(ChatBoostDefaults):
    def test_slot_behaviour(self, chat_boost_source):
        inst = chat_boost_source
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self, chat_boost_source):
        assert type(ChatBoostSource("premium").source) is ChatBoostSources
        assert ChatBoostSource("unknown").source == "unknown"

    def test_de_json(self, offline_bot):
        json_dict = {
            "source": "unknown",
        }
        cbs = ChatBoostSource.de_json(json_dict, offline_bot)

        assert cbs.api_kwargs == {}
        assert cbs.source == "unknown"

    @pytest.mark.parametrize(
        ("cb_source", "subclass"),
        [
            ("premium", ChatBoostSourcePremium),
            ("gift_code", ChatBoostSourceGiftCode),
            ("giveaway", ChatBoostSourceGiveaway),
        ],
    )
    def test_de_json_subclass(self, offline_bot, cb_source, subclass):
        json_dict = {
            "source": cb_source,
            "user": ChatBoostDefaults.user.to_dict(),
            "giveaway_message_id": ChatBoostDefaults.giveaway_message_id,
        }
        cbs = ChatBoostSource.de_json(json_dict, offline_bot)

        assert type(cbs) is subclass
        assert set(cbs.api_kwargs.keys()) == set(json_dict.keys()) - set(subclass.__slots__) - {
            "source"
        }
        assert cbs.source == cb_source

    def test_to_dict(self, chat_boost_source):
        chat_boost_source_dict = chat_boost_source.to_dict()

        assert isinstance(chat_boost_source_dict, dict)
        assert chat_boost_source_dict["source"] == chat_boost_source.source

    def test_equality(self, chat_boost_source):
        a = chat_boost_source
        b = ChatBoostSource(source=ChatBoostDefaults.source)
        c = ChatBoostSource(source="unknown")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture(scope="module")
def chat_boost_source_premium():
    return ChatBoostSourcePremium(
        user=TestChatBoostSourcePremiumWithoutRequest.user,
    )


class TestChatBoostSourcePremiumWithoutRequest(ChatBoostDefaults):
    source = ChatBoostSources.PREMIUM

    def test_slot_behaviour(self, chat_boost_source_premium):
        inst = chat_boost_source_premium
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "user": self.user.to_dict(),
        }
        cbsp = ChatBoostSourcePremium.de_json(json_dict, offline_bot)

        assert cbsp.api_kwargs == {}
        assert cbsp.user == self.user

    def test_to_dict(self, chat_boost_source_premium):
        chat_boost_source_premium_dict = chat_boost_source_premium.to_dict()

        assert isinstance(chat_boost_source_premium_dict, dict)
        assert chat_boost_source_premium_dict["source"] == self.source
        assert chat_boost_source_premium_dict["user"] == self.user.to_dict()

    def test_equality(self, chat_boost_source_premium):
        a = chat_boost_source_premium
        b = ChatBoostSourcePremium(user=self.user)
        c = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)


@pytest.fixture(scope="module")
def chat_boost_source_gift_code():
    return ChatBoostSourceGiftCode(
        user=TestChatBoostSourceGiftCodeWithoutRequest.user,
    )


class TestChatBoostSourceGiftCodeWithoutRequest(ChatBoostDefaults):
    source = ChatBoostSources.GIFT_CODE

    def test_slot_behaviour(self, chat_boost_source_gift_code):
        inst = chat_boost_source_gift_code
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "user": self.user.to_dict(),
        }
        cbsgc = ChatBoostSourceGiftCode.de_json(json_dict, offline_bot)

        assert cbsgc.api_kwargs == {}
        assert cbsgc.user == self.user

    def test_to_dict(self, chat_boost_source_gift_code):
        chat_boost_source_gift_code_dict = chat_boost_source_gift_code.to_dict()

        assert isinstance(chat_boost_source_gift_code_dict, dict)
        assert chat_boost_source_gift_code_dict["source"] == self.source
        assert chat_boost_source_gift_code_dict["user"] == self.user.to_dict()

    def test_equality(self, chat_boost_source_gift_code):
        a = chat_boost_source_gift_code
        b = ChatBoostSourceGiftCode(user=self.user)
        c = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)


@pytest.fixture(scope="module")
def chat_boost_source_giveaway():
    return ChatBoostSourceGiveaway(
        user=TestChatBoostSourceGiveawayWithoutRequest.user,
        giveaway_message_id=TestChatBoostSourceGiveawayWithoutRequest.giveaway_message_id,
    )


class TestChatBoostSourceGiveawayWithoutRequest(ChatBoostDefaults):
    source = ChatBoostSources.GIVEAWAY

    def test_slot_behaviour(self, chat_boost_source_giveaway):
        inst = chat_boost_source_giveaway
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "user": self.user.to_dict(),
            "giveaway_message_id": self.giveaway_message_id,
        }
        cbsg = ChatBoostSourceGiveaway.de_json(json_dict, offline_bot)

        assert cbsg.api_kwargs == {}
        assert cbsg.user == self.user
        assert cbsg.giveaway_message_id == self.giveaway_message_id

    def test_to_dict(self, chat_boost_source_giveaway):
        chat_boost_source_giveaway_dict = chat_boost_source_giveaway.to_dict()

        assert isinstance(chat_boost_source_giveaway_dict, dict)
        assert chat_boost_source_giveaway_dict["source"] == self.source
        assert chat_boost_source_giveaway_dict["user"] == self.user.to_dict()
        assert chat_boost_source_giveaway_dict["giveaway_message_id"] == self.giveaway_message_id

    def test_equality(self, chat_boost_source_giveaway):
        a = chat_boost_source_giveaway
        b = ChatBoostSourceGiveaway(user=self.user, giveaway_message_id=self.giveaway_message_id)
        c = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)


@pytest.fixture(scope="module")
def chat_boost():
    return ChatBoost(
        boost_id=ChatBoostDefaults.boost_id,
        add_date=ChatBoostDefaults.date,
        expiration_date=ChatBoostDefaults.date,
        source=ChatBoostDefaults.default_source,
    )


class TestChatBoostWithoutRequest(ChatBoostDefaults):
    def test_slot_behaviour(self, chat_boost):
        inst = chat_boost
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, chat_boost):
        json_dict = {
            "boost_id": self.boost_id,
            "add_date": to_timestamp(self.date),
            "expiration_date": to_timestamp(self.date),
            "source": self.default_source.to_dict(),
        }
        cb = ChatBoost.de_json(json_dict, offline_bot)

        assert cb.api_kwargs == {}
        assert cb.boost_id == self.boost_id
        assert (cb.add_date) == self.date
        assert (cb.expiration_date) == self.date
        assert cb.source == self.default_source

    def test_de_json_localization(self, offline_bot, raw_bot, tz_bot):
        json_dict = {
            "boost_id": "2",
            "add_date": to_timestamp(self.date),
            "expiration_date": to_timestamp(self.date),
            "source": self.default_source.to_dict(),
        }

        cb_bot = ChatBoost.de_json(json_dict, offline_bot)
        cb_raw = ChatBoost.de_json(json_dict, raw_bot)
        cb_tz = ChatBoost.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        message_offset = cb_tz.add_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(cb_tz.add_date.replace(tzinfo=None))

        assert cb_raw.add_date.tzinfo == UTC
        assert cb_bot.add_date.tzinfo == UTC
        assert message_offset == tz_bot_offset

    def test_to_dict(self, chat_boost):
        chat_boost_dict = chat_boost.to_dict()

        assert isinstance(chat_boost_dict, dict)
        assert chat_boost_dict["boost_id"] == chat_boost.boost_id
        assert chat_boost_dict["add_date"] == to_timestamp(chat_boost.add_date)
        assert chat_boost_dict["expiration_date"] == to_timestamp(chat_boost.expiration_date)
        assert chat_boost_dict["source"] == chat_boost.source.to_dict()

    def test_equality(self):
        a = ChatBoost(
            boost_id="2",
            add_date=self.date,
            expiration_date=self.date,
            source=self.default_source,
        )
        b = ChatBoost(
            boost_id="2",
            add_date=self.date,
            expiration_date=self.date,
            source=self.default_source,
        )
        c = ChatBoost(
            boost_id="3",
            add_date=self.date,
            expiration_date=self.date,
            source=self.default_source,
        )

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)


@pytest.fixture(scope="module")
def chat_boost_updated(chat_boost):
    return ChatBoostUpdated(
        chat=ChatBoostDefaults.chat,
        boost=chat_boost,
    )


class TestChatBoostUpdatedWithoutRequest(ChatBoostDefaults):
    def test_slot_behaviour(self, chat_boost_updated):
        inst = chat_boost_updated
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, chat_boost):
        json_dict = {
            "chat": self.chat.to_dict(),
            "boost": self.boost.to_dict(),
        }
        cbu = ChatBoostUpdated.de_json(json_dict, offline_bot)

        assert cbu.api_kwargs == {}
        assert cbu.chat == self.chat
        assert cbu.boost == self.boost

    def test_to_dict(self, chat_boost_updated):
        chat_boost_updated_dict = chat_boost_updated.to_dict()

        assert isinstance(chat_boost_updated_dict, dict)
        assert chat_boost_updated_dict["chat"] == chat_boost_updated.chat.to_dict()
        assert chat_boost_updated_dict["boost"] == chat_boost_updated.boost.to_dict()

    def test_equality(self):
        a = ChatBoostUpdated(
            chat=Chat(1, "group"),
            boost=ChatBoost(
                boost_id="2",
                add_date=self.date,
                expiration_date=self.date,
                source=self.default_source,
            ),
        )
        b = ChatBoostUpdated(
            chat=Chat(1, "group"),
            boost=ChatBoost(
                boost_id="2",
                add_date=self.date,
                expiration_date=self.date,
                source=self.default_source,
            ),
        )
        c = ChatBoostUpdated(
            chat=Chat(2, "group"),
            boost=ChatBoost(
                boost_id="3",
                add_date=self.date,
                expiration_date=self.date,
                source=self.default_source,
            ),
        )

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)


@pytest.fixture(scope="module")
def chat_boost_removed():
    return ChatBoostRemoved(
        chat=ChatBoostDefaults.chat,
        boost_id=ChatBoostDefaults.boost_id,
        remove_date=ChatBoostDefaults.date,
        source=ChatBoostDefaults.default_source,
    )


class TestChatBoostRemovedWithoutRequest(ChatBoostDefaults):
    def test_slot_behaviour(self, chat_boost_removed):
        inst = chat_boost_removed
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, chat_boost_removed):
        json_dict = {
            "chat": self.chat.to_dict(),
            "boost_id": self.boost_id,
            "remove_date": to_timestamp(self.date),
            "source": self.default_source.to_dict(),
        }
        cbr = ChatBoostRemoved.de_json(json_dict, offline_bot)

        assert cbr.api_kwargs == {}
        assert cbr.chat == self.chat
        assert cbr.boost_id == self.boost_id
        assert cbr.remove_date == self.date
        assert cbr.source == self.default_source

    def test_de_json_localization(self, offline_bot, raw_bot, tz_bot):
        json_dict = {
            "chat": self.chat.to_dict(),
            "boost_id": self.boost_id,
            "remove_date": to_timestamp(self.date),
            "source": self.default_source.to_dict(),
        }

        cbr_bot = ChatBoostRemoved.de_json(json_dict, offline_bot)
        cbr_raw = ChatBoostRemoved.de_json(json_dict, raw_bot)
        cbr_tz = ChatBoostRemoved.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        message_offset = cbr_tz.remove_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(cbr_tz.remove_date.replace(tzinfo=None))

        assert cbr_raw.remove_date.tzinfo == UTC
        assert cbr_bot.remove_date.tzinfo == UTC
        assert message_offset == tz_bot_offset

    def test_to_dict(self, chat_boost_removed):
        chat_boost_removed_dict = chat_boost_removed.to_dict()

        assert isinstance(chat_boost_removed_dict, dict)
        assert chat_boost_removed_dict["chat"] == chat_boost_removed.chat.to_dict()
        assert chat_boost_removed_dict["boost_id"] == chat_boost_removed.boost_id
        assert chat_boost_removed_dict["remove_date"] == to_timestamp(
            chat_boost_removed.remove_date
        )
        assert chat_boost_removed_dict["source"] == chat_boost_removed.source.to_dict()

    def test_equality(self):
        a = ChatBoostRemoved(
            chat=Chat(1, "group"),
            boost_id="2",
            remove_date=self.date,
            source=self.default_source,
        )
        b = ChatBoostRemoved(
            chat=Chat(1, "group"),
            boost_id="2",
            remove_date=self.date,
            source=self.default_source,
        )
        c = ChatBoostRemoved(
            chat=Chat(2, "group"),
            boost_id="3",
            remove_date=self.date,
            source=self.default_source,
        )

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)


@pytest.fixture(scope="module")
def user_chat_boosts(chat_boost):
    return UserChatBoosts(
        boosts=[chat_boost],
    )


class TestUserChatBoostsWithoutRequest(ChatBoostDefaults):
    def test_slot_behaviour(self, user_chat_boosts):
        inst = user_chat_boosts
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, user_chat_boosts):
        json_dict = {
            "boosts": [
                self.boost.to_dict(),
            ]
        }
        ucb = UserChatBoosts.de_json(json_dict, offline_bot)

        assert ucb.api_kwargs == {}
        assert ucb.boosts[0] == self.boost

    def test_to_dict(self, user_chat_boosts):
        user_chat_boosts_dict = user_chat_boosts.to_dict()

        assert isinstance(user_chat_boosts_dict, dict)
        assert isinstance(user_chat_boosts_dict["boosts"], list)
        assert user_chat_boosts_dict["boosts"][0] == user_chat_boosts.boosts[0].to_dict()

    async def test_get_user_chat_boosts(self, monkeypatch, offline_bot):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            chat_id = data["chat_id"] == "3"
            user_id = data["user_id"] == "2"
            if not all((chat_id, user_id)):
                pytest.fail("I got wrong parameters in post")
            return get_dummy_object_json_dict(UserChatBoosts)

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)

        assert await offline_bot.get_user_chat_boosts("3", 2)


class TestUserChatBoostsWithRequest(ChatBoostDefaults):
    async def test_get_user_chat_boosts(self, bot, channel_id, chat_id):
        chat_boosts = await bot.get_user_chat_boosts(channel_id, chat_id)
        assert isinstance(chat_boosts, UserChatBoosts)


class TestChatBoostAddedWithoutRequest:
    boost_count = 100

    def test_slot_behaviour(self):
        action = ChatBoostAdded(8)
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self):
        json_dict = {"boost_count": self.boost_count}
        chat_boost_added = ChatBoostAdded.de_json(json_dict, None)
        assert chat_boost_added.api_kwargs == {}

        assert chat_boost_added.boost_count == self.boost_count

    def test_to_dict(self):
        chat_boost_added = ChatBoostAdded(self.boost_count)
        chat_boost_added_dict = chat_boost_added.to_dict()

        assert isinstance(chat_boost_added_dict, dict)
        assert chat_boost_added_dict["boost_count"] == self.boost_count

    def test_equality(self):
        a = ChatBoostAdded(100)
        b = ChatBoostAdded(100)
        c = ChatBoostAdded(50)
        d = Chat(1, "")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
