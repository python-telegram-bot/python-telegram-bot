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
import inspect
import os
from typing import List

import httpx
import pytest
from bs4 import BeautifulSoup

import telegram
from tests.conftest import env_var_2_bool

IGNORED_OBJECTS = ('ResponseParameters', 'CallbackGame')
IGNORED_PARAMETERS = {
    'self',
    'args',
    '_kwargs',
    'read_timeout',
    'write_timeout',
    'connect_timeout',
    'pool_timeout',
    'bot',
    'api_kwargs',
    'kwargs',
}

ignored_param_requirements = {  # Ignore these since there's convenience params in them (eg. Venue)
    'send_location': {'latitude', 'longitude'},
    'edit_message_live_location': {'latitude', 'longitude'},
    'send_venue': {'latitude', 'longitude', 'title', 'address'},
    'send_contact': {'phone_number', 'first_name'},
}


def find_next_sibling_until(tag, name, until):
    for sibling in tag.next_siblings:
        if sibling is until:
            return
        if sibling.name == name:
            return sibling


def parse_table(h4) -> List[List[str]]:
    """Parses the Telegram doc table and has an output of a 2D list."""
    table = find_next_sibling_until(h4, 'table', h4.find_next_sibling('h4'))
    if not table:
        return []
    t = []
    for tr in table.find_all('tr')[1:]:
        t.append([td.text for td in tr.find_all('td')])
    return t


def check_method(h4):
    name = h4.text  # name of the method in telegram's docs.
    method = getattr(telegram.Bot, name)  # Retrieve our lib method
    table = parse_table(h4)

    # Check arguments based on source
    sig = inspect.signature(method, follow_wrapped=True)

    checked = []
    for parameter in table:
        param = sig.parameters.get(parameter[0])
        assert param is not None, f"Parameter {parameter[0]} not found in {method.__name__}"

        # TODO: Check type via docstring
        assert check_required_param(
            parameter, param.name, sig, method.__name__
        ), f'Param {param.name!r} of method {method.__name__!r} requirement mismatch!'
        checked.append(parameter[0])

    ignored = IGNORED_PARAMETERS.copy()
    if name == 'getUpdates':
        ignored -= {'timeout'}  # Has it's own timeout parameter that we do wanna check for
    elif name in (
        f'send{media_type}'
        for media_type in [
            'Animation',
            'Audio',
            'Document',
            'Photo',
            'Video',
            'VideoNote',
            'Voice',
        ]
    ):
        ignored |= {'filename'}  # Convenience parameter
    elif name == 'sendContact':
        ignored |= {'contact'}  # Added for ease of use
    elif name in ['sendLocation', 'editMessageLiveLocation']:
        ignored |= {'location'}  # Added for ease of use
    elif name == 'sendVenue':
        ignored |= {'venue'}  # Added for ease of use
    elif name == 'answerInlineQuery':
        ignored |= {'current_offset'}  # Added for ease of use

    assert (sig.parameters.keys() ^ checked) - ignored == set()


def check_object(h4):
    name = h4.text
    obj = getattr(telegram, name)
    table = parse_table(h4)

    # Check arguments based on source. Makes sure to only check __init__'s signature & nothing else
    sig = inspect.signature(obj.__init__, follow_wrapped=True)

    checked = set()
    for parameter in table:
        field = parameter[0]
        if field == 'from':
            field = 'from_user'
        elif (
            name.startswith('InlineQueryResult')
            or name.startswith('InputMedia')
            or name.startswith('BotCommandScope')
            or name.startswith('MenuButton')
        ) and field == 'type':
            continue
        elif (name.startswith('ChatMember')) and field == 'status':  # We autofill the status
            continue
        elif (
            name.startswith('PassportElementError') and field == 'source'
        ) or field == 'remove_keyboard':
            continue
        elif name.startswith('ForceReply') and field == 'force_reply':  # this param is always True
            continue

        param = sig.parameters.get(field)
        assert param is not None, f"Attribute {field} not found in {obj.__name__}"
        # TODO: Check type via docstring
        assert check_required_param(
            parameter, field, sig, obj.__name__
        ), f"{obj.__name__!r} parameter {param.name!r} requirement mismatch"
        checked.add(field)

    ignored = IGNORED_PARAMETERS.copy()
    if name == 'InputFile':
        return
    if name == 'InlineQueryResult':
        ignored |= {'id', 'type'}  # attributes common to all subclasses
    if name == 'ChatMember':
        ignored |= {'user', 'status'}  # attributes common to all subclasses
    if name == 'BotCommandScope':
        ignored |= {'type'}  # attributes common to all subclasses
    if name == 'MenuButton':
        ignored |= {'type'}  # attributes common to all subclasses
    elif name in ('PassportFile', 'EncryptedPassportElement'):
        ignored |= {'credentials'}
    elif name == 'PassportElementError':
        ignored |= {'message', 'type', 'source'}
    elif name == 'InputMedia':
        ignored |= {'caption', 'caption_entities', 'media', 'media_type', 'parse_mode'}
    elif name.startswith('InputMedia'):
        ignored |= {'filename'}  # Convenience parameter

    assert (sig.parameters.keys() ^ checked) - ignored == set()


def check_required_param(
    param_desc: List[str], param_name: str, sig: inspect.Signature, method_or_obj_name: str
) -> bool:
    """Checks if the method/class parameter is a required/optional param as per Telegram docs."""
    if len(param_desc) == 4:  # this means that there is a dedicated 'Required' column present.
        # Handle cases where we provide convenience intentionally-
        if param_name in ignored_param_requirements.get(method_or_obj_name, {}):
            return True
        is_required = True if param_desc[2] in {'Required', 'Yes'} else False
        is_ours_required = sig.parameters[param_name].default is inspect.Signature.empty
        return is_required is is_ours_required

    if len(param_desc) == 3:  # The docs mention the requirement in the description for classes...
        if param_name in ignored_param_requirements.get(method_or_obj_name, {}):
            return True
        is_required = False if param_desc[2].split('.', 1)[0] == 'Optional' else True
        is_ours_required = sig.parameters[param_name].default is inspect.Signature.empty
        return is_required is is_ours_required


argvalues = []
names = []
request = httpx.get('https://core.telegram.org/bots/api')
soup = BeautifulSoup(request.text, 'html.parser')

for thing in soup.select('h4 > a.anchor'):
    # Methods and types don't have spaces in them, luckily all other sections of the docs do
    # TODO: don't depend on that
    if '-' not in thing['name']:
        h4 = thing.parent

        # Is it a method
        if h4.text[0].lower() == h4.text[0]:
            argvalues.append((check_method, h4))
            names.append(h4.text)
        elif h4.text not in IGNORED_OBJECTS:  # Or a type/object
            argvalues.append((check_object, h4))
            names.append(h4.text)


@pytest.mark.parametrize(('method', 'data'), argvalues=argvalues, ids=names)
@pytest.mark.skipif(
    not env_var_2_bool(os.getenv('TEST_OFFICIAL')), reason='test_official is not enabled'
)
def test_official(method, data):
    method(data)
