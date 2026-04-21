#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
# along with this program. If not, see [http://www.gnu.org/licenses/].

from telegram import (
    KeyboardButton,
    KeyboardButtonRequestManagedBot,
    PreparedKeyboardButton,
)


class TestBot96WithoutRequest:
    async def test_get_managed_bot_token(self, offline_bot, monkeypatch):
        async def make_assertion(endpoint, data, **kwargs):
            assert endpoint == "getManagedBotToken"
            assert data == {"user_id": 123}
            assert kwargs["api_kwargs"] is None
            return "managed-token"

        monkeypatch.setattr(offline_bot, "_post", make_assertion)
        assert await offline_bot.get_managed_bot_token(123) == "managed-token"

    async def test_replace_managed_bot_token(self, offline_bot, monkeypatch):
        async def make_assertion(endpoint, data, **kwargs):
            assert endpoint == "replaceManagedBotToken"
            assert data == {"user_id": 123}
            assert kwargs["api_kwargs"] is None
            return "managed-token-2"

        monkeypatch.setattr(offline_bot, "_post", make_assertion)
        assert await offline_bot.replace_managed_bot_token(123) == "managed-token-2"

    async def test_save_prepared_keyboard_button(self, offline_bot, monkeypatch):
        button = KeyboardButton(
            "Create managed bot",
            request_managed_bot=KeyboardButtonRequestManagedBot(1, "Managed Bot", "managed_test"),
        )

        async def make_assertion(endpoint, data, **kwargs):
            assert endpoint == "savePreparedKeyboardButton"
            assert data["user_id"] == 123
            assert data["button"] == button
            assert kwargs["api_kwargs"] is None
            return {"id": "prepared-button-id"}

        monkeypatch.setattr(offline_bot, "_post", make_assertion)
        out = await offline_bot.save_prepared_keyboard_button(123, button)
        assert isinstance(out, PreparedKeyboardButton)
        assert out.id == "prepared-button-id"

    async def test_send_poll_payload(self, offline_bot, monkeypatch):
        async def make_assertion(endpoint, data, **kwargs):
            assert endpoint == "sendPoll"
            assert data["allows_revoting"] is True
            assert data["shuffle_options"] is True
            assert data["allow_adding_options"] is True
            assert data["hide_results_until_closes"] is True
            assert data["correct_option_ids"] == [0, 2]
            assert data["description"] == "description"
            return True

        monkeypatch.setattr(offline_bot, "_send_message", make_assertion)
        assert await offline_bot.send_poll(
            chat_id=123,
            question="Question?",
            options=["A", "B", "C"],
            type="quiz",
            allows_multiple_answers=True,
            allows_revoting=True,
            shuffle_options=True,
            allow_adding_options=True,
            hide_results_until_closes=True,
            correct_option_ids=[0, 2],
            description="description",
        )
