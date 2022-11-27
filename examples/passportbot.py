#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to print/download all incoming passport data

See https://telegram.org/blog/passport for info about what telegram passport is.

See https://github.com/python-telegram-bot/python-telegram-bot/wiki/Telegram-Passport
 for how to use Telegram Passport properly with python-telegram-bot.

Note:
To use Telegram Passport, you must install PTB via
`pip install python-telegram-bot[passport]`
"""
import logging
from pathlib import Path

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# Enable logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Downloads and prints the received passport data."""
    # Retrieve passport data
    passport_data = update.message.passport_data
    # If our nonce doesn't match what we think, this Update did not originate from us
    # Ideally you would randomize the nonce on the server
    if passport_data.decrypted_credentials.nonce != "thisisatest":
        return

    # Print the decrypted credential data
    # For all elements
    # Print their decrypted data
    # Files will be downloaded to current directory
    for data in passport_data.decrypted_data:  # This is where the data gets decrypted
        if data.type == "phone_number":
            print("Phone: ", data.phone_number)
        elif data.type == "email":
            print("Email: ", data.email)
        if data.type in (
            "personal_details",
            "passport",
            "driver_license",
            "identity_card",
            "internal_passport",
            "address",
        ):
            print(data.type, data.data)
        if data.type in (
            "utility_bill",
            "bank_statement",
            "rental_agreement",
            "passport_registration",
            "temporary_registration",
        ):
            print(data.type, len(data.files), "files")
            for file in data.files:
                actual_file = await file.get_file()
                print(actual_file)
                await actual_file.download_to_drive()
        if (
            data.type in ("passport", "driver_license", "identity_card", "internal_passport")
            and data.front_side
        ):
            front_file = await data.front_side.get_file()
            print(data.type, front_file)
            await front_file.download_to_drive()
        if data.type in ("driver_license" and "identity_card") and data.reverse_side:
            reverse_file = await data.reverse_side.get_file()
            print(data.type, reverse_file)
            await reverse_file.download_to_drive()
        if (
            data.type in ("passport", "driver_license", "identity_card", "internal_passport")
            and data.selfie
        ):
            selfie_file = await data.selfie.get_file()
            print(data.type, selfie_file)
            await selfie_file.download_to_drive()
        if data.translation and data.type in (
            "passport",
            "driver_license",
            "identity_card",
            "internal_passport",
            "utility_bill",
            "bank_statement",
            "rental_agreement",
            "passport_registration",
            "temporary_registration",
        ):
            print(data.type, len(data.translation), "translation")
            for file in data.translation:
                actual_file = await file.get_file()
                print(actual_file)
                await actual_file.download_to_drive()


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your token and private key
    private_key = Path("private.key")
    application = (
        Application.builder().token("TOKEN").private_key(private_key.read_bytes()).build()
    )

    # On messages that include passport data call msg
    application.add_handler(MessageHandler(filters.PASSPORT_DATA, msg))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
