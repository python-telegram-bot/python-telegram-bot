import sys
import inspect
import warnings
from collections import namedtuple

import certifi
import logging
from bs4 import BeautifulSoup

sys.path.append('.')

from telegram.vendor.ptb_urllib3 import urllib3
import telegram

IGNORED_OBJECTS = ('ResponseParameters', 'CallbackGame')
IGNORED_PARAMETERS = {'self', 'args', 'kwargs', 'read_latency', 'network_delay', 'timeout', 'bot'}

logger = logging.getLogger(__name__)


def find_next_sibling_until(tag, name, until):
    for sibling in tag.next_siblings:
        if sibling is until:
            return
        if sibling.name == name:
            return sibling


def parse_table(h4):
    table = find_next_sibling_until(h4, 'table', h4.find_next_sibling('h4'))
    if not table:
        return []
    head = [td.text for td in table.tr.find_all('td')]
    row = namedtuple('{}TableRow'.format(h4.text), ','.join(head))
    t = []
    for tr in table.find_all('tr')[1:]:
        t.append(row(*[td.text for td in tr.find_all('td')]))
    return t


def check_method(h4):
    name = h4.text
    method = getattr(telegram.Bot, name)
    table = parse_table(h4)

    # Check arguments based on source
    sig = inspect.signature(method, follow_wrapped=True)

    checked = []
    for parameter in table:
        param = sig.parameters.get(parameter.Parameters)
        logger.debug(parameter)
        assert param is not None
        # TODO: Check type via docstring
        # TODO: Check if optional or required
        checked.append(parameter.Parameters)

    ignored = IGNORED_PARAMETERS.copy()
    if name == 'getUpdates':
        ignored -= {'timeout'}  # Has it's own timeout parameter that we do wanna check for
    elif name == 'sendDocument':
        ignored |= {'filename'}  # Undocumented
    elif name == 'setGameScore':
        ignored |= {'edit_message'}  # TODO: Now deprecated, so no longer in telegrams docs

    logger.debug((sig.parameters.keys(), checked, ignored,
                 sig.parameters.keys() - checked - ignored))
    assert (sig.parameters.keys() ^ checked) - ignored == set()


def check_object(h4):
    name = h4.text
    obj = getattr(telegram, name)
    table = parse_table(h4)

    # Check arguments based on source
    sig = inspect.signature(obj, follow_wrapped=True)

    checked = []
    for parameter in table:
        field = parameter.Field
        if field == 'from':
            field = 'from_user'
        elif name.startswith('InlineQueryResult') and field == 'type':
            continue
        elif field == 'remove_keyboard':
            continue

        param = sig.parameters.get(field)
        logger.debug(parameter)
        assert param is not None
        # TODO: Check type via docstring
        # TODO: Check if optional or required
        checked.append(field)

    ignored = IGNORED_PARAMETERS.copy()
    if name == 'InputFile':
        ignored |= {'data'}
    elif name == 'InlineQueryResult':
        ignored |= {'id'}
    elif name == 'User':
        ignored |= {'type'}  # TODO: Deprecation

    if name.startswith('InlineQueryResult'):
        ignored |= {'type'}

    logger.debug((sig.parameters.keys(), checked, ignored,
                 sig.parameters.keys() - checked - ignored))
    assert (sig.parameters.keys() ^ checked) - ignored == set()


def test_official():
    if not sys.version_info >= (3, 5):
        warnings.warn('Not running tests, since follow_wrapped is not supported on this platform'
                      '(python version >= 3.5 required)')
        return

    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())
    request = http.request('GET', 'https://core.telegram.org/bots/api')
    soup = BeautifulSoup(request.data.decode('utf-8'), 'html.parser')

    for thing in soup.select('h4 > a.anchor'):
        # Methods and types don't have spaces in them, luckily all other sections of the docs do
        # TODO: don't depend on that
        if '-' not in thing['name']:
            h4 = thing.parent
            name = h4.text

            test = None
            # Is it a method
            if h4.text[0].lower() == h4.text[0]:
                test = check_method
            else:  # Or a type/object
                if name not in IGNORED_OBJECTS:
                    test = check_object

            if test:
                def fn():
                    return test(h4)
                fn.description = '{}({}) ({})'.format(test.__name__, h4.text, __name__)
                yield fn


if __name__ == '__main__':
    # Since we don't have the nice unittest asserts which show the comparison
    # We turn on debugging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
    for f in test_official():
        f()
