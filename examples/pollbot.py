#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that works with polls.
"""
import logging

from telegram import Poll
from telegram.ext import Updater, CommandHandler, PollAnswerHandler, PollHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Please select /poll to get a poll or /quiz to get a Quiz')


def poll(update, context):
    questions = ["Good", "Really good", "Fantastic", "Great"]
    message = context.bot.send_poll(update.effective_user.id, "how are you?", questions,
                                    is_anonymous=False, allows_multiple_answers=True)
    context.user_data.update({"questions": questions, "message_id": message.message_id,
                              "chat_id": update.effective_chat.id})


def receive_poll_answer(update, context):
    try:
        questions = context.user_data["questions"]
    # this means someone else answers the poll, nothing we can do with this though
    except KeyError:
        return
    selected_options = update.poll_answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    update.effective_user.send_message("Great, I also feel {}!".format(answer_string))
    if "message_id" in context.user_data:
        context.bot.stop_poll(context.user_data["chat_id"], context.user_data["message_id"])


QUIZ = {}


def quiz(update, context):
    questions = ["1", "2", "4", "20"]
    message = update.effective_message.reply_poll("How many eggs do you need for a cake?",
                                                  questions, type=Poll.QUIZ, correct_option_id=2)
    QUIZ[message.poll.id] = {"chat_id": update.effective_chat.id, "message_id": message.message_id}


def receive_quiz_answer(update, context):
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 3:
        try:
            quiz_data = QUIZ[update.poll.id]
        except ValueError:
            return
        context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


def help(update, context):
    update.message.reply_text("Use /quiz or /poll to test this bot.")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("TOKEN", use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('poll', poll))
    updater.dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    updater.dispatcher.add_handler(CommandHandler('quiz', quiz))
    updater.dispatcher.add_handler(PollHandler(receive_quiz_answer))
    updater.dispatcher.add_handler(CommandHandler('help', help))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
