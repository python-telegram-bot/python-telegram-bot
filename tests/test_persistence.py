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
import logging
from collections import defaultdict

import pytest

from telegram import Update, Message, User, Chat
from telegram.ext import BasePersistence, Updater, ConversationHandler, MessageHandler, Filters


@pytest.fixture(scope="function")
def base_persistence():
    return BasePersistence(store_chat_data=True, store_user_data=True)


@pytest.fixture(scope="function")
def chat_data():
    return defaultdict(dict, {-12345: {'test1': 'test2'}, -67890: {'test3': 'test4'}})


@pytest.fixture(scope="function")
def user_data():
    return defaultdict(dict, {12345: {'test1': 'test2'}, 67890: {'test3': 'test4'}})


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
            base_persistence.update_chat_data(None)
        with pytest.raises(NotImplementedError):
            base_persistence.update_user_data(None)
        with pytest.raises(NotImplementedError):
            base_persistence.update_conversation(None)
        with pytest.raises(NotImplementedError):
            base_persistence.flush()

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

    def test_dispatcher_integration_handlers(self, caplog, bot, base_persistence: BasePersistence,
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
        dp.process_update(u)

        assert dp.user_data[54321][1] == 'test7'
        assert dp.chat_data[-987654][2] == 'test8'
