==============
Testing in PTB
==============

PTB uses `pytest`_ for testing. To run the tests, you need to
have pytest installed along with a few other dependencies. You can find the list of dependencies
in the ``pyproject.toml`` file in the root of the repository.

Since PTB uses a src-based layout, make sure you have installed the package in development mode before running the tests:

.. code-block:: bash

   $ pip install -e .

Running tests
=============

To run the entire test suite, you can use the following command:

.. code-block:: bash

    $ pytest

This will run all the tests, including the ones which make a request to the Telegram servers, which
may take a long time (total > 13 mins). To run only the tests that don't require a connection, you
can run the following command:

.. code-block:: bash

    $ pytest -m no_req

Or alternatively, you can run the following command to run only the tests that require a connection:

.. code-block:: bash

    $ pytest -m req

To further speed up the tests, you can run them in parallel using the ``-n`` flag (requires `pytest-xdist`_). But beware that
this will use multiple CPU cores on your machine. The ``--dist`` flag is used to specify how the
tests will be distributed across the cores. The ``loadgroup`` option is used to distribute the tests
such that tests marked with ``@pytest.mark.xdist_group("name")`` are run on the same core — important if you want avoid race conditions in some tests:

.. code-block:: bash

    $ pytest -n auto --dist=loadgroup

This will result in a significant speedup, but may cause some tests to fail. If you want to run
the failed tests in isolation, you can use the ``--lf`` flag:

.. code-block:: bash

    $ pytest --lf


Writing tests
=============

PTB has a separate test file for every file in the ``telegram.*`` namespace. Further, the tests for
the ``telegram`` module are split into two classes, based on whether the test methods in them make a
request or not. When writing tests, make sure to split them into these two classes, and make sure
to name the test class as: ``TestXXXWithoutRequest`` for tests that don't make a request, and ``TestXXXWithRequest`` for tests that do.

Writing tests is a creative process; allowing you to design your test however you'd like, but there
are a few conventions that you should follow:

- Each new test class needs a ``test_slot_behaviour``, ``test_to_dict``, ``test_de_json`` and
  ``test_equality`` (in most cases).

- Make use of pytest's fixtures and parametrize wherever possible. Having knowledge of pytest's
  tooling can help you as well. You can look at the existing tests for examples and inspiration.

- New fixtures should go into ``conftest.py``. New auxiliary functions and classes, used either directly in the tests or in the fixtures, should go into the ``tests/auxil`` directory.

If you have made some API changes, you may want to run ``test_official`` to validate that the changes are
complete and correct. To run it, export an environment variable first:

.. code-block:: bash

    $ export TEST_OFFICIAL=true

and then run ``pytest tests/test_official/test_official.py``. Note: You need py 3.10+ to run this test.

We also have another marker, ``@pytest.mark.dev``, which you can add to tests that you want to run selectively.
Use as follows:

.. code-block:: bash

    $ pytest -m dev


Debugging tests
===============

Writing tests can be challenging, and fixing failing tests can be even more so. To help with this,
PTB has started to adopt the use of ``logging`` in the test suite. You can insert debug logging 
statements in your tests to help you understand what's going on. To enable these logs, you can set 
``log_level = DEBUG`` in ``setup.cfg`` or use the ``--log-level=INFO`` flag when running the tests.
If a test is large and complicated, it is recommended to leave the debug logs for others to use as 
well.


Bots used in tests
==================

If you run the tests locally, the test setup will use one of the two public bots available. Which
bot of the two gets chosen for the test session is random. Whereas when the tests on the
Github Actions CI are run, the test setup allocates a different, but the same bot is allocated for every combination of Python version and
OS. The operating systems and Python versions the CI runs the tests on can be viewed in the `corresponding workflow`_.


That's it! If you have any questions, feel free to ask them in the `PTB dev
group`_.

.. _pytest: https://docs.pytest.org/en/stable/
.. _pytest-xdist: https://pypi.org/project/pytest-xdist/
.. _PTB dev group: https://t.me/pythontelegrambotgroup
.. _corresponding workflow: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/.github/workflows/unit_tests.yml
