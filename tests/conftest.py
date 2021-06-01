#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
import datetime
import functools
import inspect

import os
import re
from collections import defaultdict
from queue import Queue
from threading import Thread, Event
from time import sleep
from typing import Callable, List, Iterable, Any

import pytest
import pytz

from telegram import (
    Message,
    User,
    Chat,
    MessageEntity,
    Update,
    InlineQuery,
    CallbackQuery,
    ShippingQuery,
    PreCheckoutQuery,
    ChosenInlineResult,
    File,
    ChatPermissions,
)
from telegram.ext import (
    Dispatcher,
    JobQueue,
    Updater,
    MessageFilter,
    Defaults,
    UpdateFilter,
    ExtBot,
)
from telegram.error import BadRequest
from telegram.utils.helpers import DefaultValue, DEFAULT_NONE
from tests.bots import get_bot


# This is here instead of in setup.cfg due to https://github.com/pytest-dev/pytest/issues/8343
def pytest_runtestloop(session):
    session.add_marker(
        pytest.mark.filterwarnings('ignore::telegram.utils.deprecate.TelegramDeprecationWarning')
    )


GITHUB_ACTION = os.getenv('GITHUB_ACTION', False)

if GITHUB_ACTION:
    pytest_plugins = ['tests.plugin_github_group']

# THIS KEY IS OBVIOUSLY COMPROMISED
# DO NOT USE IN PRODUCTION!
PRIVATE_KEY = b"-----BEGIN RSA PRIVATE KEY-----\r\nMIIEowIBAAKCAQEA0AvEbNaOnfIL3GjB8VI4M5IaWe+GcK8eSPHkLkXREIsaddum\r\nwPBm/+w8lFYdnY+O06OEJrsaDtwGdU//8cbGJ/H/9cJH3dh0tNbfszP7nTrQD+88\r\nydlcYHzClaG8G+oTe9uEZSVdDXj5IUqR0y6rDXXb9tC9l+oSz+ShYg6+C4grAb3E\r\nSTv5khZ9Zsi/JEPWStqNdpoNuRh7qEYc3t4B/a5BH7bsQENyJSc8AWrfv+drPAEe\r\njQ8xm1ygzWvJp8yZPwOIYuL+obtANcoVT2G2150Wy6qLC0bD88Bm40GqLbSazueC\r\nRHZRug0B9rMUKvKc4FhG4AlNzBCaKgIcCWEqKwIDAQABAoIBACcIjin9d3Sa3S7V\r\nWM32JyVF3DvTfN3XfU8iUzV7U+ZOswA53eeFM04A/Ly4C4ZsUNfUbg72O8Vd8rg/\r\n8j1ilfsYpHVvphwxaHQlfIMa1bKCPlc/A6C7b2GLBtccKTbzjARJA2YWxIaqk9Nz\r\nMjj1IJK98i80qt29xRnMQ5sqOO3gn2SxTErvNchtBiwOH8NirqERXig8VCY6fr3n\r\nz7ZImPU3G/4qpD0+9ULrt9x/VkjqVvNdK1l7CyAuve3D7ha3jPMfVHFtVH5gqbyp\r\nKotyIHAyD+Ex3FQ1JV+H7DkP0cPctQiss7OiO9Zd9C1G2OrfQz9el7ewAPqOmZtC\r\nKjB3hUECgYEA/4MfKa1cvaCqzd3yUprp1JhvssVkhM1HyucIxB5xmBcVLX2/Kdhn\r\nhiDApZXARK0O9IRpFF6QVeMEX7TzFwB6dfkyIePsGxputA5SPbtBlHOvjZa8omMl\r\nEYfNa8x/mJkvSEpzvkWPascuHJWv1cEypqphu/70DxubWB5UKo/8o6cCgYEA0HFy\r\ncgwPMB//nltHGrmaQZPFT7/Qgl9ErZT3G9S8teWY4o4CXnkdU75tBoKAaJnpSfX3\r\nq8VuRerF45AFhqCKhlG4l51oW7TUH50qE3GM+4ivaH5YZB3biwQ9Wqw+QyNLAh/Q\r\nnS4/Wwb8qC9QuyEgcCju5lsCaPEXZiZqtPVxZd0CgYEAshBG31yZjO0zG1TZUwfy\r\nfN3euc8mRgZpSdXIHiS5NSyg7Zr8ZcUSID8jAkJiQ3n3OiAsuq1MGQ6kNa582kLT\r\nFPQdI9Ea8ahyDbkNR0gAY9xbM2kg/Gnro1PorH9PTKE0ekSodKk1UUyNrg4DBAwn\r\nqE6E3ebHXt/2WmqIbUD653ECgYBQCC8EAQNX3AFegPd1GGxU33Lz4tchJ4kMCNU0\r\nN2NZh9VCr3nTYjdTbxsXU8YP44CCKFG2/zAO4kymyiaFAWEOn5P7irGF/JExrjt4\r\nibGy5lFLEq/HiPtBjhgsl1O0nXlwUFzd7OLghXc+8CPUJaz5w42unqT3PBJa40c3\r\nQcIPdQKBgBnSb7BcDAAQ/Qx9juo/RKpvhyeqlnp0GzPSQjvtWi9dQRIu9Pe7luHc\r\nm1Img1EO1OyE3dis/rLaDsAa2AKu1Yx6h85EmNjavBqP9wqmFa0NIQQH8fvzKY3/\r\nP8IHY6009aoamLqYaexvrkHVq7fFKiI6k8myMJ6qblVNFv14+KXU\r\n-----END RSA PRIVATE KEY-----"  # noqa: E501


def env_var_2_bool(env_var: object) -> bool:
    if isinstance(env_var, bool):
        return env_var
    if not isinstance(env_var, str):
        return False
    return env_var.lower().strip() == 'true'


@pytest.fixture(scope='session')
def bot_info():
    return get_bot()


@pytest.fixture(scope='session')
def bot(bot_info):
    class DictExtBot(
        ExtBot
    ):  # Subclass Bot to allow monkey patching of attributes and functions, would
        pass  # come into effect when we __dict__ is dropped from slots

    return DictExtBot(bot_info['token'], private_key=PRIVATE_KEY)


DEFAULT_BOTS = {}


@pytest.fixture(scope='function')
def default_bot(request, bot_info):
    param = request.param if hasattr(request, 'param') else {}

    defaults = Defaults(**param)
    default_bot = DEFAULT_BOTS.get(defaults)
    if default_bot:
        return default_bot
    default_bot = make_bot(bot_info, **{'defaults': defaults})
    DEFAULT_BOTS[defaults] = default_bot
    return default_bot


@pytest.fixture(scope='function')
def tz_bot(timezone, bot_info):
    defaults = Defaults(tzinfo=timezone)
    default_bot = DEFAULT_BOTS.get(defaults)
    if default_bot:
        return default_bot
    default_bot = make_bot(bot_info, **{'defaults': defaults})
    DEFAULT_BOTS[defaults] = default_bot
    return default_bot


@pytest.fixture(scope='session')
def chat_id(bot_info):
    return bot_info['chat_id']


@pytest.fixture(scope='session')
def super_group_id(bot_info):
    return bot_info['super_group_id']


@pytest.fixture(scope='session')
def channel_id(bot_info):
    return bot_info['channel_id']


@pytest.fixture(scope='session')
def provider_token(bot_info):
    return bot_info['payment_provider_token']


def create_dp(bot):
    # Dispatcher is heavy to init (due to many threads and such) so we have a single session
    # scoped one here, but before each test, reset it (dp fixture below)
    dispatcher = Dispatcher(bot, Queue(), job_queue=JobQueue(), workers=2, use_context=False)
    dispatcher.job_queue.set_dispatcher(dispatcher)
    thr = Thread(target=dispatcher.start)
    thr.start()
    sleep(2)
    yield dispatcher
    sleep(1)
    if dispatcher.running:
        dispatcher.stop()
    thr.join()


@pytest.fixture(scope='session')
def _dp(bot):
    yield from create_dp(bot)


@pytest.fixture(scope='function')
def dp(_dp):
    # Reset the dispatcher first
    while not _dp.update_queue.empty():
        _dp.update_queue.get(False)
    _dp.chat_data = defaultdict(dict)
    _dp.user_data = defaultdict(dict)
    _dp.bot_data = {}
    _dp.persistence = None
    _dp.handlers = {}
    _dp.groups = []
    _dp.error_handlers = {}
    # For some reason if we setattr with the name mangled, then some tests(like async) run forever,
    # due to threads not acquiring, (blocking). This adds these attributes to the __dict__.
    object.__setattr__(_dp, '__stop_event', Event())
    object.__setattr__(_dp, '__exception_event', Event())
    object.__setattr__(_dp, '__async_queue', Queue())
    object.__setattr__(_dp, '__async_threads', set())
    _dp.persistence = None
    _dp.use_context = False
    if _dp._Dispatcher__singleton_semaphore.acquire(blocking=0):
        Dispatcher._set_singleton(_dp)
    yield _dp
    Dispatcher._Dispatcher__singleton_semaphore.release()


@pytest.fixture(scope='function')
def cdp(dp):
    dp.use_context = True
    yield dp
    dp.use_context = False


@pytest.fixture(scope='function')
def updater(bot):
    up = Updater(bot=bot, workers=2, use_context=False)
    yield up
    if up.running:
        up.stop()


@pytest.fixture(scope='function')
def thumb_file():
    f = open('tests/data/thumb.jpg', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def class_thumb_file():
    f = open('tests/data/thumb.jpg', 'rb')
    yield f
    f.close()


def pytest_configure(config):
    config.addinivalue_line('filterwarnings', 'ignore::ResourceWarning')
    # TODO: Write so good code that we don't need to ignore ResourceWarnings anymore


def make_bot(bot_info, **kwargs):
    """
    Tests are executed on tg.ext.ExtBot, as that class only extends the functionality of tg.bot
    """
    return ExtBot(bot_info['token'], private_key=PRIVATE_KEY, **kwargs)


CMD_PATTERN = re.compile(r'/[\da-z_]{1,32}(?:@\w{1,32})?')
DATE = datetime.datetime.now()


def make_message(text, **kwargs):
    """
    Testing utility factory to create a fake ``telegram.Message`` with
    reasonable defaults for mimicking a real message.
    :param text: (str) message text
    :return: a (fake) ``telegram.Message``
    """
    return Message(
        message_id=1,
        from_user=kwargs.pop('user', User(id=1, first_name='', is_bot=False)),
        date=kwargs.pop('date', DATE),
        chat=kwargs.pop('chat', Chat(id=1, type='')),
        text=text,
        bot=kwargs.pop('bot', make_bot(get_bot())),
        **kwargs,
    )


def make_command_message(text, **kwargs):
    """
    Testing utility factory to create a message containing a single telegram
    command.
    Mimics the Telegram API in that it identifies commands within the message
    and tags the returned ``Message`` object with the appropriate ``MessageEntity``
    tag (but it does this only for commands).

    :param text: (str) message text containing (or not) the command
    :return: a (fake) ``telegram.Message`` containing only the command
    """

    match = re.search(CMD_PATTERN, text)
    entities = (
        [
            MessageEntity(
                type=MessageEntity.BOT_COMMAND, offset=match.start(0), length=len(match.group(0))
            )
        ]
        if match
        else []
    )

    return make_message(text, entities=entities, **kwargs)


def make_message_update(message, message_factory=make_message, edited=False, **kwargs):
    """
    Testing utility factory to create an update from a message, as either a
    ``telegram.Message`` or a string. In the latter case ``message_factory``
    is used to convert ``message`` to a ``telegram.Message``.
    :param message: either a ``telegram.Message`` or a string with the message text
    :param message_factory: function to convert the message text into a ``telegram.Message``
    :param edited: whether the message should be stored as ``edited_message`` (vs. ``message``)
    :return: ``telegram.Update`` with the given message
    """
    if not isinstance(message, Message):
        message = message_factory(message, **kwargs)
    update_kwargs = {'message' if not edited else 'edited_message': message}
    return Update(0, **update_kwargs)


def make_command_update(message, edited=False, **kwargs):
    """
    Testing utility factory to create an update from a message that potentially
    contains a command. See ``make_command_message`` for more details.
    :param message: message potentially containing a command
    :param edited: whether the message should be stored as ``edited_message`` (vs. ``message``)
    :return: ``telegram.Update`` with the given message
    """
    return make_message_update(message, make_command_message, edited, **kwargs)


@pytest.fixture(
    scope='class',
    params=[{'class': MessageFilter}, {'class': UpdateFilter}],
    ids=['MessageFilter', 'UpdateFilter'],
)
def mock_filter(request):
    class MockFilter(request.param['class']):
        def __init__(self):
            self.tested = False

        def filter(self, _):
            self.tested = True

    return MockFilter()


def get_false_update_fixture_decorator_params():
    message = Message(1, DATE, Chat(1, ''), from_user=User(1, '', False), text='test')
    params = [
        {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
        {'channel_post': message},
        {'edited_channel_post': message},
        {'inline_query': InlineQuery(1, User(1, '', False), '', '')},
        {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
        {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
        {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
        {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')},
    ]
    ids = tuple(key for kwargs in params for key in kwargs)
    return {'params': params, 'ids': ids}


@pytest.fixture(scope='function', **get_false_update_fixture_decorator_params())
def false_update(request):
    return Update(update_id=1, **request.param)


@pytest.fixture(params=['Europe/Berlin', 'Asia/Singapore', 'UTC'])
def tzinfo(request):
    return pytz.timezone(request.param)


@pytest.fixture()
def timezone(tzinfo):
    return tzinfo


@pytest.fixture()
def mro_slots():
    def _mro_slots(_class):
        return [
            attr
            for cls in _class.__class__.__mro__[:-1]
            if hasattr(cls, '__slots__')  # ABC doesn't have slots in py 3.7 and below
            for attr in cls.__slots__
            if attr != '__dict__'
        ]

    return _mro_slots


def expect_bad_request(func, message, reason):
    """
    Wrapper for testing bot functions expected to result in an :class:`telegram.error.BadRequest`.
    Makes it XFAIL, if the specified error message is present.

    Args:
        func: The callable to be executed.
        message: The expected message of the bad request error. If another message is present,
            the error will be reraised.
        reason: Explanation for the XFAIL.

    Returns:
        On success, returns the return value of :attr:`func`
    """
    try:
        return func()
    except BadRequest as e:
        if message in str(e):
            pytest.xfail(f'{reason}. {e}')
        else:
            raise e


def check_shortcut_signature(
    shortcut: Callable,
    bot_method: Callable,
    shortcut_kwargs: List[str],
    additional_kwargs: List[str],
) -> bool:
    """
    Checks that the signature of a shortcut matches the signature of the underlying bot method.

    Args:
        shortcut: The shortcut, e.g. :meth:`telegram.Message.reply_text`
        bot_method: The bot method, e.g. :meth:`telegram.Bot.send_message`
        shortcut_kwargs: The kwargs passed by the shortcut directly, e.g. ``chat_id``
        additional_kwargs: Additional kwargs of the shortcut that the bot method doesn't have, e.g.
            ``quote``.

    Returns:
        :obj:`bool`: Whether or not the signature matches.
    """
    shortcut_sig = inspect.signature(shortcut)
    effective_shortcut_args = set(shortcut_sig.parameters.keys()).difference(additional_kwargs)
    effective_shortcut_args.discard('self')

    bot_sig = inspect.signature(bot_method)
    expected_args = set(bot_sig.parameters.keys()).difference(shortcut_kwargs)
    expected_args.discard('self')

    args_check = expected_args == effective_shortcut_args
    if not args_check:
        raise Exception(f'Expected arguments {expected_args}, got {effective_shortcut_args}')

    # TODO: Also check annotation of return type. Would currently be a hassle b/c typing doesn't
    # resolve `ForwardRef('Type')` to `Type`. For now we rely on MyPy, which probably allows the
    # shortcuts to return more specific types than the bot method, but it's only annotations after
    # all
    for kwarg in effective_shortcut_args:
        if bot_sig.parameters[kwarg].annotation != shortcut_sig.parameters[kwarg].annotation:
            if isinstance(bot_sig.parameters[kwarg].annotation, type):
                if bot_sig.parameters[kwarg].annotation.__name__ != str(
                    shortcut_sig.parameters[kwarg].annotation
                ):
                    raise Exception(
                        f'For argument {kwarg} I expected {bot_sig.parameters[kwarg].annotation}, '
                        f'but got {shortcut_sig.parameters[kwarg].annotation}'
                    )
            else:
                raise Exception(
                    f'For argument {kwarg} I expected {bot_sig.parameters[kwarg].annotation}, but '
                    f'got {shortcut_sig.parameters[kwarg].annotation}'
                )

    bot_method_sig = inspect.signature(bot_method)
    shortcut_sig = inspect.signature(shortcut)
    for arg in expected_args:
        if not shortcut_sig.parameters[arg].default == bot_method_sig.parameters[arg].default:
            raise Exception(
                f'Default for argument {arg} does not match the default of the Bot method.'
            )

    return True


def check_shortcut_call(
    shortcut_method: Callable,
    bot: ExtBot,
    bot_method_name: str,
    skip_params: Iterable[str] = None,
    shortcut_kwargs: Iterable[str] = None,
) -> bool:
    """
    Checks that a shortcut passes all the existing arguments to the underlying bot method. Use as::

        assert check_shortcut_call(message.reply_text, message.bot, 'send_message')

    Args:
        shortcut_method: The shortcut method, e.g. `message.reply_text`
        bot: The bot
        bot_method_name: The bot methods name, e.g. `'send_message'`
        skip_params: Parameters that are allowed to be missing, e.g. `['inline_message_id']`
        shortcut_kwargs: The kwargs passed by the shortcut directly, e.g. ``chat_id``

    Returns:
        :obj:`bool`
    """
    if not skip_params:
        skip_params = set()
    if not shortcut_kwargs:
        shortcut_kwargs = set()

    orig_bot_method = getattr(bot, bot_method_name)
    bot_signature = inspect.signature(orig_bot_method)
    expected_args = set(bot_signature.parameters.keys()) - {'self'} - set(skip_params)
    positional_args = {
        name for name, param in bot_signature.parameters.items() if param.default == param.empty
    }
    ignored_args = positional_args | set(shortcut_kwargs)

    shortcut_signature = inspect.signature(shortcut_method)
    # auto_pagination: Special casing for InlineQuery.answer
    kwargs = {name: name for name in shortcut_signature.parameters if name != 'auto_pagination'}

    def make_assertion(**kw):
        # name == value makes sure that
        # a) we receive non-None input for all parameters
        # b) we receive the correct input for each kwarg
        received_kwargs = {
            name for name, value in kw.items() if name in ignored_args or value == name
        }
        if not received_kwargs == expected_args:
            raise Exception(
                f'{orig_bot_method.__name__} did not receive correct value for the parameters '
                f'{expected_args - received_kwargs}'
            )

        if bot_method_name == 'get_file':
            # This is here mainly for PassportFile.get_file, which calls .set_credentials on the
            # return value
            return File(file_id='result', file_unique_id='result')
        return True

    setattr(bot, bot_method_name, make_assertion)
    try:
        shortcut_method(**kwargs)
    except Exception as exc:
        raise exc
    finally:
        setattr(bot, bot_method_name, orig_bot_method)

    return True


def check_defaults_handling(
    method: Callable,
    bot: ExtBot,
    return_value=None,
) -> bool:
    """
    Checks that tg.ext.Defaults are handled correctly.

    Args:
        method: The shortcut/bot_method
        bot: The bot
        return_value: Optional. The return value of Bot._post that the method expects. Defaults to
            None. get_file is automatically handled.

    """

    def build_kwargs(signature: inspect.Signature, default_kwargs, dfv: Any = DEFAULT_NONE):
        kws = {}
        for name, param in signature.parameters.items():
            # For required params we need to pass something
            if param.default == param.empty:
                # Some special casing
                if name == 'permissions':
                    kws[name] = ChatPermissions()
                elif name in ['prices', 'media', 'results', 'commands', 'errors']:
                    kws[name] = []
                elif name == 'ok':
                    kws['ok'] = False
                    kws['error_message'] = 'error'
                else:
                    kws[name] = True
            # pass values for params that can have defaults only if we don't want to use the
            # standard default
            elif name in default_kwargs:
                if dfv != DEFAULT_NONE:
                    kws[name] = dfv
            # Some special casing for methods that have "exactly one of the optionals" type args
            elif name in ['location', 'contact', 'venue', 'inline_message_id']:
                kws[name] = True
        return kws

    shortcut_signature = inspect.signature(method)
    kwargs_need_default = [
        kwarg
        for kwarg, value in shortcut_signature.parameters.items()
        if isinstance(value.default, DefaultValue)
    ]
    # shortcut_signature.parameters['timeout'] is of type DefaultValue
    method_timeout = shortcut_signature.parameters['timeout'].default.value

    default_kwarg_names = kwargs_need_default
    # special case explanation_parse_mode of Bot.send_poll:
    if 'explanation_parse_mode' in default_kwarg_names:
        default_kwarg_names.remove('explanation_parse_mode')

    defaults_no_custom_defaults = Defaults()
    defaults_custom_defaults = Defaults(
        **{kwarg: 'custom_default' for kwarg in default_kwarg_names}
    )

    expected_return_values = [None, []] if return_value is None else [return_value]

    def make_assertion(_, data, timeout=DEFAULT_NONE, df_value=DEFAULT_NONE):
        expected_timeout = method_timeout if df_value == DEFAULT_NONE else df_value
        if timeout != expected_timeout:
            pytest.fail(f'Got value {timeout} for "timeout", expected {expected_timeout}')

        for arg in (dkw for dkw in kwargs_need_default if dkw != 'timeout'):
            # 'None' should not be passed along to Telegram
            if df_value in [None, DEFAULT_NONE]:
                if arg in data:
                    pytest.fail(
                        f'Got value {data[arg]} for argument {arg}, expected it to be absent'
                    )
            else:
                value = data.get(arg, '`not passed at all`')
                if value != df_value:
                    pytest.fail(f'Got value {value} for argument {arg} instead of {df_value}')

        if method.__name__ in ['get_file', 'get_small_file', 'get_big_file']:
            # This is here mainly for PassportFile.get_file, which calls .set_credentials on the
            # return value
            out = File(file_id='result', file_unique_id='result')
            nonlocal expected_return_values
            expected_return_values = [out]
            return out.to_dict()
        # Otherwise return None by default, as TGObject.de_json/list(None) in [None, []]
        # That way we can check what gets passed to Request.post without having to actually
        # make a request
        # Some methods expect specific output, so we allow to customize that
        return return_value

    orig_post = bot.request.post
    try:
        for default_value, defaults in [
            (DEFAULT_NONE, defaults_no_custom_defaults),
            ('custom_default', defaults_custom_defaults),
        ]:
            bot.defaults = defaults
            # 1: test that we get the correct default value, if we don't specify anything
            kwargs = build_kwargs(
                shortcut_signature,
                kwargs_need_default,
            )
            assertion_callback = functools.partial(make_assertion, df_value=default_value)
            setattr(bot.request, 'post', assertion_callback)
            assert method(**kwargs) in expected_return_values

            # 2: test that we get the manually passed non-None value
            kwargs = build_kwargs(shortcut_signature, kwargs_need_default, dfv='non-None-value')
            assertion_callback = functools.partial(make_assertion, df_value='non-None-value')
            setattr(bot.request, 'post', assertion_callback)
            assert method(**kwargs) in expected_return_values

            # 3: test that we get the manually passed None value
            kwargs = build_kwargs(
                shortcut_signature,
                kwargs_need_default,
                dfv=None,
            )
            assertion_callback = functools.partial(make_assertion, df_value=None)
            setattr(bot.request, 'post', assertion_callback)
            assert method(**kwargs) in expected_return_values
    except Exception as exc:
        raise exc
    finally:
        setattr(bot.request, 'post', orig_post)
        bot.defaults = None

    return True
