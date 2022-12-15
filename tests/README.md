## Testing in PTB

PTB uses [pytest](https://docs.pytest.org/en/latest/) for testing. To run the tests, you need to
have pytest installed along with a few other dependencies. You can find the list of dependencies
in the `requirements-dev.txt` file in the root of the repository.

### Running tests

To run the entire test suite, you can use the following command:

    $ pytest

This will run all the tests, including the ones which make a request to the Telegram servers, which
may take a long time (about > 13 mins). To run only the tests that don't require a connection, you
can run the following command:

    $ pytest -m no_req

To further speed up the tests, you can run them in parallel using the `-n` flag:

    $ pytest -n auto

This will result in a significant speedup, but may cause some tests to fail. If you want to run
the failed tests in isolation, you can use the `--lf` flag:

    $ pytest --lf


### Writing tests

PTB has a separate test file for every file in the `telegram.*` namespace. Further, the tests for
the `telegram` module are split into two classes, based on whether the test methods in them make a
request or not. When writing tests, make sure to split them into these two classes, and make sure
to name the test class as: `TestXXXNoReq` for tests that don't make a request, and `TestXXXReq` for
tests that do.

Writing tests is a creative process, where you can design your test however you'd like, but there
are a few conventions that you should follow:

- Each new test class needs a `test_slot_behaviour`, `test_to_dict`, `test_de_json` and
  `test_equality` (in most cases).

- Make use of pytest's fixtures and parametrize wherever possible. Having knowledge of pytest's
  tooling can help you as well. You can look at the existing tests for examples.

We also have another marker, `@pytest.mark.dev`, which is used to mark tests that you want to run selectively.
Use as follows:

    $ pytest -m dev

That's it! If you have any questions, feel free to ask them in the [PTB dev group](https://t.me/pythontelegrambotdev).