#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
""" This module contains the Filters for use with the MessageHandler class """
from telegram import Chat

try:
    str_type = base_string
except NameError:
    str_type = str


class BaseFilter(object):
    """Base class for all Message Filters

    Subclassing from this class filters to be combined using bitwise operators:

    And:

        >>> (Filters.text & Filters.entity(MENTION))

    Or:

        >>> (Filters.audio | Filters.video)

    Not:

        >>> ~ Filters.command

    Also works with more than two filters:

        >>> (Filters.text & (Filters.entity(URL) | Filters.entity(TEXT_LINK)))
        >>> Filters.text & (~ Filters.forwarded)

    If you want to create your own filters create a class inheriting from this class and implement
    a `filter` method that returns a boolean: `True` if the message should be handled, `False`
    otherwise. Note that the filters work only as class instances, not actual class objects
    (so remember to initialize your filter classes).
    """

    def __call__(self, message):
        return self.filter(message)

    def __and__(self, other):
        return MergedFilter(self, and_filter=other)

    def __or__(self, other):
        return MergedFilter(self, or_filter=other)

    def __invert__(self):
        return InvertedFilter(self)

    def filter(self, message):
        raise NotImplementedError


class InvertedFilter(BaseFilter):
    """Represents a filter that has been inverted.

    Args:
        f: The filter to invert
    """

    def __init__(self, f):
        self.f = f

    def filter(self, message):
        return not self.f(message)

    def __str__(self):
        return "<telegram.ext.filters.InvertedFilter inverting {}>".format(self.f)

    __repr__ = __str__


class MergedFilter(BaseFilter):
    """Represents a filter consisting of two other filters.

    Args:
        base_filter: Filter 1 of the merged filter
        and_filter: Optional filter to "and" with base_filter. Mutually exclusive with or_filter.
        or_filter: Optional filter to "or" with base_filter. Mutually exclusive with and_filter.
    """

    def __init__(self, base_filter, and_filter=None, or_filter=None):
        self.base_filter = base_filter
        self.and_filter = and_filter
        self.or_filter = or_filter

    def filter(self, message):
        if self.and_filter:
            return self.base_filter(message) and self.and_filter(message)
        elif self.or_filter:
            return self.base_filter(message) or self.or_filter(message)

    def __str__(self):
        return ("<telegram.ext.filters.MergedFilter consisting of"
                " {} {} {}>").format(self.base_filter, "and" if self.and_filter else "or",
                                     self.and_filter or self.or_filter)

    __repr__ = __str__


class Filters(object):
    """
    Predefined filters for use with the `filter` argument of :class:`telegram.ext.MessageHandler`.
    """

    class _All(BaseFilter):

        def filter(self, message):
            return True

    all = _All()

    class _Text(BaseFilter):

        def filter(self, message):
            return bool(message.text and not message.text.startswith('/'))

    text = _Text()

    class _Command(BaseFilter):

        def filter(self, message):
            return bool(message.text and message.text.startswith('/'))

    class _Reply(BaseFilter):

        def filter(self, message):
            return bool(message.reply_to_message)

    reply = _Reply()

    command = _Command()

    class _Audio(BaseFilter):

        def filter(self, message):
            return bool(message.audio)

    audio = _Audio()

    class _Document(BaseFilter):

        def filter(self, message):
            return bool(message.document)

    document = _Document()

    class _Photo(BaseFilter):

        def filter(self, message):
            return bool(message.photo)

    photo = _Photo()

    class _Sticker(BaseFilter):

        def filter(self, message):
            return bool(message.sticker)

    sticker = _Sticker()

    class _Video(BaseFilter):

        def filter(self, message):
            return bool(message.video)

    video = _Video()

    class _Voice(BaseFilter):

        def filter(self, message):
            return bool(message.voice)

    voice = _Voice()

    class _Contact(BaseFilter):

        def filter(self, message):
            return bool(message.contact)

    contact = _Contact()

    class _Location(BaseFilter):

        def filter(self, message):
            return bool(message.location)

    location = _Location()

    class _Venue(BaseFilter):

        def filter(self, message):
            return bool(message.venue)

    venue = _Venue()

    class _StatusUpdate(BaseFilter):

        class _NewChatMembers(BaseFilter):

            def filter(self, message):
                return bool(message.new_chat_members)

        new_chat_members = _NewChatMembers()

        class _LeftChatMember(BaseFilter):

            def filter(self, message):
                return bool(message.left_chat_member)

        left_chat_member = _LeftChatMember()

        class _NewChatTitle(BaseFilter):

            def filter(self, message):
                return bool(message.new_chat_title)

        new_chat_title = _NewChatTitle()

        class _NewChatPhoto(BaseFilter):

            def filter(self, message):
                return bool(message.new_chat_photo)

        new_chat_photo = _NewChatPhoto()

        class _DeleteChatPhoto(BaseFilter):

            def filter(self, message):
                return bool(message.delete_chat_photo)

        delete_chat_photo = _DeleteChatPhoto()

        class _ChatCreated(BaseFilter):

            def filter(self, message):
                return bool(message.group_chat_created or message.supergroup_chat_created or
                            message.channel_chat_created)

        chat_created = _ChatCreated()

        class _Migrate(BaseFilter):

            def filter(self, message):
                return bool(message.migrate_from_chat_id or message.migrate_to_chat_id)

        migrate = _Migrate()

        class _PinnedMessage(BaseFilter):

            def filter(self, message):
                return bool(message.pinned_message)

        pinned_message = _PinnedMessage()

        def filter(self, message):
            return bool(self.new_chat_members(message) or self.left_chat_member(message) or
                        self.new_chat_title(message) or self.new_chat_photo(message) or
                        self.delete_chat_photo(message) or self.chat_created(message) or
                        self.migrate(message) or self.pinned_message(message))

    status_update = _StatusUpdate()

    class _Forwarded(BaseFilter):

        def filter(self, message):
            return bool(message.forward_date)

    forwarded = _Forwarded()

    class _Game(BaseFilter):

        def filter(self, message):
            return bool(message.game)

    game = _Game()

    class entity(BaseFilter):
        """Filters messages to only allow those which have a :class:`telegram.MessageEntity`
        where their `type` matches `entity_type`.

        Args:
            entity_type: Entity type to check for. All types can be found as constants
                in :class:`telegram.MessageEntity`.

        Returns: function to use as filter
        """

        def __init__(self, entity_type):
            self.entity_type = entity_type

        def filter(self, message):
            return any([entity.type == self.entity_type for entity in message.entities])

    class _Private(BaseFilter):

        def filter(self, message):
            return message.chat.type == Chat.PRIVATE

    private = _Private()

    class _Group(BaseFilter):

        def filter(self, message):
            return message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]

    group = _Group()

    class _Invoice(BaseFilter):

        def filter(self, message):
            return bool(message.invoice)

    invoice = _Invoice()

    class _SuccessfulPayment(BaseFilter):

        def filter(self, message):
            return bool(message.successful_payment)

    successful_payment = _SuccessfulPayment()

    class language(BaseFilter):
        """
        Filters messages to only allow those which are from users with a certain language code.
        Note that according to telegrams documentation, every single user does not have the
        language_code attribute.

        Args:
            lang (str|list): Which language code(s) to allow through. This will be matched using
                .startswith meaning that 'en' will match both 'en_US' and 'en_GB'
        """

        def __init__(self, lang):
            if isinstance(lang, str_type):
                self.lang = [lang]
            else:
                self.lang = lang

        def filter(self, message):
            return message.from_user.language_code and any(
                [message.from_user.language_code.startswith(x) for x in self.lang])
