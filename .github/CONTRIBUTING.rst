=================
How To Contribute
=================

Every open source project lives from the generous help by contributors that sacrifice their time and ``python-telegram-bot`` is no different. To make participation as pleasant as possible, this project adheres to the `Code of Conduct`_ by the Python Software Foundation.

Setting things up
=================

1. Fork the ``python-telegram-bot`` repository to your GitHub account.

2. Clone your forked repository of ``python-telegram-bot`` to your computer:

   .. code-block:: bash

      $ git clone https://github.com/<your username>/python-telegram-bot
      $ cd python-telegram-bot

3. Add a track to the original repository:

   .. code-block:: bash

      $ git remote add upstream https://github.com/python-telegram-bot/python-telegram-bot

4. Install dependencies:

   .. code-block:: bash

      $ pip install -r requirements-all.txt


5. Install pre-commit hooks:

   .. code-block:: bash

      $ pre-commit install

Finding something to do
=======================

If you already know what you'd like to work on, you can skip this section.

If you have an idea for something to do, first check if it's already been filed on the `issue tracker`_. If so, add a comment to the issue saying you'd like to work on it, and we'll help you get started! Otherwise, please file a new issue and assign yourself to it.

Another great way to start contributing is by writing tests. Tests are really important because they help prevent developers from accidentally breaking existing code, allowing them to build cool things faster. If you're interested in helping out, let the development team know by posting to the `Telegram group`_, and we'll help you get started.

That being said, we want to mention that we are very hesitant about adding new requirements to our projects. If you intend to do this, please state this in an issue and get a verification from one of the maintainers.

Instructions for making a code change
=====================================

The central development branch is ``master``, which should be clean and ready for release at any time. In general, all changes should be done as feature branches based off of ``master``.

If you want to do solely documentation changes, base them and PR to the branch ``doc-fixes``. This branch also has its own `RTD build`_.

Here's how to make a one-off code change.

1. **Choose a descriptive branch name.** It should be lowercase, hyphen-separated, and a noun describing the change (so, ``fuzzy-rules``, but not ``implement-fuzzy-rules``). Also, it shouldn't start with ``hotfix`` or ``release``.

2. **Create a new branch with this name, starting from** ``master``. In other words, run:

   .. code-block:: bash

      $ git fetch upstream
      $ git checkout master
      $ git merge upstream/master
      $ git checkout -b your-branch-name

3. **Make a commit to your feature branch**. Each commit should be self-contained and have a descriptive commit message that helps other developers understand why the changes were made.

   - You can refer to relevant issues in the commit message by writing, e.g., "#105".

   - Your code should adhere to the `PEP 8 Style Guide`_, with the exception that we have a maximum line length of 99.

   - Provide static typing with signature annotations. The documentation of `MyPy`_ will be a good start, the cheat sheet is `here`_. We also have some custom type aliases in ``telegram._utils.types``.

   - Document your code. This step is pretty important to us, so it has its own `section`_.

   - For consistency, please conform to `Google Python Style Guide`_ and `Google Python Style Docstrings`_.

   - The following exceptions to the above (Google's) style guides applies:

        - Documenting types of global variables and complex types of class members can be done using the Sphinx docstring convention.

   -  In addition, PTB uses some formatting/styling and linting tools in the pre-commit setup. Some of those tools also have command line tools that can help to run these tools outside of the pre-commit step. If you'd like to leverage that, please have a look at the `pre-commit config file`_ for an overview of which tools (and which versions of them) are used. For example, we use `Black`_ for code formatting. Plugins for Black exist for some `popular editors`_. You can use those instead of manually formatting everything.

   - Please ensure that the code you write is well-tested and that all automated tests still pass. We
     have dedicated an `testing page`_ to help you with that.

   - Don't break backward compatibility.

   - Add yourself to the AUTHORS.rst_ file in an alphabetical fashion.

   - If you want run style & type checks before committing run

     .. code-block:: bash

        $ pre-commit run -a

   - To actually make the commit (this will trigger tests style & type checks automatically):

     .. code-block:: bash

        $ git add your-file-changed.py

   - Finally, push it to your GitHub fork, run:

     .. code-block:: bash

      $ git push origin your-branch-name

4. **When your feature is ready to merge, create a pull request.**

   - Go to your fork on GitHub, select your branch from the dropdown menu, and click "New pull request".

   - Add a descriptive comment explaining the purpose of the branch (e.g. "Add the new API feature to create inline bot queries."). This will tell the reviewer what the purpose of the branch is.

   - Click "Create pull request". An admin will assign a reviewer to your commit.

5. **Address review comments until all reviewers give LGTM ('looks good to me').**

   - When your reviewer has reviewed the code, you'll get a notification. You'll need to respond in two ways:

       - Make a new commit addressing the comments you agree with, and push it to the same branch. Ideally, the commit message would explain what the commit does (e.g. "Fix lint error"), but if there are lots of disparate review comments, it's fine to refer to the original commit message and add something like "(address review comments)".

       - In order to keep the commit history intact, please avoid squashing or amending history and then force-pushing to the PR. Reviewers often want to look at individual commits.

       - In addition, please reply to each comment. Each reply should be either "Done" or a response explaining why the corresponding suggestion wasn't implemented. All comments must be resolved before LGTM can be given.

   - Resolve any merge conflicts that arise. To resolve conflicts between 'your-branch-name' (in your fork) and 'master' (in the ``python-telegram-bot`` repository), run:

     .. code-block:: bash

        $ git checkout your-branch-name
        $ git fetch upstream
        $ git merge upstream/master
        $ ...[fix the conflicts]...
        $ ...[make sure the tests pass before committing]...
        $ git commit -a
        $ git push origin your-branch-name

   - At the end, the reviewer will merge the pull request.

6. **Tidy up!** Delete the feature branch from both your local clone and the GitHub repository:

   .. code-block:: bash

      $ git branch -D your-branch-name
      $ git push origin --delete your-branch-name

7. **Celebrate.** Congratulations, you have contributed to ``python-telegram-bot``!

Documenting
===========

The documentation of this project is separated in two sections: User facing and dev facing.

User facing docs are hosted at `RTD`_. They are the main way the users of our library are supposed to get information about the objects. They don't care about the internals, they just want to know
what they have to pass to make it work, what it actually does. You can/should provide examples for non obvious cases (like the Filter module), and notes/warnings.

Dev facing, on the other side, is for the devs/maintainers of this project. These
doc strings don't have a separate documentation site they generate, instead, they document the actual code.

User facing documentation
-------------------------
We use `sphinx`_ to generate static HTML docs. To build them, first make sure you're running Python 3.9 or above and have the required dependencies:

.. code-block:: bash

   $ pip install -r docs/requirements-docs.txt

then run the following from the PTB root directory:

.. code-block:: bash

   $ make -C docs html

or, if you don't have ``make`` available (e.g. on Windows):

.. code-block:: bash

   $ sphinx-build docs/source docs/build/html

Once the process terminates, you can view the built documentation by opening ``docs/build/html/index.html`` with a browser.

- Add ``.. versionadded:: NEXT.VERSION``, ``.. versionchanged:: NEXT.VERSION`` or ``.. deprecated:: NEXT.VERSION`` to the associated documentation of your changes, depending on what kind of change you made. This only applies if the change you made is visible to an end user. The directives should be added to class/method descriptions if their general behaviour changed and to the description of all arguments & attributes that changed.

Dev facing documentation
------------------------
We adhere to the `CSI`_ standard. This documentation is not fully implemented in the project, yet, but new code changes should comply with the `CSI` standard.
The idea behind this is to make it very easy for you/a random maintainer or even a totally foreign person to drop anywhere into the code and more or less immediately understand what a particular line does. This will make it easier
for new to make relevant changes if said lines don't do what they are supposed to.



Style commandments
==================

Assert comparison order
-----------------------

Assert statements should compare in **actual** == **expected** order.
For example (assuming ``test_call`` is the thing being tested):

.. code-block:: python

    # GOOD
    assert test_call() == 5

    # BAD
    assert 5 == test_call()

Properly calling callables
--------------------------

Methods, functions and classes can specify optional parameters (with default
values) using Python's keyword arg syntax. When providing a value to such a
callable we prefer that the call also uses keyword arg syntax. For example:

.. code-block:: python

   # GOOD
   f(0, optional=True)

   # BAD
   f(0, True)

This gives us the flexibility to re-order arguments and more importantly
to add new required arguments. It's also more explicit and easier to read.

Properly defining optional arguments
------------------------------------

It's always good to not initialize optional arguments at class creation,
instead use ``**kwargs`` to get them. It's well known Telegram API can
change without notice, in that case if a new argument is added it won't
break the API classes. For example:

.. code-block:: python

    # GOOD
    def __init__(self, id, name, last_name=None, **kwargs):
        self.last_name = last_name


    # BAD
    def __init__(self, id, name, last_name=None):
        self.last_name = last_name


.. _`Code of Conduct`: https://www.python.org/psf/conduct/
.. _`issue tracker`: https://github.com/python-telegram-bot/python-telegram-bot/issues
.. _`Telegram group`: https://telegram.me/pythontelegrambotgroup
.. _`PEP 8 Style Guide`: https://peps.python.org/pep-0008/
.. _`sphinx`: https://www.sphinx-doc.org/en/master
.. _`Google Python Style Guide`: https://google.github.io/styleguide/pyguide.html
.. _`Google Python Style Docstrings`: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
.. _AUTHORS.rst: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/AUTHORS.rst
.. _`MyPy`: https://mypy.readthedocs.io/en/stable/index.html
.. _`here`: https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
.. _`pre-commit config file`: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/.pre-commit-config.yaml
.. _`Black`: https://black.readthedocs.io/en/stable/index.html
.. _`popular editors`: https://black.readthedocs.io/en/stable/integrations/editors.html
.. _`RTD`: https://docs.python-telegram-bot.org/
.. _`RTD build`: https://docs.python-telegram-bot.org/en/doc-fixes
.. _`CSI`: https://standards.mousepawmedia.com/en/stable/csi.html
.. _`section`: #documenting
.. _`testing page`: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/tests/README.rst
