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
# pylint: disable=R0201
"""This module contains the class Defaults, which allows to pass default values to Updater."""
from typing import NoReturn, Optional, Dict, Any

import pytz

from telegram.utils.deprecate import set_new_attribute_deprecated
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import ODVInput


class Defaults:
    """Convenience Class to gather all parameters with a (user defined) default value

    Parameters:
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or URLs in your bot's message.
        disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
            receive a notification with no sound.
        disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in this
            message.
        allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
            should be sent even if the specified replied-to message is not found.
        timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as the
            read timeout from the server (instead of the one specified during creation of the
            connection pool).

            Note:
                Will *not* be used for :meth:`telegram.Bot.get_updates`!
        quote (:obj:`bool`, optional): If set to :obj:`True`, the reply is sent as an actual reply
            to the message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter will
            be ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.
        tzinfo (:obj:`tzinfo`, optional): A timezone to be used for all date(time) inputs
            appearing throughout PTB, i.e. if a timezone naive date(time) object is passed
            somewhere, it will be assumed to be in ``tzinfo``. Must be a timezone provided by the
            ``pytz`` module. Defaults to UTC.
        run_async (:obj:`bool`, optional): Default setting for the ``run_async`` parameter of
            handlers and error handlers registered through :meth:`Dispatcher.add_handler` and
            :meth:`Dispatcher.add_error_handler`. Defaults to :obj:`False`.
    """

    __slots__ = (
        '_timeout',
        '_tzinfo',
        '_disable_web_page_preview',
        '_run_async',
        '_quote',
        '_disable_notification',
        '_allow_sending_without_reply',
        '_parse_mode',
        '_api_defaults',
        '__dict__',
    )

    def __init__(
        self,
        parse_mode: str = None,
        disable_notification: bool = None,
        disable_web_page_preview: bool = None,
        # Timeout needs special treatment, since the bot methods have two different
        # default values for timeout (None and 20s)
        timeout: ODVInput[float] = DEFAULT_NONE,
        quote: bool = None,
        tzinfo: pytz.BaseTzInfo = pytz.utc,
        run_async: bool = False,
        allow_sending_without_reply: bool = None,
    ):
        self._parse_mode = parse_mode
        self._disable_notification = disable_notification
        self._disable_web_page_preview = disable_web_page_preview
        self._allow_sending_without_reply = allow_sending_without_reply
        self._timeout = timeout
        self._quote = quote
        self._tzinfo = tzinfo
        self._run_async = run_async

        # Gather all defaults that actually have a default value
        self._api_defaults = {}
        for kwarg in (
            'parse_mode',
            'explanation_parse_mode',
            'disable_notification',
            'disable_web_page_preview',
            'allow_sending_without_reply',
        ):
            value = getattr(self, kwarg)
            if value not in [None, DEFAULT_NONE]:
                self._api_defaults[kwarg] = value
        # Special casing, as None is a valid default value
        if self._timeout != DEFAULT_NONE:
            self._api_defaults['timeout'] = self._timeout

    def __setattr__(self, key: str, value: object) -> None:
        set_new_attribute_deprecated(self, key, value)

    @property
    def api_defaults(self) -> Dict[str, Any]:  # skip-cq: PY-D0003
        return self._api_defaults

    @property
    def parse_mode(self) -> Optional[str]:
        """:obj:`str`: Optional. Send Markdown or HTML, if you want Telegram apps to show
        bold, italic, fixed-width text or URLs in your bot's message.
        """
        return self._parse_mode

    @parse_mode.setter
    def parse_mode(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to defaults after because it would "
            "not have any effect."
        )

    @property
    def explanation_parse_mode(self) -> Optional[str]:
        """:obj:`str`: Optional. Alias for :attr:`parse_mode`, used for
        the corresponding parameter of :meth:`telegram.Bot.send_poll`.
        """
        return self._parse_mode

    @explanation_parse_mode.setter
    def explanation_parse_mode(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to defaults after because it would "
            "not have any effect."
        )

    @property
    def disable_notification(self) -> Optional[bool]:
        """:obj:`bool`: Optional. Sends the message silently. Users will
        receive a notification with no sound.
        """
        return self._disable_notification

    @disable_notification.setter
    def disable_notification(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to defaults after because it would "
            "not have any effect."
        )

    @property
    def disable_web_page_preview(self) -> Optional[bool]:
        """:obj:`bool`: Optional. Disables link previews for links in this
        message.
        """
        return self._disable_web_page_preview

    @disable_web_page_preview.setter
    def disable_web_page_preview(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to defaults after because it would "
            "not have any effect."
        )

    @property
    def allow_sending_without_reply(self) -> Optional[bool]:
        """:obj:`bool`: Optional. Pass :obj:`True`, if the message
        should be sent even if the specified replied-to message is not found.
        """
        return self._allow_sending_without_reply

    @allow_sending_without_reply.setter
    def allow_sending_without_reply(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to defaults after because it would "
            "not have any effect."
        )

    @property
    def timeout(self) -> ODVInput[float]:
        """:obj:`int` | :obj:`float`: Optional. If this value is specified, use it as the
        read timeout from the server (instead of the one specified during creation of the
        connection pool).
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to defaults after because it would "
            "not have any effect."
        )

    @property
    def quote(self) -> Optional[bool]:
        """:obj:`bool`: Optional. If set to :obj:`True`, the reply is sent as an actual reply
        to the message. If ``reply_to_message_id`` is passed in ``kwargs``, this parameter will
        be ignored. Default: :obj:`True` in group chats and :obj:`False` in private chats.
        """
        return self._quote

    @quote.setter
    def quote(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to defaults after because it would "
            "not have any effect."
        )

    @property
    def tzinfo(self) -> pytz.BaseTzInfo:
        """:obj:`tzinfo`: A timezone to be used for all date(time) objects appearing
        throughout PTB.
        """
        return self._tzinfo

    @tzinfo.setter
    def tzinfo(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to defaults after because it would "
            "not have any effect."
        )

    @property
    def run_async(self) -> bool:
        """:obj:`bool`: Optional. Default setting for the ``run_async`` parameter of
        handlers and error handlers registered through :meth:`Dispatcher.add_handler` and
        :meth:`Dispatcher.add_error_handler`.
        """
        return self._run_async

    @run_async.setter
    def run_async(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to defaults after because it would "
            "not have any effect."
        )

    def __hash__(self) -> int:
        return hash(
            (
                self._parse_mode,
                self._disable_notification,
                self._disable_web_page_preview,
                self._allow_sending_without_reply,
                self._timeout,
                self._quote,
                self._tzinfo,
                self._run_async,
            )
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Defaults):
            return all(getattr(self, attr) == getattr(other, attr) for attr in self.__slots__)
        return False

    def __ne__(self, other: object) -> bool:
        return not self == other
