#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using nested ConversationHandlers.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# State definitions for top level conversation
SELECTING_ACTION, ADDING_PARENT, ADDING_CHILD = map(chr, range(3))
# State definitions for second level conversation
SELECTING_GENDER, DESCRIBING = map(chr, range(4, 6))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# Meta states
STOPPING, SHOWING, SHOWING_NESTED = map(chr, range(8, 11))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Different constants for this example
(PARENTS, CHILDREN, GENDER, MALE, FEMALE, AGE, NAME, START_OVER, FEATURES,
 CURRENT_FEATURE, CURRENT_LEVEL) = map(chr, range(11, 22))


# Top level conversation callbacks
def start(update, context):
    """Select an action: Adding prante/child or show data."""
    parents = context.user_data.get(PARENTS)
    if parents and len(parents) == 2:
        text = 'You already added both the mother and the father. ' \
               'Your may add a child, show the gathered data or end the conversation.'
        buttons = [[
            InlineKeyboardButton(text='Add Child', callback_data=str(ADDING_CHILD)),
            InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
            InlineKeyboardButton(text='Done', callback_data=str(END))
        ]]
    else:
        text = 'You may add a parent, add a child, show the gathered data or end the ' \
               'conversation. To abort, simply type /stop.'
        buttons = [[
            InlineKeyboardButton(text='Add parent', callback_data=str(ADDING_PARENT)),
            InlineKeyboardButton(text='Add child', callback_data=str(ADDING_CHILD))
        ], [
            InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
            InlineKeyboardButton(text='Done', callback_data=str(END))
        ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need do send a new message
    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text('Hi, I\'m FamiliyBot and here to help you gather information'
                                  'about your family.')
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    text = 'See you around!'
    update.callback_query.edit_message_text(text=text)

    return END


def child_data(user_data):
    children = user_data.get(CHILDREN)
    if not children:
        return 'No information about children yet.'

    text = 'CHILDREN:'
    for child in user_data[CHILDREN]:
        gender = 'Daughter' if child[GENDER] == FEMALE else 'Son'
        text += '\n{0}: Name: {1}, Age: {2}'.format(gender, child.get(NAME, '-'),
                                                    child.get(AGE, '-'))
    return text


def parent_data(user_data):
    parents = user_data.get(PARENTS)
    if not parents:
        return 'No information about parents yet.'

    text = 'PARENTS:'
    for parent in user_data[PARENTS]:
        gender = 'Mother' if parent[GENDER] == FEMALE else 'Father'
        text += '\n{0}: Name: {1}, Age: {2}'.format(gender, parent.get(NAME, '-'),
                                                    parent.get(AGE, '-'))
    return text


def show_data(update, context):
    """Pretty print gathered data."""
    ud = context.user_data
    text = parent_data(ud) + '\n\n' + child_data(ud)

    buttons = [[
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    ud[START_OVER] = True

    return SHOWING


def stop(update, context):
    """End Conversation by command."""
    update.message.reply_text('Okay, bye.')

    return END


# Second level callbacks
def add_parent(update, context):
    """Choose to add mother or father."""
    parents = context.user_data.get(PARENTS)
    if not parents:
        text = 'Which parent do you want to add first?'
        buttons = [[
            InlineKeyboardButton(text='Mother', callback_data=str(FEMALE)),
            InlineKeyboardButton(text='Father', callback_data=str(MALE))
        ], [
            InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
            InlineKeyboardButton(text='Done', callback_data=str(END))
        ]]
    elif len(parents) == 2:
        text = 'You already added both parents. Sorry, but this example doesn\'t support ' \
               'patchwork families.'
        buttons = [[
            InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
            InlineKeyboardButton(text='Done', callback_data=str(END))
        ]]
    else:
        gender = parents[0][GENDER]
        if gender == MALE:
            parent_text = 'father'
            missing_parent_text = 'mother'
            missing_gender = FEMALE
        else:
            parent_text = 'mother'
            missing_parent_text = 'father'
            missing_gender = MALE
        text = 'You already added the {0}. Press the button ' \
               'to add the {1}'.format(parent_text, missing_parent_text)
        buttons = [[
            InlineKeyboardButton(text='Add {0}'.format(missing_parent_text),
                                 callback_data=str(missing_gender)),
            InlineKeyboardButton(text='Show data', callback_data=str(PARENTS) + str(SHOWING)),
            InlineKeyboardButton(text='Done', callback_data=str(END))
        ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    context.user_data[CURRENT_LEVEL] = PARENTS

    return DESCRIBING


def add_child(update, context):
    """Choose to add daughter or son."""
    print('1')
    text = 'Do you want to add a son or a daughter?'
    buttons = [[
        InlineKeyboardButton(text='Son', callback_data=str(MALE)),
        InlineKeyboardButton(text='Daughter', callback_data=str(FEMALE))
    ], [
        InlineKeyboardButton(text='Show data', callback_data=str(CHILDREN) + str(SHOWING)),
        InlineKeyboardButton(text='Done', callback_data=str(END)),
    ]]
    print('2')
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    print('3')
    context.user_data[CURRENT_LEVEL] = CHILDREN

    return DESCRIBING


def show_parent_data(update, context):
    """Show gathered data for parents."""
    text = parent_data(context.user_data)

    buttons = [[
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return SHOWING_NESTED


def show_child_data(update, context):
    """Show gathered data for children."""
    text = child_data(context.user_data)

    buttons = [[
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return SHOWING_NESTED


def end_second_level(update, context):
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    start(update, context)

    return END


# Third level callbacks
def select_feature(update, context):
    """Select a feature to update for a person."""
    buttons = [[
        InlineKeyboardButton(text='Name', callback_data=str(NAME)),
        InlineKeyboardButton(text='Age', callback_data=str(AGE)),
        InlineKeyboardButton(text='Done', callback_data=str(END)),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we collect features for a new person, clear the cache and save the gender
    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {GENDER: update.callback_query.data}
        text = 'Please select a feature to update.'
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = 'Got it! Please select a feature to update.'
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE


def ask_for_input(update, context):
    """Prompt user to input data for selected feature."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Okay, tell me.'
    update.callback_query.edit_message_text(text=text)

    return TYPING


def save_input(update, context):
    """Save input for feature and return to feature selection."""
    ud = context.user_data
    ud[FEATURES][ud[CURRENT_FEATURE]] = update.message.text

    ud[START_OVER] = True

    return select_feature(update, context)


def end_describing(update, context):
    """End gathering of features and return to parent conversation."""
    ud = context.user_data
    level = ud[CURRENT_LEVEL]
    if not ud.get(level):
        ud[level] = []
    ud[level].append(ud[FEATURES])

    if level == PARENTS:
        add_parent(update, context)
    elif level == CHILDREN:
        add_child(update, context)

    return END


def stop_nested(update, context):
    """Completely end conversation from nested conversation."""
    update.message.reply_text('Okay, bye.')

    return STOPPING


# Error handler
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Set up Description-Conversation to use in both the parents and the childrens conversation
    description_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_feature,
                                           pattern='^' + str(MALE) + '$|^' + str(FEMALE) + '$')],

        states={
            SELECTING_FEATURE: [CallbackQueryHandler(ask_for_input,
                                                     pattern='^(?!' + str(END) + ').*$')],
            TYPING: [MessageHandler(Filters.text, save_input)],
        },

        fallbacks=[
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            # Return to second level menu
            END: DESCRIBING,
            # End conversation alltogether
            STOPPING: STOPPING,
        }
    )

    # Set up the main ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SHOWING: [CallbackQueryHandler(start, pattern='^' + str(END) + '$')],
            SELECTING_ACTION: [
                CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
                # For adding parents
                ConversationHandler(
                    entry_points=[CallbackQueryHandler(add_parent,
                                                       pattern='^' + str(ADDING_PARENT) + '$')],

                    states={
                        DESCRIBING: [
                            description_conv,
                            CallbackQueryHandler(show_parent_data,
                                                 pattern='^' + str(PARENTS) + str(SHOWING) + '$')
                        ]
                    },

                    fallbacks=[
                        CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
                        CommandHandler('stop', stop_nested)
                    ],

                    map_to_parent={
                        # Return to top level menu
                        END: SELECTING_ACTION,
                        # Return to top level menu after showing data
                        SHOWING_NESTED: SHOWING,
                        # End conversation alltogether
                        STOPPING: END,
                    }
                ),
                # For adding children
                ConversationHandler(
                    entry_points=[CallbackQueryHandler(add_child,
                                                       pattern='^' + str(ADDING_CHILD) + '$')],

                    states={
                        DESCRIBING: [
                            description_conv,
                            CallbackQueryHandler(show_child_data,
                                                 pattern='^' + str(CHILDREN) + str(SHOWING) + '$')
                        ]
                    },

                    fallbacks=[
                        CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
                        CommandHandler('stop', stop_nested)
                    ],

                    map_to_parent={
                        # Return to top level menu
                        END: SELECTING_ACTION,
                        # Return to top level menu after showing data
                        SHOWING_NESTED: SHOWING,
                        # End conversation alltogether
                        STOPPING: END,
                    }
                )
            ],
        },

        fallbacks=[CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
                   CommandHandler('stop', stop)],
    )

    dp.add_handler(conv_handler)

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
