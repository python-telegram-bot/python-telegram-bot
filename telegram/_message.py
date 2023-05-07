#!/usr/bin/env python
# pylint: disable=too-many-instance-attributes, too-many-arguments
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
from html import escape
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple, Union

from telegram._chat import Chat
from telegram._dice import Dice
from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.contact import Contact
from telegram._files.document import Document
from telegram._files.location import Location
from telegram._files.photosize import PhotoSize
from telegram._files.sticker import Sticker
from telegram._files.venue import Venue
from telegram._files.video import Video
from telegram._files.videonote import VideoNote
from telegram._files.voice import Voice
from telegram._forumtopic import (
    ForumTopicClosed,
    ForumTopicCreated,
    ForumTopicEdited,
    ForumTopicReopened,
    GeneralForumTopicHidden,
    GeneralForumTopicUnhidden,
)
from telegram._games.game import Game
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._messageautodeletetimerchanged import MessageAutoDeleteTimerChanged
from telegram._messageentity import MessageEntity
from telegram._passport.passportdata import PassportData
from telegram._payment.invoice import Invoice
from telegram._payment.successfulpayment import SuccessfulPayment
from telegram._poll import Poll
from telegram._proximityalerttriggered import ProximityAlertTriggered
from telegram._shared import ChatShared, UserShared
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.datetime import extract_tzinfo_from_defaults, from_timestamp
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram._utils.types import DVInput, FileInput, JSONDict, ODVInput, ReplyMarkup
from telegram._utils.warnings import warn
from telegram._videochat import (
    VideoChatEnded,
    VideoChatParticipantsInvited,
    VideoChatScheduled,
    VideoChatStarted,
)
from telegram._webappdata import WebAppData
from telegram._writeaccessallowed import WriteAccessAllowed
from telegram.constants import MessageAttachmentType, ParseMode
from telegram.helpers import escape_markdown
from telegram.warnings import PTBDeprecationWarning

if TYPE_CHECKING:
    from telegram import (
        Bot,
        GameHighScore,
        InputMedia,
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        LabeledPrice,
        MessageId,
    )


class Message(TelegramObject):
    # fmt: off
    """This object represents a message.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`message_id` and :attr:`chat` are equal.

    Note:
        In Python :keyword:`from` is a reserved word. Use :paramref:`from_user` instead.

    .. versionchanged:: 20.0

        * The arguments and attributes ``voice_chat_scheduled``, ``voice_chat_started`` and
          ``voice_chat_ended``, ``voice_chat_participants_invited`` were renamed to
          :paramref:`video_chat_scheduled`/:attr:`video_chat_scheduled`,
          :paramref:`video_chat_started`/:attr:`video_chat_started`,
          :paramref:`video_chat_ended`/:attr:`video_chat_ended` and
          :paramref:`video_chat_participants_invited`/:attr:`video_chat_participants_invited`,
          respectively, in accordance to Bot API 6.0.
        * The following are now keyword-only arguments in Bot methods:
          ``{read, write, connect, pool}_timeout``, ``api_kwargs``, ``contact``, ``quote``,
          ``filename``, ``loaction``, ``venue``. Use a named argument for those,
          and notice that some positional arguments changed position as a result.

    Args:
        message_id (:obj:`int`): Unique message identifier inside this chat.
        from_user (:class:`telegram.User`, optional): Sender of the message; empty for messages
            sent to channels. For backward compatibility, this will contain a fake sender user in
            non-channel chats, if the message was sent on behalf of a chat.
        sender_chat (:class:`telegram.Chat`, optional): Sender of the message, sent on behalf of a
            chat. For example, the channel itself for channel posts, the supergroup itself for
            messages from anonymous group administrators, the linked channel for messages
            automatically forwarded to the discussion group. For backward compatibility,
            :attr:`from_user` contains a fake sender user in non-channel chats, if the message was
            sent on behalf of a chat.
        date (:class:`datetime.datetime`): Date the message was sent in Unix time. Converted to
            :class:`datetime.datetime`.

            .. versionchanged:: 20.3
                |datetime_localization|
        chat (:class:`telegram.Chat`): Conversation the message belongs to.
        forward_from (:class:`telegram.User`, optional): For forwarded messages, sender of
            the original message.
        forward_from_chat (:class:`telegram.Chat`, optional): For messages forwarded from channels
            or from anonymous administrators, information about the original sender chat.
        forward_from_message_id (:obj:`int`, optional): For forwarded channel posts, identifier of
            the original message in the channel.
        forward_sender_name (:obj:`str`, optional): Sender's name for messages forwarded from
            users who disallow adding a link to their account in forwarded messages.
        forward_date (:class:`datetime.datetime`, optional): For forwarded messages, date the
            original message was sent in Unix time. Converted to :class:`datetime.datetime`.

            .. versionchanged:: 20.3
                |datetime_localization|
        is_automatic_forward (:obj:`bool`, optional): :obj:`True`, if the message is a channel
            post that was automatically forwarded to the connected discussion group.

            .. versionadded:: 13.9
        reply_to_message (:class:`telegram.Message`, optional): For replies, the original message.
            Note that the Message object in this field will not contain further
            ``reply_to_message`` fields even if it itself is a reply.
        edit_date (:class:`datetime.datetime`, optional): Date the message was last edited in Unix
            time. Converted to :class:`datetime.datetime`.

            .. versionchanged:: 20.3
                |datetime_localization|
        has_protected_content (:obj:`bool`, optional): :obj:`True`, if the message can't be
            forwarded.

            .. versionadded:: 13.9
        media_group_id (:obj:`str`, optional): The unique identifier of a media message group this
            message belongs to.
        text (:obj:`str`, optional): For text messages, the actual UTF-8 text of the message,
            0-:tg-const:`telegram.constants.MessageLimit.MAX_TEXT_LENGTH` characters.
        entities (Sequence[:class:`telegram.MessageEntity`], optional): For text messages, special
            entities like usernames, URLs, bot commands, etc. that appear in the text. See
            :attr:`parse_entity` and :attr:`parse_entities` methods for how to use properly.
            This list is empty if the message does not contain entities.

            .. versionchanged:: 20.0
                |sequenceclassargs|

        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): For messages with a
            Caption. Special entities like usernames, URLs, bot commands, etc. that appear in the
            caption. See :attr:`Message.parse_caption_entity` and :attr:`parse_caption_entities`
            methods for how to use properly. This list is empty if the message does not contain
            caption entities.

            .. versionchanged:: 20.0
                |sequenceclassargs|

        audio (:class:`telegram.Audio`, optional): Message is an audio file, information
            about the file.
        document (:class:`telegram.Document`, optional): Message is a general file, information
            about the file.
        animation (:class:`telegram.Animation`, optional): Message is an animation, information
            about the animation. For backward compatibility, when this field is set, the document
            field will also be set.
        game (:class:`telegram.Game`, optional): Message is a game, information about the game.
        photo (Sequence[:class:`telegram.PhotoSize`], optional): Message is a photo, available
            sizes of the photo. This list is empty if the message does not contain a photo.

            .. versionchanged:: 20.0
                |sequenceclassargs|

        sticker (:class:`telegram.Sticker`, optional): Message is a sticker, information
            about the sticker.
        video (:class:`telegram.Video`, optional): Message is a video, information about the
            video.
        voice (:class:`telegram.Voice`, optional): Message is a voice message, information about
            the file.
        video_note (:class:`telegram.VideoNote`, optional): Message is a video note, information
            about the video message.
        new_chat_members (Sequence[:class:`telegram.User`], optional): New members that were added
            to the group or supergroup and information about them (the bot itself may be one of
            these members). This list is empty if the message does not contain new chat members.

            .. versionchanged:: 20.0
                |sequenceclassargs|

        caption (:obj:`str`, optional): Caption for the animation, audio, document, photo, video
            or voice, 0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters.
        contact (:class:`telegram.Contact`, optional): Message is a shared contact, information
            about the contact.
        location (:class:`telegram.Location`, optional): Message is a shared location, information
            about the location.
        venue (:class:`telegram.Venue`, optional): Message is a venue, information about the
            venue. For backward compatibility, when this field is set, the location field will
            also be set.
        left_chat_member (:class:`telegram.User`, optional): A member was removed from the group,
            information about them (this member may be the bot itself).
        new_chat_title (:obj:`str`, optional): A chat title was changed to this value.
        new_chat_photo (Sequence[:class:`telegram.PhotoSize`], optional): A chat photo was changed
            to this value. This list is empty if the message does not contain a new chat photo.

            .. versionchanged:: 20.0
                |sequenceclassargs|

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
        migrate_to_chat_id (:obj:`int`, optional): The group has been migrated to a supergroup
            with the specified identifier.
        migrate_from_chat_id (:obj:`int`, optional): The supergroup has been migrated from a group
            with the specified identifier.
        pinned_message (:class:`telegram.Message`, optional): Specified message was pinned. Note
            that the Message object in this field will not contain further
            :attr:`reply_to_message` fields even if it is itself a reply.
        invoice (:class:`telegram.Invoice`, optional): Message is an invoice for a payment,
            information about the invoice.
        successful_payment (:class:`telegram.SuccessfulPayment`, optional): Message is a service
            message about a successful payment, information about the payment.
        connected_website (:obj:`str`, optional): The domain name of the website on which the user
            has logged in.
        forward_signature (:obj:`str`, optional): For messages forwarded from channels, signature
            of the post author if present.
        author_signature (:obj:`str`, optional): Signature of the post author for messages in
            channels, or the custom title of an anonymous group administrator.
        passport_data (:class:`telegram.PassportData`, optional): Telegram Passport data.
        poll (:class:`telegram.Poll`, optional): Message is a native poll,
            information about the poll.
        dice (:class:`telegram.Dice`, optional): Message is a dice with random value.
        via_bot (:class:`telegram.User`, optional): Bot through which message was sent.
        proximity_alert_triggered (:class:`telegram.ProximityAlertTriggered`, optional): Service
            message. A user in the chat triggered another user's proximity alert while sharing
            Live Location.
        video_chat_scheduled (:class:`telegram.VideoChatScheduled`, optional): Service message:
            video chat scheduled.

            .. versionadded:: 20.0
        video_chat_started (:class:`telegram.VideoChatStarted`, optional): Service message: video
            chat started.

            .. versionadded:: 20.0
        video_chat_ended (:class:`telegram.VideoChatEnded`, optional): Service message: video chat
            ended.

            .. versionadded:: 20.0
        video_chat_participants_invited (:class:`telegram.VideoChatParticipantsInvited` optional):
            Service message: new participants invited to a video chat.

            .. versionadded:: 20.0
        web_app_data (:class:`telegram.WebAppData`, optional): Service message: data sent by a Web
            App.

            .. versionadded:: 20.0
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message. :paramref:`~telegram.InlineKeyboardButton.login_url` buttons are
            represented as ordinary url buttons.
        is_topic_message (:obj:`bool`, optional): :obj:`True`, if the message is sent to a forum
            topic.

            .. versionadded:: 20.0
        message_thread_id (:obj:`int`, optional): Unique identifier of a message thread to which
            the message belongs; for supergroups only.

            .. versionadded:: 20.0
        forum_topic_created (:class:`telegram.ForumTopicCreated`, optional): Service message:
            forum topic created.

            .. versionadded:: 20.0
        forum_topic_closed (:class:`telegram.ForumTopicClosed`, optional): Service message:
            forum topic closed.

            .. versionadded:: 20.0
        forum_topic_reopened (:class:`telegram.ForumTopicReopened`, optional): Service message:
            forum topic reopened.

            .. versionadded:: 20.0
        forum_topic_edited (:class:`telegram.ForumTopicEdited`, optional): Service message:
            forum topic edited.

            .. versionadded:: 20.0
        general_forum_topic_hidden (:class:`telegram.GeneralForumTopicHidden`, optional):
            Service message: General forum topic hidden.

            .. versionadded:: 20.0
        general_forum_topic_unhidden (:class:`telegram.GeneralForumTopicUnhidden`, optional):
            Service message: General forum topic unhidden.

            .. versionadded:: 20.0
        write_access_allowed (:class:`telegram.WriteAccessAllowed`, optional): Service message:
            the user allowed the bot added to the attachment menu to write messages.

            .. versionadded:: 20.0
        has_media_spoiler (:obj:`bool`, optional): :obj:`True`, if the message media is covered
            by a spoiler animation.

            .. versionadded:: 20.0
        user_shared (:class:`telegram.UserShared`, optional): Service message: a user was shared
            with the bot.

            .. versionadded:: 20.1
        chat_shared (:class:`telegram.ChatShared`, optional):Service message: a chat was shared
            with the bot.

            .. versionadded:: 20.1

    Attributes:
        message_id (:obj:`int`): Unique message identifier inside this chat.
        from_user (:class:`telegram.User`): Optional. Sender of the message; empty for messages
            sent to channels. For backward compatibility, this will contain a fake sender user in
            non-channel chats, if the message was sent on behalf of a chat.
        sender_chat (:class:`telegram.Chat`): Optional. Sender of the message, sent on behalf of a
            chat. For example, the channel itself for channel posts, the supergroup itself for
            messages from anonymous group administrators, the linked channel for messages
            automatically forwarded to the discussion group. For backward compatibility,
            :attr:`from_user` contains a fake sender user in non-channel chats, if the message was
            sent on behalf of a chat.
        date (:class:`datetime.datetime`): Date the message was sent in Unix time. Converted to
            :class:`datetime.datetime`.

            .. versionchanged:: 20.3
                |datetime_localization|
        chat (:class:`telegram.Chat`): Conversation the message belongs to.
        forward_from (:class:`telegram.User`): Optional. For forwarded messages, sender of the
            original message.
        forward_from_chat (:class:`telegram.Chat`): Optional. For messages forwarded from channels
            or from anonymous administrators, information about the original sender chat.
        forward_from_message_id (:obj:`int`): Optional. For forwarded channel posts, identifier of
            the original message in the channel.
        forward_date (:class:`datetime.datetime`): Optional. For forwarded messages, date the
            original message was sent in Unix time. Converted to :class:`datetime.datetime`.

            .. versionchanged:: 20.3
                |datetime_localization|
        is_automatic_forward (:obj:`bool`): Optional. :obj:`True`, if the message is a channel
            post that was automatically forwarded to the connected discussion group.

            .. versionadded:: 13.9
        reply_to_message (:class:`telegram.Message`): Optional. For replies, the original message.
            Note that the Message object in this field will not contain further
            ``reply_to_message`` fields even if it itself is a reply.
        edit_date (:class:`datetime.datetime`): Optional. Date the message was last edited in Unix
            time. Converted to :class:`datetime.datetime`.

            .. versionchanged:: 20.3
                |datetime_localization|
        has_protected_content (:obj:`bool`): Optional. :obj:`True`, if the message can't be
            forwarded.

            .. versionadded:: 13.9
        media_group_id (:obj:`str`): Optional. The unique identifier of a media message group this
            message belongs to.
        text (:obj:`str`): Optional. For text messages, the actual UTF-8 text of the message,
            0-:tg-const:`telegram.constants.MessageLimit.MAX_TEXT_LENGTH` characters.
        entities (Tuple[:class:`telegram.MessageEntity`]): Optional. For text messages, special
            entities like usernames, URLs, bot commands, etc. that appear in the text. See
            :attr:`parse_entity` and :attr:`parse_entities` methods for how to use properly.
            This list is empty if the message does not contain entities.

            .. versionchanged:: 20.0
                |tupleclassattrs|

        caption_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. For messages with a
            Caption. Special entities like usernames, URLs, bot commands, etc. that appear in the
            caption. See :attr:`Message.parse_caption_entity` and :attr:`parse_caption_entities`
            methods for how to use properly. This list is empty if the message does not contain
            caption entities.

            .. versionchanged:: 20.0
                |tupleclassattrs|

        audio (:class:`telegram.Audio`): Optional. Message is an audio file, information
            about the file.

            .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`
        document (:class:`telegram.Document`): Optional. Message is a general file, information
            about the file.

            .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`
        animation (:class:`telegram.Animation`): Optional. Message is an animation, information
            about the animation. For backward compatibility, when this field is set, the document
            field will also be set.

            .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`
        game (:class:`telegram.Game`): Optional. Message is a game, information about the game.
        photo (Tuple[:class:`telegram.PhotoSize`]): Optional. Message is a photo, available
            sizes of the photo. This list is empty if the message does not contain a photo.

            .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

            .. versionchanged:: 20.0
                |tupleclassattrs|

        sticker (:class:`telegram.Sticker`): Optional. Message is a sticker, information
            about the sticker.

            .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`
        video (:class:`telegram.Video`): Optional. Message is a video, information about the
            video.

            .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`
        voice (:class:`telegram.Voice`): Optional. Message is a voice message, information about
            the file.

            .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`
        video_note (:class:`telegram.VideoNote`): Optional. Message is a video note, information
            about the video message.

            .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`
        new_chat_members (Tuple[:class:`telegram.User`]): Optional. New members that were added
            to the group or supergroup and information about them (the bot itself may be one of
            these members). This list is empty if the message does not contain new chat members.

            .. versionchanged:: 20.0
                |tupleclassattrs|
        caption (:obj:`str`): Optional. Caption for the animation, audio, document, photo, video
            or voice, 0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters.
        contact (:class:`telegram.Contact`): Optional. Message is a shared contact, information
            about the contact.
        location (:class:`telegram.Location`): Optional. Message is a shared location, information
            about the location.
        venue (:class:`telegram.Venue`): Optional. Message is a venue, information about the
            venue. For backward compatibility, when this field is set, the location field will
            also be set.
        left_chat_member (:class:`telegram.User`): Optional. A member was removed from the group,
            information about them (this member may be the bot itself).
        new_chat_title (:obj:`str`): Optional. A chat title was changed to this value.
        new_chat_photo (Tuple[:class:`telegram.PhotoSize`]): A chat photo was changed to
            this value. This list is empty if the message does not contain a new chat photo.

            .. versionchanged:: 20.0
                |tupleclassattrs|

        delete_chat_photo (:obj:`bool`): Optional. Service message: The chat photo was deleted.
        group_chat_created (:obj:`bool`): Optional. Service message: The group has been created.
        supergroup_chat_created (:obj:`bool`): Optional. Service message: The supergroup has been
            created. This field can't be received in a message coming through updates, because bot
            can't be a member of a supergroup when it is created. It can only be found in
            :attr:`reply_to_message` if someone replies to a very first message in a directly
            created supergroup.
        channel_chat_created (:obj:`bool`): Optional. Service message: The channel has been
            created. This field can't be received in a message coming through updates, because bot
            can't be a member of a channel when it is created. It can only be found in
            :attr:`reply_to_message` if someone replies to a very first message in a channel.
        message_auto_delete_timer_changed (:class:`telegram.MessageAutoDeleteTimerChanged`):
            Optional. Service message: auto-delete timer settings changed in the chat.

            .. versionadded:: 13.4
        migrate_to_chat_id (:obj:`int`): Optional. The group has been migrated to a supergroup
            with the specified identifier.
        migrate_from_chat_id (:obj:`int`): Optional. The supergroup has been migrated from a group
            with the specified identifier.
        pinned_message (:class:`telegram.Message`): Optional. Specified message was pinned. Note
            that the Message object in this field will not contain further
            :attr:`reply_to_message` fields even if it is itself a reply.
        invoice (:class:`telegram.Invoice`): Optional. Message is an invoice for a payment,
            information about the invoice.
        successful_payment (:class:`telegram.SuccessfulPayment`): Optional. Message is a service
            message about a successful payment, information about the payment.
        connected_website (:obj:`str`): Optional. The domain name of the website on which the user
            has logged in.
        forward_signature (:obj:`str`): Optional. For messages forwarded from channels, signature
            of the post author if present.
        author_signature (:obj:`str`): Optional. Signature of the post author for messages in
            channels, or the custom title of an anonymous group administrator.
        forward_sender_name (:obj:`str`): Optional. Sender's name for messages forwarded from
            users who disallow adding a link to their account in forwarded messages.
        passport_data (:class:`telegram.PassportData`): Optional. Telegram Passport data.

            Examples:
                :any:`Passport Bot <examples.passportbot>`
        poll (:class:`telegram.Poll`): Optional. Message is a native poll,
            information about the poll.
        dice (:class:`telegram.Dice`): Optional. Message is a dice with random value.
        via_bot (:class:`telegram.User`): Optional. Bot through which message was sent.
        proximity_alert_triggered (:class:`telegram.ProximityAlertTriggered`): Optional. Service
            message. A user in the chat triggered another user's proximity alert while sharing
            Live Location.
        video_chat_scheduled (:class:`telegram.VideoChatScheduled`): Optional. Service message:
            video chat scheduled.

            .. versionadded:: 20.0
        video_chat_started (:class:`telegram.VideoChatStarted`): Optional. Service message: video
            chat started.

            .. versionadded:: 20.0
        video_chat_ended (:class:`telegram.VideoChatEnded`): Optional. Service message: video chat
            ended.

            .. versionadded:: 20.0
        video_chat_participants_invited (:class:`telegram.VideoChatParticipantsInvited`): Optional.
            Service message: new participants invited to a video chat.

            .. versionadded:: 20.0
        web_app_data (:class:`telegram.WebAppData`): Optional. Service message: data sent by a Web
            App.

            .. versionadded:: 20.0
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message. :paramref:`~telegram.InlineKeyboardButton.login_url` buttons are
            represented as ordinary url buttons.
        is_topic_message (:obj:`bool`): Optional. :obj:`True`, if the message is sent to a forum
            topic.

            .. versionadded:: 20.0
        message_thread_id (:obj:`int`): Optional. Unique identifier of a message thread to which
            the message belongs; for supergroups only.

            .. versionadded:: 20.0
        forum_topic_created (:class:`telegram.ForumTopicCreated`): Optional. Service message:
            forum topic created.

            .. versionadded:: 20.0
        forum_topic_closed (:class:`telegram.ForumTopicClosed`): Optional. Service message:
            forum topic closed.

            .. versionadded:: 20.0
        forum_topic_reopened (:class:`telegram.ForumTopicReopened`): Optional. Service message:
            forum topic reopened.

            .. versionadded:: 20.0
        forum_topic_edited (:class:`telegram.ForumTopicEdited`): Optional. Service message:
            forum topic edited.

            .. versionadded:: 20.0
        general_forum_topic_hidden (:class:`telegram.GeneralForumTopicHidden`): Optional.
            Service message: General forum topic hidden.

            .. versionadded:: 20.0
        general_forum_topic_unhidden (:class:`telegram.GeneralForumTopicUnhidden`): Optional.
            Service message: General forum topic unhidden.

            .. versionadded:: 20.0
        write_access_allowed (:class:`telegram.WriteAccessAllowed`): Optional. Service message:
            the user allowed the bot added to the attachment menu to write messages.

            .. versionadded:: 20.0
        has_media_spoiler (:obj:`bool`): Optional. :obj:`True`, if the message media is covered
            by a spoiler animation.

            .. versionadded:: 20.0
        user_shared (:class:`telegram.UserShared`): Optional. Service message: a user was shared
            with the bot.

            .. versionadded:: 20.1
        chat_shared (:class:`telegram.ChatShared`): Optional. Service message: a chat was shared
            with the bot.

            .. versionadded:: 20.1

    .. |custom_emoji_formatting_note| replace:: Custom emoji entities will be ignored by this
        function. Instead, the supplied replacement for the emoji will be used.

    .. |custom_emoji_md1_deprecation| replace:: Since custom emoji entities are not supported by
       :attr:`~telegram.constants.ParseMode.MARKDOWN`, this method will raise a
       :exc:`ValueError` in future versions instead of falling back to the supplied replacement
       for the emoji.
    """

    # fmt: on
    __slots__ = (
        "reply_markup",
        "audio",
        "contact",
        "migrate_to_chat_id",
        "forward_signature",
        "chat",
        "successful_payment",
        "game",
        "text",
        "forward_sender_name",
        "document",
        "new_chat_title",
        "forward_date",
        "group_chat_created",
        "media_group_id",
        "caption",
        "video",
        "entities",
        "via_bot",
        "new_chat_members",
        "connected_website",
        "animation",
        "migrate_from_chat_id",
        "forward_from",
        "sticker",
        "location",
        "venue",
        "edit_date",
        "reply_to_message",
        "passport_data",
        "pinned_message",
        "forward_from_chat",
        "new_chat_photo",
        "message_id",
        "delete_chat_photo",
        "from_user",
        "author_signature",
        "proximity_alert_triggered",
        "sender_chat",
        "dice",
        "forward_from_message_id",
        "caption_entities",
        "voice",
        "date",
        "supergroup_chat_created",
        "poll",
        "left_chat_member",
        "photo",
        "channel_chat_created",
        "invoice",
        "video_note",
        "_effective_attachment",
        "message_auto_delete_timer_changed",
        "video_chat_ended",
        "video_chat_participants_invited",
        "video_chat_started",
        "video_chat_scheduled",
        "is_automatic_forward",
        "has_protected_content",
        "web_app_data",
        "is_topic_message",
        "message_thread_id",
        "forum_topic_created",
        "forum_topic_closed",
        "forum_topic_reopened",
        "forum_topic_edited",
        "general_forum_topic_hidden",
        "general_forum_topic_unhidden",
        "write_access_allowed",
        "has_media_spoiler",
        "user_shared",
        "chat_shared",
    )

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
        reply_to_message: "Message" = None,
        edit_date: datetime.datetime = None,
        text: str = None,
        entities: Sequence["MessageEntity"] = None,
        caption_entities: Sequence["MessageEntity"] = None,
        audio: Audio = None,
        document: Document = None,
        game: Game = None,
        photo: Sequence[PhotoSize] = None,
        sticker: Sticker = None,
        video: Video = None,
        voice: Voice = None,
        video_note: VideoNote = None,
        new_chat_members: Sequence[User] = None,
        caption: str = None,
        contact: Contact = None,
        location: Location = None,
        venue: Venue = None,
        left_chat_member: User = None,
        new_chat_title: str = None,
        new_chat_photo: Sequence[PhotoSize] = None,
        delete_chat_photo: bool = None,
        group_chat_created: bool = None,
        supergroup_chat_created: bool = None,
        channel_chat_created: bool = None,
        migrate_to_chat_id: int = None,
        migrate_from_chat_id: int = None,
        pinned_message: "Message" = None,
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
        dice: Dice = None,
        via_bot: User = None,
        proximity_alert_triggered: ProximityAlertTriggered = None,
        sender_chat: Chat = None,
        video_chat_started: VideoChatStarted = None,
        video_chat_ended: VideoChatEnded = None,
        video_chat_participants_invited: VideoChatParticipantsInvited = None,
        message_auto_delete_timer_changed: MessageAutoDeleteTimerChanged = None,
        video_chat_scheduled: VideoChatScheduled = None,
        is_automatic_forward: bool = None,
        has_protected_content: bool = None,
        web_app_data: WebAppData = None,
        is_topic_message: bool = None,
        message_thread_id: int = None,
        forum_topic_created: ForumTopicCreated = None,
        forum_topic_closed: ForumTopicClosed = None,
        forum_topic_reopened: ForumTopicReopened = None,
        forum_topic_edited: ForumTopicEdited = None,
        general_forum_topic_hidden: GeneralForumTopicHidden = None,
        general_forum_topic_unhidden: GeneralForumTopicUnhidden = None,
        write_access_allowed: WriteAccessAllowed = None,
        has_media_spoiler: bool = None,
        user_shared: UserShared = None,
        chat_shared: ChatShared = None,
        *,
        api_kwargs: JSONDict = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        # Required
        self.message_id: int = message_id
        # Optionals
        self.from_user: Optional[User] = from_user
        self.sender_chat: Optional[Chat] = sender_chat
        self.date: datetime.datetime = date
        self.chat: Chat = chat
        self.forward_from: Optional[User] = forward_from
        self.forward_from_chat: Optional[Chat] = forward_from_chat
        self.forward_date: Optional[datetime.datetime] = forward_date
        self.is_automatic_forward: Optional[bool] = is_automatic_forward
        self.reply_to_message: Optional[Message] = reply_to_message
        self.edit_date: Optional[datetime.datetime] = edit_date
        self.has_protected_content: Optional[bool] = has_protected_content
        self.text: Optional[str] = text
        self.entities: Tuple["MessageEntity", ...] = parse_sequence_arg(entities)
        self.caption_entities: Tuple["MessageEntity", ...] = parse_sequence_arg(caption_entities)
        self.audio: Optional[Audio] = audio
        self.game: Optional[Game] = game
        self.document: Optional[Document] = document
        self.photo: Tuple[PhotoSize, ...] = parse_sequence_arg(photo)
        self.sticker: Optional[Sticker] = sticker
        self.video: Optional[Video] = video
        self.voice: Optional[Voice] = voice
        self.video_note: Optional[VideoNote] = video_note
        self.caption: Optional[str] = caption
        self.contact: Optional[Contact] = contact
        self.location: Optional[Location] = location
        self.venue: Optional[Venue] = venue
        self.new_chat_members: Tuple[User, ...] = parse_sequence_arg(new_chat_members)
        self.left_chat_member: Optional[User] = left_chat_member
        self.new_chat_title: Optional[str] = new_chat_title
        self.new_chat_photo: Tuple[PhotoSize, ...] = parse_sequence_arg(new_chat_photo)
        self.delete_chat_photo: Optional[bool] = bool(delete_chat_photo)
        self.group_chat_created: Optional[bool] = bool(group_chat_created)
        self.supergroup_chat_created: Optional[bool] = bool(supergroup_chat_created)
        self.migrate_to_chat_id: Optional[int] = migrate_to_chat_id
        self.migrate_from_chat_id: Optional[int] = migrate_from_chat_id
        self.channel_chat_created: Optional[bool] = bool(channel_chat_created)
        self.message_auto_delete_timer_changed: Optional[
            MessageAutoDeleteTimerChanged
        ] = message_auto_delete_timer_changed
        self.pinned_message: Optional[Message] = pinned_message
        self.forward_from_message_id: Optional[int] = forward_from_message_id
        self.invoice: Optional[Invoice] = invoice
        self.successful_payment: Optional[SuccessfulPayment] = successful_payment
        self.connected_website: Optional[str] = connected_website
        self.forward_signature: Optional[str] = forward_signature
        self.forward_sender_name: Optional[str] = forward_sender_name
        self.author_signature: Optional[str] = author_signature
        self.media_group_id: Optional[str] = media_group_id
        self.animation: Optional[Animation] = animation
        self.passport_data: Optional[PassportData] = passport_data
        self.poll: Optional[Poll] = poll
        self.dice: Optional[Dice] = dice
        self.via_bot: Optional[User] = via_bot
        self.proximity_alert_triggered: Optional[
            ProximityAlertTriggered
        ] = proximity_alert_triggered
        self.video_chat_scheduled: Optional[VideoChatScheduled] = video_chat_scheduled
        self.video_chat_started: Optional[VideoChatStarted] = video_chat_started
        self.video_chat_ended: Optional[VideoChatEnded] = video_chat_ended
        self.video_chat_participants_invited: Optional[
            VideoChatParticipantsInvited
        ] = video_chat_participants_invited
        self.reply_markup: Optional[InlineKeyboardMarkup] = reply_markup
        self.web_app_data: Optional[WebAppData] = web_app_data
        self.is_topic_message: Optional[bool] = is_topic_message
        self.message_thread_id: Optional[int] = message_thread_id
        self.forum_topic_created: Optional[ForumTopicCreated] = forum_topic_created
        self.forum_topic_closed: Optional[ForumTopicClosed] = forum_topic_closed
        self.forum_topic_reopened: Optional[ForumTopicReopened] = forum_topic_reopened
        self.forum_topic_edited: Optional[ForumTopicEdited] = forum_topic_edited
        self.general_forum_topic_hidden: Optional[
            GeneralForumTopicHidden
        ] = general_forum_topic_hidden
        self.general_forum_topic_unhidden: Optional[
            GeneralForumTopicUnhidden
        ] = general_forum_topic_unhidden
        self.write_access_allowed: Optional[WriteAccessAllowed] = write_access_allowed
        self.has_media_spoiler: Optional[bool] = has_media_spoiler
        self.user_shared: Optional[UserShared] = user_shared
        self.chat_shared: Optional[ChatShared] = chat_shared

        self._effective_attachment = DEFAULT_NONE

        self._id_attrs = (self.message_id, self.chat)

        self._freeze()

    @property
    def chat_id(self) -> int:
        """:obj:`int`: Shortcut for :attr:`telegram.Chat.id` for :attr:`chat`."""
        return self.chat.id

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """
        :obj:`int`: Shortcut for :attr:`message_id`.

            .. versionadded:: 20.0
        """
        return self.message_id

    @property
    def link(self) -> Optional[str]:
        """:obj:`str`: Convenience property. If the chat of the message is not
        a private chat or normal group, returns a t.me link of the message.

            .. versionchanged:: 20.3
                For messages that are replies or part of a forum topic, the link now points
                to the corresponding thread view.
        """
        if self.chat.type not in [Chat.PRIVATE, Chat.GROUP]:
            # the else block gets rid of leading -100 for supergroups:
            to_link = self.chat.username if self.chat.username else f"c/{str(self.chat.id)[4:]}"
            baselink = f"https://t.me/{to_link}/{self.message_id}"

            # adds the thread for topics and replies
            if (self.is_topic_message and self.message_thread_id) or self.reply_to_message:
                baselink = f"{baselink}?thread={self.message_thread_id}"
            return baselink
        return None

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["Message"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)

        data["from_user"] = User.de_json(data.pop("from", None), bot)
        data["sender_chat"] = Chat.de_json(data.get("sender_chat"), bot)
        data["date"] = from_timestamp(data["date"], tzinfo=loc_tzinfo)
        data["chat"] = Chat.de_json(data.get("chat"), bot)
        data["entities"] = MessageEntity.de_list(data.get("entities"), bot)
        data["caption_entities"] = MessageEntity.de_list(data.get("caption_entities"), bot)
        data["forward_from"] = User.de_json(data.get("forward_from"), bot)
        data["forward_from_chat"] = Chat.de_json(data.get("forward_from_chat"), bot)
        data["forward_date"] = from_timestamp(data.get("forward_date"), tzinfo=loc_tzinfo)
        data["reply_to_message"] = Message.de_json(data.get("reply_to_message"), bot)
        data["edit_date"] = from_timestamp(data.get("edit_date"), tzinfo=loc_tzinfo)
        data["audio"] = Audio.de_json(data.get("audio"), bot)
        data["document"] = Document.de_json(data.get("document"), bot)
        data["animation"] = Animation.de_json(data.get("animation"), bot)
        data["game"] = Game.de_json(data.get("game"), bot)
        data["photo"] = PhotoSize.de_list(data.get("photo"), bot)
        data["sticker"] = Sticker.de_json(data.get("sticker"), bot)
        data["video"] = Video.de_json(data.get("video"), bot)
        data["voice"] = Voice.de_json(data.get("voice"), bot)
        data["video_note"] = VideoNote.de_json(data.get("video_note"), bot)
        data["contact"] = Contact.de_json(data.get("contact"), bot)
        data["location"] = Location.de_json(data.get("location"), bot)
        data["venue"] = Venue.de_json(data.get("venue"), bot)
        data["new_chat_members"] = User.de_list(data.get("new_chat_members"), bot)
        data["left_chat_member"] = User.de_json(data.get("left_chat_member"), bot)
        data["new_chat_photo"] = PhotoSize.de_list(data.get("new_chat_photo"), bot)
        data["message_auto_delete_timer_changed"] = MessageAutoDeleteTimerChanged.de_json(
            data.get("message_auto_delete_timer_changed"), bot
        )
        data["pinned_message"] = Message.de_json(data.get("pinned_message"), bot)
        data["invoice"] = Invoice.de_json(data.get("invoice"), bot)
        data["successful_payment"] = SuccessfulPayment.de_json(data.get("successful_payment"), bot)
        data["passport_data"] = PassportData.de_json(data.get("passport_data"), bot)
        data["poll"] = Poll.de_json(data.get("poll"), bot)
        data["dice"] = Dice.de_json(data.get("dice"), bot)
        data["via_bot"] = User.de_json(data.get("via_bot"), bot)
        data["proximity_alert_triggered"] = ProximityAlertTriggered.de_json(
            data.get("proximity_alert_triggered"), bot
        )
        data["reply_markup"] = InlineKeyboardMarkup.de_json(data.get("reply_markup"), bot)
        data["video_chat_scheduled"] = VideoChatScheduled.de_json(
            data.get("video_chat_scheduled"), bot
        )
        data["video_chat_started"] = VideoChatStarted.de_json(data.get("video_chat_started"), bot)
        data["video_chat_ended"] = VideoChatEnded.de_json(data.get("video_chat_ended"), bot)
        data["video_chat_participants_invited"] = VideoChatParticipantsInvited.de_json(
            data.get("video_chat_participants_invited"), bot
        )
        data["web_app_data"] = WebAppData.de_json(data.get("web_app_data"), bot)
        data["forum_topic_closed"] = ForumTopicClosed.de_json(data.get("forum_topic_closed"), bot)
        data["forum_topic_created"] = ForumTopicCreated.de_json(
            data.get("forum_topic_created"), bot
        )
        data["forum_topic_reopened"] = ForumTopicReopened.de_json(
            data.get("forum_topic_reopened"), bot
        )
        data["forum_topic_edited"] = ForumTopicEdited.de_json(data.get("forum_topic_edited"), bot)
        data["general_forum_topic_hidden"] = GeneralForumTopicHidden.de_json(
            data.get("general_forum_topic_hidden"), bot
        )
        data["general_forum_topic_unhidden"] = GeneralForumTopicUnhidden.de_json(
            data.get("general_forum_topic_unhidden"), bot
        )
        data["write_access_allowed"] = WriteAccessAllowed.de_json(
            data.get("write_access_allowed"), bot
        )
        data["user_shared"] = UserShared.de_json(data.get("user_shared"), bot)
        data["chat_shared"] = ChatShared.de_json(data.get("chat_shared"), bot)

        return super().de_json(data=data, bot=bot)

    @property
    def effective_attachment(
        self,
    ) -> Union[
        Animation,
        Audio,
        Contact,
        Dice,
        Document,
        Game,
        Invoice,
        Location,
        PassportData,
        Sequence[PhotoSize],
        Poll,
        Sticker,
        SuccessfulPayment,
        Venue,
        Video,
        VideoNote,
        Voice,
        None,
    ]:
        """If this message is neither a plain text message nor a status update, this gives the
        attachment that this message was sent with. This may be one of

        * :class:`telegram.Audio`
        * :class:`telegram.Dice`
        * :class:`telegram.Contact`
        * :class:`telegram.Document`
        * :class:`telegram.Animation`
        * :class:`telegram.Game`
        * :class:`telegram.Invoice`
        * :class:`telegram.Location`
        * :class:`telegram.PassportData`
        * List[:class:`telegram.PhotoSize`]
        * :class:`telegram.Poll`
        * :class:`telegram.Sticker`
        * :class:`telegram.SuccessfulPayment`
        * :class:`telegram.Venue`
        * :class:`telegram.Video`
        * :class:`telegram.VideoNote`
        * :class:`telegram.Voice`

        Otherwise :obj:`None` is returned.

        .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

        .. versionchanged:: 20.0
            :attr:`dice`, :attr:`passport_data` and :attr:`poll` are now also considered to be an
            attachment.

        """
        if not isinstance(self._effective_attachment, DefaultValue):
            return self._effective_attachment

        for attachment_type in MessageAttachmentType:
            if self[attachment_type]:
                self._effective_attachment = self[attachment_type]  # type: ignore[assignment]
                break
        else:
            self._effective_attachment = None

        return self._effective_attachment  # type: ignore[return-value]

    def _quote(self, quote: Optional[bool], reply_to_message_id: Optional[int]) -> Optional[int]:
        """Modify kwargs for replying with or without quoting."""
        if reply_to_message_id is not None:
            return reply_to_message_id

        if quote is not None:
            if quote:
                return self.message_id

        else:
            # Unfortunately we need some ExtBot logic here because it's hard to move shortcut
            # logic into ExtBot
            if hasattr(self.get_bot(), "defaults") and self.get_bot().defaults:  # type: ignore
                default_quote = self.get_bot().defaults.quote  # type: ignore[attr-defined]
            else:
                default_quote = None
            if (default_quote is None and self.chat.type != Chat.PRIVATE) or default_quote:
                return self.message_id

        return None

    async def reply_text(
        self,
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_message(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the message is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def reply_markdown(
        self,
        text: str,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

            await bot.send_message(
                update.effective_message.chat_id,
                parse_mode=ParseMode.MARKDOWN,
                *args,
                **kwargs,
            )

        Sends a message with Markdown version 1 formatting.

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Note:
            :tg-const:`telegram.constants.ParseMode.MARKDOWN` is a legacy mode, retained by
            Telegram for backward compatibility. You should use :meth:`reply_markdown_v2` instead.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the message is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.
        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def reply_markdown_v2(
        self,
        text: str,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

            await bot.send_message(
                update.effective_message.chat_id,
                parse_mode=ParseMode.MARKDOWN_V2,
                *args,
                **kwargs,
            )

        Sends a message with markdown version 2 formatting.

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the message is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.
        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def reply_html(
        self,
        text: str,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

            await bot.send_message(
                update.effective_message.chat_id,
                parse_mode=ParseMode.HTML,
                *args,
                **kwargs,
            )

        Sends a message with HTML formatting.

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the message is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.
        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def reply_media_group(
        self,
        media: Sequence[
            Union["InputMediaAudio", "InputMediaDocument", "InputMediaPhoto", "InputMediaVideo"]
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
    ) -> Tuple["Message", ...]:
        """Shortcut for::

             await bot.send_media_group(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_media_group`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the media group is sent as an
                actual reply to this message. If ``reply_to_message_id`` is passed, this parameter
                will be ignored. Default: :obj:`True` in group chats and :obj:`False` in private
                chats.

        Returns:
            Tuple[:class:`telegram.Message`]: An array of the sent Messages.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_media_group(
            chat_id=self.chat_id,
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )

    async def reply_photo(
        self,
        photo: Union[FileInput, "PhotoSize"],
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        has_spoiler: bool = None,
        *,
        filename: str = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_photo(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_photo`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the photo is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_photo(
            chat_id=self.chat_id,
            photo=photo,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            has_spoiler=has_spoiler,
        )

    async def reply_audio(
        self,
        audio: Union[FileInput, "Audio"],
        duration: int = None,
        performer: str = None,
        title: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        thumbnail: FileInput = None,
        *,
        filename: str = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_audio(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_audio`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the audio is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_audio(
            chat_id=self.chat_id,
            audio=audio,
            duration=duration,
            performer=performer,
            title=title,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            thumb=thumb,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            thumbnail=thumbnail,
        )

    async def reply_document(
        self,
        document: Union[FileInput, "Document"],
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        disable_content_type_detection: bool = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        thumbnail: FileInput = None,
        *,
        filename: str = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_document(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_document`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the document is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_document(
            chat_id=self.chat_id,
            document=document,
            filename=filename,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            parse_mode=parse_mode,
            thumb=thumb,
            api_kwargs=api_kwargs,
            disable_content_type_detection=disable_content_type_detection,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            thumbnail=thumbnail,
        )

    async def reply_animation(
        self,
        animation: Union[FileInput, "Animation"],
        duration: int = None,
        width: int = None,
        height: int = None,
        thumb: FileInput = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        has_spoiler: bool = None,
        thumbnail: FileInput = None,
        *,
        filename: str = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_animation(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_animation`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the animation is sent as an
                actual reply to this message. If ``reply_to_message_id`` is passed, this parameter
                will be ignored. Default: :obj:`True` in group chats and :obj:`False` in private
                chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_animation(
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
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            has_spoiler=has_spoiler,
            thumbnail=thumbnail,
        )

    async def reply_sticker(
        self,
        sticker: Union[FileInput, "Sticker"],
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        emoji: str = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_sticker(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_sticker`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the sticker is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_sticker(
            chat_id=self.chat_id,
            sticker=sticker,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            emoji=emoji,
        )

    async def reply_video(
        self,
        video: Union[FileInput, "Video"],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        width: int = None,
        height: int = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        supports_streaming: bool = None,
        thumb: FileInput = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        has_spoiler: bool = None,
        thumbnail: FileInput = None,
        *,
        filename: str = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_video(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the video is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_video(
            chat_id=self.chat_id,
            video=video,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            width=width,
            height=height,
            parse_mode=parse_mode,
            supports_streaming=supports_streaming,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            has_spoiler=has_spoiler,
            thumbnail=thumbnail,
        )

    async def reply_video_note(
        self,
        video_note: Union[FileInput, "VideoNote"],
        duration: int = None,
        length: int = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        thumb: FileInput = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        thumbnail: FileInput = None,
        *,
        filename: str = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_video_note(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video_note`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the video note is sent as an
                actual reply to this message. If ``reply_to_message_id`` is passed, this parameter
                will be ignored. Default: :obj:`True` in group chats and :obj:`False` in private
                chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_video_note(
            chat_id=self.chat_id,
            video_note=video_note,
            duration=duration,
            length=length,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            thumbnail=thumbnail,
        )

    async def reply_voice(
        self,
        voice: Union[FileInput, "Voice"],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        filename: str = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_voice(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_voice`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the voice note is sent as an
                actual reply to this message. If ``reply_to_message_id`` is passed, this parameter
                will be ignored. Default: :obj:`True` in group chats and :obj:`False` in private
                chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_voice(
            chat_id=self.chat_id,
            voice=voice,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def reply_location(
        self,
        latitude: float = None,
        longitude: float = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        live_period: int = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        location: Location = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_location(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_location`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the location is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_location(
            chat_id=self.chat_id,
            latitude=latitude,
            longitude=longitude,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            location=location,
            live_period=live_period,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def reply_venue(
        self,
        latitude: float = None,
        longitude: float = None,
        title: str = None,
        address: str = None,
        foursquare_id: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        foursquare_type: str = None,
        google_place_id: str = None,
        google_place_type: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        venue: Venue = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_venue(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_venue`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the venue is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_venue(
            chat_id=self.chat_id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            venue=venue,
            foursquare_type=foursquare_type,
            api_kwargs=api_kwargs,
            google_place_id=google_place_id,
            google_place_type=google_place_type,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def reply_contact(
        self,
        phone_number: str = None,
        first_name: str = None,
        last_name: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        vcard: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        contact: Contact = None,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_contact(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_contact`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the contact is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_contact(
            chat_id=self.chat_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            contact=contact,
            vcard=vcard,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def reply_poll(
        self,
        question: str,
        options: Sequence[str],
        is_anonymous: bool = None,
        type: str = None,  # pylint: disable=redefined-builtin
        allows_multiple_answers: bool = None,
        correct_option_id: int = None,
        is_closed: bool = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        explanation: str = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        open_period: int = None,
        close_date: Union[int, datetime.datetime] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        explanation_entities: Sequence["MessageEntity"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_poll(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_poll`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the poll is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_poll(
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
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            open_period=open_period,
            close_date=close_date,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            explanation_entities=explanation_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def reply_dice(
        self,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        emoji: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_dice(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_dice`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the dice is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_dice(
            chat_id=self.chat_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            emoji=emoji,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def reply_chat_action(
        self,
        action: str,
        message_thread_id: int = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             await bot.send_chat_action(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_chat_action`.

        .. versionadded:: 13.2

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().send_chat_action(
            chat_id=self.chat_id,
            message_thread_id=message_thread_id,
            action=action,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def reply_game(
        self,
        game_short_name: str,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: "InlineKeyboardMarkup" = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_game(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_game`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the game is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        .. versionadded:: 13.2

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_game(
            chat_id=self.chat_id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def reply_invoice(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: Sequence["LabeledPrice"],
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
        reply_markup: "InlineKeyboardMarkup" = None,
        provider_data: Union[str, object] = None,
        send_phone_number_to_provider: bool = None,
        send_email_to_provider: bool = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        max_tip_amount: int = None,
        suggested_tip_amounts: Sequence[int] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_invoice(update.effective_message.chat_id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_invoice`.

        Warning:
            As of API 5.2 :paramref:`start_parameter <telegram.Bot.send_invoice.start_parameter>`
            is an optional argument and therefore the
            order of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        .. versionadded:: 13.2

        .. versionchanged:: 13.5
            As of Bot API 5.2, the parameter
            :paramref:`start_parameter <telegram.Bot.send_invoice.start_parameter>` is optional.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the invoice is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().send_invoice(
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
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def forward(
        self,
        chat_id: Union[int, str],
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "Message":
        """Shortcut for::

             await bot.forward_message(
                 from_chat_id=update.effective_message.chat_id,
                 message_id=update.effective_message.message_id,
                 *args,
                 **kwargs
             )

        For the documentation of the arguments, please see :meth:`telegram.Bot.forward_message`.

        Note:
            Since the release of Bot API 5.5 it can be impossible to forward messages from
            some chats. Use the attributes :attr:`telegram.Message.has_protected_content` and
            :attr:`telegram.Chat.has_protected_content` to check this.

            As a workaround, it is still possible to use :meth:`copy`. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message forwarded.

        """
        return await self.get_bot().forward_message(
            chat_id=chat_id,
            from_chat_id=self.chat_id,
            message_id=self.message_id,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def copy(
        self,
        chat_id: Union[int, str],
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: ReplyMarkup = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "MessageId":
        """Shortcut for::

             await bot.copy_message(
                 chat_id=chat_id,
                 from_chat_id=update.effective_message.chat_id,
                 message_id=update.effective_message.message_id,
                 *args,
                 **kwargs
             )

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Returns:
            :class:`telegram.MessageId`: On success, returns the MessageId of the sent message.

        """
        return await self.get_bot().copy_message(
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
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def reply_copy(
        self,
        from_chat_id: Union[str, int],
        message_id: int,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: ReplyMarkup = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: int = None,
        *,
        quote: bool = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> "MessageId":
        """Shortcut for::

             await bot.copy_message(
                 chat_id=message.chat.id,
                 message_id=message_id,
                 *args,
                 **kwargs
             )

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Keyword Args:
            quote (:obj:`bool`, optional): If set to :obj:`True`, the copy is sent as an actual
                reply to this message. If ``reply_to_message_id`` is passed, this parameter will be
                ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.

                .. versionadded:: 13.1

        Returns:
            :class:`telegram.MessageId`: On success, returns the MessageId of the sent message.

        """
        reply_to_message_id = self._quote(quote, reply_to_message_id)
        return await self.get_bot().copy_message(
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
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def edit_text(
        self,
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: InlineKeyboardMarkup = None,
        entities: Sequence["MessageEntity"] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union["Message", bool]:
        """Shortcut for::

             await bot.edit_message_text(
                 chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
             )

        For the documentation of the arguments, please see :meth:`telegram.Bot.edit_message_text`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.

        """
        return await self.get_bot().edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            entities=entities,
            inline_message_id=None,
        )

    async def edit_caption(
        self,
        caption: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Sequence["MessageEntity"] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union["Message", bool]:
        """Shortcut for::

             await bot.edit_message_caption(
                 chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
             )

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
        return await self.get_bot().edit_message_caption(
            chat_id=self.chat_id,
            message_id=self.message_id,
            caption=caption,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            caption_entities=caption_entities,
            inline_message_id=None,
        )

    async def edit_media(
        self,
        media: "InputMedia",
        reply_markup: InlineKeyboardMarkup = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union["Message", bool]:
        """Shortcut for::

             await bot.edit_message_media(
                 chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_media`.

        Note:
            You can only edit messages that the bot sent itself(i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited Message is returned, otherwise ``True`` is returned.

        """
        return await self.get_bot().edit_message_media(
            media=media,
            chat_id=self.chat_id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    async def edit_reply_markup(
        self,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union["Message", bool]:
        """Shortcut for::

             await bot.edit_message_reply_markup(
                 chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
             )

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
        return await self.get_bot().edit_message_reply_markup(
            chat_id=self.chat_id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    async def edit_live_location(
        self,
        latitude: float = None,
        longitude: float = None,
        reply_markup: InlineKeyboardMarkup = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        *,
        location: Location = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union["Message", bool]:
        """Shortcut for::

             await bot.edit_message_live_location(
                 chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
             )

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
        return await self.get_bot().edit_message_live_location(
            chat_id=self.chat_id,
            message_id=self.message_id,
            latitude=latitude,
            longitude=longitude,
            location=location,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            inline_message_id=None,
        )

    async def stop_live_location(
        self,
        reply_markup: InlineKeyboardMarkup = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union["Message", bool]:
        """Shortcut for::

             await bot.stop_message_live_location(
                 chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
             )

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
        return await self.get_bot().stop_message_live_location(
            chat_id=self.chat_id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    async def set_game_score(
        self,
        user_id: Union[int, str],
        score: int,
        force: bool = None,
        disable_edit_message: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union["Message", bool]:
        """Shortcut for::

             await bot.set_game_score(
                 chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
             )

        For the documentation of the arguments, please see :meth:`telegram.Bot.set_game_score`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.
        """
        return await self.get_bot().set_game_score(
            chat_id=self.chat_id,
            message_id=self.message_id,
            user_id=user_id,
            score=score,
            force=force,
            disable_edit_message=disable_edit_message,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    async def get_game_high_scores(
        self,
        user_id: Union[int, str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Tuple["GameHighScore", ...]:
        """Shortcut for::

             await bot.get_game_high_scores(
                 chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_game_high_scores`.

        Note:
            You can only edit messages that the bot sent itself (i.e. of the ``bot.send_*`` family
            of methods) or channel posts, if the bot is an admin in that channel. However, this
            behaviour is undocumented and might be changed by Telegram.

        Returns:
            Tuple[:class:`telegram.GameHighScore`]
        """
        return await self.get_bot().get_game_high_scores(
            chat_id=self.chat_id,
            message_id=self.message_id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            inline_message_id=None,
        )

    async def delete(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

              await bot.delete_message(
                  chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
              )

        For the documentation of the arguments, please see :meth:`telegram.Bot.delete_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().delete_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def stop_poll(
        self,
        reply_markup: InlineKeyboardMarkup = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Poll:
        """Shortcut for::

              await bot.stop_poll(
                  chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
              )

        For the documentation of the arguments, please see :meth:`telegram.Bot.stop_poll`.

        Returns:
            :class:`telegram.Poll`: On success, the stopped Poll with the final results is
            returned.

        """
        return await self.get_bot().stop_poll(
            chat_id=self.chat_id,
            message_id=self.message_id,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def pin(
        self,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

              await bot.pin_chat_message(
                  chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
              )

        For the documentation of the arguments, please see :meth:`telegram.Bot.pin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().pin_chat_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            disable_notification=disable_notification,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unpin(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

              await bot.unpin_chat_message(
                  chat_id=message.chat_id, message_id=message.message_id, *args, **kwargs
              )

        For the documentation of the arguments, please see :meth:`telegram.Bot.unpin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().unpin_chat_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def edit_forum_topic(
        self,
        name: str = None,
        icon_custom_emoji_id: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             await bot.edit_forum_topic(
                chat_id=message.chat_id, message_thread_id=message.message_thread_id, *args,
                **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().edit_forum_topic(
            chat_id=self.chat_id,
            message_thread_id=self.message_thread_id,
            name=name,
            icon_custom_emoji_id=icon_custom_emoji_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def close_forum_topic(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             await bot.close_forum_topic(
                chat_id=message.chat_id, message_thread_id=message.message_thread_id, *args,
                **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.close_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().close_forum_topic(
            chat_id=self.chat_id,
            message_thread_id=self.message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def reopen_forum_topic(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            await bot.reopen_forum_topic(
                chat_id=message.chat_id, message_thread_id=message.message_thread_id, *args,
                **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.reopen_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().reopen_forum_topic(
            chat_id=self.chat_id,
            message_thread_id=self.message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def delete_forum_topic(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             await bot.delete_forum_topic(
                chat_id=message.chat_id, message_thread_id=message.message_thread_id, *args,
                **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.delete_forum_topic`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().delete_forum_topic(
            chat_id=self.chat_id,
            message_thread_id=self.message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def unpin_all_forum_topic_messages(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             await bot.unpin_all_forum_topic_messages(
                chat_id=message.chat_id, message_thread_id=message.message_thread_id, *args,
                **kwargs
             )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_all_forum_topic_messages`.

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().unpin_all_forum_topic_messages(
            chat_id=self.chat_id,
            message_thread_id=self.message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
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

        entity_text = self.text.encode("utf-16-le")
        entity_text = entity_text[entity.offset * 2 : (entity.offset + entity.length) * 2]
        return entity_text.decode("utf-16-le")

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

        entity_text = self.caption.encode("utf-16-le")
        entity_text = entity_text[entity.offset * 2 : (entity.offset + entity.length) * 2]
        return entity_text.decode("utf-16-le")

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
            entity: self.parse_entity(entity) for entity in self.entities if entity.type in types
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
            for entity in self.caption_entities
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

        message_text = message_text.encode("utf-16-le")  # type: ignore

        html_text = ""
        last_offset = 0

        sorted_entities = sorted(entities.items(), key=lambda item: item[0].offset)
        parsed_entities = []

        for entity, text in sorted_entities:
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
                escaped_text = escape(text)

                if nested_entities:
                    escaped_text = Message._parse_html(
                        orig_text, nested_entities, urled=urled, offset=entity.offset
                    )

                if entity.type == MessageEntity.TEXT_LINK:
                    insert = f'<a href="{entity.url}">{escaped_text}</a>'
                elif entity.type == MessageEntity.TEXT_MENTION and entity.user:
                    insert = f'<a href="tg://user?id={entity.user.id}">{escaped_text}</a>'
                elif entity.type == MessageEntity.URL and urled:
                    insert = f'<a href="{escaped_text}">{escaped_text}</a>'
                elif entity.type == MessageEntity.BOLD:
                    insert = f"<b>{escaped_text}</b>"
                elif entity.type == MessageEntity.ITALIC:
                    insert = f"<i>{escaped_text}</i>"
                elif entity.type == MessageEntity.CODE:
                    insert = f"<code>{escaped_text}</code>"
                elif entity.type == MessageEntity.PRE:
                    if entity.language:
                        insert = (
                            f'<pre><code class="{entity.language}">{escaped_text}</code></pre>'
                        )
                    else:
                        insert = f"<pre>{escaped_text}</pre>"
                elif entity.type == MessageEntity.UNDERLINE:
                    insert = f"<u>{escaped_text}</u>"
                elif entity.type == MessageEntity.STRIKETHROUGH:
                    insert = f"<s>{escaped_text}</s>"
                elif entity.type == MessageEntity.SPOILER:
                    insert = f'<span class="tg-spoiler">{escaped_text}</span>'
                elif entity.type == MessageEntity.CUSTOM_EMOJI:
                    insert = (
                        f'<tg-emoji emoji-id="{entity.custom_emoji_id}">{escaped_text}</tg-emoji>'
                    )
                else:
                    insert = escaped_text

                if offset == 0:
                    html_text += (
                        escape(
                            message_text[  # type: ignore
                                last_offset * 2 : (entity.offset - offset) * 2
                            ].decode("utf-16-le")
                        )
                        + insert
                    )
                else:
                    html_text += (
                        message_text[  # type: ignore
                            last_offset * 2 : (entity.offset - offset) * 2
                        ].decode("utf-16-le")
                        + insert
                    )

                last_offset = entity.offset - offset + entity.length

        if offset == 0:
            html_text += escape(
                message_text[last_offset * 2 :].decode("utf-16-le")  # type: ignore
            )
        else:
            html_text += message_text[last_offset * 2 :].decode("utf-16-le")  # type: ignore

        return html_text

    @property
    def text_html(self) -> str:
        """Creates an HTML-formatted string from the markup entities found in the message.

        Use this if you want to retrieve the message text with the entities formatted as HTML in
        the same way the original message was formatted.

        .. versionchanged:: 13.10
           Spoiler entities are now formatted as HTML.

        .. versionchanged:: 20.3
           Custom emoji entities are now supported.

        Returns:
            :obj:`str`: Message text with entities formatted as HTML.

        """
        return self._parse_html(self.text, self.parse_entities(), urled=False)

    @property
    def text_html_urled(self) -> str:
        """Creates an HTML-formatted string from the markup entities found in the message.

        Use this if you want to retrieve the message text with the entities formatted as HTML.
        This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        .. versionchanged:: 13.10
           Spoiler entities are now formatted as HTML.

        .. versionchanged:: 20.3
           Custom emoji entities are now supported.

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

        .. versionchanged:: 13.10
           Spoiler entities are now formatted as HTML.

        .. versionchanged:: 20.3
           Custom emoji entities are now supported.

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

        .. versionchanged:: 13.10
           Spoiler entities are now formatted as HTML.

        .. versionchanged:: 20.3
           Custom emoji entities are now supported.

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

        message_text = message_text.encode("utf-16-le")  # type: ignore

        markdown_text = ""
        last_offset = 0

        sorted_entities = sorted(entities.items(), key=lambda item: item[0].offset)
        parsed_entities = []

        for entity, text in sorted_entities:
            if entity not in parsed_entities:
                nested_entities = {
                    e: t
                    for (e, t) in sorted_entities
                    if e.offset >= entity.offset
                    and e.offset + e.length <= entity.offset + entity.length
                    and e != entity
                }
                parsed_entities.extend(list(nested_entities.keys()))

                escaped_text = escape_markdown(text, version=version)

                if nested_entities:
                    if version < 2:
                        raise ValueError(
                            "Nested entities are not supported for Markdown version 1"
                        )

                    escaped_text = Message._parse_markdown(
                        text,
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
                    insert = f"[{escaped_text}]({url})"
                elif entity.type == MessageEntity.TEXT_MENTION and entity.user:
                    insert = f"[{escaped_text}](tg://user?id={entity.user.id})"
                elif entity.type == MessageEntity.URL and urled:
                    link = text if version == 1 else escaped_text
                    insert = f"[{link}]({text})"
                elif entity.type == MessageEntity.BOLD:
                    insert = f"*{escaped_text}*"
                elif entity.type == MessageEntity.ITALIC:
                    insert = f"_{escaped_text}_"
                elif entity.type == MessageEntity.CODE:
                    # Monospace needs special escaping. Also can't have entities nested within
                    insert = f"`{escape_markdown(text, version, MessageEntity.CODE)}`"

                elif entity.type == MessageEntity.PRE:
                    # Monospace needs special escaping. Also can't have entities nested within
                    code = escape_markdown(text, version=version, entity_type=MessageEntity.PRE)
                    if entity.language:
                        prefix = f"```{entity.language}\n"
                    elif code.startswith("\\"):
                        prefix = "```"
                    else:
                        prefix = "```\n"
                    insert = f"{prefix}{code}```"
                elif entity.type == MessageEntity.UNDERLINE:
                    if version == 1:
                        raise ValueError(
                            "Underline entities are not supported for Markdown version 1"
                        )
                    insert = f"__{escaped_text}__"
                elif entity.type == MessageEntity.STRIKETHROUGH:
                    if version == 1:
                        raise ValueError(
                            "Strikethrough entities are not supported for Markdown version 1"
                        )
                    insert = f"~{escaped_text}~"
                elif entity.type == MessageEntity.SPOILER:
                    if version == 1:
                        raise ValueError(
                            "Spoiler entities are not supported for Markdown version 1"
                        )
                    insert = f"||{escaped_text}||"
                elif entity.type == MessageEntity.CUSTOM_EMOJI:
                    if version == 1:
                        # this ensures compatibility to previous PTB versions
                        insert = escaped_text
                        warn(
                            "Custom emoji entities are not supported for Markdown version 1. "
                            "Future version of PTB will raise a ValueError instead of falling "
                            "back to the alternative standard emoji.",
                            stacklevel=3,
                            category=PTBDeprecationWarning,
                        )
                    else:
                        # This should never be needed because ids are numeric but the documentation
                        # specifically mentions it so here we are
                        custom_emoji_id = escape_markdown(
                            entity.custom_emoji_id,
                            version=version,
                            entity_type=MessageEntity.CUSTOM_EMOJI,
                        )
                        insert = f"![{escaped_text}](tg://emoji?id={custom_emoji_id})"
                else:
                    insert = escaped_text

                if offset == 0:
                    markdown_text += (
                        escape_markdown(
                            message_text[  # type: ignore
                                last_offset * 2 : (entity.offset - offset) * 2
                            ].decode("utf-16-le"),
                            version=version,
                        )
                        + insert
                    )
                else:
                    markdown_text += (
                        message_text[  # type: ignore
                            last_offset * 2 : (entity.offset - offset) * 2
                        ].decode("utf-16-le")
                        + insert
                    )

                last_offset = entity.offset - offset + entity.length

        if offset == 0:
            markdown_text += escape_markdown(
                message_text[last_offset * 2 :].decode("utf-16-le"),  # type: ignore
                version=version,
            )
        else:
            markdown_text += message_text[last_offset * 2 :].decode("utf-16-le")  # type: ignore

        return markdown_text

    @property
    def text_markdown(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message
        using :class:`telegram.constants.ParseMode.MARKDOWN`.

        Use this if you want to retrieve the message text with the entities formatted as Markdown
        in the same way the original message was formatted.

        Note:
            * :tg-const:`telegram.constants.ParseMode.MARKDOWN` is a legacy mode, retained by
              Telegram for backward compatibility. You should use
              :meth:`text_markdown_v2` instead.

            * |custom_emoji_formatting_note|

        .. deprecated:: 20.3
            |custom_emoji_md1_deprecation|

        Returns:
            :obj:`str`: Message text with entities formatted as Markdown.

        Raises:
            :exc:`ValueError`: If the message contains underline, strikethrough, spoiler or nested
                entities.

        """
        return self._parse_markdown(self.text, self.parse_entities(), urled=False)

    @property
    def text_markdown_v2(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message
        using :class:`telegram.constants.ParseMode.MARKDOWN_V2`.

        Use this if you want to retrieve the message text with the entities formatted as Markdown
        in the same way the original message was formatted.

        .. versionchanged:: 13.10
           Spoiler entities are now formatted as Markdown V2.

        .. versionchanged:: 20.3
           Custom emoji entities are now supported.

        Returns:
            :obj:`str`: Message text with entities formatted as Markdown.
        """
        return self._parse_markdown(self.text, self.parse_entities(), urled=False, version=2)

    @property
    def text_markdown_urled(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message
        using :class:`telegram.constants.ParseMode.MARKDOWN`.

        Use this if you want to retrieve the message text with the entities formatted as Markdown.
        This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        Note:
            * :tg-const:`telegram.constants.ParseMode.MARKDOWN` is a legacy mode, retained by
              Telegram for backward compatibility. You should use :meth:`text_markdown_v2_urled`
              instead.

            * |custom_emoji_formatting_note|

        .. deprecated:: 20.3
            |custom_emoji_md1_deprecation|

        Returns:
            :obj:`str`: Message text with entities formatted as Markdown.

        Raises:
            :exc:`ValueError`: If the message contains underline, strikethrough, spoiler or nested
                entities.

        """
        return self._parse_markdown(self.text, self.parse_entities(), urled=True)

    @property
    def text_markdown_v2_urled(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message
        using :class:`telegram.constants.ParseMode.MARKDOWN_V2`.

        Use this if you want to retrieve the message text with the entities formatted as Markdown.
        This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        .. versionchanged:: 13.10
           Spoiler entities are now formatted as Markdown V2.

        .. versionchanged:: 20.3
           Custom emoji entities are now supported.

        Returns:
            :obj:`str`: Message text with entities formatted as Markdown.
        """
        return self._parse_markdown(self.text, self.parse_entities(), urled=True, version=2)

    @property
    def caption_markdown(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message's
        caption using :class:`telegram.constants.ParseMode.MARKDOWN`.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        Markdown in the same way the original message was formatted.

        Note:
            * :tg-const:`telegram.constants.ParseMode.MARKDOWN` is a legacy mode, retained by
              Telegram for backward compatibility. You should use :meth:`caption_markdown_v2`
              instead.

            * |custom_emoji_formatting_note|

        .. deprecated:: 20.3
            |custom_emoji_md1_deprecation|

        Returns:
            :obj:`str`: Message caption with caption entities formatted as Markdown.

        Raises:
            :exc:`ValueError`: If the message contains underline, strikethrough, spoiler or nested
                entities.

        """
        return self._parse_markdown(self.caption, self.parse_caption_entities(), urled=False)

    @property
    def caption_markdown_v2(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message's
        caption using :class:`telegram.constants.ParseMode.MARKDOWN_V2`.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        Markdown in the same way the original message was formatted.

        .. versionchanged:: 13.10
           Spoiler entities are now formatted as Markdown V2.

        .. versionchanged:: 20.3
           Custom emoji entities are now supported.

        Returns:
            :obj:`str`: Message caption with caption entities formatted as Markdown.
        """
        return self._parse_markdown(
            self.caption, self.parse_caption_entities(), urled=False, version=2
        )

    @property
    def caption_markdown_urled(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message's
        caption using :class:`telegram.constants.ParseMode.MARKDOWN`.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        Markdown. This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        Note:
            * :tg-const:`telegram.constants.ParseMode.MARKDOWN` is a legacy mode, retained by
              Telegram for backward compatibility. You should use
              :meth:`caption_markdown_v2_urled` instead.

            * |custom_emoji_formatting_note|

        .. deprecated:: 20.3
            |custom_emoji_md1_deprecation|

        Returns:
            :obj:`str`: Message caption with caption entities formatted as Markdown.

        Raises:
            :exc:`ValueError`: If the message contains underline, strikethrough, spoiler or nested
                entities.

        """
        return self._parse_markdown(self.caption, self.parse_caption_entities(), urled=True)

    @property
    def caption_markdown_v2_urled(self) -> str:
        """Creates an Markdown-formatted string from the markup entities found in the message's
        caption using :class:`telegram.constants.ParseMode.MARKDOWN_V2`.

        Use this if you want to retrieve the message caption with the caption entities formatted as
        Markdown. This also formats :attr:`telegram.MessageEntity.URL` as a hyperlink.

        .. versionchanged:: 13.10
           Spoiler entities are now formatted as Markdown V2.

        .. versionchanged:: 20.3
           Custom emoji entities are now supported.

        Returns:
            :obj:`str`: Message caption with caption entities formatted as Markdown.
        """
        return self._parse_markdown(
            self.caption, self.parse_caption_entities(), urled=True, version=2
        )
