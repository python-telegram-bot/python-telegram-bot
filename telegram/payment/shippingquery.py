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
"""This module contains an object that represents a Telegram ShippingQuery."""

from typing import TYPE_CHECKING, Any, Optional, List

from telegram import ShippingAddress, TelegramObject, User, ShippingOption
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import JSONDict, ODVInput

if TYPE_CHECKING:
    from telegram import Bot


class ShippingQuery(TelegramObject):
    """This object contains information about an incoming shipping query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Note:
        In Python ``from`` is a reserved word, use ``from_user`` instead.

    Args:
        id (:obj:`str`): Unique query identifier.
        from_user (:class:`telegram.User`): User who sent the query.
        invoice_payload (:obj:`str`): Bot specified invoice payload.
        shipping_address (:class:`telegram.ShippingAddress`): User specified shipping address.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        id (:obj:`str`): Unique query identifier.
        from_user (:class:`telegram.User`): User who sent the query.
        invoice_payload (:obj:`str`): Bot specified invoice payload.
        shipping_address (:class:`telegram.ShippingAddress`): User specified shipping address.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    """

    __slots__ = ('bot', 'invoice_payload', 'shipping_address', 'id', 'from_user', '_id_attrs')

    def __init__(
        self,
        id: str,  # pylint: disable=W0622
        from_user: User,
        invoice_payload: str,
        shipping_address: ShippingAddress,
        bot: 'Bot' = None,
        **_kwargs: Any,
    ):
        self.id = id  # pylint: disable=C0103
        self.from_user = from_user
        self.invoice_payload = invoice_payload
        self.shipping_address = shipping_address

        self.bot = bot

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['ShippingQuery']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['from_user'] = User.de_json(data.pop('from'), bot)
        data['shipping_address'] = ShippingAddress.de_json(data.get('shipping_address'), bot)

        return cls(bot=bot, **data)

    def answer(  # pylint: disable=C0103
        self,
        ok: bool,
        shipping_options: List[ShippingOption] = None,
        error_message: str = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            bot.answer_shipping_query(update.shipping_query.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.answer_shipping_query`.

        """
        return self.bot.answer_shipping_query(
            shipping_query_id=self.id,
            ok=ok,
            shipping_options=shipping_options,
            error_message=error_message,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )
