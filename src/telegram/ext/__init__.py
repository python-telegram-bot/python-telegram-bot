#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""Extensions over the Telegram Bot API to facilitate bot making"""

__all__ = (
    "AIORateLimiter",
    "Application",
    "ApplicationBuilder",
    "ApplicationHandlerStop",
    "BaseHandler",
    "BasePersistence",
    "BaseRateLimiter",
    "BaseUpdateProcessor",
    "BusinessConnectionHandler",
    "BusinessMessagesDeletedHandler",
    "CallbackContext",
    "CallbackDataCache",
    "CallbackQueryHandler",
    "ChatBoostHandler",
    "ChatJoinRequestHandler",
    "ChatMemberHandler",
    "ChosenInlineResultHandler",
    "CommandHandler",
    "ContextTypes",
    "ConversationHandler",
    "Defaults",
    "DictPersistence",
    "ExtBot",
    "InlineQueryHandler",
    "InvalidCallbackData",
    "Job",
    "JobQueue",
    "ManagedBotUpdatedHandler",
    "MessageHandler",
    "MessageReactionHandler",
    "PaidMediaPurchasedHandler",
    "PersistenceInput",
    "PicklePersistence",
    "PollAnswerHandler",
    "PollHandler",
    "PreCheckoutQueryHandler",
    "PrefixHandler",
    "ShippingQueryHandler",
    "SimpleUpdateProcessor",
    "StringCommandHandler",
    "StringRegexHandler",
    "TypeHandler",
    "Updater",
    "filters",
)

__lazy_modules__ = [
    "telegram.ext",
    "telegram.ext._aioratelimiter",
    "telegram.ext._application",
    "telegram.ext._applicationbuilder",
    "telegram.ext._basepersistence",
    "telegram.ext._baseratelimiter",
    "telegram.ext._baseupdateprocessor",
    "telegram.ext._callbackcontext",
    "telegram.ext._callbackdatacache",
    "telegram.ext._contexttypes",
    "telegram.ext._defaults",
    "telegram.ext._dictpersistence",
    "telegram.ext._extbot",
    "telegram.ext._handlers.basehandler",
    "telegram.ext._handlers.businessconnectionhandler",
    "telegram.ext._handlers.businessmessagesdeletedhandler",
    "telegram.ext._handlers.callbackqueryhandler",
    "telegram.ext._handlers.chatboosthandler",
    "telegram.ext._handlers.chatjoinrequesthandler",
    "telegram.ext._handlers.chatmemberhandler",
    "telegram.ext._handlers.choseninlineresulthandler",
    "telegram.ext._handlers.commandhandler",
    "telegram.ext._handlers.conversationhandler",
    "telegram.ext._handlers.inlinequeryhandler",
    "telegram.ext._handlers.managedbotupdatedhandler",
    "telegram.ext._handlers.messagehandler",
    "telegram.ext._handlers.messagereactionhandler",
    "telegram.ext._handlers.paidmediapurchasedhandler",
    "telegram.ext._handlers.pollanswerhandler",
    "telegram.ext._handlers.pollhandler",
    "telegram.ext._handlers.precheckoutqueryhandler",
    "telegram.ext._handlers.prefixhandler",
    "telegram.ext._handlers.shippingqueryhandler",
    "telegram.ext._handlers.stringcommandhandler",
    "telegram.ext._handlers.stringregexhandler",
    "telegram.ext._handlers.typehandler",
    "telegram.ext._jobqueue",
    "telegram.ext._picklepersistence",
    "telegram.ext._updater",
]

from . import filters
from ._aioratelimiter import AIORateLimiter
from ._application import Application, ApplicationHandlerStop
from ._applicationbuilder import ApplicationBuilder
from ._basepersistence import BasePersistence, PersistenceInput
from ._baseratelimiter import BaseRateLimiter
from ._baseupdateprocessor import BaseUpdateProcessor, SimpleUpdateProcessor
from ._callbackcontext import CallbackContext
from ._callbackdatacache import CallbackDataCache, InvalidCallbackData
from ._contexttypes import ContextTypes
from ._defaults import Defaults
from ._dictpersistence import DictPersistence
from ._extbot import ExtBot
from ._handlers.basehandler import BaseHandler
from ._handlers.businessconnectionhandler import BusinessConnectionHandler
from ._handlers.businessmessagesdeletedhandler import BusinessMessagesDeletedHandler
from ._handlers.callbackqueryhandler import CallbackQueryHandler
from ._handlers.chatboosthandler import ChatBoostHandler
from ._handlers.chatjoinrequesthandler import ChatJoinRequestHandler
from ._handlers.chatmemberhandler import ChatMemberHandler
from ._handlers.choseninlineresulthandler import ChosenInlineResultHandler
from ._handlers.commandhandler import CommandHandler
from ._handlers.conversationhandler import ConversationHandler
from ._handlers.inlinequeryhandler import InlineQueryHandler
from ._handlers.managedbotupdatedhandler import ManagedBotUpdatedHandler
from ._handlers.messagehandler import MessageHandler
from ._handlers.messagereactionhandler import MessageReactionHandler
from ._handlers.paidmediapurchasedhandler import PaidMediaPurchasedHandler
from ._handlers.pollanswerhandler import PollAnswerHandler
from ._handlers.pollhandler import PollHandler
from ._handlers.precheckoutqueryhandler import PreCheckoutQueryHandler
from ._handlers.prefixhandler import PrefixHandler
from ._handlers.shippingqueryhandler import ShippingQueryHandler
from ._handlers.stringcommandhandler import StringCommandHandler
from ._handlers.stringregexhandler import StringRegexHandler
from ._handlers.typehandler import TypeHandler
from ._jobqueue import Job, JobQueue
from ._picklepersistence import PicklePersistence
from ._updater import Updater
