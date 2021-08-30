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
import re
from queue import Queue

import pytest

from telegram import (
    Message,
    Update,
    Chat,
    Bot,
    User,
    CallbackQuery,
    InlineQuery,
    ChosenInlineResult,
    ShippingQuery,
    PreCheckoutQuery,
)
from telegram.ext import Filters, MessageHandler, CallbackContext, JobQueue, UpdateFilter

message = Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Text')

params = [
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
    {'inline_query': InlineQuery(1, User(1, '', False), '', '')},
    {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
    {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
    {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')},
]

ids = (
    'callback_query',
    'inline_query',
    'chosen_inline_result',
    'shipping_query',
    'pre_checkout_query',
    'callback_query_without_message',
)


@pytest.fixture(scope='class', params=params, ids=ids)
def false_update(request):
    return Update(update_id=1, **request.param)


@pytest.fixture(scope='class')
def message(bot):
    return Message(1, None, Chat(1, ''), from_user=User(1, '', False), bot=bot)


class TestMessageHandler:
    test_flag = False
    SRE_TYPE = type(re.match("", ""))

    def test_slot_behaviour(self, mro_slots):
        handler = MessageHandler(Filters.all, self.callback_context)
        for attr in handler.__slots__:
            assert getattr(handler, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def callback_context(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, Update)
            and isinstance(context.update_queue, Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.chat_data, dict)
            and isinstance(context.bot_data, dict)
            and (
                (
                    isinstance(context.user_data, dict)
                    and (
                        isinstance(update.message, Message)
                        or isinstance(update.edited_message, Message)
                    )
                )
                or (
                    context.user_data is None
                    and (
                        isinstance(update.channel_post, Message)
                        or isinstance(update.edited_channel_post, Message)
                    )
                )
            )
        )

    def callback_context_regex1(self, update, context):
        if context.matches:
            types = all(type(res) is self.SRE_TYPE for res in context.matches)
            num = len(context.matches) == 1
            self.test_flag = types and num

    def callback_context_regex2(self, update, context):
        if context.matches:
            types = all(type(res) is self.SRE_TYPE for res in context.matches)
            num = len(context.matches) == 2
            self.test_flag = types and num

    def test_with_filter(self, message):
        handler = MessageHandler(Filters.chat_type.group, self.callback_context)

        message.chat.type = 'group'
        assert handler.check_update(Update(0, message))

        message.chat.type = 'private'
        assert not handler.check_update(Update(0, message))

    def test_callback_query_with_filter(self, message):
        class TestFilter(UpdateFilter):
            flag = False

            def filter(self, u):
                self.flag = True

        test_filter = TestFilter()
        handler = MessageHandler(test_filter, self.callback_context)

        update = Update(1, callback_query=CallbackQuery(1, None, None, message=message))

        assert update.effective_message
        assert not handler.check_update(update)
        assert not test_filter.flag

    def test_specific_filters(self, message):
        f = (
            ~Filters.update.messages
            & ~Filters.update.channel_post
            & Filters.update.edited_channel_post
        )
        handler = MessageHandler(f, self.callback_context)

        assert not handler.check_update(Update(0, edited_message=message))
        assert not handler.check_update(Update(0, message=message))
        assert not handler.check_update(Update(0, channel_post=message))
        assert handler.check_update(Update(0, edited_channel_post=message))

    def test_other_update_types(self, false_update):
        handler = MessageHandler(None, self.callback_context)
        assert not handler.check_update(false_update)

    def test_context(self, dp, message):
        handler = MessageHandler(
            None,
            self.callback_context,
        )
        dp.add_handler(handler)

        dp.process_update(Update(0, message=message))
        assert self.test_flag

        self.test_flag = False
        dp.process_update(Update(0, edited_message=message))
        assert self.test_flag

        self.test_flag = False
        dp.process_update(Update(0, channel_post=message))
        assert self.test_flag

        self.test_flag = False
        dp.process_update(Update(0, edited_channel_post=message))
        assert self.test_flag

    def test_context_regex(self, dp, message):
        handler = MessageHandler(Filters.regex('one two'), self.callback_context_regex1)
        dp.add_handler(handler)

        message.text = 'not it'
        dp.process_update(Update(0, message))
        assert not self.test_flag

        message.text += ' one two now it is'
        dp.process_update(Update(0, message))
        assert self.test_flag

    def test_context_multiple_regex(self, dp, message):
        handler = MessageHandler(
            Filters.regex('one') & Filters.regex('two'), self.callback_context_regex2
        )
        dp.add_handler(handler)

        message.text = 'not it'
        dp.process_update(Update(0, message))
        assert not self.test_flag

        message.text += ' one two now it is'
        dp.process_update(Update(0, message))
        assert self.test_flag
