from unittest.mock import MagicMock

import pytest

from examples.echobot import echo, help_command, start
from telegram import ForceReply, Message, Update, User
from telegram.ext import ContextTypes


class TestEchoBot:
    MENTION_HTML = "mention_html"
    TEXT = "text"

    def setup_method(self) -> None:
        self.user = MagicMock(spec=User)
        self.user.mention_html.return_value = self.MENTION_HTML

        self.message = MagicMock(spec=Message)
        self.message.text = self.TEXT

        self.update = MagicMock(spec=Update)
        self.update.effective_user = self.user
        self.update.message = self.message

        self.context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    @pytest.mark.asyncio
    async def test_start(self) -> None:
        await start(self.update, self.context)
        self.update.message.reply_html.assert_called_once_with(
            f"Hi {self.MENTION_HTML}!", reply_markup=ForceReply(selective=True)
        )

    @pytest.mark.asyncio
    async def test_help_command(self) -> None:
        await help_command(self.update, self.context)
        self.update.message.reply_text.assert_called_once_with("Help!")

    @pytest.mark.asyncio
    async def test_echo(self) -> None:
        await echo(self.update, self.context)
        self.update.message.reply_text.assert_called_once_with(self.TEXT)
