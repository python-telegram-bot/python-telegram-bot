#!/usr/bin/env python
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
"""This module contains an object that represents a Telegram Update."""

from typing import TYPE_CHECKING, ClassVar, List, Optional

from telegram import constants
from telegram._callbackquery import CallbackQuery
from telegram._chatjoinrequest import ChatJoinRequest
from telegram._chatmemberupdated import ChatMemberUpdated
from telegram._choseninlineresult import ChosenInlineResult
from telegram._inline.inlinequery import InlineQuery
from telegram._message import Message
from telegram._payment.precheckoutquery import PreCheckoutQuery
from telegram._payment.shippingquery import ShippingQuery
from telegram._poll import Poll, PollAnswer
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot, Chat, User


class Update(TelegramObject):
    """This object represents an incoming update.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`update_id` is equal.

    Note:
        At most one of the optional parameters can be present in any given update.

    .. seealso:: :wiki:`Your First Bot <Extensions---Your-first-Bot>`

    Args:
        update_id (:obj:`int`): The update's unique identifier. Update identifiers start from a
            certain positive number and increase sequentially. This ID becomes especially handy if
            you're using Webhooks, since it allows you to ignore repeated updates or to restore the
            correct update sequence, should they get out of order. If there are no new updates for
            at least a week, then identifier of the next update will be chosen randomly instead of
            sequentially.
        message (:class:`telegram.Message`, optional): New incoming message of any kind - text,
            photo, sticker, etc.
        edited_message (:class:`telegram.Message`, optional): New version of a message that is
            known to the bot and was edited.
        channel_post (:class:`telegram.Message`, optional): New incoming channel post of any kind
            - text, photo, sticker, etc.
        edited_channel_post (:class:`telegram.Message`, optional): New version of a channel post
            that is known to the bot and was edited.
        inline_query (:class:`telegram.InlineQuery`, optional): New incoming inline query.
        chosen_inline_result (:class:`telegram.ChosenInlineResult`, optional): The result of an
            inline query that was chosen by a user and sent to their chat partner.
        callback_query (:class:`telegram.CallbackQuery`, optional): New incoming callback query.
        shipping_query (:class:`telegram.ShippingQuery`, optional): New incoming shipping query.
            Only for invoices with flexible price.
        pre_checkout_query (:class:`telegram.PreCheckoutQuery`, optional): New incoming
            pre-checkout query. Contains full information about checkout.
        poll (:class:`telegram.Poll`, optional): New poll state. Bots receive only updates about
            stopped polls and polls, which are sent by the bot.
        poll_answer (:class:`telegram.PollAnswer`, optional): A user changed their answer
            in a non-anonymous poll. Bots receive new votes only in polls that were sent
            by the bot itself.
        my_chat_member (:class:`telegram.ChatMemberUpdated`, optional): The bot's chat member
            status was updated in a chat. For private chats, this update is received only when the
            bot is blocked or unblocked by the user.

            .. versionadded:: 13.4
        chat_member (:class:`telegram.ChatMemberUpdated`, optional): A chat member's status was
            updated in a chat. The bot must be an administrator in the chat and must explicitly
            specify :attr:`CHAT_MEMBER` in the list of
            :paramref:`telegram.ext.Application.run_polling.allowed_updates` to receive these
            updates (see :meth:`telegram.Bot.get_updates`, :meth:`telegram.Bot.set_webhook`,
            :meth:`telegram.ext.Application.run_polling` and
            :meth:`telegram.ext.Application.run_webhook`).

            .. versionadded:: 13.4
        chat_join_request (:class:`telegram.ChatJoinRequest`, optional): A request to join the
            chat has been sent. The bot must have the
            :attr:`telegram.ChatPermissions.can_invite_users` administrator right in the chat to
            receive these updates.

            .. versionadded:: 13.8
    Attributes:
        update_id (:obj:`int`): The update's unique identifier. Update identifiers start from a
            certain positive number and increase sequentially. This ID becomes especially handy if
            you're using Webhooks, since it allows you to ignore repeated updates or to restore the
            correct update sequence, should they get out of order. If there are no new updates for
            at least a week, then identifier of the next update will be chosen randomly instead of
            sequentially.
        message (:class:`telegram.Message`): Optional. New incoming message of any kind - text,
            photo, sticker, etc.
        edited_message (:class:`telegram.Message`): Optional. New version of a message that is
            known to the bot and was edited.
        channel_post (:class:`telegram.Message`): Optional. New incoming channel post of any kind
            - text, photo, sticker, etc.
        edited_channel_post (:class:`telegram.Message`): Optional. New version of a channel post
            that is known to the bot and was edited.
        inline_query (:class:`telegram.InlineQuery`): Optional. New incoming inline query.
        chosen_inline_result (:class:`telegram.ChosenInlineResult`): Optional. The result of an
            inline query that was chosen by a user and sent to their chat partner.
        callback_query (:class:`telegram.CallbackQuery`): Optional. New incoming callback query.

            Examples:
                :any:`Arbitrary Callback Data Bot <examples.arbitrarycallbackdatabot>`
        shipping_query (:class:`telegram.ShippingQuery`): Optional. New incoming shipping query.
            Only for invoices with flexible price.
        pre_checkout_query (:class:`telegram.PreCheckoutQuery`): Optional. New incoming
            pre-checkout query. Contains full information about checkout.
        poll (:class:`telegram.Poll`): Optional. New poll state. Bots receive only updates about
            stopped polls and polls, which are sent by the bot.
        poll_answer (:class:`telegram.PollAnswer`): Optional. A user changed their answer
            in a non-anonymous poll. Bots receive new votes only in polls that were sent
            by the bot itself.
        my_chat_member (:class:`telegram.ChatMemberUpdated`): Optional. The bot's chat member
            status was updated in a chat. For private chats, this update is received only when the
            bot is blocked or unblocked by the user.

            .. versionadded:: 13.4
        chat_member (:class:`telegram.ChatMemberUpdated`): Optional. A chat member's status was
            updated in a chat. The bot must be an administrator in the chat and must explicitly
            specify :attr:`CHAT_MEMBER` in the list of
            :paramref:`telegram.ext.Application.run_polling.allowed_updates` to receive these
            updates (see :meth:`telegram.Bot.get_updates`, :meth:`telegram.Bot.set_webhook`,
            :meth:`telegram.ext.Application.run_polling` and
            :meth:`telegram.ext.Application.run_webhook`).

            .. versionadded:: 13.4
        chat_join_request (:class:`telegram.ChatJoinRequest`): Optional. A request to join the
            chat has been sent. The bot must have the
            :attr:`telegram.ChatPermissions.can_invite_users` administrator right in the chat to
            receive these updates.

            .. versionadded:: 13.8

    """

    __slots__ = (
        "callback_query",
        "chosen_inline_result",
        "pre_checkout_query",
        "inline_query",
        "update_id",
        "message",
        "shipping_query",
        "poll",
        "poll_answer",
        "channel_post",
        "edited_channel_post",
        "edited_message",
        "_effective_user",
        "_effective_chat",
        "_effective_message",
        "my_chat_member",
        "chat_member",
        "chat_join_request",
    )

    MESSAGE: ClassVar[str] = constants.UpdateType.MESSAGE
    """:const:`telegram.constants.UpdateType.MESSAGE`

    .. versionadded:: 13.5"""
    EDITED_MESSAGE: ClassVar[str] = constants.UpdateType.EDITED_MESSAGE
    """:const:`telegram.constants.UpdateType.EDITED_MESSAGE`

    .. versionadded:: 13.5"""
    CHANNEL_POST: ClassVar[str] = constants.UpdateType.CHANNEL_POST
    """:const:`telegram.constants.UpdateType.CHANNEL_POST`

    .. versionadded:: 13.5"""
    EDITED_CHANNEL_POST: ClassVar[str] = constants.UpdateType.EDITED_CHANNEL_POST
    """:const:`telegram.constants.UpdateType.EDITED_CHANNEL_POST`

    .. versionadded:: 13.5"""
    INLINE_QUERY: ClassVar[str] = constants.UpdateType.INLINE_QUERY
    """:const:`telegram.constants.UpdateType.INLINE_QUERY`

    .. versionadded:: 13.5"""
    CHOSEN_INLINE_RESULT: ClassVar[str] = constants.UpdateType.CHOSEN_INLINE_RESULT
    """:const:`telegram.constants.UpdateType.CHOSEN_INLINE_RESULT`

    .. versionadded:: 13.5"""
    CALLBACK_QUERY: ClassVar[str] = constants.UpdateType.CALLBACK_QUERY
    """:const:`telegram.constants.UpdateType.CALLBACK_QUERY`

    .. versionadded:: 13.5"""
    SHIPPING_QUERY: ClassVar[str] = constants.UpdateType.SHIPPING_QUERY
    """:const:`telegram.constants.UpdateType.SHIPPING_QUERY`

    .. versionadded:: 13.5"""
    PRE_CHECKOUT_QUERY: ClassVar[str] = constants.UpdateType.PRE_CHECKOUT_QUERY
    """:const:`telegram.constants.UpdateType.PRE_CHECKOUT_QUERY`

    .. versionadded:: 13.5"""
    POLL: ClassVar[str] = constants.UpdateType.POLL
    """:const:`telegram.constants.UpdateType.POLL`

    .. versionadded:: 13.5"""
    POLL_ANSWER: ClassVar[str] = constants.UpdateType.POLL_ANSWER
    """:const:`telegram.constants.UpdateType.POLL_ANSWER`

    .. versionadded:: 13.5"""
    MY_CHAT_MEMBER: ClassVar[str] = constants.UpdateType.MY_CHAT_MEMBER
    """:const:`telegram.constants.UpdateType.MY_CHAT_MEMBER`

    .. versionadded:: 13.5"""
    CHAT_MEMBER: ClassVar[str] = constants.UpdateType.CHAT_MEMBER
    """:const:`telegram.constants.UpdateType.CHAT_MEMBER`

    .. versionadded:: 13.5"""
    CHAT_JOIN_REQUEST = constants.UpdateType.CHAT_JOIN_REQUEST
    """:const:`telegram.constants.UpdateType.CHAT_JOIN_REQUEST`

    .. versionadded:: 13.8"""
    ALL_TYPES: ClassVar[List[str]] = list(constants.UpdateType)
    """List[:obj:`str`]: A list of all available update types.

    .. versionadded:: 13.5"""

    def __init__(
        self,
        update_id: int,
        message: Message = None,
        edited_message: Message = None,
        channel_post: Message = None,
        edited_channel_post: Message = None,
        inline_query: InlineQuery = None,
        chosen_inline_result: ChosenInlineResult = None,
        callback_query: CallbackQuery = None,
        shipping_query: ShippingQuery = None,
        pre_checkout_query: PreCheckoutQuery = None,
        poll: Poll = None,
        poll_answer: PollAnswer = None,
        my_chat_member: ChatMemberUpdated = None,
        chat_member: ChatMemberUpdated = None,
        chat_join_request: ChatJoinRequest = None,
        *,
        api_kwargs: JSONDict = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.update_id: int = update_id
        # Optionals
        self.message: Optional[Message] = message
        self.edited_message: Optional[Message] = edited_message
        self.inline_query: Optional[InlineQuery] = inline_query
        self.chosen_inline_result: Optional[ChosenInlineResult] = chosen_inline_result
        self.callback_query: Optional[CallbackQuery] = callback_query
        self.shipping_query: Optional[ShippingQuery] = shipping_query
        self.pre_checkout_query: Optional[PreCheckoutQuery] = pre_checkout_query
        self.channel_post: Optional[Message] = channel_post
        self.edited_channel_post: Optional[Message] = edited_channel_post
        self.poll: Optional[Poll] = poll
        self.poll_answer: Optional[PollAnswer] = poll_answer
        self.my_chat_member: Optional[ChatMemberUpdated] = my_chat_member
        self.chat_member: Optional[ChatMemberUpdated] = chat_member
        self.chat_join_request: Optional[ChatJoinRequest] = chat_join_request

        self._effective_user: Optional["User"] = None
        self._effective_chat: Optional["Chat"] = None
        self._effective_message: Optional[Message] = None

        self._id_attrs = (self.update_id,)

        self._freeze()

    @property
    def effective_user(self) -> Optional["User"]:
        """
        :class:`telegram.User`: The user that sent this update, no matter what kind of update this
        is. If no user is associated with this update, this gives :obj:`None`. This is the case
        if :attr:`channel_post`, :attr:`edited_channel_post` or :attr:`poll` is present.

        Example:
            * If :attr:`message` is present, this will give
              :attr:`telegram.Message.from_user`.
            * If :attr:`poll_answer` is present, this will give :attr:`telegram.PollAnswer.user`.

        """
        if self._effective_user:
            return self._effective_user

        user = None

        if self.message:
            user = self.message.from_user

        elif self.edited_message:
            user = self.edited_message.from_user

        elif self.inline_query:
            user = self.inline_query.from_user

        elif self.chosen_inline_result:
            user = self.chosen_inline_result.from_user

        elif self.callback_query:
            user = self.callback_query.from_user

        elif self.shipping_query:
            user = self.shipping_query.from_user

        elif self.pre_checkout_query:
            user = self.pre_checkout_query.from_user

        elif self.poll_answer:
            user = self.poll_answer.user

        elif self.my_chat_member:
            user = self.my_chat_member.from_user

        elif self.chat_member:
            user = self.chat_member.from_user

        elif self.chat_join_request:
            user = self.chat_join_request.from_user

        self._effective_user = user
        return user

    @property
    def effective_chat(self) -> Optional["Chat"]:
        """
        :class:`telegram.Chat`: The chat that this update was sent in, no matter what kind of
        update this is.
        If no chat is associated with this update, this gives :obj:`None`.
        This is the case, if :attr:`inline_query`,
        :attr:`chosen_inline_result`, :attr:`callback_query` from inline messages,
        :attr:`shipping_query`, :attr:`pre_checkout_query`, :attr:`poll` or
        :attr:`poll_answer` is present.

        Example:
            If :attr:`message` is present, this will give :attr:`telegram.Message.chat`.

        """
        if self._effective_chat:
            return self._effective_chat

        chat = None

        if self.message:
            chat = self.message.chat

        elif self.edited_message:
            chat = self.edited_message.chat

        elif self.callback_query and self.callback_query.message:
            chat = self.callback_query.message.chat

        elif self.channel_post:
            chat = self.channel_post.chat

        elif self.edited_channel_post:
            chat = self.edited_channel_post.chat

        elif self.my_chat_member:
            chat = self.my_chat_member.chat

        elif self.chat_member:
            chat = self.chat_member.chat

        elif self.chat_join_request:
            chat = self.chat_join_request.chat

        self._effective_chat = chat
        return chat

    @property
    def effective_message(self) -> Optional[Message]:
        """
        :class:`telegram.Message`: The message included in this update, no matter what kind of
            update this is. More precisely, this will be the message contained in :attr:`message`,
            :attr:`edited_message`, :attr:`channel_post`, :attr:`edited_channel_post` or
            :attr:`callback_query` (i.e. :attr:`telegram.CallbackQuery.message`) or :obj:`None`, if
            none of those are present.

        """
        if self._effective_message:
            return self._effective_message

        message = None

        if self.message:
            message = self.message

        elif self.edited_message:
            message = self.edited_message

        elif self.callback_query:
            message = self.callback_query.message

        elif self.channel_post:
            message = self.channel_post

        elif self.edited_channel_post:
            message = self.edited_channel_post

        self._effective_message = message
        return message

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["Update"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["message"] = Message.de_json(data.get("message"), bot)
        data["edited_message"] = Message.de_json(data.get("edited_message"), bot)
        data["inline_query"] = InlineQuery.de_json(data.get("inline_query"), bot)
        data["chosen_inline_result"] = ChosenInlineResult.de_json(
            data.get("chosen_inline_result"), bot
        )
        data["callback_query"] = CallbackQuery.de_json(data.get("callback_query"), bot)
        data["shipping_query"] = ShippingQuery.de_json(data.get("shipping_query"), bot)
        data["pre_checkout_query"] = PreCheckoutQuery.de_json(data.get("pre_checkout_query"), bot)
        data["channel_post"] = Message.de_json(data.get("channel_post"), bot)
        data["edited_channel_post"] = Message.de_json(data.get("edited_channel_post"), bot)
        data["poll"] = Poll.de_json(data.get("poll"), bot)
        data["poll_answer"] = PollAnswer.de_json(data.get("poll_answer"), bot)
        data["my_chat_member"] = ChatMemberUpdated.de_json(data.get("my_chat_member"), bot)
        data["chat_member"] = ChatMemberUpdated.de_json(data.get("chat_member"), bot)
        data["chat_join_request"] = ChatJoinRequest.de_json(data.get("chat_join_request"), bot)

        return super().de_json(data=data, bot=bot)
