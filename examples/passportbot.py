#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import logging

from telegram.ext import Updater, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def msg(bot, update):
    passport_data = update.message.passport_data
    if passport_data:
        print(update.message.passport_data.credentials.decrypted_data)
        for data in passport_data.data:
            if data.type == 'phone_number':
                print('Phone: ', data.phone_number)
            elif data.type == 'email':
                print('Email: ', data.email)
            if data.type in ('personal_details', 'passport', 'driver_license', 'identity_card',
                             'identity_passport', 'address'):
                print(data.type, data.decrypted_data)
            if data.type in ('utility_bill', 'bank_statement', 'rental_agreement',
                             'passport_registration', 'temporary_registration'):
                print(data.type, len(data.files), 'files')
                for file in data.files:
                    print(file.get_file())
            if data.type in ('passport', 'driver_license', 'identity_card',
                             'internal_passport'):
                if data.front_side:
                    print(data.type, data.front_side.get_file())
            if data.type in ('driver_license' and 'identity_card'):
                if data.reverse_side:
                    print(data.type, data.reverse_side.get_file())
            if data.type in ('passport', 'driver_license', 'identity_card',
                             'internal_passport'):
                if data.selfie:
                    print(data.type, data.selfie.get_file())


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token and private key.
    updater = Updater("TOKEN", private_key="PRIVATE_KEY")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.all, msg))

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
