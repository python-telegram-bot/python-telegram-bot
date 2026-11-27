# python-telegram-bot - a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
from telegram._utils.datetime import to_timestamp
from telegram.constants import ChatBoostSources
from telegram.request import RequestData
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.dummy_objects import get_dummy_object_json_dict
from tests.auxil.slots import mro_slots


class ChatBoostDefaults:
    source = ChatBoostSource.PREMIUM
    chat_id = 1
    boost_id = "2"
    giveaway_message_id = 3
    is_unclaimed = True
    chat = Chat(1, "group")
    user = User(1, "user", False)
    date = dtm.datetime.now(dtm.UTC).replace(microsecond=0)
    expiration_date = date + dtm.timedelta(days=7)
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


class TestChatBoostSourceWithoutRequest(ChatBoostDefaults, DeserializationTestBase):
    de_json_class = ChatBoostSource

    def test_slot_behaviour(self, chat_boost_source):
        inst = chat_boost_source
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self, chat_boost_source):
        assert type(ChatBoostSource("premium").source) is ChatBoostSources
        assert ChatBoostSource("unknown").source == "unknown"

    @pytest.fixture
    def de_json_dict(self):
        # An unknown source, so that ChatBoostSource.de_json does not dispatch to a subclass
        return {"source": "unknown"}

    def test_de_json(self, offline_bot, de_json_dict):
        cbs = ChatBoostSource.de_json(de_json_dict, offline_bot)
        assert type(cbs) is ChatBoostSource
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


class TestChatBoostSourcePremiumWithoutRequest(ChatBoostDefaults, DeserializationTestBase):
    de_json_class = ChatBoostSourcePremium
    source = ChatBoostSources.PREMIUM

    def test_slot_behaviour(self, chat_boost_source_premium):
        inst = chat_boost_source_premium
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"user": self.user.to_dict()}

    def test_de_json(self, offline_bot, de_json_dict):
        cbsp = ChatBoostSourcePremium.de_json(de_json_dict, offline_bot)
        assert type(cbsp) is ChatBoostSourcePremium
        assert cbsp.api_kwargs == {}
        assert cbsp.source == self.source
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


class TestChatBoostSourceGiftCodeWithoutRequest(ChatBoostDefaults, DeserializationTestBase):
    de_json_class = ChatBoostSourceGiftCode
    source = ChatBoostSources.GIFT_CODE

    def test_slot_behaviour(self, chat_boost_source_gift_code):
        inst = chat_boost_source_gift_code
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"user": self.user.to_dict()}

    def test_de_json(self, offline_bot, de_json_dict):
        cbsgc = ChatBoostSourceGiftCode.de_json(de_json_dict, offline_bot)
        assert type(cbsgc) is ChatBoostSourceGiftCode
        assert cbsgc.api_kwargs == {}
        assert cbsgc.source == self.source
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


class TestChatBoostSourceGiveawayWithoutRequest(ChatBoostDefaults, DeserializationTestBase):
    de_json_class = ChatBoostSourceGiveaway
    source = ChatBoostSources.GIVEAWAY

    def test_slot_behaviour(self, chat_boost_source_giveaway):
        inst = chat_boost_source_giveaway
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {
            "giveaway_message_id": self.giveaway_message_id,
            "user": self.user.to_dict(),
            "is_unclaimed": self.is_unclaimed,
            "prize_star_count": self.prize_star_count,
        }

    def test_de_json(self, offline_bot, de_json_dict):
        cbsg = ChatBoostSourceGiveaway.de_json(de_json_dict, offline_bot)
        assert type(cbsg) is ChatBoostSourceGiveaway
        assert cbsg.api_kwargs == {}
        assert cbsg.source == self.source
        assert cbsg.giveaway_message_id == self.giveaway_message_id
        assert cbsg.user == self.user
        assert cbsg.is_unclaimed == self.is_unclaimed
        assert cbsg.prize_star_count == self.prize_star_count

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


class TestChatBoostWithoutRequest(ChatBoostDefaults, DeserializationTestBase):
    de_json_class = ChatBoost

    def test_slot_behaviour(self, chat_boost):
        inst = chat_boost
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {
            "boost_id": self.boost_id,
            "add_date": to_timestamp(self.date),
            "expiration_date": to_timestamp(self.expiration_date),
            "source": self.default_source.to_dict(),
        }

    def test_de_json(self, offline_bot, de_json_dict):
        cb = ChatBoost.de_json(de_json_dict, offline_bot)
        assert type(cb) is ChatBoost
        assert cb.api_kwargs == {}
        assert cb.boost_id == self.boost_id
        assert cb.add_date == self.date
        assert cb.expiration_date == self.expiration_date
        assert cb.source == self.default_source

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


class TestChatBoostUpdatedWithoutRequest(ChatBoostDefaults, DeserializationTestBase):
    de_json_class = ChatBoostUpdated

    def test_slot_behaviour(self, chat_boost_updated):
        inst = chat_boost_updated
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"chat": self.chat.to_dict(), "boost": self.boost.to_dict()}

    def test_de_json(self, offline_bot, de_json_dict):
        cbu = ChatBoostUpdated.de_json(de_json_dict, offline_bot)
        assert type(cbu) is ChatBoostUpdated
        assert cbu.api_kwargs == {}
        assert cbu.chat == self.chat
        assert cbu.boost == self.boost

    @pytest.mark.xfail(
        strict=True,
        reason="`_id_attrs` uses `chat.id`, so a missing `chat` raises an AttributeError",
    )
    def test_de_json_missing_required_args(self, offline_bot, de_json_dict):
        super().test_de_json_missing_required_args(offline_bot, de_json_dict)

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


class TestChatBoostRemovedWithoutRequest(ChatBoostDefaults, DeserializationTestBase):
    de_json_class = ChatBoostRemoved

    def test_slot_behaviour(self, chat_boost_removed):
        inst = chat_boost_removed
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {
            "chat": self.chat.to_dict(),
            "boost_id": self.boost_id,
            "remove_date": to_timestamp(self.date),
            "source": self.default_source.to_dict(),
        }

    def test_de_json(self, offline_bot, de_json_dict):
        cbr = ChatBoostRemoved.de_json(de_json_dict, offline_bot)
        assert type(cbr) is ChatBoostRemoved
        assert cbr.api_kwargs == {}
        assert cbr.chat == self.chat
        assert cbr.boost_id == self.boost_id
        assert cbr.remove_date == self.date
        assert cbr.source == self.default_source

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


class TestUserChatBoostsWithoutRequest(ChatBoostDefaults, DeserializationTestBase):
    de_json_class = UserChatBoosts

    def test_slot_behaviour(self, user_chat_boosts):
        inst = user_chat_boosts
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"boosts": [self.boost.to_dict()]}

    def test_de_json(self, offline_bot, de_json_dict):
        ucb = UserChatBoosts.de_json(de_json_dict, offline_bot)
        assert type(ucb) is UserChatBoosts
        assert ucb.api_kwargs == {}
        assert ucb.boosts == (self.boost,)

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


class TestChatBoostAddedWithoutRequest(DeserializationTestBase):
    de_json_class = ChatBoostAdded
    boost_count = 100

    def test_slot_behaviour(self):
        action = ChatBoostAdded(8)
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"boost_count": self.boost_count}

    def test_de_json(self, offline_bot, de_json_dict):
        chat_boost_added = ChatBoostAdded.de_json(de_json_dict, offline_bot)
        assert type(chat_boost_added) is ChatBoostAdded
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
