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

if __name__ == '__main__':
    original = Path('tests/' + sys.argv[1]).open('r', encoding='UTF-8').read()
    new_text = header
    new_text += '\nimport pytest\n\nfrom telegram import\n\n'
    match = re.search(CLASS, original)
    if not match:
        match = re.search(CLASS[:-11], original)
    new_text += 'class {}Test:\n{}'.format(match.group(1), match.group(2))
    new_text = re.sub(r'telegram\.', '', new_text)
    new_text = re.sub(r'self\.assertTrue\(self\.is_json\((.*)\)\)', r'json.loads(\1)', new_text)
    new_text = re.sub(r'self.assert(True|False)\((.*)\)', r'assert \2 is \1', new_text)
    new_text = re.sub(r'self.assertEqual\((.*), (.*)\)', r'assert \1 == \2', new_text)
    new_file = Path('pytests/' + sys.argv[1]).open('w', encoding='UTF-8').write(new_text)
