#!/usr/bin/env python
# This program is dedicated to the public domain under the CC0 license.
# pylint: disable=import-error,unused-argument
"""
Simple example of a bot that uses a custom webhook setup and handles custom updates.
For the custom webhook setup, the libraries `quart` and `uvicorn` are used. Please
install them as `pip install quart~=0.18.4 uvicorn~=0.23.2`.
Note that any other `asyncio` based web server framework can be used for a custom webhook setup
just as well.

Usage:
Set bot Token, URL, admin CHAT_ID and PORT after the imports.
You may also need to change the `listen` value in the uvicorn configuration to match your setup.
Press Ctrl-C on the command line or send a signal to the process to stop the bot.
"""

import asyncio
import html
import logging
from dataclasses import dataclass
from http import HTTPStatus

import uvicorn
from quart import Quart, Response, abort, make_response, request

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ExtBot,
    TypeHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define configuration constants
URL = "https://domain.tld"
ADMIN_CHAT_ID = 123456
PORT = 8000
TOKEN = "123:ABC"  # nosec B105


@dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type"""

    user_id: int
    payload: str


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


async def start(update: Update, context: CustomContext) -> None:
    """Display a message with instructions on how to use this bot."""
    payload_url = html.escape(f"{URL}/submitpayload?user_id=<your user id>&payload=<payload>")
    text = (
        f"To check if the bot is still running, call <code>{URL}/healthcheck</code>.\n\n"
        f"To post a custom update, call <code>{payload_url}</code>."
    )
    await update.message.reply_html(text=text)


async def webhook_update(update: WebhookUpdate, context: CustomContext) -> None:
    """Handle custom updates."""
    chat_member = await context.bot.get_chat_member(chat_id=update.user_id, user_id=update.user_id)
    payloads = context.user_data.setdefault("payloads", [])
    payloads.append(update.payload)
    combined_payloads = "</code>\n• <code>".join(payloads)
    text = (
        f"The user {chat_member.user.mention_html()} has sent a new payload. "
        f"So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode=ParseMode.HTML)


async def main() -> None:
    """Set up PTB application and a web application for handling the incoming requests."""
    context_types = ContextTypes(context=CustomContext)
    # Here we set updater to None because we want our custom webhook server to handle the updates
    # and hence we don't need an Updater instance
    application = (
        Application.builder().token(TOKEN).updater(None).context_types(context_types).build()
    )

    # register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(TypeHandler(type=WebhookUpdate, callback=webhook_update))

    # Pass webhook settings to telegram
    await application.bot.set_webhook(url=f"{URL}/telegram", allowed_updates=Update.ALL_TYPES)

    # Set up webserver
    quart_app = Quart(__name__)

    @quart_app.post("/telegram")  # type: ignore[misc]
    async def telegram() -> Response:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        await application.update_queue.put(
            Update.de_json(data=await request.get_json(), bot=application.bot)
        )
        return Response(status=HTTPStatus.OK)

    @quart_app.route("/submitpayload", methods=["GET", "POST"])  # type: ignore[misc]
    async def custom_updates() -> Response:
        """
        Handle incoming webhook updates by also putting them into the `update_queue` if
        the required parameters were passed correctly.
        """
        try:
            user_id = int(request.args["user_id"])
            payload = request.args["payload"]
        except KeyError:
            abort(
                HTTPStatus.BAD_REQUEST,
                "Please pass both `user_id` and `payload` as query parameters.",
            )
        except ValueError:
            abort(HTTPStatus.BAD_REQUEST, "The `user_id` must be a string!")

        await application.update_queue.put(WebhookUpdate(user_id=user_id, payload=payload))
        return Response(status=HTTPStatus.OK)

    @quart_app.get("/healthcheck")  # type: ignore[misc]
    async def health() -> Response:
        """For the health endpoint, reply with a simple plain text message."""
        response = await make_response("The bot is still running fine :)", HTTPStatus.OK)
        response.mimetype = "text/plain"
        return response

    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=quart_app,
            port=PORT,
            use_colors=False,
            host="127.0.0.1",
        )
    )

    # Run application and webserver together
    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())
