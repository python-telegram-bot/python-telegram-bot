#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
from time import sleep

import pytest

from telegram import Update, Message, User, Chat, CallbackQuery
from telegram.ext import (ConversationHandler, CommandHandler, CallbackQueryHandler)


@pytest.fixture(scope='class')
def user1():
    return User(first_name='Misses Test', id=123)


@pytest.fixture(scope='class')
def user2():
    return User(first_name='Mister Test', id=124)


class TestConversationHandler(object):
    # State definitions
    # At first we're thirsty.  Then we brew coffee, we drink it
    # and then we can start coding!
    END, THIRSTY, BREWING, DRINKING, CODING = range(-1, 4)

    current_state, entry_points, states, fallbacks = None, None, None, None
    group = Chat(0, Chat.GROUP)
    second_group = Chat(1, Chat.GROUP)

    # Test related
    @pytest.fixture(autouse=True)
    def reset(self):
        self.current_state = dict()
        self.entry_points = [CommandHandler('start', self.start)]
        self.states = {
            self.THIRSTY: [CommandHandler('brew', self.brew), CommandHandler('wait', self.start)],
            self.BREWING: [CommandHandler('pourCoffee', self.drink)],
            self.DRINKING:
                [CommandHandler('startCoding', self.code),
                 CommandHandler('drinkMore', self.drink)],
            self.CODING: [
                CommandHandler('keepCoding', self.code),
                CommandHandler('gettingThirsty', self.start),
                CommandHandler('drinkMore', self.drink)
            ],
        }
        self.fallbacks = [CommandHandler('eat', self.start)]

    # State handlers
    def _set_state(self, update, state):
        self.current_state[update.message.from_user.id] = state
        return state

    # Actions
    def start(self, bot, update):
        return self._set_state(update, self.THIRSTY)

    def start_end(self, bot, update):
        return self._set_state(update, self.END)

    def brew(self, bot, update):
        return self._set_state(update, self.BREWING)

    def drink(self, bot, update):
        return self._set_state(update, self.DRINKING)

    def code(self, bot, update):
        return self._set_state(update, self.CODING)

    # Tests
    def test_per_all_false(self):
        with pytest.raises(ValueError, match="can't all be 'False'"):
            handler = ConversationHandler(self.entry_points, self.states, self.fallbacks,
                                          per_chat=False, per_user=False, per_message=False)

    def test_conversation_handler(self, dp, bot, user1, user2):
        handler = ConversationHandler(entry_points=self.entry_points, states=self.states,
                                      fallbacks=self.fallbacks)
        dp.add_handler(handler)

        # User one, starts the state machine.
        message = Message(0, user1, None, self.group, text='/start', bot=bot)
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.THIRSTY

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.BREWING

        # Lets see if an invalid command makes sure, no state is changed.
        message.text = '/nothing'
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.BREWING

        # Lets see if the state machine still works by pouring coffee.
        message.text = '/pourCoffee'
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING

        # Let's now verify that for another user, who did not start yet,
        # the state has not been changed.
        message.from_user = user2
        dp.process_update(Update(update_id=0, message=message))
        with pytest.raises(KeyError):
            self.current_state[user2.id]

    def test_conversation_handler_fallback(self, dp, bot, user1, user2):
        handler = ConversationHandler(entry_points=self.entry_points, states=self.states,
                                      fallbacks=self.fallbacks)
        dp.add_handler(handler)

        # first check if fallback will not trigger start when not started
        message = Message(0, user1, None, self.group, text='/eat', bot=bot)
        dp.process_update(Update(update_id=0, message=message))
        with pytest.raises(KeyError):
            self.current_state[user1.id]

        # User starts the state machine.
        message.text = '/start'
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.THIRSTY

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.BREWING

        # Now a fallback command is issued
        message.text = '/eat'
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.THIRSTY

    def test_conversation_handler_per_chat(self, dp, bot, user1, user2):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            per_user=False)
        dp.add_handler(handler)

        # User one, starts the state machine.
        message = Message(0, user1, None, self.group, text='/start', bot=bot)
        dp.process_update(Update(update_id=0, message=message))

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        dp.process_update(Update(update_id=0, message=message))

        # Let's now verify that for another user, who did not start yet,
        # the state will be changed because they are in the same group.
        message.from_user = user2
        message.text = '/pourCoffee'
        dp.process_update(Update(update_id=0, message=message))

        assert handler.conversations[(self.group.id,)] == self.DRINKING

    def test_conversation_handler_per_user(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            per_chat=False)
        dp.add_handler(handler)

        # User one, starts the state machine.
        message = Message(0, user1, None, self.group, text='/start', bot=bot)
        dp.process_update(Update(update_id=0, message=message))

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        dp.process_update(Update(update_id=0, message=message))

        # Let's now verify that for the same user in a different group, the state will still be
        # updated
        message.chat = self.second_group
        message.text = '/pourCoffee'
        dp.process_update(Update(update_id=0, message=message))

        assert handler.conversations[(user1.id,)] == self.DRINKING

    def test_conversation_handler_per_message(self, dp, bot, user1, user2):
        def entry(bot, update):
            return 1

        def one(bot, update):
            return 2

        def two(bot, update):
            return ConversationHandler.END

        handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(entry)],
            states={1: [CallbackQueryHandler(one)],
                    2: [CallbackQueryHandler(two)]},
            fallbacks=[],
            per_message=True)
        dp.add_handler(handler)

        # User one, starts the state machine.
        message = Message(0, user1, None, self.group, text='msg w/ inlinekeyboard', bot=bot)

        cbq = CallbackQuery(0, user1, None, message=message, data='data', bot=bot)
        dp.process_update(Update(update_id=0, callback_query=cbq))

        assert handler.conversations[(self.group.id, user1.id, message.message_id)] == 1

        dp.process_update(Update(update_id=0, callback_query=cbq))

        assert handler.conversations[(self.group.id, user1.id, message.message_id)] == 2

        # Let's now verify that for a different user in the same group, the state will not be
        # updated
        cbq.from_user = user2
        dp.process_update(Update(update_id=0, callback_query=cbq))

        assert handler.conversations[(self.group.id, user1.id, message.message_id)] == 2

    def test_end_on_first_message(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_end)], states={}, fallbacks=[])
        dp.add_handler(handler)

        # User starts the state machine and immediately ends it.
        message = Message(0, user1, None, self.group, text='/start', bot=bot)
        dp.process_update(Update(update_id=0, message=message))
        assert len(handler.conversations) == 0

    def test_end_on_first_message_async(self, dp, bot, user1):
        start_end_async = (lambda bot, update: dp.run_async(self.start_end, bot, update))

        handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_end_async)], states={}, fallbacks=[])
        dp.add_handler(handler)

        # User starts the state machine with an async function that immediately ends the
        # conversation. Async results are resolved when the users state is queried next time.
        message = Message(0, user1, None, self.group, text='/start', bot=bot)
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(.1)
        # Assert that the Promise has been accepted as the new state
        assert len(handler.conversations) == 1

        message.text = 'resolve promise pls'
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(.1)
        # Assert that the Promise has been resolved and the conversation ended.
        assert len(handler.conversations) == 0

    def test_per_chat_message_without_chat(self, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_end)], states={}, fallbacks=[])
        cbq = CallbackQuery(0, user1, None, None, bot=bot)
        update = Update(0, callback_query=cbq)
        assert not handler.check_update(update)

    def test_channel_message_without_chat(self, bot):
        handler = ConversationHandler(entry_points=[CommandHandler('start', self.start_end)],
                                      states={}, fallbacks=[])
        message = Message(0, None, None, Chat(0, Chat.CHANNEL, 'Misses Test'), bot=bot)
        update = Update(0, message=message)
        assert not handler.check_update(update)
