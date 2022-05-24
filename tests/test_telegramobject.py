#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
import pickle
from copy import deepcopy

import pytest

from telegram import Chat, Message, PhotoSize, TelegramObject, User


class TestTelegramObject:
    class Sub(TelegramObject):
        def __init__(self, private, normal, b):
            self._private = private
            self.normal = normal
            self._bot = b

    def test_to_json(self, monkeypatch):
        # to_json simply takes whatever comes from to_dict, therefore we only need to test it once
        telegram_object = TelegramObject()

        # Test that it works with a dict with str keys as well as dicts as lists as values
        d = {"str": "str", "str2": ["str", "str"], "str3": {"str": "str"}}
        monkeypatch.setattr("telegram.TelegramObject.to_dict", lambda _: d)
        json = telegram_object.to_json()
        # Order isn't guarantied
        assert '"str": "str"' in json
        assert '"str2": ["str", "str"]' in json
        assert '"str3": {"str": "str"}' in json

        # Now make sure that it doesn't work with not json stuff and that it fails loudly
        # Tuples aren't allowed as keys in json
        d = {("str", "str"): "str"}

        monkeypatch.setattr("telegram.TelegramObject.to_dict", lambda _: d)
        with pytest.raises(TypeError):
            telegram_object.to_json()

    def test_to_dict_private_attribute(self):
        class TelegramObjectSubclass(TelegramObject):
            __slots__ = ("a", "_b")  # Added slots so that the attrs are converted to dict

            def __init__(self):
                self.a = 1
                self._b = 2

        subclass_instance = TelegramObjectSubclass()
        assert subclass_instance.to_dict() == {"a": 1}

    def test_slot_behaviour(self, mro_slots):
        inst = TelegramObject()
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_meaningless_comparison(self, recwarn):
        expected_warning = "Objects of type TGO can not be meaningfully tested for equivalence."

        class TGO(TelegramObject):
            pass

        a = TGO()
        b = TGO()
        assert a == b
        assert len(recwarn) == 1
        assert str(recwarn[0].message) == expected_warning
        assert recwarn[0].filename == __file__, "wrong stacklevel"

    def test_meaningful_comparison(self, recwarn):
        class TGO(TelegramObject):
            def __init__(self):
                self._id_attrs = (1,)

        a = TGO()
        b = TGO()
        assert a == b
        assert len(recwarn) == 0
        assert b == a
        assert len(recwarn) == 0

    def test_bot_instance_none(self):
        tg_object = TelegramObject()
        with pytest.raises(RuntimeError):
            tg_object.get_bot()

    @pytest.mark.parametrize("bot_inst", ["bot", None])
    def test_bot_instance_states(self, bot_inst):
        tg_object = TelegramObject()
        tg_object.set_bot("bot" if bot_inst == "bot" else bot_inst)
        if bot_inst == "bot":
            assert tg_object.get_bot() == "bot"
        elif bot_inst is None:
            with pytest.raises(RuntimeError):
                tg_object.get_bot()

    def test_subscription(self):
        # We test with Message because that gives us everything we want to test - easier than
        # implementing a custom subclass just for this test
        chat = Chat(2, Chat.PRIVATE)
        user = User(3, "first_name", False)
        message = Message(1, None, chat=chat, from_user=user, text="foobar")
        assert message["text"] == "foobar"
        assert message["chat"] is chat
        assert message["chat_id"] == 2
        assert message["from"] is user
        assert message["from_user"] is user
        with pytest.raises(KeyError, match="Message don't have an attribute called `no_key`"):
            message["no_key"]

    def test_pickle(self, bot):
        chat = Chat(2, Chat.PRIVATE)
        user = User(3, "first_name", False)
        date = datetime.datetime.now()
        photo = PhotoSize("file_id", "unique", 21, 21, bot=bot)
        msg = Message(1, date, chat, from_user=user, text="foobar", bot=bot, photo=[photo])

        # Test pickling of TGObjects, we choose Message since it's contains the most subclasses.
        assert msg.get_bot()
        unpickled = pickle.loads(pickle.dumps(msg))

        with pytest.raises(RuntimeError):
            unpickled.get_bot()  # There should be no bot when we pickle TGObjects

        assert unpickled.chat == chat
        assert unpickled.from_user == user
        assert unpickled.date == date
        assert unpickled.photo[0] == photo

    def test_deepcopy_telegram_obj(self, bot):
        chat = Chat(2, Chat.PRIVATE)
        user = User(3, "first_name", False)
        date = datetime.datetime.now()
        photo = PhotoSize("file_id", "unique", 21, 21, bot=bot)
        msg = Message(1, date, chat, from_user=user, text="foobar", bot=bot, photo=[photo])

        new_msg = deepcopy(msg)

        # The same bot should be present when deepcopying.
        assert new_msg.get_bot() == bot and new_msg.get_bot() is bot

        assert new_msg.date == date and new_msg.date is not date
        assert new_msg.chat == chat and new_msg.chat is not chat
        assert new_msg.from_user == user and new_msg.from_user is not user
        assert new_msg.photo[0] == photo and new_msg.photo[0] is not photo

    def test_deepcopy_subclass_telegram_obj(self, bot):
        s = self.Sub("private", "normal", bot)
        d = deepcopy(s)
        assert d is not s
        assert d._private == s._private  # Can't test for identity since two equal strings is True
        assert d._bot == s._bot and d._bot is s._bot
        assert d.normal == s.normal
