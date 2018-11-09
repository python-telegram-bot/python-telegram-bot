#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
from telegram.utils.helpers import enocde_conversations_to_json

try:
    import ujson as json
except ImportError:
    import json
import logging
import os
import pickle
from collections import defaultdict

import pytest

from telegram import Update, Message, User, Chat
from telegram.ext import BasePersistence, Updater, ConversationHandler, MessageHandler, Filters, \
    PicklePersistence, CommandHandler, DictPersistence, TypeHandler


@pytest.fixture(scope="function")
def base_persistence():
    return BasePersistence(store_chat_data=True, store_user_data=True)


@pytest.fixture(scope="function")
def chat_data():
    return defaultdict(dict, {-12345: {'test1': 'test2'}, -67890: {3: 'test4'}})


@pytest.fixture(scope="function")
def user_data():
    return defaultdict(dict, {12345: {'test1': 'test2'}, 67890: {3: 'test4'}})


@pytest.fixture(scope='function')
def conversations():
    return {'name1': {(123, 123): 3, (456, 654): 4},
            'name2': {(123, 321): 1, (890, 890): 2}}


@pytest.fixture(scope="function")
def updater(bot, base_persistence):
    base_persistence.store_chat_data = False
    base_persistence.store_user_data = False
    u = Updater(bot=bot, persistence=base_persistence)
    base_persistence.store_chat_data = True
    base_persistence.store_user_data = True
    return u


class TestBasePersistence(object):

    def test_creation(self, base_persistence):
        assert base_persistence.store_chat_data
        assert base_persistence.store_user_data
        with pytest.raises(NotImplementedError):
            base_persistence.get_chat_data()
        with pytest.raises(NotImplementedError):
            base_persistence.get_user_data()
        with pytest.raises(NotImplementedError):
            base_persistence.get_conversations("test")
        with pytest.raises(NotImplementedError):
            base_persistence.update_chat_data(None, None)
        with pytest.raises(NotImplementedError):
            base_persistence.update_user_data(None, None)
        with pytest.raises(NotImplementedError):
            base_persistence.update_conversation(None, None, None)

    def test_implementation(self, updater, base_persistence):
        dp = updater.dispatcher
        assert dp.persistence == base_persistence

    def test_conversationhandler_addition(self, dp, base_persistence):
        with pytest.raises(ValueError, match="when handler is unnamed"):
            ConversationHandler([], [], [], persistent=True)
        with pytest.raises(ValueError, match="if dispatcher has no persistence"):
            dp.add_handler(ConversationHandler([], {}, [], persistent=True, name="My Handler"))
        dp.persistence = base_persistence
        with pytest.raises(NotImplementedError):
            dp.add_handler(ConversationHandler([], {}, [], persistent=True, name="My Handler"))

    def test_dispatcher_integration_init(self, bot, base_persistence, chat_data, user_data):
        def get_user_data():
            return "test"

        def get_chat_data():
            return "test"

        base_persistence.get_user_data = get_user_data
        base_persistence.get_chat_data = get_chat_data
        with pytest.raises(ValueError, match="user_data must be of type defaultdict"):
            u = Updater(bot=bot, persistence=base_persistence)

        def get_user_data():
            return user_data

        base_persistence.get_user_data = get_user_data
        with pytest.raises(ValueError, match="chat_data must be of type defaultdict"):
            u = Updater(bot=bot, persistence=base_persistence)

        def get_chat_data():
            return chat_data

        base_persistence.get_chat_data = get_chat_data
        u = Updater(bot=bot, persistence=base_persistence)
        assert u.dispatcher.chat_data == chat_data
        assert u.dispatcher.user_data == user_data
        u.dispatcher.chat_data[442233]['test5'] = 'test6'
        assert u.dispatcher.chat_data[442233]['test5'] == 'test6'

    def test_dispatcher_integration_handlers(self, caplog, bot, base_persistence,
                                             chat_data, user_data):
        def get_user_data():
            return user_data

        def get_chat_data():
            return chat_data

        base_persistence.get_user_data = get_user_data
        base_persistence.get_chat_data = get_chat_data
        # base_persistence.update_chat_data = lambda x: x
        # base_persistence.update_user_data = lambda x: x
        updater = Updater(bot=bot, persistence=base_persistence)
        dp = updater.dispatcher

        def callback_known_user(bot, update, user_data, chat_data):
            if not user_data['test1'] == 'test2':
                pytest.fail('user_data corrupt')

        def callback_known_chat(bot, update, user_data, chat_data):
            if not chat_data['test3'] == 'test4':
                pytest.fail('chat_data corrupt')

        def callback_unknown_user_or_chat(bot, update, user_data, chat_data):
            if not user_data == {}:
                pytest.fail('user_data corrupt')
            if not chat_data == {}:
                pytest.fail('chat_data corrupt')
            user_data[1] = 'test7'
            chat_data[2] = 'test8'

        known_user = MessageHandler(Filters.user(user_id=12345), callback_known_user,
                                    pass_chat_data=True, pass_user_data=True)
        known_chat = MessageHandler(Filters.chat(chat_id=-67890), callback_known_chat,
                                    pass_chat_data=True, pass_user_data=True)
        unknown = MessageHandler(Filters.all, callback_unknown_user_or_chat, pass_chat_data=True,
                                 pass_user_data=True)
        dp.add_handler(known_user)
        dp.add_handler(known_chat)
        dp.add_handler(unknown)
        user1 = User(id=12345, first_name='test user', is_bot=False)
        user2 = User(id=54321, first_name='test user', is_bot=False)
        chat1 = Chat(id=-67890, type='group')
        chat2 = Chat(id=-987654, type='group')
        m = Message(1, user1, None, chat2)
        u = Update(0, m)
        with caplog.at_level(logging.ERROR):
            dp.process_update(u)
        rec = caplog.records[-1]
        assert rec.msg == 'Saving user data raised an error'
        assert rec.levelname == 'ERROR'
        rec = caplog.records[-2]
        assert rec.msg == 'Saving chat data raised an error'
        assert rec.levelname == 'ERROR'
        m.from_user = user2
        m.chat = chat1
        u = Update(1, m)
        dp.process_update(u)
        m.chat = chat2
        u = Update(2, m)

        def save_chat_data(data):
            if -987654 not in data:
                pytest.fail()

        def save_user_data(data):
            if 54321 not in data:
                pytest.fail()

        base_persistence.update_chat_data = save_chat_data
        base_persistence.update_user_data = save_user_data
        dp.process_update(u)

        assert dp.user_data[54321][1] == 'test7'
        assert dp.chat_data[-987654][2] == 'test8'

    def test_persistence_dispatcher_arbitrary_update_types(self, dp, base_persistence, caplog):
        # Updates used with TypeHandler doesn't necessarily have the proper attributes for
        # persistence, makes sure it works anyways

        dp.persistence = base_persistence

        class MyUpdate(object):
            pass

        dp.add_handler(TypeHandler(MyUpdate, lambda *_: None))

        with caplog.at_level(logging.ERROR):
            dp.process_update(MyUpdate())
        assert 'An uncaught error was raised while processing the update' not in caplog.text


@pytest.fixture(scope='function')
def pickle_persistence():
    return PicklePersistence(filename='pickletest',
                             store_user_data=True,
                             store_chat_data=True,
                             singe_file=False,
                             on_flush=False)


@pytest.fixture(scope='function')
def bad_pickle_files():
    for name in ['pickletest_user_data', 'pickletest_chat_data', 'pickletest_conversations',
                 'pickletest']:
        with open(name, 'w') as f:
            f.write('(())')
    yield True
    for name in ['pickletest_user_data', 'pickletest_chat_data', 'pickletest_conversations',
                 'pickletest']:
        os.remove(name)


@pytest.fixture(scope='function')
def good_pickle_files(user_data, chat_data, conversations):
    all = {'user_data': user_data, 'chat_data': chat_data, 'conversations': conversations}
    with open('pickletest_user_data', 'wb') as f:
        pickle.dump(user_data, f)
    with open('pickletest_chat_data', 'wb') as f:
        pickle.dump(chat_data, f)
    with open('pickletest_conversations', 'wb') as f:
        pickle.dump(conversations, f)
    with open('pickletest', 'wb') as f:
        pickle.dump(all, f)
    yield True
    for name in ['pickletest_user_data', 'pickletest_chat_data', 'pickletest_conversations',
                 'pickletest']:
        os.remove(name)


@pytest.fixture(scope='function')
def update(bot):
    user = User(id=321, first_name='test_user', is_bot=False)
    chat = Chat(id=123, type='group')
    message = Message(1, user, None, chat, text="Hi there", bot=bot)
    return Update(0, message=message)


class TestPickelPersistence(object):
    def test_no_files_present_multi_file(self, pickle_persistence):
        assert pickle_persistence.get_user_data() == defaultdict(dict)
        assert pickle_persistence.get_user_data() == defaultdict(dict)
        assert pickle_persistence.get_chat_data() == defaultdict(dict)
        assert pickle_persistence.get_chat_data() == defaultdict(dict)
        assert pickle_persistence.get_conversations('noname') == {}
        assert pickle_persistence.get_conversations('noname') == {}

    def test_no_files_present_single_file(self, pickle_persistence):
        pickle_persistence.single_file = True
        assert pickle_persistence.get_user_data() == defaultdict(dict)
        assert pickle_persistence.get_chat_data() == defaultdict(dict)
        assert pickle_persistence.get_conversations('noname') == {}

    def test_with_bad_multi_file(self, pickle_persistence, bad_pickle_files):
        with pytest.raises(TypeError, match='pickletest_user_data'):
            pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match='pickletest_chat_data'):
            pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match='pickletest_conversations'):
            pickle_persistence.get_conversations('name')

    def test_with_bad_single_file(self, pickle_persistence, bad_pickle_files):
        pickle_persistence.single_file = True
        with pytest.raises(TypeError, match='pickletest'):
            pickle_persistence.get_user_data()
        with pytest.raises(TypeError, match='pickletest'):
            pickle_persistence.get_chat_data()
        with pytest.raises(TypeError, match='pickletest'):
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
        user_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(54321, user_data[54321])
        assert pickle_persistence.user_data == user_data
        with open('pickletest_user_data', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f))
        assert user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(54321, chat_data[54321])
        assert pickle_persistence.chat_data == chat_data
        with open('pickletest_chat_data', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f))
        assert chat_data_test == chat_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1
        pickle_persistence.update_conversation('name1', (123, 123), 5)
        assert pickle_persistence.conversations['name1'] == conversation1
        with open('pickletest_conversations', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f))
        assert conversations_test['name1'] == conversation1

    def test_updating_single_file(self, pickle_persistence, good_pickle_files):
        pickle_persistence.single_file = True

        user_data = pickle_persistence.get_user_data()
        user_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(54321, user_data[54321])
        assert pickle_persistence.user_data == user_data
        with open('pickletest', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f)['user_data'])
        assert user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(54321, chat_data[54321])
        assert pickle_persistence.chat_data == chat_data
        with open('pickletest', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f)['chat_data'])
        assert chat_data_test == chat_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1
        pickle_persistence.update_conversation('name1', (123, 123), 5)
        assert pickle_persistence.conversations['name1'] == conversation1
        with open('pickletest', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f)['conversations'])
        assert conversations_test['name1'] == conversation1

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
            conversations_test = defaultdict(dict, pickle.load(f)['conversations'])
        assert conversations_test['name1'] == conversation1

    def test_with_handler(self, bot, update, pickle_persistence, good_pickle_files):
        u = Updater(bot=bot, persistence=pickle_persistence)
        dp = u.dispatcher

        def first(bot, update, user_data, chat_data):
            if not user_data == {}:
                pytest.fail()
            if not chat_data == {}:
                pytest.fail()
            user_data['test1'] = 'test2'
            chat_data['test3'] = 'test4'

        def second(bot, update, user_data, chat_data):
            if not user_data['test1'] == 'test2':
                pytest.fail()
            if not chat_data['test3'] == 'test4':
                pytest.fail()

        h1 = MessageHandler(None, first, pass_user_data=True, pass_chat_data=True)
        h2 = MessageHandler(None, second, pass_user_data=True, pass_chat_data=True)
        dp.add_handler(h1)
        dp.process_update(update)
        del (dp)
        del (u)
        del (pickle_persistence)
        pickle_persistence_2 = PicklePersistence(filename='pickletest',
                                                 store_user_data=True,
                                                 store_chat_data=True,
                                                 singe_file=False,
                                                 on_flush=False)
        u = Updater(bot=bot, persistence=pickle_persistence_2)
        dp = u.dispatcher
        dp.add_handler(h2)
        dp.process_update(update)

    def test_with_conversationHandler(self, dp, update, good_pickle_files, pickle_persistence):
        dp.persistence = pickle_persistence
        NEXT, NEXT2 = range(2)

        def start(bot, update):
            return NEXT

        start = CommandHandler('start', start)

        def next(bot, update):
            return NEXT2

        next = MessageHandler(None, next)

        def next2(bot, update):
            return ConversationHandler.END

        next2 = MessageHandler(None, next2)

        ch = ConversationHandler([start], {NEXT: [next], NEXT2: [next2]}, [], name='name2',
                                 persistent=True)
        dp.add_handler(ch)
        assert ch.conversations[ch._get_key(update)] == 1
        dp.process_update(update)
        assert ch._get_key(update) not in ch.conversations
        update.message.text = '/start'
        dp.process_update(update)
        assert ch.conversations[ch._get_key(update)] == 0
        assert ch.conversations == pickle_persistence.conversations['name2']

    @classmethod
    def teardown_class(cls):
        try:
            for name in ['pickletest_user_data', 'pickletest_chat_data',
                         'pickletest_conversations',
                         'pickletest']:
                os.remove(name)
        except Exception:
            pass


@pytest.fixture(scope='function')
def user_data_json(user_data):
    return json.dumps(user_data)


@pytest.fixture(scope='function')
def chat_data_json(chat_data):
    return json.dumps(chat_data)


@pytest.fixture(scope='function')
def conversations_json(conversations):
    return """{"name1": {"[123, 123]": 3, "[456, 654]": 4}, "name2":
              {"[123, 321]": 1, "[890, 890]": 2}}"""


class TestDictPersistence(object):
    def test_no_json_given(self):
        dict_persistence = DictPersistence()
        assert dict_persistence.get_user_data() == defaultdict(dict)
        assert dict_persistence.get_chat_data() == defaultdict(dict)
        assert dict_persistence.get_conversations('noname') == {}

    def test_bad_json_string_given(self):
        bad_user_data = 'thisisnojson99900()))('
        bad_chat_data = 'thisisnojson99900()))('
        bad_conversations = 'thisisnojson99900()))('
        with pytest.raises(TypeError, match='user_data'):
            DictPersistence(user_data_json=bad_user_data)
        with pytest.raises(TypeError, match='chat_data'):
            DictPersistence(chat_data_json=bad_chat_data)
        with pytest.raises(TypeError, match='conversations'):
            DictPersistence(conversations_json=bad_conversations)

    def test_invalid_json_string_given(self, pickle_persistence, bad_pickle_files):
        bad_user_data = '["this", "is", "json"]'
        bad_chat_data = '["this", "is", "json"]'
        bad_conversations = '["this", "is", "json"]'
        with pytest.raises(TypeError, match='user_data'):
            DictPersistence(user_data_json=bad_user_data)
        with pytest.raises(TypeError, match='chat_data'):
            DictPersistence(chat_data_json=bad_chat_data)
        with pytest.raises(TypeError, match='conversations'):
            DictPersistence(conversations_json=bad_conversations)

    def test_good_json_input(self, user_data_json, chat_data_json, conversations_json):
        dict_persistence = DictPersistence(user_data_json=user_data_json,
                                           chat_data_json=chat_data_json,
                                           conversations_json=conversations_json)
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

    def test_dict_outputs(self, user_data, user_data_json, chat_data, chat_data_json,
                          conversations, conversations_json):
        dict_persistence = DictPersistence(user_data_json=user_data_json,
                                           chat_data_json=chat_data_json,
                                           conversations_json=conversations_json)
        assert dict_persistence.user_data == user_data
        assert dict_persistence.chat_data == chat_data
        assert dict_persistence.conversations == conversations

    def test_json_outputs(self, user_data_json, chat_data_json, conversations_json):
        dict_persistence = DictPersistence(user_data_json=user_data_json,
                                           chat_data_json=chat_data_json,
                                           conversations_json=conversations_json)
        assert dict_persistence.user_data_json == user_data_json
        assert dict_persistence.chat_data_json == chat_data_json
        assert dict_persistence.conversations_json == conversations_json

    def test_json_changes(self, user_data, user_data_json, chat_data, chat_data_json,
                          conversations, conversations_json):
        dict_persistence = DictPersistence(user_data_json=user_data_json,
                                           chat_data_json=chat_data_json,
                                           conversations_json=conversations_json)
        user_data_two = user_data.copy()
        user_data_two.update({4: {5: 6}})
        dict_persistence.update_user_data(4, {5: 6})
        assert dict_persistence.user_data == user_data_two
        assert dict_persistence.user_data_json != user_data_json
        assert dict_persistence.user_data_json == json.dumps(user_data_two)

        chat_data_two = chat_data.copy()
        chat_data_two.update({7: {8: 9}})
        dict_persistence.update_chat_data(7, {8: 9})
        assert dict_persistence.chat_data == chat_data_two
        assert dict_persistence.chat_data_json != chat_data_json
        assert dict_persistence.chat_data_json == json.dumps(chat_data_two)

        conversations_two = conversations.copy()
        conversations_two.update({'name3': {(1, 2): 3}})
        dict_persistence.update_conversation('name3', (1, 2), 3)
        assert dict_persistence.conversations == conversations_two
        assert dict_persistence.conversations_json != conversations_json
        assert dict_persistence.conversations_json == enocde_conversations_to_json(
            conversations_two)

    def test_with_handler(self, bot, update):
        dict_persistence = DictPersistence()
        u = Updater(bot=bot, persistence=dict_persistence)
        dp = u.dispatcher

        def first(bot, update, user_data, chat_data):
            if not user_data == {}:
                pytest.fail()
            if not chat_data == {}:
                pytest.fail()
            user_data['test1'] = 'test2'
            chat_data[3] = 'test4'

        def second(bot, update, user_data, chat_data):
            if not user_data['test1'] == 'test2':
                pytest.fail()
            if not chat_data[3] == 'test4':
                pytest.fail()

        h1 = MessageHandler(None, first, pass_user_data=True, pass_chat_data=True)
        h2 = MessageHandler(None, second, pass_user_data=True, pass_chat_data=True)
        dp.add_handler(h1)
        dp.process_update(update)
        del (dp)
        del (u)
        user_data = dict_persistence.user_data_json
        chat_data = dict_persistence.chat_data_json
        del (dict_persistence)
        dict_persistence_2 = DictPersistence(user_data_json=user_data,
                                             chat_data_json=chat_data)

        u = Updater(bot=bot, persistence=dict_persistence_2)
        dp = u.dispatcher
        dp.add_handler(h2)
        dp.process_update(update)

    def test_with_conversationHandler(self, dp, update, conversations_json):
        dict_persistence = DictPersistence(conversations_json=conversations_json)
        dp.persistence = dict_persistence
        NEXT, NEXT2 = range(2)

        def start(bot, update):
            return NEXT

        start = CommandHandler('start', start)

        def next(bot, update):
            return NEXT2

        next = MessageHandler(None, next)

        def next2(bot, update):
            return ConversationHandler.END

        next2 = MessageHandler(None, next2)

        ch = ConversationHandler([start], {NEXT: [next], NEXT2: [next2]}, [], name='name2',
                                 persistent=True)
        dp.add_handler(ch)
        assert ch.conversations[ch._get_key(update)] == 1
        dp.process_update(update)
        assert ch._get_key(update) not in ch.conversations
        update.message.text = '/start'
        dp.process_update(update)
        assert ch.conversations[ch._get_key(update)] == 0
        assert ch.conversations == dict_persistence.conversations['name2']
