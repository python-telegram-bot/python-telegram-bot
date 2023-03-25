#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
import asyncio
import re

import pytest

from telegram import Bot, Chat, Message, Update
from telegram.ext import CallbackContext, CommandHandler, JobQueue, filters
from tests.auxil.build_messages import (
    make_command_message,
    make_command_update,
    make_message_update,
)
from tests.auxil.slots import mro_slots


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
    def _reset(self):
        self.test_flag = False

    async def response(self, application, update):
        """
        Utility to send an update to a dispatcher and assert
        whether the callback was called appropriately. Its purpose is
        for repeated usage in the same test function.
        """
        self.test_flag = False
        async with application:
            await application.process_update(update)
        return self.test_flag

    def callback_basic(self, update, context):
        test_bot = isinstance(context.bot, Bot)
        test_update = isinstance(update, Update)
        self.test_flag = test_bot and test_update

    def make_callback_for(self, pass_keyword):
        def callback(bot, update, **kwargs):
            self.test_flag = kwargs.get(keyword) is not None

        keyword = pass_keyword[5:]
        return callback

    async def callback(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, Update)
            and isinstance(context.update_queue, asyncio.Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.user_data, dict)
            and isinstance(context.chat_data, dict)
            and isinstance(context.bot_data, dict)
            and isinstance(update.message, Message)
        )

    def callback_args(self, update, context):
        self.test_flag = context.args == ["one", "two"]

    def callback_regex1(self, update, context):
        if context.matches:
            types = all(type(res) is self.SRE_TYPE for res in context.matches)
            num = len(context.matches) == 1
            self.test_flag = types and num

    def callback_regex2(self, update, context):
        if context.matches:
            types = all(type(res) is self.SRE_TYPE for res in context.matches)
            num = len(context.matches) == 2
            self.test_flag = types and num

    async def _test_context_args_or_regex(self, app, handler, text):
        app.add_handler(handler)
        update = make_command_update(text, bot=app.bot)
        assert not await self.response(app, update)
        update = make_command_update(text + " one two", bot=app.bot)
        assert await self.response(app, update)

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
    CMD = "/test"

    def test_slot_behaviour(self):
        handler = self.make_default_handler()
        for attr in handler.__slots__:
            assert getattr(handler, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"

    @pytest.fixture(scope="class")
    def command(self):
        return self.CMD

    @pytest.fixture(scope="class")
    def command_message(self, command, bot):
        return make_command_message(command, bot=bot)

    @pytest.fixture(scope="class")
    def command_update(self, command_message):
        return make_command_update(command_message)

    def make_default_handler(self, callback=None, **kwargs):
        callback = callback or self.callback_basic
        return CommandHandler(self.CMD[1:], callback, **kwargs)

    async def test_basic(self, app, command):
        """Test whether a command handler responds to its command
        and not to others, or badly formatted commands"""
        handler = self.make_default_handler()
        app.add_handler(handler)

        assert await self.response(app, make_command_update(command, bot=app.bot))
        assert not is_match(handler, make_command_update(command[1:], bot=app.bot))
        assert not is_match(handler, make_command_update(f"/not{command[1:]}", bot=app.bot))
        assert not is_match(handler, make_command_update(f"not {command} at start", bot=app.bot))
        assert not is_match(
            handler, make_message_update(bot=app.bot, message=None, caption="caption")
        )

        handler = CommandHandler(["FOO", "bAR"], callback=self.callback)
        assert isinstance(handler.commands, frozenset)
        assert handler.commands == {"foo", "bar"}

        handler = CommandHandler(["FOO"], callback=self.callback)
        assert isinstance(handler.commands, frozenset)
        assert handler.commands == {"foo"}

    @pytest.mark.parametrize(
        "cmd",
        ["way_too_longcommand1234567yes_way_toooooooLong", "ïñválídletters", "invalid #&* chars"],
        ids=["too long", "invalid letter", "invalid characters"],
    )
    def test_invalid_commands(self, cmd):
        with pytest.raises(
            ValueError, match=f"`{re.escape(cmd.lower())}` is not a valid bot command"
        ):
            CommandHandler(cmd, self.callback_basic)

    def test_command_list(self, bot):
        """A command handler with multiple commands registered should respond to all of them."""
        handler = CommandHandler(["test", "star"], self.callback_basic)
        assert is_match(handler, make_command_update("/test", bot=bot))
        assert is_match(handler, make_command_update("/star", bot=bot))
        assert not is_match(handler, make_command_update("/stop", bot=bot))

    def test_edited(self, command_message):
        """Test that a CH responds to an edited message if its filters allow it"""
        handler_edited = self.make_default_handler()
        handler_no_edited = self.make_default_handler(filters=~filters.UpdateType.EDITED_MESSAGE)
        self._test_edited(command_message, handler_edited, handler_no_edited)

    def test_directed_commands(self, bot, command):
        """Test recognition of commands with a mention to the bot"""
        handler = self.make_default_handler()
        assert is_match(handler, make_command_update(command + "@" + bot.username, bot=bot))
        assert not is_match(handler, make_command_update(command + "@otherbot", bot=bot))

    def test_with_filter(self, command, bot):
        """Test that a CH with a (generic) filter responds if its filters match"""
        handler = self.make_default_handler(filters=filters.ChatType.GROUP)
        assert is_match(handler, make_command_update(command, chat=Chat(-23, Chat.GROUP), bot=bot))
        assert not is_match(
            handler, make_command_update(command, chat=Chat(23, Chat.PRIVATE), bot=bot)
        )

    async def test_newline(self, app, command):
        """Assert that newlines don't interfere with a command handler matching a message"""
        handler = self.make_default_handler()
        app.add_handler(handler)
        update = make_command_update(command + "\nfoobar", bot=app.bot)
        async with app:
            assert is_match(handler, update)
        assert await self.response(app, update)

    def test_other_update_types(self, false_update):
        """Test that a command handler doesn't respond to unrelated updates"""
        handler = self.make_default_handler()
        assert not is_match(handler, false_update)

    def test_filters_for_wrong_command(self, mock_filter, bot):
        """Filters should not be executed if the command does not match the handler"""
        handler = self.make_default_handler(filters=mock_filter)
        assert not is_match(handler, make_command_update("/star", bot=bot))
        assert not mock_filter.tested

    async def test_context(self, app, command_update):
        """Test correct behaviour of CHs with context-based callbacks"""
        handler = self.make_default_handler(self.callback)
        app.add_handler(handler)
        assert await self.response(app, command_update)

    async def test_context_args(self, app, command):
        """Test CHs that pass arguments through ``context``"""
        handler = self.make_default_handler(self.callback_args)
        await self._test_context_args_or_regex(app, handler, command)

    async def test_context_regex(self, app, command):
        """Test CHs with context-based callbacks and a single filter"""
        handler = self.make_default_handler(self.callback_regex1, filters=filters.Regex("one two"))
        await self._test_context_args_or_regex(app, handler, command)

    async def test_context_multiple_regex(self, app, command):
        """Test CHs with context-based callbacks and filters combined"""
        handler = self.make_default_handler(
            self.callback_regex2, filters=filters.Regex("one") & filters.Regex("two")
        )
        await self._test_context_args_or_regex(app, handler, command)
