#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""This modules contains objects that represents Telegram Replies"""

from typing import TYPE_CHECKING

from telegram._chat import Chat
from telegram._checklists import Checklist
from telegram._dice import Dice
from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.document import Document
from telegram._files.livephoto import LivePhoto
from telegram._files.photosize import PhotoSize
from telegram._files.sticker import Sticker
from telegram._files.venue import Venue
from telegram._files.video import Video
from telegram._files.videonote import VideoNote
from telegram._files.voice import Voice
from telegram._games.game import Game
from telegram._giveaway import Giveaway, GiveawayWinners
from telegram._linkpreviewoptions import LinkPreviewOptions
from telegram._messageentity import MessageEntity
from telegram._messageorigin import MessageOrigin
from telegram._paidmedia import PaidMediaInfo
from telegram._payment.invoice import Invoice
from telegram._poll import Poll
from telegram._story import Story
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import ODVInput

if TYPE_CHECKING:
    from telegram._files.contact import Contact
    from telegram._files.location import Location


@tg_dataclass()
class ExternalReplyInfo(TelegramObject):
    """
    This object contains information about a message that is being replied to, which may
    come from another chat or forum topic.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`origin` is equal.

    .. versionadded:: 20.8

    Args:
        origin (:class:`telegram.MessageOrigin`): Origin of the message replied to by the given
            message.
        chat (:class:`telegram.Chat`, optional): Chat the original message belongs to. Available
            only if the chat is a supergroup or a channel.
        message_id (:obj:`int`, optional): Unique message identifier inside the original chat.
            Available only if the original chat is a supergroup or a channel.
        link_preview_options (:class:`telegram.LinkPreviewOptions`, optional): Options used for
            link preview generation for the original message, if it is a text message
        animation (:class:`telegram.Animation`, optional): Message is an animation, information
            about the animation.
        audio (:class:`telegram.Audio`, optional): Message is an audio file, information about the
            file.
        document (:class:`telegram.Document`, optional): Message is a general file, information
            about the file.
        photo (Sequence[:class:`telegram.PhotoSize`], optional): Message is a photo, available
            sizes of the photo.
        sticker (:class:`telegram.Sticker`, optional): Message is a sticker, information about the
            sticker.
        story (:class:`telegram.Story`, optional): Message is a forwarded story.
        video (:class:`telegram.Video`, optional): Message is a video, information about the video.
        video_note (:class:`telegram.VideoNote`, optional): Message is a `video note
            <https://telegram.org/blog/video-messages-and-telescope>`_, information about the video
            message.
        voice (:class:`telegram.Voice`, optional): Message is a voice message, information about
            the file.
        has_media_spoiler (:obj:`bool`, optional): :obj:`True`, if the message media is covered by
            a spoiler animation.
        checklist (:class:`telegram.Checklist`, optional): Message is a checklist.

            .. versionadded:: 22.3
        contact (:class:`telegram.Contact`, optional): Message is a shared contact, information
            about the contact.
        dice (:class:`telegram.Dice`, optional): Message is a dice with random value.
        game (:Class:`telegram.Game`. optional): Message is a game, information about the game.
            :ref:`More about games >> <games-tree>`.
        giveaway (:class:`telegram.Giveaway`, optional): Message is a scheduled giveaway,
            information about the giveaway.
        giveaway_winners (:class:`telegram.GiveawayWinners`, optional): A giveaway with public
            winners was completed.
        invoice (:class:`telegram.Invoice`, optional): Message is an invoice for a payment,
            information about the invoice. :ref:`More about payments >> <payments-tree>`.
        location (:class:`telegram.Location`, optional): Message is a shared location, information
            about the location.
        poll (:class:`telegram.Poll`, optional): Message is a native poll, information about the
            poll.
        venue (:class:`telegram.Venue`, optional): Message is a venue, information about the venue.
        paid_media (:class:`telegram.PaidMedia`, optional): Message contains paid media;
            information about the paid media.

            .. versionadded:: 21.4
        live_photo (:class:`telegram.LivePhoto`, optional): Message is a live photo, information
            about the live photo.

            .. versionadded:: 22.8

    Attributes:
        origin (:class:`telegram.MessageOrigin`): Origin of the message replied to by the given
            message.
        chat (:class:`telegram.Chat`): Optional. Chat the original message belongs to. Available
            only if the chat is a supergroup or a channel.
        message_id (:obj:`int`): Optional. Unique message identifier inside the original chat.
            Available only if the original chat is a supergroup or a channel.
        link_preview_options (:class:`telegram.LinkPreviewOptions`): Optional. Options used for
            link preview generation for the original message, if it is a text message.
        animation (:class:`telegram.Animation`): Optional. Message is an animation, information
            about the animation.
        audio (:class:`telegram.Audio`): Optional. Message is an audio file, information about the
            file.
        document (:class:`telegram.Document`): Optional. Message is a general file, information
            about the file.
        photo (tuple[:class:`telegram.PhotoSize`]): Optional. Message is a photo, available sizes
            of the photo.
        sticker (:class:`telegram.Sticker`): Optional. Message is a sticker, information about the
            sticker.
        story (:class:`telegram.Story`): Optional. Message is a forwarded story.
        video (:class:`telegram.Video`): Optional. Message is a video, information about the video.
        video_note (:class:`telegram.VideoNote`): Optional. Message is a `video note
            <https://telegram.org/blog/video-messages-and-telescope>`_, information about the video
            message.
        voice (:class:`telegram.Voice`): Optional. Message is a voice message, information about
            the file.
        has_media_spoiler (:obj:`bool`): Optional. :obj:`True`, if the message media is covered by
            a spoiler animation.
        checklist (:class:`telegram.Checklist`): Optional. Message is a checklist.

            .. versionadded:: 22.3
        contact (:class:`telegram.Contact`): Optional. Message is a shared contact, information
            about the contact.
        dice (:class:`telegram.Dice`): Optional. Message is a dice with random value.
        game (:Class:`telegram.Game`): Optional. Message is a game, information about the game.
            :ref:`More about games >> <games-tree>`.
        giveaway (:class:`telegram.Giveaway`): Optional. Message is a scheduled giveaway,
            information about the giveaway.
        giveaway_winners (:class:`telegram.GiveawayWinners`): Optional. A giveaway with public
            winners was completed.
        invoice (:class:`telegram.Invoice`): Optional. Message is an invoice for a payment,
            information about the invoice. :ref:`More about payments >> <payments-tree>`.
        location (:class:`telegram.Location`): Optional. Message is a shared location, information
            about the location.
        poll (:class:`telegram.Poll`): Optional. Message is a native poll, information about the
            poll.
        venue (:class:`telegram.Venue`): Optional. Message is a venue, information about the venue.
        paid_media (:class:`telegram.PaidMedia`): Optional. Message contains paid media;
            information about the paid media.

            .. versionadded:: 21.4
        live_photo (:class:`telegram.LivePhoto`): Optional. Message is a live photo, information
            about the live photo.

            .. versionadded:: 22.8

    """

    # Required
    origin: MessageOrigin = tg_field(compare=True)
    # Optionals
    chat: Chat | None = tg_field(default=None)
    message_id: int | None = tg_field(default=None)
    link_preview_options: LinkPreviewOptions | None = tg_field(default=None)
    animation: Animation | None = tg_field(default=None)
    audio: Audio | None = tg_field(default=None)
    document: Document | None = tg_field(default=None)
    photo: tuple[PhotoSize, ...] = tg_field(default=None, converter=parse_sequence_arg)
    sticker: Sticker | None = tg_field(default=None)
    story: Story | None = tg_field(default=None)
    video: Video | None = tg_field(default=None)
    video_note: VideoNote | None = tg_field(default=None)
    voice: Voice | None = tg_field(default=None)
    has_media_spoiler: bool | None = tg_field(default=None)
    contact: "Contact | None" = tg_field(default=None)
    dice: Dice | None = tg_field(default=None)
    game: Game | None = tg_field(default=None)
    giveaway: Giveaway | None = tg_field(default=None)
    giveaway_winners: GiveawayWinners | None = tg_field(default=None)
    invoice: Invoice | None = tg_field(default=None)
    location: "Location | None" = tg_field(default=None)
    poll: Poll | None = tg_field(default=None)
    venue: Venue | None = tg_field(default=None)
    paid_media: PaidMediaInfo | None = tg_field(default=None)
    checklist: Checklist | None = tg_field(default=None)
    live_photo: LivePhoto | None = tg_field(default=None)


@tg_dataclass()
class TextQuote(TelegramObject):
    """
    This object contains information about the quoted part of a message that is replied to
    by the given message.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`text` and :attr:`position` are equal.

    .. versionadded:: 20.8

    Args:
        text (:obj:`str`): Text of the quoted part of a message that is replied to by the given
            message.
        position (:obj:`int`): Approximate quote position in the original message in UTF-16 code
            units as specified by the sender.
        entities (Sequence[:class:`telegram.MessageEntity`], optional): Special entities that
            appear
            in the quote. Currently, only bold, italic, underline, strikethrough, spoiler,
            custom_emoji, and date_time entities are kept in quotes.
        is_manual (:obj:`bool`, optional): :obj:`True`, if the quote was chosen manually by the
            message sender. Otherwise, the quote was added automatically by the server.

    Attributes:
        text (:obj:`str`): Text of the quoted part of a message that is replied to by the given
            message.
        position (:obj:`int`): Approximate quote position in the original message in UTF-16 code
            units as specified by the sender.
        entities (tuple[:class:`telegram.MessageEntity`]): Optional. Special entities that appear
            in the quote. Currently, only bold, italic, underline, strikethrough, spoiler,
            custom_emoji, and date_time entities are kept in quotes.
        is_manual (:obj:`bool`): Optional. :obj:`True`, if the quote was chosen manually by the
            message sender. Otherwise, the quote was added automatically by the server.
    """

    # Required
    text: str = tg_field(compare=True)
    position: int = tg_field(compare=True)
    # Optional
    entities: tuple[MessageEntity, ...] = tg_field(default=None, converter=parse_sequence_arg)
    is_manual: bool | None = tg_field(default=None)


@tg_dataclass()
class ReplyParameters(TelegramObject):
    """
    Describes reply parameters for the message that is being sent.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`message_id` is equal.

    .. versionadded:: 20.8

    .. versionchanged:: 22.5
        The :paramref:`checklist_task_id` parameter has been moved to the last position to
        maintain backward compatibility with versions prior to 22.4.
        This resolves a breaking change accidentally introduced in version 22.4. See the changelog
        for version 22.5 for more information.

    Args:
        message_id (:obj:`int`): Identifier of the message that will be replied to in the current
            chat, or in the chat :paramref:`chat_id` if it is specified.
        chat_id (:obj:`int` | :obj:`str`, optional): If the message to be replied to is from a
            different chat, |chat_id_channel|
            Not supported for messages sent on behalf of a business account and messages from
            channel direct messages chats.
        allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply| Can be
            used only for replies in the same chat and forum topic.
        quote (:obj:`str`, optional): Quoted part of the message to be replied to; 0-1024
            characters after entities parsing. The quote must be an exact substring of the message
            to be replied to, including bold, italic, underline, strikethrough, spoiler,
            custom_emoji, and date_time entities. The message will fail to send if the quote isn't
            found in the original message.
        quote_parse_mode (:obj:`str`, optional): Mode for parsing entities in the quote. See
            :wiki:`formatting options <Code-snippets#message-formatting-bold-italic-code->` for
            more details.
        quote_entities (Sequence[:class:`telegram.MessageEntity`], optional): A JSON-serialized
            list
            of special entities that appear in the quote. It can be specified instead of
            :paramref:`quote_parse_mode`.
        quote_position (:obj:`int`, optional): Position of the quote in the original message in
            UTF-16 code units.
        checklist_task_id (:obj:`int`, optional): Identifier of the specific checklist task to be
            replied to.

            .. versionadded:: 22.4
        poll_option_id (:obj:`str`, optional): Persistent
            identifier of the specific poll option to be replied to.

            .. versionadded:: 22.8

    Attributes:
        message_id (:obj:`int`): Identifier of the message that will be replied to in the current
            chat, or in the chat :paramref:`chat_id` if it is specified.
        chat_id (:obj:`int` | :obj:`str`): Optional. If the message to be replied to is from a
            different chat, |chat_id_channel|
            Not supported for messages sent on behalf of a business account and messages from
            channel direct messages chats.
        allow_sending_without_reply (:obj:`bool`): Optional. |allow_sending_without_reply| Can be
            used only for replies in the same chat and forum topic.
        quote (:obj:`str`): Optional. Quoted part of the message to be replied to; 0-1024
            characters after entities parsing. The quote must be an exact substring of the message
            to be replied to, including bold, italic, underline, strikethrough, spoiler,
            custom_emoji, and date_time entities. The message will fail to send if the quote isn't
            found in the original message.
        quote_parse_mode (:obj:`str`): Optional. Mode for parsing entities in the quote. See
            :wiki:`formatting options <Code-snippets#message-formatting-bold-italic-code->` for
            more details.
        quote_entities (tuple[:class:`telegram.MessageEntity`]): Optional. A JSON-serialized list
            of special entities that appear in the quote. It can be specified instead of
            :paramref:`quote_parse_mode`.
        quote_position (:obj:`int`): Optional. Position of the quote in the original message in
            UTF-16 code units.
        checklist_task_id (:obj:`int`): Optional. Identifier of the specific checklist task to be
            replied to.

            .. versionadded:: 22.4
        poll_option_id (:obj:`str`): Optional. Persistent
            identifier of the specific poll option to be replied to.

            .. versionadded:: 22.8
    """

    # Required
    message_id: int = tg_field(compare=True)
    # Optional
    chat_id: int | str | None = tg_field(default=None)
    allow_sending_without_reply: ODVInput[bool] = tg_field(default=DEFAULT_NONE)
    quote: str | None = tg_field(default=None)
    quote_parse_mode: ODVInput[str] = tg_field(default=DEFAULT_NONE)
    quote_entities: tuple[MessageEntity, ...] = tg_field(
        default=None, converter=parse_sequence_arg
    )
    quote_position: int | None = tg_field(default=None)
    checklist_task_id: int | None = tg_field(default=None)
    poll_option_id: str | None = tg_field(default=None)
