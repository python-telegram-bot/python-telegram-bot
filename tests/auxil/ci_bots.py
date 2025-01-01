#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2025
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

from telegram._utils.strings import TextEncoding

from .envvars import GITHUB_ACTIONS

# Provide some public fallbacks so it's easy for contributors to run tests on their local machine
# These bots are only able to talk in our test chats, so they are quite useless for other
# purposes than testing.
FALLBACKS = (
    "W3sidG9rZW4iOiAiNTc5Njk0NzE0OkFBRnBLOHc2emtrVXJENHhTZVl3RjNNTzhlLTRHcm1jeTdjIiwgInBheW1lbnRfc"
    "HJvdmlkZXJfdG9rZW4iOiAiMjg0Njg1MDYzOlRFU1Q6TmpRME5qWmxOekk1WWpKaSIsICJjaGF0X2lkIjogIjY3NTY2Nj"
    "IyNCIsICJzdXBlcl9ncm91cF9pZCI6ICItMTAwMTMxMDkxMTEzNSIsICJmb3J1bV9ncm91cF9pZCI6ICItMTAwMTgzODA"
    "wNDU3NyIsICJjaGFubmVsX2lkIjogIkBweXRob250ZWxlZ3JhbWJvdHRlc3RzIiwgIm5hbWUiOiAiUFRCIHRlc3RzIGZh"
    "bGxiYWNrIDEiLCAidXNlcm5hbWUiOiAiQHB0Yl9mYWxsYmFja18xX2JvdCIsICJzdWJzY3JpcHRpb25fY2hhbm5lbF9pZ"
    "CI6IC0xMDAyMjI5NjQ5MzAzfSwgeyJ0b2tlbiI6ICI1NTgxOTQwNjY6QUFGd0RQSUZsekdVbENhV0h0VE9FWDRSRnJYOH"
    "U5RE1xZm8iLCAicGF5bWVudF9wcm92aWRlcl90b2tlbiI6ICIyODQ2ODUwNjM6VEVTVDpZakV3T0RRd01URm1ORGN5Iiw"
    "gImNoYXRfaWQiOiAiNjc1NjY2MjI0IiwgInN1cGVyX2dyb3VwX2lkIjogIi0xMDAxMjIxMjE2ODMwIiwgImZvcnVtX2dy"
    "b3VwX2lkIjogIi0xMDAxODU3ODQ4MzE0IiwgImNoYW5uZWxfaWQiOiAiQHB5dGhvbnRlbGVncmFtYm90dGVzdHMiLCAib"
    "mFtZSI6ICJQVEIgdGVzdHMgZmFsbGJhY2sgMiIsICJ1c2VybmFtZSI6ICJAcHRiX2ZhbGxiYWNrXzJfYm90IiwgInN1Yn"
    "NjcmlwdGlvbl9jaGFubmVsX2lkIjogLTEwMDIyMjk2NDkzMDN9XQ=="
)

BOTS = os.getenv("BOTS", None)
JOB_INDEX = os.getenv("JOB_INDEX", None)
if GITHUB_ACTIONS and BOTS is not None and JOB_INDEX is not None:
    BOTS = json.loads(base64.b64decode(BOTS).decode(TextEncoding.UTF_8))
    JOB_INDEX = int(JOB_INDEX)

FALLBACKS = json.loads(
    base64.b64decode(FALLBACKS).decode(TextEncoding.UTF_8)
)  # type: list[dict[str, str]]


class BotInfoProvider:
    def __init__(self):
        self._cached = {}

    @staticmethod
    def _get_value(key, fallback):
        # If we're running as a github action then fetch bots from the repo secrets
        if GITHUB_ACTIONS and BOTS is not None and JOB_INDEX is not None:
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
