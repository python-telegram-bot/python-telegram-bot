#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains the base class for handlers as used by the Dispatcher."""
import warnings

from telegram.utils.inspection import inspect_arguments


class Handler(object):
    """
    The base class for all update handlers. Create custom handlers by inheriting from it.

    If your subclass needs the *autowiring* functionality, make sure to call
    ``set_autowired_flags`` **after** initializing the ``pass_*`` members. The ``passable``
    argument to this method denotes all the flags your Handler supports, e.g.
    ``{'update_queue', 'job_queue', 'args'}``.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        autowire (:obj:`bool`): Optional. Determines whether objects will be passed to the
            callback function automatically.
        pass_update_queue (:obj:`bool`): Optional. Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Optional. Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Optional. Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Optional. Determines whether ``chat_data`` will be passed to
            the callback function.

    Note:
        :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a ``dict`` you
        can use to keep any data in will be sent to the :attr:`callback` function.. Related to
        either the user or the chat that the update was sent in. For each update from the same user
        or in the same chat, it will be the same ``dict``.

    Args:
        callback (:obj:`callable`): A function that takes ``bot, update`` as positional arguments.
            It will be called when the :attr:`check_update` has determined that an update should be
            processed by this handler.
        autowire (:obj:`bool`, optional): If set to ``True``, your callback handler will be
            inspected for positional arguments and be passed objects whose names match any of the
            ``pass_*`` flags of this Handler. Using any ``pass_*`` argument in conjunction with
            ``autowire`` will yield a warning.
        pass_update_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is ``False``.
        pass_job_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.
        pass_user_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is ``False``.
        pass_chat_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is ``False``.

    """

    PASSABLE_OBJECTS = {'update_queue', 'job_queue', 'user_data', 'chat_data',
                        'args', 'groups', 'groupdict'}

    def __init__(self,
                 callback,
                 autowire=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        self.callback = callback
        self.autowire = autowire
        self.pass_update_queue = pass_update_queue
        self.pass_job_queue = pass_job_queue
        self.pass_user_data = pass_user_data
        self.pass_chat_data = pass_chat_data
        self._autowire_initialized = False
        self._callback_args = None
        self._passable = None

    def check_update(self, update):
        """
        This method is called to determine if an update should be handled by
        this handler instance. It should always be overridden.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be tested.

        Returns:
            :obj:`bool`

        """
        raise NotImplementedError

    def handle_update(self, update, dispatcher):
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance. It should also be overridden, but in most
        cases call ``self.callback(dispatcher.bot, update)``, possibly along with
        optional arguments. To work with the ``ConversationHandler``, this method should return the
        value returned from ``self.callback``

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be handled.
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher to collect optional args.

        """
        raise NotImplementedError

    def __warn_autowire(self):
        """ Warn if the user has set any `pass_*` flags to True in addition to `autowire` """
        for flag in self._get_available_pass_flags():
            to_pass = bool(getattr(self, flag))
            if to_pass is True:
                warnings.warn('If `autowire` is set to `True`, it is unnecessary '
                              'to provide the `{}` flag.'.format(flag))

    def _get_available_pass_flags(self):
        """
        Used to provide warnings if the user decides to use `autowire` in conjunction with
        ``pass_*`` flags, and to recalculate all flags.

        Getting objects dynamically is better than hard-coding all passable objects and setting
        them to False in here, because the base class should not know about the existence of
        passable objects that are only relevant to subclasses (e.g. args, groups, groupdict).
        """
        return [f for f in dir(self) if f.startswith('pass_')]

    def __should_pass_obj(self, name):
        """
        Utility to determine whether a passable object is part of
        the user handler's signature, makes sense in this context,
        and is not explicitly set to `False`.
        """
        is_requested = name in self.PASSABLE_OBJECTS and name in self._callback_args
        if is_requested and name not in self._passable:
            warnings.warn("The argument `{}` cannot be autowired since it is not available "
                          "on `{}s`.".format(name, type(self).__name__))
            return False
        return is_requested

    def set_autowired_flags(self,
                            passable={'update_queue', 'job_queue', 'user_data', 'chat_data'}):
        """
        This method inspects the callback handler for used arguments. If it finds arguments that
        are ``passable``, i.e. types that can also be passed by the various ``pass_*`` flags,
        it sets the according flags to true.

        If the handler signature is prone to change at runtime for whatever reason, you can call
        this method again to recalculate the flags to use.

        The ``passable`` arguments are required to be explicit as opposed to dynamically generated
        to be absolutely safe that no arguments will be passed that are not allowed.

        Args:
            passable: An iterable that contains the allowed flags for this handler
        """
        self._passable = passable

        if not self.autowire:
            raise ValueError("This handler is not autowired.")

        if self._autowire_initialized:
            # In case that users decide to change their callback signatures at runtime, give the
            # possibility to recalculate all flags.
            for flag in self._get_available_pass_flags():
                setattr(self, flag, False)

        self.__warn_autowire()

        self._callback_args = inspect_arguments(self.callback)

        # Actually set `pass_*` flags to True
        for to_pass in self.PASSABLE_OBJECTS:
            if self.__should_pass_obj(to_pass):
                setattr(self, 'pass_' + to_pass, True)

        self._autowire_initialized = True

    def collect_optional_args(self, dispatcher, update=None):
        """
        Prepares the optional arguments that are the same for all types of handlers.

        Args:
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher.

        """
        optional_args = dict()

        if self.autowire:
            # Subclasses are responsible for calling `set_autowired_flags`
            # at the end of their __init__
            assert self._autowire_initialized

        if self.pass_update_queue:
            optional_args['update_queue'] = dispatcher.update_queue
        if self.pass_job_queue:
            optional_args['job_queue'] = dispatcher.job_queue
        if self.pass_user_data:
            user = update.effective_user
            optional_args['user_data'] = dispatcher.user_data[user.id if user else None]
        if self.pass_chat_data:
            chat = update.effective_chat
            optional_args['chat_data'] = dispatcher.chat_data[chat.id if chat else None]

        return optional_args

    def collect_bot_update_args(self, dispatcher, update):
        """
        Prepares the positional arguments ``bot`` and/or ``update`` that are required for every
        python-telegram-bot handler that is not **autowired**. If ``autowire`` is set to ``True``,
        this method uses the inspected callback arguments to decide whether bot or update,
        respectively, need to be passed. The order is always (bot, update).


        Args:
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher.
            update (:class:`telegram.Update`): The update.

        Returns:
            A tuple of bot, update, or both
        """
        if self.autowire:
            # Subclasses are responsible for calling `set_autowired_flags` in their __init__
            assert self._autowire_initialized

            positional_args = []
            if 'bot' in self._callback_args:
                positional_args.append(dispatcher.bot)
            if 'update' in self._callback_args:
                positional_args.append(update)
            return tuple(positional_args)
        else:
            return (dispatcher.bot, update)
