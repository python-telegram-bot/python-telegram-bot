#!/usr/bin/env python
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user interacting with the pot.
Send /start to initiate the conversation.
Send /quiz to get a quiz poll. Choosing an option shows whether the answer is correct
and sends a button the user can click to get another question.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Poll, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PersistenceInput,
    PicklePersistence,
    PollHandler,
    filters,
)

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# sample questions
QUESTIONS = [
    {
        "text": "Which of these features was added in the 1994 game 'Heretic' \
            that the original 'DOOM' could not add due to limitations?",
        "answers": [
            "Increased room sizes",
            "Unlimited weapons",
            "Looking up and down",
            "Highly-detailed textures",
        ],
        "answer_index": 2,
    },
    {
        "text": "What is the largest Muslim country in the world?",
        "answers": ["Indonesia", "Pakistan", "Saudi Arabia", "Iran"],
        "answer_index": 0,
    },
    {
        "text": "What is the 4th boss in the 1997 video game 'Crash Bandicoot 2: \
            Cortex Strikes Back'?",
        "answers": [
            "Dr. Neo Cortex",
            "Dr. N. Gin",
            "Komodo Brothers",
            "Tiny Tiger",
        ],
        "answer_index": 1,
    },
    {
        "text": "Which of these plays was famously first performed posthumously \
            after the playwright committed suicide?",
        "answers": [
            "Hamilton",
            "4.48 Psychosis",
            "Much Ado About Nothing",
            "The Birthday Party",
        ],
        "answer_index": 1,
    },
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        update.effective_chat.id,
        f"Hi {update.effective_user.first_name}. Use /quiz to get a question from the bot",
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a question to the user"""
    # simulate getting a question from an api
    question: dict = random.choice(QUESTIONS)

    if update.callback_query:
        await update.callback_query.edit_message_reply_markup()

    message = await update.effective_message.reply_poll(
        question.get("text"),
        question.get("answers"),
        type=Poll.QUIZ,
        correct_option_id=question.get("answer_index"),
    )
    # data to be used in receive_quiz_answer
    payload = {
        message.poll.id: {
            "chat_id": update.effective_chat.id,
            "message_id": message.message_id,
        }
    }

    context.bot_data.update(payload)


async def receive_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive an answer from the user and ask if they want another question"""
    if not update.poll.is_closed:
        try:
            payload = context.bot_data.get(update.poll.id)
            chat_id = payload.get("chat_id")
            message_id = payload.get("message_id")

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Next Question", callback_data="next")]]
            )

            await context.bot.stop_poll(chat_id, message_id, reply_markup=reply_markup)
            del context.bot_data[update.poll.id]

        except AttributeError as e:
            logger.error("Error occurred!", exc_info=e)


def main() -> None:
    # store only bot_data where the quiz data will be saved
    persistence_input = PersistenceInput(
        chat_data=False,
        callback_data=False,
        user_data=False,
    )
    persistence = PicklePersistence(
        filepath=".bot_data",
        store_data=persistence_input,
    )
    app = ApplicationBuilder().token("TOKEN").persistence(persistence).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CallbackQueryHandler(quiz, "next"))
    app.add_handler(PollHandler(receive_quiz_answer))
    # sending any other command will return the help message
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.run_polling()


if __name__ == "__main__":
    main()
