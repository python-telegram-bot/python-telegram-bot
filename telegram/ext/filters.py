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
""" This module contains the MessageHandler class """


class BaseFilter(object):
    """Base class for all Message Filters"""

    def __call__(self, message):
        self.filter(message)

    def __and__(self, other):
        return MergedFilter(self, and_filter=other)

    def __or__(self, other):
        return MergedFilter(self, or_filter=other)

    def filter(self, message):
        raise NotImplementedError


class MergedFilter(BaseFilter):
    """Represents a filter consisting of two other filters."""

    def __init__(self, base_filter, and_filter=None, or_filter=None):
        self.base_filter = base_filter
        self.and_filter = and_filter
        self.or_filter = or_filter

    def filter(self, message):
        if self.and_filter:
            return self.base_filter(message) and self.and_filter(message)
        elif self.or_filter:
            return self.base_filter(message) or self.or_filter(message)


class Filters(object):
    """
    Convenient namespace (class) & methods for the filter funcs of the
    MessageHandler class.
    """

    class Text(BaseFilter):

        def filter(self, message):
            return bool(message.text and not message.text.startswith('/'))

    text = Text()

    class Command(BaseFilter):

        def filter(self, message):
            return bool(message.text and message.text.startswith('/'))

    command = Command()

    class Audio(BaseFilter):

        def filter(self, message):
            return bool(message.audio)

    audio = Audio()

    class Document(BaseFilter):

        def filter(self, message):
            return bool(message.document)

    document = Document()

    class Photo(BaseFilter):

        def filter(self, message):
            return bool(message.photo)

    photo = Photo()

    class Sticker(BaseFilter):

        def filter(self, message):
            return bool(message.sticker)

    sticker = Sticker()

    class Video(BaseFilter):

        def filter(self, message):
            return bool(message.video)

    video = Video()

    class Voice(BaseFilter):

        def filter(self, message):
            return bool(message.voice)

    voice = Voice()

    class Contact(BaseFilter):

        def filter(self, message):
            return bool(message.contact)

    contact = Contact()

    class Location(BaseFilter):

        def filter(self, message):
            return bool(message.location)

    location = Location()

    class Venue(BaseFilter):

        def filter(self, message):
            return bool(message.venue)

    venue = Venue()

    class StatusUpdate(BaseFilter):

        def filter(self, message):
            return bool(message.new_chat_member or message.left_chat_member
                        or message.new_chat_title or message.new_chat_photo
                        or message.delete_chat_photo or message.group_chat_created
                        or message.supergroup_chat_created or message.channel_chat_created
                        or message.migrate_to_chat_id or message.migrate_from_chat_id
                        or message.pinned_message)

    status_update = StatusUpdate()

    class Forwarded(BaseFilter):

        def filter(self, message):
            return bool(message.forward_date)

    forwarded = Forwarded()
