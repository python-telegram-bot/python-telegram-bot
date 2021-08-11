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
import re
from queue import Queue

import pytest
import itertools
from telegram.utils.deprecate import TelegramDeprecationWarning

from telegram import Message, Update, Chat, Bot
from telegram.ext import CommandHandler, Filters, CallbackContext, JobQueue, PrefixHandler
from tests.conftest import (
    make_command_message,
    make_command_update,
    make_message,
    make_message_update,
)


def is_match(handler, update):
    """
    Utility function that returns whether an update matched
    against a specific handler.
    :param handler: ``CommandHandler`` to check against
    :param update: update to check
    :return: (bool) whether ``update`` matched with ``handler``
    """
    check = handler.check_update(update)
    return check is not None and check is not False


class BaseTest:
    """Base class for command and prefix handler test classes. Contains
    utility methods an several callbacks used by both classes."""

    test_flag = False
    SRE_TYPE = type(re.match("", ""))

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    PASS_KEYWORDS = ('pass_user_data', 'pass_chat_data', 'pass_job_queue', 'pass_update_queue')

    @pytest.fixture(scope='module', params=itertools.combinations(PASS_KEYWORDS, 2))
    def pass_combination(self, request):
        return {key: True for key in request.param}

    def response(self, dispatcher, update):
        """
        Utility to send an update to a dispatcher and assert
        whether the callback was called appropriately. Its purpose is
        for repeated usage in the same test function.
        """
        self.test_flag = False
        dispatcher.process_update(update)
        return self.test_flag

    def callback_basic(self, bot, update):
        test_bot = isinstance(bot, Bot)
        test_update = isinstance(update, Update)
        self.test_flag = test_bot and test_update

    def make_callback_for(self, pass_keyword):
        def callback(bot, update, **kwargs):
            self.test_flag = kwargs.get(keyword) is not None

        keyword = pass_keyword[5:]
        return callback

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
            and isinstance(update.message, Message)
        )

    def callback_context_args(self, update, context):
        self.test_flag = context.args == ['one', 'two']

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

    def _test_context_args_or_regex(self, cdp, handler, text):
        cdp.add_handler(handler)
        update = make_command_update(text)
        assert not self.response(cdp, update)
        update.message.text += ' one two'
        assert self.response(cdp, update)

    def _test_edited(self, message, handler_edited, handler_not_edited):
        """
        Assert whether a handler that should accept edited messages
        and a handler that shouldn't work correctly.
        :param message: ``telegram.Message`` to check against the handlers
        :param handler_edited:  handler that should accept edited messages
        :param handler_not_edited:  handler that should not accept edited messages
        """
        update = make_command_update(message)
        edited_update = make_command_update(message, edited=True)

        assert is_match(handler_edited, update)
        assert is_match(handler_edited, edited_update)
        assert is_match(handler_not_edited, update)
        assert not is_match(handler_not_edited, edited_update)


# ----------------------------- CommandHandler -----------------------------


class TestCommandHandler(BaseTest):
    CMD = '/test'

    def test_slot_behaviour(self, recwarn, mro_slots):
        handler = self.make_default_handler()
        for attr in handler.__slots__:
            assert getattr(handler, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not handler.__dict__, f"got missing slot(s): {handler.__dict__}"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"
        handler.custom, handler.command = 'should give warning', self.CMD
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    @pytest.fixture(scope='class')
    def command(self):
        return self.CMD

    @pytest.fixture(scope='class')
    def command_message(self, command):
        return make_command_message(command)

    @pytest.fixture(scope='class')
    def command_update(self, command_message):
        return make_command_update(command_message)

    def ch_callback_args(self, bot, update, args):
        if update.message.text == self.CMD:
            self.test_flag = len(args) == 0
        elif update.message.text == f'{self.CMD}@{bot.username}':
            self.test_flag = len(args) == 0
        else:
            self.test_flag = args == ['one', 'two']

    def make_default_handler(self, callback=None, **kwargs):
        callback = callback or self.callback_basic
        return CommandHandler(self.CMD[1:], callback, **kwargs)

    def test_basic(self, dp, command):
        """Test whether a command handler responds to its command
        and not to others, or badly formatted commands"""
        handler = self.make_default_handler()
        dp.add_handler(handler)

        assert self.response(dp, make_command_update(command))
        assert not is_match(handler, make_command_update(command[1:]))
        assert not is_match(handler, make_command_update(f'/not{command[1:]}'))
        assert not is_match(handler, make_command_update(f'not {command} at start'))

    @pytest.mark.parametrize(
        'cmd',
        ['way_too_longcommand1234567yes_way_toooooooLong', 'ïñválídletters', 'invalid #&* chars'],
        ids=['too long', 'invalid letter', 'invalid characters'],
    )
    def test_invalid_commands(self, cmd):
        with pytest.raises(ValueError, match='not a valid bot command'):
            CommandHandler(cmd, self.callback_basic)

    def test_command_list(self):
        """A command handler with multiple commands registered should respond to all of them."""
        handler = CommandHandler(['test', 'star'], self.callback_basic)
        assert is_match(handler, make_command_update('/test'))
        assert is_match(handler, make_command_update('/star'))
        assert not is_match(handler, make_command_update('/stop'))

    def test_deprecation_warning(self):
        """``allow_edited`` deprecated in favor of filters"""
        with pytest.warns(TelegramDeprecationWarning, match='See https://git.io/fxJuV'):
            self.make_default_handler(allow_edited=True)

    def test_edited(self, command_message):
        """Test that a CH responds to an edited message iff its filters allow it"""
        handler_edited = self.make_default_handler()
        handler_no_edited = self.make_default_handler(filters=~Filters.update.edited_message)
        self._test_edited(command_message, handler_edited, handler_no_edited)

    def test_edited_deprecated(self, command_message):
        """Test that a CH responds to an edited message iff ``allow_edited`` is True"""
        handler_edited = self.make_default_handler(allow_edited=True)
        handler_no_edited = self.make_default_handler(allow_edited=False)
        self._test_edited(command_message, handler_edited, handler_no_edited)

    def test_directed_commands(self, bot, command):
        """Test recognition of commands with a mention to the bot"""
        handler = self.make_default_handler()
        assert is_match(handler, make_command_update(command + '@' + bot.username, bot=bot))
        assert not is_match(handler, make_command_update(command + '@otherbot', bot=bot))

    def test_with_filter(self, command):
        """Test that a CH with a (generic) filter responds iff its filters match"""
        handler = self.make_default_handler(filters=Filters.group)
        assert is_match(handler, make_command_update(command, chat=Chat(-23, Chat.GROUP)))
        assert not is_match(handler, make_command_update(command, chat=Chat(23, Chat.PRIVATE)))

    def test_pass_args(self, dp, bot, command):
        """Test the passing of arguments alongside a command"""
        handler = self.make_default_handler(self.ch_callback_args, pass_args=True)
        dp.add_handler(handler)
        at_command = f'{command}@{bot.username}'
        assert self.response(dp, make_command_update(command))
        assert self.response(dp, make_command_update(command + ' one two'))
        assert self.response(dp, make_command_update(at_command, bot=bot))
        assert self.response(dp, make_command_update(at_command + ' one two', bot=bot))

    def test_newline(self, dp, command):
        """Assert that newlines don't interfere with a command handler matching a message"""
        handler = self.make_default_handler()
        dp.add_handler(handler)
        update = make_command_update(command + '\nfoobar')
        assert is_match(handler, update)
        assert self.response(dp, update)

    @pytest.mark.parametrize('pass_keyword', BaseTest.PASS_KEYWORDS)
    def test_pass_data(self, dp, command_update, pass_combination, pass_keyword):
        handler = CommandHandler('test', self.make_callback_for(pass_keyword), **pass_combination)
        dp.add_handler(handler)
        assert self.response(dp, command_update) == pass_combination.get(pass_keyword, False)

    def test_other_update_types(self, false_update):
        """Test that a command handler doesn't respond to unrelated updates"""
        handler = self.make_default_handler()
        assert not is_match(handler, false_update)

    def test_filters_for_wrong_command(self, mock_filter):
        """Filters should not be executed if the command does not match the handler"""
        handler = self.make_default_handler(filters=mock_filter)
        assert not is_match(handler, make_command_update('/star'))
        assert not mock_filter.tested

    def test_context(self, cdp, command_update):
        """Test correct behaviour of CHs with context-based callbacks"""
        handler = self.make_default_handler(self.callback_context)
        cdp.add_handler(handler)
        assert self.response(cdp, command_update)

    def test_context_args(self, cdp, command):
        """Test CHs that pass arguments through ``context``"""
        handler = self.make_default_handler(self.callback_context_args)
        self._test_context_args_or_regex(cdp, handler, command)

    def test_context_regex(self, cdp, command):
        """Test CHs with context-based callbacks and a single filter"""
        handler = self.make_default_handler(
            self.callback_context_regex1, filters=Filters.regex('one two')
        )
        self._test_context_args_or_regex(cdp, handler, command)

    def test_context_multiple_regex(self, cdp, command):
        """Test CHs with context-based callbacks and filters combined"""
        handler = self.make_default_handler(
            self.callback_context_regex2, filters=Filters.regex('one') & Filters.regex('two')
        )
        self._test_context_args_or_regex(cdp, handler, command)


# ----------------------------- PrefixHandler -----------------------------


def combinations(prefixes, commands):
    return (prefix + command for prefix in prefixes for command in commands)


class TestPrefixHandler(BaseTest):
    # Prefixes and commands with which to test PrefixHandler:
    PREFIXES = ['!', '#', 'mytrig-']
    COMMANDS = ['help', 'test']
    COMBINATIONS = list(combinations(PREFIXES, COMMANDS))

    def test_slot_behaviour(self, mro_slots, recwarn):
        handler = self.make_default_handler()
        for attr in handler.__slots__:
            assert getattr(handler, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not handler.__dict__, f"got missing slot(s): {handler.__dict__}"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"
        handler.custom, handler.command = 'should give warning', self.COMMANDS
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    @pytest.fixture(scope='class', params=PREFIXES)
    def prefix(self, request):
        return request.param

    @pytest.fixture(scope='class', params=[1, 2], ids=['single prefix', 'multiple prefixes'])
    def prefixes(self, request):
        return TestPrefixHandler.PREFIXES[: request.param]

    @pytest.fixture(scope='class', params=COMMANDS)
    def command(self, request):
        return request.param

    @pytest.fixture(scope='class', params=[1, 2], ids=['single command', 'multiple commands'])
    def commands(self, request):
        return TestPrefixHandler.COMMANDS[: request.param]

    @pytest.fixture(scope='class')
    def prefix_message_text(self, prefix, command):
        return prefix + command

    @pytest.fixture(scope='class')
    def prefix_message(self, prefix_message_text):
        return make_message(prefix_message_text)

    @pytest.fixture(scope='class')
    def prefix_message_update(self, prefix_message):
        return make_message_update(prefix_message)

    def make_default_handler(self, callback=None, **kwargs):
        callback = callback or self.callback_basic
        return PrefixHandler(self.PREFIXES, self.COMMANDS, callback, **kwargs)

    def ch_callback_args(self, bot, update, args):
        if update.message.text in TestPrefixHandler.COMBINATIONS:
            self.test_flag = len(args) == 0
        else:
            self.test_flag = args == ['one', 'two']

    def test_basic(self, dp, prefix, command):
        """Test the basic expected response from a prefix handler"""
        handler = self.make_default_handler()
        dp.add_handler(handler)
        text = prefix + command

        assert self.response(dp, make_message_update(text))
        assert not is_match(handler, make_message_update(command))
        assert not is_match(handler, make_message_update(prefix + 'notacommand'))
        assert not is_match(handler, make_command_update(f'not {text} at start'))

    def test_single_multi_prefixes_commands(self, prefixes, commands, prefix_message_update):
        """Test various combinations of prefixes and commands"""
        handler = self.make_default_handler()
        result = is_match(handler, prefix_message_update)
        expected = prefix_message_update.message.text in combinations(prefixes, commands)
        return result == expected

    def test_edited(self, prefix_message):
        handler_edited = self.make_default_handler()
        handler_no_edited = self.make_default_handler(filters=~Filters.update.edited_message)
        self._test_edited(prefix_message, handler_edited, handler_no_edited)

    def test_with_filter(self, prefix_message_text):
        handler = self.make_default_handler(filters=Filters.group)
        text = prefix_message_text
        assert is_match(handler, make_message_update(text, chat=Chat(-23, Chat.GROUP)))
        assert not is_match(handler, make_message_update(text, chat=Chat(23, Chat.PRIVATE)))

    def test_pass_args(self, dp, prefix_message):
        handler = self.make_default_handler(self.ch_callback_args, pass_args=True)
        dp.add_handler(handler)
        assert self.response(dp, make_message_update(prefix_message))

        update_with_args = make_message_update(prefix_message.text + ' one two')
        assert self.response(dp, update_with_args)

    @pytest.mark.parametrize('pass_keyword', BaseTest.PASS_KEYWORDS)
    def test_pass_data(self, dp, pass_combination, prefix_message_update, pass_keyword):
        """Assert that callbacks receive data iff its corresponding ``pass_*`` kwarg is enabled"""
        handler = self.make_default_handler(
            self.make_callback_for(pass_keyword), **pass_combination
        )
        dp.add_handler(handler)
        assert self.response(dp, prefix_message_update) == pass_combination.get(
            pass_keyword, False
        )

    def test_other_update_types(self, false_update):
        handler = self.make_default_handler()
        assert not is_match(handler, false_update)

    def test_filters_for_wrong_command(self, mock_filter):
        """Filters should not be executed if the command does not match the handler"""
        handler = self.make_default_handler(filters=mock_filter)
        assert not is_match(handler, make_message_update('/test'))
        assert not mock_filter.tested

    def test_edit_prefix(self):
        handler = self.make_default_handler()
        handler.prefix = ['?', '§']
        assert handler._commands == list(combinations(['?', '§'], self.COMMANDS))
        handler.prefix = '+'
        assert handler._commands == list(combinations(['+'], self.COMMANDS))

    def test_edit_command(self):
        handler = self.make_default_handler()
        handler.command = 'foo'
        assert handler._commands == list(combinations(self.PREFIXES, ['foo']))

    def test_basic_after_editing(self, dp, prefix, command):
        """Test the basic expected response from a prefix handler"""
        handler = self.make_default_handler()
        dp.add_handler(handler)
        text = prefix + command

        assert self.response(dp, make_message_update(text))
        handler.command = 'foo'
        text = prefix + 'foo'
        assert self.response(dp, make_message_update(text))

    def test_context(self, cdp, prefix_message_update):
        handler = self.make_default_handler(self.callback_context)
        cdp.add_handler(handler)
        assert self.response(cdp, prefix_message_update)

    def test_context_args(self, cdp, prefix_message_text):
        handler = self.make_default_handler(self.callback_context_args)
        self._test_context_args_or_regex(cdp, handler, prefix_message_text)

    def test_context_regex(self, cdp, prefix_message_text):
        handler = self.make_default_handler(
            self.callback_context_regex1, filters=Filters.regex('one two')
        )
        self._test_context_args_or_regex(cdp, handler, prefix_message_text)

    def test_context_multiple_regex(self, cdp, prefix_message_text):
        handler = self.make_default_handler(
            self.callback_context_regex2, filters=Filters.regex('one') & Filters.regex('two')
        )
        self._test_context_args_or_regex(cdp, handler, prefix_message_text)
