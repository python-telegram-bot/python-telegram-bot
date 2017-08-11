import time
from collections import defaultdict

import _pytest.config
import pytest

fold_plugins = {'_cov': 'Coverage report', 'flaky': 'Flaky report'}


def terminal_summary_wrapper(original, plugin_name):
    text = fold_plugins[plugin_name]

    def pytest_terminal_summary(terminalreporter):
        terminalreporter.write('travis_fold:start:plugin.{}\n{}\n'.format(plugin_name, text))
        original(terminalreporter)
        terminalreporter.write('travis_fold:end:plugin.{}\n'.format(plugin_name))

    return pytest_terminal_summary


@pytest.mark.trylast
def pytest_configure(config):
    for hookimpl in config.pluginmanager.hook.pytest_terminal_summary._nonwrappers:
        if hookimpl.plugin_name in fold_plugins.keys():
            hookimpl.function = terminal_summary_wrapper(hookimpl.function,
                                                         hookimpl.plugin_name)


terminal = None
previous_name = None
failed = set()
durations = defaultdict(int)


def _get_name(location):
    return '{}::{}'.format(location[0], location[2].split('.')[0].split('[')[0])


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    name = _get_name(item.location)
    durations[name] += rep.duration
    if rep.failed:
        global failed
        failed.add(name)


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
        terminal.write('\ntravis_fold:start:{}\r'.format(name.split('::')[1]))
        terminal.write('travis_time:start:{}time\r'.format(name.split('::')[1]))
        terminal.write(name)

    yield

    if nextitem is None or _get_name(nextitem.location) != name:
        global failed
        if name in failed:
            terminal.write('')
        else:
            terminal.write('\n\ntravis_fold:end:{}'.format(name.split('::')[1]))
        terminal.write('\rtravis_time:end:{}time:'
                       'duration={}'.format(name.split('::')[1],
                                            int(durations[name] * 1E9)))
        time.sleep(0.001)  # Tiny sleep so travis hopefully doesn't mangle the log
