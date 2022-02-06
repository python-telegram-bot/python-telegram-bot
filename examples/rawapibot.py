#!/usr/bin/env python
# pylint: disable=global-statement
"""Simple Bot to reply to Telegram messages.

This is built on the API wrapper, see echobot.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import asyncio
import logging
from typing import NoReturn

import telegram
from telegram.error import NetworkError, Forbidden


UPDATE_ID = None


async def main() -> NoReturn:
    """Run the bot."""
    global UPDATE_ID
    # Telegram Bot Authorization Token
    bot = telegram.Bot('TOKEN')

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Forbidden" exception.
    try:
        UPDATE_ID = (await bot.get_updates())[0].update_id
    except IndexError:
        UPDATE_ID = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            await echo(bot)
        except NetworkError:
            await asyncio.sleep(1)
        except Forbidden:
            # The user has removed or blocked the bot.
            UPDATE_ID += 1


async def echo(bot: telegram.Bot) -> None:
    """Echo the message the user sent."""
    global UPDATE_ID
    # Request updates after the last update_id
    for update in await bot.get_updates(offset=UPDATE_ID, timeout=10):
        UPDATE_ID = update.update_id + 1

        # your bot can receive updates without messages
        # and not all messages contain text
        if update.message and update.message.text:
            # Reply to the message
            await update.message.reply_text(update.message.text)


if __name__ == '__main__':
    asyncio.run(main())
