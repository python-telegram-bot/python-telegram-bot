#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
import json

import pytest

from telegram.ext import DictPersistence
from tests.auxil.slots import mro_slots


@pytest.fixture(autouse=True)
def _reset_callback_data_cache(cdc_bot):
    yield
    cdc_bot.callback_data_cache.clear_callback_data()
    cdc_bot.callback_data_cache.clear_callback_queries()


@pytest.fixture()
def bot_data():
    return {"test1": "test2", "test3": {"test4": "test5"}}


@pytest.fixture()
def chat_data():
    return {-12345: {"test1": "test2", "test3": {"test4": "test5"}}, -67890: {3: "test4"}}


@pytest.fixture()
def user_data():
    return {12345: {"test1": "test2", "test3": {"test4": "test5"}}, 67890: {3: "test4"}}


@pytest.fixture()
def callback_data():
    return [("test1", 1000, {"button1": "test0", "button2": "test1"})], {"test1": "test2"}


@pytest.fixture()
def conversations():
    return {
        "name1": {(123, 123): 3, (456, 654): 4},
        "name2": {(123, 321): 1, (890, 890): 2},
        "name3": {(123, 321): 1, (890, 890): 2},
    }


@pytest.fixture()
def user_data_json(user_data):
    return json.dumps(user_data)


@pytest.fixture()
def chat_data_json(chat_data):
    return json.dumps(chat_data)


@pytest.fixture()
def bot_data_json(bot_data):
    return json.dumps(bot_data)


@pytest.fixture()
def callback_data_json(callback_data):
    return json.dumps(callback_data)


@pytest.fixture()
def conversations_json(conversations):
    return """{"name1": {"[123, 123]": 3, "[456, 654]": 4}, "name2":
              {"[123, 321]": 1, "[890, 890]": 2}, "name3":
              {"[123, 321]": 1, "[890, 890]": 2}}"""


class TestDictPersistence:
    """Just tests the DictPersistence interface. Integration of persistence into Applictation
    is tested in TestBasePersistence!"""

    async def test_slot_behaviour(self, recwarn):
        inst = DictPersistence()
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    async def test_no_json_given(self):
        dict_persistence = DictPersistence()
        assert await dict_persistence.get_user_data() == {}
        assert await dict_persistence.get_chat_data() == {}
        assert await dict_persistence.get_bot_data() == {}
        assert await dict_persistence.get_callback_data() is None
        assert await dict_persistence.get_conversations("noname") == {}

    async def test_bad_json_string_given(self):
        bad_user_data = "thisisnojson99900()))("
        bad_chat_data = "thisisnojson99900()))("
        bad_bot_data = "thisisnojson99900()))("
        bad_callback_data = "thisisnojson99900()))("
        bad_conversations = "thisisnojson99900()))("
        with pytest.raises(TypeError, match="user_data"):
            DictPersistence(user_data_json=bad_user_data)
        with pytest.raises(TypeError, match="chat_data"):
            DictPersistence(chat_data_json=bad_chat_data)
        with pytest.raises(TypeError, match="bot_data"):
            DictPersistence(bot_data_json=bad_bot_data)
        with pytest.raises(TypeError, match="callback_data"):
            DictPersistence(callback_data_json=bad_callback_data)
        with pytest.raises(TypeError, match="conversations"):
            DictPersistence(conversations_json=bad_conversations)

    async def test_invalid_json_string_given(self):
        bad_user_data = '["this", "is", "json"]'
        bad_chat_data = '["this", "is", "json"]'
        bad_bot_data = '["this", "is", "json"]'
        bad_conversations = '["this", "is", "json"]'
        bad_callback_data_1 = '[[["str", 3.14, {"di": "ct"}]], "is"]'
        bad_callback_data_2 = '[[["str", "non-float", {"di": "ct"}]], {"di": "ct"}]'
        bad_callback_data_3 = '[[[{"not": "a str"}, 3.14, {"di": "ct"}]], {"di": "ct"}]'
        bad_callback_data_4 = '[[["wrong", "length"]], {"di": "ct"}]'
        bad_callback_data_5 = '["this", "is", "json"]'
        with pytest.raises(TypeError, match="user_data"):
            DictPersistence(user_data_json=bad_user_data)
        with pytest.raises(TypeError, match="chat_data"):
            DictPersistence(chat_data_json=bad_chat_data)
        with pytest.raises(TypeError, match="bot_data"):
            DictPersistence(bot_data_json=bad_bot_data)
        for bad_callback_data in [
            bad_callback_data_1,
            bad_callback_data_2,
            bad_callback_data_3,
            bad_callback_data_4,
            bad_callback_data_5,
        ]:
            with pytest.raises(TypeError, match="callback_data"):
                DictPersistence(callback_data_json=bad_callback_data)
        with pytest.raises(TypeError, match="conversations"):
            DictPersistence(conversations_json=bad_conversations)

    async def test_good_json_input(
        self, user_data_json, chat_data_json, bot_data_json, conversations_json, callback_data_json
    ):
        dict_persistence = DictPersistence(
            user_data_json=user_data_json,
            chat_data_json=chat_data_json,
            bot_data_json=bot_data_json,
            conversations_json=conversations_json,
            callback_data_json=callback_data_json,
        )
        user_data = await dict_persistence.get_user_data()
        assert isinstance(user_data, dict)
        assert user_data[12345]["test1"] == "test2"
        assert user_data[67890][3] == "test4"

        chat_data = await dict_persistence.get_chat_data()
        assert isinstance(chat_data, dict)
        assert chat_data[-12345]["test1"] == "test2"
        assert chat_data[-67890][3] == "test4"

        bot_data = await dict_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data["test1"] == "test2"
        assert bot_data["test3"]["test4"] == "test5"
        assert "test6" not in bot_data

        callback_data = await dict_persistence.get_callback_data()

        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [("test1", 1000, {"button1": "test0", "button2": "test1"})]
        assert callback_data[1] == {"test1": "test2"}

        conversation1 = await dict_persistence.get_conversations("name1")
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = await dict_persistence.get_conversations("name2")
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    async def test_good_json_input_callback_data_none(self):
        dict_persistence = DictPersistence(callback_data_json="null")
        assert dict_persistence.callback_data is None
        assert dict_persistence.callback_data_json == "null"

    async def test_dict_outputs(
        self,
        user_data,
        user_data_json,
        chat_data,
        chat_data_json,
        bot_data,
        bot_data_json,
        callback_data_json,
        conversations,
        conversations_json,
    ):
        dict_persistence = DictPersistence(
            user_data_json=user_data_json,
            chat_data_json=chat_data_json,
            bot_data_json=bot_data_json,
            callback_data_json=callback_data_json,
            conversations_json=conversations_json,
        )
        assert dict_persistence.user_data == user_data
        assert dict_persistence.chat_data == chat_data
        assert dict_persistence.bot_data == bot_data
        assert dict_persistence.bot_data == bot_data
        assert dict_persistence.conversations == conversations

    async def test_json_outputs(
        self, user_data_json, chat_data_json, bot_data_json, callback_data_json, conversations_json
    ):
        dict_persistence = DictPersistence(
            user_data_json=user_data_json,
            chat_data_json=chat_data_json,
            bot_data_json=bot_data_json,
            callback_data_json=callback_data_json,
            conversations_json=conversations_json,
        )
        assert dict_persistence.user_data_json == user_data_json
        assert dict_persistence.chat_data_json == chat_data_json
        assert dict_persistence.callback_data_json == callback_data_json
        assert dict_persistence.conversations_json == conversations_json

    async def test_updating(
        self,
        user_data_json,
        chat_data_json,
        bot_data_json,
        callback_data,
        callback_data_json,
        conversations,
        conversations_json,
    ):
        dict_persistence = DictPersistence(
            user_data_json=user_data_json,
            chat_data_json=chat_data_json,
            bot_data_json=bot_data_json,
            callback_data_json=callback_data_json,
            conversations_json=conversations_json,
        )

        user_data = await dict_persistence.get_user_data()
        user_data[12345]["test3"]["test4"] = "test6"
        assert dict_persistence.user_data != user_data
        assert dict_persistence.user_data_json != json.dumps(user_data)
        await dict_persistence.update_user_data(12345, user_data[12345])
        assert dict_persistence.user_data == user_data
        assert dict_persistence.user_data_json == json.dumps(user_data)
        await dict_persistence.drop_user_data(67890)
        assert 67890 not in dict_persistence.user_data
        dict_persistence._user_data = None
        await dict_persistence.drop_user_data(123)
        assert isinstance(await dict_persistence.get_user_data(), dict)

        chat_data = await dict_persistence.get_chat_data()
        chat_data[-12345]["test3"]["test4"] = "test6"
        assert dict_persistence.chat_data != chat_data
        assert dict_persistence.chat_data_json != json.dumps(chat_data)
        await dict_persistence.update_chat_data(-12345, chat_data[-12345])
        assert dict_persistence.chat_data == chat_data
        assert dict_persistence.chat_data_json == json.dumps(chat_data)
        await dict_persistence.drop_chat_data(-67890)
        assert -67890 not in dict_persistence.chat_data
        dict_persistence._chat_data = None
        await dict_persistence.drop_chat_data(123)
        assert isinstance(await dict_persistence.get_chat_data(), dict)

        bot_data = await dict_persistence.get_bot_data()
        bot_data["test3"]["test4"] = "test6"
        assert dict_persistence.bot_data != bot_data
        assert dict_persistence.bot_data_json != json.dumps(bot_data)
        await dict_persistence.update_bot_data(bot_data)
        assert dict_persistence.bot_data == bot_data
        assert dict_persistence.bot_data_json == json.dumps(bot_data)

        callback_data = await dict_persistence.get_callback_data()
        callback_data[1]["test3"] = "test4"
        callback_data[0][0][2]["button2"] = "test41"
        assert dict_persistence.callback_data != callback_data
        assert dict_persistence.callback_data_json != json.dumps(callback_data)
        await dict_persistence.update_callback_data(callback_data)
        assert dict_persistence.callback_data == callback_data
        assert dict_persistence.callback_data_json == json.dumps(callback_data)

        conversation1 = await dict_persistence.get_conversations("name1")
        conversation1[(123, 123)] = 5
        assert dict_persistence.conversations["name1"] != conversation1
        await dict_persistence.update_conversation("name1", (123, 123), 5)
        assert dict_persistence.conversations["name1"] == conversation1
        conversations["name1"][(123, 123)] = 5
        assert (
            dict_persistence.conversations_json
            == DictPersistence._encode_conversations_to_json(conversations)
        )
        assert await dict_persistence.get_conversations("name1") == conversation1

        dict_persistence._conversations = None
        await dict_persistence.update_conversation("name1", (123, 123), 5)
        assert dict_persistence.conversations["name1"] == {(123, 123): 5}
        assert await dict_persistence.get_conversations("name1") == {(123, 123): 5}
        assert (
            dict_persistence.conversations_json
            == DictPersistence._encode_conversations_to_json({"name1": {(123, 123): 5}})
        )

    async def test_no_data_on_init(
        self, bot_data, user_data, chat_data, conversations, callback_data
    ):
        dict_persistence = DictPersistence()

        assert dict_persistence.user_data is None
        assert dict_persistence.chat_data is None
        assert dict_persistence.bot_data is None
        assert dict_persistence.conversations is None
        assert dict_persistence.callback_data is None
        assert dict_persistence.user_data_json == "null"
        assert dict_persistence.chat_data_json == "null"
        assert dict_persistence.bot_data_json == "null"
        assert dict_persistence.conversations_json == "null"
        assert dict_persistence.callback_data_json == "null"

        await dict_persistence.update_bot_data(bot_data)
        await dict_persistence.update_user_data(12345, user_data[12345])
        await dict_persistence.update_chat_data(-12345, chat_data[-12345])
        await dict_persistence.update_conversation("name", (1, 1), "new_state")
        await dict_persistence.update_callback_data(callback_data)

        assert dict_persistence.user_data[12345] == user_data[12345]
        assert dict_persistence.chat_data[-12345] == chat_data[-12345]
        assert dict_persistence.bot_data == bot_data
        assert dict_persistence.conversations["name"] == {(1, 1): "new_state"}
        assert dict_persistence.callback_data == callback_data

    async def test_no_json_dumping_if_data_did_not_change(
        self, bot_data, user_data, chat_data, conversations, callback_data, monkeypatch
    ):
        dict_persistence = DictPersistence()

        await dict_persistence.update_bot_data(bot_data)
        await dict_persistence.update_user_data(12345, user_data[12345])
        await dict_persistence.update_chat_data(-12345, chat_data[-12345])
        await dict_persistence.update_conversation("name", (1, 1), "new_state")
        await dict_persistence.update_callback_data(callback_data)

        assert dict_persistence.user_data_json == json.dumps({12345: user_data[12345]})
        assert dict_persistence.chat_data_json == json.dumps({-12345: chat_data[-12345]})
        assert dict_persistence.bot_data_json == json.dumps(bot_data)
        assert (
            dict_persistence.conversations_json
            == DictPersistence._encode_conversations_to_json({"name": {(1, 1): "new_state"}})
        )
        assert dict_persistence.callback_data_json == json.dumps(callback_data)

        flag = False

        def dumps(*args, **kwargs):
            nonlocal flag
            flag = True

        # Since the data doesn't change, json.dumps shoduln't be called beyond this point!
        monkeypatch.setattr(json, "dumps", dumps)

        await dict_persistence.update_bot_data(bot_data)
        await dict_persistence.update_user_data(12345, user_data[12345])
        await dict_persistence.update_chat_data(-12345, chat_data[-12345])
        await dict_persistence.update_conversation("name", (1, 1), "new_state")
        await dict_persistence.update_callback_data(callback_data)

        assert not flag
