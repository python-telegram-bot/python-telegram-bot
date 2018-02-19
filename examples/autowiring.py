#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Bot that displays the autowiring functionality
# This program is dedicated to the public domain under the CC0 license.
"""
This bot shows how to use `autowire=True` in Handler definitions to save a lot of effort typing
the explicit pass_* flags.

Usage:
Autowiring example: Try sending /start, /data, "My name is Leandro", or some random text.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram.ext import Updater, CommandHandler, RegexHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def start(bot, update, args):
    query = ' '.join(args)  # `args` is magically defined
    if query:
        update.message.reply_text(query)
    else:
        update.message.reply_text("Example: /start here I am")


def simple_update_only(update):
    """
    A simple handler that only needs an `update` object.
    Useful e.g. for basic commands like /help that need to do nothing but reply with some text.
    """
    update.message.reply_text("This should have produced an error "
                              "for the MessageHandler in group=1.")


def callback_with_data(bot, update, chat_data, user_data):
    msg = 'Adding something to chat_data...\n'
    chat_data['value'] = "I'm a chat_data value"
    msg += chat_data['value']

    msg += '\n\n'

    msg += 'Adding something to user_data...\n'
    user_data['value'] = "I'm a user_data value"
    msg += user_data['value']

    update.message.reply_text(msg, quote=True)


def regex_with_groups(bot, update, groups, groupdict):
    update.message.reply_text("Nice, your {} is {}.".format(groups[0], groups[1]))
    update.message.reply_text('Groupdict: {}'.format(groupdict))


def callback_undefined_arguments(bot, update, chat_data, groups):
    pass


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Inject the `args` parameter automagically
    dp.add_handler(CommandHandler("start", start, autowire=True))

    # A RegexHandler example where `groups` and `groupdict` are passed automagically
    # Examples: Send "My name is Leandro" or "My cat is blue".
    dp.add_handler(RegexHandler(r'[Mm]y (?P<object>.*) is (?P<value>.*)',
                                regex_with_groups,
                                autowire=True))

    # This will raise an error because the bot argument is missing...
    dp.add_handler(CommandHandler('help', simple_update_only), group=1)
    # ... but with the autowiring capability, you can have callbacks with only an `update` argument.
    dp.add_handler(CommandHandler('help', simple_update_only, autowire=True), group=2)

    # Passing `chat_data` and `user_data` explicitly...
    dp.add_handler(CommandHandler("data", callback_with_data,
                                  pass_chat_data=True,
                                  pass_user_data=True))
    # ... is equivalent to passing them automagically.
    dp.add_handler(CommandHandler("data", callback_with_data, autowire=True))

    # An example of using the `groups` parameter which is not defined for a CommandHandler.
    # Uncomment the line below and you will see a warning.
    # dp.add_handler(CommandHandler("erroneous", callback_undefined_arguments, autowire=True))

    dp.add_error_handler(error)
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
