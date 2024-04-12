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

.. image:: https://img.shields.io/badge/Bot%20API-7.2-blue?logo=telegram
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

.. image:: https://github.com/python-telegram-bot/python-telegram-bot/actions/workflows/unit_tests.yml/badge.svg?branch=master
   :target: https://github.com/python-telegram-bot/python-telegram-bot/
   :alt: Github Actions workflow

.. image:: https://codecov.io/gh/python-telegram-bot/python-telegram-bot/branch/master/graph/badge.svg
   :target: https://app.codecov.io/gh/python-telegram-bot/python-telegram-bot
   :alt: Code coverage

.. image:: https://isitmaintained.com/badge/resolution/python-telegram-bot/python-telegram-bot.svg
   :target: https://isitmaintained.com/project/python-telegram-bot/python-telegram-bot
   :alt: Median time to resolve an issue

.. image:: https://api.codacy.com/project/badge/Grade/99d901eaa09b44b4819aec05c330c968
   :target: https://app.codacy.com/gh/python-telegram-bot/python-telegram-bot/dashboard
   :alt: Code quality: Codacy

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
It's compatible with Python versions **3.8+**.

In addition to the pure API implementation, this library features a number of high-level classes to
make the development of bots easy and straightforward. These classes are contained in the
``telegram.ext`` submodule.

A pure API implementation *without* ``telegram.ext`` is available as the standalone package ``python-telegram-bot-raw``.  `See here for details. <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/README_RAW.rst>`_

Note
----

Installing both ``python-telegram-bot`` and ``python-telegram-bot-raw`` in conjunction will result in undesired side-effects, so only install *one* of both.

Telegram API support
====================

All types and methods of the Telegram Bot API **7.2** are supported.

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

Verifying Releases
------------------

We sign all the releases with a GPG key.
The signatures are uploaded to both the `GitHub releases page <https://github.com/python-telegram-bot/python-telegram-bot/releases>`_ and the `PyPI project <https://pypi.org/project/python-telegram-bot/>`_ and end with a suffix ``.asc``.
Please find the public keys `here <https://github.com/python-telegram-bot/python-telegram-bot/tree/master/public_keys>`_.
The keys are named in the format ``<first_version>-<last_version>.gpg`` or ``<first_version>-current.gpg`` if the key is currently being used for new releases.

In addition, the GitHub release page also contains the sha1 hashes of the release files in the files with the suffix ``.sha1``.

This allows you to verify that a release file that you downloaded was indeed provided by the ``python-telegram-bot`` team.

Dependencies & Their Versions
-----------------------------

``python-telegram-bot`` tries to use as few 3rd party dependencies as possible.
However, for some features using a 3rd party library is more sane than implementing the functionality again.
As these features are *optional*, the corresponding 3rd party dependencies are not installed by default.
Instead, they are listed as optional dependencies.
This allows to avoid unnecessary dependency conflicts for users who don't need the optional features.

The only required dependency is `httpx ~= 0.27 <https://www.python-httpx.org>`_ for
``telegram.request.HTTPXRequest``, the default networking backend.

``python-telegram-bot`` is most useful when used along with additional libraries.
To minimize dependency conflicts, we try to be liberal in terms of version requirements on the (optional) dependencies.
On the other hand, we have to ensure stability of ``python-telegram-bot``, which is why we do apply version bounds.
If you encounter dependency conflicts due to these bounds, feel free to reach out.

Optional Dependencies
#####################

PTB can be installed with optional dependencies:

* ``pip install "python-telegram-bot[passport]"`` installs the `cryptography>=39.0.1 <https://cryptography.io/en/stable>`_ library. Use this, if you want to use Telegram Passport related functionality.
* ``pip install "python-telegram-bot[socks]"`` installs `httpx[socks] <https://www.python-httpx.org/#dependencies>`_. Use this, if you want to work behind a Socks5 server.
* ``pip install "python-telegram-bot[http2]"`` installs `httpx[http2] <https://www.python-httpx.org/#dependencies>`_. Use this, if you want to use HTTP/2.
* ``pip install "python-telegram-bot[rate-limiter]"`` installs `aiolimiter~=1.1.0 <https://aiolimiter.readthedocs.io/en/stable/>`_. Use this, if you want to use ``telegram.ext.AIORateLimiter``.
* ``pip install "python-telegram-bot[webhooks]"`` installs the `tornado~=6.4 <https://www.tornadoweb.org/en/stable/>`_ library. Use this, if you want to use ``telegram.ext.Updater.start_webhook``/``telegram.ext.Application.run_webhook``.
* ``pip install "python-telegram-bot[callback-data]"`` installs the `cachetools~=5.3.3 <https://cachetools.readthedocs.io/en/latest/>`_ library. Use this, if you want to use `arbitrary callback_data <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Arbitrary-callback_data>`_.
* ``pip install "python-telegram-bot[job-queue]"`` installs the `APScheduler~=3.10.4 <https://apscheduler.readthedocs.io/en/3.x/>`_ library and enforces `pytz>=2018.6 <https://pypi.org/project/pytz/>`_, where ``pytz`` is a dependency of ``APScheduler``. Use this, if you want to use the ``telegram.ext.JobQueue``.

To install multiple optional dependencies, separate them by commas, e.g. ``pip install "python-telegram-bot[socks,webhooks]"``.

Additionally, two shortcuts are provided:

* ``pip install "python-telegram-bot[all]"`` installs all optional dependencies.
* ``pip install "python-telegram-bot[ext]"`` installs all optional dependencies that are related to ``telegram.ext``, i.e. ``[rate-limiter, webhooks, callback-data, job-queue]``.

Quick Start
===========

Our Wiki contains an `Introduction to the API <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API>`_ explaining how the pure Bot API can be accessed via ``python-telegram-bot``.
Moreover, the `Tutorial: Your first Bot <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot>`_ gives an introduction on how chatbots can be easily programmed with the help of the ``telegram.ext`` module.

Resources
=========

- The `package documentation <https://docs.python-telegram-bot.org/>`_ is the technical reference for ``python-telegram-bot``.
  It contains descriptions of all available classes, modules, methods and arguments as well as the `changelog <https://docs.python-telegram-bot.org/changelog.html>`_.
- The `wiki <https://github.com/python-telegram-bot/python-telegram-bot/wiki/>`_ is home to number of more elaborate introductions of the different features of ``python-telegram-bot`` and other useful resources that go beyond the technical documentation.
- Our `examples section <https://docs.python-telegram-bot.org/examples.html>`_ contains several examples that showcase the different features of both the Bot API and ``python-telegram-bot``.
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
You can also help by `reporting bugs or feature requests <https://github.com/python-telegram-bot/python-telegram-bot/issues/new/choose>`_.

Donating
========
Occasionally we are asked if we accept donations to support the development.
While we appreciate the thought, maintaining PTB is our hobby, and we have almost no running costs for it. We therefore have nothing set up to accept donations.
If you still want to donate, we kindly ask you to donate to another open source project/initiative of your choice instead.

License
=======

You may copy, distribute and modify the software provided that modifications are described and licensed for free under `LGPL-3 <https://www.gnu.org/licenses/lgpl-3.0.html>`_.
Derivatives works (including modifications or anything statically linked to the library) can only be redistributed under LGPL-3, but applications that use the library don't have to be.
