#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2024
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
"""Provide a bot to tests"""
import base64
import json
import os
import random

# Provide some public fallbacks so it's easy for contributors to run tests on their local machine
# These bots are only able to talk in our test chats, so they are quite useless for other
# purposes than testing.
FALLBACKS = (
    "W3sidG9rZW4iOiAiNTc5Njk0NzE0OkFBRnBLOHc2emtrVXJENHhTZVl3RjNNTzhlLTRHcm1jeTdjIiwgInBheW1lbnRfc"
    "HJvdmlkZXJfdG9rZW4iOiAiMjg0Njg1MDYzOlRFU1Q6TmpRME5qWmxOekk1WWpKaSIsICJjaGF0X2 lkIjogIjY3NTY2N"
    "jIyNCIsICJzdXBlcl9ncm91cF9pZCI6ICItMTAwMTMxMDkxMTEzNSIsICJmb3J1bV9ncm91cF9pZCI6ICItMTAwMTgzOD"
    "AwNDU3NyIsICJjaGFubmVsX2lkIjogIkBweXRob250ZWxlZ3JhbWJvdHRlc3RzIi wgIm5hbWUiOiAiUFRCIHRlc3RzIG"
    "ZhbGxiYWNrIDEiLCAidXNlcm5hbWUiOiAiQHB0Yl9mYWxsYmFja18xX2JvdCJ9LCB7InRva2VuIjogIjU1ODE5NDA2Njp"
    "BQUZ3RFBJRmx6R1VsQ2FXSHRUT0VYNFJGclg4dTlETXFmbyIsIC JwYXltZW50X3Byb3ZpZGVyX3Rva2VuIjogIjI4NDY"
    "4NTA2MzpURVNUOllqRXdPRFF3TVRGbU5EY3kiLCAiY2hhdF9pZCI6ICI2NzU2NjYyMjQiLCAic3VwZXJfZ3JvdXBfaWQi"
    "OiAiLTEwMDEyMjEyMTY4MzAiLCAiZm9ydW1fZ3 JvdXBfaWQiOiAiLTEwMDE4NTc4NDgzMTQiLCAiY2hhbm5lbF9pZCI6"
    "ICJAcHl0aG9udGVsZWdyYW1ib3R0ZXN0cyIsICJuYW1lIjogIlBUQiB0ZXN0cyBmYWxsYmFjayAyIiwgInVzZXJuYW1lI"
    "jogIkBwdGJfZmFsbGJhY2tfMl9ib3QifV0="
)

GITHUB_ACTION = os.getenv("GITHUB_ACTION", None)
BOTS = os.getenv("BOTS", None)
JOB_INDEX = os.getenv("JOB_INDEX", None)
if GITHUB_ACTION is not None and BOTS is not None and JOB_INDEX is not None:
    BOTS = json.loads(base64.b64decode(BOTS).decode("utf-8"))
    JOB_INDEX = int(JOB_INDEX)

FALLBACKS = json.loads(base64.b64decode(FALLBACKS).decode("utf-8"))  # type: list[dict[str, str]]


class BotInfoProvider:
    def __init__(self):
        self._cached = {}

    @staticmethod
    def _get_value(key, fallback):
        # If we're running as a github action then fetch bots from the repo secrets
        if GITHUB_ACTION is not None and BOTS is not None and JOB_INDEX is not None:
            try:
                return BOTS[JOB_INDEX][key]
            except (IndexError, KeyError):
                pass

        # Otherwise go with the fallback
        return fallback

    def get_info(self):
        if self._cached:
            return self._cached
        self._cached = {k: self._get_value(k, v) for k, v in random.choice(FALLBACKS).items()}
        return self._cached


BOT_INFO_PROVIDER = BotInfoProvider()
