#!/usr/bin/env python
# pylint: disable=R0902,R0912,R0913
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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

"""This module contains a object that represents a Telegram Message"""

from datetime import datetime
from time import mktime

from telegram import (Audio, Contact, Document, GroupChat, Location, PhotoSize,
                      Sticker, TelegramObject, User, Video, Voice)


class Message(TelegramObject):
    """This object represents a Telegram Message.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        message_id (int):
        from_user (:class:`telegram.User`):
        date (:class:`datetime.datetime`):
        forward_from (:class:`telegram.User`):
        forward_date (:class:`datetime.datetime`):
        reply_to_message (:class:`telegram.Message`):
        text (str):
        audio (:class:`telegram.Audio`):
        document (:class:`telegram.Document`):
        photo (List[:class:`telegram.PhotoSize`]):
        sticker (:class:`telegram.Sticker`):
        video (:class:`telegram.Video`):
        voice (:class:`telegram.Voice`):
        caption (str):
        contact (:class:`telegram.Contact`):
        location (:class:`telegram.Location`):
        new_chat_participant (:class:`telegram.User`):
        left_chat_participant (:class:`telegram.User`):
        new_chat_title (str):
        new_chat_photo (List[:class:`telegram.PhotoSize`]):
        delete_chat_photo (bool):
        group_chat_created (bool):

    Args:
        message_id (int):
        from_user (:class:`telegram.User`):
        date (:class:`datetime.datetime`):
        chat (:class:`telegram.User` or :class:`telegram.GroupChat`):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        forward_from (Optional[:class:`telegram.User`]):
        forward_date (Optional[:class:`datetime.datetime`]):
        reply_to_message (Optional[:class:`telegram.Message`]):
        text (Optional[str]):
        audio (Optional[:class:`telegram.Audio`]):
        document (Optional[:class:`telegram.Document`]):
        photo (Optional[List[:class:`telegram.PhotoSize`]]):
        sticker (Optional[:class:`telegram.Sticker`]):
        video (Optional[:class:`telegram.Video`]):
        voice (Optional[:class:`telegram.Voice`]):
        caption (Optional[str]):
        contact (Optional[:class:`telegram.Contact`]):
        location (Optional[:class:`telegram.Location`]):
        new_chat_participant (Optional[:class:`telegram.User`]):
        left_chat_participant (Optional[:class:`telegram.User`]):
        new_chat_title (Optional[str]):
        new_chat_photo (Optional[List[:class:`telegram.PhotoSize`]):
        delete_chat_photo (Optional[bool]):
        group_chat_created (Optional[bool]):
    """

    def __init__(self,
                 message_id,
                 from_user,
                 date,
                 chat,
                 **kwargs):
        # Required
        self.message_id = int(message_id)
        self.from_user = from_user
        self.date = date
        self.chat = chat
        # Optionals
        self.forward_from = kwargs.get('forward_from')
        self.forward_date = kwargs.get('forward_date')
        self.reply_to_message = kwargs.get('reply_to_message')
        self.text = kwargs.get('text', '')
        self.audio = kwargs.get('audio')
        self.document = kwargs.get('document')
        self.photo = kwargs.get('photo')
        self.sticker = kwargs.get('sticker')
        self.video = kwargs.get('video')
        self.voice = kwargs.get('voice')
        self.caption = kwargs.get('caption', '')
        self.contact = kwargs.get('contact')
        self.location = kwargs.get('location')
        self.new_chat_participant = kwargs.get('new_chat_participant')
        self.left_chat_participant = kwargs.get('left_chat_participant')
        self.new_chat_title = kwargs.get('new_chat_title', '')
        self.new_chat_photo = kwargs.get('new_chat_photo')
        self.delete_chat_photo = bool(kwargs.get('delete_chat_photo', False))
        self.group_chat_created = bool(kwargs.get('group_chat_created', False))

    @property
    def chat_id(self):
        """int: Short for :attr:`Message.chat.id`"""
        return self.chat.id

    @staticmethod
    def de_json(data):
        """
        Args:
            data (str):

        Returns:
            telegram.Message:
        """
        if not data:
            return None

        data['from_user'] = User.de_json(data.get('from'))
        data['date'] = datetime.fromtimestamp(data['date'])
        if 'first_name' in data.get('chat', ''):
            data['chat'] = User.de_json(data.get('chat'))
        elif 'title' in data.get('chat', ''):
            data['chat'] = GroupChat.de_json(data.get('chat'))
        data['forward_from'] = \
            User.de_json(data.get('forward_from'))
        data['forward_date'] = \
            Message._fromtimestamp(data.get('forward_date'))
        data['reply_to_message'] = \
            Message.de_json(data.get('reply_to_message'))
        data['audio'] = \
            Audio.de_json(data.get('audio'))
        data['document'] = \
            Document.de_json(data.get('document'))
        data['photo'] = \
            PhotoSize.de_list(data.get('photo'))
        data['sticker'] = \
            Sticker.de_json(data.get('sticker'))
        data['video'] = \
            Video.de_json(data.get('video'))
        data['voice'] = \
            Voice.de_json(data.get('voice'))
        data['contact'] = \
            Contact.de_json(data.get('contact'))
        data['location'] = \
            Location.de_json(data.get('location'))
        data['new_chat_participant'] = \
            User.de_json(data.get('new_chat_participant'))
        data['left_chat_participant'] = \
            User.de_json(data.get('left_chat_participant'))
        data['new_chat_photo'] = \
            PhotoSize.de_list(data.get('new_chat_photo'))

        return Message(**data)

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
        if self.photo:
            data['photo'] = [p.to_dict() for p in self.photo]
        if self.new_chat_photo:
            data['new_chat_photo'] = [p.to_dict() for p in self.new_chat_photo]

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
