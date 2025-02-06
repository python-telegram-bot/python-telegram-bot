#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.
"""State machine bot showcasing how concurrency can be handled with FSM.
How to use:

* Use Case 1: Concurrent balance updates
    - /unsafe_update <balance_update>: Unsafe update of the wallet balance. Send the command
        multiple times in quick succession (less than 1 second) to see the effect
    - /safe_update <balance_update>: Safe update of the wallet balance. Send the command
        multiple times in quick succession (less than 1 second) to see the effect

* Use Case 2: Declare a winner - who is the fastest?
    - /unsafe_declare_winner: Unsafe declaration of the user as winner. Send the command
        multiple times in quick succession (less than 1 second) to see the effect. Needs restart
        after the winner is declared.
    - /safe_declare_winner: Safe declaration of the user as winner. Send the command
        multiple times in quick succession (less than 1 second) to see the effect. Needs restart
        after the winner is declared.
"""
import asyncio
import logging

from telegram import Update
from telegram.constants import ChatAction
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


class ConcurrentMachine(FiniteStateMachine[None]):
    """This FSM only knows a global state for the whole bot"""

    UPDATING_BALANCE = State("UPDATING_BALANCE")
    WINNER_DECLARED = State("WINNER_DECLARED")

    def get_state_info(self, update: object) -> StateInfo[None]:
        state, version = self.states[None]
        return StateInfo(key=None, state=state, version=version)


########################################
# Use case 1: Concurrent balance updates
########################################


async def update_balance(context: ContextTypes.DEFAULT_TYPE, update: Update) -> None:
    initial_balance = context.bot_data.get("balance", 0)
    balance_update = int(context.args[0])
    # Simulate heavy computation
    await update.effective_message.reply_text(
        f"Initiating balance update: {initial_balance}. Updating ..."
    )
    await update.effective_chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(4.5)
    new_balance = context.bot_data["balance"] = initial_balance + balance_update
    await update.effective_message.reply_text(f"Balance updated. New balance: {new_balance}")


async def unsafe_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unsafe update of the wallet balance"""
    # Simulate heavy computation *before* the update is processed
    await asyncio.sleep(1)

    await context.fsm.set_state(context.fsm_state_info.key, ConcurrentMachine.UPDATING_BALANCE)

    # At this point, the lock is released such that multiple updates can update
    # the balance concurrently. This can lead to race conditions.
    await update_balance(context, update)

    await context.fsm.set_state(context.fsm_state_info.key, State.IDLE)


async def safe_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Safe update of the wallet balance"""
    # Simulate heavy computation *before* the update is processed
    await asyncio.sleep(1)

    async with context.as_fsm_state(ConcurrentMachine.UPDATING_BALANCE):
        # At this point, the lock is acquired such that only one update can update
        # the balance at a time. This prevents race conditions.
        await update_balance(context, update)


async def busy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Busy state"""
    await update.effective_message.reply_text("I'm busy, try again later.")


####################################################
# Use case 2: Declare a winner - who is the fastest?
####################################################


async def declare_winner_unsafe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Declare the user as winner"""
    # Simulate heavy computation *before* the update is processed
    await asyncio.sleep(1)

    # Unsafe state update: No version check, so the state might have already changed
    await context.fsm.set_state(context.fsm_state_info.key, ConcurrentMachine.WINNER_DECLARED)
    await update.effective_message.reply_text("You are the winner!")


async def declare_winner_safe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Declare the user as winner"""
    # Simulate heavy computation *before* the update is processed
    await asyncio.sleep(1)

    try:
        await context.set_state(ConcurrentMachine.WINNER_DECLARED)
        await update.effective_message.reply_text("You are the winner!")
    except ValueError:
        await update.effective_message.reply_text(
            "Sorry, you are too late. Someone else was faster."
        )


def main() -> None:
    application = Application.builder().token("TOKEN").concurrent_updates(True).build()
    application.fsm = ConcurrentMachine()

    # Note: OR-combination of states is used here to allow both use cases to be handled
    # in parallel. Not really necessary for the showcasing, just a nice touch :)

    # Use case 2: Declare a winner - who is the fastest?
    application.add_handler(
        CommandHandler("unsafe_declare_winner", declare_winner_unsafe),
        state=State.IDLE | ConcurrentMachine.UPDATING_BALANCE,
    )
    application.add_handler(
        CommandHandler("safe_declare_winner", declare_winner_safe),
        state=State.IDLE | ConcurrentMachine.UPDATING_BALANCE,
    )

    # Use case 1: Concurrent balance updates
    application.add_handler(
        CommandHandler("unsafe_update", unsafe_update, has_args=1),
        state=State.IDLE | ConcurrentMachine.WINNER_DECLARED,
    )
    application.add_handler(
        CommandHandler("safe_update", safe_update, has_args=1),
        state=State.IDLE | ConcurrentMachine.WINNER_DECLARED,
    )
    # Order matters, so this needs to be added last
    application.add_handler(
        MessageHandler(filters.ALL, busy), state=ConcurrentMachine.UPDATING_BALANCE
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
