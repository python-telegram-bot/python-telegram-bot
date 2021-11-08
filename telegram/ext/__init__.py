#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
# pylint: disable=C0413
"""Extensions over the Telegram Bot API to facilitate bot making"""

from .extbot import ExtBot
from .basepersistence import BasePersistence
from .picklepersistence import PicklePersistence
from .dictpersistence import DictPersistence
from .handler import Handler
from .callbackcontext import CallbackContext
from .contexttypes import ContextTypes
from .dispatcher import Dispatcher, DispatcherHandlerStop, run_async

# https://bugs.python.org/issue41451, fixed on 3.7+, doesn't actually remove slots
# try-except is just  here in case the __init__ is called twice (like in the tests)
# this block is also the reason for the pylint-ignore at the top of the file
try:
    del Dispatcher.__slots__
except AttributeError as exc:
    if str(exc) == '__slots__':
        pass
    else:
        raise exc

from .jobqueue import JobQueue, Job
from .updater import Updater
from .callbackqueryhandler import CallbackQueryHandler
from .choseninlineresulthandler import ChosenInlineResultHandler
from .inlinequeryhandler import InlineQueryHandler
from .filters import BaseFilter, MessageFilter, UpdateFilter, Filters
from .messagehandler import MessageHandler
from .commandhandler import CommandHandler, PrefixHandler
from .regexhandler import RegexHandler
from .stringcommandhandler import StringCommandHandler
from .stringregexhandler import StringRegexHandler
from .typehandler import TypeHandler
from .conversationhandler import ConversationHandler
from .precheckoutqueryhandler import PreCheckoutQueryHandler
from .shippingqueryhandler import ShippingQueryHandler
from .messagequeue import MessageQueue
from .messagequeue import DelayQueue
from .pollanswerhandler import PollAnswerHandler
from .pollhandler import PollHandler
from .chatmemberhandler import ChatMemberHandler
from .chatjoinrequesthandler import ChatJoinRequestHandler
from .defaults import Defaults
from .callbackdatacache import CallbackDataCache, InvalidCallbackData

__all__ = (
    'BaseFilter',
    'BasePersistence',
    'CallbackContext',
    'CallbackDataCache',
    'CallbackQueryHandler',
    'ChatJoinRequestHandler',
    'ChatMemberHandler',
    'ChosenInlineResultHandler',
    'CommandHandler',
    'ContextTypes',
    'ConversationHandler',
    'Defaults',
    'DelayQueue',
    'DictPersistence',
    'Dispatcher',
    'DispatcherHandlerStop',
    'ExtBot',
    'Filters',
    'Handler',
    'InlineQueryHandler',
    'InvalidCallbackData',
    'Job',
    'JobQueue',
    'MessageFilter',
    'MessageHandler',
    'MessageQueue',
    'PicklePersistence',
    'PollAnswerHandler',
    'PollHandler',
    'PreCheckoutQueryHandler',
    'PrefixHandler',
    'RegexHandler',
    'ShippingQueryHandler',
    'StringCommandHandler',
    'StringRegexHandler',
    'TypeHandler',
    'UpdateFilter',
    'Updater',
    'run_async',
)
