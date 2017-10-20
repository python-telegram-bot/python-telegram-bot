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
"""This module contains the Filters for use with the MessageHandler class."""
from telegram import Chat
from future.utils import string_types


class BaseFilter(object):
    """Base class for all Message Filters.

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

    Attributes:
        name (:obj:`str`): Name for this filter. Defaults to the type of filter.

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
        """This method must be overwritten.

        Args:
            message (:class:`telegram.Message`): The message that is tested.

        Returns:
            :obj:`bool`

        """

        raise NotImplementedError


class InvertedFilter(BaseFilter):
    """Represents a filter that has been inverted.

    Args:
        f: The filter to invert.

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
    """Predefined filters for use as the `filter` argument of :class:`telegram.ext.MessageHandler`.

    Examples:
        Use ``MessageHandler(Filters.video, callback_method)`` to filter all video
        messages. Use ``MessageHandler(Filters.contact, callback_method)`` for all contacts. etc.

    """

    class _All(BaseFilter):
        name = 'Filters.all'

        def filter(self, message):
            return True

    all = _All()
    """:obj:`Filter`: All Messages."""

    class _Text(BaseFilter):
        name = 'Filters.text'

        def filter(self, message):
            return bool(message.text and not message.text.startswith('/'))

    text = _Text()
    """:obj:`Filter`: Text Messages."""

    class _Command(BaseFilter):
        name = 'Filters.command'

        def filter(self, message):
            return bool(message.text and message.text.startswith('/'))

    command = _Command()
    """:obj:`Filter`: Messages starting with ``/``."""

    class _Reply(BaseFilter):
        name = 'Filters.reply'

        def filter(self, message):
            return bool(message.reply_to_message)

    reply = _Reply()
    """:obj:`Filter`: Messages that are a reply to another message."""

    class _Audio(BaseFilter):
        name = 'Filters.audio'

        def filter(self, message):
            return bool(message.audio)

    audio = _Audio()
    """:obj:`Filter`: Messages that contain :class:`telegram.Audio`."""

    class _Document(BaseFilter):
        name = 'Filters.document'

        def filter(self, message):
            return bool(message.document)

    document = _Document()
    """:obj:`Filter`: Messages that contain :class:`telegram.Document`."""

    class _Photo(BaseFilter):
        name = 'Filters.photo'

        def filter(self, message):
            return bool(message.photo)

    photo = _Photo()
    """:obj:`Filter`: Messages that contain :class:`telegram.PhotoSize`."""

    class _Sticker(BaseFilter):
        name = 'Filters.sticker'

        def filter(self, message):
            return bool(message.sticker)

    sticker = _Sticker()
    """:obj:`Filter`: Messages that contain :class:`telegram.Sticker`."""

    class _Video(BaseFilter):
        name = 'Filters.video'

        def filter(self, message):
            return bool(message.video)

    video = _Video()
    """:obj:`Filter`: Messages that contain :class:`telegram.Video`."""

    class _Voice(BaseFilter):
        name = 'Filters.voice'

        def filter(self, message):
            return bool(message.voice)

    voice = _Voice()
    """:obj:`Filter`: Messages that contain :class:`telegram.Voice`."""

    class _Contact(BaseFilter):
        name = 'Filters.contact'

        def filter(self, message):
            return bool(message.contact)

    contact = _Contact()
    """:obj:`Filter`: Messages that contain :class:`telegram.Contact`."""

    class _Location(BaseFilter):
        name = 'Filters.location'

        def filter(self, message):
            return bool(message.location)

    location = _Location()
    """:obj:`Filter`: Messages that contain :class:`telegram.Location`."""

    class _Venue(BaseFilter):
        name = 'Filters.venue'

        def filter(self, message):
            return bool(message.venue)

    venue = _Venue()
    """:obj:`Filter`: Messages that contain :class:`telegram.Venue`."""

    class _StatusUpdate(BaseFilter):
        """Subset for messages containing a status update.

        Examples:
            Use these filters like: ``Filters.status_update.new_chat_members`` etc. Or use just
            ``Filters.status_update`` for all status update messages.

        """

        class _NewChatMembers(BaseFilter):
            name = 'Filters.status_update.new_chat_members'

            def filter(self, message):
                return bool(message.new_chat_members)

        new_chat_members = _NewChatMembers()
        """:obj:`Filter`: Messages that contain :attr:`telegram.Message.new_chat_member`."""

        class _LeftChatMember(BaseFilter):
            name = 'Filters.status_update.left_chat_member'

            def filter(self, message):
                return bool(message.left_chat_member)

        left_chat_member = _LeftChatMember()
        """:obj:`Filter`: Messages that contain :attr:`telegram.Message.left_chat_member`."""

        class _NewChatTitle(BaseFilter):
            name = 'Filters.status_update.new_chat_title'

            def filter(self, message):
                return bool(message.new_chat_title)

        new_chat_title = _NewChatTitle()
        """:obj:`Filter`: Messages that contain :attr:`telegram.Message.new_chat_title`."""

        class _NewChatPhoto(BaseFilter):
            name = 'Filters.status_update.new_chat_photo'

            def filter(self, message):
                return bool(message.new_chat_photo)

        new_chat_photo = _NewChatPhoto()
        """:obj:`Filter`: Messages that contain :attr:`telegram.Message.new_chat_photo`."""

        class _DeleteChatPhoto(BaseFilter):
            name = 'Filters.status_update.delete_chat_photo'

            def filter(self, message):
                return bool(message.delete_chat_photo)

        delete_chat_photo = _DeleteChatPhoto()
        """:obj:`Filter`: Messages that contain :attr:`telegram.Message.delete_chat_photo`."""

        class _ChatCreated(BaseFilter):
            name = 'Filters.status_update.chat_created'

            def filter(self, message):
                return bool(message.group_chat_created or message.supergroup_chat_created or
                            message.channel_chat_created)

        chat_created = _ChatCreated()
        """:obj:`Filter`: Messages that contain :attr:`telegram.Message.group_chat_created`,
            :attr: `telegram.Message.supergroup_chat_created` or
            :attr: `telegram.Message.channel_chat_created`."""

        class _Migrate(BaseFilter):
            name = 'Filters.status_update.migrate'

            def filter(self, message):
                return bool(message.migrate_from_chat_id or message.migrate_to_chat_id)

        migrate = _Migrate()
        """:obj:`Filter`: Messages that contain :attr:`telegram.Message.migrate_from_chat_id` or
            :attr: `telegram.Message.migrate_to_chat_id`."""

        class _PinnedMessage(BaseFilter):
            name = 'Filters.status_update.pinned_message'

            def filter(self, message):
                return bool(message.pinned_message)

        pinned_message = _PinnedMessage()
        """:obj:`Filter`: Messages that contain :attr:`telegram.Message.pinned_message`."""

        name = 'Filters.status_update'

        def filter(self, message):
            return bool(self.new_chat_members(message) or self.left_chat_member(message) or
                        self.new_chat_title(message) or self.new_chat_photo(message) or
                        self.delete_chat_photo(message) or self.chat_created(message) or
                        self.migrate(message) or self.pinned_message(message))

    status_update = _StatusUpdate()
    """Subset for messages containing a status update.

    Examples:
        Use these filters like: ``Filters.status_update.new_chat_member`` etc. Or use just
        ``Filters.status_update`` for all status update messages.

    Attributes:
        chat_created (:obj:`Filter`): Messages that contain
            :attr:`telegram.Message.group_chat_created`,
            :attr:`telegram.Message.supergroup_chat_created` or
            :attr:`telegram.Message.channel_chat_created`.
        delete_chat_photo (:obj:`Filter`): Messages that contain
            :attr:`telegram.Message.delete_chat_photo`.
        left_chat_member (:obj:`Filter`): Messages that contain
            :attr:`telegram.Message.left_chat_member`.
        migrate (:obj:`Filter`): Messages that contain
            :attr:`telegram.Message.migrate_from_chat_id` or
            :attr: `telegram.Message.migrate_from_chat_id`.
        new_chat_members (:obj:`Filter`): Messages that contain
            :attr:`telegram.Message.new_chat_member`.
        new_chat_photo (:obj:`Filter`): Messages that contain
            :attr:`telegram.Message.new_chat_photo`.
        new_chat_title (:obj:`Filter`): Messages that contain
            :attr:`telegram.Message.new_chat_title`.
        pinned_message (:obj:`Filter`): Messages that contain
            :attr:`telegram.Message.pinned_message`.
    """

    class _Forwarded(BaseFilter):
        name = 'Filters.forwarded'

        def filter(self, message):
            return bool(message.forward_date)

    forwarded = _Forwarded()
    """:obj:`Filter`: Messages that are forwarded."""

    class _Game(BaseFilter):
        name = 'Filters.game'

        def filter(self, message):
            return bool(message.game)

    game = _Game()
    """:obj:`Filter`: Messages that contain :class:`telegram.Game`."""

    class entity(BaseFilter):
        """
        Filters messages to only allow those which have a :class:`telegram.MessageEntity`
        where their `type` matches `entity_type`.

        Examples:
            Example ``MessageHandler(Filters.entity("hashtag"), callback_method)``

        Args:
            entity_type: Entity type to check for. All types can be found as constants
                in :class:`telegram.MessageEntity`.

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
    """:obj:`Filter`: Messages sent in a private chat."""

    class _Group(BaseFilter):
        name = 'Filters.group'

        def filter(self, message):
            return message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]

    group = _Group()
    """:obj:`Filter`: Messages sent in a group chat."""

    class user(BaseFilter):
        """Filters messages to allow only those which are from specified user ID.

        Examples:
            ``MessageHandler(Filters.user(1234), callback_method)``

        Args:
            user_id(:obj:`int` | List[:obj:`int`], optional): Which user ID(s) to allow through.
            username(:obj:`str` | List[:obj:`str`], optional): Which username(s) to allow through.
                If username starts with '@' symbol, it will be ignored.

        Raises:
            ValueError: If chat_id and username are both present, or neither is.

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

        Examples:
            ``MessageHandler(Filters.chat(-1234), callback_method)``

        Args:
            chat_id(:obj:`int` | List[:obj:`int`], optional): Which chat ID(s) to allow through.
            username(:obj:`str` | List[:obj:`str`], optional): Which username(s) to allow through.
                If username start swith '@' symbol, it will be ignored.

        Raises:
            ValueError: If chat_id and username are both present, or neither is.

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
    """:obj:`Filter`: Messages that contain :class:`telegram.Invoice`."""

    class _SuccessfulPayment(BaseFilter):
        name = 'Filters.successful_payment'

        def filter(self, message):
            return bool(message.successful_payment)

    successful_payment = _SuccessfulPayment()
    """:obj:`Filter`: Messages that confirm a :class:`telegram.SuccessfulPayment`."""

    class language(BaseFilter):
        """Filters messages to only allow those which are from users with a certain language code.

        Note: According to telegrams documentation, every single user does not have the
        `language_code` attribute.

        Examples:
            ``MessageHandler(Filters.language("en"), callback_method)``

        Args:
            lang (:obj:`str` | List[:obj:`str`]): Which language code(s) to allow through. This
                will be matched using ``.startswith`` meaning that 'en' will match both 'en_US'
                and 'en_GB'.

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
