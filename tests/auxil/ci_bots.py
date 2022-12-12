#!/usr/bin/env python

#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2022
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
"""Provide a bot to tests"""
import base64
import json
import os
import random

from tests.auxil.envvars import TEST_WITH_OPT_DEPS
from tests.auxil.networking import NonchalantHttpxRequest
from tests.auxil.slots import DictExtBot

# Provide some public fallbacks so it's easy for contributors to run tests on their local machine
# These bots are only able to talk in our test chats, so they are quite useless for other
# purposes than testing.
FALLBACKS = (
    "W3sidG9rZW4iOiAiNTc5Njk0NzE0OkFBRnBLOHc2emtrVXJENHhTZVl3RjNNTzhlLTRHcm1jeTdjIiwgInBheW1lbnRfc"
    "HJvdmlkZXJfdG9rZW4iOiAiMjg0Njg1MDYzOlRFU1Q6TmpRME5qWmxOekk1WWpKaSIsICJjaGF0X2lkIjogIjY3NTY2Nj"
    "IyNCIsICJzdXBlcl9ncm91cF9pZCI6ICItMTAwMTMxMDkxMTEzNSIsICJmb3J1bV9ncm91cF9pZCI6ICItMTAwMTYxOTE"
    "1OTQwNCIsICJjaGFubmVsX2lkIjogIkBweXRob250ZWxlZ3JhbWJvdHRlc3RzIiwgImJvdF9uYW1lIjogIlBUQiB0ZXN0"
    "cyBmYWxsYmFjayAxIiwgImJvdF91c2VybmFtZSI6ICJAcHRiX2ZhbGxiYWNrXzFfYm90In0sIHsidG9rZW4iOiAiNTU4M"
    "Tk0MDY2OkFBRndEUElGbHpHVWxDYVdIdFRPRVg0UkZyWDh1OURNcWZvIiwgInBheW1lbnRfcHJvdmlkZXJfdG9rZW4iOi"
    "AiMjg0Njg1MDYzOlRFU1Q6WWpFd09EUXdNVEZtTkRjeSIsICJjaGF0X2lkIjogIjY3NTY2NjIyNCIsICJzdXBlcl9ncm9"
    "1cF9pZCI6ICItMTAwMTIyMTIxNjgzMCIsICJmb3J1bV9ncm91cF9pZCI6ICItMTAwMTYxOTE1OTQwNCIsICJjaGFubmVs"
    "X2lkIjogIkBweXRob250ZWxlZ3JhbWJvdHRlc3RzIiwgImJvdF9uYW1lIjogIlBUQiB0ZXN0cyBmYWxsYmFjayAyIiwgI"
    "mJvdF91c2VybmFtZSI6ICJAcHRiX2ZhbGxiYWNrXzJfYm90In1d "
)

GITHUB_ACTION = os.getenv("GITHUB_ACTION", None)
BOTS = os.getenv("BOTS", None)
JOB_INDEX = os.getenv("JOB_INDEX", None)
if GITHUB_ACTION is not None and BOTS is not None and JOB_INDEX is not None:
    BOTS = json.loads(base64.b64decode(BOTS).decode("utf-8"))
    JOB_INDEX = int(JOB_INDEX)

FALLBACKS = json.loads(base64.b64decode(FALLBACKS).decode("utf-8"))

# THIS KEY IS OBVIOUSLY COMPROMISED
# DO NOT USE IN PRODUCTION!
PRIVATE_KEY = b"-----BEGIN RSA PRIVATE KEY-----\r\nMIIEowIBAAKCAQEA0AvEbNaOnfIL3GjB8VI4M5IaWe+GcK8eSPHkLkXREIsaddum\r\nwPBm/+w8lFYdnY+O06OEJrsaDtwGdU//8cbGJ/H/9cJH3dh0tNbfszP7nTrQD+88\r\nydlcYHzClaG8G+oTe9uEZSVdDXj5IUqR0y6rDXXb9tC9l+oSz+ShYg6+C4grAb3E\r\nSTv5khZ9Zsi/JEPWStqNdpoNuRh7qEYc3t4B/a5BH7bsQENyJSc8AWrfv+drPAEe\r\njQ8xm1ygzWvJp8yZPwOIYuL+obtANcoVT2G2150Wy6qLC0bD88Bm40GqLbSazueC\r\nRHZRug0B9rMUKvKc4FhG4AlNzBCaKgIcCWEqKwIDAQABAoIBACcIjin9d3Sa3S7V\r\nWM32JyVF3DvTfN3XfU8iUzV7U+ZOswA53eeFM04A/Ly4C4ZsUNfUbg72O8Vd8rg/\r\n8j1ilfsYpHVvphwxaHQlfIMa1bKCPlc/A6C7b2GLBtccKTbzjARJA2YWxIaqk9Nz\r\nMjj1IJK98i80qt29xRnMQ5sqOO3gn2SxTErvNchtBiwOH8NirqERXig8VCY6fr3n\r\nz7ZImPU3G/4qpD0+9ULrt9x/VkjqVvNdK1l7CyAuve3D7ha3jPMfVHFtVH5gqbyp\r\nKotyIHAyD+Ex3FQ1JV+H7DkP0cPctQiss7OiO9Zd9C1G2OrfQz9el7ewAPqOmZtC\r\nKjB3hUECgYEA/4MfKa1cvaCqzd3yUprp1JhvssVkhM1HyucIxB5xmBcVLX2/Kdhn\r\nhiDApZXARK0O9IRpFF6QVeMEX7TzFwB6dfkyIePsGxputA5SPbtBlHOvjZa8omMl\r\nEYfNa8x/mJkvSEpzvkWPascuHJWv1cEypqphu/70DxubWB5UKo/8o6cCgYEA0HFy\r\ncgwPMB//nltHGrmaQZPFT7/Qgl9ErZT3G9S8teWY4o4CXnkdU75tBoKAaJnpSfX3\r\nq8VuRerF45AFhqCKhlG4l51oW7TUH50qE3GM+4ivaH5YZB3biwQ9Wqw+QyNLAh/Q\r\nnS4/Wwb8qC9QuyEgcCju5lsCaPEXZiZqtPVxZd0CgYEAshBG31yZjO0zG1TZUwfy\r\nfN3euc8mRgZpSdXIHiS5NSyg7Zr8ZcUSID8jAkJiQ3n3OiAsuq1MGQ6kNa582kLT\r\nFPQdI9Ea8ahyDbkNR0gAY9xbM2kg/Gnro1PorH9PTKE0ekSodKk1UUyNrg4DBAwn\r\nqE6E3ebHXt/2WmqIbUD653ECgYBQCC8EAQNX3AFegPd1GGxU33Lz4tchJ4kMCNU0\r\nN2NZh9VCr3nTYjdTbxsXU8YP44CCKFG2/zAO4kymyiaFAWEOn5P7irGF/JExrjt4\r\nibGy5lFLEq/HiPtBjhgsl1O0nXlwUFzd7OLghXc+8CPUJaz5w42unqT3PBJa40c3\r\nQcIPdQKBgBnSb7BcDAAQ/Qx9juo/RKpvhyeqlnp0GzPSQjvtWi9dQRIu9Pe7luHc\r\nm1Img1EO1OyE3dis/rLaDsAa2AKu1Yx6h85EmNjavBqP9wqmFa0NIQQH8fvzKY3/\r\nP8IHY6009aoamLqYaexvrkHVq7fFKiI6k8myMJ6qblVNFv14+KXU\r\n-----END RSA PRIVATE KEY-----"  # noqa: E501


def get(name, fallback):
    # If we have TOKEN, PAYMENT_PROVIDER_TOKEN, CHAT_ID, SUPER_GROUP_ID,
    # CHANNEL_ID, BOT_NAME, or BOT_USERNAME in the environment, then use that
    val = os.getenv(name.upper())
    if val:
        return val

    # If we're running as a github action then fetch bots from the repo secrets
    if GITHUB_ACTION is not None and BOTS is not None and JOB_INDEX is not None:
        try:
            return BOTS[JOB_INDEX][name]
        except (KeyError, IndexError):
            pass

    # Otherwise go with the fallback
    return fallback


def get_bot():
    return {k: get(k, v) for k, v in random.choice(FALLBACKS).items()}


def make_bot(bot_info=None, **kwargs):
    """
    Tests are executed on tg.ext.ExtBot, as that class only extends the functionality of tg.bot
    """
    token = kwargs.pop("token", (bot_info or {}).get("token"))
    private_key = kwargs.pop("private_key", PRIVATE_KEY)
    kwargs.pop("token", None)
    _bot = DictExtBot(
        token=token,
        private_key=private_key if TEST_WITH_OPT_DEPS else None,
        request=NonchalantHttpxRequest(8),
        get_updates_request=NonchalantHttpxRequest(1),
        **kwargs,
    )
    return _bot
