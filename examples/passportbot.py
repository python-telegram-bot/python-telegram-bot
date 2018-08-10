#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to print/download all incoming passport data
# This program is dedicated to the public domain under the CC0 license.
"""
See https://telegram.org/blog/passport for info about what telegram passport is.

To try this example with simple javascript SDK do the following:

1) Make sure you have openssl
2) Generate a private key by typing this in a terminal
> openssl genrsa 2048 > private.key
WARNING: Keep this key private
3) Generate a public key by typing this in a terminal
> openssl rsa -in private.key -pubout
4) Copy-paste the result of previous command into /setpublickey with @BotFather
5) Add a privacy policy to your bot that details how you intend to handle this data
6) Open examples/passportbot.html and insert your bot id and public key. Bot id is the part
before : in your bot token
7) Also in examples/passportbot.html decide what scopes (data) your bot needs
8) If you upload the examples/passportbot.html file to a server, put the url in the callback
url. For test/example purposes, example.org is fine.
9) Make sure that the SDK file from https://github.com/TelegramMessenger/TGPassportJsSDK is
download and in the same directory as examples/passportbot.html.
10) Make sure the private.key from step 2 is in the same folder as this file.
11) Start the bot by executing this file
12) Open examples/passportbot.html in a browser and click the button
13) This should open telegram with it's passport setup
14) After you've authorized the request, the bot will print and download all the data and files.

"""
import logging

from telegram.ext import Updater, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def msg(bot, update):
    # If we received any passport data
    passport_data = update.message.passport_data
    if passport_data:
        # Print the decrypted credential data
        # For all elements
        # Print their decrypted data
        # Files will be downloaded to current directory
        for data in passport_data.data:
            if data.type == 'phone_number':
                print('Phone: ', data.phone_number)
            elif data.type == 'email':
                print('Email: ', data.email)
            if data.type in ('personal_details', 'passport', 'driver_license', 'identity_card',
                             'identity_passport', 'address'):
                print(data.type, data.data)
            if data.type in ('utility_bill', 'bank_statement', 'rental_agreement',
                             'passport_registration', 'temporary_registration'):
                print(data.type, len(data.files), 'files')
                for file in data.files:
                    actual_file = file.get_file()
                    print(actual_file)
                    actual_file.download()
            if data.type in ('passport', 'driver_license', 'identity_card',
                             'internal_passport'):
                if data.front_side:
                    file = data.front_side.get_file()
                    print(data.type, file)
                    file.download()
            if data.type in ('driver_license' and 'identity_card'):
                if data.reverse_side:
                    file = data.reverse_side.get_file()
                    print(data.type, file)
                    file.download()
            if data.type in ('passport', 'driver_license', 'identity_card',
                             'internal_passport'):
                if data.selfie:
                    file = data.selfie.get_file()
                    print(data.type, file)
                    file.download()


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your token and private key
    updater = Updater("TOKEN", private_key=open('private.key', 'rb').read())

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # On messages that include passport data call msg
    dp.add_handler(MessageHandler(Filters.passport_data, msg))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
