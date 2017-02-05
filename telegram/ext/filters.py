#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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


class BaseFilter(object):
    """Base class for all Message Filters

    Subclassing from this class filters to be combined using bitwise operators:

    And:

        >>> (Filters.text & Filters.entity(MENTION))

    Or:

        >>> (Filters.audio | Filters.video)

    Also works with more than two filters:

        >>> (Filters.text & (Filters.entity(URL) | Filters.entity(TEXT_LINK)))

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

    def filter(self, message):
        raise NotImplementedError


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

        def filter(self, message):
            return bool(message.new_chat_member or message.left_chat_member
                        or message.new_chat_title or message.new_chat_photo
                        or message.delete_chat_photo or message.group_chat_created
                        or message.supergroup_chat_created or message.channel_chat_created
                        or message.migrate_to_chat_id or message.migrate_from_chat_id
                        or message.pinned_message)

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
