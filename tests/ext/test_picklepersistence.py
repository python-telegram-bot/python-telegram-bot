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
import datetime
import gzip
import os
import pickle
import sys
from pathlib import Path

import pytest

from telegram import Chat, Message, TelegramObject, Update, User
from telegram.ext import ContextTypes, PersistenceInput, PicklePersistence
from telegram.warnings import PTBUserWarning
from tests.auxil.files import PROJECT_ROOT_PATH
from tests.auxil.pytest_classes import make_bot
from tests.auxil.slots import mro_slots


@pytest.fixture(autouse=True)
def _change_directory(tmp_path: Path):
    orig_dir = Path.cwd()
    # Switch to a temporary directory, so we don't have to worry about cleaning up files
    os.chdir(tmp_path)
    yield
    # Go back to original directory
    os.chdir(orig_dir)


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
def pickle_persistence():
    return PicklePersistence(
        filepath="pickletest",
        single_file=False,
        on_flush=False,
    )


@pytest.fixture()
def pickle_persistence_only_bot():
    return PicklePersistence(
        filepath="pickletest",
        store_data=PersistenceInput(callback_data=False, user_data=False, chat_data=False),
        single_file=False,
        on_flush=False,
    )


@pytest.fixture()
def pickle_persistence_only_chat():
    return PicklePersistence(
        filepath="pickletest",
        store_data=PersistenceInput(callback_data=False, user_data=False, bot_data=False),
        single_file=False,
        on_flush=False,
    )


@pytest.fixture()
def pickle_persistence_only_user():
    return PicklePersistence(
        filepath="pickletest",
        store_data=PersistenceInput(callback_data=False, chat_data=False, bot_data=False),
        single_file=False,
        on_flush=False,
    )


@pytest.fixture()
def pickle_persistence_only_callback():
    return PicklePersistence(
        filepath="pickletest",
        store_data=PersistenceInput(user_data=False, chat_data=False, bot_data=False),
        single_file=False,
        on_flush=False,
    )


@pytest.fixture()
def bad_pickle_files():
    for name in [
        "pickletest_user_data",
        "pickletest_chat_data",
        "pickletest_bot_data",
        "pickletest_callback_data",
        "pickletest_conversations",
        "pickletest",
    ]:
        Path(name).write_text("(())")
    return True


@pytest.fixture()
def invalid_pickle_files():
    for name in [
        "pickletest_user_data",
        "pickletest_chat_data",
        "pickletest_bot_data",
        "pickletest_callback_data",
        "pickletest_conversations",
        "pickletest",
    ]:
        # Just a random way to trigger pickle.UnpicklingError
        # see https://stackoverflow.com/a/44422239/10606962
        with gzip.open(name, "wb") as file:
            pickle.dump([1, 2, 3], file)
    return True


@pytest.fixture()
def good_pickle_files(user_data, chat_data, bot_data, callback_data, conversations):
    data = {
        "user_data": user_data,
        "chat_data": chat_data,
        "bot_data": bot_data,
        "callback_data": callback_data,
        "conversations": conversations,
    }
    with Path("pickletest_user_data").open("wb") as f:
        pickle.dump(user_data, f)
    with Path("pickletest_chat_data").open("wb") as f:
        pickle.dump(chat_data, f)
    with Path("pickletest_bot_data").open("wb") as f:
        pickle.dump(bot_data, f)
    with Path("pickletest_callback_data").open("wb") as f:
        pickle.dump(callback_data, f)
    with Path("pickletest_conversations").open("wb") as f:
        pickle.dump(conversations, f)
    with Path("pickletest").open("wb") as f:
        pickle.dump(data, f)
    return True


@pytest.fixture()
def pickle_files_wo_bot_data(user_data, chat_data, callback_data, conversations):
    data = {
        "user_data": user_data,
        "chat_data": chat_data,
        "conversations": conversations,
        "callback_data": callback_data,
    }
    with Path("pickletest_user_data").open("wb") as f:
        pickle.dump(user_data, f)
    with Path("pickletest_chat_data").open("wb") as f:
        pickle.dump(chat_data, f)
    with Path("pickletest_callback_data").open("wb") as f:
        pickle.dump(callback_data, f)
    with Path("pickletest_conversations").open("wb") as f:
        pickle.dump(conversations, f)
    with Path("pickletest").open("wb") as f:
        pickle.dump(data, f)
    return True


@pytest.fixture()
def pickle_files_wo_callback_data(user_data, chat_data, bot_data, conversations):
    data = {
        "user_data": user_data,
        "chat_data": chat_data,
        "bot_data": bot_data,
        "conversations": conversations,
    }
    with Path("pickletest_user_data").open("wb") as f:
        pickle.dump(user_data, f)
    with Path("pickletest_chat_data").open("wb") as f:
        pickle.dump(chat_data, f)
    with Path("pickletest_bot_data").open("wb") as f:
        pickle.dump(bot_data, f)
    with Path("pickletest_conversations").open("wb") as f:
        pickle.dump(conversations, f)
    with Path("pickletest").open("wb") as f:
        pickle.dump(data, f)
    return True


@pytest.fixture()
def update(bot):
    user = User(id=321, first_name="test_user", is_bot=False)
    chat = Chat(id=123, type="group")
    message = Message(1, datetime.datetime.now(), chat, from_user=user, text="Hi there")
    message.set_bot(bot)
    return Update(0, message=message)


class TestPicklePersistence:
    """Just tests the PicklePersistence interface. Integration of persistence into Applictation
    is tested in TestBasePersistence!"""

    class DictSub(TelegramObject):  # Used for testing our custom (Un)Pickler.
        def __init__(self, private, normal, b):
            super().__init__()
            self._private = private
            self.normal = normal
            self._bot = b

    class SlotsSub(TelegramObject):
        __slots__ = ("_private", "new_var")

        def __init__(self, new_var, private):
            super().__init__()
            self.new_var = new_var
            self._private = private

    class NormalClass:
        def __init__(self, my_var):
            self.my_var = my_var

    async def test_slot_behaviour(self, pickle_persistence):
        inst = pickle_persistence
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.mark.parametrize("on_flush", [True, False])
    async def test_on_flush(self, pickle_persistence, on_flush):
        pickle_persistence.on_flush = on_flush
        pickle_persistence.single_file = True
        file_path = Path(pickle_persistence.filepath)

        await pickle_persistence.update_callback_data("somedata")
        assert file_path.is_file() != on_flush

        await pickle_persistence.update_bot_data("data")
        assert file_path.is_file() != on_flush

        await pickle_persistence.update_user_data(123, "data")
        assert file_path.is_file() != on_flush

        await pickle_persistence.update_chat_data(123, "data")
        assert file_path.is_file() != on_flush

        await pickle_persistence.update_conversation("name", (1, 1), "new_state")
        assert file_path.is_file() != on_flush

        await pickle_persistence.flush()
        assert file_path.is_file()

    async def test_pickle_behaviour_with_slots(self, pickle_persistence):
        bot_data = await pickle_persistence.get_bot_data()
        bot_data["message"] = Message(3, datetime.datetime.now(), Chat(2, type="supergroup"))
        await pickle_persistence.update_bot_data(bot_data)
        retrieved = await pickle_persistence.get_bot_data()
        assert retrieved == bot_data

    async def test_no_files_present_multi_file(self, pickle_persistence):
        assert await pickle_persistence.get_user_data() == {}
        assert await pickle_persistence.get_chat_data() == {}
        assert await pickle_persistence.get_bot_data() == {}
        assert await pickle_persistence.get_callback_data() is None
        assert await pickle_persistence.get_conversations("noname") == {}

    async def test_no_files_present_single_file(self, pickle_persistence):
        pickle_persistence.single_file = True
        assert await pickle_persistence.get_user_data() == {}
        assert await pickle_persistence.get_chat_data() == {}
        assert await pickle_persistence.get_bot_data() == {}
        assert await pickle_persistence.get_callback_data() is None
        assert await pickle_persistence.get_conversations("noname") == {}

    async def test_with_bad_multi_file(self, pickle_persistence, bad_pickle_files):
        with pytest.raises(TypeError, match="pickletest_user_data"):
            await pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match="pickletest_chat_data"):
            await pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match="pickletest_bot_data"):
            await pickle_persistence.get_bot_data()
        with pytest.raises(TypeError, match="pickletest_callback_data"):
            await pickle_persistence.get_callback_data()
        with pytest.raises(TypeError, match="pickletest_conversations"):
            await pickle_persistence.get_conversations("name")

    async def test_with_invalid_multi_file(self, pickle_persistence, invalid_pickle_files):
        with pytest.raises(TypeError, match="pickletest_user_data does not contain"):
            await pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match="pickletest_chat_data does not contain"):
            await pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match="pickletest_bot_data does not contain"):
            await pickle_persistence.get_bot_data()
        with pytest.raises(TypeError, match="pickletest_callback_data does not contain"):
            await pickle_persistence.get_callback_data()
        with pytest.raises(TypeError, match="pickletest_conversations does not contain"):
            await pickle_persistence.get_conversations("name")

    async def test_with_bad_single_file(self, pickle_persistence, bad_pickle_files):
        pickle_persistence.single_file = True
        with pytest.raises(TypeError, match="pickletest"):
            await pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match="pickletest"):
            await pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match="pickletest"):
            await pickle_persistence.get_bot_data()
        with pytest.raises(TypeError, match="pickletest"):
            await pickle_persistence.get_callback_data()
        with pytest.raises(TypeError, match="pickletest"):
            await pickle_persistence.get_conversations("name")

    async def test_with_invalid_single_file(self, pickle_persistence, invalid_pickle_files):
        pickle_persistence.single_file = True
        with pytest.raises(TypeError, match="pickletest does not contain"):
            await pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match="pickletest does not contain"):
            await pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match="pickletest does not contain"):
            await pickle_persistence.get_bot_data()
        with pytest.raises(TypeError, match="pickletest does not contain"):
            await pickle_persistence.get_callback_data()
        with pytest.raises(TypeError, match="pickletest does not contain"):
            await pickle_persistence.get_conversations("name")

    async def test_with_good_multi_file(self, pickle_persistence, good_pickle_files):
        user_data = await pickle_persistence.get_user_data()
        assert isinstance(user_data, dict)
        assert user_data[12345]["test1"] == "test2"
        assert user_data[67890][3] == "test4"

        chat_data = await pickle_persistence.get_chat_data()
        assert isinstance(chat_data, dict)
        assert chat_data[-12345]["test1"] == "test2"
        assert chat_data[-67890][3] == "test4"

        bot_data = await pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data["test1"] == "test2"
        assert bot_data["test3"]["test4"] == "test5"
        assert "test0" not in bot_data

        callback_data = await pickle_persistence.get_callback_data()
        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [("test1", 1000, {"button1": "test0", "button2": "test1"})]
        assert callback_data[1] == {"test1": "test2"}

        conversation1 = await pickle_persistence.get_conversations("name1")
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = await pickle_persistence.get_conversations("name2")
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    async def test_with_good_single_file(self, pickle_persistence, good_pickle_files):
        pickle_persistence.single_file = True
        user_data = await pickle_persistence.get_user_data()
        assert isinstance(user_data, dict)
        assert user_data[12345]["test1"] == "test2"
        assert user_data[67890][3] == "test4"

        chat_data = await pickle_persistence.get_chat_data()
        assert isinstance(chat_data, dict)
        assert chat_data[-12345]["test1"] == "test2"
        assert chat_data[-67890][3] == "test4"

        bot_data = await pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data["test1"] == "test2"
        assert bot_data["test3"]["test4"] == "test5"
        assert "test0" not in bot_data

        callback_data = await pickle_persistence.get_callback_data()
        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [("test1", 1000, {"button1": "test0", "button2": "test1"})]
        assert callback_data[1] == {"test1": "test2"}

        conversation1 = await pickle_persistence.get_conversations("name1")
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = await pickle_persistence.get_conversations("name2")
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    async def test_with_multi_file_wo_bot_data(self, pickle_persistence, pickle_files_wo_bot_data):
        user_data = await pickle_persistence.get_user_data()
        assert isinstance(user_data, dict)
        assert user_data[12345]["test1"] == "test2"
        assert user_data[67890][3] == "test4"

        chat_data = await pickle_persistence.get_chat_data()
        assert isinstance(chat_data, dict)
        assert chat_data[-12345]["test1"] == "test2"
        assert chat_data[-67890][3] == "test4"

        bot_data = await pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert not bot_data.keys()

        callback_data = await pickle_persistence.get_callback_data()
        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [("test1", 1000, {"button1": "test0", "button2": "test1"})]
        assert callback_data[1] == {"test1": "test2"}

        conversation1 = await pickle_persistence.get_conversations("name1")
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = await pickle_persistence.get_conversations("name2")
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    async def test_with_multi_file_wo_callback_data(
        self, pickle_persistence, pickle_files_wo_callback_data
    ):
        user_data = await pickle_persistence.get_user_data()
        assert isinstance(user_data, dict)
        assert user_data[12345]["test1"] == "test2"
        assert user_data[67890][3] == "test4"

        chat_data = await pickle_persistence.get_chat_data()
        assert isinstance(chat_data, dict)
        assert chat_data[-12345]["test1"] == "test2"
        assert chat_data[-67890][3] == "test4"

        bot_data = await pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data["test1"] == "test2"
        assert bot_data["test3"]["test4"] == "test5"
        assert "test0" not in bot_data

        callback_data = await pickle_persistence.get_callback_data()
        assert callback_data is None

        conversation1 = await pickle_persistence.get_conversations("name1")
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = await pickle_persistence.get_conversations("name2")
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    async def test_with_single_file_wo_bot_data(
        self, pickle_persistence, pickle_files_wo_bot_data
    ):
        pickle_persistence.single_file = True
        user_data = await pickle_persistence.get_user_data()
        assert isinstance(user_data, dict)
        assert user_data[12345]["test1"] == "test2"
        assert user_data[67890][3] == "test4"

        chat_data = await pickle_persistence.get_chat_data()
        assert isinstance(chat_data, dict)
        assert chat_data[-12345]["test1"] == "test2"
        assert chat_data[-67890][3] == "test4"

        bot_data = await pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert not bot_data.keys()

        callback_data = await pickle_persistence.get_callback_data()
        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [("test1", 1000, {"button1": "test0", "button2": "test1"})]
        assert callback_data[1] == {"test1": "test2"}

        conversation1 = await pickle_persistence.get_conversations("name1")
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = await pickle_persistence.get_conversations("name2")
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    async def test_with_single_file_wo_callback_data(
        self, pickle_persistence, pickle_files_wo_callback_data
    ):
        user_data = await pickle_persistence.get_user_data()
        assert isinstance(user_data, dict)
        assert user_data[12345]["test1"] == "test2"
        assert user_data[67890][3] == "test4"

        chat_data = await pickle_persistence.get_chat_data()
        assert isinstance(chat_data, dict)
        assert chat_data[-12345]["test1"] == "test2"
        assert chat_data[-67890][3] == "test4"

        bot_data = await pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data["test1"] == "test2"
        assert bot_data["test3"]["test4"] == "test5"
        assert "test0" not in bot_data

        callback_data = await pickle_persistence.get_callback_data()
        assert callback_data is None

        conversation1 = await pickle_persistence.get_conversations("name1")
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = await pickle_persistence.get_conversations("name2")
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    async def test_updating_multi_file(self, pickle_persistence, good_pickle_files):
        user_data = await pickle_persistence.get_user_data()
        user_data[12345]["test3"]["test4"] = "test6"
        assert pickle_persistence.user_data != user_data
        await pickle_persistence.update_user_data(12345, user_data[12345])
        assert pickle_persistence.user_data == user_data
        with Path("pickletest_user_data").open("rb") as f:
            user_data_test = dict(pickle.load(f))
        assert user_data_test == user_data
        await pickle_persistence.drop_user_data(67890)
        assert 67890 not in await pickle_persistence.get_user_data()

        chat_data = await pickle_persistence.get_chat_data()
        chat_data[-12345]["test3"]["test4"] = "test6"
        assert pickle_persistence.chat_data != chat_data
        await pickle_persistence.update_chat_data(-12345, chat_data[-12345])
        assert pickle_persistence.chat_data == chat_data
        with Path("pickletest_chat_data").open("rb") as f:
            chat_data_test = dict(pickle.load(f))
        assert chat_data_test == chat_data
        await pickle_persistence.drop_chat_data(-67890)
        assert -67890 not in await pickle_persistence.get_chat_data()

        bot_data = await pickle_persistence.get_bot_data()
        bot_data["test3"]["test4"] = "test6"
        assert pickle_persistence.bot_data != bot_data
        await pickle_persistence.update_bot_data(bot_data)
        assert pickle_persistence.bot_data == bot_data
        with Path("pickletest_bot_data").open("rb") as f:
            bot_data_test = pickle.load(f)
        assert bot_data_test == bot_data

        callback_data = await pickle_persistence.get_callback_data()
        callback_data[1]["test3"] = "test4"
        assert pickle_persistence.callback_data != callback_data
        await pickle_persistence.update_callback_data(callback_data)
        assert pickle_persistence.callback_data == callback_data
        with Path("pickletest_callback_data").open("rb") as f:
            callback_data_test = pickle.load(f)
        assert callback_data_test == callback_data

        conversation1 = await pickle_persistence.get_conversations("name1")
        conversation1[(123, 123)] = 5
        assert pickle_persistence.conversations["name1"] != conversation1
        await pickle_persistence.update_conversation("name1", (123, 123), 5)
        assert pickle_persistence.conversations["name1"] == conversation1
        assert await pickle_persistence.get_conversations("name1") == conversation1
        with Path("pickletest_conversations").open("rb") as f:
            conversations_test = dict(pickle.load(f))
        assert conversations_test["name1"] == conversation1

        pickle_persistence.conversations = None
        await pickle_persistence.update_conversation("name1", (123, 123), 5)
        assert pickle_persistence.conversations["name1"] == {(123, 123): 5}
        assert await pickle_persistence.get_conversations("name1") == {(123, 123): 5}

    async def test_updating_single_file(self, pickle_persistence, good_pickle_files):
        pickle_persistence.single_file = True

        user_data = await pickle_persistence.get_user_data()
        user_data[12345]["test3"]["test4"] = "test6"
        assert pickle_persistence.user_data != user_data
        await pickle_persistence.update_user_data(12345, user_data[12345])
        assert pickle_persistence.user_data == user_data
        with Path("pickletest").open("rb") as f:
            user_data_test = dict(pickle.load(f))["user_data"]
        assert user_data_test == user_data
        await pickle_persistence.drop_user_data(67890)
        assert 67890 not in await pickle_persistence.get_user_data()

        chat_data = await pickle_persistence.get_chat_data()
        chat_data[-12345]["test3"]["test4"] = "test6"
        assert pickle_persistence.chat_data != chat_data
        await pickle_persistence.update_chat_data(-12345, chat_data[-12345])
        assert pickle_persistence.chat_data == chat_data
        with Path("pickletest").open("rb") as f:
            chat_data_test = dict(pickle.load(f))["chat_data"]
        assert chat_data_test == chat_data
        await pickle_persistence.drop_chat_data(-67890)
        assert -67890 not in await pickle_persistence.get_chat_data()

        bot_data = await pickle_persistence.get_bot_data()
        bot_data["test3"]["test4"] = "test6"
        assert pickle_persistence.bot_data != bot_data
        await pickle_persistence.update_bot_data(bot_data)
        assert pickle_persistence.bot_data == bot_data
        with Path("pickletest").open("rb") as f:
            bot_data_test = pickle.load(f)["bot_data"]
        assert bot_data_test == bot_data

        callback_data = await pickle_persistence.get_callback_data()
        callback_data[1]["test3"] = "test4"
        assert pickle_persistence.callback_data != callback_data
        await pickle_persistence.update_callback_data(callback_data)
        assert pickle_persistence.callback_data == callback_data
        with Path("pickletest").open("rb") as f:
            callback_data_test = pickle.load(f)["callback_data"]
        assert callback_data_test == callback_data

        conversation1 = await pickle_persistence.get_conversations("name1")
        conversation1[(123, 123)] = 5
        assert pickle_persistence.conversations["name1"] != conversation1
        await pickle_persistence.update_conversation("name1", (123, 123), 5)
        assert pickle_persistence.conversations["name1"] == conversation1
        assert await pickle_persistence.get_conversations("name1") == conversation1
        with Path("pickletest").open("rb") as f:
            conversations_test = dict(pickle.load(f))["conversations"]
        assert conversations_test["name1"] == conversation1

        pickle_persistence.conversations = None
        await pickle_persistence.update_conversation("name1", (123, 123), 5)
        assert pickle_persistence.conversations["name1"] == {(123, 123): 5}
        assert await pickle_persistence.get_conversations("name1") == {(123, 123): 5}

    async def test_updating_single_file_no_data(self, pickle_persistence):
        pickle_persistence.single_file = True
        assert not any(
            [
                pickle_persistence.user_data,
                pickle_persistence.chat_data,
                pickle_persistence.bot_data,
                pickle_persistence.callback_data,
                pickle_persistence.conversations,
            ]
        )
        await pickle_persistence.flush()
        with pytest.raises(FileNotFoundError, match="pickletest"), Path("pickletest").open("rb"):
            pass

    async def test_save_on_flush_multi_files(self, pickle_persistence, good_pickle_files):
        # Should run without error
        await pickle_persistence.flush()
        pickle_persistence.on_flush = True

        user_data = await pickle_persistence.get_user_data()
        user_data[54321] = {}
        user_data[54321]["test9"] = "test 10"
        assert pickle_persistence.user_data != user_data

        await pickle_persistence.update_user_data(54321, user_data[54321])
        assert pickle_persistence.user_data == user_data

        await pickle_persistence.drop_user_data(0)
        assert pickle_persistence.user_data == user_data

        with Path("pickletest_user_data").open("rb") as f:
            user_data_test = dict(pickle.load(f))
        assert user_data_test != user_data

        chat_data = await pickle_persistence.get_chat_data()
        chat_data[54321] = {}
        chat_data[54321]["test9"] = "test 10"
        assert pickle_persistence.chat_data != chat_data

        await pickle_persistence.update_chat_data(54321, chat_data[54321])
        assert pickle_persistence.chat_data == chat_data

        await pickle_persistence.drop_chat_data(0)
        assert pickle_persistence.user_data == user_data

        with Path("pickletest_chat_data").open("rb") as f:
            chat_data_test = dict(pickle.load(f))
        assert chat_data_test != chat_data

        bot_data = await pickle_persistence.get_bot_data()
        bot_data["test6"] = "test 7"
        assert pickle_persistence.bot_data != bot_data

        await pickle_persistence.update_bot_data(bot_data)
        assert pickle_persistence.bot_data == bot_data

        with Path("pickletest_bot_data").open("rb") as f:
            bot_data_test = pickle.load(f)
        assert bot_data_test != bot_data

        callback_data = await pickle_persistence.get_callback_data()
        callback_data[1]["test3"] = "test4"
        assert pickle_persistence.callback_data != callback_data

        await pickle_persistence.update_callback_data(callback_data)
        assert pickle_persistence.callback_data == callback_data

        with Path("pickletest_callback_data").open("rb") as f:
            callback_data_test = pickle.load(f)
        assert callback_data_test != callback_data

        conversation1 = await pickle_persistence.get_conversations("name1")
        conversation1[(123, 123)] = 5
        assert pickle_persistence.conversations["name1"] != conversation1

        await pickle_persistence.update_conversation("name1", (123, 123), 5)
        assert pickle_persistence.conversations["name1"] == conversation1

        with Path("pickletest_conversations").open("rb") as f:
            conversations_test = dict(pickle.load(f))
        assert conversations_test["name1"] != conversation1

        await pickle_persistence.flush()
        with Path("pickletest_user_data").open("rb") as f:
            user_data_test = dict(pickle.load(f))
        assert user_data_test == user_data

        with Path("pickletest_chat_data").open("rb") as f:
            chat_data_test = dict(pickle.load(f))
        assert chat_data_test == chat_data

        with Path("pickletest_bot_data").open("rb") as f:
            bot_data_test = pickle.load(f)
        assert bot_data_test == bot_data

        with Path("pickletest_conversations").open("rb") as f:
            conversations_test = dict(pickle.load(f))
        assert conversations_test["name1"] == conversation1

    async def test_save_on_flush_single_files(self, pickle_persistence, good_pickle_files):
        # Should run without error
        await pickle_persistence.flush()

        pickle_persistence.on_flush = True
        pickle_persistence.single_file = True

        user_data = await pickle_persistence.get_user_data()
        user_data[54321] = {}
        user_data[54321]["test9"] = "test 10"
        assert pickle_persistence.user_data != user_data
        await pickle_persistence.update_user_data(54321, user_data[54321])
        assert pickle_persistence.user_data == user_data
        with Path("pickletest").open("rb") as f:
            user_data_test = dict(pickle.load(f))["user_data"]
        assert user_data_test != user_data

        chat_data = await pickle_persistence.get_chat_data()
        chat_data[54321] = {}
        chat_data[54321]["test9"] = "test 10"
        assert pickle_persistence.chat_data != chat_data
        await pickle_persistence.update_chat_data(54321, chat_data[54321])
        assert pickle_persistence.chat_data == chat_data
        with Path("pickletest").open("rb") as f:
            chat_data_test = dict(pickle.load(f))["chat_data"]
        assert chat_data_test != chat_data

        bot_data = await pickle_persistence.get_bot_data()
        bot_data["test6"] = "test 7"
        assert pickle_persistence.bot_data != bot_data
        await pickle_persistence.update_bot_data(bot_data)
        assert pickle_persistence.bot_data == bot_data
        with Path("pickletest").open("rb") as f:
            bot_data_test = pickle.load(f)["bot_data"]
        assert bot_data_test != bot_data

        callback_data = await pickle_persistence.get_callback_data()
        callback_data[1]["test3"] = "test4"
        assert pickle_persistence.callback_data != callback_data
        await pickle_persistence.update_callback_data(callback_data)
        assert pickle_persistence.callback_data == callback_data
        with Path("pickletest").open("rb") as f:
            callback_data_test = pickle.load(f)["callback_data"]
        assert callback_data_test != callback_data

        conversation1 = await pickle_persistence.get_conversations("name1")
        conversation1[(123, 123)] = 5
        assert pickle_persistence.conversations["name1"] != conversation1
        await pickle_persistence.update_conversation("name1", (123, 123), 5)
        assert pickle_persistence.conversations["name1"] == conversation1
        with Path("pickletest").open("rb") as f:
            conversations_test = dict(pickle.load(f))["conversations"]
        assert conversations_test["name1"] != conversation1

        await pickle_persistence.flush()
        with Path("pickletest").open("rb") as f:
            user_data_test = dict(pickle.load(f))["user_data"]
        assert user_data_test == user_data

        with Path("pickletest").open("rb") as f:
            chat_data_test = dict(pickle.load(f))["chat_data"]
        assert chat_data_test == chat_data

        with Path("pickletest").open("rb") as f:
            bot_data_test = pickle.load(f)["bot_data"]
        assert bot_data_test == bot_data

        with Path("pickletest").open("rb") as f:
            conversations_test = dict(pickle.load(f))["conversations"]
        assert conversations_test["name1"] == conversation1

    async def test_custom_pickler_unpickler_simple(
        self, pickle_persistence, good_pickle_files, cdc_bot, recwarn
    ):
        bot = cdc_bot
        update = Update(1)
        update.set_bot(bot)

        pickle_persistence.set_bot(bot)  # assign the current bot to the persistence
        data_with_bot = {"current_bot": update}
        await pickle_persistence.update_chat_data(
            12345, data_with_bot
        )  # also calls BotPickler.dumps()

        # Test that regular pickle load fails -
        err_msg = (
            "A load persistent id instruction was encountered,\nbut no persistent_load "
            "function was specified."
        )
        with Path("pickletest_chat_data").open("rb") as f, pytest.raises(
            pickle.UnpicklingError,
            match=err_msg if sys.version_info < (3, 12) else err_msg.replace("\n", " "),
        ):
            pickle.load(f)

        # Test that our custom unpickler works as intended -- inserts the current bot
        # We have to create a new instance otherwise unpickling is skipped
        pp = PicklePersistence("pickletest", single_file=False, on_flush=False)
        pp.set_bot(bot)  # Set the bot
        assert (await pp.get_chat_data())[12345]["current_bot"].get_bot() is bot

        # Now test that pickling of unknown bots in TelegramObjects will be replaced by None-
        assert not len(recwarn)
        data_with_bot = {}
        async with make_bot(token=bot.token) as other_bot:
            user = User(1, "Dev", False)
            user.set_bot(other_bot)
            data_with_bot["unknown_bot_in_user"] = user
        await pickle_persistence.update_chat_data(12345, data_with_bot)
        assert len(recwarn) == 1
        assert recwarn[-1].category is PTBUserWarning
        assert str(recwarn[-1].message).startswith("Unknown bot instance found.")
        assert (
            Path(recwarn[-1].filename)
            == PROJECT_ROOT_PATH / "telegram" / "ext" / "_picklepersistence.py"
        ), "wrong stacklevel!"
        pp = PicklePersistence("pickletest", single_file=False, on_flush=False)
        pp.set_bot(bot)
        assert (await pp.get_chat_data())[12345]["unknown_bot_in_user"]._bot is None

    async def test_custom_pickler_unpickler_with_custom_objects(
        self, cdc_bot, pickle_persistence, good_pickle_files
    ):
        bot = cdc_bot

        dict_s = self.DictSub("private", "normal", bot)
        slot_s = self.SlotsSub("new_var", "private_var")
        regular = self.NormalClass(12)

        pickle_persistence.set_bot(bot)
        await pickle_persistence.update_user_data(
            1232, {"sub_dict": dict_s, "sub_slots": slot_s, "r": regular}
        )
        pp = PicklePersistence("pickletest", single_file=False, on_flush=False)
        pp.set_bot(bot)  # Set the bot
        data = (await pp.get_user_data())[1232]
        sub_dict = data["sub_dict"]
        sub_slots = data["sub_slots"]
        sub_regular = data["r"]
        assert sub_dict._bot is bot
        assert sub_dict.normal == dict_s.normal
        assert sub_dict._private == dict_s._private
        assert sub_slots.new_var == slot_s.new_var
        assert sub_slots._private == slot_s._private
        assert sub_slots._bot is None  # We didn't set the bot, so it shouldn't have it here.
        assert sub_regular.my_var == regular.my_var

    @pytest.mark.parametrize(
        "filepath",
        ["pickletest", Path("pickletest")],
        ids=["str filepath", "pathlib.Path filepath"],
    )
    async def test_filepath_argument_types(self, filepath):
        pick_persist = PicklePersistence(
            filepath=filepath,
            on_flush=False,
        )
        await pick_persist.update_user_data(1, 1)

        assert (await pick_persist.get_user_data())[1] == 1
        assert Path(filepath).is_file()

    @pytest.mark.parametrize("singlefile", [True, False])
    @pytest.mark.parametrize("ud", [int, float, complex])
    @pytest.mark.parametrize("cd", [int, float, complex])
    @pytest.mark.parametrize("bd", [int, float, complex])
    async def test_with_context_types(self, ud, cd, bd, singlefile):
        cc = ContextTypes(user_data=ud, chat_data=cd, bot_data=bd)
        persistence = PicklePersistence("pickletest", single_file=singlefile, context_types=cc)

        assert isinstance(await persistence.get_bot_data(), bd)
        assert await persistence.get_bot_data() == 0

        persistence.user_data = None
        persistence.chat_data = None
        await persistence.drop_user_data(123)
        await persistence.drop_chat_data(123)
        assert isinstance(await persistence.get_user_data(), dict)
        assert isinstance(await persistence.get_chat_data(), dict)
        persistence.user_data = None
        persistence.chat_data = None
        await persistence.update_user_data(1, ud(1))
        await persistence.update_chat_data(1, cd(1))
        await persistence.update_bot_data(bd(1))
        assert (await persistence.get_user_data())[1] == 1
        assert (await persistence.get_chat_data())[1] == 1
        assert await persistence.get_bot_data() == 1

        await persistence.flush()
        persistence = PicklePersistence("pickletest", single_file=singlefile, context_types=cc)
        assert isinstance((await persistence.get_user_data())[1], ud)
        assert (await persistence.get_user_data())[1] == 1
        assert isinstance((await persistence.get_chat_data())[1], cd)
        assert (await persistence.get_chat_data())[1] == 1
        assert isinstance(await persistence.get_bot_data(), bd)
        assert await persistence.get_bot_data() == 1

    async def test_no_write_if_data_did_not_change(
        self, pickle_persistence, bot_data, user_data, chat_data, conversations, callback_data
    ):
        pickle_persistence.single_file = True
        pickle_persistence.on_flush = False

        await pickle_persistence.update_bot_data(bot_data)
        await pickle_persistence.update_user_data(12345, user_data[12345])
        await pickle_persistence.update_chat_data(-12345, chat_data[-12345])
        await pickle_persistence.update_conversation("name", (1, 1), "new_state")
        await pickle_persistence.update_callback_data(callback_data)

        assert pickle_persistence.filepath.is_file()
        pickle_persistence.filepath.unlink(missing_ok=True)
        assert not pickle_persistence.filepath.is_file()

        await pickle_persistence.update_bot_data(bot_data)
        await pickle_persistence.update_user_data(12345, user_data[12345])
        await pickle_persistence.update_chat_data(-12345, chat_data[-12345])
        await pickle_persistence.update_conversation("name", (1, 1), "new_state")
        await pickle_persistence.update_callback_data(callback_data)

        assert not pickle_persistence.filepath.is_file()
