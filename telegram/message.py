#!/usr/bin/env python
# pylint: disable=R0902,R0912,R0913
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
"""This module contains an object that represents a Telegram Message."""
import sys
from datetime import datetime
from time import mktime

from telegram import (Audio, Contact, Document, Chat, Location, PhotoSize, Sticker, TelegramObject,
                      User, Video, Voice, Venue, MessageEntity, Game, Invoice, SuccessfulPayment)
from telegram.utils.deprecate import warn_deprecate_obj
from telegram.utils.helpers import escape_html, escape_markdown
from telegram.videonote import VideoNote


class Message(TelegramObject):
    """This object represents a Telegram Message.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        message_id (int): Unique message identifier inside this chat
        from_user (:class:`telegram.User`): Sender, can be empty for messages sent to channels
        date (:class:`datetime.datetime`): Date the message was sent in Unix time
        chat (:class:`telegram.Chat`): Conversation the message belongs to
        forward_from (:class:`telegram.User`): For forwarded messages, sender of the original
            message
        forward_from_chat (:class:`telegram.Chat`): For messages forwarded from a channel,
            information about the original channel
        forward_from_message_id (int): For forwarded channel posts, identifier of the original
            message in the channel
        forward_date (:class:`datetime.datetime`): For forwarded messages, date the original
            message was sent in Unix time
        reply_to_message (:class:`telegram.Message`): For replies, the original message. Note
            that the Message object in this field will not contain further reply_to_message
            fields even if it itself is a reply.
        edit_date (:class:`datetime.datetime`): Date the message was last edited in Unix time
        text (str): For text messages, the actual UTF-8 text of the message, 0-4096 characters.
        entities (List[:class:`telegram.MessageEntity`]): For text messages, special entities
            like usernames, URLs, bot commands, etc. that appear in the text. See
            parse_entity and parse_entities methods for how to use properly
        video_note (:class:`telegram.VideoNote`): Message is a video note, information about the
            video message
        audio (:class:`telegram.Audio`): Message is an audio file, information about the file
        document (:class:`telegram.Document`): Message is a general file, information about the
            file
        game (:class:`telegram.Game`):Message is a game, information about the game
        photo (List[:class:`telegram.PhotoSize`]): Message is a photo, available sizes of the photo
        sticker (:class:`telegram.Sticker`): Message is a sticker, information about the sticker
        video (:class:`telegram.Video`): Message is a video, information about the video
        voice (:class:`telegram.Voice`): Message is a voice message, information about the file
        caption (str): Caption for the document, photo or video, 0-200 characters
        contact (:class:`telegram.Contact`): Message is a shared contact, information about the
            contact
        location (:class:`telegram.Location`): Message is a shared location, information about the
            location
        new_chat_member (:class:`telegram.User`): A new member was added to the group,
            information about them (this member may be the bot itself)
        left_chat_member (:class:`telegram.User`): A member was removed from the group,
            information about them (this member may be the bot itself)
        new_chat_title (str): A chat title was changed to this value
        new_chat_photo (List[:class:`telegram.PhotoSize`]): A chat photo was change to this value
        delete_chat_photo (bool): Service message: the chat photo was deleted
        group_chat_created (bool): Service message: the group has been created
        supergroup_chat_created (bool): Service message: the supergroup has been created. This
            field can't be received in a message coming through updates, because bot can't be a
            member of a supergroup when it is created. It can only be found in reply_to_message
            if someone replies to a very first message in a directly created supergroup.
        migrate_to_chat_id (int): The group has been migrated to a supergroup with the specified
            identifier.
        migrate_from_chat_id (int): The supergroup has been migrated from a group with the
            specified identifier.
        channel_chat_created (bool): Service message: the channel has been created. This field
            can't be received in a message coming through updates, because bot can't be a member
            of a channel when it is created. It can only be found in reply_to_message if someone
            replies to a very first message in a channel.
        pinned_message (:class:`telegram.message`): Specified message was pinned. Note that the
            Message object in this field will not contain further reply_to_message fields even if
            it is itself a reply.
        invoice (:class:`telegram.Invoice`): Message is an invoice for a payment, information
            about the invoice.
        successful_payment (:class:`telegram.SuccessfulPayment`): Message is a service message
            about a successful payment, information about the payment.
        bot (Optional[telegram.Bot]): The Bot to use for instance methods

    Deprecated: 4.0
        new_chat_participant (:class:`telegram.User`): Use `new_chat_member`
        instead.

        left_chat_participant  (:class:`telegram.User`): Use `left_chat_member`
        instead.
    """

    def __init__(self,
                 message_id,
                 from_user,
                 date,
                 chat,
                 forward_from=None,
                 forward_from_chat=None,
                 forward_date=None,
                 reply_to_message=None,
                 edit_date=None,
                 text=None,
                 entities=None,
                 audio=None,
                 document=None,
                 photo=None,
                 sticker=None,
                 video=None,
                 voice=None,
                 caption=None,
                 contact=None,
                 location=None,
                 venue=None,
                 new_chat_member=None,
                 new_chat_members=None,
                 left_chat_member=None,
                 new_chat_title=None,
                 new_chat_photo=None,
                 delete_chat_photo=False,
                 group_chat_created=False,
                 supergroup_chat_created=False,
                 migrate_to_chat_id=None,
                 migrate_from_chat_id=None,
                 channel_chat_created=False,
                 pinned_message=None,
                 forward_from_message_id=None,
                 invoice=None,
                 successful_payment=None,
                 bot=None,
                 video_note=None,
                 **kwargs):
        # Required
        self.message_id = int(message_id)
        self.from_user = from_user
        self.date = date
        self.chat = chat
        # Optionals
        self.forward_from = forward_from
        self.forward_from_chat = forward_from_chat
        self.forward_date = forward_date
        self.reply_to_message = reply_to_message
        self.edit_date = edit_date
        self.text = text
        self.entities = entities or list()
        self.audio = audio
        self.game = kwargs.get('game')
        self.document = document
        self.photo = photo
        self.sticker = sticker
        self.video = video
        self.voice = voice
        self.video_note = video_note
        self.caption = caption
        self.contact = contact
        self.location = location
        self.venue = venue
        self._new_chat_member = new_chat_member
        self.new_chat_members = new_chat_members
        self.left_chat_member = left_chat_member
        self.new_chat_title = new_chat_title
        self.new_chat_photo = new_chat_photo
        self.delete_chat_photo = bool(delete_chat_photo)
        self.group_chat_created = bool(group_chat_created)
        self.supergroup_chat_created = bool(supergroup_chat_created)
        self.migrate_to_chat_id = migrate_to_chat_id
        self.migrate_from_chat_id = migrate_from_chat_id
        self.channel_chat_created = bool(channel_chat_created)
        self.pinned_message = pinned_message
        self.forward_from_message_id = forward_from_message_id
        self.invoice = invoice
        self.successful_payment = successful_payment

        self.bot = bot

        self._id_attrs = (self.message_id,)

    @property
    def chat_id(self):
        """int: Short for :attr:`Message.chat.id`"""
        return self.chat.id

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.Message:
        """
        if not data:
            return None

        data = super(Message, Message).de_json(data, bot)

        data['from_user'] = User.de_json(data.get('from'), bot)
        data['date'] = Message._fromtimestamp(data['date'])
        data['chat'] = Chat.de_json(data.get('chat'), bot)
        data['entities'] = MessageEntity.de_list(data.get('entities'), bot)
        data['forward_from'] = User.de_json(data.get('forward_from'), bot)
        data['forward_from_chat'] = Chat.de_json(data.get('forward_from_chat'), bot)
        data['forward_date'] = Message._fromtimestamp(data.get('forward_date'))
        data['reply_to_message'] = Message.de_json(data.get('reply_to_message'), bot)
        data['edit_date'] = Message._fromtimestamp(data.get('edit_date'))
        data['audio'] = Audio.de_json(data.get('audio'), bot)
        data['document'] = Document.de_json(data.get('document'), bot)
        data['game'] = Game.de_json(data.get('game'), bot)
        data['photo'] = PhotoSize.de_list(data.get('photo'), bot)
        data['sticker'] = Sticker.de_json(data.get('sticker'), bot)
        data['video'] = Video.de_json(data.get('video'), bot)
        data['voice'] = Voice.de_json(data.get('voice'), bot)
        data['video_note'] = VideoNote.de_json(data.get('video_note'), bot)
        data['contact'] = Contact.de_json(data.get('contact'), bot)
        data['location'] = Location.de_json(data.get('location'), bot)
        data['venue'] = Venue.de_json(data.get('venue'), bot)
        data['new_chat_member'] = User.de_json(data.get('new_chat_member'), bot)
        data['new_chat_members'] = User.de_list(data.get('new_chat_members'), bot)
        data['left_chat_member'] = User.de_json(data.get('left_chat_member'), bot)
        data['new_chat_photo'] = PhotoSize.de_list(data.get('new_chat_photo'), bot)
        data['pinned_message'] = Message.de_json(data.get('pinned_message'), bot)
        data['invoice'] = Invoice.de_json(data.get('invoice'), bot)
        data['successful_payment'] = SuccessfulPayment.de_json(data.get('successful_payment'), bot)

        return Message(bot=bot, **data)

    def __getitem__(self, item):
        if item in self.__dict__.keys():
            return self.__dict__[item]
        elif item == 'chat_id':
            return self.chat.id

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = super(Message, self).to_dict()

        # Required
        data['from'] = data.pop('from_user', None)
        data['date'] = self._totimestamp(self.date)
        # Optionals
        if self.forward_date:
            data['forward_date'] = self._totimestamp(self.forward_date)
        if self.edit_date:
            data['edit_date'] = self._totimestamp(self.edit_date)
        if self.photo:
            data['photo'] = [p.to_dict() for p in self.photo]
        if self.entities:
            data['entities'] = [e.to_dict() for e in self.entities]
        if self.new_chat_photo:
            data['new_chat_photo'] = [p.to_dict() for p in self.new_chat_photo]
        data['new_chat_member'] = data.pop('_new_chat_member', None)
        if self.new_chat_members:
            data['new_chat_members'] = [u.to_dict() for u in self.new_chat_members]

        return data

    @staticmethod
    def _fromtimestamp(unixtime):
        """
        Args:
            unixtime (int):

        Returns:
            datetime.datetime:
        """
        if not unixtime:
            return None

        return datetime.fromtimestamp(unixtime)

    @staticmethod
    def _totimestamp(dt_obj):
        """
        Args:
            dt_obj (:class:`datetime.datetime`):

        Returns:
            int:
        """
        if not dt_obj:
            return None

        try:
            # Python 3.3+
            return int(dt_obj.timestamp())
        except AttributeError:
            # Python 3 (< 3.3) and Python 2
            return int(mktime(dt_obj.timetuple()))

    def _quote(self, kwargs):
        """Modify kwargs for replying with or without quoting"""

        if 'reply_to_message_id' in kwargs:
            if 'quote' in kwargs:
                del kwargs['quote']

        elif 'quote' in kwargs:
            if kwargs['quote']:
                kwargs['reply_to_message_id'] = self.message_id

            del kwargs['quote']

        else:
            if self.chat.type != Chat.PRIVATE:
                kwargs['reply_to_message_id'] = self.message_id

    def reply_text(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_message(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the message is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.
        """

        self._quote(kwargs)
        return self.bot.send_message(self.chat_id, *args, **kwargs)

    def reply_photo(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_photo(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the photo is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_photo(self.chat_id, *args, **kwargs)

    def reply_audio(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_audio(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the audio is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_audio(self.chat_id, *args, **kwargs)

    def reply_document(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_document(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the document is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_document(self.chat_id, *args, **kwargs)

    def reply_sticker(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_sticker(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the sticker is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_sticker(self.chat_id, *args, **kwargs)

    def reply_video(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_video(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the video is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_video(self.chat_id, *args, **kwargs)

    def reply_video_note(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_video_note(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the video is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_video_note(self.chat_id, *args, **kwargs)

    def reply_voice(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_voice(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the voice is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_voice(self.chat_id, *args, **kwargs)

    def reply_location(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_location(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the location is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_location(self.chat_id, *args, **kwargs)

    def reply_venue(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_venue(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the venue is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_venue(self.chat_id, *args, **kwargs)

    def reply_contact(self, *args, **kwargs):
        """
        Shortcut for ``bot.send_contact(update.message.chat_id, *args, **kwargs)``

        Keyword Args:
            quote (Optional[bool]): If set to ``True``, the contact is sent as an actual reply to
                this message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter
                will be ignored. Default: ``True`` in group chats and ``False`` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """

        self._quote(kwargs)
        return self.bot.send_contact(self.chat_id, *args, **kwargs)

    def forward(self, chat_id, disable_notification=False):
        """Shortcut for

            >>> bot.forward_message(chat_id=chat_id,
            ...                    from_chat_id=update.message.chat_id,
            ...                    disable_notification=disable_notification,
            ...                    message_id=update.message.message_id)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message forwarded.

        """
        return self.bot.forward_message(
            chat_id=chat_id,
            from_chat_id=self.chat_id,
            disable_notification=disable_notification,
            message_id=self.message_id)

    def edit_text(self, *args, **kwargs):
        """
        Shortcut for

            >>> bot.edit_message_text(chat_id=message.chat_id,
            ...                     message_id=message.message_id,
            ...                     *args, **kwargs)

        Note:
            You can only edit messages that the bot sent itself,
            therefore this method can only be used on the
            return value of the ``bot.send_*`` family of methods.

        """
        return self.bot.edit_message_text(
            chat_id=self.chat_id, message_id=self.message_id, *args, **kwargs)

    def edit_caption(self, *args, **kwargs):
        """
        Shortcut for

            >>> bot.edit_message_caption(chat_id=message.chat_id,
            ...                        message_id=message.message_id,
            ...                        *args, **kwargs)

        Note:
            You can only edit messages that the bot sent itself,
            therefore this method can only be used on the
            return value of the ``bot.send_*`` family of methods.
        """
        return self.bot.edit_message_caption(
            chat_id=self.chat_id, message_id=self.message_id, *args, **kwargs)

    def edit_reply_markup(self, *args, **kwargs):
        """
        Shortcut for

            >>> bot.edit_message_reply_markup(chat_id=message.chat_id,
            ...                     message_id=message.message_id,
            ...                     *args, **kwargs)

        Note:
            You can only edit messages that the bot sent itself,
            therefore this method can only be used on the
            return value of the ``bot.send_*`` family of methods.
        """
        return self.bot.edit_message_reply_markup(
            chat_id=self.chat_id, message_id=self.message_id, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Shortcut for

            >>> bot.delete_message(chat_id=message.chat_id,
            ...                   message_id=message.message_id,
            ...                   *args, **kwargs)

        Returns:
            bool: On success, `True` is returned.

        """
        return self.bot.delete_message(
            chat_id=self.chat_id, message_id=self.message_id, *args, **kwargs)

    def parse_entity(self, entity):
        """
        Returns the text from a given :class:`telegram.MessageEntity`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (telegram.MessageEntity): The entity to extract the text from. It must be an
                entity that belongs to this message.

        Returns:
            str: The text of the given entity
        """
        # Is it a narrow build, if so we don't need to convert
        if sys.maxunicode == 0xffff:
            return self.text[entity.offset:entity.offset + entity.length]
        else:
            entity_text = self.text.encode('utf-16-le')
            entity_text = entity_text[entity.offset * 2:(entity.offset + entity.length) * 2]

        return entity_text.decode('utf-16-le')

    def parse_entities(self, types=None):
        """
        Returns a ``dict`` that maps :class:`telegram.MessageEntity` to ``str``.
        It contains entities from this message filtered by their ``type`` attribute as the key, and
        the text that each entity belongs to as the value of the ``dict``.

        Note:
            This method should always be used instead of the ``entities`` attribute, since it
            calculates the correct substring from the message text based on UTF-16 codepoints.
            See ``get_entity_text`` for more info.

        Args:
            types (Optional[list]): List of ``telegram.MessageEntity`` types as strings. If the
                ``type`` attribute of an entity is contained in this list, it will be returned.
                Defaults to a list of all types. All types can be found as constants in
                :class:`telegram.MessageEntity`.

        Returns:
            dict[:class:`telegram.MessageEntity`, ``str``]: A dictionary of entities mapped to the
                text that belongs to them, calculated based on UTF-16 codepoints.

        """
        if types is None:
            types = MessageEntity.ALL_TYPES

        return {
            entity: self.parse_entity(entity)
            for entity in self.entities if entity.type in types
        }

    @property
    def text_html(self):
        """
        Creates an html-formatted string from the markup entities found in the message
        (uses ``parse_entities``).

        Use this if you want to retrieve the original string sent by the bot, as opposed to the
        plain text with corresponding markup entities.

        Returns:
            str

        """
        entities = self.parse_entities()
        message_text = self.text
        if not sys.maxunicode == 0xffff:
            message_text = message_text.encode('utf-16-le')

        markdown_text = ''
        last_offset = 0

        for entity, text in sorted(entities.items(), key=(lambda item: item[0].offset)):
            text = escape_html(text)

            if entity.type == MessageEntity.TEXT_LINK:
                insert = '<a href="{}">{}</a>'.format(entity.url, text)
            elif entity.type == MessageEntity.BOLD:
                insert = '<b>' + text + '</b>'
            elif entity.type == MessageEntity.ITALIC:
                insert = '<i>' + text + '</i>'
            elif entity.type == MessageEntity.CODE:
                insert = '<code>' + text + '</code>'
            elif entity.type == MessageEntity.PRE:
                insert = '<pre>' + text + '</pre>'
            else:
                insert = text

            if sys.maxunicode == 0xffff:
                markdown_text += escape_html(message_text[last_offset:entity.offset]) + insert
            else:
                markdown_text += escape_html(message_text[last_offset * 2:entity.offset * 2]
                                             .decode('utf-16-le')) + insert

            last_offset = entity.offset + entity.length

        if sys.maxunicode == 0xffff:
            markdown_text += escape_html(message_text[last_offset:])
        else:
            markdown_text += escape_html(message_text[last_offset * 2:].decode('utf-16-le'))
        return markdown_text

    @property
    def text_markdown(self):
        """
        Creates a markdown-formatted string from the markup entities found in the message
        (uses ``parse_entities``).

        Use this if you want to retrieve the original string sent by the bot, as opposed to the
        plain text with corresponding markup entities.

        Returns:
            str
        """
        entities = self.parse_entities()
        message_text = self.text
        if not sys.maxunicode == 0xffff:
            message_text = message_text.encode('utf-16-le')

        markdown_text = ''
        last_offset = 0

        for entity, text in sorted(entities.items(), key=(lambda item: item[0].offset)):
            text = escape_markdown(text)

            if entity.type == MessageEntity.TEXT_LINK:
                insert = '[{}]({})'.format(text, entity.url)
            elif entity.type == MessageEntity.BOLD:
                insert = '*' + text + '*'
            elif entity.type == MessageEntity.ITALIC:
                insert = '_' + text + '_'
            elif entity.type == MessageEntity.CODE:
                insert = '`' + text + '`'
            elif entity.type == MessageEntity.PRE:
                insert = '```' + text + '```'
            else:
                insert = text
            if sys.maxunicode == 0xffff:
                markdown_text += escape_markdown(message_text[last_offset:entity.offset]) + insert
            else:
                markdown_text += escape_markdown(message_text[last_offset * 2:entity.offset * 2]
                                                 .decode('utf-16-le')) + insert

            last_offset = entity.offset + entity.length

        if sys.maxunicode == 0xffff:
            markdown_text += escape_markdown(message_text[last_offset:])
        else:
            markdown_text += escape_markdown(message_text[last_offset * 2:].decode('utf-16-le'))
        return markdown_text

    @property
    def new_chat_member(self):
        warn_deprecate_obj('new_chat_member', 'new_chat_members')
        return self._new_chat_member
