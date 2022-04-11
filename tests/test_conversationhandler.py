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
"""Persistence of conversations is tested in test_basepersistence.py"""
import asyncio
import logging
from warnings import filterwarnings

import pytest

from telegram import (
    Chat,
    Update,
    Message,
    MessageEntity,
    User,
    CallbackQuery,
    InlineQuery,
    ChosenInlineResult,
    ShippingQuery,
    PreCheckoutQuery,
)
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    ApplicationHandlerStop,
    TypeHandler,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    JobQueue,
    StringCommandHandler,
    StringRegexHandler,
    PollHandler,
    ShippingQueryHandler,
    PreCheckoutQueryHandler,
    InlineQueryHandler,
    PollAnswerHandler,
    ChosenInlineResultHandler,
)
from telegram.warnings import PTBUserWarning


@pytest.fixture(scope='class')
def user1():
    return User(first_name='Misses Test', id=123, is_bot=False)


@pytest.fixture(scope='class')
def user2():
    return User(first_name='Mister Test', id=124, is_bot=False)


def raise_dphs(func):
    async def decorator(self, *args, **kwargs):
        result = await func(self, *args, **kwargs)
        if self.raise_dp_handler_stop:
            raise ApplicationHandlerStop(result)
        return result

    return decorator


class TestConversationHandler:
    """Persistence of conversations is tested in test_basepersistence.py"""

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
    async def start(self, update, context):
        if isinstance(update, Update):
            return self._set_state(update, self.THIRSTY)
        return self._set_state(context.bot, self.THIRSTY)

    @raise_dphs
    async def end(self, update, context):
        return self._set_state(update, self.END)

    @raise_dphs
    async def start_end(self, update, context):
        return self._set_state(update, self.END)

    @raise_dphs
    async def start_none(self, update, context):
        return self._set_state(update, None)

    @raise_dphs
    async def brew(self, update, context):
        if isinstance(update, Update):
            return self._set_state(update, self.BREWING)
        return self._set_state(context.bot, self.BREWING)

    @raise_dphs
    async def drink(self, update, context):
        return self._set_state(update, self.DRINKING)

    @raise_dphs
    async def code(self, update, context):
        return self._set_state(update, self.CODING)

    @raise_dphs
    async def passout(self, update, context):
        assert update.message.text == '/brew'
        assert isinstance(update, Update)
        self.is_timeout = True

    @raise_dphs
    async def passout2(self, update, context):
        assert isinstance(update, Update)
        self.is_timeout = True

    @raise_dphs
    async def passout_context(self, update, context):
        assert update.message.text == '/brew'
        assert isinstance(context, CallbackContext)
        self.is_timeout = True

    @raise_dphs
    async def passout2_context(self, update, context):
        assert isinstance(context, CallbackContext)
        self.is_timeout = True

    # Drinking actions (nested)

    @raise_dphs
    async def hold(self, update, context):
        return self._set_state(update, self.HOLDING)

    @raise_dphs
    async def sip(self, update, context):
        return self._set_state(update, self.SIPPING)

    @raise_dphs
    async def swallow(self, update, context):
        return self._set_state(update, self.SWALLOWING)

    @raise_dphs
    async def replenish(self, update, context):
        return self._set_state(update, self.REPLENISHING)

    @raise_dphs
    async def stop(self, update, context):
        return self._set_state(update, self.STOPPING)

    def test_slot_behaviour(self, mro_slots):
        handler = ConversationHandler(entry_points=[], states={}, fallbacks=[])
        for attr in handler.__slots__:
            assert getattr(handler, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"

    def test_init(self):
        entry_points = []
        states = {}
        fallbacks = []
        map_to_parent = {}
        ch = ConversationHandler(
            entry_points=entry_points,
            states=states,
            fallbacks=fallbacks,
            per_chat='per_chat',
            per_user='per_user',
            per_message='per_message',
            persistent='persistent',
            name='name',
            allow_reentry='allow_reentry',
            conversation_timeout=42,
            map_to_parent=map_to_parent,
        )
        assert ch.entry_points is entry_points
        assert ch.states is states
        assert ch.fallbacks is fallbacks
        assert ch.map_to_parent is map_to_parent
        assert ch.per_chat == 'per_chat'
        assert ch.per_user == 'per_user'
        assert ch.per_message == 'per_message'
        assert ch.persistent == 'persistent'
        assert ch.name == 'name'
        assert ch.allow_reentry == 'allow_reentry'

    @pytest.mark.asyncio
    async def test_handlers_generate_warning(self, recwarn):
        """this function tests all handler + per_* setting combinations."""

        # the warning message action needs to be set to always,
        # otherwise only the first occurrence will be issued
        filterwarnings(action="always", category=PTBUserWarning)

        # this class doesn't do anything, its just not the Update class
        class NotUpdate:
            pass

        # this conversation handler has the string, string_regex, Pollhandler and TypeHandler
        # which should all generate a warning no matter the per_* setting. TypeHandler should
        # not when the class is Update
        ConversationHandler(
            entry_points=[StringCommandHandler("code", self.code)],
            states={
                self.BREWING: [
                    StringRegexHandler("code", self.code),
                    PollHandler(self.code),
                    TypeHandler(NotUpdate, self.code),
                ],
            },
            fallbacks=[TypeHandler(Update, self.code)],
        )

        # these handlers should all raise a warning when per_chat is True
        ConversationHandler(
            entry_points=[ShippingQueryHandler(self.code)],
            states={
                self.BREWING: [
                    InlineQueryHandler(self.code),
                    PreCheckoutQueryHandler(self.code),
                    PollAnswerHandler(self.code),
                ],
            },
            fallbacks=[ChosenInlineResultHandler(self.code)],
            per_chat=True,
        )

        # the CallbackQueryHandler should *not* raise when per_message is True,
        # but any other one should
        ConversationHandler(
            entry_points=[CallbackQueryHandler(self.code)],
            states={
                self.BREWING: [CommandHandler("code", self.code)],
            },
            fallbacks=[CallbackQueryHandler(self.code)],
            per_message=True,
        )

        # the CallbackQueryHandler should raise when per_message is False
        ConversationHandler(
            entry_points=[CommandHandler("code", self.code)],
            states={
                self.BREWING: [CommandHandler("code", self.code)],
            },
            fallbacks=[CallbackQueryHandler(self.code)],
            per_message=False,
        )

        # adding a nested conv to a conversation with timeout should warn
        child = ConversationHandler(
            entry_points=[CommandHandler("code", self.code)],
            states={
                self.BREWING: [CommandHandler("code", self.code)],
            },
            fallbacks=[CommandHandler("code", self.code)],
        )

        ConversationHandler(
            entry_points=[CommandHandler("code", self.code)],
            states={
                self.BREWING: [child],
            },
            fallbacks=[CommandHandler("code", self.code)],
            conversation_timeout=42,
        )

        # If per_message is True, per_chat should also be True, since msg ids are not unique
        ConversationHandler(
            entry_points=[CallbackQueryHandler(self.code, "code")],
            states={
                self.BREWING: [CallbackQueryHandler(self.code, "code")],
            },
            fallbacks=[CallbackQueryHandler(self.code, "code")],
            per_message=True,
            per_chat=False,
        )

        # the overall number of handlers throwing a warning is 13
        assert len(recwarn) == 13
        # now we test the messages, they are raised in the order they are inserted
        # into the conversation handler
        assert str(recwarn[0].message) == (
            "The `ConversationHandler` only handles updates of type `telegram.Update`. "
            "StringCommandHandler handles updates of type `str`."
        )
        assert str(recwarn[1].message) == (
            "The `ConversationHandler` only handles updates of type `telegram.Update`. "
            "StringRegexHandler handles updates of type `str`."
        )
        assert str(recwarn[2].message) == (
            "PollHandler will never trigger in a conversation since it has no information "
            "about the chat or the user who voted in it. Do you mean the "
            "`PollAnswerHandler`?"
        )
        assert str(recwarn[3].message) == (
            "The `ConversationHandler` only handles updates of type `telegram.Update`. "
            "The TypeHandler is set to handle NotUpdate."
        )

        per_faq_link = (
            " Read this FAQ entry to learn more about the per_* settings: "
            "https://github.com/python-telegram-bot/python-telegram-bot/wiki"
            "/Frequently-Asked-Questions#what-do-the-per_-settings-in-conversationhandler-do."
        )

        assert str(recwarn[4].message) == (
            "Updates handled by ShippingQueryHandler only have information about the user,"
            " so this handler won't ever be triggered if `per_chat=True`." + per_faq_link
        )
        assert str(recwarn[5].message) == (
            "Updates handled by ChosenInlineResultHandler only have information about the user,"
            " so this handler won't ever be triggered if `per_chat=True`." + per_faq_link
        )
        assert str(recwarn[6].message) == (
            "Updates handled by InlineQueryHandler only have information about the user,"
            " so this handler won't ever be triggered if `per_chat=True`." + per_faq_link
        )
        assert str(recwarn[7].message) == (
            "Updates handled by PreCheckoutQueryHandler only have information about the user,"
            " so this handler won't ever be triggered if `per_chat=True`." + per_faq_link
        )
        assert str(recwarn[8].message) == (
            "Updates handled by PollAnswerHandler only have information about the user,"
            " so this handler won't ever be triggered if `per_chat=True`." + per_faq_link
        )
        assert str(recwarn[9].message) == (
            "If 'per_message=True', all entry points, state handlers, and fallbacks must be "
            "'CallbackQueryHandler', since no other handlers have a message context."
            + per_faq_link
        )
        assert str(recwarn[10].message) == (
            "If 'per_message=False', 'CallbackQueryHandler' will not be tracked for "
            "every message." + per_faq_link
        )
        assert str(recwarn[11].message) == (
            "Using `conversation_timeout` with nested conversations is currently not "
            "supported. You can still try to use it, but it will likely behave differently"
            " from what you expect."
        )

        assert str(recwarn[12].message) == (
            "If 'per_message=True' is used, 'per_chat=True' should also be used, "
            "since message IDs are not globally unique."
        )

        # this for loop checks if the correct stacklevel is used when generating the warning
        for warning in recwarn:
            assert warning.filename == __file__, "incorrect stacklevel!"

    @pytest.mark.parametrize(
        'attr',
        [
            'entry_points',
            'states',
            'fallbacks',
            'per_chat',
            'per_user',
            'per_message',
            'name',
            'persistent',
            'allow_reentry',
            'conversation_timeout',
            'map_to_parent',
        ],
        indirect=False,
    )
    def test_immutable(self, attr):
        ch = ConversationHandler(entry_points=[], states={}, fallbacks=[])
        with pytest.raises(AttributeError, match=f'You can not assign a new value to {attr}'):
            setattr(ch, attr, True)

    def test_per_all_false(self):
        with pytest.raises(ValueError, match="can't all be 'False'"):
            ConversationHandler(
                entry_points=[],
                states={},
                fallbacks=[],
                per_chat=False,
                per_user=False,
                per_message=False,
            )

    @pytest.mark.asyncio
    async def test_conversation_handler(self, app, bot, user1, user2):
        handler = ConversationHandler(
            entry_points=self.entry_points, states=self.states, fallbacks=self.fallbacks
        )
        app.add_handler(handler)

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
        async with app:
            await app.process_update(Update(update_id=0, message=message))
            assert self.current_state[user1.id] == self.THIRSTY

            # The user is thirsty and wants to brew coffee.
            message.text = '/brew'
            message.entities[0].length = len('/brew')
            await app.process_update(Update(update_id=0, message=message))
            assert self.current_state[user1.id] == self.BREWING

            # Lets see if an invalid command makes sure, no state is changed.
            message.text = '/nothing'
            message.entities[0].length = len('/nothing')
            await app.process_update(Update(update_id=0, message=message))
            assert self.current_state[user1.id] == self.BREWING

            # Lets see if the state machine still works by pouring coffee.
            message.text = '/pourCoffee'
            message.entities[0].length = len('/pourCoffee')
            await app.process_update(Update(update_id=0, message=message))
            assert self.current_state[user1.id] == self.DRINKING

            # Let's now verify that for another user, who did not start yet,
            # the state has not been changed.
            message.from_user = user2
            await app.process_update(Update(update_id=0, message=message))
            with pytest.raises(KeyError):
                self.current_state[user2.id]

    @pytest.mark.asyncio
    async def test_conversation_handler_end(self, caplog, app, bot, user1):
        handler = ConversationHandler(
            entry_points=self.entry_points, states=self.states, fallbacks=self.fallbacks
        )
        app.add_handler(handler)

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

        async with app:
            await app.process_update(Update(update_id=0, message=message))
            message.text = '/brew'
            message.entities[0].length = len('/brew')
            await app.process_update(Update(update_id=0, message=message))
            message.text = '/pourCoffee'
            message.entities[0].length = len('/pourCoffee')
            await app.process_update(Update(update_id=0, message=message))
            message.text = '/end'
            message.entities[0].length = len('/end')
            caplog.clear()
            with caplog.at_level(logging.ERROR):
                await app.process_update(Update(update_id=0, message=message))
            assert len(caplog.records) == 0
            assert self.current_state[user1.id] == self.END

            # make sure that the conversation has ended by checking that the start command is
            # accepted again
            message.text = '/start'
            message.entities[0].length = len('/start')
            assert handler.check_update(Update(update_id=0, message=message))

    @pytest.mark.asyncio
    async def test_conversation_handler_fallback(self, app, bot, user1, user2):
        handler = ConversationHandler(
            entry_points=self.entry_points, states=self.states, fallbacks=self.fallbacks
        )
        app.add_handler(handler)

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

        async with app:
            await app.process_update(Update(update_id=0, message=message))
            with pytest.raises(KeyError):
                self.current_state[user1.id]

            # User starts the state machine.
            message.text = '/start'
            message.entities[0].length = len('/start')
            await app.process_update(Update(update_id=0, message=message))
            assert self.current_state[user1.id] == self.THIRSTY

            # The user is thirsty and wants to brew coffee.
            message.text = '/brew'
            message.entities[0].length = len('/brew')
            await app.process_update(Update(update_id=0, message=message))
            assert self.current_state[user1.id] == self.BREWING

            # Now a fallback command is issued
            message.text = '/eat'
            message.entities[0].length = len('/eat')
            await app.process_update(Update(update_id=0, message=message))
            assert self.current_state[user1.id] == self.THIRSTY

    @pytest.mark.asyncio
    async def test_unknown_state_warning(self, app, bot, user1, recwarn):
        def build_callback(state):
            async def callback(_, __):
                return state

            return callback

        handler = ConversationHandler(
            entry_points=[CommandHandler("start", build_callback(1))],
            states={
                1: [TypeHandler(Update, build_callback(69))],
                2: [TypeHandler(Update, build_callback(42))],
            },
            fallbacks=self.fallbacks,
            name="xyz",
        )
        app.add_handler(handler)
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
        async with app:
            await app.process_update(Update(update_id=0, message=message))
            try:
                await app.process_update(Update(update_id=1, message=message))
            except Exception as exc:
                print(exc)
                raise exc
            assert len(recwarn) == 1
            assert str(recwarn[0].message) == (
                "Handler returned state 69 which is unknown to the ConversationHandler xyz."
            )

    @pytest.mark.asyncio
    async def test_conversation_handler_per_chat(self, app, bot, user1, user2):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            per_user=False,
        )
        app.add_handler(handler)

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

        async with app:
            await app.process_update(Update(update_id=0, message=message))

            # The user is thirsty and wants to brew coffee.
            message.text = '/brew'
            message.entities[0].length = len('/brew')
            await app.process_update(Update(update_id=0, message=message))

            # Let's now verify that for another user, who did not start yet,
            # the state will be changed because they are in the same group.
            message.from_user = user2
            message.text = '/pourCoffee'
            message.entities[0].length = len('/pourCoffee')
            await app.process_update(Update(update_id=0, message=message))

            # Check that we're in the DRINKING state by checking that the corresponding command
            # is accepted
            message.from_user = user1
            message.text = '/startCoding'
            message.entities[0].length = len('/startCoding')
            assert handler.check_update(Update(update_id=0, message=message))
            message.from_user = user2
            assert handler.check_update(Update(update_id=0, message=message))

    @pytest.mark.asyncio
    async def test_conversation_handler_per_user(self, app, bot, user1):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            per_chat=False,
        )
        app.add_handler(handler)

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
        async with app:
            await app.process_update(Update(update_id=0, message=message))

            # The user is thirsty and wants to brew coffee.
            message.text = '/brew'
            message.entities[0].length = len('/brew')
            await app.process_update(Update(update_id=0, message=message))

            # Let's now verify that for the same user in a different group, the state will still be
            # updated
            message.chat = self.second_group
            message.text = '/pourCoffee'
            message.entities[0].length = len('/pourCoffee')
            await app.process_update(Update(update_id=0, message=message))

            # Check that we're in the DRINKING state by checking that the corresponding command
            # is accepted
            message.chat = self.group
            message.text = '/startCoding'
            message.entities[0].length = len('/startCoding')
            assert handler.check_update(Update(update_id=0, message=message))
            message.chat = self.second_group
            assert handler.check_update(Update(update_id=0, message=message))

    @pytest.mark.asyncio
    async def test_conversation_handler_per_message(self, app, bot, user1, user2):
        async def entry(update, context):
            return 1

        async def one(update, context):
            return 2

        async def two(update, context):
            return ConversationHandler.END

        handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(entry)],
            states={
                1: [CallbackQueryHandler(one, pattern='^1$')],
                2: [CallbackQueryHandler(two, pattern='^2$')],
            },
            fallbacks=[],
            per_message=True,
        )
        app.add_handler(handler)

        # User one, starts the state machine.
        message = Message(
            0, None, self.group, from_user=user1, text='msg w/ inlinekeyboard', bot=bot
        )

        async with app:
            cbq_1 = CallbackQuery(0, user1, None, message=message, data='1', bot=bot)
            cbq_2 = CallbackQuery(0, user1, None, message=message, data='2', bot=bot)
            await app.process_update(Update(update_id=0, callback_query=cbq_1))

            # Make sure that we're in the correct state
            assert handler.check_update(Update(0, callback_query=cbq_1))
            assert not handler.check_update(Update(0, callback_query=cbq_2))

            await app.process_update(Update(update_id=0, callback_query=cbq_1))

            # Make sure that we're in the correct state
            assert not handler.check_update(Update(0, callback_query=cbq_1))
            assert handler.check_update(Update(0, callback_query=cbq_2))

            # Let's now verify that for a different user in the same group, the state will not be
            # updated
            cbq_2.from_user = user2
            await app.process_update(Update(update_id=0, callback_query=cbq_2))

            cbq_2.from_user = user1
            assert not handler.check_update(Update(0, callback_query=cbq_1))
            assert handler.check_update(Update(0, callback_query=cbq_2))

    @pytest.mark.asyncio
    async def test_end_on_first_message(self, app, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_end)], states={}, fallbacks=[]
        )
        app.add_handler(handler)

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
        async with app:
            await app.process_update(Update(update_id=0, message=message))
            assert handler.check_update(Update(update_id=0, message=message))

    @pytest.mark.asyncio
    async def test_end_on_first_message_non_blocking_handler(self, app, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', callback=self.start_end, block=False)],
            states={},
            fallbacks=[],
        )
        app.add_handler(handler)

        # User starts the state machine with a non-blocking function that immediately ends the
        # conversation. non-blocking results are resolved when the users state is queried next
        # time.
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
        async with app:
            await app.process_update(Update(update_id=0, message=message))
            # give the task a chance to finish
            await asyncio.sleep(0.1)

            # Let's check that processing the same update again is accepted. this confirms that
            # a) the pending state is correctly resolved
            # b) the conversation has ended
            assert handler.check_update(Update(0, message=message))

    @pytest.mark.asyncio
    async def test_none_on_first_message(self, app, bot, user1):
        handler = ConversationHandler(
            entry_points=[MessageHandler(filters.ALL, self.start_none)], states={}, fallbacks=[]
        )
        app.add_handler(handler)

        # User starts the state machine and a callback function returns None
        message = Message(0, None, self.group, from_user=user1, text='/start', bot=bot)
        async with app:
            await app.process_update(Update(update_id=0, message=message))
            # Check that the same message is accepted again, i.e. the conversation immediately
            # ended
            assert handler.check_update(Update(0, message=message))

    # TODO
    # @pytest.mark.asyncio
    # async def test_none_on_first_message_async(self, app, bot, user1):
    #     handler = ConversationHandler(
    #         entry_points=[
    #             CommandHandler(
    #                 'start', lambda update, context: app.run_async(self.start_none, update,
    #                 context)
    #             )
    #         ],
    #         states={},
    #         fallbacks=[],
    #     )
    #     app.add_handler(handler)
    #
    #     # User starts the state machine with an async function that returns None
    #     # Async results are resolved when the users state is queried next time.
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     app.update_queue.put(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.1)
    #     # Assert that the Promise has been accepted as the new state
    #     assert len(handler.conversations) == 1
    #
    #     message.text = 'resolve promise pls'
    #     app.update_queue.put(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.1)
    #     # Assert that the Promise has been resolved and the conversation ended.
    #     assert len(handler.conversations) == 0
    #
    # @pytest.mark.asyncio
    # async def test_none_on_first_message_async_handler(self, app, bot, user1):
    #     handler = ConversationHandler(
    #         entry_points=[CommandHandler('start', self.start_none, run_async=True)],
    #         states={},
    #         fallbacks=[],
    #     )
    #     app.add_handler(handler)
    #
    #     # User starts the state machine with an async function that returns None
    #     # Async results are resolved when the users state is queried next time.
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         text='/start',
    #         from_user=user1,
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     app.update_queue.put(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.1)
    #     # Assert that the Promise has been accepted as the new state
    #     assert len(handler.conversations) == 1
    #
    #     message.text = 'resolve promise pls'
    #     app.update_queue.put(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.1)
    #     # Assert that the Promise has been resolved and the conversation ended.
    #     assert len(handler.conversations) == 0

    @pytest.mark.asyncio
    async def test_per_chat_message_without_chat(self, bot, user1):
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_end)], states={}, fallbacks=[]
        )
        cbq = CallbackQuery(0, user1, None, None, bot=bot)
        update = Update(0, callback_query=cbq)
        assert not handler.check_update(update)

    @pytest.mark.asyncio
    async def test_channel_message_without_chat(self, bot):
        handler = ConversationHandler(
            entry_points=[MessageHandler(filters.ALL, self.start_end)], states={}, fallbacks=[]
        )
        message = Message(0, date=None, chat=Chat(0, Chat.CHANNEL, 'Misses Test'), bot=bot)

        update = Update(0, channel_post=message)
        assert not handler.check_update(update)

        update = Update(0, edited_channel_post=message)
        assert not handler.check_update(update)

    @pytest.mark.asyncio
    async def test_all_update_types(self, app, bot, user1):
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

    @pytest.mark.asyncio
    async def test_no_job_queue_warning(self, app, bot, user1, recwarn):
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            conversation_timeout=0.5,
        )
        # save app.job_queue in temp variable jqueue
        # and then set app.job_queue to None.
        jqueue = app.job_queue
        app.job_queue = None
        app.add_handler(handler)

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

        async with app:
            await app.process_update(Update(update_id=0, message=message))
            await asyncio.sleep(0.5)
            assert len(recwarn) == 1
            assert (
                str(recwarn[0].message)
                == "Ignoring `conversation_timeout` because the Application has no JobQueue."
            )
            # now set app.job_queue back to it's original value
            app.job_queue = jqueue

    @pytest.mark.asyncio
    async def test_schedule_job_exception(self, app, bot, user1, monkeypatch, caplog):
        def mocked_run_once(*a, **kw):
            raise Exception("job error")

        class DictJB(JobQueue):
            pass

        app.job_queue = DictJB()
        monkeypatch.setattr(app.job_queue, "run_once", mocked_run_once)
        handler = ConversationHandler(
            entry_points=self.entry_points,
            states=self.states,
            fallbacks=self.fallbacks,
            conversation_timeout=100,
        )
        app.add_handler(handler)

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

        async with app:
            with caplog.at_level(logging.ERROR):
                await app.process_update(Update(update_id=0, message=message))
                await asyncio.sleep(0.5)

            assert len(caplog.records) == 1
            assert caplog.records[0].message == "Failed to schedule timeout."
            assert str(caplog.records[0].exc_info[1]) == "job error"

    # @pytest.mark.asyncio
    # async def test_promise_exception(self, app, bot, user1, caplog):
    #     """
    #     Here we make sure that when a run_async handle raises an
    #     exception, the state isn't changed.
    #     """
    #
    #     def conv_entry(*a, **kw):
    #         return 1
    #
    #     def raise_error(*a, **kw):
    #         raise Exception("promise exception")
    #
    #     handler = ConversationHandler(
    #         entry_points=[CommandHandler("start", conv_entry)],
    #         states={1: [MessageHandler(filters.ALL, raise_error)]},
    #         fallbacks=self.fallbacks,
    #         run_async=True,
    #     )
    #     app.add_handler(handler)
    #
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     # start the conversation
    #     await app.process_update(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.1)
    #     message.text = "error"
    #     await app.process_update(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.1)
    #     message.text = "resolve promise pls"
    #     caplog.clear()
    #     with caplog.at_level(logging.ERROR):
    #         await app.process_update(Update(update_id=0, message=message))
    #         await asyncio.sleep(0.5)
    #     assert len(caplog.records) == 3
    #     assert caplog.records[0].message == "Promise function raised exception"
    #     assert caplog.records[1].message == "promise exception"
    #     # assert res is old state
    #     assert handler.conversations.get((self.group.id, user1.id))[0] == 1
    #
    # @pytest.mark.asyncio
    # async def test_conversation_timeout(self, app, bot, user1):
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points,
    #         states=self.states,
    #         fallbacks=self.fallbacks,
    #         conversation_timeout=0.5,
    #     )
    #     app.add_handler(handler)
    #
    #     # Start state machine, then reach timeout
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
    #     await asyncio.sleep(0.75)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #
    #     # Start state machine, do something, then reach timeout
    #     await app.process_update(Update(update_id=1, message=message))
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     await app.process_update(Update(update_id=2, message=message))
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.BREWING
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #
    # @pytest.mark.asyncio
    # async def test_timeout_not_triggered_on_conv_end_async(self, bot, app, user1):
    #     def timeout(*a, **kw):
    #         self.test_flag = True
    #
    #     self.states.update({ConversationHandler.TIMEOUT: [TypeHandler(Update, timeout)]})
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points,
    #         states=self.states,
    #         fallbacks=self.fallbacks,
    #         conversation_timeout=0.5,
    #         run_async=True,
    #     )
    #     app.add_handler(handler)
    #
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     # start the conversation
    #     await app.process_update(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.1)
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     await app.process_update(Update(update_id=1, message=message))
    #     await asyncio.sleep(0.1)
    #     message.text = '/pourCoffee'
    #     message.entities[0].length = len('/pourCoffee')
    #     await app.process_update(Update(update_id=2, message=message))
    #     await asyncio.sleep(0.1)
    #     message.text = '/end'
    #     message.entities[0].length = len('/end')
    #     await app.process_update(Update(update_id=3, message=message))
    #     await asyncio.sleep(1)
    #     # assert timeout handler didn't got called
    #     assert self.test_flag is False
    #
    # @pytest.mark.asyncio
    # async def test_conversation_timeout_dispatcher_handler_stop(self, app, bot, user1, recwarn):
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points,
    #         states=self.states,
    #         fallbacks=self.fallbacks,
    #         conversation_timeout=0.5,
    #     )
    #
    #     def timeout(*args, **kwargs):
    #         raise DispatcherHandlerStop()
    #
    #     self.states.update({ConversationHandler.TIMEOUT: [TypeHandler(Update, timeout)]})
    #     app.add_handler(handler)
    #
    #     # Start state machine, then reach timeout
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         text='/start',
    #         from_user=user1,
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
    #     await asyncio.sleep(0.9)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert len(recwarn) == 1
    #     assert str(recwarn[0].message).startswith('DispatcherHandlerStop in TIMEOUT')
    #
    # @pytest.mark.asyncio
    # async def test_conversation_handler_timeout_update_and_context(self, app, bot, user1):
    #     context = None
    #
    #     def start_callback(u, c):
    #         nonlocal context, self
    #         context = c
    #         return self.start(u, c)
    #
    #     states = self.states
    #     timeout_handler = CommandHandler('start', None)
    #     states.update({ConversationHandler.TIMEOUT: [timeout_handler]})
    #     handler = ConversationHandler(
    #         entry_points=[CommandHandler('start', start_callback)],
    #         states=states,
    #         fallbacks=self.fallbacks,
    #         conversation_timeout=0.5,
    #     )
    #     app.add_handler(handler)
    #
    #     # Start state machine, then reach timeout
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     update = Update(update_id=0, message=message)
    #
    #     def timeout_callback(u, c):
    #         nonlocal update, context, self
    #         self.is_timeout = True
    #         assert u is update
    #         assert c is context
    #
    #     timeout_handler.callback = timeout_callback
    #
    #     await app.process_update(update)
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert self.is_timeout
    #
    # @flaky(3, 1)
    # @pytest.mark.asyncio
    # async def test_conversation_timeout_keeps_extending(self, app, bot, user1):
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points,
    #         states=self.states,
    #         fallbacks=self.fallbacks,
    #         conversation_timeout=0.5,
    #     )
    #     app.add_handler(handler)
    #
    #     # Start state machine, wait, do something, verify the timeout is extended.
    #     # t=0 /start (timeout=.5)
    #     # t=.35 /brew (timeout=.85)
    #     # t=.5 original timeout
    #     # t=.6 /pourCoffee (timeout=1.1)
    #     # t=.85 second timeout
    #     # t=1.1 actual timeout
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
    #     await asyncio.sleep(0.35)  # t=.35
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.BREWING
    #     await asyncio.sleep(0.25)  # t=.6
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.BREWING
    #     message.text = '/pourCoffee'
    #     message.entities[0].length = len('/pourCoffee')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.DRINKING
    #     await asyncio.sleep(0.4)  # t=1.0
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.DRINKING
    #     await asyncio.sleep(0.3)  # t=1.3
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #
    # @pytest.mark.asyncio
    # async def test_conversation_timeout_two_users(self, app, bot, user1, user2):
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points,
    #         states=self.states,
    #         fallbacks=self.fallbacks,
    #         conversation_timeout=0.5,
    #     )
    #     app.add_handler(handler)
    #
    #     # Start state machine, do something as second user, then reach timeout
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert handler.conversations.get((self.group.id, user1.id)) == self.THIRSTY
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     message.entities[0].length = len('/brew')
    #     message.from_user = user2
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert handler.conversations.get((self.group.id, user2.id)) is None
    #     message.text = '/start'
    #     message.entities[0].length = len('/start')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert handler.conversations.get((self.group.id, user2.id)) == self.THIRSTY
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert handler.conversations.get((self.group.id, user2.id)) is None
    #
    # @pytest.mark.asyncio
    # async def test_conversation_handler_timeout_state(self, app, bot, user1):
    #     states = self.states
    #     states.update(
    #         {
    #             ConversationHandler.TIMEOUT: [
    #                 CommandHandler('brew', self.passout),
    #                 MessageHandler(~filters.Regex('oding'), self.passout2),
    #             ]
    #         }
    #     )
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points,
    #         states=states,
    #         fallbacks=self.fallbacks,
    #         conversation_timeout=0.5,
    #     )
    #     app.add_handler(handler)
    #
    #     # CommandHandler timeout
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     await app.process_update(Update(update_id=0, message=message))
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     await app.process_update(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert self.is_timeout
    #
    #     # MessageHandler timeout
    #     self.is_timeout = False
    #     message.text = '/start'
    #     message.entities[0].length = len('/start')
    #     await app.process_update(Update(update_id=1, message=message))
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert self.is_timeout
    #
    #     # Timeout but no valid handler
    #     self.is_timeout = False
    #     await app.process_update(Update(update_id=0, message=message))
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     await app.process_update(Update(update_id=0, message=message))
    #     message.text = '/startCoding'
    #     message.entities[0].length = len('/startCoding')
    #     await app.process_update(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert not self.is_timeout
    #
    # @pytest.mark.asyncio
    # async def test_conversation_handler_timeout_state_context(self, app, bot, user1):
    #     states = self.states
    #     states.update(
    #         {
    #             ConversationHandler.TIMEOUT: [
    #                 CommandHandler('brew', self.passout_context),
    #                 MessageHandler(~filters.Regex('oding'), self.passout2_context),
    #             ]
    #         }
    #     )
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points,
    #         states=states,
    #         fallbacks=self.fallbacks,
    #         conversation_timeout=0.5,
    #     )
    #     app.add_handler(handler)
    #
    #     # CommandHandler timeout
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     await app.process_update(Update(update_id=0, message=message))
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     await app.process_update(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert self.is_timeout
    #
    #     # MessageHandler timeout
    #     self.is_timeout = False
    #     message.text = '/start'
    #     message.entities[0].length = len('/start')
    #     await app.process_update(Update(update_id=1, message=message))
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert self.is_timeout
    #
    #     # Timeout but no valid handler
    #     self.is_timeout = False
    #     await app.process_update(Update(update_id=0, message=message))
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     await app.process_update(Update(update_id=0, message=message))
    #     message.text = '/startCoding'
    #     message.entities[0].length = len('/startCoding')
    #     await app.process_update(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert not self.is_timeout
    #
    # @pytest.mark.asyncio
    # async def test_conversation_timeout_cancel_conflict(self, app, bot, user1):
    #     # Start state machine, wait half the timeout,
    #     # then call a callback that takes more than the timeout
    #     # t=0 /start (timeout=.5)
    #     # t=.25 /slowbrew (sleep .5)
    #     # |  t=.5 original timeout (should not execute)
    #     # |  t=.75 /slowbrew returns (timeout=1.25)
    #     # t=1.25 timeout
    #
    #     def slowbrew(_update, context):
    #         await asyncio.sleep(0.25)
    #         # Let's give to the original timeout a chance to execute
    #         await asyncio.sleep(0.25)
    #         # By returning None we do not override the conversation state so
    #         # we can see if the timeout has been executed
    #
    #     states = self.states
    #     states[self.THIRSTY].append(CommandHandler('slowbrew', slowbrew))
    #     states.update({ConversationHandler.TIMEOUT: [MessageHandler(None, self.passout2)]})
    #
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points,
    #         states=states,
    #         fallbacks=self.fallbacks,
    #         conversation_timeout=0.5,
    #     )
    #     app.add_handler(handler)
    #
    #     # CommandHandler timeout
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #         bot=bot,
    #     )
    #     await app.process_update(Update(update_id=0, message=message))
    #     await asyncio.sleep(0.25)
    #     message.text = '/slowbrew'
    #     message.entities[0].length = len('/slowbrew')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert handler.conversations.get((self.group.id, user1.id)) is not None
    #     assert not self.is_timeout
    #
    #     await asyncio.sleep(0.7)
    #     assert handler.conversations.get((self.group.id, user1.id)) is None
    #     assert self.is_timeout
    #
    # @pytest.mark.asyncio
    # async def test_nested_conversation_handler(self, app, bot, user1, user2):
    #     self.nested_states[self.DRINKING] = [
    #         ConversationHandler(
    #             entry_points=self.drinking_entry_points,
    #             states=self.drinking_states,
    #             fallbacks=self.drinking_fallbacks,
    #             map_to_parent=self.drinking_map_to_parent,
    #         )
    #     ]
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points, states=self.nested_states, fallbacks=self.fallbacks
    #     )
    #     app.add_handler(handler)
    #
    #     # User one, starts the state machine.
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         from_user=user1,
    #         text='/start',
    #         bot=bot,
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #     )
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.THIRSTY
    #
    #     # The user is thirsty and wants to brew coffee.
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.BREWING
    #
    #     # Lets pour some coffee.
    #     message.text = '/pourCoffee'
    #     message.entities[0].length = len('/pourCoffee')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.DRINKING
    #
    #     # The user is holding the cup
    #     message.text = '/hold'
    #     message.entities[0].length = len('/hold')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.HOLDING
    #
    #     # The user is sipping coffee
    #     message.text = '/sip'
    #     message.entities[0].length = len('/sip')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.SIPPING
    #
    #     # The user is swallowing
    #     message.text = '/swallow'
    #     message.entities[0].length = len('/swallow')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.SWALLOWING
    #
    #     # The user is holding the cup again
    #     message.text = '/hold'
    #     message.entities[0].length = len('/hold')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.HOLDING
    #
    #     # The user wants to replenish the coffee supply
    #     message.text = '/replenish'
    #     message.entities[0].length = len('/replenish')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.REPLENISHING
    #     assert handler.conversations[(0, user1.id)] == self.BREWING
    #
    #     # The user wants to drink their coffee again
    #     message.text = '/pourCoffee'
    #     message.entities[0].length = len('/pourCoffee')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.DRINKING
    #
    #     # The user is now ready to start coding
    #     message.text = '/startCoding'
    #     message.entities[0].length = len('/startCoding')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.CODING
    #
    #     # The user decides it's time to drink again
    #     message.text = '/drinkMore'
    #     message.entities[0].length = len('/drinkMore')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.DRINKING
    #
    #     # The user is holding their cup
    #     message.text = '/hold'
    #     message.entities[0].length = len('/hold')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.HOLDING
    #
    #     # The user wants to end with the drinking and go back to coding
    #     message.text = '/end'
    #     message.entities[0].length = len('/end')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.END
    #     assert handler.conversations[(0, user1.id)] == self.CODING
    #
    #     # The user wants to drink once more
    #     message.text = '/drinkMore'
    #     message.entities[0].length = len('/drinkMore')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.DRINKING
    #
    #     # The user wants to stop altogether
    #     message.text = '/stop'
    #     message.entities[0].length = len('/stop')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.STOPPING
    #     assert handler.conversations.get((0, user1.id)) is None
    #
    # @pytest.mark.asyncio
    # async def test_conversation_dispatcher_handler_stop(self, app, bot, user1, user2):
    #     self.nested_states[self.DRINKING] = [
    #         ConversationHandler(
    #             entry_points=self.drinking_entry_points,
    #             states=self.drinking_states,
    #             fallbacks=self.drinking_fallbacks,
    #             map_to_parent=self.drinking_map_to_parent,
    #         )
    #     ]
    #     handler = ConversationHandler(
    #         entry_points=self.entry_points, states=self.nested_states, fallbacks=self.fallbacks
    #     )
    #
    #     def test_callback(u, c):
    #         self.test_flag = True
    #
    #     app.add_handler(handler)
    #     app.add_handler(TypeHandler(Update, test_callback), group=1)
    #     self.raise_dp_handler_stop = True
    #
    #     # User one, starts the state machine.
    #     message = Message(
    #         0,
    #         None,
    #         self.group,
    #         text='/start',
    #         bot=bot,
    #         from_user=user1,
    #         entities=[
    #             MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #         ],
    #     )
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.THIRSTY
    #     assert not self.test_flag
    #
    #     # The user is thirsty and wants to brew coffee.
    #     message.text = '/brew'
    #     message.entities[0].length = len('/brew')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.BREWING
    #     assert not self.test_flag
    #
    #     # Lets pour some coffee.
    #     message.text = '/pourCoffee'
    #     message.entities[0].length = len('/pourCoffee')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.DRINKING
    #     assert not self.test_flag
    #
    #     # The user is holding the cup
    #     message.text = '/hold'
    #     message.entities[0].length = len('/hold')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.HOLDING
    #     assert not self.test_flag
    #
    #     # The user is sipping coffee
    #     message.text = '/sip'
    #     message.entities[0].length = len('/sip')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.SIPPING
    #     assert not self.test_flag
    #
    #     # The user is swallowing
    #     message.text = '/swallow'
    #     message.entities[0].length = len('/swallow')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.SWALLOWING
    #     assert not self.test_flag
    #
    #     # The user is holding the cup again
    #     message.text = '/hold'
    #     message.entities[0].length = len('/hold')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.HOLDING
    #     assert not self.test_flag
    #
    #     # The user wants to replenish the coffee supply
    #     message.text = '/replenish'
    #     message.entities[0].length = len('/replenish')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.REPLENISHING
    #     assert handler.conversations[(0, user1.id)] == self.BREWING
    #     assert not self.test_flag
    #
    #     # The user wants to drink their coffee again
    #     message.text = '/pourCoffee'
    #     message.entities[0].length = len('/pourCoffee')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.DRINKING
    #     assert not self.test_flag
    #
    #     # The user is now ready to start coding
    #     message.text = '/startCoding'
    #     message.entities[0].length = len('/startCoding')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.CODING
    #     assert not self.test_flag
    #
    #     # The user decides it's time to drink again
    #     message.text = '/drinkMore'
    #     message.entities[0].length = len('/drinkMore')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.DRINKING
    #     assert not self.test_flag
    #
    #     # The user is holding their cup
    #     message.text = '/hold'
    #     message.entities[0].length = len('/hold')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.HOLDING
    #     assert not self.test_flag
    #
    #     # The user wants to end with the drinking and go back to coding
    #     message.text = '/end'
    #     message.entities[0].length = len('/end')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.END
    #     assert handler.conversations[(0, user1.id)] == self.CODING
    #     assert not self.test_flag
    #
    #     # The user wants to drink once more
    #     message.text = '/drinkMore'
    #     message.entities[0].length = len('/drinkMore')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.DRINKING
    #     assert not self.test_flag
    #
    #     # The user wants to stop altogether
    #     message.text = '/stop'
    #     message.entities[0].length = len('/stop')
    #     await app.process_update(Update(update_id=0, message=message))
    #     assert self.current_state[user1.id] == self.STOPPING
    #     assert handler.conversations.get((0, user1.id)) is None
    #     assert not self.test_flag
    #
    # @pytest.mark.asyncio
    # async def test_conversation_handler_run_async_true(self, app):
    #     conv_handler = ConversationHandler(
    #         entry_points=self.entry_points,
    #         states=self.states,
    #         fallbacks=self.fallbacks,
    #         run_async=True,
    #     )
    #
    #     all_handlers = conv_handler.entry_points + conv_handler.fallbacks
    #     for state_handlers in conv_handler.states.values():
    #         all_handlers += state_handlers
    #
    #     for handler in all_handlers:
    #         assert handler.run_async
    #
    # @pytest.mark.asyncio
    # async def test_conversation_handler_run_async_false(self, app):
    #     conv_handler = ConversationHandler(
    #         entry_points=[CommandHandler('start', self.start_end, run_async=True)],
    #         states=self.states,
    #         fallbacks=self.fallbacks,
    #         run_async=False,
    #     )
    #
    #     for handler in conv_handler.entry_points:
    #         assert handler.run_async
    #
    #     all_handlers = conv_handler.fallbacks
    #     for state_handlers in conv_handler.states.values():
    #         all_handlers += state_handlers
    #
    #     for handler in all_handlers:
    #         assert not handler.run_async.value
