#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""Basic example for a bot that can receive payments from users."""

import logging

from telegram import LabeledPrice, ShippingOption, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    ShippingQueryHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Set a higher logging level for httpx to avoid logging every GET and POST request
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Insert the token from your payment provider. In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
PAYMENT_PROVIDER_TOKEN = "PAYMENT_PROVIDER_TOKEN"


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provides instructions on how to use the bot."""
    msg = (
        "Use /shipping to receive an invoice with shipping included, or /noshipping for an "
        "invoice without shipping."
    )
    await update.message.reply_text(msg)


async def start_with_shipping_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends an invoice which triggers a shipping query because it requests a shipping address and has flexible shipping."""
    chat_id = update.message.chat_id
    title = "Payment Example"
    description = "Example of a payment process using the python-telegram-bot library."
    # Unique payload to identify this payment request as being from your bot
    payload = "Custom-Payload"
    # Set up the currency (e.g., "USD"), to get a list of supported currencies see https://core.telegram.org/bots/payments#supported-currencies
    currency = "USD"
    # Price in dollars
    price = 1
    # Convert price to cents from dollars.
    prices = [LabeledPrice("Test", price * 100)]

    # The following optional parameters can be used to request additional information:
    # - need_name=True: Requests the user's name.
    # - need_phone_number=True: Requests the user's phone number.
    # - need_email=True: Requests the user's email address.
    # - need_shipping_address=True: Requests the user's shipping address.
    # - is_flexible=True: Allows flexible shipping prices.
    await context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        PAYMENT_PROVIDER_TOKEN,
        currency,
        prices,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=True,
        is_flexible=True,
    )


async def start_without_shipping_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends an invoice without requiring shipping details."""
    chat_id = update.message.chat_id
    title = "Payment Example"
    description = "Example of a payment process using the python-telegram-bot library."
    # Unique payload to identify this payment request as being from your bot
    payload = "Custom-Payload"
    # Check line 49 for supported currencies
    currency = "USD"
    # Price in dollars
    price = 1
    # Convert price to cents from dollars.
    prices = [LabeledPrice("Test", price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    await context.bot.send_invoice(
        chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, prices
    )


async def shipping_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the ShippingQuery with available shipping options."""
    query = update.shipping_query
    # Verify if the payload matches, ensure it's from your bot
    if query.invoice_payload != "Custom-Payload":
        # If not, respond with an error
        await query.answer(ok=False, error_message="Something went wrong...")
        return

    # Define available shipping options
    # First option with a single price entry
    options = [ShippingOption("1", "Shipping Option A", [LabeledPrice("A", 100)])]
    # Second option with multiple price entries
    price_list = [LabeledPrice("B1", 150), LabeledPrice("B2", 200)]
    options.append(ShippingOption("2", "Shipping Option B", price_list))
    await query.answer(ok=True, shipping_options=options)


# After (optional) shipping, process the pre-checkout step
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds to the PreCheckoutQuery as the final confirmation for checkout."""
    query = update.pre_checkout_query
    # Verify if the payload matches, ensure it's from your bot
    if query.invoice_payload != "Custom-Payload":
        # If not, respond with an error
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)


# Final callback after successful payment
async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Acknowledges successful payment and thanks the user."""
    await update.message.reply_text("Thank you for your payment.")


def main() -> None:
    """Starts the bot and sets up handlers."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("TOKEN").build()

    # Start command to display usage instructions
    application.add_handler(CommandHandler("start", start_callback))

    # Command handlers for starting the payment process
    application.add_handler(CommandHandler("shipping", start_with_shipping_callback))
    application.add_handler(CommandHandler("noshipping", start_without_shipping_callback))

    # Handler for shipping query (if product requires shipping)
    application.add_handler(ShippingQueryHandler(shipping_callback))

    # Pre-checkout handler for verifying payment details.
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Handler for successful payment. Notify the user that the payment was successful.
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )

    # Start polling for updates until interrupted (CTRL+C)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
