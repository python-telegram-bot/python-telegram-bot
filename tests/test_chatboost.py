# python-telegram-bot - a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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

import datetime
import inspect
from copy import deepcopy

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
from tests.auxil.slots import mro_slots


class ChatBoostDefaults:
    chat_id = 1
    boost_id = "2"
    giveaway_message_id = 3
    is_unclaimed = False
    chat = Chat(1, "group")
    user = User(1, "user", False)
    date = to_timestamp(datetime.datetime.utcnow())
    default_source = ChatBoostSourcePremium(user)


@pytest.fixture(scope="module")
def chat_boost_removed():
    return ChatBoostRemoved(
        chat=ChatBoostDefaults.chat,
        boost_id=ChatBoostDefaults.boost_id,
        remove_date=ChatBoostDefaults.date,
        source=ChatBoostDefaults.default_source,
    )


@pytest.fixture(scope="module")
def chat_boost():
    return ChatBoost(
        boost_id=ChatBoostDefaults.boost_id,
        add_date=ChatBoostDefaults.date,
        expiration_date=ChatBoostDefaults.date,
        source=ChatBoostDefaults.default_source,
    )


@pytest.fixture(scope="module")
def chat_boost_updated(chat_boost):
    return ChatBoostUpdated(
        chat=ChatBoostDefaults.chat,
        boost=chat_boost,
    )


def chat_boost_source_gift_code():
    return ChatBoostSourceGiftCode(
        user=ChatBoostDefaults.user,
    )


def chat_boost_source_giveaway():
    return ChatBoostSourceGiveaway(
        user=ChatBoostDefaults.user,
        giveaway_message_id=ChatBoostDefaults.giveaway_message_id,
        is_unclaimed=ChatBoostDefaults.is_unclaimed,
    )


def chat_boost_source_premium():
    return ChatBoostSourcePremium(
        user=ChatBoostDefaults.user,
    )


@pytest.fixture(scope="module")
def user_chat_boosts(chat_boost):
    return UserChatBoosts(
        boosts=[chat_boost],
    )


@pytest.fixture()
def chat_boost_source(request):
    return request.param()


ignored = ["self", "api_kwargs"]


def make_json_dict(instance: ChatBoostSource, include_optional_args: bool = False) -> dict:
    """Used to make the json dict which we use for testing de_json. Similar to iter_args()"""
    json_dict = {"source": instance.source}
    sig = inspect.signature(instance.__class__.__init__)

    for param in sig.parameters.values():
        if param.name in ignored:  # ignore irrelevant params
            continue

        val = getattr(instance, param.name)
        if hasattr(val, "to_dict"):  # convert the user object or any future ones to dict.
            val = val.to_dict()
        json_dict[param.name] = val

    return json_dict


def iter_args(
    instance: ChatBoostSource, de_json_inst: ChatBoostSource, include_optional: bool = False
):
    """
    We accept both the regular instance and de_json created instance and iterate over them for
    easy one line testing later one.
    """
    yield instance.source, de_json_inst.source  # yield this here cause it's not available in sig.

    sig = inspect.signature(instance.__class__.__init__)
    for param in sig.parameters.values():
        if param.name in ignored:
            continue
        inst_at, json_at = getattr(instance, param.name), getattr(de_json_inst, param.name)
        if isinstance(json_at, datetime.datetime):  # Convert datetime to int
            json_at = to_timestamp(json_at)
        if (
            param.default is not inspect.Parameter.empty and include_optional
        ) or param.default is inspect.Parameter.empty:
            yield inst_at, json_at


@pytest.mark.parametrize(
    "chat_boost_source",
    [
        chat_boost_source_gift_code,
        chat_boost_source_giveaway,
        chat_boost_source_premium,
    ],
    indirect=True,
)
class TestChatBoostSourceTypesWithoutRequest:
    def test_slot_behaviour(self, chat_boost_source):
        inst = chat_boost_source
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json_required_args(self, bot, chat_boost_source):
        cls = chat_boost_source.__class__
        assert cls.de_json({}, bot) is None
        assert ChatBoost.de_json({}, bot) is None

        json_dict = make_json_dict(chat_boost_source)
        const_boost_source = ChatBoostSource.de_json(json_dict, bot)
        assert const_boost_source.api_kwargs == {}

        assert isinstance(const_boost_source, ChatBoostSource)
        assert isinstance(const_boost_source, cls)
        for chat_mem_type_at, const_chat_mem_at in iter_args(
            chat_boost_source, const_boost_source
        ):
            assert chat_mem_type_at == const_chat_mem_at

    def test_de_json_all_args(self, bot, chat_boost_source):
        json_dict = make_json_dict(chat_boost_source, include_optional_args=True)
        const_boost_source = ChatBoostSource.de_json(json_dict, bot)
        assert const_boost_source.api_kwargs == {}

        assert isinstance(const_boost_source, ChatBoostSource)
        assert isinstance(const_boost_source, chat_boost_source.__class__)
        for c_mem_type_at, const_c_mem_at in iter_args(
            chat_boost_source, const_boost_source, True
        ):
            assert c_mem_type_at == const_c_mem_at

    def test_de_json_invalid_source(self, chat_boost_source, bot):
        json_dict = {"source": "invalid"}
        chat_boost_source = ChatBoostSource.de_json(json_dict, bot)

        assert type(chat_boost_source) is ChatBoostSource
        assert chat_boost_source.source == "invalid"

    def test_de_json_subclass(self, chat_boost_source, bot):
        """This makes sure that e.g. ChatBoostSourcePremium(data, bot) never returns a
        ChatBoostSourceGiftCode instance."""
        cls = chat_boost_source.__class__
        json_dict = make_json_dict(chat_boost_source, True)
        assert type(cls.de_json(json_dict, bot)) is cls

    def test_to_dict(self, chat_boost_source):
        chat_boost_dict = chat_boost_source.to_dict()

        assert isinstance(chat_boost_dict, dict)
        assert chat_boost_dict["source"] == chat_boost_source.source
        assert chat_boost_dict["user"] == chat_boost_source.user.to_dict()

        for slot in chat_boost_source.__slots__:  # additional verification for the optional args
            if slot == "user":  # we already test "user" above:
                continue
            assert getattr(chat_boost_source, slot) == chat_boost_dict[slot]

    def test_equality(self, chat_boost_source):
        a = ChatBoostSource(source="status")
        b = ChatBoostSource(source="status")
        c = chat_boost_source
        d = deepcopy(chat_boost_source)
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)

    def test_enum_init(self, chat_boost_source):
        cbs = ChatBoostSource(source="foo")
        assert cbs.source == "foo"
        cbs = ChatBoostSource(source="premium")
        assert cbs.source == ChatBoostSources.PREMIUM


class TestChatBoostWithoutRequest(ChatBoostDefaults):
    def test_slot_behaviour(self, chat_boost):
        inst = chat_boost
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, chat_boost):
        json_dict = {
            "boost_id": "2",
            "add_date": self.date,
            "expiration_date": self.date,
            "source": self.default_source.to_dict(),
        }
        cb = ChatBoost.de_json(json_dict, bot)

        assert isinstance(cb, ChatBoost)
        assert isinstance(cb.add_date, datetime.datetime)
        assert isinstance(cb.expiration_date, datetime.datetime)
        assert isinstance(cb.source, ChatBoostSource)
        with cb._unfrozen():
            cb.add_date = to_timestamp(cb.add_date)
            cb.expiration_date = to_timestamp(cb.expiration_date)

        # We don't compare cbu.boost to self.boost because we have to update the _id_attrs (sigh)
        for slot in cb.__slots__:
            assert getattr(cb, slot) == getattr(chat_boost, slot), f"attribute {slot} differs"

    def test_de_json_localization(self, bot, raw_bot, tz_bot):
        json_dict = {
            "boost_id": "2",
            "add_date": self.date,
            "expiration_date": self.date,
            "source": self.default_source.to_dict(),
        }

        cb_bot = ChatBoost.de_json(json_dict, bot)
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
        assert chat_boost_dict["add_date"] == chat_boost.add_date
        assert chat_boost_dict["expiration_date"] == chat_boost.expiration_date
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


class TestChatBoostUpdatedWithoutRequest(ChatBoostDefaults):
    def test_slot_behaviour(self, chat_boost_updated):
        inst = chat_boost_updated
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, chat_boost):
        json_dict = {
            "chat": self.chat.to_dict(),
            "boost": {
                "boost_id": "2",
                "add_date": self.date,
                "expiration_date": self.date,
                "source": self.default_source.to_dict(),
            },
        }
        cbu = ChatBoostUpdated.de_json(json_dict, bot)

        assert isinstance(cbu, ChatBoostUpdated)
        assert cbu.chat == self.chat
        # We don't compare cbu.boost to chat_boost because we have to update the _id_attrs (sigh)
        with cbu.boost._unfrozen():
            cbu.boost.add_date = to_timestamp(cbu.boost.add_date)
            cbu.boost.expiration_date = to_timestamp(cbu.boost.expiration_date)
        for slot in cbu.boost.__slots__:  # Assumes _id_attrs are same as slots
            assert getattr(cbu.boost, slot) == getattr(chat_boost, slot), f"attr {slot} differs"

    # no need to test localization since that is already tested in the above class.

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


class TestChatBoostRemovedWithoutRequest(ChatBoostDefaults):
    def test_slot_behaviour(self, chat_boost_removed):
        inst = chat_boost_removed
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, chat_boost_removed):
        json_dict = {
            "chat": self.chat.to_dict(),
            "boost_id": "2",
            "remove_date": self.date,
            "source": self.default_source.to_dict(),
        }
        cbr = ChatBoostRemoved.de_json(json_dict, bot)

        assert isinstance(cbr, ChatBoostRemoved)
        assert cbr.chat == self.chat
        assert cbr.boost_id == self.boost_id
        assert to_timestamp(cbr.remove_date) == self.date
        assert cbr.source == self.default_source

    def test_de_json_localization(self, bot, raw_bot, tz_bot):
        json_dict = {
            "chat": self.chat.to_dict(),
            "boost_id": "2",
            "remove_date": self.date,
            "source": self.default_source.to_dict(),
        }

        cbr_bot = ChatBoostRemoved.de_json(json_dict, bot)
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
        assert chat_boost_removed_dict["remove_date"] == chat_boost_removed.remove_date
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


class TestUserChatBoostsWithoutRequest(ChatBoostDefaults):
    def test_slot_behaviour(self, user_chat_boosts):
        inst = user_chat_boosts
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, user_chat_boosts):
        json_dict = {
            "boosts": [
                {
                    "boost_id": "2",
                    "add_date": self.date,
                    "expiration_date": self.date,
                    "source": self.default_source.to_dict(),
                }
            ]
        }
        ucb = UserChatBoosts.de_json(json_dict, bot)

        assert isinstance(ucb, UserChatBoosts)
        assert isinstance(ucb.boosts[0], ChatBoost)
        assert ucb.boosts[0].boost_id == self.boost_id
        assert to_timestamp(ucb.boosts[0].add_date) == self.date
        assert to_timestamp(ucb.boosts[0].expiration_date) == self.date
        assert ucb.boosts[0].source == self.default_source

    def test_to_dict(self, user_chat_boosts):
        user_chat_boosts_dict = user_chat_boosts.to_dict()

        assert isinstance(user_chat_boosts_dict, dict)
        assert isinstance(user_chat_boosts_dict["boosts"], list)
        assert user_chat_boosts_dict["boosts"][0] == user_chat_boosts.boosts[0].to_dict()

    async def test_get_user_chat_boosts(self, monkeypatch, bot):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            chat_id = data["chat_id"] == "3"
            user_id = data["user_id"] == "2"
            if not all((chat_id, user_id)):
                pytest.fail("I got wrong parameters in post")
            return data

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.get_user_chat_boosts("3", 2)


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
