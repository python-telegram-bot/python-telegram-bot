#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.
"""Simple state machine to handle user support.
One admin is supported. The admin can have one active conversation at a time. Other users
are put on hold until the admin finishes the current conversation.
In each conversation, the admin and the user take turns to send messages.
"""
import logging
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    FiniteStateMachine,
    MessageHandler,
    State,
    StateInfo,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("telegram.ext.Application").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


class UserSupportMachine(FiniteStateMachine[Optional[int]]):

    HOLD = State("HOLD")
    WELCOMING = State("WELCOMING")
    WAITING_FOR_REPLY = State("WAITING_FOR_REPLY")
    WRITING = State("WRITING")

    def __init__(self, admin_id: int):
        self.admin_id = admin_id
        super().__init__()

    def _get_admin_state(self) -> tuple[State, int]:
        return self._states[self.admin_id]

    def get_state_info(self, update: object) -> StateInfo[Optional[int]]:
        if not isinstance(update, Update) or not (user := update.effective_user):
            key = None
            state, version = self.states[key]
            return StateInfo(key=key, state=state, version=version)

        # Admin is easy - just return the state
        admin_state, admin_version = self._get_admin_state()
        if user.id == self.admin_id:
            logging.debug("Returning admin state: %s", admin_state)
            return StateInfo(self.admin_id, admin_state, admin_version)

        # If the user state is active in the conversation, we can just return that state
        user_state, user_version = self._states[user.id]
        if user_state.matches(self.WELCOMING | self.WRITING | self.WAITING_FOR_REPLY):
            logging.debug("Returning user state: %s", user_state)
            return StateInfo(user.id, user_state, user_version)

        # On first interaction, we need to determine what to do with the user
        # if the admin is not idle, we put the user on hold. Otherwise, they may send the first
        # message, and we put the admin in waiting for reply to avoid another user occupying the
        # admin first
        effective_user_state = self.HOLD if admin_state != State.IDLE else self.WELCOMING
        self._do_set_state(user.id, effective_user_state, user_version)
        if effective_user_state == self.WELCOMING:
            self._do_set_state(self.admin_id, self.WAITING_FOR_REPLY)

        logging.debug("Returning user state: %s", effective_user_state)
        return StateInfo(user.id, effective_user_state, user_version)


async def welcome_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.forward(context.bot_data["admin_id"])
    suffix = ""
    if UserSupportMachine.HOLD in context.fsm.get_state_history(context.fsm_state_info.key)[:-1]:
        suffix = " Thank you for patiently waiting. We hope you enjoyed the music."

    await update.effective_message.reply_text(
        "Welcome! Your message has been forwarded to the admin. "
        f"They will get back to you soon.{suffix}"
    )
    await context.set_state(UserSupportMachine.WAITING_FOR_REPLY)
    await context.fsm.set_state(context.bot_data["admin_id"], UserSupportMachine.WRITING)
    context.bot_data["active_user"] = update.effective_user.id


async def conversation_timeout(context: ContextTypes.DEFAULT_TYPE) -> None:
    active_user = context.bot_data.get("active_user")
    admin_id = context.bot_data["admin_id"]

    async def handle(user_id: int) -> None:
        await context.bot.send_message(
            user_id, "The conversation has been stopped due to inactivity."
        )
        await context.fsm.set_state(user_id, State.IDLE)

    if active_user:
        await handle(active_user)
    await handle(admin_id)


async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (active_user := context.bot_data.get("active_user")):
        logger.warning("No active user found, ignoring message")

    target = (
        active_user
        if update.effective_user.id == (admin_id := context.bot_data["admin_id"])
        else admin_id
    )
    await context.bot.send_message(target, update.effective_message.text)
    logging.debug("Forwarded message to %s", target)
    await context.set_state(UserSupportMachine.WAITING_FOR_REPLY)
    logging.debug("Done setting state to WAITING_FOR_REPLY for %s", target)
    await context.fsm.set_state(target, UserSupportMachine.WRITING)
    logging.debug("Done setting state to WRITING for %s, context.fsm_key")

    context.fsm.schedule_timeout(
        when=30,
        callback=conversation_timeout,
        cancel_keys=[active_user, admin_id],
    )


async def stop_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "The conversation has been stopped."
    admin_id = context.bot_data["admin_id"]
    active_user = context.bot_data.get("active_user")

    await context.bot.send_message(admin_id, text)
    await context.fsm.set_state(admin_id, State.IDLE)
    if active_user:
        await context.bot.send_message(active_user, text)
        await context.fsm.set_state(active_user, State.IDLE)


async def hold_melody(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "You have been put on hold. The admin will get back to you soon. Please hear some music "
        "while you wait: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )


async def not_your_turn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "It's not your turn yet. Please wait for the other party to reply to your message."
    )


async def unsupported_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("This message is not supported.")


def main() -> None:
    application = Application.builder().token("TOKEN").build()
    application.fsm = UserSupportMachine(admin_id=123456)
    application.fsm.set_job_queue(application.job_queue)
    application.bot_data["admin_id"] = application.fsm.admin_id

    # Users are welcomed only if they are in the corresponding state
    application.add_handler(
        MessageHandler(~filters.User(application.fsm.admin_id) & filters.TEXT, welcome_user),
        state=UserSupportMachine.WELCOMING,
    )

    # Conversation logic:
    # * forward messages between user and admin
    # * stop the conversation at any time (admin or user)
    # * point out that the other party is currently writing
    # Important: Order matters!
    application.add_handler(
        CommandHandler("stop", stop_conversation),
        state=UserSupportMachine.WAITING_FOR_REPLY | UserSupportMachine.WRITING,
    )
    application.add_handler(
        MessageHandler(filters.TEXT, handle_reply), state=UserSupportMachine.WRITING
    )
    application.add_handler(
        MessageHandler(filters.TEXT, not_your_turn), state=UserSupportMachine.WAITING_FOR_REPLY
    )

    # If the admin is busy, put the user on hold
    application.add_handler(
        MessageHandler(filters.TEXT, hold_melody), state=UserSupportMachine.HOLD
    )

    # Fallback
    application.add_handler(MessageHandler(filters.ALL, unsupported_message), state=State.ANY)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
