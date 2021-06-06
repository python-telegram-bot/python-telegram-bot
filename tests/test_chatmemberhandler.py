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
import time
from queue import Queue

import pytest

from telegram import (
    Update,
    Bot,
    Message,
    User,
    Chat,
    CallbackQuery,
    ChosenInlineResult,
    ShippingQuery,
    PreCheckoutQuery,
    ChatMemberUpdated,
    ChatMember,
)
from telegram.ext import CallbackContext, JobQueue, ChatMemberHandler
from telegram.utils.helpers import from_timestamp

message = Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Text')

params = [
    {'message': message},
    {'edited_message': message},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
    {'channel_post': message},
    {'edited_channel_post': message},
    {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
    {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
    {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')},
]

ids = (
    'message',
    'edited_message',
    'callback_query',
    'channel_post',
    'edited_channel_post',
    'chosen_inline_result',
    'shipping_query',
    'pre_checkout_query',
    'callback_query_without_message',
)


@pytest.fixture(scope='class', params=params, ids=ids)
def false_update(request):
    return Update(update_id=2, **request.param)


@pytest.fixture(scope='class')
def chat_member_updated():
    return ChatMemberUpdated(
        Chat(1, 'chat'),
        User(1, '', False),
        from_timestamp(int(time.time())),
        ChatMember(User(1, '', False), ChatMember.CREATOR),
        ChatMember(User(1, '', False), ChatMember.CREATOR),
    )


@pytest.fixture(scope='function')
def chat_member(bot, chat_member_updated):
    return Update(0, my_chat_member=chat_member_updated)


class TestChatMemberHandler:
    test_flag = False

    def test_slot_behaviour(self, recwarn, mro_slots):
        action = ChatMemberHandler(self.callback_basic)
        for attr in action.__slots__:
            assert getattr(action, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not action.__dict__, f"got missing slot(s): {action.__dict__}"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"
        action.custom = 'should give warning'
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def callback_basic(self, bot, update):
        test_bot = isinstance(bot, Bot)
        test_update = isinstance(update, Update)
        self.test_flag = test_bot and test_update

    def callback_data_1(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) or (chat_data is not None)

    def callback_data_2(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) and (chat_data is not None)

    def callback_queue_1(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) or (update_queue is not None)

    def callback_queue_2(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) and (update_queue is not None)

    def callback_context(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, Update)
            and isinstance(context.update_queue, Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.user_data, dict)
            and isinstance(context.chat_data, dict)
            and isinstance(context.bot_data, dict)
            and isinstance(update.chat_member or update.my_chat_member, ChatMemberUpdated)
        )

    def test_basic(self, dp, chat_member):
        handler = ChatMemberHandler(self.callback_basic)
        dp.add_handler(handler)

        assert handler.check_update(chat_member)

        dp.process_update(chat_member)
        assert self.test_flag

    @pytest.mark.parametrize(
        argnames=['allowed_types', 'expected'],
        argvalues=[
            (ChatMemberHandler.MY_CHAT_MEMBER, (True, False)),
            (ChatMemberHandler.CHAT_MEMBER, (False, True)),
            (ChatMemberHandler.ANY_CHAT_MEMBER, (True, True)),
        ],
        ids=['MY_CHAT_MEMBER', 'CHAT_MEMBER', 'ANY_CHAT_MEMBER'],
    )
    def test_chat_member_types(
        self, dp, chat_member_updated, chat_member, expected, allowed_types
    ):
        result_1, result_2 = expected

        handler = ChatMemberHandler(self.callback_basic, chat_member_types=allowed_types)
        dp.add_handler(handler)

        assert handler.check_update(chat_member) == result_1
        dp.process_update(chat_member)
        assert self.test_flag == result_1

        self.test_flag = False
        chat_member.my_chat_member = None
        chat_member.chat_member = chat_member_updated

        assert handler.check_update(chat_member) == result_2
        dp.process_update(chat_member)
        assert self.test_flag == result_2

    def test_pass_user_or_chat_data(self, dp, chat_member):
        handler = ChatMemberHandler(self.callback_data_1, pass_user_data=True)
        dp.add_handler(handler)

        dp.process_update(chat_member)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = ChatMemberHandler(self.callback_data_1, pass_chat_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(chat_member)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = ChatMemberHandler(self.callback_data_2, pass_chat_data=True, pass_user_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(chat_member)
        assert self.test_flag

    def test_pass_job_or_update_queue(self, dp, chat_member):
        handler = ChatMemberHandler(self.callback_queue_1, pass_job_queue=True)
        dp.add_handler(handler)

        dp.process_update(chat_member)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = ChatMemberHandler(self.callback_queue_1, pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(chat_member)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = ChatMemberHandler(
            self.callback_queue_2, pass_job_queue=True, pass_update_queue=True
        )
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(chat_member)
        assert self.test_flag

    def test_other_update_types(self, false_update):
        handler = ChatMemberHandler(self.callback_basic)
        assert not handler.check_update(false_update)
        assert not handler.check_update(True)

    def test_context(self, cdp, chat_member):
        handler = ChatMemberHandler(self.callback_context)
        cdp.add_handler(handler)

        cdp.process_update(chat_member)
        assert self.test_flag
