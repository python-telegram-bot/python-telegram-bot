#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

import re

from future.utils import string_types

from telegram import Chat

__all__ = ['Filters', 'BaseFilter', 'InvertedFilter', 'MergedFilter']


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

    Note:
        Filters use the same short circuiting logic that pythons `and`, `or` and `not`.
        This means that for example:

            >>> Filters.regex(r'(a?x)') | Filters.regex(r'(b?x)')

        With a message.text of `x`, will only ever return the matches for the first filter,
        since the second one is never evaluated.


    If you want to create your own filters create a class inheriting from this class and implement
    a `filter` method that returns a boolean: `True` if the message should be handled, `False`
    otherwise. Note that the filters work only as class instances, not actual class objects
    (so remember to initialize your filter classes).

    By default the filters name (what will get printed when converted to a string for display)
    will be the class name. If you want to overwrite this assign a better name to the `name`
    class variable.

    Attributes:
        name (:obj:`str`): Name for this filter. Defaults to the type of filter.
        update_filter (:obj:`bool`): Whether this filter should work on update. If ``False`` it
            will run the filter on :attr:`update.effective_message``. Default is ``False``.
        data_filter (:obj:`bool`): Whether this filter is a data filter. A data filter should
            return a dict with lists. The dict will be merged with
            :class:`telegram.ext.CallbackContext`'s internal dict in most cases
            (depends on the handler).
    """

    name = None
    update_filter = False
    data_filter = False

    def __call__(self, update):
        if self.update_filter:
            return self.filter(update)
        else:
            return self.filter(update.effective_message)

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

    def filter(self, update):
        """This method must be overwritten.

        Note:
            If :attr:`update_filter` is false then the first argument is `message` and of
            type :class:`telegram.Message`.

        Args:
            update (:class:`telegram.Update`): The update that is tested.

        Returns:
            :obj:`dict` or :obj:`bool`

        """

        raise NotImplementedError


class InvertedFilter(BaseFilter):
    """Represents a filter that has been inverted.

    Args:
        f: The filter to invert.

    """
    update_filter = True

    def __init__(self, f):
        self.f = f

    def filter(self, update):
        return not bool(self.f(update))

    def __repr__(self):
        return "<inverted {}>".format(self.f)


class MergedFilter(BaseFilter):
    """Represents a filter consisting of two other filters.

    Args:
        base_filter: Filter 1 of the merged filter
        and_filter: Optional filter to "and" with base_filter. Mutually exclusive with or_filter.
        or_filter: Optional filter to "or" with base_filter. Mutually exclusive with and_filter.

    """
    update_filter = True

    def __init__(self, base_filter, and_filter=None, or_filter=None):
        self.base_filter = base_filter
        if self.base_filter.data_filter:
            self.data_filter = True
        self.and_filter = and_filter
        if (self.and_filter
                and not isinstance(self.and_filter, bool)
                and self.and_filter.data_filter):
            self.data_filter = True
        self.or_filter = or_filter
        if (self.or_filter
                and not isinstance(self.and_filter, bool)
                and self.or_filter.data_filter):
            self.data_filter = True

    def _merge(self, base_output, comp_output):
        base = base_output if isinstance(base_output, dict) else {}
        comp = comp_output if isinstance(comp_output, dict) else {}
        for k in comp.keys():
            # Make sure comp values are lists
            comp_value = comp[k] if isinstance(comp[k], list) else []
            try:
                # If base is a list then merge
                if isinstance(base[k], list):
                    base[k] += comp_value
                else:
                    base[k] = [base[k]] + comp_value
            except KeyError:
                base[k] = comp_value
        return base

    def filter(self, update):
        base_output = self.base_filter(update)
        # We need to check if the filters are data filters and if so return the merged data.
        # If it's not a data filter or an or_filter but no matches return bool
        if self.and_filter:
            # And filter needs to short circuit if base is falsey
            if base_output:
                comp_output = self.and_filter(update)
                if comp_output:
                    if self.data_filter:
                        merged = self._merge(base_output, comp_output)
                        if merged:
                            return merged
                    return True
        elif self.or_filter:
            # Or filter needs to short circuit if base is truthey
            if base_output:
                if self.data_filter:
                    return base_output
                return True
            else:
                comp_output = self.or_filter(update)
                if comp_output:
                    if self.data_filter:
                        return comp_output
                    return True
        return False

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
    """All Messages."""

    class _Text(BaseFilter):
        name = 'Filters.text'

        def filter(self, message):
            return bool(message.text and not message.text.startswith('/'))

    text = _Text()
    """Text Messages."""

    class _Command(BaseFilter):
        name = 'Filters.command'

        def filter(self, message):
            return bool(message.text and message.text.startswith('/'))

    command = _Command()
    """Messages starting with ``/``."""

    class regex(BaseFilter):
        """
        Filters updates by searching for an occurrence of ``pattern`` in the message text.
        The ``re.search`` function is used to determine whether an update should be filtered.

        Refer to the documentation of the ``re`` module for more information.

        To get the groups and groupdict matched, see :attr:`telegram.ext.CallbackContext.matches`.

        Examples:
            Use ``MessageHandler(Filters.regex(r'help'), callback)`` to capture all messages that
            contain the word help. You can also use
            ``MessageHandler(Filters.regex(re.compile(r'help', re.IGNORECASE), callback)`` if
            you want your pattern to be case insensitive. This approach is recommended
            if you need to specify flags on your pattern.

        Note:
            Filters use the same short circuiting logic that pythons `and`, `or` and `not`.
            This means that for example:

                >>> Filters.regex(r'(a?x)') | Filters.regex(r'(b?x)')

            With a message.text of `x`, will only ever return the matches for the first filter,
            since the second one is never evaluated.

        Args:
            pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        """

        data_filter = True

        def __init__(self, pattern):
            if isinstance(pattern, string_types):
                pattern = re.compile(pattern)
            self.pattern = pattern
            self.name = 'Filters.regex({})'.format(self.pattern)

        def filter(self, message):
            """"""  # remove method from docs
            if message.text:
                match = self.pattern.search(message.text)
                if match:
                    return {'matches': [match]}
                return {}

    class _Reply(BaseFilter):
        name = 'Filters.reply'

        def filter(self, message):
            return bool(message.reply_to_message)

    reply = _Reply()
    """Messages that are a reply to another message."""

    class _Audio(BaseFilter):
        name = 'Filters.audio'

        def filter(self, message):
            return bool(message.audio)

    audio = _Audio()
    """Messages that contain :class:`telegram.Audio`."""

    class _Document(BaseFilter):
        name = 'Filters.document'

        class category(BaseFilter):
            """This Filter filters documents by their category in the mime-type attribute

            Note:
                This Filter only filters by the mime_type of the document,
                    it doesn't check the validity of the document.
                The user can manipulate the mime-type of a message and
                    send media with wrong types that don't fit to this handler.

            Example:
                Filters.documents.category('audio/') returnes `True` for all types
                of audio sent as file, for example 'audio/mpeg' or 'audio/x-wav'
            """

            def __init__(self, category):
                """Initialize the category you want to filter

                Args:
                    category (str, optional): category of the media you want to filter"""
                self.category = category
                self.name = "Filters.document.category('{}')".format(self.category)

            def filter(self, message):
                """"""  # remove method from docs
                if message.document:
                    return message.document.mime_type.startswith(self.category)

        application = category('application/')
        audio = category('audio/')
        image = category('image/')
        video = category('video/')
        text = category('text/')

        class mime_type(BaseFilter):
            """This Filter filters documents by their mime-type attribute

            Note:
                This Filter only filters by the mime_type of the document,
                    it doesn't check the validity of document.
                The user can manipulate the mime-type of a message and
                    send media with wrong types that don't fit to this handler.

            Example:
                ``Filters.documents.mime_type('audio/mpeg')`` filters all audio in mp3 format.
            """

            def __init__(self, mimetype):
                """Initialize the category you want to filter

                Args:
                    filetype (str, optional): mime_type of the media you want to filter"""
                self.mimetype = mimetype
                self.name = "Filters.document.mime_type('{}')".format(self.mimetype)

            def filter(self, message):
                """"""  # remove method from docs
                if message.document:
                    return message.document.mime_type == self.mimetype

        apk = mime_type('application/vnd.android.package-archive')
        doc = mime_type('application/msword')
        docx = mime_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        exe = mime_type('application/x-ms-dos-executable')
        gif = mime_type('video/mp4')
        jpg = mime_type('image/jpeg')
        mp3 = mime_type('audio/mpeg')
        pdf = mime_type('application/pdf')
        py = mime_type('text/x-python')
        svg = mime_type('image/svg+xml')
        txt = mime_type('text/plain')
        targz = mime_type('application/x-compressed-tar')
        wav = mime_type('audio/x-wav')
        xml = mime_type('application/xml')
        zip = mime_type('application/zip')

        def filter(self, message):
            return bool(message.document)

    document = _Document()
    """
    Subset for messages containing a document/file.

    Examples:
        Use these filters like: ``Filters.document.mp3``,
        ``Filters.document.mime_type("text/plain")`` etc. Or use just
        ``Filters.document`` for all document messages.

    Attributes:
        category: This Filter filters documents by their category in the mime-type attribute.

            Example:
                ``Filters.documents.category('audio/')`` filters all types
                of audio sent as file, for example 'audio/mpeg' or 'audio/x-wav'. The following
                attributes can be used as a shortcut like: ``Filters.document.audio``

        application:
        audio:
        image:
        video:
        text:
        mime_type: This Filter filters documents by their mime-type attribute.

            Example:
                ``Filters.documents.mime_type('audio/mpeg')`` filters all audio in mp3 format. The
                following attributes can be used as a shortcut like: ``Filters.document.jpg``
        apk:
        doc:
        docx:
        exe:
        gif:
        jpg:
        mp3:
        pdf:
        py:
        svg:
        txt:
        targz:
        wav:
        xml:
        zip:
        category: This Filter filters documents by their category in the mime-type attribute

            Note:
                This Filter only filters by the mime_type of the document,
                it doesn't check the validity of the document.
                The user can manipulate the mime-type of a message and
                send media with wrong types that don't fit to this handler.

            Example:
                ``Filters.documents.category('audio/')`` filters all types
                of audio sent as file, for example 'audio/mpeg' or 'audio/x-wav'
        application: Same as ``Filters.document.category("application")``.
        audio: Same as ``Filters.document.category("audio")``.
        image: Same as ``Filters.document.category("image")``.
        video: Same as ``Filters.document.category("video")``.
        text: Same as ``Filters.document.category("text")``.
        mime_type: This Filter filters documents by their mime-type attribute

            Note:
                This Filter only filters by the mime_type of the document,
                it doesn't check the validity of document.

                The user can manipulate the mime-type of a message and
                send media with wrong types that don't fit to this handler.

            Example:
                ``Filters.documents.mime_type('audio/mpeg')`` filters all audio in mp3 format.
        apk: Same as ``Filters.document.mime_type("application/vnd.android.package-archive")``-
        doc: Same as ``Filters.document.mime_type("application/msword")``-
        docx: Same as ``Filters.document.mime_type("application/vnd.openxmlformats-\
officedocument.wordprocessingml.document")``-
        exe: Same as ``Filters.document.mime_type("application/x-ms-dos-executable")``-
        gif: Same as ``Filters.document.mime_type("video/mp4")``-
        jpg: Same as ``Filters.document.mime_type("image/jpeg")``-
        mp3: Same as ``Filters.document.mime_type("audio/mpeg")``-
        pdf: Same as ``Filters.document.mime_type("application/pdf")``-
        py: Same as ``Filters.document.mime_type("text/x-python")``-
        svg: Same as ``Filters.document.mime_type("image/svg+xml")``-
        txt: Same as ``Filters.document.mime_type("text/plain")``-
        targz: Same as ``Filters.document.mime_type("application/x-compressed-tar")``-
        wav: Same as ``Filters.document.mime_type("audio/x-wav")``-
        xml: Same as ``Filters.document.mime_type("application/xml")``-
        zip: Same as ``Filters.document.mime_type("application/zip")``-
    """

    class _Animation(BaseFilter):
        name = 'Filters.animation'

        def filter(self, message):
            return bool(message.animation)

    animation = _Animation()
    """Messages that contain :class:`telegram.Animation`."""

    class _Photo(BaseFilter):
        name = 'Filters.photo'

        def filter(self, message):
            return bool(message.photo)

    photo = _Photo()
    """Messages that contain :class:`telegram.PhotoSize`."""

    class _Sticker(BaseFilter):
        name = 'Filters.sticker'

        def filter(self, message):
            return bool(message.sticker)

    sticker = _Sticker()
    """Messages that contain :class:`telegram.Sticker`."""

    class _Video(BaseFilter):
        name = 'Filters.video'

        def filter(self, message):
            return bool(message.video)

    video = _Video()
    """Messages that contain :class:`telegram.Video`."""

    class _Voice(BaseFilter):
        name = 'Filters.voice'

        def filter(self, message):
            return bool(message.voice)

    voice = _Voice()
    """Messages that contain :class:`telegram.Voice`."""

    class _VideoNote(BaseFilter):
        name = 'Filters.video_note'

        def filter(self, message):
            return bool(message.video_note)

    video_note = _VideoNote()
    """Messages that contain :class:`telegram.VideoNote`."""

    class _Contact(BaseFilter):
        name = 'Filters.contact'

        def filter(self, message):
            return bool(message.contact)

    contact = _Contact()
    """Messages that contain :class:`telegram.Contact`."""

    class _Location(BaseFilter):
        name = 'Filters.location'

        def filter(self, message):
            return bool(message.location)

    location = _Location()
    """Messages that contain :class:`telegram.Location`."""

    class _Venue(BaseFilter):
        name = 'Filters.venue'

        def filter(self, message):
            return bool(message.venue)

    venue = _Venue()
    """Messages that contain :class:`telegram.Venue`."""

    class _StatusUpdate(BaseFilter):
        """Subset for messages containing a status update.

        Examples:
            Use these filters like: ``Filters.status_update.new_chat_members`` etc. Or use just
            ``Filters.status_update`` for all status update messages.

        """
        update_filter = True

        class _NewChatMembers(BaseFilter):
            name = 'Filters.status_update.new_chat_members'

            def filter(self, message):
                return bool(message.new_chat_members)

        new_chat_members = _NewChatMembers()
        """Messages that contain :attr:`telegram.Message.new_chat_members`."""

        class _LeftChatMember(BaseFilter):
            name = 'Filters.status_update.left_chat_member'

            def filter(self, message):
                return bool(message.left_chat_member)

        left_chat_member = _LeftChatMember()
        """Messages that contain :attr:`telegram.Message.left_chat_member`."""

        class _NewChatTitle(BaseFilter):
            name = 'Filters.status_update.new_chat_title'

            def filter(self, message):
                return bool(message.new_chat_title)

        new_chat_title = _NewChatTitle()
        """Messages that contain :attr:`telegram.Message.new_chat_title`."""

        class _NewChatPhoto(BaseFilter):
            name = 'Filters.status_update.new_chat_photo'

            def filter(self, message):
                return bool(message.new_chat_photo)

        new_chat_photo = _NewChatPhoto()
        """Messages that contain :attr:`telegram.Message.new_chat_photo`."""

        class _DeleteChatPhoto(BaseFilter):
            name = 'Filters.status_update.delete_chat_photo'

            def filter(self, message):
                return bool(message.delete_chat_photo)

        delete_chat_photo = _DeleteChatPhoto()
        """Messages that contain :attr:`telegram.Message.delete_chat_photo`."""

        class _ChatCreated(BaseFilter):
            name = 'Filters.status_update.chat_created'

            def filter(self, message):
                return bool(message.group_chat_created or message.supergroup_chat_created
                            or message.channel_chat_created)

        chat_created = _ChatCreated()
        """Messages that contain :attr:`telegram.Message.group_chat_created`,
            :attr: `telegram.Message.supergroup_chat_created` or
            :attr: `telegram.Message.channel_chat_created`."""

        class _Migrate(BaseFilter):
            name = 'Filters.status_update.migrate'

            def filter(self, message):
                return bool(message.migrate_from_chat_id or message.migrate_to_chat_id)

        migrate = _Migrate()
        """Messages that contain :attr:`telegram.Message.migrate_from_chat_id` or
            :attr: `telegram.Message.migrate_to_chat_id`."""

        class _PinnedMessage(BaseFilter):
            name = 'Filters.status_update.pinned_message'

            def filter(self, message):
                return bool(message.pinned_message)

        pinned_message = _PinnedMessage()
        """Messages that contain :attr:`telegram.Message.pinned_message`."""

        class _ConnectedWebsite(BaseFilter):
            name = 'Filters.status_update.connected_website'

            def filter(self, message):
                return bool(message.connected_website)

        connected_website = _ConnectedWebsite()
        """Messages that contain :attr:`telegram.Message.connected_website`."""

        name = 'Filters.status_update'

        def filter(self, message):
            return bool(self.new_chat_members(message) or self.left_chat_member(message)
                        or self.new_chat_title(message) or self.new_chat_photo(message)
                        or self.delete_chat_photo(message) or self.chat_created(message)
                        or self.migrate(message) or self.pinned_message(message)
                        or self.connected_website(message))

    status_update = _StatusUpdate()
    """Subset for messages containing a status update.

    Examples:
        Use these filters like: ``Filters.status_update.new_chat_members`` etc. Or use just
        ``Filters.status_update`` for all status update messages.

    Attributes:
        chat_created: Messages that contain
            :attr:`telegram.Message.group_chat_created`,
            :attr:`telegram.Message.supergroup_chat_created` or
            :attr:`telegram.Message.channel_chat_created`.
        delete_chat_photo: Messages that contain
            :attr:`telegram.Message.delete_chat_photo`.
        left_chat_member: Messages that contain
            :attr:`telegram.Message.left_chat_member`.
        migrate: Messages that contain
            :attr:`telegram.Message.migrate_from_chat_id` or
            :attr: `telegram.Message.migrate_from_chat_id`.
        new_chat_members: Messages that contain
            :attr:`telegram.Message.new_chat_members`.
        new_chat_photo: Messages that contain
            :attr:`telegram.Message.new_chat_photo`.
        new_chat_title: Messages that contain
            :attr:`telegram.Message.new_chat_title`.
        pinned_message: Messages that contain
            :attr:`telegram.Message.pinned_message`.
    """

    class _Forwarded(BaseFilter):
        name = 'Filters.forwarded'

        def filter(self, message):
            return bool(message.forward_date)

    forwarded = _Forwarded()
    """Messages that are forwarded."""

    class _Game(BaseFilter):
        name = 'Filters.game'

        def filter(self, message):
            return bool(message.game)

    game = _Game()
    """Messages that contain :class:`telegram.Game`."""

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
            """"""  # remove method from docs
            return any(entity.type == self.entity_type for entity in message.entities)

    class caption_entity(BaseFilter):
        """
        Filters media messages to only allow those which have a :class:`telegram.MessageEntity`
        where their `type` matches `entity_type`.

        Examples:
            Example ``MessageHandler(Filters.caption_entity("hashtag"), callback_method)``

        Args:
            entity_type: Caption Entity type to check for. All types can be found as constants
                in :class:`telegram.MessageEntity`.

        """

        def __init__(self, entity_type):
            self.entity_type = entity_type
            self.name = 'Filters.caption_entity({})'.format(self.entity_type)

        def filter(self, message):
            """"""  # remove method from docs
            return any(entity.type == self.entity_type for entity in message.caption_entities)

    class _Private(BaseFilter):
        name = 'Filters.private'

        def filter(self, message):
            return message.chat.type == Chat.PRIVATE

    private = _Private()
    """Messages sent in a private chat."""

    class _Group(BaseFilter):
        name = 'Filters.group'

        def filter(self, message):
            return message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]

    group = _Group()
    """Messages sent in a group chat."""

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
            """"""  # remove method from docs
            if self.user_ids is not None:
                return bool(message.from_user and message.from_user.id in self.user_ids)
            else:
                # self.usernames is not None
                return bool(message.from_user and message.from_user.username
                            and message.from_user.username in self.usernames)

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
            """"""  # remove method from docs
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
    """Messages that contain :class:`telegram.Invoice`."""

    class _SuccessfulPayment(BaseFilter):
        name = 'Filters.successful_payment'

        def filter(self, message):
            return bool(message.successful_payment)

    successful_payment = _SuccessfulPayment()
    """Messages that confirm a :class:`telegram.SuccessfulPayment`."""

    class _PassportData(BaseFilter):
        name = 'Filters.passport_data'

        def filter(self, message):
            return bool(message.passport_data)

    passport_data = _PassportData()
    """Messages that contain a :class:`telegram.PassportData`"""

    class language(BaseFilter):
        """Filters messages to only allow those which are from users with a certain language code.

        Note:
            According to official telegram api documentation, not every single user has the
            `language_code` attribute. Do not count on this filter working on all users.

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
            """"""  # remove method from docs
            return message.from_user.language_code and any(
                [message.from_user.language_code.startswith(x) for x in self.lang])

    class _UpdateType(BaseFilter):
        update_filter = True

        class _Message(BaseFilter):
            update_filter = True

            def filter(self, update):
                return update.message is not None

        message = _Message()

        class _EditedMessage(BaseFilter):
            update_filter = True

            def filter(self, update):
                return update.edited_message is not None

        edited_message = _EditedMessage()

        class _Messages(BaseFilter):
            update_filter = True

            def filter(self, update):
                return update.message is not None or update.edited_message is not None

        messages = _Messages()

        class _ChannelPost(BaseFilter):
            update_filter = True

            def filter(self, update):
                return update.channel_post is not None

        channel_post = _ChannelPost()

        class _EditedChannelPost(BaseFilter):
            update_filter = True

            def filter(self, update):
                return update.edited_channel_post is not None

        edited_channel_post = _EditedChannelPost()

        class _ChannelPosts(BaseFilter):
            update_filter = True

            def filter(self, update):
                return update.channel_post is not None or update.edited_channel_post is not None

        channel_posts = _ChannelPosts()

        def filter(self, update):
            return self.messages(update) or self.channel_posts(update)

    update = _UpdateType()
    """Subset for filtering the type of update.

    Examples:
        Use these filters like: ``Filters.update.message`` or
        ``Filters.update.channel_posts`` etc. Or use just ``Filters.update`` for all
        types.

    Attributes:
        message: Updates with :attr:`telegram.Update.message`
        edited_message: Updates with :attr:`telegram.Update.edited_message`
        messages: Updates with either :attr:`telegram.Update.message` or
            :attr:`telegram.Update.edited_message`
        channel_post: Updates with :attr:`telegram.Update.channel_post`
        edited_channel_post: Updates with
            :attr:`telegram.Update.edited_channel_post`
        channel_posts: Updates with either :attr:`telegram.Update.channel_post` or
            :attr:`telegram.Update.edited_channel_post`
    """
