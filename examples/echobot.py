#!/usr/bin/env python

'''Simple Bot to reply Telegram messages'''

import telegram
import time

# Telegram Bot Authorization Token
bot = telegram.Bot('token')

# This will be our global variable to keep the latest update_id when requesting
# for updates. It starts with the latest update_id available.
LAST_UPDATE_ID = bot.getUpdates()[-1].update_id


def echo():
    global LAST_UPDATE_ID

    # Request updates from last updated_id
    for update in bot.getUpdates(offset=LAST_UPDATE_ID):
        if LAST_UPDATE_ID < update.update_id:
            # chat_id is required to reply any message
            chat_id = update.message.chat_id
            message = update.message.text

            if (message):
                # Reply the message
                bot.sendMessage(chat_id=chat_id,
                                text=message)

                # Updates global offset to get the new updates
                LAST_UPDATE_ID = update.update_id


if __name__ == '__main__':
    while True:
        echo()
        time.sleep(5)
