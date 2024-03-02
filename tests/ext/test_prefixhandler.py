#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2024
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
import pytest

from telegram import Chat
from telegram.ext import CallbackContext, PrefixHandler, filters
from tests.auxil.build_messages import make_command_update, make_message, make_message_update
from tests.auxil.slots import mro_slots
from tests.ext.test_commandhandler import BaseTest, is_match


def combinations(prefixes, commands):
    return (prefix + command for prefix in prefixes for command in commands)


class TestPrefixHandler(BaseTest):
    # Prefixes and commands with which to test PrefixHandler:
    PREFIXES = ["!", "#", "mytrig-"]
    COMMANDS = ["help", "test"]
    COMBINATIONS = list(combinations(PREFIXES, COMMANDS))

    def test_slot_behaviour(self):
        handler = self.make_default_handler()
        for attr in handler.__slots__:
            assert getattr(handler, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"

    @pytest.fixture(scope="class", params=PREFIXES)
    def prefix(self, request):
        return request.param

    @pytest.fixture(scope="class", params=[1, 2], ids=["single prefix", "multiple prefixes"])
    def prefixes(self, request):
        return TestPrefixHandler.PREFIXES[: request.param]

    @pytest.fixture(scope="class", params=COMMANDS)
    def command(self, request):
        return request.param

    @pytest.fixture(scope="class", params=[1, 2], ids=["single command", "multiple commands"])
    def commands(self, request):
        return TestPrefixHandler.COMMANDS[: request.param]

    @pytest.fixture(scope="class")
    def prefix_message_text(self, prefix, command):
        return prefix + command

    @pytest.fixture(scope="class")
    def prefix_message(self, prefix_message_text):
        return make_message(prefix_message_text)

    @pytest.fixture(scope="class")
    def prefix_message_update(self, prefix_message):
        return make_message_update(prefix_message)

    def make_default_handler(self, callback=None, **kwargs):
        callback = callback or self.callback_basic
        return PrefixHandler(self.PREFIXES, self.COMMANDS, callback, **kwargs)

    async def test_basic(self, app, prefix, command):
        """Test the basic expected response from a prefix handler"""
        handler = self.make_default_handler()
        app.add_handler(handler)
        text = prefix + command

        assert await self.response(app, make_message_update(text))
        assert not is_match(handler, make_message_update(command))
        assert not is_match(handler, make_message_update(prefix + "notacommand"))
        assert not is_match(handler, make_command_update(f"not {text} at start"))
        assert not is_match(
            handler, make_message_update(bot=app.bot, message=None, caption="caption")
        )

        handler = PrefixHandler(prefix=["!", "#"], command="cmd", callback=self.callback)
        assert isinstance(handler.commands, frozenset)
        assert handler.commands == {"!cmd", "#cmd"}

        handler = PrefixHandler(prefix="#", command={"cmd", "bmd"}, callback=self.callback)
        assert isinstance(handler.commands, frozenset)
        assert handler.commands == {"#cmd", "#bmd"}

    def test_single_multi_prefixes_commands(self, prefixes, commands, prefix_message_update):
        """Test various combinations of prefixes and commands"""
        handler = self.make_default_handler()
        result = is_match(handler, prefix_message_update)
        expected = prefix_message_update.message.text in combinations(prefixes, commands)
        return result == expected

    def test_edited(self, prefix_message):
        handler_edited = self.make_default_handler()
        handler_no_edited = self.make_default_handler(filters=~filters.UpdateType.EDITED_MESSAGE)
        self._test_edited(prefix_message, handler_edited, handler_no_edited)

    def test_with_filter(self, prefix_message_text):
        handler = self.make_default_handler(filters=filters.ChatType.GROUP)
        text = prefix_message_text
        assert is_match(handler, make_message_update(text, chat=Chat(-23, Chat.GROUP)))
        assert not is_match(handler, make_message_update(text, chat=Chat(23, Chat.PRIVATE)))

    def test_other_update_types(self, false_update):
        handler = self.make_default_handler()
        assert not is_match(handler, false_update)

    def test_filters_for_wrong_command(self, mock_filter):
        """Filters should not be executed if the command does not match the handler"""
        handler = self.make_default_handler(filters=mock_filter)
        assert not is_match(handler, make_message_update("/test"))
        assert not mock_filter.tested

    async def test_context(self, app, prefix_message_update):
        handler = self.make_default_handler(self.callback)
        app.add_handler(handler)
        assert await self.response(app, prefix_message_update)

    async def test_context_args(self, app, prefix_message_text):
        handler = self.make_default_handler(self.callback_args)
        await self._test_context_args_or_regex(app, handler, prefix_message_text)

    async def test_context_regex(self, app, prefix_message_text):
        handler = self.make_default_handler(self.callback_regex1, filters=filters.Regex("one two"))
        await self._test_context_args_or_regex(app, handler, prefix_message_text)

    async def test_context_multiple_regex(self, app, prefix_message_text):
        handler = self.make_default_handler(
            self.callback_regex2, filters=filters.Regex("one") & filters.Regex("two")
        )
        await self._test_context_args_or_regex(app, handler, prefix_message_text)

    def test_collect_additional_context(self, app):
        handler = self.make_default_handler(
            self.callback_regex2, filters=filters.Regex("one") & filters.Regex("two")
        )
        context = CallbackContext(application=app)
        handler.collect_additional_context(
            context=context, update=None, application=app, check_result=None
        )
        assert context.args is None
