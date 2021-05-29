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
import logging
from time import sleep

import pytest
from flaky import flaky

from telegram import (
    CallbackQuery,
    Chat,
    ChosenInlineResult,
    InlineQuery,
    Message,
    PreCheckoutQuery,
    ShippingQuery,
    Update,
    User,
    MessageEntity,
)
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    InlineQueryHandler,
    CallbackContext,
    DispatcherHandlerStop,
    TypeHandler,
    JobQueue,
)


@pytest.fixture(scope='class')
def user1():
    return User(first_name='Misses Test', id=123, is_bot=False)


@pytest.fixture(scope='class')
def user2():
    return User(first_name='Mister Test', id=124, is_bot=False)


@pytest.fixture(autouse=True)
def start_stop_job_queue(dp):
    dp.job_queue = JobQueue()
    dp.job_queue.set_dispatcher(dp)
    dp.job_queue.start()
    yield
    dp.job_queue.stop()


def raise_dphs(func):
    def decorator(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if self.raise_dp_handler_stop:
            raise DispatcherHandlerStop(result)
        return result

    return decorator


class TestConversationHandler:
    # State definitions
    # At first we're thirsty.  Then we brew coffee, we drink it
    # and then we can start coding!
    END, THIRSTY, BREWING, DRINKING, CODING = range(-1, 4)

    # Drinking state definitions (nested)
    # At first we're holding the cup.  Then we sip coffee, and last we swallow it
    HOLDING, SIPPING, SWALLOWING, REPLENISHING, STOPPING = map(chr, range(ord('a'), ord('f')))

    current_state, entry_points, states, fallbacks = None, None, None, None
    group = Chat(0, Chat.GROUP)
    second_group = Chat(1, Chat.GROUP)

    raise_dp_handler_stop = False
    test_flag = False

    def test_slot_behaviour(self, recwarn, mro_slots):
        handler = ConversationHandler(self.entry_points, self.states, self.fallbacks)
        for attr in handler.__slots__:
            assert getattr(handler, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not handler.__dict__, f"got missing slot(s): {handler.__dict__}"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"
        handler.custom, handler._persistence = 'should give warning', handler._persistence
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), [
            w.message for w in recwarn.list
        ]

    # Test related
    @pytest.fixture(autouse=True)
    def reset(self):
        self.raise_dp_handler_stop = False
        self.test_flag = False
        self.current_state = {}
        self.entry_points = [CommandHandler('start', self.start)]
        self.states = {
            self.THIRSTY: [CommandHandler('brew', self.brew), CommandHandler('wait', self.start)],
            self.BREWING: [CommandHandler('pourCoffee', self.drink)],
            self.DRINKING: [
                CommandHandler('startCoding', self.code),
                CommandHandler('drinkMore', self.drink),
                CommandHandler('end', self.end),
            ],
            self.CODING: [
                CommandHandler('keepCoding', self.code),
                CommandHandler('gettingThirsty', self.start),
                CommandHandler('drinkMore', self.drink),
            ],
        }
        self.fallbacks = [CommandHandler('eat', self.start)]
        self.is_timeout = False

        # for nesting tests
        self.nested_states = {
            self.THIRSTY: [CommandHandler('brew', self.brew), CommandHandler('wait', self.start)],
            self.BREWING: [CommandHandler('pourCoffee', self.drink)],
            self.CODING: [
                CommandHandler('keepCoding', self.code),
                CommandHandler('gettingThirsty', self.start),
                CommandHandler('drinkMore', self.drink),
            ],
        }
        self.drinking_entry_points = [CommandHandler('hold', self.hold)]
        self.drinking_states = {
            self.HOLDING: [CommandHandler('sip', self.sip)],
            self.SIPPING: [CommandHandler('swallow', self.swallow)],
            self.SWALLOWING: [CommandHandler('hold', self.hold)],
        }
        self.drinking_fallbacks = [
            CommandHandler('replenish', self.replenish),
            CommandHandler('stop', self.stop),
            CommandHandler('end', self.end),
            CommandHandler('startCoding', self.code),
            CommandHandler('drinkMore', self.drink),
        ]
        self.drinking_entry_points.extend(self.drinking_fallbacks)

        # Map nested states to parent states:
        self.drinking_map_to_parent = {
            # Option 1 - Map a fictional internal state to an external parent state
            self.REPLENISHING: self.BREWING,
            # Option 2 - Map a fictional internal state to the END state on the parent
            self.STOPPING: self.END,
            # Option 3 - Map the internal END state to an external parent state
            self.END: self.CODING,
            # Option 4 - Map an external state to the same external parent state
            self.CODING: self.CODING,
            # Option 5 - Map an external state to the internal entry point
            self.DRINKING: self.DRINKING,
        }

    # State handlers
    def _set_state(self, update, state):
        self.current_state[update.message.from_user.id] = state
        return state

    # Actions
    @raise_dphs
    def start(self, bot, update):
        if isinstance(update, Update):
            return self._set_state(update, self.THIRSTY)
        return self._set_state(bot, self.THIRSTY)

    @raise_dphs
    def end(self, bot, update):
        return self._set_state(update, self.END)

    @raise_dphs
    def start_end(self, bot, update):
        return self._set_state(update, self.END)

    @raise_dphs
    def start_none(self, bot, update):
        return self._set_state(update, None)

    @raise_dphs
    def brew(self, bot, update):
        if isinstance(update, Update):
            return self._set_state(update, self.BREWING)
        return self._set_state(bot, self.BREWING)

    @raise_dphs
    def drink(self, bot, update):
        return self._set_state(update, self.DRINKING)

    @raise_dphs
    def code(self, bot, update):
        return self._set_state(update, self.CODING)

    @raise_dphs
    def passout(self, bot, update):
        assert update.message.text == '/brew'
        assert isinstance(update, Update)
        self.is_timeout = True

    @raise_dphs
    def passout2(self, bot, update):
        assert isinstance(update, Update)
        self.is_timeout = True

    @raise_dphs
    def passout_context(self, update, context):
        assert update.message.text == '/brew'
        assert isinstance(context, CallbackContext)
        self.is_timeout = True

    @raise_dphs
    def passout2_context(self, update, context):
        assert isinstance(context, CallbackContext)
        self.is_timeout = True

    # Drinking actions (nested)

    @raise_dphs
    def hold(self, bot, update):
        return self._set_state(update, self.HOLDING)

    @raise_dphs
    def sip(self, bot, update):
        return self._set_state(update, self.SIPPING)

    @raise_dphs
    def swallow(self, bot, update):
        return self._set_state(update, self.SWALLOWING)

    @raise_dphs
    def replenish(self, bot, update):
        return self._set_state(update, self.REPLENISHING)

    @raise_dphs
    def stop(self, bot, update):
        return self._set_state(update, self.STOPPING)

    # Tests
    @pytest.mark.parametrize(
        'attr',
        [
            'entry_points',
            'states',
            'fallbacks',
            'per_chat',
            'name',
            'per_user',
            'allow_reentry',
            'conversation_timeout',
            'map_to_parent',
        ],
        indirect=False,
    )
    def test_immutable(self, attr):
        ch = ConversationHandler(
            'entry_points',
            {'states': ['states']},
            'fallbacks',
            per_chat='per_chat',
            per_user='per_user',
            per_message=False,
            allow_reentry='allow_reentry',
            conversation_timeout='conversation_timeout',
            name='name',
            map_to_parent='map_to_parent',
        )

        value = getattr(ch, attr)
        if isinstance(value, list):
            assert value[0] == attr
        elif isinstance(value, dict):
            assert list(value.keys())[0] == attr
        else:
            assert getattr(ch, attr) == attr
        with pytest.raises(ValueError, match=f'You can not assign a new value to {attr}'):
            setattr(ch, attr, True)

    def test_immutable_per_message(self):
        ch = ConversationHandler(
            'entry_points',
            {'states': ['states']},
            'fallbacks',
            per_chat='per_chat',
            per_user='per_user',
            per_message=False,
            allow_reentry='allow_reentry',
            conversation_timeout='conversation_timeout',
            name='name',
            map_to_parent='map_to_parent',
        )
        assert ch.per_message is False
        with pytest.raises(ValueError, match='You can not assign a new value to per_message'):
            ch.per_message = True

    def test_per_all_false(self):
        with pytest.raises(ValueError, match="can't all be 'False'"):
            ConversationHandler(
                self.entry_points,
                self.states,
                self.fallbacks,
                per_chat=False,
                per_user=False,
                per_message=False,
            )

    def test_name_and_persistent(self, dp):
        with pytest.raises(ValueError, match="when handler is unnamed"):
            dp.add_handler(ConversationHandler([], {}, [], persistent=True))
        c = ConversationHandler([], {}, [], name="handler", persistent=True)
        assert c.name == "handler"

    def test_conversation_handler(self, dp, bot, user1, user2):
        handler = ConversationHandler(
            entry_points=self.entry_points, states=self.states, fallbacks=self.fallbacks
        )
        dp.add_handler(handler)

        # User one, starts the state machine.
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.THIRSTY

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.BREWING

        # Lets see if an invalid command makes sure, no state is changed.
        message.text = '/nothing'
        message.entities[0].length = len('/nothing')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.BREWING

        # Lets see if the state machine still works by pouring coffee.
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING

        # Let's now verify that for another user, who did not start yet,
        # the state has not been changed.
        message.from_user = user2
        dp.process_update(Update(update_id=0, message=message))
        with pytest.raises(KeyError):
            self.current_state[user2.id]

    def test_conversation_handler_end(self, caplog, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=self.entry_points, states=self.states, fallbacks=self.fallbacks
        )
        dp.add_handler(handler)

        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
        dp.process_update(Update(update_id=0, message=message))
        message.text = '/end'
        message.entities[0].length = len('/end')
        caplog.clear()
        with caplog.at_level(logging.ERROR):
            dp.process_update(Update(update_id=0, message=message))
        assert len(caplog.records) == 0
        assert self.current_state[user1.id] == self.END
        with pytest.raises(KeyError):
            print(handler.conversations[(self.group.id, user1.id)])

    def test_conversation_handler_fallback(self, dp, bot, user1, user2):
        handler = ConversationHandler(
            entry_points=self.entry_points, states=self.states, fallbacks=self.fallbacks
        )
        dp.add_handler(handler)

        # first check if fallback will not trigger start when not started
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/eat',
            entities=[MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/eat'))],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        with pytest.raises(KeyError):
            self.current_state[user1.id]

        # User starts the state machine.
        message.text = '/start'
        message.entities[0].length = len('/start')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.THIRSTY

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.BREWING

        # Now a fallback command is issued
        message.text = '/eat'
        message.entities[0].length = len('/eat')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.THIRSTY

    def test_unknown_state_warning(self, dp, bot, user1, recwarn):
        handler = ConversationHandler(
            entry_points=[CommandHandler("start", lambda u, c: 1)],
            states={
                1: [TypeHandler(Update, lambda u, c: 69)],
                2: [TypeHandler(Update, lambda u, c: -1)],
            },
            fallbacks=self.fallbacks,
            name="xyz",
        )
        dp.add_handler(handler)
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        sleep(0.5)
        dp.process_update(Update(update_id=1, message=message))
        sleep(0.5)
        assert len(recwarn) == 1
        assert str(recwarn[0].message) == (
            "Handler returned state 69 which is unknown to the ConversationHandler xyz."
        )

    def test_conversation_handler_per_chat(self, dp, bot, user1, user2):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            per_user=False,
        )
        dp.add_handler(handler)

        # User one, starts the state machine.
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))

        # Let's now verify that for another user, who did not start yet,
        # the state will be changed because they are in the same group.
        message.from_user = user2
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
        dp.process_update(Update(update_id=0, message=message))

        assert handler.conversations[(self.group.id,)] == self.DRINKING

    def test_conversation_handler_per_user(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            per_chat=False,
        )
        dp.add_handler(handler)

        # User one, starts the state machine.
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))

        # Let's now verify that for the same user in a different group, the state will still be
        # updated
        message.chat = self.second_group
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
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
            states={1: [CallbackQueryHandler(one)], 2: [CallbackQueryHandler(two)]},
            fallbacks=[],
            per_message=True,
        )
        dp.add_handler(handler)

        # User one, starts the state machine.
        message = Message(
            0, None, self.group, from_user=user1, text='msg w/ inlinekeyboard', bot=bot
        )

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
            entry_points=[CommandHandler('start', self.start_end)], states={}, fallbacks=[]
        )
        dp.add_handler(handler)

        # User starts the state machine and immediately ends it.
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        assert len(handler.conversations) == 0

    def test_end_on_first_message_async(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=[
                CommandHandler(
                    'start', lambda bot, update: dp.run_async(self.start_end, bot, update)
                )
            ],
            states={},
            fallbacks=[],
        )
        dp.add_handler(handler)

        # User starts the state machine with an async function that immediately ends the
        # conversation. Async results are resolved when the users state is queried next time.
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(0.1)
        # Assert that the Promise has been accepted as the new state
        assert len(handler.conversations) == 1

        message.text = 'resolve promise pls'
        message.entities[0].length = len('resolve promise pls')
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(0.1)
        # Assert that the Promise has been resolved and the conversation ended.
        assert len(handler.conversations) == 0

    def test_end_on_first_message_async_handler(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_end, run_async=True)],
            states={},
            fallbacks=[],
        )
        dp.add_handler(handler)

        # User starts the state machine with an async function that immediately ends the
        # conversation. Async results are resolved when the users state is queried next time.
        message = Message(
            0,
            None,
            self.group,
            text='/start',
            from_user=user1,
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(0.1)
        # Assert that the Promise has been accepted as the new state
        assert len(handler.conversations) == 1

        message.text = 'resolve promise pls'
        message.entities[0].length = len('resolve promise pls')
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(0.1)
        # Assert that the Promise has been resolved and the conversation ended.
        assert len(handler.conversations) == 0

    def test_none_on_first_message(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_none)], states={}, fallbacks=[]
        )
        dp.add_handler(handler)

        # User starts the state machine and a callback function returns None
        message = Message(0, None, self.group, from_user=user1, text='/start', bot=bot)
        dp.process_update(Update(update_id=0, message=message))
        assert len(handler.conversations) == 0

    def test_none_on_first_message_async(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=[
                CommandHandler(
                    'start', lambda bot, update: dp.run_async(self.start_none, bot, update)
                )
            ],
            states={},
            fallbacks=[],
        )
        dp.add_handler(handler)

        # User starts the state machine with an async function that returns None
        # Async results are resolved when the users state is queried next time.
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(0.1)
        # Assert that the Promise has been accepted as the new state
        assert len(handler.conversations) == 1

        message.text = 'resolve promise pls'
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(0.1)
        # Assert that the Promise has been resolved and the conversation ended.
        assert len(handler.conversations) == 0

    def test_none_on_first_message_async_handler(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_none, run_async=True)],
            states={},
            fallbacks=[],
        )
        dp.add_handler(handler)

        # User starts the state machine with an async function that returns None
        # Async results are resolved when the users state is queried next time.
        message = Message(
            0,
            None,
            self.group,
            text='/start',
            from_user=user1,
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(0.1)
        # Assert that the Promise has been accepted as the new state
        assert len(handler.conversations) == 1

        message.text = 'resolve promise pls'
        dp.update_queue.put(Update(update_id=0, message=message))
        sleep(0.1)
        # Assert that the Promise has been resolved and the conversation ended.
        assert len(handler.conversations) == 0

    def test_per_chat_message_without_chat(self, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_end)], states={}, fallbacks=[]
        )
        cbq = CallbackQuery(0, user1, None, None, bot=bot)
        update = Update(0, callback_query=cbq)
        assert not handler.check_update(update)

    def test_channel_message_without_chat(self, bot):
        handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.all, self.start_end)], states={}, fallbacks=[]
        )
        message = Message(0, date=None, chat=Chat(0, Chat.CHANNEL, 'Misses Test'), bot=bot)

        update = Update(0, channel_post=message)
        assert not handler.check_update(update)

        update = Update(0, edited_channel_post=message)
        assert not handler.check_update(update)

    def test_all_update_types(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_end)], states={}, fallbacks=[]
        )
        message = Message(0, None, self.group, from_user=user1, text='ignore', bot=bot)
        callback_query = CallbackQuery(0, user1, None, message=message, data='data', bot=bot)
        chosen_inline_result = ChosenInlineResult(0, user1, 'query', bot=bot)
        inline_query = InlineQuery(0, user1, 'query', 0, bot=bot)
        pre_checkout_query = PreCheckoutQuery(0, user1, 'USD', 100, [], bot=bot)
        shipping_query = ShippingQuery(0, user1, [], None, bot=bot)
        assert not handler.check_update(Update(0, callback_query=callback_query))
        assert not handler.check_update(Update(0, chosen_inline_result=chosen_inline_result))
        assert not handler.check_update(Update(0, inline_query=inline_query))
        assert not handler.check_update(Update(0, message=message))
        assert not handler.check_update(Update(0, pre_checkout_query=pre_checkout_query))
        assert not handler.check_update(Update(0, shipping_query=shipping_query))

    def test_no_jobqueue_warning(self, dp, bot, user1, caplog):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )
        # save dp.job_queue in temp variable jqueue
        # and then set dp.job_queue to None.
        jqueue = dp.job_queue
        dp.job_queue = None
        dp.add_handler(handler)

        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )

        with caplog.at_level(logging.WARNING):
            dp.process_update(Update(update_id=0, message=message))
            sleep(0.5)
        assert len(caplog.records) == 1
        assert (
            caplog.records[0].message
            == "Ignoring `conversation_timeout` because the Dispatcher has no JobQueue."
        )
        # now set dp.job_queue back to it's original value
        dp.job_queue = jqueue

    def test_schedule_job_exception(self, dp, bot, user1, monkeypatch, caplog):
        def mocked_run_once(*a, **kw):
            raise Exception("job error")

        monkeypatch.setattr(dp.job_queue, "run_once", mocked_run_once)
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            conversation_timeout=100,
        )
        dp.add_handler(handler)

        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )

        with caplog.at_level(logging.ERROR):
            dp.process_update(Update(update_id=0, message=message))
            sleep(0.5)
        assert len(caplog.records) == 2
        assert (
            caplog.records[0].message
            == "Failed to schedule timeout job due to the following exception:"
        )
        assert caplog.records[1].message == "job error"

    def test_promise_exception(self, dp, bot, user1, caplog):
        """
        Here we make sure that when a run_async handle raises an
        exception, the state isn't changed.
        """

        def conv_entry(*a, **kw):
            return 1

        def raise_error(*a, **kw):
            raise Exception("promise exception")

        handler = ConversationHandler(
            entry_points=[CommandHandler("start", conv_entry)],
            states={1: [MessageHandler(Filters.all, raise_error)]},
            fallbacks=self.fallbacks,
            run_async=True,
        )
        dp.add_handler(handler)

        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        # start the conversation
        dp.process_update(Update(update_id=0, message=message))
        sleep(0.1)
        message.text = "error"
        dp.process_update(Update(update_id=0, message=message))
        sleep(0.1)
        message.text = "resolve promise pls"
        caplog.clear()
        with caplog.at_level(logging.ERROR):
            dp.process_update(Update(update_id=0, message=message))
            sleep(0.5)
        assert len(caplog.records) == 3
        assert caplog.records[0].message == "Promise function raised exception"
        assert caplog.records[1].message == "promise exception"
        # assert res is old state
        assert handler.conversations.get((self.group.id, user1.id))[0] == 1

    def test_conversation_timeout(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )
        dp.add_handler(handler)

        # Start state machine, then reach timeout
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
        sleep(0.75)
        assert handler.conversations.get((self.group.id, user1.id)) is None

        # Start state machine, do something, then reach timeout
        dp.process_update(Update(update_id=1, message=message))
        assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=2, message=message))
        assert handler.conversations.get((self.group.id, user1.id)) == self.BREWING
        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None

    def test_timeout_not_triggered_on_conv_end_async(self, bot, dp, user1):
        def timeout(*a, **kw):
            self.test_flag = True

        self.states.update({ConversationHandler.TIMEOUT: [TypeHandler(Update, timeout)]})
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
            run_async=True,
        )
        dp.add_handler(handler)

        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        # start the conversation
        dp.process_update(Update(update_id=0, message=message))
        sleep(0.1)
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=1, message=message))
        sleep(0.1)
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
        dp.process_update(Update(update_id=2, message=message))
        sleep(0.1)
        message.text = '/end'
        message.entities[0].length = len('/end')
        dp.process_update(Update(update_id=3, message=message))
        sleep(1)
        # assert timeout handler didn't got called
        assert self.test_flag is False

    def test_conversation_timeout_dispatcher_handler_stop(self, dp, bot, user1, caplog):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )

        def timeout(*args, **kwargs):
            raise DispatcherHandlerStop()

        self.states.update({ConversationHandler.TIMEOUT: [TypeHandler(Update, timeout)]})
        dp.add_handler(handler)

        # Start state machine, then reach timeout
        message = Message(
            0,
            None,
            self.group,
            text='/start',
            from_user=user1,
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )

        with caplog.at_level(logging.WARNING):
            dp.process_update(Update(update_id=0, message=message))
            assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
            sleep(0.9)
            assert handler.conversations.get((self.group.id, user1.id)) is None
        assert len(caplog.records) == 1
        rec = caplog.records[-1]
        assert rec.getMessage().startswith('DispatcherHandlerStop in TIMEOUT')

    def test_conversation_handler_timeout_update_and_context(self, cdp, bot, user1):
        context = None

        def start_callback(u, c):
            nonlocal context, self
            context = c
            return self.start(u, c)

        states = self.states
        timeout_handler = CommandHandler('start', None)
        states.update({ConversationHandler.TIMEOUT: [timeout_handler]})
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_callback)],
            states=states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )
        cdp.add_handler(handler)

        # Start state machine, then reach timeout
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        update = Update(update_id=0, message=message)

        def timeout_callback(u, c):
            nonlocal update, context, self
            self.is_timeout = True
            assert u is update
            assert c is context

        timeout_handler.callback = timeout_callback

        cdp.process_update(update)
        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None
        assert self.is_timeout

    @flaky(3, 1)
    def test_conversation_timeout_keeps_extending(self, dp, bot, user1):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )
        dp.add_handler(handler)

        # Start state machine, wait, do something, verify the timeout is extended.
        # t=0 /start (timeout=.5)
        # t=.35 /brew (timeout=.85)
        # t=.5 original timeout
        # t=.6 /pourCoffee (timeout=1.1)
        # t=.85 second timeout
        # t=1.1 actual timeout
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
        sleep(0.35)  # t=.35
        assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))
        assert handler.conversations.get((self.group.id, user1.id)) == self.BREWING
        sleep(0.25)  # t=.6
        assert handler.conversations.get((self.group.id, user1.id)) == self.BREWING
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
        dp.process_update(Update(update_id=0, message=message))
        assert handler.conversations.get((self.group.id, user1.id)) == self.DRINKING
        sleep(0.4)  # t=1.0
        assert handler.conversations.get((self.group.id, user1.id)) == self.DRINKING
        sleep(0.3)  # t=1.3
        assert handler.conversations.get((self.group.id, user1.id)) is None

    def test_conversation_timeout_two_users(self, dp, bot, user1, user2):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )
        dp.add_handler(handler)

        # Start state machine, do something as second user, then reach timeout
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        message.entities[0].length = len('/brew')
        message.from_user = user2
        dp.process_update(Update(update_id=0, message=message))
        assert handler.conversations.get((self.group.id, user2.id)) is None
        message.text = '/start'
        message.entities[0].length = len('/start')
        dp.process_update(Update(update_id=0, message=message))
        assert handler.conversations.get((self.group.id, user2.id)) == self.THIRSTY
        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None
        assert handler.conversations.get((self.group.id, user2.id)) is None

    def test_conversation_handler_timeout_state(self, dp, bot, user1):
        states = self.states
        states.update(
            {
                ConversationHandler.TIMEOUT: [
                    CommandHandler('brew', self.passout),
                    MessageHandler(~Filters.regex('oding'), self.passout2),
                ]
            }
        )
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )
        dp.add_handler(handler)

        # CommandHandler timeout
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))
        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None
        assert self.is_timeout

        # MessageHandler timeout
        self.is_timeout = False
        message.text = '/start'
        message.entities[0].length = len('/start')
        dp.process_update(Update(update_id=1, message=message))
        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None
        assert self.is_timeout

        # Timeout but no valid handler
        self.is_timeout = False
        dp.process_update(Update(update_id=0, message=message))
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))
        message.text = '/startCoding'
        message.entities[0].length = len('/startCoding')
        dp.process_update(Update(update_id=0, message=message))
        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None
        assert not self.is_timeout

    def test_conversation_handler_timeout_state_context(self, cdp, bot, user1):
        states = self.states
        states.update(
            {
                ConversationHandler.TIMEOUT: [
                    CommandHandler('brew', self.passout_context),
                    MessageHandler(~Filters.regex('oding'), self.passout2_context),
                ]
            }
        )
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )
        cdp.add_handler(handler)

        # CommandHandler timeout
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        cdp.process_update(Update(update_id=0, message=message))
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        cdp.process_update(Update(update_id=0, message=message))
        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None
        assert self.is_timeout

        # MessageHandler timeout
        self.is_timeout = False
        message.text = '/start'
        message.entities[0].length = len('/start')
        cdp.process_update(Update(update_id=1, message=message))
        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None
        assert self.is_timeout

        # Timeout but no valid handler
        self.is_timeout = False
        cdp.process_update(Update(update_id=0, message=message))
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        cdp.process_update(Update(update_id=0, message=message))
        message.text = '/startCoding'
        message.entities[0].length = len('/startCoding')
        cdp.process_update(Update(update_id=0, message=message))
        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None
        assert not self.is_timeout

    def test_conversation_timeout_cancel_conflict(self, dp, bot, user1):
        # Start state machine, wait half the timeout,
        # then call a callback that takes more than the timeout
        # t=0 /start (timeout=.5)
        # t=.25 /slowbrew (sleep .5)
        # |  t=.5 original timeout (should not execute)
        # |  t=.75 /slowbrew returns (timeout=1.25)
        # t=1.25 timeout

        def slowbrew(_bot, update):
            sleep(0.25)
            # Let's give to the original timeout a chance to execute
            sleep(0.25)
            # By returning None we do not override the conversation state so
            # we can see if the timeout has been executed

        states = self.states
        states[self.THIRSTY].append(CommandHandler('slowbrew', slowbrew))
        states.update({ConversationHandler.TIMEOUT: [MessageHandler(None, self.passout2)]})

        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )
        dp.add_handler(handler)

        # CommandHandler timeout
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
            bot=bot,
        )
        dp.process_update(Update(update_id=0, message=message))
        sleep(0.25)
        message.text = '/slowbrew'
        message.entities[0].length = len('/slowbrew')
        dp.process_update(Update(update_id=0, message=message))
        assert handler.conversations.get((self.group.id, user1.id)) is not None
        assert not self.is_timeout

        sleep(0.7)
        assert handler.conversations.get((self.group.id, user1.id)) is None
        assert self.is_timeout

    def test_conversation_timeout_warning_only_shown_once(self, recwarn):
        ConversationHandler(
            entry_points=self.entry_points,
            states={
                self.THIRSTY: [
                    ConversationHandler(
                        entry_points=self.entry_points,
                        states={
                            self.BREWING: [CommandHandler('pourCoffee', self.drink)],
                        },
                        fallbacks=self.fallbacks,
                    )
                ],
                self.DRINKING: [
                    ConversationHandler(
                        entry_points=self.entry_points,
                        states={
                            self.CODING: [CommandHandler('startCoding', self.code)],
                        },
                        fallbacks=self.fallbacks,
                    )
                ],
            },
            fallbacks=self.fallbacks,
            conversation_timeout=100,
        )
        assert len(recwarn) == 1
        assert str(recwarn[0].message) == (
            "Using `conversation_timeout` with nested conversations is currently not "
            "supported. You can still try to use it, but it will likely behave "
            "differently from what you expect."
        )

    def test_per_message_warning_is_only_shown_once(self, recwarn):
        ConversationHandler(
            entry_points=self.entry_points,
            states={
                self.THIRSTY: [CommandHandler('pourCoffee', self.drink)],
                self.BREWING: [CommandHandler('startCoding', self.code)],
            },
            fallbacks=self.fallbacks,
            per_message=True,
        )
        assert len(recwarn) == 1
        assert str(recwarn[0].message) == (
            "If 'per_message=True', all entry points and state handlers"
            " must be 'CallbackQueryHandler', since no other handlers"
            " have a message context."
        )

    def test_per_message_false_warning_is_only_shown_once(self, recwarn):
        ConversationHandler(
            entry_points=self.entry_points,
            states={
                self.THIRSTY: [CallbackQueryHandler(self.drink)],
                self.BREWING: [CallbackQueryHandler(self.code)],
            },
            fallbacks=self.fallbacks,
            per_message=False,
        )
        assert len(recwarn) == 1
        assert str(recwarn[0].message) == (
            "If 'per_message=False', 'CallbackQueryHandler' will not be "
            "tracked for every message."
        )

    def test_warnings_per_chat_is_only_shown_once(self, recwarn):
        def hello(bot, update):
            return self.BREWING

        def bye(bot, update):
            return ConversationHandler.END

        ConversationHandler(
            entry_points=self.entry_points,
            states={
                self.THIRSTY: [InlineQueryHandler(hello)],
                self.BREWING: [InlineQueryHandler(bye)],
            },
            fallbacks=self.fallbacks,
            per_chat=True,
        )
        assert len(recwarn) == 1
        assert str(recwarn[0].message) == (
            "If 'per_chat=True', 'InlineQueryHandler' can not be used,"
            " since inline queries have no chat context."
        )

    def test_nested_conversation_handler(self, dp, bot, user1, user2):
        self.nested_states[self.DRINKING] = [
            ConversationHandler(
                entry_points=self.drinking_entry_points,
                states=self.drinking_states,
                fallbacks=self.drinking_fallbacks,
                map_to_parent=self.drinking_map_to_parent,
            )
        ]
        handler = ConversationHandler(
            entry_points=self.entry_points, states=self.nested_states, fallbacks=self.fallbacks
        )
        dp.add_handler(handler)

        # User one, starts the state machine.
        message = Message(
            0,
            None,
            self.group,
            from_user=user1,
            text='/start',
            bot=bot,
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
        )
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.THIRSTY

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.BREWING

        # Lets pour some coffee.
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING

        # The user is holding the cup
        message.text = '/hold'
        message.entities[0].length = len('/hold')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.HOLDING

        # The user is sipping coffee
        message.text = '/sip'
        message.entities[0].length = len('/sip')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.SIPPING

        # The user is swallowing
        message.text = '/swallow'
        message.entities[0].length = len('/swallow')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.SWALLOWING

        # The user is holding the cup again
        message.text = '/hold'
        message.entities[0].length = len('/hold')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.HOLDING

        # The user wants to replenish the coffee supply
        message.text = '/replenish'
        message.entities[0].length = len('/replenish')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.REPLENISHING
        assert handler.conversations[(0, user1.id)] == self.BREWING

        # The user wants to drink their coffee again
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING

        # The user is now ready to start coding
        message.text = '/startCoding'
        message.entities[0].length = len('/startCoding')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.CODING

        # The user decides it's time to drink again
        message.text = '/drinkMore'
        message.entities[0].length = len('/drinkMore')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING

        # The user is holding their cup
        message.text = '/hold'
        message.entities[0].length = len('/hold')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.HOLDING

        # The user wants to end with the drinking and go back to coding
        message.text = '/end'
        message.entities[0].length = len('/end')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.END
        assert handler.conversations[(0, user1.id)] == self.CODING

        # The user wants to drink once more
        message.text = '/drinkMore'
        message.entities[0].length = len('/drinkMore')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING

        # The user wants to stop altogether
        message.text = '/stop'
        message.entities[0].length = len('/stop')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.STOPPING
        assert handler.conversations.get((0, user1.id)) is None

    def test_conversation_dispatcher_handler_stop(self, dp, bot, user1, user2):
        self.nested_states[self.DRINKING] = [
            ConversationHandler(
                entry_points=self.drinking_entry_points,
                states=self.drinking_states,
                fallbacks=self.drinking_fallbacks,
                map_to_parent=self.drinking_map_to_parent,
            )
        ]
        handler = ConversationHandler(
            entry_points=self.entry_points, states=self.nested_states, fallbacks=self.fallbacks
        )

        def test_callback(u, c):
            self.test_flag = True

        dp.add_handler(handler)
        dp.add_handler(TypeHandler(Update, test_callback), group=1)
        self.raise_dp_handler_stop = True

        # User one, starts the state machine.
        message = Message(
            0,
            None,
            self.group,
            text='/start',
            bot=bot,
            from_user=user1,
            entities=[
                MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
            ],
        )
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.THIRSTY
        assert not self.test_flag

        # The user is thirsty and wants to brew coffee.
        message.text = '/brew'
        message.entities[0].length = len('/brew')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.BREWING
        assert not self.test_flag

        # Lets pour some coffee.
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING
        assert not self.test_flag

        # The user is holding the cup
        message.text = '/hold'
        message.entities[0].length = len('/hold')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.HOLDING
        assert not self.test_flag

        # The user is sipping coffee
        message.text = '/sip'
        message.entities[0].length = len('/sip')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.SIPPING
        assert not self.test_flag

        # The user is swallowing
        message.text = '/swallow'
        message.entities[0].length = len('/swallow')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.SWALLOWING
        assert not self.test_flag

        # The user is holding the cup again
        message.text = '/hold'
        message.entities[0].length = len('/hold')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.HOLDING
        assert not self.test_flag

        # The user wants to replenish the coffee supply
        message.text = '/replenish'
        message.entities[0].length = len('/replenish')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.REPLENISHING
        assert handler.conversations[(0, user1.id)] == self.BREWING
        assert not self.test_flag

        # The user wants to drink their coffee again
        message.text = '/pourCoffee'
        message.entities[0].length = len('/pourCoffee')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING
        assert not self.test_flag

        # The user is now ready to start coding
        message.text = '/startCoding'
        message.entities[0].length = len('/startCoding')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.CODING
        assert not self.test_flag

        # The user decides it's time to drink again
        message.text = '/drinkMore'
        message.entities[0].length = len('/drinkMore')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING
        assert not self.test_flag

        # The user is holding their cup
        message.text = '/hold'
        message.entities[0].length = len('/hold')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.HOLDING
        assert not self.test_flag

        # The user wants to end with the drinking and go back to coding
        message.text = '/end'
        message.entities[0].length = len('/end')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.END
        assert handler.conversations[(0, user1.id)] == self.CODING
        assert not self.test_flag

        # The user wants to drink once more
        message.text = '/drinkMore'
        message.entities[0].length = len('/drinkMore')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.DRINKING
        assert not self.test_flag

        # The user wants to stop altogether
        message.text = '/stop'
        message.entities[0].length = len('/stop')
        dp.process_update(Update(update_id=0, message=message))
        assert self.current_state[user1.id] == self.STOPPING
        assert handler.conversations.get((0, user1.id)) is None
        assert not self.test_flag

    def test_conversation_handler_run_async_true(self, dp):
        conv_handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            run_async=True,
        )

        all_handlers = conv_handler.entry_points + conv_handler.fallbacks
        for state_handlers in conv_handler.states.values():
            all_handlers += state_handlers

        for handler in all_handlers:
            assert handler.run_async

    def test_conversation_handler_run_async_false(self, dp):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_end, run_async=True)],
            states=self.states,
            fallbacks=self.fallbacks,
            run_async=False,
        )

        for handler in conv_handler.entry_points:
            assert handler.run_async

        all_handlers = conv_handler.fallbacks
        for state_handlers in conv_handler.states.values():
            all_handlers += state_handlers

        for handler in all_handlers:
            assert not handler.run_async.value
