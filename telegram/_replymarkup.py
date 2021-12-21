#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
"""Base class for Telegram ReplyMarkup Objects."""
from telegram import TelegramObject


class ReplyMarkup(TelegramObject):
    """Base class for Telegram ReplyMarkup Objects.

    See :class:`telegram.InlineKeyboardMarkup`, :class:`telegram.ReplyKeyboardMarkup`,
    :class:`telegram.ReplyKeyboardRemove` and :class:`telegram.ForceReply` for
    detailed use.

    .. seealso:: :attr:`telegram.Message.reply_markup`

        :attr:`telegram.InlineQueryResultAudio.reply_markup`

        :attr:`telegram.InlineQueryResultCachedAudio.reply_markup`

        :attr:`telegram.InlineQueryResultDocument.reply_markup`

        :attr:`telegram.InlineQueryResultCachedDocument.reply_markup`

        :attr:`telegram.InlineQueryResultGif.reply_markup`

        :attr:`telegram.InlineQueryResultCachedGif.reply_markup`

        :attr:`telegram.InlineQueryResultMpeg4Gif.reply_markup`

        :attr:`telegram.InlineQueryResultCachedMpeg4Gif.reply_markup`

        :attr:`telegram.InlineQueryResultPhoto.reply_markup`

        :attr:`telegram.InlineQueryResultCachedPhoto.reply_markup`

        :attr:`telegram.InlineQueryResultVideo.reply_markup`

        :attr:`telegram.InlineQueryResultCachedVideo.reply_markup`

        :attr:`telegram.InlineQueryResultVoice.reply_markup`

        :attr:`telegram.InlineQueryResultCachedVoice.reply_markup`

        :attr:`telegram.InlineQueryResultSticker.reply_markup`

        :attr:`telegram.InlineQueryResultContact.reply_markup`

        :attr:`telegram.InlineQueryResultGame.reply_markup`

        :attr:`telegram.InlineQueryResultLocation.reply_markup`

        :attr:`telegram.InlineQueryResultVenue.reply_markup`

        :attr:`telegram.InlineQueryResultArticle.reply_markup`

    """

    __slots__ = ()

    @staticmethod
    def _check_keyboard_type(keyboard: object) -> bool:
        """Checks if the keyboard provided is of the correct type - A list of lists."""
        if not isinstance(keyboard, list):
            return False
        for row in keyboard:
            if not isinstance(row, list):
                return False
        return True
