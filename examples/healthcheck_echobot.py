#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Additional features:
- Configuration via environment variables allows to quickly
  check the connectivity in a certain test environment
- Added health check when run with webhook
  - check if the webhook url is properly set as expected
  - check if webhook is overridden by another bot instance
  - ask telegram api for communication errors with the bot within the last few minutes

Example set of environment variables to run with webhook:
TELEGRAM_AUTH_TOKEN=1234:AAbbCCddEEffGGhh
TELEGRAM_WEBHOOK=true
TELEGRAM_WEBHOOK_URL=https://bot.mysite.org
TELEGRAM_WEBHOOK_PORT=443
TELEGRAM_LISTEN_PORT=8443
LOG_LEVEL=DEBUG
SSL_CERT=webhook_cert.pem
SSL_KEY=webhook_key.pem

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import datetime
import logging
import os
import uuid
import requests

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def env_var(env_var_name, default, raise_on_not_found=False):
    if env_var_name not in os.environ:
        if raise_on_not_found:
            raise ValueError("Environment variable {} not defined".format(env_var_name))
        return default
    return os.environ[env_var_name]


def env_boolean(env_var_name, default=False):
    return env_var(env_var_name, str(default)).lower() == "true"


def env_int(env_var_name, default):
    return int(env_var(env_var_name, str(default)))


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=env_var("LOG_LEVEL", "INFO"))

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    auth_token = env_var("TELEGRAM_AUTH_TOKEN", default=None, raise_on_not_found=True)
    listen_port = env_int("TELEGRAM_LISTEN_PORT", default=443)
    listen_address = env_var("TELEGRAM_LISTEN_ADDRESS", default="0.0.0.0")

    # webhook port and listen port may differ when used in docker containers for example
    webhook_port = env_int("TELEGRAM_WEBHOOK_PORT", default=8443)
    use_webhook = env_boolean("TELEGRAM_WEBHOOK", False)
    webhook_url = env_var("TELEGRAM_WEBHOOK_URL", default=None, raise_on_not_found=use_webhook)
    ssl_cert = env_var("SSL_CERT", default="/app/config/webhook_cert.pem")
    ssl_key = env_var("SSL_KEY", default="/app/config/webhook_pkey.pem")

    now = datetime.datetime.now().strftime("%Y-%m-%d")
    url_path = "{}-{}".format(uuid.uuid4(), now)
    webhook_url = "{}:{}/{}/".format(webhook_url, webhook_port, url_path)

    updater = Updater(auth_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    if not use_webhook:
        logger.info("Using polling to get updates.")
        updater.start_polling()

    else:
        # add healthcheck
        def simple_available():
            return True, "up and running"

        def telegram_communication():
            telegram_api_info = "https://api.telegram.org/bot{token}/getWebhookInfo"
            response = requests.get(telegram_api_info.format(token=auth_token))
            result = response.json()
            # check if my webhook is the one telegram is using to contact me
            if "result" in result.keys() and "url" in result["result"].keys():
                telegram_webhook_url = result["result"]["url"]
                if telegram_webhook_url != webhook_url:
                    msg = "wrong webhook defined in telegram api for communication with the bot"
                    return False, msg

            # check for known errors by the telegram api
            if "result" in result.keys() and "last_error_date" in result["result"].keys():
                now = datetime.datetime.now()
                last_error = datetime.datetime.fromtimestamp(result["result"]["last_error_date"])
                seconds_since_error = (now - last_error).total_seconds()
                if seconds_since_error < 300:
                    msg = "communication error {} seconds ago"
                    return False, msg.format(int(seconds_since_error))

            if "ok" in result.keys():
                return True, "health ok"
            else:
                return False, "health check failed"

        updater.health.add_check(simple_available)
        updater.health.add_check(telegram_communication)

        logger.info("Using webhook at {}".format(webhook_url))
        updater.start_webhook(listen=listen_address,
                              port=listen_port,
                              url_path=url_path,
                              key=ssl_key,
                              cert=ssl_cert,
                              webhook_url=webhook_url)
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
