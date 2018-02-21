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
import pickle
from collections import defaultdict

import os

import pytest

from telegram.ext import PicklePersistence


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
        with open(name, 'wb') as f:
            f.write(bytes('nonesense', 'utf8'))
    yield True
    for name in ['pickletest_user_data', 'pickletest_chat_data', 'pickletest_conversations',
                 'pickletest']:
        os.remove(name)


@pytest.fixture(scope='function')
def good_pickle_files():
    user_data = {12345: {'test1': 'test2'}, 67890: {'test3': 'test4'}}
    chat_data = {-12345: {'test5': 'test6'}, -67890: {'test7': 'test8'}}
    conversations = {'name1': {(123, 123): 1, (456, 654): 2},
                     'name2': {(123, 321): 3, (890, 890): 4}}
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


class TestPickelPersistence(object):
    def test_no_files_present_multi_file(self, pickle_persistence):
        assert pickle_persistence.get_user_data() == defaultdict(dict)
        assert pickle_persistence.get_chat_data() == defaultdict(dict)
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
        assert user_data[67890]['test3'] == 'test4'
        assert user_data[54321] == {}

        chat_data = pickle_persistence.get_chat_data()
        assert isinstance(chat_data, defaultdict)
        assert chat_data[-12345]['test5'] == 'test6'
        assert chat_data[-67890]['test7'] == 'test8'
        assert chat_data[-54321] == {}

        conversation1 = pickle_persistence.get_conversations('name1')
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 1
        assert conversation1[(456, 654)] == 2
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = pickle_persistence.get_conversations('name2')
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 3
        assert conversation2[(890, 890)] == 4
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    def test_with_good_single_file(self, pickle_persistence, good_pickle_files):
        pickle_persistence.single_file = True
        user_data = pickle_persistence.get_user_data()
        assert isinstance(user_data, defaultdict)
        assert user_data[12345]['test1'] == 'test2'
        assert user_data[67890]['test3'] == 'test4'
        assert user_data[54321] == {}

        chat_data = pickle_persistence.get_chat_data()
        assert isinstance(chat_data, defaultdict)
        assert chat_data[-12345]['test5'] == 'test6'
        assert chat_data[-67890]['test7'] == 'test8'
        assert chat_data[-54321] == {}

        conversation1 = pickle_persistence.get_conversations('name1')
        assert isinstance(conversation1, dict)
        assert conversation1[(123, 123)] == 1
        assert conversation1[(456, 654)] == 2
        with pytest.raises(KeyError):
            conversation1[(890, 890)]
        conversation2 = pickle_persistence.get_conversations('name2')
        assert isinstance(conversation1, dict)
        assert conversation2[(123, 321)] == 3
        assert conversation2[(890, 890)] == 4
        with pytest.raises(KeyError):
            conversation2[(123, 123)]

    def test_updating_multi_file(self, pickle_persistence: PicklePersistence, good_pickle_files):
        user_data = pickle_persistence.get_user_data()
        user_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(user_data)
        assert pickle_persistence.user_data == user_data
        with open('pickletest_user_data', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f))
        assert user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(chat_data)
        assert pickle_persistence.chat_data == chat_data
        with open('pickletest_chat_data', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f))
        assert chat_data_test == chat_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1
        pickle_persistence.update_conversations('name1', conversation1)
        assert pickle_persistence.conversations['name1'] == conversation1
        with open('pickletest_conversations', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f))
        assert conversations_test['name1'] == conversation1

    def test_updating_single_file(self, pickle_persistence: PicklePersistence, good_pickle_files):
        pickle_persistence.single_file = True

        user_data = pickle_persistence.get_user_data()
        user_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(user_data)
        assert pickle_persistence.user_data == user_data
        with open('pickletest', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f)['user_data'])
        assert user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(chat_data)
        assert pickle_persistence.chat_data == chat_data
        with open('pickletest', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f)['chat_data'])
        assert chat_data_test == chat_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1
        pickle_persistence.update_conversations('name1', conversation1)
        assert pickle_persistence.conversations['name1'] == conversation1
        with open('pickletest', 'rb') as f:
            conversations_test = defaultdict(dict, pickle.load(f)['conversations'])
        assert conversations_test['name1'] == conversation1

    def test_save_on_flush_multi_files(self, pickle_persistence, good_pickle_files):
        pickle_persistence.on_flush = True

        user_data = pickle_persistence.get_user_data()
        user_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.user_data == user_data

        pickle_persistence.update_user_data(user_data)
        assert pickle_persistence.user_data == user_data

        with open('pickletest_user_data', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f))
        assert not user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.chat_data == chat_data

        pickle_persistence.update_chat_data(chat_data)
        assert pickle_persistence.chat_data == chat_data

        with open('pickletest_chat_data', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f))
        assert not chat_data_test == chat_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1

        pickle_persistence.update_conversations('name1', conversation1)
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
        pickle_persistence.on_flush = True
        pickle_persistence.single_file = True

        user_data = pickle_persistence.get_user_data()
        user_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.user_data == user_data
        pickle_persistence.update_user_data(user_data)
        assert pickle_persistence.user_data == user_data
        with open('pickletest', 'rb') as f:
            user_data_test = defaultdict(dict, pickle.load(f)['user_data'])
        assert not user_data_test == user_data

        chat_data = pickle_persistence.get_chat_data()
        chat_data[54321]['test9'] = 'test 10'
        assert not pickle_persistence.chat_data == chat_data
        pickle_persistence.update_chat_data(chat_data)
        assert pickle_persistence.chat_data == chat_data
        with open('pickletest', 'rb') as f:
            chat_data_test = defaultdict(dict, pickle.load(f)['chat_data'])
        assert not chat_data_test == chat_data

        conversation1 = pickle_persistence.get_conversations('name1')
        conversation1[(123, 123)] = 5
        assert not pickle_persistence.conversations['name1'] == conversation1
        pickle_persistence.update_conversations('name1', conversation1)
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

    @classmethod
    def teardown_class(cls):
        try:
            for name in ['pickletest_user_data', 'pickletest_chat_data',
                         'pickletest_conversations',
                         'pickletest']:
                os.remove(name)
        except Exception:
            pass
