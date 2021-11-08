..
    Make user to apply any changes to this file to README.rst as well!

.. image:: https://github.com/python-telegram-bot/logos/blob/master/logo-text/png/ptb-raw-logo-text_768.png?raw=true
   :align: center
   :target: https://python-telegram-bot.org
   :alt: python-telegram-bot-raw Logo

We have made you a wrapper you can't refuse

We have a vibrant community of developers helping each other in our `Telegram group <https://telegram.me/pythontelegrambotgroup>`_. Join us!

*Stay tuned for library updates and new releases on our* `Telegram Channel <https://telegram.me/pythontelegrambotchannel>`_.

.. image:: https://img.shields.io/pypi/v/python-telegram-bot-raw.svg
   :target: https://pypi.org/project/python-telegram-bot-raw/
   :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/pyversions/python-telegram-bot-raw.svg
   :target: https://pypi.org/project/python-telegram-bot-raw/
   :alt: Supported Python versions

.. image:: https://img.shields.io/badge/Bot%20API-5.4-blue?logo=telegram
   :target: https://core.telegram.org/bots/api-changelog
   :alt: Supported Bot API versions

.. image:: https://img.shields.io/pypi/dm/python-telegram-bot-raw
   :target: https://pypistats.org/packages/python-telegram-bot-raw
   :alt: PyPi Package Monthly Download

.. image:: https://readthedocs.org/projects/python-telegram-bot/badge/?version=stable
   :target: https://python-telegram-bot.readthedocs.io/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/l/python-telegram-bot-raw.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0.html
   :alt: LGPLv3 License

.. image:: https://github.com/python-telegram-bot/python-telegram-bot/workflows/GitHub%20Actions/badge.svg
   :target: https://github.com/python-telegram-bot/python-telegram-bot/
   :alt: Github Actions workflow

.. image:: https://codecov.io/gh/python-telegram-bot/python-telegram-bot/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/python-telegram-bot/python-telegram-bot
   :alt: Code coverage

.. image:: http://isitmaintained.com/badge/resolution/python-telegram-bot/python-telegram-bot.svg
   :target: http://isitmaintained.com/project/python-telegram-bot/python-telegram-bot
   :alt: Median time to resolve an issue

.. image:: https://api.codacy.com/project/badge/Grade/99d901eaa09b44b4819aec05c330c968
   :target: https://www.codacy.com/app/python-telegram-bot/python-telegram-bot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=python-telegram-bot/python-telegram-bot&amp;utm_campaign=Badge_Grade
   :alt: Code quality: Codacy

.. image:: https://deepsource.io/gh/python-telegram-bot/python-telegram-bot.svg/?label=active+issues
   :target: https://deepsource.io/gh/python-telegram-bot/python-telegram-bot/?ref=repository-badge
   :alt: Code quality: DeepSource

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/Telegram-Group-blue.svg?logo=telegram
   :target: https://telegram.me/pythontelegrambotgroup
   :alt: Telegram Group

=================
Table of contents
=================

- `Introduction`_

- `Telegram API support`_

- `Installing`_

- `Getting started`_

  #. `Logging`_

  #. `Documentation`_

- `Getting help`_

- `Contributing`_

- `License`_

============
Introduction
============

This library provides a pure Python, lightweight interface for the
`Telegram Bot API <https://core.telegram.org/bots/api>`_.
It's compatible with Python versions 3.6.8+. PTB-Raw might also work on `PyPy <http://pypy.org/>`_, though there have been a lot of issues before. Hence, PyPy is not officially supported.

``python-telegram-bot-raw`` is part of the `python-telegram-bot <https://python-telegram-bot.org>`_ ecosystem and provides the pure API functionality extracted from PTB. It therefore does *not* have independent release schedules, changelogs or documentation. Please consult the PTB resources.

----
Note
----

Installing both ``python-telegram-bot`` and ``python-telegram-bot-raw`` in conjunction will result in undesired side-effects, so only install *one* of both.

====================
Telegram API support
====================

All types and methods of the Telegram Bot API **5.4** are supported.

==========
Installing
==========

You can install or upgrade python-telegram-bot-raw with:

.. code:: shell

    $ pip install python-telegram-bot-raw --upgrade

Or you can install from source with:

.. code:: shell

    $ git clone https://github.com/python-telegram-bot/python-telegram-bot --recursive
    $ cd python-telegram-bot
    $ python setup-raw.py install

In case you have a previously cloned local repository already, you should initialize the added urllib3 submodule before installing with:

.. code:: shell

    $ git submodule update --init --recursive

----
Note
----

Installing the `.tar.gz` archive available on PyPi directly via `pip` will *not* work as expected, as `pip` does not recognize that it should use `setup-raw.py` instead of `setup.py`.

---------------------
Optional Dependencies
---------------------

PTB can be installed with optional dependencies:

* ``pip install python-telegram-bot-raw[passport]`` installs the `cryptography <https://cryptography.io>`_ library. Use this, if you want to use Telegram Passport related functionality.
* ``pip install python-telegram-bot-raw[ujson]`` installs the `ujson <https://pypi.org/project/ujson/>`_ library. It will then be used for JSON de- & encoding, which can bring speed up compared to the standard `json <https://docs.python.org/3/library/json.html>`_ library.

===============
Getting started
===============

Our Wiki contains an `Introduction to the API <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API>`_. Other references are:

- the `Telegram API documentation <https://core.telegram.org/bots/api>`_
- the `python-telegram-bot documentation <https://python-telegram-bot.readthedocs.io/>`_

-------
Logging
-------

This library uses the ``logging`` module. To set up logging to standard output, put:

.. code:: python

    import logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

at the beginning of your script.

You can also use logs in your application by calling ``logging.getLogger()`` and setting the log level you want:

.. code:: python

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

If you want DEBUG logs instead:

.. code:: python

    logger.setLevel(logging.DEBUG)


=============
Documentation
=============

``python-telegram-bot``'s documentation lives at `readthedocs.io <https://python-telegram-bot.readthedocs.io/>`_, which
includes the relevant documentation for ``python-telegram-bot-raw``.

============
Getting help
============

You can get help in several ways:

1. We have a vibrant community of developers helping each other in our `Telegram group <https://telegram.me/pythontelegrambotgroup>`_. Join us!

2. Report bugs, request new features or ask questions by `creating an issue <https://github.com/python-telegram-bot/python-telegram-bot/issues/new/choose>`_ or `a discussion <https://github.com/python-telegram-bot/python-telegram-bot/discussions/new>`_.

3. Our `Wiki pages <https://github.com/python-telegram-bot/python-telegram-bot/wiki/>`_ offer a growing amount of resources.

4. You can even ask for help on Stack Overflow using the `python-telegram-bot tag <https://stackoverflow.com/questions/tagged/python-telegram-bot>`_.

============
Contributing
============

Contributions of all sizes are welcome. Please review our `contribution guidelines <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/.github/CONTRIBUTING.rst>`_ to get started. You can also help by `reporting bugs <https://github.com/python-telegram-bot/python-telegram-bot/issues/new>`_.

========
Donating
========
Occasionally we are asked if we accept donations to support the development. While we appreciate the thought, maintaining PTB is our hobby and we have almost no running costs for it. We therefore have nothing set up to accept donations. If you still want to donate, we kindly ask you to donate to another open source project/initiative of your choice instead.

=======
License
=======

You may copy, distribute and modify the software provided that modifications are described and licensed for free under `LGPL-3 <https://www.gnu.org/licenses/lgpl-3.0.html>`_. Derivatives works (including modifications or anything statically linked to the library) can only be redistributed under LGPL-3, but applications that use the library don't have to be.
