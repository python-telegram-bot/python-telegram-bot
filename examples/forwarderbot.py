#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to forward a user's message to a chat.

For the bot to forward the message to the group the following steps are necessary:
- Add the bot to the group
- Get the group's or chat's id:
    https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id
- Save the group's or chat's id in the "destination_id" variable (line 36)

Usage:
Basic bot to forward messages to a determined group
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

DESTINATION_ID = "id"


async def start(update: Update, context: CallbackContext) -> None:
    """Starts the conversation and asks the user to send a message"""
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"""
        Hi {user}, send a message to forward it to the designated chat
        """
    )


async def forward_message(update: Update, context: CallbackContext) -> None:
    """Forwards the user's message to the designated group or chat"""
    await context.bot.forward_message(
        chat_id=DESTINATION_ID,
        from_chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
    )
    await update.message.reply_text("Message forwarded!")


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    application = Application.builder().token("TOKEN").build()

    # Handle the /start command
    start_handler = CommandHandler("start", start)

    application.add_handler(start_handler)

    # Hadle the /forward command
    forward_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message)

    application.add_handler(forward_handler)

    # Start the Bot until Ctrl-C is pressed
    application.run_polling()


if __name__ == "__main__":
    main()
