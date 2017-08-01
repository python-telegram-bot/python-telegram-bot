"""Helper for migrating to pytests

Run it like::

    python pytest_migration.py test_forcereply.py
"""

import re
import sys
from pathlib import Path

header = """#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/]."""

CLASS = r'class (.*)Test\(BaseTest, unittest.TestCase\):(?:\r?\n)([\s\S]*)if __name__'
JSON_DICT = r'self.json_dict = (\{[\s\S]*\})([\s\S]*?def)'
CLASS_VARS = r'    def setUp\(self\):\n([\s\S]*?def)'

if __name__ == '__main__':
    original = Path('tests/' + sys.argv[1]).open('r', encoding='UTF-8').read()
    new_text = header
    new_text += '\nimport json\n\nimport pytest\n\n'

    match = re.search(CLASS, original)
    if not match:
        match = re.search(CLASS[:-11], original)

    name = match.group(1)
    test_name = 'Test' + name

    new_class = 'class {}:\n{}'.format(test_name, match.group(2))

    imports = {name}
    for find in re.finditer('telegram\.([^().]*)', new_class):
        imports.add(find.group(1))
    tg_imports = ', '.join(imports)
    new_text += 'from telegram import {}{}{}\n\n'.format('(' if len(tg_imports) > 77 else '',
                                                         tg_imports,
                                                         ')' if len(tg_imports) > 77 else '')

    new_class = re.sub(r'telegram\.', '', new_class)
    new_class = re.sub(r'self\.assertTrue\(isinstance\((.*), (.*)\)\)',
                       r'assert isinstance(\1, \2)', new_class)
    new_class = re.sub(r'self\.assertTrue\(self\.is_json\((.*)\)\)', r'json.loads(\1)', new_class)
    new_class = re.sub(r'self\.assertTrue\(self\.is_dict\((.*)\)\)',
                       r'assert isinstance(\1, dict)', new_class)
    new_class = re.sub(r'self\.assert(True|False)\((.*)\)', r'assert \2 is \1', new_class)
    new_class = re.sub(r'self\.assertIsNone\((.*)\)', r'assert \1 is None', new_class)
    new_class = re.sub(r'self\.assertIsInstance\((.*), (.*)\)',
                       r'assert isinstance(\1, \2)', new_class)
    new_class = re.sub(r'self\.assert(?:Dict)?Equals?\((.*), (.*)\)',
                       r'assert \1 == \2', new_class)
    new_class = re.sub(r'self\.assertNotEquals?\((.*), (.*)\)', r'assert \1 != \2', new_class)
    new_class = re.sub(r'self\.assertIs\((.*), (.*)\)', r'assert \1 is \2', new_class)
    new_class = re.sub(r'self\.assertIsNot\((.*), (.*)\)', r'assert \1 is not \2', new_class)
    new_class = re.sub(r'self\._bot', r'bot', new_class)
    new_class = re.sub(r'self\._chat_id,', r'chat_id', new_class)
    new_class = re.sub(r'self\._id', 'self.id', new_class)

    new_class = re.sub(r'def test_.*_(de|to)_(json|dict)\(self\):',
                       r'def test_\1_\2(self):', new_class)

    name_lower = name.lower()
    proper_name_lower = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    proper_name_lower = re.sub('([a-z0-9])([A-Z])', r'\1_\2', proper_name_lower).lower()
    new_class.replace(name_lower, proper_name_lower)

    json_dict = re.search(JSON_DICT, new_class)
    if json_dict:
        new_class = re.sub(JSON_DICT, r'\2', new_class)
        new_text += '@pytest.fixture(scope=\'class\')\ndef json_dict():\n    return '
        new_text += json_dict.group(1).replace('self.', test_name + '.')
        new_text += '\n\n'
        new_text += '@pytest.fixture(scope=\'class\')\ndef {}():\n'.format(proper_name_lower)
        args = []
        for line in json_dict.group(1).replace('self.', test_name + '.').split(','):
            match = re.search(r'\'(.*)\': (.*?\.[^,\s.]*)', line)
            if match:
                args.append('{}={}'.format(match.group(1), match.group(2)))
        new_text += '   return {}({})\n\n'.format(name, ', '.join(args))

    class_vars = re.search(CLASS_VARS, new_class)
    if class_vars:
        class_vars = class_vars.group(1)
        class_vars = class_vars.replace('    ', '')
        class_vars = class_vars.replace('self.', '')
        class_vars = '\n'.join(['    ' + x for x in class_vars.split('\n')])
        new_class = re.sub(CLASS_VARS, class_vars, new_class)

    new_class = re.sub(r'self.json_dict', r'json_dict', new_class)

    new_text += new_class
    new_file = Path('pytests/' + sys.argv[1]).open('w', encoding='UTF-8').write(new_text)
