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
import _pytest.config
import pytest

fold_plugins = {'_cov': 'Coverage report', 'flaky': 'Flaky report'}


def terminal_summary_wrapper(original, plugin_name):
    text = fold_plugins[plugin_name]

    def pytest_terminal_summary(terminalreporter):
        terminalreporter.write('##[group] {}\n'.format(text))
        original(terminalreporter)
        terminalreporter.write('##[endgroup]')

    return pytest_terminal_summary


@pytest.mark.trylast
def pytest_configure(config):
    for hookimpl in config.pluginmanager.hook.pytest_terminal_summary._nonwrappers:
        if hookimpl.plugin_name in fold_plugins.keys():
            hookimpl.function = terminal_summary_wrapper(hookimpl.function,
                                                         hookimpl.plugin_name)


terminal = None
previous_name = None


def _get_name(location):
    if location[0].startswith('tests/'):
        return location[0][6:]
    return location[0]


@pytest.mark.trylast
def pytest_itemcollected(item):
    item._nodeid = item._nodeid.split('::', 1)[1]


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    # This is naughty but pytests' own plugins does something similar too, so who cares
    global terminal
    if terminal is None:
        terminal = _pytest.config.create_terminal_writer(item.config)

    global previous_name

    name = _get_name(item.location)

    if previous_name is None or previous_name != name:
        previous_name = name
        terminal.write('\n##[group] {}'.format(name))

    yield

    if nextitem is None or _get_name(nextitem.location) != name:
        terminal.write('\n##[endgroup]')
