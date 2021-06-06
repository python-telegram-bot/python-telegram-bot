#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""This is a very simple example on how one could implement a custom error handler."""
import html
import json
import logging
import traceback

from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# The token you got from @botfather when you created the bot
BOT_TOKEN = "TOKEN"

# This can be your own ID, or one for a developer group/channel.
# You can use the /start command of this bot to see your chat id.
DEVELOPER_CHAT_ID = 123456789


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def bad_command(update: Update, context: CallbackContext) -> None:
    """Raise an error to trigger the error handler."""
    context.bot.wrong_method_name()  # type: ignore[attr-defined]


def start(update: Update, context: CallbackContext) -> None:
    """Displays info on how to trigger an error."""
    update.effective_message.reply_html(
        'Use /bad_command to cause an error.\n'
        f'Your chat id is <code>{update.effective_chat.id}</code>.'
    )


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the commands...
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('bad_command', bad_command))

    # ...and the error handler
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
