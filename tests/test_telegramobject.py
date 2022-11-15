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
import inspect
import pickle
from copy import deepcopy
from pathlib import Path

import pytest

from telegram import Bot, BotCommand, Chat, Message, PhotoSize, TelegramObject, User


def all_subclasses(cls):
    # Gets all subclasses of the specified object, recursively. from
    # https://stackoverflow.com/a/3862957/9706202
    # also includes the class itself
    return (
        set(cls.__subclasses__())
        .union([s for c in cls.__subclasses__() for s in all_subclasses(c)])
        .union({cls})
    )


TO_SUBCLASSES = sorted(all_subclasses(TelegramObject), key=lambda cls: cls.__name__)


class TestTelegramObject:
    class Sub(TelegramObject):
        def __init__(self, private, normal, b):
            super().__init__()
            self._private = private
            self.normal = normal
            self._bot = b

    class ChangingTO(TelegramObject):
        # Don't use in any tests, this is just for testing the pickle behaviour and the
        # class is altered during the test procedure
        pass

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

    def test_de_json_api_kwargs(self, bot):
        to = TelegramObject.de_json(data={"foo": "bar"}, bot=bot)
        assert to.api_kwargs == {"foo": "bar"}
        assert to.get_bot() is bot

    @pytest.mark.parametrize("cls", TO_SUBCLASSES, ids=[cls.__name__ for cls in TO_SUBCLASSES])
    def test_subclasses_have_api_kwargs(self, cls):
        """Checks that all subclasses of TelegramObject have an api_kwargs argument that is
        kw-only. Also, tries to check that this argument is passed to super - by checking that
        the `__init__` contains `api_kwargs=api_kwargs`
        """
        if issubclass(cls, Bot):
            # Bot doesn't have api_kwargs, because it's not defined by TG
            return

        # only relevant for subclasses that have their own init
        if inspect.getsourcefile(cls.__init__) != inspect.getsourcefile(cls):
            return

        # Ignore classes in the test directory
        source_file = Path(inspect.getsourcefile(cls))
        parents = source_file.parents
        is_test_file = Path(__file__).parent.resolve() in parents
        if is_test_file:
            return

        # check the signature first
        signature = inspect.signature(cls)
        assert signature.parameters.get("api_kwargs").kind == inspect.Parameter.KEYWORD_ONLY

        # Now check for `api_kwargs=api_kwargs` in the source code of `__init__`
        if cls is TelegramObject:
            # TelegramObject doesn't have a super class
            return
        assert "api_kwargs=api_kwargs" in inspect.getsource(
            cls.__init__
        ), f"{cls.__name__} doesn't seem to pass `api_kwargs` to `super().__init__`"

    def test_de_json_arbitrary_exceptions(self, bot):
        class SubClass(TelegramObject):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                raise TypeError("This is a test")

        with pytest.raises(TypeError, match="This is a test"):
            SubClass.de_json({}, bot)

    def test_to_dict_private_attribute(self):
        class TelegramObjectSubclass(TelegramObject):
            __slots__ = ("a", "_b")  # Added slots so that the attrs are converted to dict

            def __init__(self):
                super().__init__()
                self.a = 1
                self._b = 2

        subclass_instance = TelegramObjectSubclass()
        assert subclass_instance.to_dict() == {"a": 1}

    def test_to_dict_api_kwargs(self):
        to = TelegramObject(api_kwargs={"foo": "bar"})
        assert to.to_dict() == {"foo": "bar"}

    def test_to_dict_recursion(self):
        class Recursive(TelegramObject):
            __slots__ = ("recursive",)

            def __init__(self):
                super().__init__()
                self.recursive = "recursive"

        class SubClass(TelegramObject):
            """This class doesn't have `__slots__`, so has `__dict__` instead."""

            def __init__(self):
                super().__init__()
                self.subclass = Recursive()

        to = SubClass()
        to_dict_no_recurse = to.to_dict(recursive=False)
        assert to_dict_no_recurse
        assert isinstance(to_dict_no_recurse["subclass"], Recursive)
        to_dict_recurse = to.to_dict(recursive=True)
        assert to_dict_recurse
        assert isinstance(to_dict_recurse["subclass"], dict)
        assert to_dict_recurse["subclass"]["recursive"] == "recursive"

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
        photo = PhotoSize("file_id", "unique", 21, 21)
        photo.set_bot(bot)
        msg = Message(1, date, chat, from_user=user, text="foobar", photo=[photo])
        msg.set_bot(bot)

        # Test pickling of TGObjects, we choose Message since it's contains the most subclasses.
        assert msg.get_bot()
        unpickled = pickle.loads(pickle.dumps(msg))

        with pytest.raises(RuntimeError):
            unpickled.get_bot()  # There should be no bot when we pickle TGObjects

        assert unpickled.chat == chat, f"{unpickled.chat._id_attrs} != {chat._id_attrs}"
        assert unpickled.from_user == user
        assert unpickled.date == date, f"{unpickled.date} != {date}"
        assert unpickled.photo[0] == photo

    def test_pickle_apply_api_kwargs(self, bot):
        """Makes sure that when a class gets new attributes, the api_kwargs are moved to the
        new attributes on unpickling."""
        obj = self.ChangingTO(api_kwargs={"foo": "bar"})
        pickled = pickle.dumps(obj)

        self.ChangingTO.foo = None
        obj = pickle.loads(pickled)

        assert obj.foo == "bar"
        assert obj.api_kwargs == {}

    def test_deepcopy_telegram_obj(self, bot):
        chat = Chat(2, Chat.PRIVATE)
        user = User(3, "first_name", False)
        date = datetime.datetime.now()
        photo = PhotoSize("file_id", "unique", 21, 21)
        photo.set_bot(bot)
        msg = Message(1, date, chat, from_user=user, text="foobar", photo=[photo])
        msg.set_bot(bot)

        new_msg = deepcopy(msg)

        assert new_msg == msg
        assert new_msg is not msg

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

    def test_string_representation(self):
        class TGO(TelegramObject):
            def __init__(self, api_kwargs=None):
                super().__init__(api_kwargs=api_kwargs)
                self.string_attr = "string"
                self.int_attr = 42
                self.to_attr = BotCommand("command", "description")
                self.list_attr = [
                    BotCommand("command_1", "description_1"),
                    BotCommand("command_2", "description_2"),
                ]
                self.dict_attr = {
                    BotCommand("command_1", "description_1"): BotCommand(
                        "command_2", "description_2"
                    )
                }
                self.empty_tuple_attrs = ()
                self.empty_str_attribute = ""
                # Should not be included in string representation
                self.none_attr = None

        expected_without_api_kwargs = (
            "TGO(dict_attr={BotCommand(command='command_1', description='description_1'): "
            "BotCommand(command='command_2', description='description_2')}, int_attr=42, "
            "list_attr=[BotCommand(command='command_1', description='description_1'), "
            "BotCommand(command='command_2', description='description_2')], "
            "string_attr='string', to_attr=BotCommand(command='command', "
            "description='description'))"
        )
        assert str(TGO()) == expected_without_api_kwargs
        assert repr(TGO()) == expected_without_api_kwargs

        expected_with_api_kwargs = (
            "TGO(api_kwargs={'foo': 'bar'}, dict_attr={BotCommand(command='command_1', "
            "description='description_1'): BotCommand(command='command_2', "
            "description='description_2')}, int_attr=42, "
            "list_attr=[BotCommand(command='command_1', description='description_1'), "
            "BotCommand(command='command_2', description='description_2')], "
            "string_attr='string', to_attr=BotCommand(command='command', "
            "description='description'))"
        )
        assert str(TGO(api_kwargs={"foo": "bar"})) == expected_with_api_kwargs
        assert repr(TGO(api_kwargs={"foo": "bar"})) == expected_with_api_kwargs
