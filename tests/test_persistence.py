#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
import gzip
import signal
import uuid
from threading import Lock

from telegram.ext.callbackdatacache import CallbackDataCache
from telegram.utils.helpers import encode_conversations_to_json

try:
    import ujson as json
except ImportError:
    import json
import logging
import os
import pickle
from collections import defaultdict
from collections.abc import Container
from time import sleep
from sys import version_info as py_ver

import pytest

from telegram import Update, Message, User, Chat, MessageEntity, Bot
from telegram.ext import (
    BasePersistence,
    Updater,
    ConversationHandler,
    MessageHandler,
    Filters,
    PicklePersistence,
    CommandHandler,
    DictPersistence,
    TypeHandler,
    JobQueue,
    ContextTypes,
)


@pytest.fixture(autouse=True)
def change_directory(tmp_path):
    orig_dir = os.getcwd()
    # Switch to a temporary directory so we don't have to worry about cleaning up files
    # (str() for py<3.6)
    os.chdir(str(tmp_path))
    yield
    # Go back to original directory
    os.chdir(orig_dir)


@pytest.fixture(autouse=True)
def reset_callback_data_cache(bot):
    yield
    bot.callback_data_cache.clear_callback_data()
    bot.callback_data_cache.clear_callback_queries()
    bot.arbitrary_callback_data = False


class OwnPersistence(BasePersistence):
    def get_bot_data(self):
        raise NotImplementedError

    def get_chat_data(self):
        raise NotImplementedError

    def get_user_data(self):
        raise NotImplementedError

    def get_conversations(self, name):
        raise NotImplementedError

    def update_bot_data(self, data):
        raise NotImplementedError

    def update_chat_data(self, chat_id, data):
        raise NotImplementedError

    def update_conversation(self, name, key, new_state):
        raise NotImplementedError

    def update_user_data(self, user_id, data):
        raise NotImplementedError


@pytest.fixture(scope="function")
def base_persistence():
    return OwnPersistence(
        store_chat_data=True, store_user_data=True, store_bot_data=True, store_callback_data=True
    )


@pytest.fixture(scope="function")
def bot_persistence():
    class BotPersistence(BasePersistence):
        __slots__ = ()

        def __init__(self):
            super().__init__()
            self.bot_data = None
            self.chat_data = defaultdict(dict)
            self.user_data = defaultdict(dict)
            self.callback_data = None

        def get_bot_data(self):
            return self.bot_data

        def get_chat_data(self):
            return self.chat_data

        def get_user_data(self):
            return self.user_data

        def get_callback_data(self):
            return self.callback_data

        def get_conversations(self, name):
            raise NotImplementedError

        def update_bot_data(self, data):
            self.bot_data = data

        def update_chat_data(self, chat_id, data):
            self.chat_data[chat_id] = data

        def update_user_data(self, user_id, data):
            self.user_data[user_id] = data

        def update_callback_data(self, data):
            self.callback_data = data

        def update_conversation(self, name, key, new_state):
            raise NotImplementedError

    return BotPersistence()


@pytest.fixture(scope="function")
def bot_data():
    return {'test1': 'test2', 'test3': {'test4': 'test5'}}


@pytest.fixture(scope="function")
def chat_data():
    return defaultdict(
        dict, {-12345: {'test1': 'test2', 'test3': {'test4': 'test5'}}, -67890: {3: 'test4'}}
    )


@pytest.fixture(scope="function")
def user_data():
    return defaultdict(
        dict, {12345: {'test1': 'test2', 'test3': {'test4': 'test5'}}, 67890: {3: 'test4'}}
    )


@pytest.fixture(scope="function")
def callback_data():
    return [('test1', 1000, {'button1': 'test0', 'button2': 'test1'})], {'test1': 'test2'}


@pytest.fixture(scope='function')
def conversations():
    return {
        'name1': {(123, 123): 3, (456, 654): 4},
        'name2': {(123, 321): 1, (890, 890): 2},
        'name3': {(123, 321): 1, (890, 890): 2},
    }


@pytest.fixture(scope="function")
def updater(bot, base_persistence):
    base_persistence.store_chat_data = False
    base_persistence.store_bot_data = False
    base_persistence.store_user_data = False
    base_persistence.store_callback_data = False
    u = Updater(bot=bot, persistence=base_persistence)
    base_persistence.store_bot_data = True
    base_persistence.store_chat_data = True
    base_persistence.store_user_data = True
    base_persistence.store_callback_data = True
    return u


@pytest.fixture(scope='function')
def job_queue(bot):
    jq = JobQueue()
    yield jq
    jq.stop()


def assert_data_in_cache(callback_data_cache: CallbackDataCache, data):
    for val in callback_data_cache._keyboard_data.values():
        if data in val.button_data.values():
            return data
    return False


class TestBasePersistence:
    test_flag = False

    @pytest.fixture(scope='function', autouse=True)
    def reset(self):
        self.test_flag = False

    def test_slot_behaviour(self, bot_persistence, mro_slots, recwarn):
        inst = bot_persistence
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        # assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        # The below test fails if the child class doesn't define __slots__ (not a cause of concern)
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.store_user_data, inst.custom = {}, "custom persistence shouldn't warn"
        assert len(recwarn) == 0, recwarn.list
        assert '__dict__' not in BasePersistence.__slots__ if py_ver < (3, 7) else True, 'has dict'

    def test_creation(self, base_persistence):
        assert base_persistence.store_chat_data
        assert base_persistence.store_user_data
        assert base_persistence.store_bot_data

    def test_abstract_methods(self, base_persistence):
        with pytest.raises(
            TypeError,
            match=(
                'get_bot_data, get_chat_data, get_conversations, '
                'get_user_data, update_bot_data, update_chat_data, '
                'update_conversation, update_user_data'
            ),
        ):
            BasePersistence()
        with pytest.raises(NotImplementedError):
            base_persistence.get_callback_data()
        with pytest.raises(NotImplementedError):
            base_persistence.update_callback_data((None, {'foo': 'bar'}))

    def test_implementation(self, updater, base_persistence):
        dp = updater.dispatcher
        assert dp.persistence == base_persistence

    def test_conversationhandler_addition(self, dp, base_persistence):
        with pytest.raises(ValueError, match="when handler is unnamed"):
            ConversationHandler([], [], [], persistent=True)
        with pytest.raises(ValueError, match="if dispatcher has no persistence"):
            dp.add_handler(ConversationHandler([], {}, [], persistent=True, name="My Handler"))
        dp.persistence = base_persistence

    def test_dispatcher_integration_init(
        self, bot, base_persistence, chat_data, user_data, bot_data, callback_data
    ):
        def get_user_data():
            return "test"

        def get_chat_data():
            return "test"

        def get_bot_data():
            return "test"

        def get_callback_data():
            return "test"

        base_persistence.get_user_data = get_user_data
        base_persistence.get_chat_data = get_chat_data
        base_persistence.get_bot_data = get_bot_data
        base_persistence.get_callback_data = get_callback_data

        with pytest.raises(ValueError, match="user_data must be of type defaultdict"):
            u = Updater(bot=bot, persistence=base_persistence)

        def get_user_data():
            return user_data

        base_persistence.get_user_data = get_user_data
        with pytest.raises(ValueError, match="chat_data must be of type defaultdict"):
            Updater(bot=bot, persistence=base_persistence)

        def get_chat_data():
            return chat_data

        base_persistence.get_chat_data = get_chat_data
        with pytest.raises(ValueError, match="bot_data must be of type dict"):
            Updater(bot=bot, persistence=base_persistence)

        def get_bot_data():
            return bot_data

        base_persistence.get_bot_data = get_bot_data
        with pytest.raises(ValueError, match="callback_data must be a 2-tuple"):
            Updater(bot=bot, persistence=base_persistence)

        def get_callback_data():
            return callback_data

        base_persistence.get_callback_data = get_callback_data
        u = Updater(bot=bot, persistence=base_persistence)
        assert u.dispatcher.bot_data == bot_data
        assert u.dispatcher.chat_data == chat_data
        assert u.dispatcher.user_data == user_data
        assert u.dispatcher.bot.callback_data_cache.persistence_data == callback_data
        u.dispatcher.chat_data[442233]['test5'] = 'test6'
        assert u.dispatcher.chat_data[442233]['test5'] == 'test6'

    @pytest.mark.parametrize('run_async', [True, False], ids=['synchronous', 'run_async'])
    def test_dispatcher_integration_handlers(
        self,
        cdp,
        caplog,
        bot,
        base_persistence,
        chat_data,
        user_data,
        bot_data,
        callback_data,
        run_async,
    ):
        def get_user_data():
            return user_data

        def get_chat_data():
            return chat_data

        def get_bot_data():
            return bot_data

        def get_callback_data():
            return callback_data

        base_persistence.get_user_data = get_user_data
        base_persistence.get_chat_data = get_chat_data
        base_persistence.get_bot_data = get_bot_data
        base_persistence.get_callback_data = get_callback_data
        # base_persistence.update_chat_data = lambda x: x
        # base_persistence.update_user_data = lambda x: x
        base_persistence.refresh_bot_data = lambda x: x
        base_persistence.refresh_chat_data = lambda x, y: x
        base_persistence.refresh_user_data = lambda x, y: x
        updater = Updater(bot=bot, persistence=base_persistence, use_context=True)
        dp = updater.dispatcher

        def callback_known_user(update, context):
            if not context.user_data['test1'] == 'test2':
                pytest.fail('user_data corrupt')
            if not context.bot_data == bot_data:
                pytest.fail('bot_data corrupt')

        def callback_known_chat(update, context):
            if not context.chat_data['test3'] == 'test4':
                pytest.fail('chat_data corrupt')
            if not context.bot_data == bot_data:
                pytest.fail('bot_data corrupt')

        def callback_unknown_user_or_chat(update, context):
            if not context.user_data == {}:
                pytest.fail('user_data corrupt')
            if not context.chat_data == {}:
                pytest.fail('chat_data corrupt')
            if not context.bot_data == bot_data:
                pytest.fail('bot_data corrupt')
            context.user_data[1] = 'test7'
            context.chat_data[2] = 'test8'
            context.bot_data['test0'] = 'test0'
            context.bot.callback_data_cache.put('test0')

        known_user = MessageHandler(
            Filters.user(user_id=12345),
            callback_known_user,
            pass_chat_data=True,
            pass_user_data=True,
        )
        known_chat = MessageHandler(
            Filters.chat(chat_id=-67890),
            callback_known_chat,
            pass_chat_data=True,
            pass_user_data=True,
        )
        unknown = MessageHandler(
            Filters.all, callback_unknown_user_or_chat, pass_chat_data=True, pass_user_data=True
        )
        dp.add_handler(known_user)
        dp.add_handler(known_chat)
        dp.add_handler(unknown)
        user1 = User(id=12345, first_name='test user', is_bot=False)
        user2 = User(id=54321, first_name='test user', is_bot=False)
        chat1 = Chat(id=-67890, type='group')
        chat2 = Chat(id=-987654, type='group')
        m = Message(1, None, chat2, from_user=user1)
        u = Update(0, m)
        with caplog.at_level(logging.ERROR):
            dp.process_update(u)
        rec = caplog.records[-1]
        assert rec.getMessage() == 'No error handlers are registered, logging exception.'
        assert rec.levelname == 'ERROR'
        rec = caplog.records[-2]
        assert rec.getMessage() == 'No error handlers are registered, logging exception.'
        assert rec.levelname == 'ERROR'
        rec = caplog.records[-3]
        assert rec.getMessage() == 'No error handlers are registered, logging exception.'
        assert rec.levelname == 'ERROR'
        m.from_user = user2
        m.chat = chat1
        u = Update(1, m)
        dp.process_update(u)
        m.chat = chat2
        u = Update(2, m)

        def save_bot_data(data):
            if 'test0' not in data:
                pytest.fail()

        def save_chat_data(data):
            if -987654 not in data:
                pytest.fail()

        def save_user_data(data):
            if 54321 not in data:
                pytest.fail()

        def save_callback_data(data):
            if not assert_data_in_cache(dp.bot.callback_data, 'test0'):
                pytest.fail()

        base_persistence.update_chat_data = save_chat_data
        base_persistence.update_user_data = save_user_data
        base_persistence.update_bot_data = save_bot_data
        base_persistence.update_callback_data = save_callback_data
        dp.process_update(u)

        assert dp.user_data[54321][1] == 'test7'
        assert dp.chat_data[-987654][2] == 'test8'
        assert dp.bot_data['test0'] == 'test0'
        assert assert_data_in_cache(dp.bot.callback_data_cache, 'test0')

    @pytest.mark.parametrize(
        'store_user_data', [True, False], ids=['store_user_data-True', 'store_user_data-False']
    )
    @pytest.mark.parametrize(
        'store_chat_data', [True, False], ids=['store_chat_data-True', 'store_chat_data-False']
    )
    @pytest.mark.parametrize(
        'store_bot_data', [True, False], ids=['store_bot_data-True', 'store_bot_data-False']
    )
    @pytest.mark.parametrize('run_async', [True, False], ids=['synchronous', 'run_async'])
    def test_persistence_dispatcher_integration_refresh_data(
        self,
        cdp,
        base_persistence,
        chat_data,
        bot_data,
        user_data,
        store_bot_data,
        store_chat_data,
        store_user_data,
        run_async,
    ):
        base_persistence.refresh_bot_data = lambda x: x.setdefault(
            'refreshed', x.get('refreshed', 0) + 1
        )
        # x is the user/chat_id
        base_persistence.refresh_chat_data = lambda x, y: y.setdefault('refreshed', x)
        base_persistence.refresh_user_data = lambda x, y: y.setdefault('refreshed', x)
        base_persistence.store_bot_data = store_bot_data
        base_persistence.store_chat_data = store_chat_data
        base_persistence.store_user_data = store_user_data
        cdp.persistence = base_persistence

        self.test_flag = True

        def callback_with_user_and_chat(update, context):
            if store_user_data:
                if context.user_data.get('refreshed') != update.effective_user.id:
                    self.test_flag = 'user_data was not refreshed'
            else:
                if 'refreshed' in context.user_data:
                    self.test_flag = 'user_data was wrongly refreshed'
            if store_chat_data:
                if context.chat_data.get('refreshed') != update.effective_chat.id:
                    self.test_flag = 'chat_data was not refreshed'
            else:
                if 'refreshed' in context.chat_data:
                    self.test_flag = 'chat_data was wrongly refreshed'
            if store_bot_data:
                if context.bot_data.get('refreshed') != 1:
                    self.test_flag = 'bot_data was not refreshed'
            else:
                if 'refreshed' in context.bot_data:
                    self.test_flag = 'bot_data was wrongly refreshed'

        def callback_without_user_and_chat(_, context):
            if store_bot_data:
                if context.bot_data.get('refreshed') != 1:
                    self.test_flag = 'bot_data was not refreshed'
            else:
                if 'refreshed' in context.bot_data:
                    self.test_flag = 'bot_data was wrongly refreshed'

        with_user_and_chat = MessageHandler(
            Filters.user(user_id=12345),
            callback_with_user_and_chat,
            pass_chat_data=True,
            pass_user_data=True,
            run_async=run_async,
        )
        without_user_and_chat = MessageHandler(
            Filters.all,
            callback_without_user_and_chat,
            pass_chat_data=True,
            pass_user_data=True,
            run_async=run_async,
        )
        cdp.add_handler(with_user_and_chat)
        cdp.add_handler(without_user_and_chat)
        user = User(id=12345, first_name='test user', is_bot=False)
        chat = Chat(id=-987654, type='group')
        m = Message(1, None, chat, from_user=user)

        # has user and chat
        u = Update(0, m)
        cdp.process_update(u)

        assert self.test_flag is True

        # has neither user nor hat
        m.from_user = None
        m.chat = None
        u = Update(1, m)
        cdp.process_update(u)

        assert self.test_flag is True

        sleep(0.1)

    def test_persistence_dispatcher_arbitrary_update_types(self, dp, base_persistence, caplog):
        # Updates used with TypeHandler doesn't necessarily have the proper attributes for
        # persistence, makes sure it works anyways

        dp.persistence = base_persistence

        class MyUpdate:
            pass

        dp.add_handler(TypeHandler(MyUpdate, lambda *_: None))

        with caplog.at_level(logging.ERROR):
            dp.process_update(MyUpdate())
        assert 'An uncaught error was raised while processing the update' not in caplog.text

    def test_bot_replace_insert_bot(self, bot, bot_persistence):
        class CustomSlottedClass:
            __slots__ = ('bot', '__dict__')

            def __init__(self):
                self.bot = bot
                self.not_in_slots = bot

            def __eq__(self, other):
                if isinstance(other, CustomSlottedClass):
                    return self.bot is other.bot and self.not_in_slots is other.not_in_slots
                return False

        class DictNotInSlots(Container):
            """This classes parent has slots, but __dict__ is not in those slots."""

            def __init__(self):
                self.bot = bot

            def __contains__(self, item):
                return True

            def __eq__(self, other):
                if isinstance(other, DictNotInSlots):
                    return self.bot is other.bot
                return False

        class CustomClass:
            def __init__(self):
                self.bot = bot
                self.slotted_object = CustomSlottedClass()
                self.dict_not_in_slots_object = DictNotInSlots()
                self.list_ = [1, 2, bot]
                self.tuple_ = tuple(self.list_)
                self.set_ = set(self.list_)
                self.frozenset_ = frozenset(self.list_)
                self.dict_ = {item: item for item in self.list_}
                self.defaultdict_ = defaultdict(dict, self.dict_)

            @staticmethod
            def replace_bot():
                cc = CustomClass()
                cc.bot = BasePersistence.REPLACED_BOT
                cc.slotted_object.bot = BasePersistence.REPLACED_BOT
                cc.slotted_object.not_in_slots = BasePersistence.REPLACED_BOT
                cc.dict_not_in_slots_object.bot = BasePersistence.REPLACED_BOT
                cc.list_ = [1, 2, BasePersistence.REPLACED_BOT]
                cc.tuple_ = tuple(cc.list_)
                cc.set_ = set(cc.list_)
                cc.frozenset_ = frozenset(cc.list_)
                cc.dict_ = {item: item for item in cc.list_}
                cc.defaultdict_ = defaultdict(dict, cc.dict_)
                return cc

            def __eq__(self, other):
                if isinstance(other, CustomClass):
                    return (
                        self.bot is other.bot
                        and self.slotted_object == other.slotted_object
                        and self.dict_not_in_slots_object == other.dict_not_in_slots_object
                        and self.list_ == other.list_
                        and self.tuple_ == other.tuple_
                        and self.set_ == other.set_
                        and self.frozenset_ == other.frozenset_
                        and self.dict_ == other.dict_
                        and self.defaultdict_ == other.defaultdict_
                    )
                return False

        persistence = bot_persistence
        persistence.set_bot(bot)
        cc = CustomClass()

        persistence.update_bot_data({1: cc})
        assert persistence.bot_data[1].bot == BasePersistence.REPLACED_BOT
        assert persistence.bot_data[1] == cc.replace_bot()

        persistence.update_chat_data(123, {1: cc})
        assert persistence.chat_data[123][1].bot == BasePersistence.REPLACED_BOT
        assert persistence.chat_data[123][1] == cc.replace_bot()

        persistence.update_user_data(123, {1: cc})
        assert persistence.user_data[123][1].bot == BasePersistence.REPLACED_BOT
        assert persistence.user_data[123][1] == cc.replace_bot()

        persistence.update_callback_data(([('1', 2, {0: cc})], {'1': '2'}))
        assert persistence.callback_data[0][0][2][0].bot == BasePersistence.REPLACED_BOT
        assert persistence.callback_data[0][0][2][0] == cc.replace_bot()

        assert persistence.get_bot_data()[1] == cc
        assert persistence.get_bot_data()[1].bot is bot
        assert persistence.get_chat_data()[123][1] == cc
        assert persistence.get_chat_data()[123][1].bot is bot
        assert persistence.get_user_data()[123][1] == cc
        assert persistence.get_user_data()[123][1].bot is bot
        assert persistence.get_callback_data()[0][0][2][0].bot is bot
        assert persistence.get_callback_data()[0][0][2][0] == cc

    def test_bot_replace_insert_bot_unpickable_objects(self, bot, bot_persistence, recwarn):
        """Here check that unpickable objects are just returned verbatim."""
        persistence = bot_persistence
        persistence.set_bot(bot)

        class CustomClass:
            def __copy__(self):
                raise TypeError('UnhandledException')

        lock = Lock()

        persistence.update_bot_data({1: lock})
        assert persistence.bot_data[1] is lock
        persistence.update_chat_data(123, {1: lock})
        assert persistence.chat_data[123][1] is lock
        persistence.update_user_data(123, {1: lock})
        assert persistence.user_data[123][1] is lock
        persistence.update_callback_data(([('1', 2, {0: lock})], {'1': '2'}))
        assert persistence.callback_data[0][0][2][0] is lock

        assert persistence.get_bot_data()[1] is lock
        assert persistence.get_chat_data()[123][1] is lock
        assert persistence.get_user_data()[123][1] is lock
        assert persistence.get_callback_data()[0][0][2][0] is lock

        cc = CustomClass()

        persistence.update_bot_data({1: cc})
        assert persistence.bot_data[1] is cc
        persistence.update_chat_data(123, {1: cc})
        assert persistence.chat_data[123][1] is cc
        persistence.update_user_data(123, {1: cc})
        assert persistence.user_data[123][1] is cc
        persistence.update_callback_data(([('1', 2, {0: cc})], {'1': '2'}))
        assert persistence.callback_data[0][0][2][0] is cc

        assert persistence.get_bot_data()[1] is cc
        assert persistence.get_chat_data()[123][1] is cc
        assert persistence.get_user_data()[123][1] is cc
        assert persistence.get_callback_data()[0][0][2][0] is cc

        assert len(recwarn) == 2
        assert str(recwarn[0].message).startswith(
            "BasePersistence.replace_bot does not handle objects that can not be copied."
        )
        assert str(recwarn[1].message).startswith(
            "BasePersistence.insert_bot does not handle objects that can not be copied."
        )

    def test_bot_replace_insert_bot_unparsable_objects(self, bot, bot_persistence, recwarn):
        """Here check that objects in __dict__ or __slots__ that can't
        be parsed are just returned verbatim."""
        persistence = bot_persistence
        persistence.set_bot(bot)

        uuid_obj = uuid.uuid4()

        persistence.update_bot_data({1: uuid_obj})
        assert persistence.bot_data[1] is uuid_obj
        persistence.update_chat_data(123, {1: uuid_obj})
        assert persistence.chat_data[123][1] is uuid_obj
        persistence.update_user_data(123, {1: uuid_obj})
        assert persistence.user_data[123][1] is uuid_obj
        persistence.update_callback_data(([('1', 2, {0: uuid_obj})], {'1': '2'}))
        assert persistence.callback_data[0][0][2][0] is uuid_obj

        assert persistence.get_bot_data()[1] is uuid_obj
        assert persistence.get_chat_data()[123][1] is uuid_obj
        assert persistence.get_user_data()[123][1] is uuid_obj
        assert persistence.get_callback_data()[0][0][2][0] is uuid_obj

        assert len(recwarn) == 2
        assert str(recwarn[0].message).startswith(
            "Parsing of an object failed with the following exception: "
        )
        assert str(recwarn[1].message).startswith(
            "Parsing of an object failed with the following exception: "
        )

    def test_bot_replace_insert_bot_classes(self, bot, bot_persistence, recwarn):
        """Here check that classes are just returned verbatim."""
        persistence = bot_persistence
        persistence.set_bot(bot)

        class CustomClass:
            pass

        persistence.update_bot_data({1: CustomClass})
        assert persistence.bot_data[1] is CustomClass
        persistence.update_chat_data(123, {1: CustomClass})
        assert persistence.chat_data[123][1] is CustomClass
        persistence.update_user_data(123, {1: CustomClass})
        assert persistence.user_data[123][1] is CustomClass

        assert persistence.get_bot_data()[1] is CustomClass
        assert persistence.get_chat_data()[123][1] is CustomClass
        assert persistence.get_user_data()[123][1] is CustomClass

        assert len(recwarn) == 2
        assert str(recwarn[0].message).startswith(
            "BasePersistence.replace_bot does not handle classes."
        )
        assert str(recwarn[1].message).startswith(
            "BasePersistence.insert_bot does not handle classes."
        )

    def test_bot_replace_insert_bot_objects_with_faulty_equality(self, bot, bot_persistence):
        """Here check that trying to compare obj == self.REPLACED_BOT doesn't lead to problems."""
        persistence = bot_persistence
        persistence.set_bot(bot)

        class CustomClass:
            def __init__(self, data):
                self.data = data

            def __eq__(self, other):
                raise RuntimeError("Can't be compared")

        cc = CustomClass({1: bot, 2: 'foo'})
        expected = {1: BasePersistence.REPLACED_BOT, 2: 'foo'}

        persistence.update_bot_data({1: cc})
        assert persistence.bot_data[1].data == expected
        persistence.update_chat_data(123, {1: cc})
        assert persistence.chat_data[123][1].data == expected
        persistence.update_user_data(123, {1: cc})
        assert persistence.user_data[123][1].data == expected
        persistence.update_callback_data(([('1', 2, {0: cc})], {'1': '2'}))
        assert persistence.callback_data[0][0][2][0].data == expected

        expected = {1: bot, 2: 'foo'}

        assert persistence.get_bot_data()[1].data == expected
        assert persistence.get_chat_data()[123][1].data == expected
        assert persistence.get_user_data()[123][1].data == expected
        assert persistence.get_callback_data()[0][0][2][0].data == expected

    @pytest.mark.filterwarnings('ignore:BasePersistence')
    def test_replace_insert_bot_item_identity(self, bot, bot_persistence):
        persistence = bot_persistence
        persistence.set_bot(bot)

        class CustomSlottedClass:
            __slots__ = ('value',)

            def __init__(self):
                self.value = 5

        class CustomClass:
            pass

        slot_object = CustomSlottedClass()
        dict_object = CustomClass()
        lock = Lock()
        list_ = [slot_object, dict_object, lock]
        tuple_ = (1, 2, 3)
        dict_ = {1: slot_object, 2: dict_object}

        data = {
            'bot_1': bot,
            'bot_2': bot,
            'list_1': list_,
            'list_2': list_,
            'tuple_1': tuple_,
            'tuple_2': tuple_,
            'dict_1': dict_,
            'dict_2': dict_,
        }

        def make_assertion(data_):
            return (
                data_['bot_1'] is data_['bot_2']
                and data_['list_1'] is data_['list_2']
                and data_['list_1'][0] is data_['list_2'][0]
                and data_['list_1'][1] is data_['list_2'][1]
                and data_['list_1'][2] is data_['list_2'][2]
                and data_['tuple_1'] is data_['tuple_2']
                and data_['dict_1'] is data_['dict_2']
                and data_['dict_1'][1] is data_['dict_2'][1]
                and data_['dict_1'][1] is data_['list_1'][0]
                and data_['dict_1'][2] is data_['list_1'][1]
                and data_['dict_1'][2] is data_['dict_2'][2]
            )

        persistence.update_bot_data(data)
        assert make_assertion(persistence.bot_data)
        assert make_assertion(persistence.get_bot_data())

    def test_set_bot_exception(self, bot):
        non_ext_bot = Bot(bot.token)
        persistence = OwnPersistence(store_callback_data=True)
        with pytest.raises(TypeError, match='store_callback_data can only be used'):
            persistence.set_bot(non_ext_bot)


@pytest.fixture(scope='function')
def pickle_persistence():
    return PicklePersistence(
        filename='pickletest',
        store_user_data=True,
        store_chat_data=True,
        store_bot_data=True,
        store_callback_data=True,
        single_file=False,
        on_flush=False,
    )


@pytest.fixture(scope='function')
def pickle_persistence_only_bot():
    return PicklePersistence(
        filename='pickletest',
        store_user_data=False,
        store_chat_data=False,
        store_bot_data=True,
        store_callback_data=False,
        single_file=False,
        on_flush=False,
    )


@pytest.fixture(scope='function')
def pickle_persistence_only_chat():
    return PicklePersistence(
        filename='pickletest',
        store_user_data=False,
        store_chat_data=True,
        store_bot_data=False,
        store_callback_data=False,
        single_file=False,
        on_flush=False,
    )


@pytest.fixture(scope='function')
def pickle_persistence_only_user():
    return PicklePersistence(
        filename='pickletest',
        store_user_data=True,
        store_chat_data=False,
        store_bot_data=False,
        store_callback_data=False,
        single_file=False,
        on_flush=False,
    )


@pytest.fixture(scope='function')
def pickle_persistence_only_callback():
    return PicklePersistence(
        filename='pickletest',
        store_user_data=False,
        store_chat_data=False,
        store_bot_data=False,
        store_callback_data=True,
        single_file=False,
        on_flush=False,
    )


@pytest.fixture(scope='function')
def bad_pickle_files():
    for name in [
        'pickletest_user_data',
        'pickletest_chat_data',
        'pickletest_bot_data',
        'pickletest_callback_data',
        'pickletest_conversations',
        'pickletest',
    ]:
        with open(name, 'w') as f:
            f.write('(())')
    yield True


@pytest.fixture(scope='function')
def invalid_pickle_files():
    for name in [
        'pickletest_user_data',
        'pickletest_chat_data',
        'pickletest_bot_data',
        'pickletest_callback_data',
        'pickletest_conversations',
        'pickletest',
    ]:
        # Just a random way to trigger pickle.UnpicklingError
        # see https://stackoverflow.com/a/44422239/10606962
        with gzip.open(name, 'wb') as file:
            pickle.dump([1, 2, 3], file)
    yield True


@pytest.fixture(scope='function')
def good_pickle_files(user_data, chat_data, bot_data, callback_data, conversations):
    data = {
        'user_data': user_data,
        'chat_data': chat_data,
        'bot_data': bot_data,
        'callback_data': callback_data,
        'conversations': conversations,
    }
    with open('pickletest_user_data', 'wb') as f:
        pickle.dump(user_data, f)
    with open('pickletest_chat_data', 'wb') as f:
        pickle.dump(chat_data, f)
    with open('pickletest_bot_data', 'wb') as f:
        pickle.dump(bot_data, f)
    with open('pickletest_callback_data', 'wb') as f:
        pickle.dump(callback_data, f)
    with open('pickletest_conversations', 'wb') as f:
        pickle.dump(conversations, f)
    with open('pickletest', 'wb') as f:
        pickle.dump(data, f)
    yield True


@pytest.fixture(scope='function')
def pickle_files_wo_bot_data(user_data, chat_data, callback_data, conversations):
    data = {
        'user_data': user_data,
        'chat_data': chat_data,
        'conversations': conversations,
        'callback_data': callback_data,
    }
    with open('pickletest_user_data', 'wb') as f:
        pickle.dump(user_data, f)
    with open('pickletest_chat_data', 'wb') as f:
        pickle.dump(chat_data, f)
    with open('pickletest_callback_data', 'wb') as f:
        pickle.dump(callback_data, f)
    with open('pickletest_conversations', 'wb') as f:
        pickle.dump(conversations, f)
    with open('pickletest', 'wb') as f:
        pickle.dump(data, f)
    yield True


@pytest.fixture(scope='function')
def pickle_files_wo_callback_data(user_data, chat_data, bot_data, conversations):
    data = {
        'user_data': user_data,
        'chat_data': chat_data,
        'bot_data': bot_data,
        'conversations': conversations,
    }
    with open('pickletest_user_data', 'wb') as f:
        pickle.dump(user_data, f)
    with open('pickletest_chat_data', 'wb') as f:
        pickle.dump(chat_data, f)
    with open('pickletest_bot_data', 'wb') as f:
        pickle.dump(bot_data, f)
    with open('pickletest_conversations', 'wb') as f:
        pickle.dump(conversations, f)
    with open('pickletest', 'wb') as f:
        pickle.dump(data, f)
    yield True


@pytest.fixture(scope='function')
def update(bot):
    user = User(id=321, first_name='test_user', is_bot=False)
    chat = Chat(id=123, type='group')
    message = Message(1, None, chat, from_user=user, text="Hi there", bot=bot)
    return Update(0, message=message)


class CustomMapping(defaultdict):
    pass


class TestPicklePersistence:
    def test_slot_behaviour(self, mro_slots, recwarn, pickle_persistence):
        inst = pickle_persistence
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        # assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.store_user_data = 'should give warning', {}
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_pickle_behaviour_with_slots(self, pickle_persistence):
        bot_data = pickle_persistence.get_bot_data()
        bot_data['message'] = Message(3, None, Chat(2, type='supergroup'))
        pickle_persistence.update_bot_data(bot_data)
        retrieved = pickle_persistence.get_bot_data()
        assert retrieved == bot_data

    def test_no_files_present_multi_file(self, pickle_persistence):
        assert pickle_persistence.get_user_data() == defaultdict(dict)
        assert pickle_persistence.get_user_data() == defaultdict(dict)
        assert pickle_persistence.get_chat_data() == defaultdict(dict)
        assert pickle_persistence.get_chat_data() == defaultdict(dict)
        assert pickle_persistence.get_bot_data() == {}
        assert pickle_persistence.get_bot_data() == {}
        assert pickle_persistence.get_callback_data() is None
        assert pickle_persistence.get_conversations('noname') == {}
        assert pickle_persistence.get_conversations('noname') == {}

    def test_no_files_present_single_file(self, pickle_persistence):
        pickle_persistence.single_file = True
        assert pickle_persistence.get_user_data() == defaultdict(dict)
        assert pickle_persistence.get_chat_data() == defaultdict(dict)
        assert pickle_persistence.get_bot_data() == {}
        assert pickle_persistence.get_callback_data() is None
        assert pickle_persistence.get_conversations('noname') == {}

    def test_with_bad_multi_file(self, pickle_persistence, bad_pickle_files):
        with pytest.raises(TypeError, match='pickletest_user_data'):
            pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match='pickletest_chat_data'):
            pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match='pickletest_bot_data'):
            pickle_persistence.get_bot_data()
        with pytest.raises(TypeError, match='pickletest_callback_data'):
            pickle_persistence.get_callback_data()
        with pytest.raises(TypeError, match='pickletest_conversations'):
            pickle_persistence.get_conversations('name')

    def test_with_invalid_multi_file(self, pickle_persistence, invalid_pickle_files):
        with pytest.raises(TypeError, match='pickletest_user_data does not contain'):
            pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match='pickletest_chat_data does not contain'):
            pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match='pickletest_bot_data does not contain'):
            pickle_persistence.get_bot_data()
        with pytest.raises(TypeError, match='pickletest_callback_data does not contain'):
            pickle_persistence.get_callback_data()
        with pytest.raises(TypeError, match='pickletest_conversations does not contain'):
            pickle_persistence.get_conversations('name')

    def test_with_bad_single_file(self, pickle_persistence, bad_pickle_files):
        pickle_persistence.single_file = True
        with pytest.raises(TypeError, match='pickletest'):
            pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match='pickletest'):
            pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match='pickletest'):
            pickle_persistence.get_bot_data()
        with pytest.raises(TypeError, match='pickletest'):
            pickle_persistence.get_callback_data()
        with pytest.raises(TypeError, match='pickletest'):
            pickle_persistence.get_conversations('name')

    def test_with_invalid_single_file(self, pickle_persistence, invalid_pickle_files):
        pickle_persistence.single_file = True
        with pytest.raises(TypeError, match='pickletest does not contain'):
            pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match='pickletest does not contain'):
            pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match='pickletest does not contain'):
            pickle_persistence.get_bot_data()
        with pytest.raises(TypeError, match='pickletest does not contain'):
            pickle_persistence.get_callback_data()
        with pytest.raises(TypeError, match='pickletest does not contain'):
            pickle_persistence.get_conversations('name')

    def test_with_good_multi_file(self, pickle_persistence, good_pickle_files):
        user_data = pickle_persistence.get_user_data()
        assert isinstance(user_data, defaultdict)
        assert user_data[12345]['test1'] == 'test2'
        assert user_data[67890][3] == 'test4'
        assert user_data[54321] == {}

        chat_data = pickle_persistence.get_chat_data()
        assert isinstance(chat_data, defaultdict)
        assert chat_data[-12345]['test1'] == 'test2'
        assert chat_data[-67890][3] == 'test4'
        assert chat_data[-54321] == {}

        bot_data = pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data['test1'] == 'test2'
        assert bot_data['test3']['test4'] == 'test5'
        assert 'test0' not in bot_data

        callback_data = pickle_persistence.get_callback_data()
        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [('test1', 1000, {'button1': 'test0', 'button2': 'test1'})]
        assert callback_data[1] == {'test1': 'test2'}

        conversation1 = pickle_persistence.get_conversations('name1')
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = pickle_persistence.get_conversations('name2')
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    def test_with_good_single_file(self, pickle_persistence, good_pickle_files):
        pickle_persistence.single_file = True
        user_data = pickle_persistence.get_user_data()
        assert isinstance(user_data, defaultdict)
        assert user_data[12345]['test1'] == 'test2'
        assert user_data[67890][3] == 'test4'
        assert user_data[54321] == {}

        chat_data = pickle_persistence.get_chat_data()
        assert isinstance(chat_data, defaultdict)
        assert chat_data[-12345]['test1'] == 'test2'
        assert chat_data[-67890][3] == 'test4'
        assert chat_data[-54321] == {}

        bot_data = pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data['test1'] == 'test2'
        assert bot_data['test3']['test4'] == 'test5'
        assert 'test0' not in bot_data

        callback_data = pickle_persistence.get_callback_data()
        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [('test1', 1000, {'button1': 'test0', 'button2': 'test1'})]
        assert callback_data[1] == {'test1': 'test2'}

        conversation1 = pickle_persistence.get_conversations('name1')
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = pickle_persistence.get_conversations('name2')
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    def test_with_multi_file_wo_bot_data(self, pickle_persistence, pickle_files_wo_bot_data):
        user_data = pickle_persistence.get_user_data()
        assert isinstance(user_data, defaultdict)
        assert user_data[12345]['test1'] == 'test2'
        assert user_data[67890][3] == 'test4'
        assert user_data[54321] == {}

        chat_data = pickle_persistence.get_chat_data()
        assert isinstance(chat_data, defaultdict)
        assert chat_data[-12345]['test1'] == 'test2'
        assert chat_data[-67890][3] == 'test4'
        assert chat_data[-54321] == {}

        bot_data = pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert not bot_data.keys()

        callback_data = pickle_persistence.get_callback_data()
        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [('test1', 1000, {'button1': 'test0', 'button2': 'test1'})]
        assert callback_data[1] == {'test1': 'test2'}

        conversation1 = pickle_persistence.get_conversations('name1')
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = pickle_persistence.get_conversations('name2')
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    def test_with_multi_file_wo_callback_data(
        self, pickle_persistence, pickle_files_wo_callback_data
    ):
        user_data = pickle_persistence.get_user_data()
        assert isinstance(user_data, defaultdict)
        assert user_data[12345]['test1'] == 'test2'
        assert user_data[67890][3] == 'test4'
        assert user_data[54321] == {}

        chat_data = pickle_persistence.get_chat_data()
        assert isinstance(chat_data, defaultdict)
        assert chat_data[-12345]['test1'] == 'test2'
        assert chat_data[-67890][3] == 'test4'
        assert chat_data[-54321] == {}

        bot_data = pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data['test1'] == 'test2'
        assert bot_data['test3']['test4'] == 'test5'
        assert 'test0' not in bot_data

        callback_data = pickle_persistence.get_callback_data()
        assert callback_data is None

        conversation1 = pickle_persistence.get_conversations('name1')
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = pickle_persistence.get_conversations('name2')
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    def test_with_single_file_wo_bot_data(self, pickle_persistence, pickle_files_wo_bot_data):
        pickle_persistence.single_file = True
        user_data = pickle_persistence.get_user_data()
        assert isinstance(user_data, defaultdict)
        assert user_data[12345]['test1'] == 'test2'
        assert user_data[67890][3] == 'test4'
        assert user_data[54321] == {}

        chat_data = pickle_persistence.get_chat_data()
        assert isinstance(chat_data, defaultdict)
        assert chat_data[-12345]['test1'] == 'test2'
        assert chat_data[-67890][3] == 'test4'
        assert chat_data[-54321] == {}

        bot_data = pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert not bot_data.keys()

        callback_data = pickle_persistence.get_callback_data()
        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [('test1', 1000, {'button1': 'test0', 'button2': 'test1'})]
        assert callback_data[1] == {'test1': 'test2'}

        conversation1 = pickle_persistence.get_conversations('name1')
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = pickle_persistence.get_conversations('name2')
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    def test_with_single_file_wo_callback_data(
        self, pickle_persistence, pickle_files_wo_callback_data
    ):
        user_data = pickle_persistence.get_user_data()
        assert isinstance(user_data, defaultdict)
        assert user_data[12345]['test1'] == 'test2'
        assert user_data[67890][3] == 'test4'
        assert user_data[54321] == {}

        chat_data = pickle_persistence.get_chat_data()
        assert isinstance(chat_data, defaultdict)
        assert chat_data[-12345]['test1'] == 'test2'
        assert chat_data[-67890][3] == 'test4'
        assert chat_data[-54321] == {}

        bot_data = pickle_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data['test1'] == 'test2'
        assert bot_data['test3']['test4'] == 'test5'
        assert 'test0' not in bot_data

        callback_data = pickle_persistence.get_callback_data()
        assert callback_data is None

        conversation1 = pickle_persistence.get_conversations('name1')
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = pickle_persistence.get_conversations('name2')
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    def test_updating_multi_file(self, pickle_persistence, good_pickle_files):
        user_data = pickle_persistence.get_user_data()
        user_data[12345]['test3']['test4'] = 'test6'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(12345, user_data[12345])
        user_data[12345]['test3']['test4'] = 'test7'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(12345, user_data[12345])
        assert pickle_persistence.user_data == user_data
        with open('pickletest_user_data', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f))
        assert user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[-12345]['test3']['test4'] = 'test6'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(-12345, chat_data[-12345])
        chat_data[-12345]['test3']['test4'] = 'test7'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(-12345, chat_data[-12345])
        assert pickle_persistence.chat_data == chat_data
        with open('pickletest_chat_data', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f))
        assert chat_data_test == chat_data

        bot_data = pickle_persistence.get_bot_data()
        bot_data['test3']['test4'] = 'test6'
        assert not pickle_persistence.bot_data == bot_data
        pickle_persistence.update_bot_data(bot_data)
        bot_data['test3']['test4'] = 'test7'
        assert not pickle_persistence.bot_data == bot_data
        pickle_persistence.update_bot_data(bot_data)
        assert pickle_persistence.bot_data == bot_data
        with open('pickletest_bot_data', 'rb') as f:
            bot_data_test = pickle.load(f)
        assert bot_data_test == bot_data

        callback_data = pickle_persistence.get_callback_data()
        callback_data[1]['test3'] = 'test4'
        assert not pickle_persistence.callback_data == callback_data
        pickle_persistence.update_callback_data(callback_data)
        callback_data[1]['test3'] = 'test5'
        assert not pickle_persistence.callback_data == callback_data
        pickle_persistence.update_callback_data(callback_data)
        assert pickle_persistence.callback_data == callback_data
        with open('pickletest_callback_data', 'rb') as f:
            callback_data_test = pickle.load(f)
        assert callback_data_test == callback_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1
        pickle_persistence.update_conversation('name1', (123, 123), 5)
        assert pickle_persistence.conversations['name1'] == conversation1
        assert pickle_persistence.get_conversations('name1') == conversation1
        with open('pickletest_conversations', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f))
        assert conversations_test['name1'] == conversation1

        pickle_persistence.conversations = None
        pickle_persistence.update_conversation('name1', (123, 123), 5)
        assert pickle_persistence.conversations['name1'] == {(123, 123): 5}
        assert pickle_persistence.get_conversations('name1') == {(123, 123): 5}

    def test_updating_single_file(self, pickle_persistence, good_pickle_files):
        pickle_persistence.single_file = True

        user_data = pickle_persistence.get_user_data()
        user_data[12345]['test3']['test4'] = 'test6'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(12345, user_data[12345])
        user_data[12345]['test3']['test4'] = 'test7'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(12345, user_data[12345])
        assert pickle_persistence.user_data == user_data
        with open('pickletest', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f)['user_data'])
        assert user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[-12345]['test3']['test4'] = 'test6'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(-12345, chat_data[-12345])
        chat_data[-12345]['test3']['test4'] = 'test7'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(-12345, chat_data[-12345])
        assert pickle_persistence.chat_data == chat_data
        with open('pickletest', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f)['chat_data'])
        assert chat_data_test == chat_data

        bot_data = pickle_persistence.get_bot_data()
        bot_data['test3']['test4'] = 'test6'
        assert not pickle_persistence.bot_data == bot_data
        pickle_persistence.update_bot_data(bot_data)
        bot_data['test3']['test4'] = 'test7'
        assert not pickle_persistence.bot_data == bot_data
        pickle_persistence.update_bot_data(bot_data)
        assert pickle_persistence.bot_data == bot_data
        with open('pickletest', 'rb') as f:
            bot_data_test = pickle.load(f)['bot_data']
        assert bot_data_test == bot_data

        callback_data = pickle_persistence.get_callback_data()
        callback_data[1]['test3'] = 'test4'
        assert not pickle_persistence.callback_data == callback_data
        pickle_persistence.update_callback_data(callback_data)
        callback_data[1]['test3'] = 'test5'
        assert not pickle_persistence.callback_data == callback_data
        pickle_persistence.update_callback_data(callback_data)
        assert pickle_persistence.callback_data == callback_data
        with open('pickletest', 'rb') as f:
            callback_data_test = pickle.load(f)['callback_data']
        assert callback_data_test == callback_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1
        pickle_persistence.update_conversation('name1', (123, 123), 5)
        assert pickle_persistence.conversations['name1'] == conversation1
        assert pickle_persistence.get_conversations('name1') == conversation1
        with open('pickletest', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f)['conversations'])
        assert conversations_test['name1'] == conversation1

        pickle_persistence.conversations = None
        pickle_persistence.update_conversation('name1', (123, 123), 5)
        assert pickle_persistence.conversations['name1'] == {(123, 123): 5}
        assert pickle_persistence.get_conversations('name1') == {(123, 123): 5}

    def test_updating_single_file_no_data(self, pickle_persistence):
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
        pickle_persistence.flush()
        with pytest.raises(FileNotFoundError, match='pickletest'):
            open('pickletest', 'rb')

    def test_save_on_flush_multi_files(self, pickle_persistence, good_pickle_files):
        # Should run without error
        pickle_persistence.flush()
        pickle_persistence.on_flush = True

        user_data = pickle_persistence.get_user_data()
        user_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.user_data == user_data

        pickle_persistence.update_user_data(54321, user_data[54321])
        assert pickle_persistence.user_data == user_data

        with open('pickletest_user_data', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f))
        assert not user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.chat_data == chat_data

        pickle_persistence.update_chat_data(54321, chat_data[54321])
        assert pickle_persistence.chat_data == chat_data

        with open('pickletest_chat_data', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f))
        assert not chat_data_test == chat_data

        bot_data = pickle_persistence.get_bot_data()
        bot_data['test6'] = 'test 7'
        assert not pickle_persistence.bot_data == bot_data

        pickle_persistence.update_bot_data(bot_data)
        assert pickle_persistence.bot_data == bot_data

        with open('pickletest_bot_data', 'rb') as f:
            bot_data_test = pickle.load(f)
        assert not bot_data_test == bot_data

        callback_data = pickle_persistence.get_callback_data()
        callback_data[1]['test3'] = 'test4'
        assert not pickle_persistence.callback_data == callback_data

        pickle_persistence.update_callback_data(callback_data)
        assert pickle_persistence.callback_data == callback_data

        with open('pickletest_callback_data', 'rb') as f:
            callback_data_test = pickle.load(f)
        assert not callback_data_test == callback_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1

        pickle_persistence.update_conversation('name1', (123, 123), 5)
        assert pickle_persistence.conversations['name1'] == conversation1

        with open('pickletest_conversations', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f))
        assert not conversations_test['name1'] == conversation1

        pickle_persistence.flush()
        with open('pickletest_user_data', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f))
        assert user_data_test == user_data

        with open('pickletest_chat_data', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f))
        assert chat_data_test == chat_data

        with open('pickletest_bot_data', 'rb') as f:
            bot_data_test = pickle.load(f)
        assert bot_data_test == bot_data

        with open('pickletest_conversations', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f))
        assert conversations_test['name1'] == conversation1

    def test_save_on_flush_single_files(self, pickle_persistence, good_pickle_files):
        # Should run without error
        pickle_persistence.flush()

        pickle_persistence.on_flush = True
        pickle_persistence.single_file = True

        user_data = pickle_persistence.get_user_data()
        user_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(54321, user_data[54321])
        assert pickle_persistence.user_data == user_data
        with open('pickletest', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f)['user_data'])
        assert not user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(54321, chat_data[54321])
        assert pickle_persistence.chat_data == chat_data
        with open('pickletest', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f)['chat_data'])
        assert not chat_data_test == chat_data

        bot_data = pickle_persistence.get_bot_data()
        bot_data['test6'] = 'test 7'
        assert not pickle_persistence.bot_data == bot_data
        pickle_persistence.update_bot_data(bot_data)
        assert pickle_persistence.bot_data == bot_data
        with open('pickletest', 'rb') as f:
            bot_data_test = pickle.load(f)['bot_data']
        assert not bot_data_test == bot_data

        callback_data = pickle_persistence.get_callback_data()
        callback_data[1]['test3'] = 'test4'
        assert not pickle_persistence.callback_data == callback_data
        pickle_persistence.update_callback_data(callback_data)
        assert pickle_persistence.callback_data == callback_data
        with open('pickletest', 'rb') as f:
            callback_data_test = pickle.load(f)['callback_data']
        assert not callback_data_test == callback_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1
        pickle_persistence.update_conversation('name1', (123, 123), 5)
        assert pickle_persistence.conversations['name1'] == conversation1
        with open('pickletest', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f)['conversations'])
        assert not conversations_test['name1'] == conversation1

        pickle_persistence.flush()
        with open('pickletest', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f)['user_data'])
        assert user_data_test == user_data

        with open('pickletest', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f)['chat_data'])
        assert chat_data_test == chat_data

        with open('pickletest', 'rb') as f:
            bot_data_test = pickle.load(f)['bot_data']
        assert bot_data_test == bot_data

        with open('pickletest', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f)['conversations'])
        assert conversations_test['name1'] == conversation1

    def test_with_handler(self, bot, update, bot_data, pickle_persistence, good_pickle_files):
        u = Updater(bot=bot, persistence=pickle_persistence, use_context=True)
        dp = u.dispatcher
        bot.callback_data_cache.clear_callback_data()
        bot.callback_data_cache.clear_callback_queries()

        def first(update, context):
            if not context.user_data == {}:
                pytest.fail()
            if not context.chat_data == {}:
                pytest.fail()
            if not context.bot_data == bot_data:
                pytest.fail()
            if not context.bot.callback_data_cache.persistence_data == ([], {}):
                pytest.fail()
            context.user_data['test1'] = 'test2'
            context.chat_data['test3'] = 'test4'
            context.bot_data['test1'] = 'test0'
            context.bot.callback_data_cache._callback_queries['test1'] = 'test0'

        def second(update, context):
            if not context.user_data['test1'] == 'test2':
                pytest.fail()
            if not context.chat_data['test3'] == 'test4':
                pytest.fail()
            if not context.bot_data['test1'] == 'test0':
                pytest.fail()
            if not context.bot.callback_data_cache.persistence_data == ([], {'test1': 'test0'}):
                pytest.fail()

        h1 = MessageHandler(None, first, pass_user_data=True, pass_chat_data=True)
        h2 = MessageHandler(None, second, pass_user_data=True, pass_chat_data=True)
        dp.add_handler(h1)
        dp.process_update(update)
        pickle_persistence_2 = PicklePersistence(
            filename='pickletest',
            store_user_data=True,
            store_chat_data=True,
            store_bot_data=True,
            store_callback_data=True,
            single_file=False,
            on_flush=False,
        )
        u = Updater(bot=bot, persistence=pickle_persistence_2)
        dp = u.dispatcher
        dp.add_handler(h2)
        dp.process_update(update)

    def test_flush_on_stop(self, bot, update, pickle_persistence):
        u = Updater(bot=bot, persistence=pickle_persistence)
        dp = u.dispatcher
        u.running = True
        dp.user_data[4242424242]['my_test'] = 'Working!'
        dp.chat_data[-4242424242]['my_test2'] = 'Working2!'
        dp.bot_data['test'] = 'Working3!'
        dp.bot.callback_data_cache._callback_queries['test'] = 'Working4!'
        u._signal_handler(signal.SIGINT, None)
        pickle_persistence_2 = PicklePersistence(
            filename='pickletest',
            store_bot_data=True,
            store_user_data=True,
            store_chat_data=True,
            store_callback_data=True,
            single_file=False,
            on_flush=False,
        )
        assert pickle_persistence_2.get_user_data()[4242424242]['my_test'] == 'Working!'
        assert pickle_persistence_2.get_chat_data()[-4242424242]['my_test2'] == 'Working2!'
        assert pickle_persistence_2.get_bot_data()['test'] == 'Working3!'
        data = pickle_persistence_2.get_callback_data()[1]
        assert data['test'] == 'Working4!'

    def test_flush_on_stop_only_bot(self, bot, update, pickle_persistence_only_bot):
        u = Updater(bot=bot, persistence=pickle_persistence_only_bot)
        dp = u.dispatcher
        u.running = True
        dp.user_data[4242424242]['my_test'] = 'Working!'
        dp.chat_data[-4242424242]['my_test2'] = 'Working2!'
        dp.bot_data['my_test3'] = 'Working3!'
        dp.bot.callback_data_cache._callback_queries['test'] = 'Working4!'
        u._signal_handler(signal.SIGINT, None)
        pickle_persistence_2 = PicklePersistence(
            filename='pickletest',
            store_user_data=False,
            store_chat_data=False,
            store_bot_data=True,
            store_callback_data=False,
            single_file=False,
            on_flush=False,
        )
        assert pickle_persistence_2.get_user_data() == {}
        assert pickle_persistence_2.get_chat_data() == {}
        assert pickle_persistence_2.get_bot_data()['my_test3'] == 'Working3!'
        assert pickle_persistence_2.get_callback_data() is None

    def test_flush_on_stop_only_chat(self, bot, update, pickle_persistence_only_chat):
        u = Updater(bot=bot, persistence=pickle_persistence_only_chat)
        dp = u.dispatcher
        u.running = True
        dp.user_data[4242424242]['my_test'] = 'Working!'
        dp.chat_data[-4242424242]['my_test2'] = 'Working2!'
        dp.bot_data['my_test3'] = 'Working3!'
        dp.bot.callback_data_cache._callback_queries['test'] = 'Working4!'
        u._signal_handler(signal.SIGINT, None)
        pickle_persistence_2 = PicklePersistence(
            filename='pickletest',
            store_user_data=False,
            store_chat_data=True,
            store_bot_data=False,
            store_callback_data=False,
            single_file=False,
            on_flush=False,
        )
        assert pickle_persistence_2.get_user_data() == {}
        assert pickle_persistence_2.get_chat_data()[-4242424242]['my_test2'] == 'Working2!'
        assert pickle_persistence_2.get_bot_data() == {}
        assert pickle_persistence_2.get_callback_data() is None

    def test_flush_on_stop_only_user(self, bot, update, pickle_persistence_only_user):
        u = Updater(bot=bot, persistence=pickle_persistence_only_user)
        dp = u.dispatcher
        u.running = True
        dp.user_data[4242424242]['my_test'] = 'Working!'
        dp.chat_data[-4242424242]['my_test2'] = 'Working2!'
        dp.bot_data['my_test3'] = 'Working3!'
        dp.bot.callback_data_cache._callback_queries['test'] = 'Working4!'
        u._signal_handler(signal.SIGINT, None)
        pickle_persistence_2 = PicklePersistence(
            filename='pickletest',
            store_user_data=True,
            store_chat_data=False,
            store_bot_data=False,
            store_callback_data=False,
            single_file=False,
            on_flush=False,
        )
        assert pickle_persistence_2.get_user_data()[4242424242]['my_test'] == 'Working!'
        assert pickle_persistence_2.get_chat_data() == {}
        assert pickle_persistence_2.get_bot_data() == {}
        assert pickle_persistence_2.get_callback_data() is None

    def test_flush_on_stop_only_callback(self, bot, update, pickle_persistence_only_callback):
        u = Updater(bot=bot, persistence=pickle_persistence_only_callback)
        dp = u.dispatcher
        u.running = True
        dp.user_data[4242424242]['my_test'] = 'Working!'
        dp.chat_data[-4242424242]['my_test2'] = 'Working2!'
        dp.bot_data['my_test3'] = 'Working3!'
        dp.bot.callback_data_cache._callback_queries['test'] = 'Working4!'
        u._signal_handler(signal.SIGINT, None)
        del dp
        del u
        del pickle_persistence_only_callback
        pickle_persistence_2 = PicklePersistence(
            filename='pickletest',
            store_user_data=False,
            store_chat_data=False,
            store_bot_data=False,
            store_callback_data=True,
            single_file=False,
            on_flush=False,
        )
        assert pickle_persistence_2.get_user_data() == {}
        assert pickle_persistence_2.get_chat_data() == {}
        assert pickle_persistence_2.get_bot_data() == {}
        data = pickle_persistence_2.get_callback_data()[1]
        assert data['test'] == 'Working4!'

    def test_with_conversation_handler(self, dp, update, good_pickle_files, pickle_persistence):
        dp.persistence = pickle_persistence
        dp.use_context = True
        NEXT, NEXT2 = range(2)

        def start(update, context):
            return NEXT

        start = CommandHandler('start', start)

        def next_callback(update, context):
            return NEXT2

        next_handler = MessageHandler(None, next_callback)

        def next2(update, context):
            return ConversationHandler.END

        next2 = MessageHandler(None, next2)

        ch = ConversationHandler(
            [start], {NEXT: [next_handler], NEXT2: [next2]}, [], name='name2', persistent=True
        )
        dp.add_handler(ch)
        assert ch.conversations[ch._get_key(update)] == 1
        dp.process_update(update)
        assert ch._get_key(update) not in ch.conversations
        update.message.text = '/start'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        dp.process_update(update)
        assert ch.conversations[ch._get_key(update)] == 0
        assert ch.conversations == pickle_persistence.conversations['name2']

    def test_with_nested_conversationHandler(
        self, dp, update, good_pickle_files, pickle_persistence
    ):
        dp.persistence = pickle_persistence
        dp.use_context = True
        NEXT2, NEXT3 = range(1, 3)

        def start(update, context):
            return NEXT2

        start = CommandHandler('start', start)

        def next_callback(update, context):
            return NEXT2

        next_handler = MessageHandler(None, next_callback)

        def next2(update, context):
            return ConversationHandler.END

        next2 = MessageHandler(None, next2)

        nested_ch = ConversationHandler(
            [next_handler],
            {NEXT2: [next2]},
            [],
            name='name3',
            persistent=True,
            map_to_parent={ConversationHandler.END: ConversationHandler.END},
        )

        ch = ConversationHandler(
            [start], {NEXT2: [nested_ch], NEXT3: []}, [], name='name2', persistent=True
        )
        dp.add_handler(ch)
        assert ch.conversations[ch._get_key(update)] == 1
        assert nested_ch.conversations[nested_ch._get_key(update)] == 1
        dp.process_update(update)
        assert ch._get_key(update) not in ch.conversations
        assert nested_ch._get_key(update) not in nested_ch.conversations
        update.message.text = '/start'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        dp.process_update(update)
        assert ch.conversations[ch._get_key(update)] == 1
        assert ch.conversations == pickle_persistence.conversations['name2']
        assert nested_ch._get_key(update) not in nested_ch.conversations
        dp.process_update(update)
        assert ch.conversations[ch._get_key(update)] == 1
        assert ch.conversations == pickle_persistence.conversations['name2']
        assert nested_ch.conversations[nested_ch._get_key(update)] == 1
        assert nested_ch.conversations == pickle_persistence.conversations['name3']

    def test_with_job(self, job_queue, cdp, pickle_persistence):
        cdp.bot.arbitrary_callback_data = True

        def job_callback(context):
            context.bot_data['test1'] = '456'
            context.dispatcher.chat_data[123]['test2'] = '789'
            context.dispatcher.user_data[789]['test3'] = '123'
            context.bot.callback_data_cache._callback_queries['test'] = 'Working4!'

        cdp.persistence = pickle_persistence
        job_queue.set_dispatcher(cdp)
        job_queue.start()
        job_queue.run_once(job_callback, 0.01)
        sleep(0.5)
        bot_data = pickle_persistence.get_bot_data()
        assert bot_data == {'test1': '456'}
        chat_data = pickle_persistence.get_chat_data()
        assert chat_data[123] == {'test2': '789'}
        user_data = pickle_persistence.get_user_data()
        assert user_data[789] == {'test3': '123'}
        data = pickle_persistence.get_callback_data()[1]
        assert data['test'] == 'Working4!'

    @pytest.mark.parametrize('singlefile', [True, False])
    @pytest.mark.parametrize('ud', [int, float, complex])
    @pytest.mark.parametrize('cd', [int, float, complex])
    @pytest.mark.parametrize('bd', [int, float, complex])
    def test_with_context_types(self, ud, cd, bd, singlefile):
        cc = ContextTypes(user_data=ud, chat_data=cd, bot_data=bd)
        persistence = PicklePersistence('pickletest', single_file=singlefile, context_types=cc)

        assert isinstance(persistence.get_user_data()[1], ud)
        assert persistence.get_user_data()[1] == 0
        assert isinstance(persistence.get_chat_data()[1], cd)
        assert persistence.get_chat_data()[1] == 0
        assert isinstance(persistence.get_bot_data(), bd)
        assert persistence.get_bot_data() == 0

        persistence.user_data = None
        persistence.chat_data = None
        persistence.update_user_data(1, ud(1))
        persistence.update_chat_data(1, cd(1))
        persistence.update_bot_data(bd(1))
        assert persistence.get_user_data()[1] == 1
        assert persistence.get_chat_data()[1] == 1
        assert persistence.get_bot_data() == 1

        persistence.flush()
        persistence = PicklePersistence('pickletest', single_file=singlefile, context_types=cc)
        assert isinstance(persistence.get_user_data()[1], ud)
        assert persistence.get_user_data()[1] == 1
        assert isinstance(persistence.get_chat_data()[1], cd)
        assert persistence.get_chat_data()[1] == 1
        assert isinstance(persistence.get_bot_data(), bd)
        assert persistence.get_bot_data() == 1


@pytest.fixture(scope='function')
def user_data_json(user_data):
    return json.dumps(user_data)


@pytest.fixture(scope='function')
def chat_data_json(chat_data):
    return json.dumps(chat_data)


@pytest.fixture(scope='function')
def bot_data_json(bot_data):
    return json.dumps(bot_data)


@pytest.fixture(scope='function')
def callback_data_json(callback_data):
    return json.dumps(callback_data)


@pytest.fixture(scope='function')
def conversations_json(conversations):
    return """{"name1": {"[123, 123]": 3, "[456, 654]": 4}, "name2":
              {"[123, 321]": 1, "[890, 890]": 2}, "name3":
              {"[123, 321]": 1, "[890, 890]": 2}}"""


class TestDictPersistence:
    def test_slot_behaviour(self, mro_slots, recwarn):
        inst = DictPersistence()
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        # assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.store_user_data = 'should give warning', {}
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_no_json_given(self):
        dict_persistence = DictPersistence()
        assert dict_persistence.get_user_data() == defaultdict(dict)
        assert dict_persistence.get_chat_data() == defaultdict(dict)
        assert dict_persistence.get_bot_data() == {}
        assert dict_persistence.get_callback_data() is None
        assert dict_persistence.get_conversations('noname') == {}

    def test_bad_json_string_given(self):
        bad_user_data = 'thisisnojson99900()))('
        bad_chat_data = 'thisisnojson99900()))('
        bad_bot_data = 'thisisnojson99900()))('
        bad_callback_data = 'thisisnojson99900()))('
        bad_conversations = 'thisisnojson99900()))('
        with pytest.raises(TypeError, match='user_data'):
            DictPersistence(user_data_json=bad_user_data)
        with pytest.raises(TypeError, match='chat_data'):
            DictPersistence(chat_data_json=bad_chat_data)
        with pytest.raises(TypeError, match='bot_data'):
            DictPersistence(bot_data_json=bad_bot_data)
        with pytest.raises(TypeError, match='callback_data'):
            DictPersistence(callback_data_json=bad_callback_data)
        with pytest.raises(TypeError, match='conversations'):
            DictPersistence(conversations_json=bad_conversations)

    def test_invalid_json_string_given(self, pickle_persistence, bad_pickle_files):
        bad_user_data = '["this", "is", "json"]'
        bad_chat_data = '["this", "is", "json"]'
        bad_bot_data = '["this", "is", "json"]'
        bad_conversations = '["this", "is", "json"]'
        bad_callback_data_1 = '[[["str", 3.14, {"di": "ct"}]], "is"]'
        bad_callback_data_2 = '[[["str", "non-float", {"di": "ct"}]], {"di": "ct"}]'
        bad_callback_data_3 = '[[[{"not": "a str"}, 3.14, {"di": "ct"}]], {"di": "ct"}]'
        bad_callback_data_4 = '[[["wrong", "length"]], {"di": "ct"}]'
        bad_callback_data_5 = '["this", "is", "json"]'
        with pytest.raises(TypeError, match='user_data'):
            DictPersistence(user_data_json=bad_user_data)
        with pytest.raises(TypeError, match='chat_data'):
            DictPersistence(chat_data_json=bad_chat_data)
        with pytest.raises(TypeError, match='bot_data'):
            DictPersistence(bot_data_json=bad_bot_data)
        for bad_callback_data in [
            bad_callback_data_1,
            bad_callback_data_2,
            bad_callback_data_3,
            bad_callback_data_4,
            bad_callback_data_5,
        ]:
            with pytest.raises(TypeError, match='callback_data'):
                DictPersistence(callback_data_json=bad_callback_data)
        with pytest.raises(TypeError, match='conversations'):
            DictPersistence(conversations_json=bad_conversations)

    def test_good_json_input(
        self, user_data_json, chat_data_json, bot_data_json, conversations_json, callback_data_json
    ):
        dict_persistence = DictPersistence(
            user_data_json=user_data_json,
            chat_data_json=chat_data_json,
            bot_data_json=bot_data_json,
            conversations_json=conversations_json,
            callback_data_json=callback_data_json,
        )
        user_data = dict_persistence.get_user_data()
        assert isinstance(user_data, defaultdict)
        assert user_data[12345]['test1'] == 'test2'
        assert user_data[67890][3] == 'test4'
        assert user_data[54321] == {}

        chat_data = dict_persistence.get_chat_data()
        assert isinstance(chat_data, defaultdict)
        assert chat_data[-12345]['test1'] == 'test2'
        assert chat_data[-67890][3] == 'test4'
        assert chat_data[-54321] == {}

        bot_data = dict_persistence.get_bot_data()
        assert isinstance(bot_data, dict)
        assert bot_data['test1'] == 'test2'
        assert bot_data['test3']['test4'] == 'test5'
        assert 'test6' not in bot_data

        callback_data = dict_persistence.get_callback_data()

        assert isinstance(callback_data, tuple)
        assert callback_data[0] == [('test1', 1000, {'button1': 'test0', 'button2': 'test1'})]
        assert callback_data[1] == {'test1': 'test2'}

        conversation1 = dict_persistence.get_conversations('name1')
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 3
        assert conversation1[(456, 654)] == 4
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = dict_persistence.get_conversations('name2')
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 1
        assert conversation2[(890, 890)] == 2
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    def test_good_json_input_callback_data_none(self):
        dict_persistence = DictPersistence(callback_data_json='null')
        assert dict_persistence.callback_data is None
        assert dict_persistence.callback_data_json == 'null'

    def test_dict_outputs(
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

    def test_json_outputs(
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

    def test_updating(
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
            store_callback_data=True,
        )

        user_data = dict_persistence.get_user_data()
        user_data[12345]['test3']['test4'] = 'test6'
        assert not dict_persistence.user_data == user_data
        assert not dict_persistence.user_data_json == json.dumps(user_data)
        dict_persistence.update_user_data(12345, user_data[12345])
        user_data[12345]['test3']['test4'] = 'test7'
        assert not dict_persistence.user_data == user_data
        assert not dict_persistence.user_data_json == json.dumps(user_data)
        dict_persistence.update_user_data(12345, user_data[12345])
        assert dict_persistence.user_data == user_data
        assert dict_persistence.user_data_json == json.dumps(user_data)

        chat_data = dict_persistence.get_chat_data()
        chat_data[-12345]['test3']['test4'] = 'test6'
        assert not dict_persistence.chat_data == chat_data
        assert not dict_persistence.chat_data_json == json.dumps(chat_data)
        dict_persistence.update_chat_data(-12345, chat_data[-12345])
        chat_data[-12345]['test3']['test4'] = 'test7'
        assert not dict_persistence.chat_data == chat_data
        assert not dict_persistence.chat_data_json == json.dumps(chat_data)
        dict_persistence.update_chat_data(-12345, chat_data[-12345])
        assert dict_persistence.chat_data == chat_data
        assert dict_persistence.chat_data_json == json.dumps(chat_data)

        bot_data = dict_persistence.get_bot_data()
        bot_data['test3']['test4'] = 'test6'
        assert not dict_persistence.bot_data == bot_data
        assert not dict_persistence.bot_data_json == json.dumps(bot_data)
        dict_persistence.update_bot_data(bot_data)
        bot_data['test3']['test4'] = 'test7'
        assert not dict_persistence.bot_data == bot_data
        assert not dict_persistence.bot_data_json == json.dumps(bot_data)
        dict_persistence.update_bot_data(bot_data)
        assert dict_persistence.bot_data == bot_data
        assert dict_persistence.bot_data_json == json.dumps(bot_data)

        callback_data = dict_persistence.get_callback_data()
        callback_data[1]['test3'] = 'test4'
        callback_data[0][0][2]['button2'] = 'test41'
        assert not dict_persistence.callback_data == callback_data
        assert not dict_persistence.callback_data_json == json.dumps(callback_data)
        dict_persistence.update_callback_data(callback_data)
        callback_data[1]['test3'] = 'test5'
        callback_data[0][0][2]['button2'] = 'test42'
        assert not dict_persistence.callback_data == callback_data
        assert not dict_persistence.callback_data_json == json.dumps(callback_data)
        dict_persistence.update_callback_data(callback_data)
        assert dict_persistence.callback_data == callback_data
        assert dict_persistence.callback_data_json == json.dumps(callback_data)

        conversation1 = dict_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not dict_persistence.conversations['name1'] == conversation1
        dict_persistence.update_conversation('name1', (123, 123), 5)
        assert dict_persistence.conversations['name1'] == conversation1
        conversations['name1'][(123, 123)] = 5
        assert dict_persistence.conversations_json == encode_conversations_to_json(conversations)
        assert dict_persistence.get_conversations('name1') == conversation1

        dict_persistence._conversations = None
        dict_persistence.update_conversation('name1', (123, 123), 5)
        assert dict_persistence.conversations['name1'] == {(123, 123): 5}
        assert dict_persistence.get_conversations('name1') == {(123, 123): 5}
        assert dict_persistence.conversations_json == encode_conversations_to_json(
            {"name1": {(123, 123): 5}}
        )

    def test_with_handler(self, bot, update):
        dict_persistence = DictPersistence(store_callback_data=True)
        u = Updater(bot=bot, persistence=dict_persistence, use_context=True)
        dp = u.dispatcher

        def first(update, context):
            if not context.user_data == {}:
                pytest.fail()
            if not context.chat_data == {}:
                pytest.fail()
            if not context.bot_data == {}:
                pytest.fail()
            if not context.bot.callback_data_cache.persistence_data == ([], {}):
                pytest.fail()
            context.user_data['test1'] = 'test2'
            context.chat_data[3] = 'test4'
            context.bot_data['test1'] = 'test0'
            context.bot.callback_data_cache._callback_queries['test1'] = 'test0'

        def second(update, context):
            if not context.user_data['test1'] == 'test2':
                pytest.fail()
            if not context.chat_data[3] == 'test4':
                pytest.fail()
            if not context.bot_data['test1'] == 'test0':
                pytest.fail()
            if not context.bot.callback_data_cache.persistence_data == ([], {'test1': 'test0'}):
                pytest.fail()

        h1 = MessageHandler(Filters.all, first)
        h2 = MessageHandler(Filters.all, second)
        dp.add_handler(h1)
        dp.process_update(update)
        user_data = dict_persistence.user_data_json
        chat_data = dict_persistence.chat_data_json
        bot_data = dict_persistence.bot_data_json
        callback_data = dict_persistence.callback_data_json
        dict_persistence_2 = DictPersistence(
            user_data_json=user_data,
            chat_data_json=chat_data,
            bot_data_json=bot_data,
            callback_data_json=callback_data,
            store_callback_data=True,
        )

        u = Updater(bot=bot, persistence=dict_persistence_2)
        dp = u.dispatcher
        dp.add_handler(h2)
        dp.process_update(update)

    def test_with_conversationHandler(self, dp, update, conversations_json):
        dict_persistence = DictPersistence(conversations_json=conversations_json)
        dp.persistence = dict_persistence
        dp.use_context = True
        NEXT, NEXT2 = range(2)

        def start(update, context):
            return NEXT

        start = CommandHandler('start', start)

        def next_callback(update, context):
            return NEXT2

        next_handler = MessageHandler(None, next_callback)

        def next2(update, context):
            return ConversationHandler.END

        next2 = MessageHandler(None, next2)

        ch = ConversationHandler(
            [start], {NEXT: [next_handler], NEXT2: [next2]}, [], name='name2', persistent=True
        )
        dp.add_handler(ch)
        assert ch.conversations[ch._get_key(update)] == 1
        dp.process_update(update)
        assert ch._get_key(update) not in ch.conversations
        update.message.text = '/start'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        dp.process_update(update)
        assert ch.conversations[ch._get_key(update)] == 0
        assert ch.conversations == dict_persistence.conversations['name2']

    def test_with_nested_conversationHandler(self, dp, update, conversations_json):
        dict_persistence = DictPersistence(conversations_json=conversations_json)
        dp.persistence = dict_persistence
        dp.use_context = True
        NEXT2, NEXT3 = range(1, 3)

        def start(update, context):
            return NEXT2

        start = CommandHandler('start', start)

        def next_callback(update, context):
            return NEXT2

        next_handler = MessageHandler(None, next_callback)

        def next2(update, context):
            return ConversationHandler.END

        next2 = MessageHandler(None, next2)

        nested_ch = ConversationHandler(
            [next_handler],
            {NEXT2: [next2]},
            [],
            name='name3',
            persistent=True,
            map_to_parent={ConversationHandler.END: ConversationHandler.END},
        )

        ch = ConversationHandler(
            [start], {NEXT2: [nested_ch], NEXT3: []}, [], name='name2', persistent=True
        )
        dp.add_handler(ch)
        assert ch.conversations[ch._get_key(update)] == 1
        assert nested_ch.conversations[nested_ch._get_key(update)] == 1
        dp.process_update(update)
        assert ch._get_key(update) not in ch.conversations
        assert nested_ch._get_key(update) not in nested_ch.conversations
        update.message.text = '/start'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        dp.process_update(update)
        assert ch.conversations[ch._get_key(update)] == 1
        assert ch.conversations == dict_persistence.conversations['name2']
        assert nested_ch._get_key(update) not in nested_ch.conversations
        dp.process_update(update)
        assert ch.conversations[ch._get_key(update)] == 1
        assert ch.conversations == dict_persistence.conversations['name2']
        assert nested_ch.conversations[nested_ch._get_key(update)] == 1
        assert nested_ch.conversations == dict_persistence.conversations['name3']

    def test_with_job(self, job_queue, cdp):
        cdp.bot.arbitrary_callback_data = True

        def job_callback(context):
            context.bot_data['test1'] = '456'
            context.dispatcher.chat_data[123]['test2'] = '789'
            context.dispatcher.user_data[789]['test3'] = '123'
            context.bot.callback_data_cache._callback_queries['test'] = 'Working4!'

        dict_persistence = DictPersistence(store_callback_data=True)
        cdp.persistence = dict_persistence
        job_queue.set_dispatcher(cdp)
        job_queue.start()
        job_queue.run_once(job_callback, 0.01)
        sleep(0.8)
        bot_data = dict_persistence.get_bot_data()
        assert bot_data == {'test1': '456'}
        chat_data = dict_persistence.get_chat_data()
        assert chat_data[123] == {'test2': '789'}
        user_data = dict_persistence.get_user_data()
        assert user_data[789] == {'test3': '123'}
        data = dict_persistence.get_callback_data()[1]
        assert data['test'] == 'Working4!'
