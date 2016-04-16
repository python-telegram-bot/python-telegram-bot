#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Basic example for a bot that awaits an answer from the user. It's built upon
# the state_machine_bot.py example
# This program is dedicated to the public domain under the CC0 license.

import logging
from telegram import Emoji, ForceReply, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, \
    CallbackQueryHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                           '%(message)s',
                    level=logging.DEBUG)

# Define the different states a chat can be in
MENU, AWAIT_CONFIRMATION, AWAIT_INPUT = range(3)

# Python 2 and 3 unicode differences
try:
    YES, NO = (Emoji.THUMBS_UP_SIGN.decode('utf-8'),
               Emoji.THUMBS_DOWN_SIGN.decode('utf-8'))
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
    user_state = state.get(chat_id, MENU)

    if user_state == MENU:
        state[user_id] = AWAIT_INPUT  # set the state
        bot.sendMessage(chat_id,
                        text="Please enter your settings value or send "
                             "/cancel to abort",
                        reply_markup=ForceReply())


def entered_value(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_state = state.get(user_id, MENU)

    # Check if we are waiting for input
    if chat_state == AWAIT_INPUT:
        state[user_id] = AWAIT_CONFIRMATION

        # Save the user id and the answer to context
        context[user_id] = update.message.text
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(YES, callback_data=YES),
              InlineKeyboardButton(NO, callback_data=NO)]])
        bot.sendMessage(chat_id, text="Are you sure?",
                        reply_markup=reply_markup)


def confirm_value(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    text = query.data
    user_state = state.get(user_id, MENU)
    user_context = context.get(user_id, None)

    # Check if we are waiting for confirmation and the right user answered
    if user_state == AWAIT_CONFIRMATION:
        del state[user_id]
        del context[user_id]
        bot.answerCallbackQuery(query.id, text="Ok!")
        if text == YES:
            values[user_id] = user_context
            bot.editMessageText(text="Changed value to %s." % values[user_id],
                                chat_id=chat_id,
                                message_id=
                                query.message.message_id)
        else:
            bot.editMessageText(text="Alright, value is still %s."
                                     % values[user_id],
                                chat_id=chat_id,
                                message_id=
                                query.message.message_id)


# Handler for the /cancel command.
# Sets the state back to MENU and clears the context
def cancel(bot, update):
    chat_id = update.message.chat_id
    del state[chat_id]
    del context[chat_id]


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text="Use /set to test this bot.")


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))

# Create the Updater and pass it your bot's token.
updater = Updater("TOKEN")

# The command
updater.dispatcher.addHandler(CommandHandler('set', set_value))
# The answer
updater.dispatcher.addHandler(MessageHandler([filters.TEXT], entered_value))
# The confirmation
updater.dispatcher.addHandler(CallbackQueryHandler(confirm_value))
updater.dispatcher.addHandler(CommandHandler('cancel', cancel))
updater.dispatcher.addHandler(CommandHandler('start', help))
updater.dispatcher.addHandler(CommandHandler('help', help))
updater.dispatcher.addErrorHandler(error)

# Start the Bot
updater.start_polling()

# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()
