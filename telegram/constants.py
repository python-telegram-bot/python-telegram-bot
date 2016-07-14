# python-telegram-bot - a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
# by the python-telegram-bot contributors <devs@python-telegram-bot.org>
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
"""Constants in the Telegram network."""

# https://core.telegram.org/method/messages.sendMessage
MAX_MESSAGE_LENGTH = 4096

# https://core.telegram.org/bots/api#sendphoto
MAX_CAPTION_LENGTH = 200

# constants above this line are tested

MAX_MESSAGES_PER_SECOND = 30
MAX_MESSAGES_PER_SECOND_PER_CHAT = 1
MAX_MESSAGES_PER_MINUTE_PER_GROUP = 20

MAX_FILESIZE_UPLOAD = 50E6  # (50MB)
MAX_FILESIZE_DOWNLOAD = 20E6  # (20MB)

SUPPORTED_WEBHOOK_PORTS = [443, 80, 88, 8443]
