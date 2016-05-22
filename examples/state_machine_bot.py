#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Basic example for a bot that awaits an answer from the user
# This program is dedicated to the public domain under the CC0 license.

import logging
from telegram import Emoji, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                    '%(message)s',
                    level=logging.INFO)

# Define the different states a chat can be in
MENU, AWAIT_CONFIRMATION, AWAIT_INPUT = range(3)

# Python 2 and 3 unicode differences
try:
    YES, NO = (Emoji.THUMBS_UP_SIGN.decode('utf-8'), Emoji.THUMBS_DOWN_SIGN.decode('utf-8'))
except AttributeError:
    YES, NO = (Emoji.THUMBS_UP_SIGN, Emoji.THUMBS_DOWN_SIGN)

# States are saved in a dict that maps chat_id -> state
state = dict()
# Sometimes you need to save data temporarily
context = dict()
# This dict is used to store the settings value for the chat.
# Usually, you'd use persistence for this (e.g. sqlite).
values = dict()


# Example handler. Will be called on the /set command and on regular messages
def set_value(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text
    chat_state = state.get(chat_id, MENU)
    chat_context = context.get(chat_id, None)

    # Since the handler will also be called on messages, we need to check if
    # the message is actually a command
    if chat_state == MENU and text[0] == '/':
        state[chat_id] = AWAIT_INPUT  # set the state
        context[chat_id] = user_id  # save the user id to context
        bot.sendMessage(chat_id,
                        text="Please enter your settings value or send "
                        "/cancel to abort",
                        reply_markup=ForceReply())

    # If we are waiting for input and the right user answered
    elif chat_state == AWAIT_INPUT and chat_context == user_id:
        state[chat_id] = AWAIT_CONFIRMATION

        # Save the user id and the answer to context
        context[chat_id] = (user_id, update.message.text)
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton(YES), KeyboardButton(NO)]],
            one_time_keyboard=True)
        bot.sendMessage(chat_id, text="Are you sure?", reply_markup=reply_markup)

    # If we are waiting for confirmation and the right user answered
    elif chat_state == AWAIT_CONFIRMATION and chat_context[0] == user_id:
        del state[chat_id]
        del context[chat_id]
        if text == YES:
            values[chat_id] = chat_context[1]
            bot.sendMessage(chat_id, text="Changed value to %s." % values[chat_id])
        else:
            bot.sendMessage(chat_id,
                            text="Value not changed: %s." % values.get(chat_id, '<not set>'))


# Handler for the /cancel command.
# Sets the state back to MENU and clears the context
def cancel(bot, update):
    chat_id = update.message.chat_id
    del state[chat_id]
    del context[chat_id]


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text="Use /set to test this bot.")

# Create the Updater and pass it your bot's token.
updater = Updater("TOKEN")

# The command
updater.dispatcher.add_handler(CommandHandler('set', set_value))
# The answer and confirmation
updater.dispatcher.add_handler(MessageHandler([Filters.text], set_value))
updater.dispatcher.add_handler(CommandHandler('cancel', cancel))
updater.dispatcher.add_handler(CommandHandler('start', help))
updater.dispatcher.add_handler(CommandHandler('help', help))

# Start the Bot
updater.start_polling()

# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()
