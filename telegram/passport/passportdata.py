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
"""Contains information about Telegram Passport data shared with the bot by the user."""

from typing import TYPE_CHECKING, Any, List, Optional

from telegram import EncryptedCredentials, EncryptedPassportElement, TelegramObject
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot, Credentials


class PassportData(TelegramObject):
    """Contains information about Telegram Passport data shared with the bot by the user.

    Note:
        To be able to decrypt this object, you must pass your ``private_key`` to either
        :class:`telegram.Updater` or :class:`telegram.Bot`. Decrypted data is then found in
        :attr:`decrypted_data` and the payload can be found in :attr:`decrypted_credentials`'s
        attribute :attr:`telegram.Credentials.payload`.

    Args:
        data (List[:class:`telegram.EncryptedPassportElement`]): Array with encrypted information
            about documents and other Telegram Passport elements that was shared with the bot.
        credentials (:class:`telegram.EncryptedCredentials`)): Encrypted credentials.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        data (List[:class:`telegram.EncryptedPassportElement`]): Array with encrypted information
            about documents and other Telegram Passport elements that was shared with the bot.
        credentials (:class:`telegram.EncryptedCredentials`): Encrypted credentials.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    """

    def __init__(
        self,
        data: List[EncryptedPassportElement],
        credentials: EncryptedCredentials,
        bot: 'Bot' = None,
        **_kwargs: Any,
    ):
        self.data = data
        self.credentials = credentials

        self.bot = bot
        self._decrypted_data: Optional[List[EncryptedPassportElement]] = None
        self._id_attrs = tuple([x.type for x in data] + [credentials.hash])

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['PassportData']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['data'] = EncryptedPassportElement.de_list(data.get('data'), bot)
        data['credentials'] = EncryptedCredentials.de_json(data.get('credentials'), bot)

        return cls(bot=bot, **data)

    def to_dict(self) -> JSONDict:
        data = super().to_dict()

        data['data'] = [e.to_dict() for e in self.data]

        return data

    @property
    def decrypted_data(self) -> List[EncryptedPassportElement]:
        """
        List[:class:`telegram.EncryptedPassportElement`]: Lazily decrypt and return information
            about documents and other Telegram Passport elements which were shared with the bot.

        Raises:
            telegram.TelegramDecryptionError: Decryption failed. Usually due to bad
                private/public key but can also suggest malformed/tampered data.
        """
        if self._decrypted_data is None:
            self._decrypted_data = [
                EncryptedPassportElement.de_json_decrypted(
                    element.to_dict(), self.bot, self.decrypted_credentials
                )
                for element in self.data
            ]
        return self._decrypted_data

    @property
    def decrypted_credentials(self) -> 'Credentials':
        """
        :class:`telegram.Credentials`: Lazily decrypt and return credentials that were used
            to decrypt the data. This object also contains the user specified payload as
            `decrypted_data.payload`.

        Raises:
            telegram.TelegramDecryptionError: Decryption failed. Usually due to bad
                private/public key but can also suggest malformed/tampered data.
        """
        return self.credentials.decrypted_data
