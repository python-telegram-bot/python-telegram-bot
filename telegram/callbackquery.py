#!/usr/bin/env python
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
# pylint: disable=W0622
"""This module contains an object that represents a Telegram CallbackQuery"""
from typing import TYPE_CHECKING, Any, List, Optional, Union, Tuple, ClassVar

from telegram import Message, TelegramObject, User, Location, ReplyMarkup, constants
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import (
        Bot,
        GameHighScore,
        InlineKeyboardMarkup,
        MessageId,
        InputMedia,
        MessageEntity,
    )


class CallbackQuery(TelegramObject):
    """
    This object represents an incoming callback query from a callback button in an inline keyboard.

    If the button that originated the query was attached to a message sent by the bot, the field
    :attr:`message` will be present. If the button was attached to a message sent via the bot (in
    inline mode), the field :attr:`inline_message_id` will be present.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.
        * Exactly one of the fields :attr:`data` or :attr:`game_short_name` will be present.
        * After the user presses an inline button, Telegram clients will display a progress bar
          until you call :attr:`answer`. It is, therefore, necessary to react
          by calling :attr:`telegram.Bot.answer_callback_query` even if no notification to the user
          is needed (e.g., without specifying any of the optional parameters).

    Args:
        id (:obj:`str`): Unique identifier for this query.
        from_user (:class:`telegram.User`): Sender.
        chat_instance (:obj:`str`): Global identifier, uniquely corresponding to the chat to which
            the message with the callback button was sent. Useful for high scores in games.
        message (:class:`telegram.Message`, optional): Message with the callback button that
            originated the query. Note that message content and message date will not be available
            if the message is too old.
        data (:obj:`str`, optional): Data associated with the callback button. Be aware that a bad
            client can send arbitrary data in this field.
        inline_message_id (:obj:`str`, optional): Identifier of the message sent via the bot in
            inline mode, that originated the query.
        game_short_name (:obj:`str`, optional): Short name of a Game to be returned, serves as
            the unique identifier for the game
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    Attributes:
        id (:obj:`str`): Unique identifier for this query.
        from_user (:class:`telegram.User`): Sender.
        chat_instance (:obj:`str`): Global identifier, uniquely corresponding to the chat to which
            the message with the callback button was sent.
        message (:class:`telegram.Message`): Optional. Message with the callback button that
            originated the query.
        data (:obj:`str`): Optional. Data associated with the callback button.
        inline_message_id (:obj:`str`): Optional. Identifier of the message sent via the bot in
                inline mode, that originated the query.
        game_short_name (:obj:`str`): Optional. Short name of a Game to be returned.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    """

    def __init__(
        self,
        id: str,  # pylint: disable=W0622
        from_user: User,
        chat_instance: str,
        message: Message = None,
        data: str = None,
        inline_message_id: str = None,
        game_short_name: str = None,
        bot: 'Bot' = None,
        **_kwargs: Any,
    ):
        # Required
        self.id = id  # pylint: disable=C0103
        self.from_user = from_user
        self.chat_instance = chat_instance
        # Optionals
        self.message = message
        self.data = data
        self.inline_message_id = inline_message_id
        self.game_short_name = game_short_name

        self.bot = bot

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['CallbackQuery']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['from_user'] = User.de_json(data.get('from'), bot)
        data['message'] = Message.de_json(data.get('message'), bot)

        return cls(bot=bot, **data)

    def answer(
        self,
        text: str = None,
        show_alert: bool = False,
        url: str = None,
        cache_time: int = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            bot.answer_callback_query(update.callback_query.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.answer_callback_query`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.answer_callback_query(
            callback_query_id=self.id,
            text=text,
            show_alert=show_alert,
            url=url,
            cache_time=cache_time,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def edit_message_text(
        self,
        text: str,
        parse_mode: str = None,
        disable_web_page_preview: bool = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            update.callback_query.message.edit_text(text, *args, **kwargs)

        or::

            bot.edit_message_text(text, inline_message_id=update.callback_query.inline_message_id,
                                *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_text`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return self.bot.edit_message_text(
                inline_message_id=self.inline_message_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                reply_markup=reply_markup,
                timeout=timeout,
                api_kwargs=api_kwargs,
                entities=entities,
                chat_id=None,
                message_id=None,
            )
        return self.message.edit_text(
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            entities=entities,
        )

    def edit_message_caption(
        self,
        caption: str = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        timeout: float = None,
        parse_mode: str = None,
        api_kwargs: JSONDict = None,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            update.callback_query.message.edit_caption(caption, *args, **kwargs)

        or::

            bot.edit_message_caption(caption=caption
                                    inline_message_id=update.callback_query.inline_message_id,
                                   *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_caption`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return self.bot.edit_message_caption(
                caption=caption,
                inline_message_id=self.inline_message_id,
                reply_markup=reply_markup,
                timeout=timeout,
                parse_mode=parse_mode,
                api_kwargs=api_kwargs,
                caption_entities=caption_entities,
                chat_id=None,
                message_id=None,
            )
        return self.message.edit_caption(
            caption=caption,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            caption_entities=caption_entities,
        )

    def edit_message_reply_markup(
        self,
        reply_markup: Optional['InlineKeyboardMarkup'] = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            update.callback_query.message.edit_reply_markup(
                reply_markup=reply_markup,
                *args,
                **kwargs
            )

        or::

            bot.edit_message_reply_markup
                inline_message_id=update.callback_query.inline_message_id,
                reply_markup=reply_markup,
                *args,
                **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_reply_markup`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return self.bot.edit_message_reply_markup(
                reply_markup=reply_markup,
                inline_message_id=self.inline_message_id,
                timeout=timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return self.message.edit_reply_markup(
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def edit_message_media(
        self,
        media: 'InputMedia' = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            update.callback_query.message.edit_media(*args, **kwargs)

        or::

            bot.edit_message_media(inline_message_id=update.callback_query.inline_message_id,
                                   *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_media`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return self.bot.edit_message_media(
                inline_message_id=self.inline_message_id,
                media=media,
                reply_markup=reply_markup,
                timeout=timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return self.message.edit_media(
            media=media,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def edit_message_live_location(
        self,
        latitude: float = None,
        longitude: float = None,
        location: Location = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            update.callback_query.message.edit_live_location(*args, **kwargs)

        or::

            bot.edit_message_live_location(
                inline_message_id=update.callback_query.inline_message_id,
                *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_message_live_location`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return self.bot.edit_message_live_location(
                inline_message_id=self.inline_message_id,
                latitude=latitude,
                longitude=longitude,
                location=location,
                reply_markup=reply_markup,
                timeout=timeout,
                api_kwargs=api_kwargs,
                horizontal_accuracy=horizontal_accuracy,
                heading=heading,
                proximity_alert_radius=proximity_alert_radius,
                chat_id=None,
                message_id=None,
            )
        return self.message.edit_live_location(
            latitude=latitude,
            longitude=longitude,
            location=location,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
        )

    def stop_message_live_location(
        self,
        reply_markup: 'InlineKeyboardMarkup' = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

            update.callback_query.message.stop_live_location(*args, **kwargs)

        or::

            bot.stop_message_live_location(
                inline_message_id=update.callback_query.inline_message_id,
                *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.stop_message_live_location`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return self.bot.stop_message_live_location(
                inline_message_id=self.inline_message_id,
                reply_markup=reply_markup,
                timeout=timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return self.message.stop_live_location(
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def set_game_score(
        self,
        user_id: Union[int, str],
        score: int,
        force: bool = None,
        disable_edit_message: bool = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """Shortcut for either::

           update.callback_query.message.set_game_score(*args, **kwargs)

        or::

            bot.set_game_score(inline_message_id=update.callback_query.inline_message_id,
                               *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_game_score`.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        """
        if self.inline_message_id:
            return self.bot.set_game_score(
                inline_message_id=self.inline_message_id,
                user_id=user_id,
                score=score,
                force=force,
                disable_edit_message=disable_edit_message,
                timeout=timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return self.message.set_game_score(
            user_id=user_id,
            score=score,
            force=force,
            disable_edit_message=disable_edit_message,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def get_game_high_scores(
        self,
        user_id: Union[int, str],
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> List['GameHighScore']:
        """Shortcut for either::

            update.callback_query.message.get_game_high_score(*args, **kwargs)

        or::

            bot.get_game_high_scores(inline_message_id=update.callback_query.inline_message_id,
                                     *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_game_high_scores`.

        Returns:
            List[:class:`telegram.GameHighScore`]

        """
        if self.inline_message_id:
            return self.bot.get_game_high_scores(
                inline_message_id=self.inline_message_id,
                user_id=user_id,
                timeout=timeout,
                api_kwargs=api_kwargs,
                chat_id=None,
                message_id=None,
            )
        return self.message.get_game_high_scores(
            user_id=user_id,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def delete_message(
        self,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            update.callback_query.message.delete(*args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.delete_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.message.delete(
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def pin_message(
        self,
        disable_notification: bool = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             bot.pin_chat_message(chat_id=message.chat_id,
                                  message_id=message.message_id,
                                  *args,
                                  **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.pin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.message.pin(
            disable_notification=disable_notification,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def unpin_message(
        self,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             bot.unpin_chat_message(chat_id=message.chat_id,
                                    message_id=message.message_id,
                                    *args,
                                    **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.message.unpin(
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def copy_message(
        self,
        chat_id: Union[int, str],
        caption: str = None,
        parse_mode: str = None,
        caption_entities: Union[Tuple['MessageEntity', ...], List['MessageEntity']] = None,
        disable_notification: bool = False,
        reply_to_message_id: Union[int, str] = None,
        allow_sending_without_reply: bool = False,
        reply_markup: ReplyMarkup = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> 'MessageId':
        """Shortcut for::

            update.callback_query.message.copy(
                chat_id,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id,
                *args,
                **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.copy_message`.

        Returns:
            :class:`telegram.MessageId`: On success, returns the MessageId of the sent message.

        """
        return self.message.copy(
            chat_id=chat_id,
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

    MAX_ANSWER_TEXT_LENGTH: ClassVar[int] = constants.MAX_ANSWER_CALLBACK_QUERY_TEXT_LENGTH
    """
    :const:`telegram.constants.MAX_ANSWER_CALLBACK_QUERY_TEXT_LENGTH`

    .. versionadded:: 13.2
    """
