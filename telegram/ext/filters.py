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
from future.utils import string_types


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

    By default the filters name (what will get printed when converted to a string for display)
    will be the class name. If you want to overwrite this assign a better name to the `name`
    class variable.
    """

    name = None

    def __call__(self, message):
        return self.filter(message)

    def __and__(self, other):
        return MergedFilter(self, and_filter=other)

    def __or__(self, other):
        return MergedFilter(self, or_filter=other)

    def __invert__(self):
        return InvertedFilter(self)

    def __repr__(self):
        # We do this here instead of in a __init__ so filter don't have to call __init__ or super()
        if self.name is None:
            self.name = self.__class__.__name__
        return self.name

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

    def __repr__(self):
        return "<inverted {}>".format(self.f)


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

    def __repr__(self):
        return "<{} {} {}>".format(self.base_filter, "and" if self.and_filter else "or",
                                   self.and_filter or self.or_filter)


class Filters(object):
    """
    Predefined filters for use with the `filter` argument of :class:`telegram.ext.MessageHandler`.
    """

    class _All(BaseFilter):
        name = 'Filters.all'

        def filter(self, message):
            return True

    all = _All()

    class _Text(BaseFilter):
        name = 'Filters.text'

        def filter(self, message):
            return bool(message.text and not message.text.startswith('/'))

    text = _Text()

    class _Command(BaseFilter):
        name = 'Filters.command'

        def filter(self, message):
            return bool(message.text and message.text.startswith('/'))

    command = _Command()

    class _Reply(BaseFilter):
        name = 'Filters.reply'

        def filter(self, message):
            return bool(message.reply_to_message)

    reply = _Reply()

    class _Audio(BaseFilter):
        name = 'Filters.audio'

        def filter(self, message):
            return bool(message.audio)

    audio = _Audio()

    class _Document(BaseFilter):
        name = 'Filters.document'

        def filter(self, message):
            return bool(message.document)

    document = _Document()

    class _Photo(BaseFilter):
        name = 'Filters.photo'

        def filter(self, message):
            return bool(message.photo)

    photo = _Photo()

    class _Sticker(BaseFilter):
        name = 'Filters.sticker'

        def filter(self, message):
            return bool(message.sticker)

    sticker = _Sticker()

    class _Video(BaseFilter):
        name = 'Filters.video'

        def filter(self, message):
            return bool(message.video)

    video = _Video()

    class _Voice(BaseFilter):
        name = 'Filters.voice'

        def filter(self, message):
            return bool(message.voice)

    voice = _Voice()

    class _Contact(BaseFilter):
        name = 'Filters.contact'

        def filter(self, message):
            return bool(message.contact)

    contact = _Contact()

    class _Location(BaseFilter):
        name = 'Filters.location'

        def filter(self, message):
            return bool(message.location)

    location = _Location()

    class _Venue(BaseFilter):
        name = 'Filters.venue'

        def filter(self, message):
            return bool(message.venue)

    venue = _Venue()

    class _StatusUpdate(BaseFilter):

        class _NewChatMembers(BaseFilter):
            name = 'Filters.status_update.new_chat_members'

            def filter(self, message):
                return bool(message.new_chat_members)

        new_chat_members = _NewChatMembers()

        class _LeftChatMember(BaseFilter):
            name = 'Filters.status_update.left_chat_member'

            def filter(self, message):
                return bool(message.left_chat_member)

        left_chat_member = _LeftChatMember()

        class _NewChatTitle(BaseFilter):
            name = 'Filters.status_update.new_chat_title'

            def filter(self, message):
                return bool(message.new_chat_title)

        new_chat_title = _NewChatTitle()

        class _NewChatPhoto(BaseFilter):
            name = 'Filters.status_update.new_chat_photo'

            def filter(self, message):
                return bool(message.new_chat_photo)

        new_chat_photo = _NewChatPhoto()

        class _DeleteChatPhoto(BaseFilter):
            name = 'Filters.status_update.delete_chat_photo'

            def filter(self, message):
                return bool(message.delete_chat_photo)

        delete_chat_photo = _DeleteChatPhoto()

        class _ChatCreated(BaseFilter):
            name = 'Filters.status_update.chat_created'

            def filter(self, message):
                return bool(message.group_chat_created or message.supergroup_chat_created or
                            message.channel_chat_created)

        chat_created = _ChatCreated()

        class _Migrate(BaseFilter):
            name = 'Filters.status_update.migrate'

            def filter(self, message):
                return bool(message.migrate_from_chat_id or message.migrate_to_chat_id)

        migrate = _Migrate()

        class _PinnedMessage(BaseFilter):
            name = 'Filters.status_update.pinned_message'

            def filter(self, message):
                return bool(message.pinned_message)

        pinned_message = _PinnedMessage()

        name = 'Filters.status_update'

        def filter(self, message):
            return bool(self.new_chat_members(message) or self.left_chat_member(message) or
                        self.new_chat_title(message) or self.new_chat_photo(message) or
                        self.delete_chat_photo(message) or self.chat_created(message) or
                        self.migrate(message) or self.pinned_message(message))

    status_update = _StatusUpdate()

    class _Forwarded(BaseFilter):
        name = 'Filters.forwarded'

        def filter(self, message):
            return bool(message.forward_date)

    forwarded = _Forwarded()

    class _Game(BaseFilter):
        name = 'Filters.game'

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
            self.name = 'Filters.entity({})'.format(self.entity_type)

        def filter(self, message):
            return any([entity.type == self.entity_type for entity in message.entities])

    class _Private(BaseFilter):
        name = 'Filters.private'

        def filter(self, message):
            return message.chat.type == Chat.PRIVATE

    private = _Private()

    class _Group(BaseFilter):
        name = 'Filters.group'

        def filter(self, message):
            return message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]

    group = _Group()

    class user(BaseFilter):
        """Filters messages to allow only those which are from specified user ID.

        Notes:
            Only one of chat_id or username must be used here.

        Args:
            user_id(Optional[int|list]): which user ID(s) to allow through.
            username(Optional[str|list]): which username(s) to allow through. If username starts
                with '@' symbol, it will be ignored.

        Raises:
            ValueError
        """

        def __init__(self, user_id=None, username=None):
            if not (bool(user_id) ^ bool(username)):
                raise ValueError('One and only one of user_id or username must be used')
            if user_id is not None and isinstance(user_id, int):
                self.user_ids = [user_id]
            else:
                self.user_ids = user_id
            if username is None:
                self.usernames = username
            elif isinstance(username, string_types):
                self.usernames = [username.replace('@', '')]
            else:
                self.usernames = [user.replace('@', '') for user in username]

        def filter(self, message):
            if self.user_ids is not None:
                return bool(message.from_user and message.from_user.id in self.user_ids)
            else:
                # self.usernames is not None
                return bool(message.from_user and message.from_user.username and
                            message.from_user.username in self.usernames)

    class chat(BaseFilter):
        """Filters messages to allow only those which are from specified chat ID.

        Notes:
            Only one of chat_id or username must be used here.

        Args:
            chat_id(Optional[int|list]): which chat ID(s) to allow through.
            username(Optional[str|list]): which username(s) to allow through. If username starts
                with '@' symbol, it will be ignored.

        Raises:
            ValueError
        """

        def __init__(self, chat_id=None, username=None):
            if not (bool(chat_id) ^ bool(username)):
                raise ValueError('One and only one of chat_id or username must be used')
            if chat_id is not None and isinstance(chat_id, int):
                self.chat_ids = [chat_id]
            else:
                self.chat_ids = chat_id
            if username is None:
                self.usernames = username
            elif isinstance(username, string_types):
                self.usernames = [username.replace('@', '')]
            else:
                self.usernames = [chat.replace('@', '') for chat in username]

        def filter(self, message):
            if self.chat_ids is not None:
                return bool(message.chat_id in self.chat_ids)
            else:
                # self.usernames is not None
                return bool(message.chat.username and message.chat.username in self.usernames)

    class _Invoice(BaseFilter):
        name = 'Filters.invoice'

        def filter(self, message):
            return bool(message.invoice)

    invoice = _Invoice()

    class _SuccessfulPayment(BaseFilter):
        name = 'Filters.successful_payment'

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
            if isinstance(lang, string_types):
                self.lang = [lang]
            else:
                self.lang = lang
            self.name = 'Filters.language({})'.format(self.lang)

        def filter(self, message):
            return message.from_user.language_code and any(
                [message.from_user.language_code.startswith(x) for x in self.lang])
