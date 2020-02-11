#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that works with polls. Only 3 people are allowed to interact with each
poll/quiz the bot generates. The preview command generates a closed poll/quiz, excatly like the
one the user sends the bot
"""
import logging

from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram.utils.helpers import mention_html

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Please select /poll to get a Poll, /quiz to get a Quiz or /preview'
                              ' to generate a preview for your poll')


def poll(update, context):
    questions = ["Good", "Really good", "Fantastic", "Great"]
    message = context.bot.send_poll(update.effective_user.id, "how are you?", questions,
                                    is_anonymous=False, allows_multiple_answers=True)
    payload = {message.poll.id: {"questions": questions, "message_id": message.message_id,
                                 "chat_id": update.effective_chat.id, "answers": 0}}
    context.bot_data.update(payload)


def receive_poll_answer(update, context):
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    user_mention = mention_html(update.effective_user.id, update.effective_user.full_name)
    context.bot.send_message(context.bot_data[poll_id]["chat_id"],
                             "{} feels {}!".format(user_mention, answer_string),
                             parse_mode=ParseMode.HTML)
    context.bot_data[poll_id]["answers"] += 1
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(context.bot_data[poll_id]["chat_id"],
                              context.bot_data[poll_id]["message_id"])


def quiz(update, context):
    questions = ["1", "2", "4", "20"]
    message = update.effective_message.reply_poll("How many eggs do you need for a cake?",
                                                  questions, type=Poll.QUIZ, correct_option_id=2)
    payload = {message.poll.id: {"chat_id": update.effective_chat.id,
                                 "message_id": message.message_id}}
    context.bot_data.update(payload)


def receive_quiz_answer(update, context):
    # the bot can receive closed poll updates we don't care about
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 3:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return
        context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


def preview(update, context):
    # using this without a type lets the user chooses what he wants (quiz or poll)
    button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
    message = "Press the button to let the bot generate a preview for your poll"
    # using one_time_keyboard to hide the keyboard
    update.effective_message.reply_text(message,
                                        reply_markup=ReplyKeyboardMarkup(button,
                                                                         one_time_keyboard=True))


def receive_poll(update, context):
    actual_poll = update.effective_message.poll
    # turning the object to a dict to pass it as parameters later on
    poll_dict = actual_poll.to_dict()
    # deleting unwanted parameters
    del poll_dict['total_voter_count']
    del poll_dict['id']
    del poll_dict['is_closed']
    # we need to replace the generated PollOption dicts with an string list
    temp_list = []
    for option in poll_dict['options']:
        temp_list.append(option['text'])
    poll_dict['options'] = temp_list
    # with is_closed true, the poll/quiz is immediately closed
    update.effective_message.reply_poll(**poll_dict, is_closed=True,
                                        reply_markup=ReplyKeyboardRemove())


def help_handler(update, context):
    update.message.reply_text("Use /quiz, /poll or /preview to test this "
                              "bot.")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("TOKEN", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('poll', poll))
    dp.add_handler(PollAnswerHandler(receive_poll_answer))
    dp.add_handler(CommandHandler('quiz', quiz))
    dp.add_handler(PollHandler(receive_quiz_answer))
    dp.add_handler(CommandHandler('preview', preview))
    dp.add_handler(MessageHandler(Filters.poll, receive_poll))
    dp.add_handler(CommandHandler('help', help_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
