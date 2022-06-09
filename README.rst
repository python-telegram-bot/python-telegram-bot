..
    Make sure to apply any changes to this file to README_RAW.rst as well!

.. image:: https://raw.githubusercontent.com/python-telegram-bot/logos/master/logo-text/png/ptb-logo-text_768.png
   :align: center
   :target: https://python-telegram-bot.org
   :alt: python-telegram-bot Logo

.. image:: https://img.shields.io/pypi/v/python-telegram-bot.svg
   :target: https://pypi.org/project/python-telegram-bot/
   :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/pyversions/python-telegram-bot.svg
   :target: https://pypi.org/project/python-telegram-bot/
   :alt: Supported Python versions

.. image:: https://img.shields.io/badge/Bot%20API-6.0-blue?logo=telegram
   :target: https://core.telegram.org/bots/api-changelog
   :alt: Supported Bot API versions

.. image:: https://img.shields.io/pypi/dm/python-telegram-bot
   :target: https://pypistats.org/packages/python-telegram-bot
   :alt: PyPi Package Monthly Download

.. image:: https://readthedocs.org/projects/python-telegram-bot/badge/?version=stable
   :target: https://docs.python-telegram-bot.org/en/stable/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/l/python-telegram-bot.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0.html
   :alt: LGPLv3 License

.. image:: https://github.com/python-telegram-bot/python-telegram-bot/workflows/GitHub%20Actions/badge.svg
   :target: https://github.com/python-telegram-bot/python-telegram-bot/
   :alt: Github Actions workflow

.. image:: https://app.codecov.io/gh/python-telegram-bot/python-telegram-bot/branch/master/graph/badge.svg
   :target: https://app.codecov.io/gh/python-telegram-bot/python-telegram-bot
   :alt: Code coverage

.. image:: https://isitmaintained.com/badge/resolution/python-telegram-bot/python-telegram-bot.svg
   :target: https://isitmaintained.com/project/python-telegram-bot/python-telegram-bot
   :alt: Median time to resolve an issue

.. image:: https://api.codacy.com/project/badge/Grade/99d901eaa09b44b4819aec05c330c968
   :target: https://app.codacy.com/gh/python-telegram-bot/python-telegram-bot/dashboard
   :alt: Code quality: Codacy

.. image:: https://deepsource.io/gh/python-telegram-bot/python-telegram-bot.svg/?label=active+issues
   :target: https://deepsource.io/gh/python-telegram-bot/python-telegram-bot/?ref=repository-badge
   :alt: Code quality: DeepSource

.. image:: https://results.pre-commit.ci/badge/github/python-telegram-bot/python-telegram-bot/master.svg
   :target: https://results.pre-commit.ci/latest/github/python-telegram-bot/python-telegram-bot/master
   :alt: pre-commit.ci status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code Style: Black

.. image:: https://img.shields.io/badge/Telegram-Channel-blue.svg?logo=telegram
   :target: https://t.me/pythontelegrambotchannel
   :alt: Telegram Channel

.. image:: https://img.shields.io/badge/Telegram-Group-blue.svg?logo=telegram
   :target: https://telegram.me/pythontelegrambotgroup
   :alt: Telegram Group

We have made you a wrapper you can't refuse

We have a vibrant community of developers helping each other in our `Telegram group <https://telegram.me/pythontelegrambotgroup>`_. Join us!

*Stay tuned for library updates and new releases on our* `Telegram Channel <https://telegram.me/pythontelegrambotchannel>`_.

Introduction
============

This library provides a pure Python, asynchronous interface for the
`Telegram Bot API <https://core.telegram.org/bots/api>`_.
It's compatible with Python versions **3.7+**.

In addition to the pure API implementation, this library features a number of high-level classes to
make the development of bots easy and straightforward. These classes are contained in the
``telegram.ext`` submodule.

A pure API implementation *without* ``telegram.ext`` is available as the standalone package ``python-telegram-bot-raw``.  `See here for details. <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/README_RAW.rst>`_

Note
----

Installing both ``python-telegram-bot`` and ``python-telegram-bot-raw`` in conjunction will result in undesired side-effects, so only install *one* of both.

Telegram API support
====================

All types and methods of the Telegram Bot API **6.0** are supported.

Installing
==========

You can install or upgrade ``python-telegram-bot`` via

.. code:: shell

    $ pip install python-telegram-bot --upgrade

To install a pre-release, use the ``--pre`` `flag <https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-pre>`_ in addition.

You can also install ``python-telegram-bot`` from source, though this is usually not necessary.

.. code:: shell

    $ git clone https://github.com/python-telegram-bot/python-telegram-bot
    $ cd python-telegram-bot
    $ python setup.py install

Dependencies & Their Versions
-----------------------------

``python-telegram-bot`` tries to use as few 3rd party dependencies as possible.
However, for some features using a 3rd party library is more sane than implementing the functionality again.
The dependencies are:

* `httpx ~= 0.23.0 <https://www.python-httpx.org>`_ for ``telegram.request.HTTPXRequest``, the default networking backend
* `tornado~=6.1 <https://www.tornadoweb.org/en/stable/>`_ for ``telegram.ext.Updater.start_webhook``
* `cachetools~=5.2.0 <https://cachetools.readthedocs.io/en/latest/>`_ for ``telegram.ext.CallbackDataCache``
* `APScheduler~=3.9.1 <https://apscheduler.readthedocs.io/en/3.x/>`_ for ``telegram.ext.JobQueue``

``python-telegram-bot`` is most useful when used along with additional libraries.
To minimize dependency conflicts, we try to be liberal in terms of version requirements on the dependencies.
On the other hand, we have to ensure stability of ``python-telegram-bot``, which is why we do apply version bounds.
If you encounter dependency conflicts due to these bounds, feel free to reach out.

Optional Dependencies
---------------------

PTB can be installed with optional dependencies:

* ``pip install python-telegram-bot[passport]`` installs the `cryptography>=3.0 <https://cryptography.io/en/stable>`_ library. Use this, if you want to use Telegram Passport related functionality.
* ``pip install python-telegram-bot[socks]`` installs ``httpx[socks]``. Use this, if you want to work behind a Socks5 server.

Quick Start
===========

Our Wiki contains an `Introduction to the API <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API>`_ explaining how the pure Bot API can be accessed via ``python-telegram-bot``.
Moreover, the `Tutorial: Your first Bot <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot>`_ gives an introduction on how chatbots can be easily programmed with the help of the ``telegram.ext`` module.

Resources
=========

- The `package documentation <https://docs.python-telegram-bot.org/>`_ is the technical reference for ``python-telegram-bot``.
  It contains descriptions of all available classes, modules, methods and arguments.
- The `wiki <https://github.com/python-telegram-bot/python-telegram-bot/wiki/>`_ is home to number of more elaborate introductions of the different features of ``python-telegram-bot`` and other useful resources that go beyond the technical documentation.
- Our `examples directory <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/README.md>`_ contains several examples that showcase the different features of both the Bot API and ``python-telegram-bot``.
  Even if it is not your approach for learning, please take a look at ``echobot.py``. It is the de facto base for most of the bots out there.
  The code for these examples is released to the public domain, so you can start by grabbing the code and building on top of it.
- The `official Telegram Bot API documentation <https://core.telegram.org/bots/api>`_ is of course always worth a read.

Getting help
============

If the resources mentioned above don't answer your questions or simply overwhelm you, there are several ways of getting help.

1. We have a vibrant community of developers helping each other in our `Telegram group <https://telegram.me/pythontelegrambotgroup>`_. Join us! Asking a question here is often the quickest way to get a pointer in the right direction.

2. Ask questions by opening `a discussion <https://github.com/python-telegram-bot/python-telegram-bot/discussions/new>`_.

3. You can even ask for help on Stack Overflow using the `python-telegram-bot tag <https://stackoverflow.com/questions/tagged/python-telegram-bot>`_.

Concurrency
===========

Since v20.0, ``python-telegram-bot`` is built on top of Pythons ``asyncio`` module.
Because ``asyncio`` is in general single-threaded, ``python-telegram-bot`` does currently not aim to be thread-safe.
Noteworthy parts of ``python-telegram-bots`` API that are likely to cause issues (e.g. race conditions) when used in a multi-threaded setting include:

* ``telegram.ext.Application/Updater.update_queue``
* ``telegram.ext.ConversationHandler.check/handle_update``
* ``telegram.ext.CallbackDataCache``
* ``telegram.ext.BasePersistence``
* all classes in the ``telegram.ext.filters`` module that allow to add/remove allowed users/chats at runtime

Contributing
============

Contributions of all sizes are welcome.
Please review our `contribution guidelines <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/.github/CONTRIBUTING.rst>`_ to get started.
You can also help by `reporting bugs or feature requests <https://github.com/python-telegram-bot/python-telegram-bot/issues/new>`_.

Donating
========
Occasionally we are asked if we accept donations to support the development.
While we appreciate the thought, maintaining PTB is our hobby, and we have almost no running costs for it. We therefore have nothing set up to accept donations.
If you still want to donate, we kindly ask you to donate to another open source project/initiative of your choice instead.

License
=======

You may copy, distribute and modify the software provided that modifications are described and licensed for free under `LGPL-3 <https://www.gnu.org/licenses/lgpl-3.0.html>`_.
Derivatives works (including modifications or anything statically linked to the library) can only be redistributed under LGPL-3, but applications that use the library don't have to be.
