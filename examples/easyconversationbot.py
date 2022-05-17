#!/usr/bin/env python
# pylint: disable=wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple example of EasyConversationBot.
The bot let user add family members and print them, in simple, functional way
 - without state machines.
"""

import logging

from telegram.ext._easyconversationhandler import EasyConversationHandler

from telegram.ext import Application, CommandHandler

# Enable logging
from telegram.ext.filters import Regex

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

SIBLINGS_KEY, CHILDREN_KEY = 1, 2


async def collect_user_inputs(context, num_items: int):
    """Collects a list of strings from the user in maximum length of `num_items`"""
    inputs = []
    for _ in range(num_items):
        # await as in regular reply_text for network request
        await context.last_update.message.reply_text("Enter input, or /done")

        # Here is the magic!
        # We can get new updates on the go
        # Just remember to await it. This waits for the user"s input, and can be for long time.
        #  - But your functional logic stays simple and saves state!
        update = await context.get_update()

        if update.message.text == "/done":
            break
        inputs.append(update.message.text)
    return inputs


async def collect_number(context):
    """Collects an int from the user"""
    while True:
        update = await context.get_update()
        if update.message.text.isdigit():
            return int(update.message.text)
        await update.message.reply_text("This is not a number. Enter a number:")


async def collect_list(context, list_name):
    """Collects list from user. First prompts with `list_name`"""
    await context.last_update.message.reply_text(f"How much {list_name}?")
    how_much = await collect_number(context)
    ret = await collect_user_inputs(context, how_much)
    await context.last_update.message.reply_text(f"{list_name}: {ret}")
    return ret


async def siblings_callback(context):
    """Entry point for /siblings command"""
    await context.get_update()  # Ignore first message (/siblings)

    # We can easily call this function multiple times in multiple logic paths
    # We need to await our functions too
    context.user_data[SIBLINGS_KEY] = await collect_list(context, "siblings")

    await print_help(context.last_update, context)


async def children_callback(context):
    """Entry point for /children command"""
    await context.get_update()  # Ignore first message
    context.user_data[CHILDREN_KEY] = await collect_list(context, "children")
    await print_help(context.last_update, context)


# Simple command handlers callbacks

async def print_data(update, context):
    """Callback for /print command"""
    siblings = context.user_data.get(SIBLINGS_KEY, "Not set yet")
    children = context.user_data.get(CHILDREN_KEY, "Not set yet")
    await update.message.reply_text(f"Your siblings: {siblings}")
    await update.message.reply_text(f"Your children: {children}")


async def print_help(update, _):
    """Callback for /help command"""
    await update.message.reply_text("Type /siblings, /children or /print")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("Token").build()

    application.add_handler(CommandHandler("print", print_data))
    application.add_handler(CommandHandler("help", print_help))
    application.add_handler(CommandHandler("start", print_help))

    application.add_handler(
        EasyConversationHandler(siblings_callback, first_message_filter=Regex("/siblings"))
    )
    application.add_handler(
        EasyConversationHandler(children_callback, first_message_filter=Regex("/children"))
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
