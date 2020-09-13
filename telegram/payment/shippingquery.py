#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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

from telegram import TelegramObject, User, ShippingAddress
from telegram.utils.types import JSONDict
from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import Bot


class ShippingQuery(TelegramObject):
    """This object contains information about an incoming shipping query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        id (:obj:`str`): Unique query identifier.
        from_user (:class:`telegram.User`): User who sent the query.
        invoice_payload (:obj:`str`): Bot specified invoice payload.
        shipping_address (:class:`telegram.ShippingAddress`): User specified shipping address.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    Args:
        id (:obj:`str`): Unique query identifier.
        from_user (:class:`telegram.User`): User who sent the query.
        invoice_payload (:obj:`str`): Bot specified invoice payload.
        shipping_address (:class:`telegram.ShippingAddress`): User specified shipping address.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id: str,
                 from_user: User,
                 invoice_payload: str,
                 shipping_address: ShippingAddress,
                 bot: 'Bot' = None,
                 **kwargs: Any):
        self.id = id
        self.from_user = from_user
        self.invoice_payload = invoice_payload
        self.shipping_address = shipping_address

        self.bot = bot

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['ShippingQuery']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['from_user'] = User.de_json(data.pop('from'), bot)
        data['shipping_address'] = ShippingAddress.de_json(data.get('shipping_address'), bot)

        return cls(bot=bot, **data)

    def answer(self, *args: Any, **kwargs: Any) -> bool:
        """Shortcut for::

            bot.answer_shipping_query(update.shipping_query.id, *args, **kwargs)

        Args:
            ok (:obj:`bool`): Specify :obj:`True` if delivery to the specified address is
                possible and :obj:`False` if there are any problems
                (for example, if delivery to the specified address is not possible).
            shipping_options (List[:class:`telegram.ShippingOption`], optional): Required if ok is
                :obj:`True`. A JSON-serialized array of available shipping options.
            error_message (:obj:`str`, optional): Required if ok is :obj:`False`. Error message in
                human readable form that explains why it is impossible to complete the order (e.g.
                "Sorry, delivery to your desired address is unavailable'). Telegram will display
                this message to the user.

        """
        return self.bot.answer_shipping_query(self.id, *args, **kwargs)
