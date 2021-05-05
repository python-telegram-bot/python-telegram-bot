#!/usr/bin/env python
# pylint: disable=R0902,R0913
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
"""This module contains an object that represents a Telegram Message."""
import datetime
import sys
from html import escape
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, ClassVar, Tuple

from telegram import (
    Animation,
    Audio,
    Chat,
    Contact,
    Dice,
    Document,
    Game,
    InlineKeyboardMarkup,
    Invoice,
    Location,
    MessageEntity,
    ParseMode,
    PassportData,
    PhotoSize,
    Poll,
    Sticker,
    SuccessfulPayment,
    TelegramObject,
    User,
    Venue,
    Video,
    VideoNote,
    Voice,
    VoiceChatStarted,
    VoiceChatEnded,
    VoiceChatParticipantsInvited,
    ProximityAlertTriggered,
    ReplyMarkup,
    MessageAutoDeleteTimerChanged,
    VoiceChatScheduled,
)
from telegram.utils.helpers import (
    escape_markdown,
    from_timestamp,
    to_timestamp,
    DEFAULT_NONE,
    DEFAULT_20,
)
from telegram.utils.types import JSONDict, FileInput, ODVInput, DVInput

if TYPE_CHECKING:
    from telegram import (
        Bot,
        GameHighScore,
        InputMedia,
        MessageId,
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        LabeledPrice,
    )

_UNDEFINED = object()


class Message(TelegramObject):
    # fmt: off
    """This object represents a message.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`message_id` and :attr:`chat` are equal.

    Note:
        In Python ``from`` is a reserved word, use ``from_user`` instead.

    Args:
        message_id (:obj:`int`): Unique message identifier inside this chat.
        from_user (:class:`telegram.User`, optional): Sender, empty for messages sent
            to channels.
        sender_chat (:class:`telegram.Chat`, optional): Sender of the message, sent on behalf of a
            chat. The channel itself for channel messages. The supergroup itself for messages from
            anonymous group administrators. The linked channel for messages automatically forwarded
            to the discussion group.
        date (:class:`datetime.datetime`): Date the message was sent in Unix time. Converted to
            :class:`datetime.datetime`.
        chat (:class:`telegram.Chat`): Conversation the message belongs to.
        forward_from (:class:`telegram.User`, optional): For forwarded messages, sender of
            the original message.
        forward_from_chat (:class:`telegram.Chat`, optional): For messages forwarded from channels
            or from anonymous administrators, information about the original sender chat.
        forward_from_message_id (:obj:`int`, optional): For forwarded channel posts, identifier of
            the original message in the channel.
        forward_sender_name	(:obj:`str`, optional): Sender's name for messages forwarded from users
            who disallow adding a link to their account in forwarded messages.
        forward_date (:class:`datetime.datetime`, optional): For forwarded messages, date the
            original message was sent in Unix time. Converted to :class:`datetime.datetime`.
        reply_to_message (:class:`telegram.Message`, optional): For replies, the original message.
        edit_date (:class:`datetime.datetime`, optional): Date the message was last edited in Unix
            time. Converted to :class:`datetime.datetime`.
        media_group_id (:obj:`str`, optional): The unique identifier of a media message group this
            message belongs to.
        text (str, optional): For text messages, the actual UTF-8 text of the message, 0-4096
            characters. Also found as :attr:`telegram.constants.MAX_MESSAGE_LENGTH`.
        entities (List[:class:`telegram.MessageEntity`], optional): For text messages, special
            entities like usernames, URLs, bot commands, etc. that appear in the text. See
            :attr:`parse_entity` and :attr:`parse_entities` methods for how to use properly.
        caption_entities (List[:class:`telegram.MessageEntity`]): Optional. For Messages with a
            Caption. Special entities like usernames, URLs, bot commands, etc. that appear in the
            caption. See :attr:`Message.parse_caption_entity` and :attr:`parse_caption_entities`
            methods for how to use properly.
        audio (:class:`telegram.Audio`, optional): Message is an audio file, information
            about the file.
        document (:class:`telegram.Document`, optional): Message is a general file, information
            about the file.
        animation (:class:`telegram.Animation`, optional): Message is an animation, information
            about the animation. For backward compatibility, when this field is set, the document
            field will also be set.
        game (:class:`telegram.Game`, optional): Message is a game, information about the game.
        photo (List[:class:`telegram.PhotoSize`], optional): Message is a photo, available
            sizes of the photo.
        sticker (:class:`telegram.Sticker`, optional): Message is a sticker, information
            about the sticker.
        video (:class:`telegram.Video`, optional): Message is a video, information about the video.
        voice (:class:`telegram.Voice`, optional): Message is a voice message, information about
            the file.
        video_note (:class:`telegram.VideoNote`, optional): Message is a video note, information
            about the video message.
        new_chat_members (List[:class:`telegram.User`], optional): New members that were added to
            the group or supergroup and information about them (the bot itself may be one of these
            members).
        caption (:obj:`str`, optional): Caption for the animation, audio, document, photo, video
            or voice, 0-1024 characters.
        contact (:class:`telegram.Contact`, optional): Message is a shared contact, information
            about the contact.
        location (:class:`telegram.Location`, optional): Message is a shared location, information
            about the location.
        venue (:class:`telegram.Venue`, optional): Message is a venue, information about the venue.
            For backward compatibility, when this field is set, the location field will also be
            set.
        left_chat_member (:class:`telegram.User`, optional): A member was removed from the group,
            information about them (this member may be the bot itself).
        new_chat_title (:obj:`str`, optional): A chat title was changed to this value.
        new_chat_photo (List[:class:`telegram.PhotoSize`], optional): A chat photo was changed to
            this value.
        delete_chat_photo (:obj:`bool`, optional): Service message: The chat photo was deleted.
        group_chat_created (:obj:`bool`, optional): Service message: The group has been created.
        supergroup_chat_created (:obj:`bool`, optional): Service message: The supergroup has been
            created. This field can't be received in a message coming through updates, because bot
            can't be a member of a supergroup when it is created. It can only be found in
            :attr:`reply_to_message` if someone replies to a very first message in a directly
            created supergroup.
        channel_chat_created (:obj:`bool`, optional): Service message: The channel has been
            created. This field can't be received in a message coming through updates, because bot
            can't be a member of a channel when it is created. It can only be found in
            :attr:`reply_to_message` if someone replies to a very first message in a channel.
        message_auto_delete_timer_changed (:class:`telegram.MessageAutoDeleteTimerChanged`, \
            optional): Service message: auto-delete timer settings changed in the chat.

            .. versionadded:: 13.4
        migrate_to_chat_id (:obj:`int`, optional): The group has been migrated to a supergroup with
            the specified identifier. This number may be greater than 32 bits and some programming
            languages may have difficulty/silent defects in interpreting it. But it is smaller than
            52 bits, so a signed 64 bit integer or double-precision float type are safe for storing
            this identifier.
        migrate_from_chat_id (:obj:`int`, optional): The supergroup has been migrated from a group
            with the specified identifier. This number may be greater than 32 bits and some
            programming languages may have difficulty/silent defects in interpreting it. But it is
            smaller than 52 bits, so a signed 64 bit integer or double-precision float type are
            safe for storing this identifier.
        pinned_message (:class:`telegram.Message`, optional): Specified message was pinned. Note
            that the Message object in this field will not contain further :attr:`reply_to_message`
            fields even if it is itself a reply.
        invoice (:class:`telegram.Invoice`, optional): Message is an invoice for a payment,
            information about the invoice.
        successful_payment (:class:`telegram.SuccessfulPayment`, optional): Message is a service
            message about a successful payment, information about the payment.
        connected_website (:obj:`str`, optional): The domain name of the website on which the user
            has logged in.
        forward_signature (:obj:`str`, optional): For messages forwarded from channels, signature
            of the post author if present.
        author_signature (:obj:`str`, optional):  Signature of the post author for messages in
            channels, or the custom title of an anonymous group administrator.
        passport_data (:class:`telegram.PassportData`, optional): Telegram Passport data.
        poll (:class:`telegram.Poll`, optional): Message is a native poll,
            information about the poll.
        dice (:class:`telegram.Dice`, optional): Message is a dice with random value from 1 to 6.
        via_bot (:class:`telegram.User`, optional): Message was sent through an inline bot.
        proximity_alert_triggered (:class:`telegram.ProximityAlertTriggered`, optional): Service
            message. A user in the chat triggered another user's proximity alert while sharing
            Live Location.
        voice_chat_scheduled (:class:`telegram.VoiceChatScheduled`, optional): Service message:
            voice chat scheduled.

            .. versionadded:: 13.5
        voice_chat_started (:class:`telegram.VoiceChatStarted`, optional): Service message: voice
            chat started.

            .. versionadded:: 13.4
        voice_chat_ended (:class:`telegram.VoiceChatEnded`, optional): Service message: voice chat
            ended.

            .. versionadded:: 13.4
        voice_chat_participants_invited (:class:`telegram.VoiceChatParticipantsInvited` optional):
            Service message: new participants invited to a voice chat.

            .. versionadded:: 13.4
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message. ``login_url`` buttons are represented as ordinary url buttons.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    Attributes:
        message_id (:obj:`int`): Unique message identifier inside this chat.
        from_user (:class:`telegram.User`): Optional. Sender.
        sender_chat (:class:`telegram.Chat`): Optional. Sender of the message, sent on behalf of a
            chat. The channel itself for channel messages. The supergroup itself for messages from
            anonymous group administrators. The linked channel for messages automatically forwarded
            to the discussion group.
        date (:class:`datetime.datetime`): Date the message was sent.
        chat (:class:`telegram.Chat`): Conversation the message belongs to.
        forward_from (:class:`telegram.User`): Optional. Sender of the original message.
        forward_from_chat (:class:`telegram.Chat`): Optional. For messages forwarded from channels
            or from anonymous administrators, information about the original sender chat.
        forward_from_message_id (:obj:`int`): Optional. Identifier of the original message in the
            channel.
        forward_date (:class:`datetime.datetime`): Optional. Date the original message was sent.
        reply_to_message (:class:`telegram.Message`): Optional. For replies, the original message.
            Note that the Message object in this field will not contain further
            ``reply_to_message`` fields even if it itself is a reply.
        edit_date (:class:`datetime.datetime`): Optional. Date the message was last edited.
        media_group_id (:obj:`str`): Optional. The unique identifier of a media message group this
            message belongs to.
        text (:obj:`str`): Optional. The actual UTF-8 text of the message.
        entities (List[:class:`telegram.MessageEntity`]): Optional. Special entities like
            usernames, URLs, bot commands, etc. that appear in the text. See
            :attr:`Message.parse_entity` and :attr:`parse_entities` methods for how to use
            properly.
        caption_entities (List[:class:`telegram.MessageEntity`]): Optional. Special entities like
            usernames, URLs, bot commands, etc. that appear in the caption. See
            :attr:`Message.parse_caption_entity` and :attr:`parse_caption_entities` methods for how
            to use properly.
        audio (:class:`telegram.Audio`): Optional. Information about the file.
        document (:class:`telegram.Document`): Optional. Information about the file.
        animation (:class:`telegram.Animation`) Optional. Information about the file.
            For backward compatibility, when this field is set, the document field will also be
            set.
        game (:class:`telegram.Game`): Optional. Information about the game.
        photo (List[:class:`telegram.PhotoSize`]): Optional. Available sizes of the photo.
        sticker (:class:`telegram.Sticker`): Optional. Information about the sticker.
        video (:class:`telegram.Video`): Optional. Information about the video.
        voice (:class:`telegram.Voice`): Optional. Information about the file.
        video_note (:class:`telegram.VideoNote`): Optional. Information about the video message.
        new_chat_members (List[:class:`telegram.User`]): Optional. Information about new members to
            the chat. (the bot itself may be one of these members).
        caption (:obj:`str`): Optional. Caption for the document, photo or video, 0-1024
            characters.
        contact (:class:`telegram.Contact`): Optional. Information about the contact.
        location (:class:`telegram.Location`): Optional. Information about the location.
        venue (:class:`telegram.Venue`): Optional. Information about the venue.
        left_chat_member (:class:`telegram.User`): Optional. Information about the user that left
            the group. (this member may be the bot itself).
        new_chat_title (:obj:`str`): Optional. A chat title was changed to this value.
        new_chat_photo (List[:class:`telegram.PhotoSize`]): Optional. A chat photo was changed to
            this value.
        delete_chat_photo (:obj:`bool`): Optional. The chat photo was deleted.
        group_chat_created (:obj:`bool`): Optional. The group has been created.
        supergroup_chat_created (:obj:`bool`): Optional. The supergroup has been created.
        channel_chat_created (:obj:`bool`): Optional. The channel has been created.
        message_auto_delete_timer_changed (:class:`telegram.MessageAutoDeleteTimerChanged`):
            Optional. Service message: auto-delete timer settings changed in the chat.

            .. versionadded:: 13.4
        migrate_to_chat_id (:obj:`int`): Optional. The group has been migrated to a supergroup with
            the specified identifier.
        migrate_from_chat_id (:obj:`int`): Optional. The supergroup has been migrated from a group
            with the specified identifier.
        pinned_message (:class:`telegram.message`): Optional. Specified message was pinned.
        invoice (:class:`telegram.Invoice`): Optional. Information about the invoice.
        successful_payment (:class:`telegram.SuccessfulPayment`): Optional. Information about the
            payment.
        connected_website (:obj:`str`): Optional. The domain name of the website on which the user
            has logged in.
        forward_signature (:obj:`str`): Optional. Signature of the post author for messages
            forwarded from channels.
        forward_sender_name	(:obj:`str`): Optional. Sender's name for messages forwarded from users
            who disallow adding a link to their account in forwarded messages.
        author_signature (:obj:`str`): Optional. Signature of the post author for messages in
            channels, or the custom title of an anonymous group administrator.
        passport_data (:class:`telegram.PassportData`): Optional. Telegram Passport data.
        poll (:class:`telegram.Poll`): Optional. Message is a native poll,
            information about the poll.
        dice (:class:`telegram.Dice`): Optional. Message is a dice.
        via_bot (:class:`telegram.User`): Optional. Bot through which the message was sent.
        proximity_alert_triggered (:class:`telegram.ProximityAlertTriggered`): Optional. Service
            message. A user in the chat triggered another user's proximity alert while sharing
            Live Location.
        voice_chat_scheduled (:class:`telegram.VoiceChatScheduled`): Optional. Service message:
            voice chat scheduled.

            .. versionadded:: 13.5
        voice_chat_started (:class:`telegram.VoiceChatStarted`): Optional. Service message: voice
            chat started.

            .. versionadded:: 13.4
        voice_chat_ended (:class:`telegram.VoiceChatEnded`): Optional. Service message: voice chat
            ended.

            .. versionadded:: 13.4
        voice_chat_participants_invited (:class:`telegram.VoiceChatParticipantsInvited`): Optional.
            Service message: new participants invited to a voice chat.

            .. versionadded:: 13.4
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    """
    # fmt: on

    _effective_attachment = _UNDEFINED

    ATTACHMENT_TYPES: ClassVar[List[str]] = [
        'audio',
        'game',
        'animation',
        'document',
        'photo',
        'sticker',
        'video',
        'voice',
        'video_note',
        'contact',
        'location',
        'venue',
        'invoice',
        'successful_payment',
    ]
    MESSAGE_TYPES: ClassVar[List[str]] = [
        'text',
        'new_chat_members',
        'left_chat_member',
        'new_chat_title',
        'new_chat_photo',
        'delete_chat_photo',
        'group_chat_created',
        'supergroup_chat_created',
        'channel_chat_created',
        'message_auto_delete_timer_changed',
        'migrate_to_chat_id',
        'migrate_from_chat_id',
        'pinned_message',
        'poll',
        'dice',
        'passport_data',
        'proximity_alert_triggered',
        'voice_chat_scheduled',
        'voice_chat_started',
        'voice_chat_ended',
        'voice_chat_participants_invited',
    ] + ATTACHMENT_TYPES

    def __init__(
        self,
        message_id: int,
        date: datetime.datetime,
        chat: Chat,
        from_user: User = None,
        forward_from: User = None,
        forward_from_chat: Chat = None,
        forward_from_message_id: int = None,
        forward_date: datetime.datetime = None,
        reply_to_message: 'Message' = None,
        edit_date: datetime.datetime = None,
        text: str = None,
        entities: List['MessageEntity'] = None,
        caption_entities: List['MessageEntity'] = None,
        audio: Audio = None,
        document: Document = None,
        game: Game = None,
        photo: List[PhotoSize] = None,
        sticker: Sticker = None,
        video: Video = None,
        voice: Voice = None,
        video_note: VideoNote = None,
        new_chat_members: List[User] = None,
        caption: str = None,
        contact: Contact = None,
        location: Location = None,
        venue: Venue = None,
        left_chat_member: User = None,
        new_chat_title: str = None,
        new_chat_photo: List[PhotoSize] = None,
        delete_chat_photo: bool = False,
        group_chat_created: bool = False,
        supergroup_chat_created: bool = False,
        channel_chat_created: bool = False,
        migrate_to_chat_id: int = None,
        migrate_from_chat_id: int = None,
        pinned_message: 'Message' = None,
        invoice: Invoice = None,
        successful_payment: SuccessfulPayment = None,
        forward_signature: str = None,
        author_signature: str = None,
        media_group_id: str = None,
        connected_website: str = None,
        animation: Animation = None,
        passport_data: PassportData = None,
        poll: Poll = None,
        forward_sender_name: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        bot: 'Bot' = None,
        dice: Dice = None,
        via_bot: User = None,
        proximity_alert_triggered: ProximityAlertTriggered = None,
        sender_chat: Chat = None,
        voice_chat_started: VoiceChatStarted = None,
        voice_chat_ended: VoiceChatEnded = None,
        voice_chat_participants_invited: VoiceChatParticipantsInvited = None,
        message_auto_delete_timer_changed: MessageAutoDeleteTimerChanged = None,
        voice_chat_scheduled: VoiceChatScheduled = None,
        **_kwargs: Any,
    ):
        # Required
        self.message_id = int(message_id)
        # Optionals
        self.from_user = from_user
        self.sender_chat = sender_chat
        self.date = date
        self.chat = chat
        self.forward_from = forward_from
        self.forward_from_chat = forward_from_chat
        self.forward_date = forward_date
        self.reply_to_message = reply_to_message
        self.edit_date = edit_date
        self.text = text
        self.entities = entities or []
        self.caption_entities = caption_entities or []
        self.audio = audio
        self.game = game
        self.document = document
        self.photo = photo or []
        self.sticker = sticker
        self.video = video
        self.voice = voice
        self.video_note = video_note
        self.caption = caption
        self.contact = contact
        self.location = location
        self.venue = venue
        self.new_chat_members = new_chat_members or []
        self.left_chat_member = left_chat_member
        self.new_chat_title = new_chat_title
        self.new_chat_photo = new_chat_photo or []
        self.delete_chat_photo = bool(delete_chat_photo)
        self.group_chat_created = bool(group_chat_created)
        self.supergroup_chat_created = bool(supergroup_chat_created)
        self.migrate_to_chat_id = migrate_to_chat_id
        self.migrate_from_chat_id = migrate_from_chat_id
        self.channel_chat_created = bool(channel_chat_created)
        self.message_auto_delete_timer_changed = message_auto_delete_timer_changed
        self.pinned_message = pinned_message
        self.forward_from_message_id = forward_from_message_id
        self.invoice = invoice
        self.successful_payment = successful_payment
        self.connected_website = connected_website
        self.forward_signature = forward_signature
        self.forward_sender_name = forward_sender_name
        self.author_signature = author_signature
        self.media_group_id = media_group_id
        self.animation = animation
        self.passport_data = passport_data
        self.poll = poll
        self.dice = dice
        self.via_bot = via_bot
        self.proximity_alert_triggered = proximity_alert_triggered
        self.voice_chat_scheduled = voice_chat_scheduled
        self.voice_chat_started = voice_chat_started
        self.voice_chat_ended = voice_chat_ended
        self.voice_chat_participants_invited = voice_chat_participants_invited
        self.reply_markup = reply_markup
        self.bot = bot

        self._id_attrs = (self.message_id, self.chat)

    @property
    def chat_id(self) -> int:
        """:obj:`int`: Shortcut for :attr:`telegram.Chat.id` for :attr:`chat`."""
        return self.chat.id

    @property
    def link(self) -> Optional[str]:
        """:obj:`str`: Convenience property. If the chat of the message is not
        a private chat or normal group, returns a t.me link of the message."""
        if self.chat.type not in [Chat.PRIVATE, Chat.GROUP]:
            if self.chat.username:
                to_link = self.chat.username
            else:
                # Get rid of leading -100 for supergroups
                to_link = f"c/{str(self.chat.id)[4:]}"
            return f"https://t.me/{to_link}/{self.message_id}"
        return None

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['Message']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['from_user'] = User.de_json(data.get('from'), bot)
        data['sender_chat'] = Chat.de_json(data.get('sender_chat'), bot)
        data['date'] = from_timestamp(data['date'])
        data['chat'] = Chat.de_json(data.get('chat'), bot)
        data['entities'] = MessageEntity.de_list(data.get('entities'), bot)
        data['caption_entities'] = MessageEntity.de_list(data.get('caption_entities'), bot)
        data['forward_from'] = User.de_json(data.get('forward_from'), bot)
        data['forward_from_chat'] = Chat.de_json(data.get('forward_from_chat'), bot)
        data['forward_date'] = from_timestamp(data.get('forward_date'))
        data['reply_to_message'] = Message.de_json(data.get('reply_to_message'), bot)
        data['edit_date'] = from_timestamp(data.get('edit_date'))
        data['audio'] = Audio.de_json(data.get('audio'), bot)
        data['document'] = Document.de_json(data.get('document'), bot)
        data['animation'] = Animation.de_json(data.get('animation'), bot)
        data['game'] = Game.de_json(data.get('game'), bot)
        data['photo'] = PhotoSize.de_list(data.get('photo'), bot)
        data['sticker'] = Sticker.de_json(data.get('sticker'), bot)
        data['video'] = Video.de_json(data.get('video'), bot)
        data['voice'] = Voice.de_json(data.get('voice'), bot)
        data['video_note'] = VideoNote.de_json(data.get('video_note'), bot)
        data['contact'] = Contact.de_json(data.get('contact'), bot)
        data['location'] = Location.de_json(data.get('location'), bot)
        data['venue'] = Venue.de_json(data.get('venue'), bot)
        data['new_chat_members'] = User.de_list(data.get('new_chat_members'), bot)
        data['left_chat_member'] = User.de_json(data.get('left_chat_member'), bot)
        data['new_chat_photo'] = PhotoSize.de_list(data.get('new_chat_photo'), bot)
        data['message_auto_delete_timer_changed'] = MessageAutoDeleteTimerChanged.de_json(
            data.get('message_auto_delete_timer_changed'), bot
        )
        data['pinned_message'] = Message.de_json(data.get('pinned_message'), bot)
        data['invoice'] = Invoice.de_json(data.get('invoice'), bot)
        data['successful_payment'] = SuccessfulPayment.de_json(data.get('successful_payment'), bot)
        data['passport_data'] = PassportData.de_json(data.get('passport_data'), bot)
        data['poll'] = Poll.de_json(data.get('poll'), bot)
        data['dice'] = Dice.de_json(data.get('dice'), bot)
        data['via_bot'] = User.de_json(data.get('via_bot'), bot)
        data['proximity_alert_triggered'] = ProximityAlertTriggered.de_json(
            data.get('proximity_alert_triggered'), bot
        )
        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['voice_chat_scheduled'] = VoiceChatScheduled.de_json(
            data.get('voice_chat_scheduled'), bot
        )
        data['voice_chat_started'] = VoiceChatStarted.de_json(data.get('voice_chat_started'), bot)
        data['voice_chat_ended'] = VoiceChatEnded.de_json(data.get('voice_chat_ended'), bot)
        data['voice_chat_participants_invited'] = VoiceChatParticipantsInvited.de_json(
            data.get('voice_chat_participants_invited'), bot
        )
        return cls(bot=bot, **data)

    @property
    def effective_attachment(
        self,
    ) -> Union[
        Contact,
        Document,
        Animation,
        Game,
        Invoice,
        Location,
        List[PhotoSize],
        Sticker,
        SuccessfulPayment,
        Venue,
        Video,
        VideoNote,
        Voice,
        None,
    ]:
        """
        :class:`telegram.Audio`
            or :class:`telegram.Contact`
            or :class:`telegram.Document`
            or :class:`telegram.Animation`
            or :class:`telegram.Game`
            or :class:`telegram.Invoice`
            or :class:`telegram.Location`
            or List[:class:`telegram.PhotoSize`]
            or :class:`telegram.Sticker`
            or :class:`telegram.SuccessfulPayment`
            or :class:`telegram.Venue`
            or :class:`telegram.Video`
            or :class:`telegram.VideoNote`
            or :class:`telegram.Voice`: The attachment that this message was sent with. May be
            :obj:`None` if no attachment was sent.

        """
        if self._effective_attachment is not _UNDEFINED:
            return self._effective_attachment  # type: ignore

        for i in Message.ATTACHMENT_TYPES:
            if getattr(self, i, None):
                self._effective_attachment = getattr(self, i)
                break
        else:
            self._effective_attachment = None

        return self._effective_attachment  # type: ignore

    def __getitem__(self, item: str) -> Any:  # pylint: disable=R1710
        if item in self.__dict__.keys():
            return self.__dict__[item]
        if item == 'chat_id':
            return self.chat.id

    def to_dict(self) -> JSONDict:
        data = super().to_dict()

        # Required
        data['date'] = to_timestamp(self.date)
        # Optionals
        if self.forward_date:
            data['forward_date'] = to_timestamp(self.forward_date)
        if self.edit_date:
            data['edit_date'] = to_timestamp(self.edit_date)
        if self.photo:
            data['photo'] = [p.to_dict() for p in self.photo]
        if self.entities:
            data['entities'] = [e.to_dict() for e in self.entities]
        if self.caption_entities:
            data['caption_entities'] = [e.to_dict() for e in self.caption_entities]
        if self.new_chat_photo:
            data['new_chat_photo'] = [p.to_dict() for p in self.new_chat_photo]
        if self.new_chat_members:
            data['new_chat_members'] = [u.to_dict() for u in self.new_chat_members]

        return data

    def _quote(self, quote: Optional[bool], reply_to_message_id: Optional[int]) -> Optional[int]:
        """Modify kwargs for replying with or without quoting."""
        if reply_to_message_id is not None:
            return reply_to_message_id

        if quote is not None:
            if quote:
                return self.message_id

        else:
            if self.bot.defaults:
                default_quote = self.bot.defaults.quote
            else:
                default_quote = None
            if (default_quote is None and self.chat.type != Chat.PRIVATE) or default_quote:
                return self.message_id

        return None

    def reply_text(
        self,
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the message is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
        )

    def reply_markdown(
        self,
        text: str,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(
                update.effective_message.chat_id,
                parse_mode=ParseMode.MARKDOWN,
                *args,
                **kwargs,
            )

        Sends a message with Markdown version 1 formatting.

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Note:
            :attr:`telegram.ParseMode.MARKDOWN` is a legacy mode, retained by Telegram for
            backward compatibility. You should use :meth:`reply_markdown_v2` instead.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the message is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.
        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
        )

    def reply_markdown_v2(
        self,
        text: str,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(
                update.effective_message.chat_id,
                parse_mode=ParseMode.MARKDOWN_V2,
                *args,
                **kwargs,
            )

        Sends a message with markdown version 2 formatting.

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the message is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.
        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
        )

    def reply_html(
        self,
        text: str,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(
                update.effective_message.chat_id,
                parse_mode=ParseMode.HTML,
                *args,
                **kwargs,
            )

        Sends a message with HTML formatting.

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the message is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.
        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
        )

    def reply_media_group(
        self,
        media: List[
            Union['InputMediaAudio', 'InputMediaDocument', 'InputMediaPhoto', 'InputMediaVideo']
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        quote: bool = None,
    ) -> List['Message']:
        """Shortcut for::

            bot.send_media_group(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_media_group`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the media group is sent as an
                actual reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``,
                this parameter will be ignored. Default: :obj:`True` in group chats and
                :obj:`False` in private chats.

        Returns:
            List[:class:`telegram.Message`]: An array of the sent Messages.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_media_group(
            chat_id=self.chat_id,
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def reply_photo(
        self,
        photo: Union[FileInput, 'PhotoSize'],
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_photo(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_photo`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the photo is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``,
                this parameter will be ignored. Default: :obj:`True` in group chats and
                :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_photo(
            chat_id=self.chat_id,
            photo=photo,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def reply_audio(
        self,
        audio: Union[FileInput, 'Audio'],
        duration: int = None,
        performer: str = None,
        title: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_audio(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_audio`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the audio is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``,
                this parameter will be ignored. Default: :obj:`True` in group chats and
                :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_audio(
            chat_id=self.chat_id,
            audio=audio,
            duration=duration,
            performer=performer,
            title=title,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def reply_document(
        self,
        document: Union[FileInput, 'Document'],
        filename: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        disable_content_type_detection: bool = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_document(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_document`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the document is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_document(
            chat_id=self.chat_id,
            document=document,
            filename=filename,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            thumb=thumb,
            api_kwargs=api_kwargs,
            disable_content_type_detection=disable_content_type_detection,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
        )

    def reply_animation(
        self,
        animation: Union[FileInput, 'Animation'],
        duration: int = None,
        width: int = None,
        height: int = None,
        thumb: FileInput = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_animation(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_animation`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the animation is sent as an
                actual reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``,
                this parameter will be ignored. Default: :obj:`True` in group chats and
                :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_animation(
            chat_id=self.chat_id,
            animation=animation,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def reply_sticker(
        self,
        sticker: Union[FileInput, 'Sticker'],
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_sticker(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_sticker`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the sticker is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_sticker(
            chat_id=self.chat_id,
            sticker=sticker,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def reply_video(
        self,
        video: Union[FileInput, 'Video'],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        width: int = None,
        height: int = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        supports_streaming: bool = None,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_video(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the video is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_video(
            chat_id=self.chat_id,
            video=video,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            width=width,
            height=height,
            parse_mode=parse_mode,
            supports_streaming=supports_streaming,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def reply_video_note(
        self,
        video_note: Union[FileInput, 'VideoNote'],
        duration: int = None,
        length: int = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: str = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_video_note(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video_note`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the video note is sent as an
                actual reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``,
                this parameter will be ignored. Default: :obj:`True` in group chats and
                :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_video_note(
            chat_id=self.chat_id,
            video_note=video_note,
            duration=duration,
            length=length,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            filename=filename,
        )

    def reply_voice(
        self,
        voice: Union[FileInput, 'Voice'],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_voice(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_voice`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the voice note is sent as an
                actual reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``,
                this parameter will be ignored. Default: :obj:`True` in group chats and
                :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_voice(
            chat_id=self.chat_id,
            voice=voice,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def reply_location(
        self,
        latitude: float = None,
        longitude: float = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        location: Location = None,
        live_period: int = None,
        api_kwargs: JSONDict = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_location(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_location`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the location is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_location(
            chat_id=self.chat_id,
            latitude=latitude,
            longitude=longitude,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            location=location,
            live_period=live_period,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def reply_venue(
        self,
        latitude: float = None,
        longitude: float = None,
        title: str = None,
        address: str = None,
        foursquare_id: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        venue: Venue = None,
        foursquare_type: str = None,
        api_kwargs: JSONDict = None,
        google_place_id: str = None,
        google_place_type: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_venue(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_venue`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the venue is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_venue(
            chat_id=self.chat_id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            venue=venue,
            foursquare_type=foursquare_type,
            api_kwargs=api_kwargs,
            google_place_id=google_place_id,
            google_place_type=google_place_type,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def reply_contact(
        self,
        phone_number: str = None,
        first_name: str = None,
        last_name: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        contact: Contact = None,
        vcard: str = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_contact(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_contact`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the contact is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False` in
                private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_contact(
            chat_id=self.chat_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            contact=contact,
            vcard=vcard,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def reply_poll(
        self,
        question: str,
        options: List[str],
        is_anonymous: bool = True,
        type: str = Poll.REGULAR,  # pylint: disable=W0622
        allows_multiple_answers: bool = False,
        correct_option_id: int = None,
        is_closed: bool = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        explanation: str = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        open_period: int = None,
        close_date: Union[int, datetime.datetime] = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        explanation_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_poll(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_poll`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the poll is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``,
                this parameter will be ignored. Default: :obj:`True` in group chats and
                :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_poll(
            chat_id=self.chat_id,
            question=question,
            options=options,
            is_anonymous=is_anonymous,
            type=type,
            allows_multiple_answers=allows_multiple_answers,
            correct_option_id=correct_option_id,
            is_closed=is_closed,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            open_period=open_period,
            close_date=close_date,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            explanation_entities=explanation_entities,
        )

    def reply_dice(
        self,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        emoji: str = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_dice(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_dice`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the dice is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False`
                in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_dice(
            chat_id=self.chat_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            emoji=emoji,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def reply_chat_action(
        self,
        action: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            bot.send_chat_action(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_chat_action`.

        .. versionadded:: 13.2

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.send_chat_action(
            chat_id=self.chat_id,
            action=action,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def reply_game(
        self,
        game_short_name: str,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        quote: bool = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_game(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_game`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the game is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False`
                in private chats.

        .. versionadded:: 13.2

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_game(
            chat_id=self.chat_id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def reply_invoice(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: List['LabeledPrice'],
        start_parameter: str = None,
        photo_url: str = None,
        photo_size: int = None,
        photo_width: int = None,
        photo_height: int = None,
        need_name: bool = None,
        need_phone_number: bool = None,
        need_email: bool = None,
        need_shipping_address: bool = None,
        is_flexible: bool = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        provider_data: Union[str, object] = None,
        send_phone_number_to_provider: bool = None,
        send_email_to_provider: bool = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        quote: bool = None,
        max_tip_amount: int = None,
        suggested_tip_amounts: List[int] = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_invoice(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_invoice`.

        Warning:
            As of API 5.2 :attr:`start_parameter` is an optional argument and therefore the order
            of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        .. versionadded:: 13.2

        .. versionchanged:: 13.5
            As of Bot API 5.2, the parameter :attr:`start_parameter` is optional.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the invoice is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``, this
                parameter will be ignored. Default: :obj:`True` in group chats and :obj:`False`
                in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.send_invoice(
            chat_id=self.chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
            start_parameter=start_parameter,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            is_flexible=is_flexible,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            provider_data=provider_data,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
        )

    def forward(
        self,
        chat_id: Union[int, str],
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'Message':
        """Shortcut for::

            bot.forward_message(chat_id=chat_id,
                                from_chat_id=update.effective_message.chat_id,
                                message_id=update.effective_message.message_id,
                                *args,
                                **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.forward_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message forwarded.

        """
        return self.bot.forward_message(
            chat_id=chat_id,
            from_chat_id=self.chat_id,
            message_id=self.message_id,
            disable_notification=disable_notification,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def copy(
        self,
        chat_id: Union[int, str],
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[Tuple['MessageEntity', ...], List['MessageEntity']] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'MessageId':
        """Shortcut for::

            bot.copy_message(chat_id=chat_id,
                             from_chat_id=update.effective_message.chat_id,
                             message_id=update.effective_message.message_id,
                             *args,
                             **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Returns:
            :class:`telegram.MessageId`: On success, returns the MessageId of the sent message.

        """
        return self.bot.copy_message(
            chat_id=chat_id,
            from_chat_id=self.chat_id,
            message_id=self.message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def reply_copy(
        self,
        from_chat_id: Union[str, int],
        message_id: int,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[Tuple['MessageEntity', ...], List['MessageEntity']] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        quote: bool = None,
    ) -> 'MessageId':
        """Shortcut for::

            bot.copy_message(chat_id=message.chat.id,
                             from_chat_id=from_chat_id,
                             message_id=message_id,
                             *args,
                             **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the copy is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed in ``kwargs``,
                this parameter will be ignored. Default: :obj:`True` in group chats and
                :obj:`False` in private chats.

                .. versionadded:: 13.1

        Returns:
            :class:`telegram.MessageId`: On success, returns the MessageId of the sent message.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return self.bot.copy_message(
            chat_id=self.chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def edit_text(
        self,
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> Union['Message', bool]:
        """Shortcut for::

            bot.edit_message_text(chat_id=message.chat_id,
                                  message_id=message.message_id,
                                  *args,
                                  **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.edit_message_text`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.

        """
        return self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            entities=entities,
            inline_message_id=None,
        )

    def edit_caption(
        self,
        caption: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> Union['Message', bool]:
        """Shortcut for::

            bot.edit_message_caption(chat_id=message.chat_id,
                                     message_id=message.message_id,
                                     *args,
                                     **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_caption`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.

        """
        return self.bot.edit_message_caption(
            chat_id=self.chat_id,
            message_id=self.message_id,
            caption=caption,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            caption_entities=caption_entities,
            inline_message_id=None,
        )

    def edit_media(
        self,
        media: 'InputMedia' = None,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union['Message', bool]:
        """Shortcut for::

            bot.edit_message_media(chat_id=message.chat_id,
                                   message_id=message.message_id,
                                   *args,
                                   **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_media`.

        Note:
            You can only edit messages that the bot sent itself(i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.

        """
        return self.bot.edit_message_media(
            chat_id=self.chat_id,
            message_id=self.message_id,
            media=media,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    def edit_reply_markup(
        self,
        reply_markup: Optional['InlineKeyboardMarkup'] = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union['Message', bool]:
        """Shortcut for::

            bot.edit_message_reply_markup(chat_id=message.chat_id,
                                          message_id=message.message_id,
                                          *args,
                                          **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_reply_markup`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.
        """
        return self.bot.edit_message_reply_markup(
            chat_id=self.chat_id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    def edit_live_location(
        self,
        latitude: float = None,
        longitude: float = None,
        location: Location = None,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
    ) -> Union['Message', bool]:
        """Shortcut for::

            bot.edit_message_live_location(chat_id=message.chat_id,
                                           message_id=message.message_id,
                                           *args,
                                           **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_live_location`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.
        """
        return self.bot.edit_message_live_location(
            chat_id=self.chat_id,
            message_id=self.message_id,
            latitude=latitude,
            longitude=longitude,
            location=location,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            inline_message_id=None,
        )

    def stop_live_location(
        self,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union['Message', bool]:
        """Shortcut for::

            bot.stop_message_live_location(chat_id=message.chat_id,
                                           message_id=message.message_id,
                                           *args,
                                           **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.stop_message_live_location`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.
        """
        return self.bot.stop_message_live_location(
            chat_id=self.chat_id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    def set_game_score(
        self,
        user_id: Union[int, str],
        score: int,
        force: bool = None,
        disable_edit_message: bool = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union['Message', bool]:
        """Shortcut for::

            bot.set_game_score(chat_id=message.chat_id,
                               message_id=message.message_id,
                               *args,
                               **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.set_game_score`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.
        """
        return self.bot.set_game_score(
            chat_id=self.chat_id,
            message_id=self.message_id,
            user_id=user_id,
            score=score,
            force=force,
            disable_edit_message=disable_edit_message,
            timeout=timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    def get_game_high_scores(
        self,
        user_id: Union[int, str],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List['GameHighScore']:
        """Shortcut for::

            bot.get_game_high_scores(chat_id=message.chat_id,
                                     message_id=message.message_id,
                                     *args,
                                     **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_game_high_scores`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            List[:class:`telegram.GameHighScore`]
        """
        return self.bot.get_game_high_scores(
            chat_id=self.chat_id,
            message_id=self.message_id,
            user_id=user_id,
            timeout=timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    def delete(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             bot.delete_message(chat_id=message.chat_id,
                                message_id=message.message_id,
                                *args,
                                **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.delete_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.delete_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def stop_poll(
        self,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Poll:
        """Shortcut for::

             bot.stop_poll(chat_id=message.chat_id,
                           message_id=message.message_id,
                           *args,
                           **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.stop_poll`.

        Returns:
            :class:`telegram.Poll`: On success, the stopped Poll with the final results is
            returned.

        """
        return self.bot.stop_poll(
            chat_id=self.chat_id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def pin(
        self,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             bot.pin_chat_message(chat_id=message.chat_id,
                                  message_id=message.message_id,
                                  *args,
                                  **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.pin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.pin_chat_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            disable_notification=disable_notification,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def unpin(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             bot.unpin_chat_message(chat_id=message.chat_id,
                                    message_id=message.message_id,
                                    *args,
                                    **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.unpin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.unpin_chat_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def parse_entity(self, entity: MessageEntity) -> str:
        """Returns the text from a given :class:`telegram.MessageEntity`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to this message.

        Returns:
            :obj:`str`: The text of the given entity.

        Raises:
            RuntimeError: If the message has no text.

        """
        if not self.text:
            raise RuntimeError("This Message has no 'text'.")

        # Is it a narrow build, if so we don't need to convert
        if sys.maxunicode == 0xFFFF:
            return self.text[entity.offset : entity.offset + entity.length]

        entity_text = self.text.encode('utf-16-le')
        entity_text = entity_text[entity.offset * 2 : (entity.offset + entity.length) * 2]
        return entity_text.decode('utf-16-le')

    def parse_caption_entity(self, entity: MessageEntity) -> str:
        """Returns the text from a given :class:`telegram.MessageEntity`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.caption`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to this message.

        Returns:
            :obj:`str`: The text of the given entity.

        Raises:
            RuntimeError: If the message has no caption.

        """
        if not self.caption:
            raise RuntimeError("This Message has no 'caption'.")

        # Is it a narrow build, if so we don't need to convert
        if sys.maxunicode == 0xFFFF:
            return self.caption[entity.offset : entity.offset + entity.length]

        entity_text = self.caption.encode('utf-16-le')
        entity_text = entity_text[entity.offset * 2 : (entity.offset + entity.length) * 2]
        return entity_text.decode('utf-16-le')

    def parse_entities(self, types: List[str] = None) -> Dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this message filtered by their
        :attr:`telegram.MessageEntity.type` attribute as the key, and the text that each entity
        belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`entities` attribute, since it
            calculates the correct substring from the message text based on UTF-16 codepoints.
            See :attr:`parse_entity` for more info.

        Args:
            types (List[:obj:`str`], optional): List of :class:`telegram.MessageEntity` types as
                strings. If the ``type`` attribute of an entity is contained in this list, it will
                be returned. Defaults to a list of all types. All types can be found as constants
                in :class:`telegram.MessageEntity`.

        Returns:
            Dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.

        """
        if types is None:
            types = MessageEntity.ALL_TYPES

        return {
            entity: self.parse_entity(entity)
            for entity in (self.entities or [])
            if entity.type in types
        }

    def parse_caption_entities(self, types: List[str] = None) -> Dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this message's caption filtered by their
        :attr:`telegram.MessageEntity.type` attribute as the key, and the text that each entity
        belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`caption_entities` attribute,
            since it calculates the correct substring from the message text based on UTF-16
            codepoints. See :attr:`parse_entity` for more info.

        Args:
            types (List[:obj:`str`], optional): List of :class:`telegram.MessageEntity` types as
                strings. If the ``type`` attribute of an entity is contained in this list, it will
                be returned. Defaults to a list of all types. All types can be found as constants
                in :class:`telegram.MessageEntity`.

        Returns:
            Dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.

        """
        if types is None:
            types = MessageEntity.ALL_TYPES

        return {
            entity: self.parse_caption_entity(entity)
            for entity in (self.caption_entities or [])
            if entity.type in types
        }

    @staticmethod
    def _parse_html(
        message_text: Optional[str],
        entities: Dict[MessageEntity, str],
        urled: bool = False,
        offset: int = 0,
    ) -> Optional[str]:
        if message_text is None:
            return None

        if sys.maxunicode != 0xFFFF:
            message_text = message_text.encode('utf-16-le')  # type: ignore

        html_text = ''
        last_offset = 0

        sorted_entities = sorted(entities.items(), key=(lambda item: item[0].offset))
        parsed_entities = []

        for (entity, text) in sorted_entities:
            if entity not in parsed_entities:
                nested_entities = {
                    e: t
                    for (e, t) in sorted_entities
                    if e.offset >= entity.offset
                    and e.offset + e.length <= entity.offset + entity.length
                    and e != entity
                }
                parsed_entities.extend(list(nested_entities.keys()))

                orig_text = text
                text = escape(text)

                if nested_entities:
                    text = Message._parse_html(
                        orig_text, nested_entities, urled=urled, offset=entity.offset
                    )

                if entity.type == MessageEntity.TEXT_LINK:
                    insert = f'<a href="{entity.url}">{text}</a>'
                elif entity.type == MessageEntity.TEXT_MENTION and entity.user:
                    insert = f'<a href="tg://user?id={entity.user.id}">{text}</a>'
                elif entity.type == MessageEntity.URL and urled:
                    insert = f'<a href="{text}">{text}</a>'
                elif entity.type == MessageEntity.BOLD:
                    insert = '<b>' + text + '</b>'
                elif entity.type == MessageEntity.ITALIC:
                    insert = '<i>' + text + '</i>'
                elif entity.type == MessageEntity.CODE:
                    insert = '<code>' + text + '</code>'
                elif entity.type == MessageEntity.PRE:
                    if entity.language:
                        insert = f'<pre><code class="{entity.language}">{text}</code></pre>'
                    else:
                        insert = '<pre>' + text + '</pre>'
                elif entity.type == MessageEntity.UNDERLINE:
                    insert = '<u>' + text + '</u>'
                elif entity.type == MessageEntity.STRIKETHROUGH:
                    insert = '<s>' + text + '</s>'
                else:
                    insert = text

                if offset == 0:
                    if sys.maxunicode == 0xFFFF:
                        html_text += (
                            escape(message_text[last_offset : entity.offset - offset]) + insert
                        )
                    else:
                        html_text += (
                            escape(
                                message_text[  # type: ignore
                                    last_offset * 2 : (entity.offset - offset) * 2
                                ].decode('utf-16-le')
                            )
                            + insert
                        )
                else:
                    if sys.maxunicode == 0xFFFF:
                        html_text += message_text[last_offset : entity.offset - offset] + insert
                    else:
                        html_text += (
                            message_text[  # type: ignore
                                last_offset * 2 : (entity.offset - offset) * 2
                            ].decode('utf-16-le')
                            + insert
                        )

                last_offset = entity.offset - offset + entity.length

        if offset == 0:
            if sys.maxunicode == 0xFFFF:
                html_text += escape(message_text[last_offset:])
            else:
                html_text += escape(
                    message_text[last_offset * 2 :].decode('utf-16-le')  # type: ignore
                )
        else:
            if sys.maxunicode == 0xFFFF:
                html_text += message_text[last_offset:]
            else:
                html_text += message_text[last_offset * 2 :].decode('utf-16-le')  # type: ignore

        return html_text

    @property
    def text_html(self) -> str:
        """Creates an HTML-formatted string from the markup entities found in the message.

        Use this if you want to retrieve the message text with the entities formatted as HTML in
        the same way the original message was formatted.

        Returns:
            :obj:`str`: Message text with entities formatted as HTML.

        """
        return self._parse_html(self.text, self.parse_entities(), urled=False)

    @property
    def text_html_urled(self) -> str:
        """Creates an HTML-formatted string from the markup entities found in the message.

        Use this if you want to retrieve the message text with the entities formatted as HTML.
        This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        Returns:
            :obj:`str`: Message text with entities formatted as HTML.

        """
        return self._parse_html(self.text, self.parse_entities(), urled=True)

    @property
    def caption_html(self) -> str:
        """Creates an HTML-formatted string from the markup entities found in the message's
        caption.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        HTML in the same way the original message was formatted.

        Returns:
            :obj:`str`: Message caption with caption entities formatted as HTML.

        """
        return self._parse_html(self.caption, self.parse_caption_entities(), urled=False)

    @property
    def caption_html_urled(self) -> str:
        """Creates an HTML-formatted string from the markup entities found in the message's
        caption.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        HTML. This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        Returns:
            :obj:`str`: Message caption with caption entities formatted as HTML.

        """
        return self._parse_html(self.caption, self.parse_caption_entities(), urled=True)

    @staticmethod
    def _parse_markdown(
        message_text: Optional[str],
        entities: Dict[MessageEntity, str],
        urled: bool = False,
        version: int = 1,
        offset: int = 0,
    ) -> Optional[str]:
        version = int(version)

        if message_text is None:
            return None

        if sys.maxunicode != 0xFFFF:
            message_text = message_text.encode('utf-16-le')  # type: ignore

        markdown_text = ''
        last_offset = 0

        sorted_entities = sorted(entities.items(), key=(lambda item: item[0].offset))
        parsed_entities = []

        for (entity, text) in sorted_entities:
            if entity not in parsed_entities:
                nested_entities = {
                    e: t
                    for (e, t) in sorted_entities
                    if e.offset >= entity.offset
                    and e.offset + e.length <= entity.offset + entity.length
                    and e != entity
                }
                parsed_entities.extend(list(nested_entities.keys()))

                orig_text = text
                text = escape_markdown(text, version=version)

                if nested_entities:
                    if version < 2:
                        raise ValueError(
                            'Nested entities are not supported for Markdown ' 'version 1'
                        )

                    text = Message._parse_markdown(
                        orig_text,
                        nested_entities,
                        urled=urled,
                        offset=entity.offset,
                        version=version,
                    )

                if entity.type == MessageEntity.TEXT_LINK:
                    if version == 1:
                        url = entity.url
                    else:
                        # Links need special escaping. Also can't have entities nested within
                        url = escape_markdown(
                            entity.url, version=version, entity_type=MessageEntity.TEXT_LINK
                        )
                    insert = f'[{text}]({url})'
                elif entity.type == MessageEntity.TEXT_MENTION and entity.user:
                    insert = f'[{text}](tg://user?id={entity.user.id})'
                elif entity.type == MessageEntity.URL and urled:
                    if version == 1:
                        link = orig_text
                    else:
                        link = text
                    insert = f'[{link}]({orig_text})'
                elif entity.type == MessageEntity.BOLD:
                    insert = '*' + text + '*'
                elif entity.type == MessageEntity.ITALIC:
                    insert = '_' + text + '_'
                elif entity.type == MessageEntity.CODE:
                    # Monospace needs special escaping. Also can't have entities nested within
                    insert = (
                        '`'
                        + escape_markdown(
                            orig_text, version=version, entity_type=MessageEntity.CODE
                        )
                        + '`'
                    )
                elif entity.type == MessageEntity.PRE:
                    # Monospace needs special escaping. Also can't have entities nested within
                    code = escape_markdown(
                        orig_text, version=version, entity_type=MessageEntity.PRE
                    )
                    if entity.language:
                        prefix = '```' + entity.language + '\n'
                    else:
                        if code.startswith('\\'):
                            prefix = '```'
                        else:
                            prefix = '```\n'
                    insert = prefix + code + '```'
                elif entity.type == MessageEntity.UNDERLINE:
                    if version == 1:
                        raise ValueError(
                            'Underline entities are not supported for Markdown ' 'version 1'
                        )
                    insert = '__' + text + '__'
                elif entity.type == MessageEntity.STRIKETHROUGH:
                    if version == 1:
                        raise ValueError(
                            'Strikethrough entities are not supported for Markdown ' 'version 1'
                        )
                    insert = '~' + text + '~'
                else:
                    insert = text

                if offset == 0:
                    if sys.maxunicode == 0xFFFF:
                        markdown_text += (
                            escape_markdown(
                                message_text[last_offset : entity.offset - offset], version=version
                            )
                            + insert
                        )
                    else:
                        markdown_text += (
                            escape_markdown(
                                message_text[  # type: ignore
                                    last_offset * 2 : (entity.offset - offset) * 2
                                ].decode('utf-16-le'),
                                version=version,
                            )
                            + insert
                        )
                else:
                    if sys.maxunicode == 0xFFFF:
                        markdown_text += (
                            message_text[last_offset : entity.offset - offset] + insert
                        )
                    else:
                        markdown_text += (
                            message_text[  # type: ignore
                                last_offset * 2 : (entity.offset - offset) * 2
                            ].decode('utf-16-le')
                            + insert
                        )

                last_offset = entity.offset - offset + entity.length

        if offset == 0:
            if sys.maxunicode == 0xFFFF:
                markdown_text += escape_markdown(message_text[last_offset:], version=version)
            else:
                markdown_text += escape_markdown(
                    message_text[last_offset * 2 :].decode('utf-16-le'),  # type: ignore
                    version=version,
                )
        else:
            if sys.maxunicode == 0xFFFF:
                markdown_text += message_text[last_offset:]
            else:
                markdown_text += message_text[last_offset * 2 :].decode(  # type: ignore
                    'utf-16-le'
                )

        return markdown_text

    @property
    def text_markdown(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message
        using :class:`telegram.ParseMode.MARKDOWN`.

        Use this if you want to retrieve the message text with the entities formatted as Markdown
        in the same way the original message was formatted.

        Note:
            :attr:`telegram.ParseMode.MARKDOWN` is is a legacy mode, retained by Telegram for
            backward compatibility. You should use :meth:`text_markdown_v2` instead.

        Returns:
            :obj:`str`: Message text with entities formatted as Markdown.

        """
        return self._parse_markdown(self.text, self.parse_entities(), urled=False)

    @property
    def text_markdown_v2(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message
        using :class:`telegram.ParseMode.MARKDOWN_V2`.

        Use this if you want to retrieve the message text with the entities formatted as Markdown
        in the same way the original message was formatted.

        Returns:
            :obj:`str`: Message text with entities formatted as Markdown.

        """
        return self._parse_markdown(self.text, self.parse_entities(), urled=False, version=2)

    @property
    def text_markdown_urled(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message
        using :class:`telegram.ParseMode.MARKDOWN`.

        Use this if you want to retrieve the message text with the entities formatted as Markdown.
        This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        Note:
            :attr:`telegram.ParseMode.MARKDOWN` is is a legacy mode, retained by Telegram for
            backward compatibility. You should use :meth:`text_markdown_v2_urled` instead.

        Returns:
            :obj:`str`: Message text with entities formatted as Markdown.

        """
        return self._parse_markdown(self.text, self.parse_entities(), urled=True)

    @property
    def text_markdown_v2_urled(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message
        using :class:`telegram.ParseMode.MARKDOWN_V2`.

        Use this if you want to retrieve the message text with the entities formatted as Markdown.
        This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        Returns:
            :obj:`str`: Message text with entities formatted as Markdown.

        """
        return self._parse_markdown(self.text, self.parse_entities(), urled=True, version=2)

    @property
    def caption_markdown(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message's
        caption using :class:`telegram.ParseMode.MARKDOWN`.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        Markdown in the same way the original message was formatted.

        Note:
            :attr:`telegram.ParseMode.MARKDOWN` is is a legacy mode, retained by Telegram for
            backward compatibility. You should use :meth:`caption_markdown_v2` instead.

        Returns:
            :obj:`str`: Message caption with caption entities formatted as Markdown.

        """
        return self._parse_markdown(self.caption, self.parse_caption_entities(), urled=False)

    @property
    def caption_markdown_v2(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message's
        caption using :class:`telegram.ParseMode.MARKDOWN_V2`.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        Markdown in the same way the original message was formatted.

        Returns:
            :obj:`str`: Message caption with caption entities formatted as Markdown.

        """
        return self._parse_markdown(
            self.caption, self.parse_caption_entities(), urled=False, version=2
        )

    @property
    def caption_markdown_urled(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message's
        caption using :class:`telegram.ParseMode.MARKDOWN`.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        Markdown. This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        Note:
            :attr:`telegram.ParseMode.MARKDOWN` is is a legacy mode, retained by Telegram for
            backward compatibility. You should use :meth:`caption_markdown_v2_urled` instead.

        Returns:
            :obj:`str`: Message caption with caption entities formatted as Markdown.

        """
        return self._parse_markdown(self.caption, self.parse_caption_entities(), urled=True)

    @property
    def caption_markdown_v2_urled(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message's
        caption using :class:`telegram.ParseMode.MARKDOWN_V2`.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        Markdown. This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        Returns:
            :obj:`str`: Message caption with caption entities formatted as Markdown.

        """
        return self._parse_markdown(
            self.caption, self.parse_caption_entities(), urled=True, version=2
        )
