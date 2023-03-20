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
import datetime
import inspect
import pickle
import re
from copy import deepcopy
from pathlib import Path
from types import MappingProxyType

import pytest

from telegram import Bot, BotCommand, Chat, Message, PhotoSize, TelegramObject, User
from telegram.ext import PicklePersistence
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


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
        class Subclass(TelegramObject):
            def __init__(self):
                super().__init__()
                self.arg = "arg"
                self.arg2 = ["arg2", "arg2"]
                self.arg3 = {"arg3": "arg3"}
                self.empty_tuple = ()

        json = Subclass().to_json()
        # Order isn't guarantied
        assert '"arg": "arg"' in json
        assert '"arg2": ["arg2", "arg2"]' in json
        assert '"arg3": {"arg3": "arg3"}' in json
        assert "empty_tuple" not in json

        # Now make sure that it doesn't work with not json stuff and that it fails loudly
        # Tuples aren't allowed as keys in json
        d = {("str", "str"): "str"}

        monkeypatch.setattr("telegram.TelegramObject.to_dict", lambda _: d)
        with pytest.raises(TypeError):
            TelegramObject().to_json()

    def test_de_json_api_kwargs(self, bot):
        to = TelegramObject.de_json(data={"foo": "bar"}, bot=bot)
        assert to.api_kwargs == {"foo": "bar"}
        assert to.get_bot() is bot

    def test_de_list(self, bot):
        class SubClass(TelegramObject):
            def __init__(self, arg: int, **kwargs):
                super().__init__(**kwargs)
                self.arg = arg

                self._id_attrs = (self.arg,)

        assert SubClass.de_list([{"arg": 1}, None, {"arg": 2}, None], bot) == (
            SubClass(1),
            SubClass(2),
        )

    def test_api_kwargs_read_only(self):
        tg_object = TelegramObject(api_kwargs={"foo": "bar"})
        tg_object._freeze()
        assert isinstance(tg_object.api_kwargs, MappingProxyType)
        with pytest.raises(TypeError):
            tg_object.api_kwargs["foo"] = "baz"
        with pytest.raises(AttributeError, match="can't be set"):
            tg_object.api_kwargs = {"foo": "baz"}

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

    def test_to_dict_missing_attribute(self):
        message = Message(
            1, datetime.datetime.now(), Chat(1, "private"), from_user=User(1, "", False)
        )
        message._unfreeze()
        del message.chat

        message_dict = message.to_dict()
        assert "chat" not in message_dict

        message_dict = message.to_dict(recursive=False)
        assert message_dict["chat"] is None

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

    def test_slot_behaviour(self):
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
        msg = Message(
            1,
            date,
            chat,
            from_user=user,
            text="foobar",
            photo=[photo],
            api_kwargs={"api": "kwargs"},
        )
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
        assert isinstance(unpickled.api_kwargs, MappingProxyType)
        assert unpickled.api_kwargs == {"api": "kwargs"}

    def test_pickle_apply_api_kwargs(self):
        """Makes sure that when a class gets new attributes, the api_kwargs are moved to the
        new attributes on unpickling."""
        obj = self.ChangingTO(api_kwargs={"foo": "bar"})
        pickled = pickle.dumps(obj)

        self.ChangingTO.foo = None
        obj = pickle.loads(pickled)

        assert obj.foo == "bar"
        assert obj.api_kwargs == {}

    async def test_pickle_backwards_compatibility(self):
        """Test when newer versions of the library remove or add attributes from classes (which
        the old pickled versions still/don't have).
        """
        # We use a modified version of the 20.0a5 Chat class, which
        # * has an `all_members_are_admins` attribute,
        # * a non-empty `api_kwargs` dict
        # * does not have the `is_forum` attribute
        # This specific version was pickled
        # using PicklePersistence.update_chat_data and that's what we use here to test if
        # * the (now) removed attribute `all_members_are_admins` was added to api_kwargs
        # * the (now) added attribute `is_forum` does not affect the unpickling
        pp = PicklePersistence(data_file("20a5_modified_chat.pickle"))
        chat = (await pp.get_chat_data())[1]
        assert chat.id == 1
        assert chat.type == Chat.PRIVATE
        assert chat.api_kwargs == {
            "all_members_are_administrators": True,
            "something": "Manually inserted",
        }
        with pytest.raises(AttributeError):
            # removed attribute should not be available as attribute, only though api_kwargs
            chat.all_members_are_administrators
        with pytest.raises(AttributeError):
            # New attribute should not be available either as is always the case for pickle
            chat.is_forum

        # Ensure that loading objects that were pickled before attributes were made immutable
        # are still mutable
        chat.id = 7
        assert chat.id == 7

    def test_deepcopy_telegram_obj(self, bot):
        chat = Chat(2, Chat.PRIVATE)
        user = User(3, "first_name", False)
        date = datetime.datetime.now()
        photo = PhotoSize("file_id", "unique", 21, 21)
        photo.set_bot(bot)
        msg = Message(
            1, date, chat, from_user=user, text="foobar", photo=[photo], api_kwargs={"foo": "bar"}
        )
        msg.set_bot(bot)

        new_msg = deepcopy(msg)

        assert new_msg == msg
        assert new_msg is not msg

        # The same bot should be present when deepcopying.
        assert new_msg.get_bot() == bot
        assert new_msg.get_bot() is bot

        assert new_msg.date == date
        assert new_msg.date is not date
        assert new_msg.chat == chat
        assert new_msg.chat is not chat
        assert new_msg.from_user == user
        assert new_msg.from_user is not user
        assert new_msg.photo[0] == photo
        assert new_msg.photo[0] is not photo
        assert new_msg.api_kwargs == {"foo": "bar"}
        assert new_msg.api_kwargs is not msg.api_kwargs

        # check that deepcopy preserves the freezing status
        with pytest.raises(
            AttributeError, match="Attribute `text` of class `Message` can't be set!"
        ):
            new_msg.text = "new text"

        msg._unfreeze()
        new_message = deepcopy(msg)
        new_message.text = "new text"
        assert new_message.text == "new text"

    def test_deepcopy_subclass_telegram_obj(self, bot):
        s = self.Sub("private", "normal", bot)
        d = deepcopy(s)
        assert d is not s
        assert d._private == s._private  # Can't test for identity since two equal strings is True
        assert d._bot == s._bot
        assert d._bot is s._bot
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

    @pytest.mark.parametrize("cls", TO_SUBCLASSES, ids=[cls.__name__ for cls in TO_SUBCLASSES])
    def test_subclasses_are_frozen(self, cls):
        if cls is TelegramObject or cls.__name__.startswith("_"):
            # Protected classes don't need to be frozen and neither does the base class
            return

        # instantiating each subclass would be tedious as some attributes require special init
        # args. So we inspect the code instead.

        source_file = inspect.getsourcefile(cls.__init__)
        parents = Path(source_file).parents
        is_test_file = Path(__file__).parent.resolve() in parents

        if is_test_file:
            # If the class is defined in a test file, we don't want to test it.
            return

        if source_file.endswith("telegramobject.py"):
            pytest.fail(
                f"{cls.__name__} does not have its own `__init__` "
                "and can therefore not be frozen correctly"
            )

        source_lines, first_line = inspect.getsourcelines(cls.__init__)

        # We use regex matching since a simple "if self._freeze() in source_lines[-1]" would also
        # allo commented lines.
        last_line_freezes = re.match(r"\s*self\.\_freeze\(\)", source_lines[-1])
        uses_with_unfrozen = re.search(
            r"\n\s*with self\.\_unfrozen\(\)\:", inspect.getsource(cls.__init__)
        )

        assert last_line_freezes or uses_with_unfrozen, f"{cls.__name__} is not frozen correctly"

    def test_freeze_unfreeze(self):
        class TestSub(TelegramObject):
            def __init__(self):
                super().__init__()
                self._protected = True
                self.public = True
                self._freeze()

        foo = TestSub()
        foo._protected = False
        assert foo._protected is False

        with pytest.raises(
            AttributeError, match="Attribute `public` of class `TestSub` can't be set!"
        ):
            foo.public = False

        with pytest.raises(
            AttributeError, match="Attribute `public` of class `TestSub` can't be deleted!"
        ):
            del foo.public

        foo._unfreeze()
        foo._protected = True
        assert foo._protected is True
        foo.public = False
        assert foo.public is False
        del foo.public
        del foo._protected
        assert not hasattr(foo, "public")
        assert not hasattr(foo, "_protected")
